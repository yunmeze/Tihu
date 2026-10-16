#!/usr/bin/env python3
"""Build the exact, hash-pinned first-map art-review registration.

Run from any directory. --check validates every input and compares the generated
bytes without writing. This only writes the registration; it never edits images,
existing registrations, map data, gameplay, or Godot project settings.
"""

from __future__ import annotations

import argparse
import hashlib
from io import BytesIO
import json
from pathlib import Path
import re
import sys

from PIL import Image


PROJECT = Path(__file__).resolve().parents[1]
OUTPUT = "assets/earth/first_map_review/registration.json"
SCHEMA = "earth-first-map-research-review-v1"
MAP = "data/maps/A13.json"
MANIFEST = "assets/original/manifest.json"
INITIAL = "assets/earth/environment/ground_plate_v4/registration.json"
SOUTH = "art_source/earth_south_ground_input_plan_v1/source_owner_evidence.json"
WALK = "scripts/earth/walk_review.gd"
UNION = "art_source/earth_coherent_grass_research_v1/coherent-grass-union-RESEARCH.png"
BOUNDS = [2400, 960, 3264, 1920]
DENSITY = 2
UNION_SIZE = [1728, 1920]
# These are reviewed input identities, not hashes computed to bless new inputs.
INPUT_PINS = {
    MAP: "d09549838963c8157307cc5406d3118baf69259d82459bcba0a3a8be5b34aa27",
    MANIFEST: "506fba1f0fd826589046d38e4ebd5285ee9a11e3235cd78495cdd133c2e63837",
    INITIAL: "146969f204793dae2cf0cc762e55c665d392062d914066037c8fe0ff38e727f1",
    SOUTH: "0d0ecc9730c0ec697b269fc48853431a17fbc6d770c612d324db65f94e31bb56",
    WALK: "53ba4310a82b368307788276e252aba95e63d86c1705b3169b0f19e1cd51ed33",
    UNION: "d6bf26a3bd518798ca1ecdde9ebc3be9e722f64034acc42303bc87128a72a4c4",
}
ACTOR_PINS = [
    (45, "art_source/earth_e45_vertical_leg_research_v1/45-HD4-CLOTH-CLEANED-RESEARCH.png",
     "ad7c9ad9c68223e7914607c970af2f621f931a6e84d15d6fdf68af3d48d67dd1"),
    (46, "art_source/earth_e_walk_layered_research_v1/46-HD4-RESEARCH.png",
     "b99726de6cbb5ae9db999e5e9f1eee50583a0e98d6fa75456884e0f2f2908f94"),
    (47, "art_source/earth_e_walk_layered_research_v1/47-HD4-RESEARCH.png",
     "26ed56945e287ee307290cd47b971a3b44840bb48ca998e773028f051cee1b47"),
    (48, "art_source/earth_e48_vertical_leg_research_v1/48-HD4-BOUNDED-DONOR-DIAGNOSTIC.png",
     "839e048cd413e2b8d280f8dbaa795fb224764d80e816772919f677f77d5128fa"),
    (49, "art_source/earth_e_walk_layered_research_v1/49-HD4-RESEARCH.png",
     "c1c89fcd1e3ed2a39bce194a4bc5f1988a8277e51fc8dfca7610861127d23cbf"),
    (50, "art_source/earth_e_walk_layered_research_v1/50-HD4-RESEARCH.png",
     "3166546267a1016054b1feffc4ce6fc1127b7b3f4a066b16a49b1227c743ee64"),
]


class RegistrationError(ValueError):
    """An input no longer satisfies the reviewed immutable contract."""


def require(condition: bool, message: str) -> None:
    # Explicit checks remain enabled under python -O.
    if not condition:
        raise RegistrationError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def verified_bytes(project: Path, path: str, expected: str) -> bytes:
    data = (project / path).read_bytes()
    require(sha256(data) == expected, f"SHA-256 mismatch: {path}")
    return data


