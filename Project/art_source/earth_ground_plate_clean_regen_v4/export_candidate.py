"""Export an entire v4 plate into exact source owners. No runtime or image-art edits."""
from pathlib import Path
import hashlib
import json
import shutil
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
P = HERE.parents[1]
OUT = P / "assets/earth/environment/ground_plate_v4"
RAW = HERE / "raw.png"
SOURCE = P / "art_source/earth_ground_plate_source_v1/source-layout-contract.json"
RAW_SHA256 = "a44d861c4485cb8596fb42681441675d1b9cefb3d8c48261113325c14492ae2f"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save_json(p, value):
    temp = p.with_suffix(".json.tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    temp.replace(p)


def main():
    source = json.loads(SOURCE.read_text())
    map_path = P / "data/maps/A13.json"
    manifest_path = P / "assets/original/manifest.json"
    assert sha(map_path) == source["source_hashes"]["data/maps/A13.json"]
    assert sha(manifest_path) == source["source_hashes"]["assets/original/manifest.json"]
    assert sha(RAW) == RAW_SHA256
    assert source["world_bounds_xyxy_half_open"] == [2496, 960, 3264, 1472]
    assert source["scope"]["selected_floor_owners"] == 64
    raw = Image.open(RAW).convert("RGB")
    assert raw.size == (1536, 1024)
    m = json.loads(map_path.read_text())
    packs = json.loads(manifest_path.read_text())["packs"]
    OUT.mkdir(parents=True, exist_ok=True)
    # This full texture is a byte-for-byte copy of v4 raw, for shared-canvas sampling.
    shutil.copyfile(RAW, OUT / "plate.png")
    assert sha(OUT / "plate.png") == RAW_SHA256
    rgba_raw = raw.convert("RGBA")
    roundtrip = Image.new("RGBA", raw.size)
    coverage = np.zeros((1024, 1536), dtype=np.uint8)
    pages = {}
    owners = []
    for o in source["selected_owners_in_source_draw_order"]:
        cx, cy = o["cell"]
        order = cx * m["height"] + cy
        assert order == o["stable_source_order"] and m["cells"][order] == o["source_cell"]
        assert o["pack"] == "Map/Res/FloorBig" and o["frame_index"] == -o["source_cell"][0]
        frame = packs[o["pack"]]["frames"][str(o["frame_index"])]
        x, y, w, h = o["world_rect"]
        assert [x, y] == [cx * 48 + frame["crop"][0], cy * 32 + frame["crop"][1]]
        assert [w, h] == frame["rect"][2:] == [96, 64]
        px, py = (x - 2496) * 2, (y - 960) * 2
        region = [px, py, w * 2, h * 2]
        tile = rgba_raw.crop((px, py, px + w * 2, py + h * 2))
        page_path = packs[o["pack"]]["pages"][frame["page"]]["file"]
        if page_path not in pages:
            pages[page_path] = Image.open(P / page_path[6:]).convert("RGBA")
        ax, ay, aw, ah = frame["rect"]
        source_alpha = pages[page_path].crop((ax, ay, ax + aw, ay + ah)).getchannel("A")
        assert source_alpha.getextrema() == (255, 255)
        alpha_2x = source_alpha.resize((aw * 2, ah * 2), Image.Resampling.NEAREST)
        tile.putalpha(alpha_2x)
        assert tile.tobytes() == rgba_raw.crop((px, py, px + w * 2, py + h * 2)).tobytes()
        filename = f"tile-{cx}-{cy}.png"
        path = OUT / filename
        tile.save(path)
        saved = Image.open(path).convert("RGBA")
        assert saved.size == (192, 128) and saved.tobytes() == tile.tobytes()
        roundtrip.alpha_composite(saved, (px, py))
        coverage[py:py + h * 2, px:px + w * 2] += 1
        owners.append({**o, "layer": 0, "sort_y": cy, "source_flag": o["source_cell"][1],
                       "layer_semantics": "floor pass tag, not object layer_for_flag; source floors always precede objects",
                       "world_top_left": [x, y], "logical_size": [w, h], "scale": .5,
                       "texture_density": 2, "texture": "res://" + str(path.relative_to(P)),
                       "texture_size": [192, 128], "texture_sha256": sha(path),
                       "source_alpha_sha256": hashlib.sha256(source_alpha.tobytes()).hexdigest(),
                       "texture_alpha_sha256": hashlib.sha256(alpha_2x.tobytes()).hexdigest(),
                       "shared_region_px": region, "raw_derivation": "direct integer crop of full v4 raw; no resample or earlier-generated RGB"})
    assert len(owners) == len({o["key"] for o in owners}) == 64
    assert np.all(coverage == 1)
    assert roundtrip.tobytes() == rgba_raw.tobytes()
    assert sha(RAW) == RAW_SHA256 and sha(OUT / "plate.png") == RAW_SHA256
    layout = json.loads((HERE / "review.json").read_text())["source_layout"]
    # Frozen manually reviewed record, not a new permissive automatic fit threshold.
    # Parent accepted its edge-case uncertainty after native joint scene review.
    assert len(layout["samples"]) == 6
    assert abs(layout["maximum_center_distance_logical"] - 3.0413812651491097) < 1e-12
    assert layout["source_manual_read_uncertainty_logical"] == 3
    assert layout["v4_manual_read_uncertainty_raw"] == 3
    registration = {
        "schema": "earth-ground-plate-v4", "status": "bounded64-owner independent Earth sample candidate approved after native joint2x; warm highlights/shared lighting remain under review",
        "map": "A13", "world_bounds_xyxy_half_open": [2496, 960, 3264, 1472], "logical_size": [768, 512],
        "texture_density": 2, "owner_count": 64, "atomic_group": "earth-ground-plate-v4-bounded64",
        "source_map_sha256": sha(map_path), "source_manifest_sha256": sha(manifest_path),
        "source_contract": "art_source/earth_ground_plate_source_v1/source-layout-contract.json", "source_contract_sha256": sha(SOURCE),
        "scope_rule": "exact listed original owner keys only; not all occurrences of their signed IDs; original outside scope",
        "shared_plate": {"texture": "res://assets/earth/environment/ground_plate_v4/plate.png", "texture_size": [1536, 1024],
                         "texture_sha256": RAW_SHA256, "world_top_left": [2496, 960], "scale": .5,
                         "sampling": "all owners use shared_region_px on this single continuous image; world-locked, no modulo/mirror/repeat"},
        "owners": owners, "floor_order": "source x-major stable order; all floor owners before original object/actor stream",
        "alpha_policy": "every exact original owner alpha nearest-expanded2x; all source alpha255 verified within this scope",
        "filter": "nearest safe initial true2x view; linear requires native shared-canvas seam check. Split textures have no gutters.",
        "fallback": "validate entire64-owner exact trusted source scope before publication; on any failure use all64 original floors, never partial replacement",
        "shadow": "none supplied; no new cast baked in plate; separate shared-light static/actor receiver checks remain",
        "provenance": {"v4_raw": str(RAW.relative_to(P)), "v4_raw_sha256": RAW_SHA256,
                       "generation": str((HERE / "generation.json").relative_to(P)), "generation_sha256": sha(HERE / "generation.json"),
                       "prompt_sha256": sha(HERE / "prompt.txt"), "source_layout_review_sha256": sha(HERE / "review.json"),
                       "earlier_generated_pixels_mixed": False, "resampled_or_warped": False,
                       "clean_source_semantic_generation": True, "entire_pavement_material_redraw_authorized": True,
                       "whole_plate_reassessment": "Native joint2x reviewed and bounded sample approved. Largest six-center read is3.041 logicalpx against source+/-3 and current+/-1.5 logical read uncertainty; not proven exact outer-edge alignment or hard excess. No new route; grass gap retained."},
        "limitations": ["Not installed by export script; imported/GPU dimensions and source toggle need unique runtime owner's verification.",
                        "Warm yellow grass highlights remain for later shared-light/hall review; do not independently reroll color.",
                        "Top-right cap center is at the finite read-budget boundary; no precise outer-edge/curb thickness claim.",
                        "No new shadow, actor environment shading, or elevated receiver proof.",
                        "Scene outside small plate remains original."]}
    # Publish manifest only after every file and roundtrip check passed.
    save_json(OUT / "registration.json", registration)
    qa = {"status": "offline export checks pass; native validation pending", "owner_count": 64,
          "texture_count": 65, "each_split_size": [192, 128], "shared_plate_size": [1536, 1024],
          "density": 2, "coverage_min_max": [int(coverage.min()), int(coverage.max())],
          "reconstructed_rgba_byte_exact_to_v4": True, "all_source_alpha255": True, "alpha_source_exact2x": True,
          "v4_raw_sha256": RAW_SHA256, "raw_unmodified": True, "earlier_generated_pixels_mixed": False,
          "map_and_manifest_source_hash_match": True, "registration_sha256": sha(OUT / "registration.json"),
          "runtime_scripts_modified": False, "godot_or_exe_executed": False}
    save_json(HERE / "export-review.json", qa)
    print(json.dumps(qa))


if __name__ == "__main__":
    main()