def image_from_bytes(data: bytes, size: list[int], label: str) -> Image.Image:
    with Image.open(BytesIO(data)) as image:
        require(image.format == "PNG", f"Not PNG: {label}")
        require(list(image.size) == size, f"Wrong dimensions: {label}")
        return image.convert("RGBA")


def resource(path: str) -> str:
    return "res://" + path


def build(project: Path = PROJECT) -> dict:
    inputs = {path: verified_bytes(project, path, digest)
              for path, digest in INPUT_PINS.items()}
    source = json.loads(inputs[MAP])
    manifest = json.loads(inputs[MANIFEST])
    initial = json.loads(inputs[INITIAL])
    south = json.loads(inputs[SOUTH])
    require(source["id"] == "A13" and source["width"] == source["height"] == 100,
            "Unexpected source map identity")
    require(source["cellOrder"] == "x-major" and len(source["cells"]) == 10000,
            "Unexpected source map cell stream")
    require(source["tile_size"] == [48, 32], "Unexpected source grid size")
    require(initial["source_map_sha256"] == south["source_map_sha256"] == INPUT_PINS[MAP],
            "Owner evidence map identity mismatch")
    require(initial["source_manifest_sha256"] == INPUT_PINS[MANIFEST],
            "Owner evidence manifest identity mismatch")
    require(initial["owner_count"] == len(initial["owners"]) == 64,
            "Initial scope must have exactly 64 owners")
    require(len(south["owners"]) == 64, "South evidence must have exactly 64 records")

    # Match the source renderer: x-major, then y; skip zero floors. Objects are
    # deliberately absent, even when the same source cell contains an object.
    stream = []
    stream_lookup = {}
    for order, cell in enumerate(source["cells"]):
        if cell[0] == 0:
            continue
        x, y = divmod(order, source["height"])
        pack = "Map/Res/FloorBig" if cell[0] < 0 else "Map/Res/FloorSmall"
        stream_lookup[order] = len(stream)
        stream.append({"pack": pack, "index": abs(cell[0]),
                       "origin": [x * 48, y * 32], "stable_source_order": order})
    require(len(stream) == 2553, "Original floor stream count changed")

    initial_by_key = {owner["key"]: owner for owner in initial["owners"]}
    require(len(initial_by_key) == 64, "Duplicate initial owner")
    require(len({owner["key"] for owner in south["owners"]}) == 64,
            "Duplicate south owner evidence")
    additions = []
    aliases = []
    for owner in south["owners"]:
        if owner["key"] in initial_by_key:
            require(owner["status"] == "frozen_existing_v4", "Overlap is not a frozen alias")
            previous = initial_by_key[owner["key"]]
            for field in ("cell", "source_cell", "source_flag", "pack", "frame_index",
                          "signed_id", "stable_source_order", "source_map_byte_offset"):
                require(owner[field] == previous[field], f"Alias identity mismatch: {field}")
            aliases.append(owner["key"])
        else:
            require(owner["status"] == "new_exact_owner_proposal", "Unexpected south owner status")
            additions.append(owner)
    require(len(additions) == 57 and len(aliases) == 7,
            "South selection must be 57 additions and seven excluded aliases")
    require(south["summary"]["status_counts"] == {
        "new_exact_owner_proposal": 57, "frozen_existing_v4": 7}, "South count evidence mismatch")
    selected = [(owner, "initial64") for owner in initial["owners"]]
    selected.extend((owner, "south57") for owner in additions)
    selected.sort(key=lambda item: item[0]["stable_source_order"])
    require(len({o["stable_source_order"] for o, _ in selected}) == 121,
            "Union scope must have 121 unique source orders")

    union = image_from_bytes(inputs[UNION], UNION_SIZE, UNION)
    require(UNION_SIZE == [DENSITY * (BOUNDS[2] - BOUNDS[0]),
                           DENSITY * (BOUNDS[3] - BOUNDS[1])], "Union density mismatch")
    atlas_images = {}
    atlas_dependencies = {}
    owners = []
    for evidence, scope in selected:
        order = evidence["stable_source_order"]
        cell = source["cells"][order]
        x, y = divmod(order, source["height"])
        frame_id = abs(cell[0])
        pack_name = "Map/Res/FloorBig" if cell[0] < 0 else "Map/Res/FloorSmall"
        key = f"{pack_name}:{frame_id}@{x},{y}"
        require(pack_name == "Map/Res/FloorBig" and cell[0] < 0, f"Not FloorBig: {key}")
        for field, expected in {
            "key": key, "cell": [x, y], "source_cell": cell, "source_flag": cell[1],
            "pack": pack_name, "frame_index": frame_id, "signed_id": cell[0],
            "source_map_byte_offset": source["cellByteOffsets"][order], "sort_y": y,
        }.items():
            require(evidence[field] == expected, f"Owner evidence mismatch: {key} / {field}")
        pack = manifest["packs"][pack_name]
        frame = pack["frames"][str(frame_id)]
        rect = frame["rect"]
        require(frame["original"] == [96, 64] and rect[2:] == [96, 64]
                and frame["crop"] == [0, 0], f"Unexpected frame geometry: {key}")
        origin = [x * 48 + frame["crop"][0], y * 32 + frame["crop"][1]]
        region = [DENSITY * (origin[0] - BOUNDS[0]),
                  DENSITY * (origin[1] - BOUNDS[1]), 192, 128]
        require(region[0] >= 0 and region[1] >= 0
                and region[0] + region[2] <= UNION_SIZE[0]
                and region[1] + region[3] <= UNION_SIZE[1], f"Region outside union: {key}")
        if scope == "initial64":
            require(evidence["world_top_left"] == origin
                    and evidence["world_rect"] == origin + [96, 64]
                    and evidence["layer"] == 0, f"Initial geometry mismatch: {key}")
        else:
            require(evidence["world_bounds_xyxy"] == origin + [origin[0] + 96, origin[1] + 64]
                    and evidence["crop"] == frame["crop"] and evidence["original"] == frame["original"]
                    and evidence["floor_pass_tag"] == 0, f"South geometry mismatch: {key}")
        page = pack["pages"][frame["page"]]
        page_path = page["file"]
        require(page_path.startswith("res://assets/original/"), "Invalid source atlas path")
        if page_path not in atlas_images:
            data = verified_bytes(project, page_path[6:], page["sha256"])
            atlas_images[page_path] = image_from_bytes(data, page["size"], page_path)
            atlas_dependencies[page_path] = {"path": page_path, "sha256": page["sha256"], "size": page["size"]}
        source_image = atlas_images[page_path].crop((rect[0], rect[1], rect[0] + rect[2], rect[1] + rect[3]))
        require(sha256(source_image.tobytes()) == frame["rgba_sha256"], f"Source RGBA mismatch: {key}")
        source_alpha = source_image.getchannel("A")
        require(sha256(source_alpha.tobytes()) == evidence["source_alpha_sha256"],
                f"Source alpha evidence mismatch: {key}")
        region_image = union.crop((region[0], region[1], region[0] + region[2], region[1] + region[3]))
        require(region_image.getchannel("A").tobytes()
                == source_alpha.resize((192, 128), Image.Resampling.NEAREST).tobytes(),
                f"Union owner alpha differs from source: {key}")
        owners.append({
            "key": key, "scope": scope, "pack": pack_name, "frame_index": frame_id,
            "signed_id": cell[0], "cell": [x, y], "source_cell": cell,
            "source_flag": cell[1], "floor_pass_tag": 0, "sort_y": y,
            "stable_source_order": order, "source_map_byte_offset": source["cellByteOffsets"][order],
            "floor_stream_index": stream_lookup[order], "world_origin": origin,
            "original_size": frame["original"], "crop": frame["crop"],
            "source_offset_ignored": frame["offset"], "atlas_rect": rect,
            "atlas_page": page_path, "atlas_page_sha256": page["sha256"],
            "source_rgba_sha256": frame["rgba_sha256"],
            "source_alpha_sha256": evidence["source_alpha_sha256"],
            "logical_size": [96, 64], "shared_region_px": region,
            "region_rgba_sha256": sha256(region_image.tobytes()),
            "region_alpha_sha256": sha256(region_image.getchannel("A").tobytes()),
        })

    match = re.search(r"const RESEARCH_PATHS\s*:=\s*\[(.*?)\]", inputs[WALK].decode("utf-8"), re.S)
    require(match is not None, "Walk research path declaration missing")
    paths = re.findall(r'"(res://[^\"]+)"', match.group(1))
    require(paths == [resource(path) for _, path, _ in ACTOR_PINS], "Walk research paths changed")
    actor_frames = []
    for frame_id, path, digest in ACTOR_PINS:
        image = image_from_bytes(verified_bytes(project, path, digest), [512, 512], path)
        actor_frames.append({"id": frame_id, "path": resource(path), "sha256": digest,
                             "size": [512, 512], "rgba_sha256": sha256(image.tobytes())})

    return {
        "schema": SCHEMA,
        "status": "Optional first-map research review; native visual acceptance pending; gameplay unchanged",
        "map": "A13",
        "source_map": {"path": resource(MAP), "sha256": INPUT_PINS[MAP]},
        "source_manifest": {"path": resource(MANIFEST), "sha256": INPUT_PINS[MANIFEST]},
        "input_sources": [{"path": resource(path), "sha256": digest}
                          for path, digest in INPUT_PINS.items()],
        "source_atlas_pages": [atlas_dependencies[path] for path in sorted(atlas_dependencies)],
        "floor_stream": {
            "count": len(stream), "sha256": sha256(canonical(stream)),
            "hash_encoding": "UTF-8 JSON records; sorted object keys; compact separators; no trailing newline",
            "order": "Original x-major source floor stream; all floors precede objects",
            "records": stream,
        },
        "ground": {
            "texture": resource(UNION), "texture_sha256": INPUT_PINS[UNION],
            "texture_size": UNION_SIZE, "world_bounds_xyxy_half_open": BOUNDS,
            "density": DENSITY, "scale": 0.5, "owner_count": 121,
            "scope_counts": {"initial64": 64, "south57": 57, "excluded_overlap_aliases": 7},
            "excluded_overlap_alias_keys": aliases,
            "owners": owners,
            "sampling": "Exact integer regions of one continuous union; no tiling, modulo, mirroring, or resampling",
            "alpha_policy": "Each owner alpha byte-exact to original source alpha nearest-expanded 2x",
            "publication": "All 121 owners atomically, or all original floors; never mix a partial replacement",
        },
        "actor": {
            "direction": "E", "action": "walk", "frame_ids": [45, 46, 47, 48, 49, 50],
            "frames": actor_frames, "logical_size": [128, 128], "logical_root": [16, 64],
            "density": 4, "scale": 0.25, "frame_ticks": 7,
            "publication": "All six frames atomically; full canvas; no per-frame fitting or root adjustment",
        },
    }


def encode(registration: dict) -> bytes:
    return (json.dumps(registration, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate inputs and exact existing output; write nothing")
    parser.add_argument("--output", type=Path, help="Alternate registration output (for isolated verification)")
    args = parser.parse_args(argv)
    output = args.output or PROJECT / OUTPUT
    try:
        data = encode(build())
        if args.check:
            require(output.is_file() and output.read_bytes() == data,
                    f"Registration missing or differs from deterministic rebuild: {output}")
        else:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(data)
        print(f"{'VERIFIED' if args.check else 'BUILT'} {output}")
        print(f"SHA256 {sha256(data)}")
        print("121 ground owners (64 + 57; seven aliases excluded); 2553 original floors; six E frames")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Registration refused: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
