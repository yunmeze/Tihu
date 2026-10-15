"""Read-only original A13 NPC preparation. Never executes EXE, scripts or Godot.

Only writes art_source/a13_npc_source and ignored diagnostics/a13-npc.
Character pixels are decoded/cropped/resized only, never drawn or invented.
Run from any directory with Python 3 + Pillow.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

P = Path(__file__).resolve().parents[2]
ROOT = P.parent
sys.path.insert(0, str(P / "tools"))
from lp_original import Reader, decode_frame, read_pack
from extract_a13_original import parse_map

OUT = P / "art_source/a13_npc_source"
DIAG = P / "diagnostics/a13-npc"
CANVAS = (128, 160)
ORIGIN = (32, 104)
KEYS = {(21, 2): "fangzhang", (9, 1): "lingyunzi"}
KEY_PARTS = {
    "fangzhang": [
        ("head-band", [22, 0, 38, 14], "Dark head top and white band; cap versus hair detail unresolved."),
        ("arm-wrap-material", [3, 10, 19, 23], "Visible exposed upper arm and dark wrist wrap, not a staff."),
        ("waist-cloth-material", [17, 25, 34, 38], "Dark forearm/waist overlap and light belt/cloth. Do not reinterpret dark body as shadow."),
    ],
    "lingyunzi": [
        ("tall-headwear", [10, 0, 22, 25], "Tall head-attached form, sampled with face; not a free-standing wooden staff."),
        ("sleeve-material", [0, 21, 12, 39], "Gray wide sleeve with dark folds; no pose transfer from this isolated crop."),
        ("hands-hanging-detail", [10, 33, 23, 51], "Hands overlap a thin hanging detail; exact object, fingers and rear hand remain unresolved."),
    ],
}


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    return sha_bytes(path.read_bytes())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def registered(image, offset):
    pos = (ORIGIN[0] + offset[0], ORIGIN[1] + offset[1])
    assert min(pos) >= 0
    assert pos[0] + image.width <= CANVAS[0]
    assert pos[1] + image.height <= CANVAS[1]
    result = Image.new("RGBA", CANVAS)
    result.paste(image, pos)  # No alpha mask: retain exact RGBA, including hidden RGB.
    assert result.crop((*pos, pos[0] + image.width, pos[1] + image.height)).tobytes() == image.tobytes()
    return result


def delta(a, b):
    pa, pb = a.tobytes(), b.tobytes()
    pixels = [(pa[i:i + 4], pb[i:i + 4]) for i in range(0, len(pa), 4)]
    changed = [p != q for p, q in pixels]
    visible_changed = [p != q and (p[3] or q[3]) for p, q in pixels]
    mask = Image.new("L", a.size)
    mask.putdata([255 if value else 0 for value in visible_changed])
    return {"identical_rgba": a.tobytes() == b.tobytes(),
            "changed_rgba_pixels": sum(changed),
            "changed_visible_pixels": sum(bool(v) for v in visible_changed),
            "changed_visible_bbox_canvas_xyxy": list(mask.getbbox()) if mask.getbbox() else None}


def union_bbox(images):
    boxes = [im.getbbox() for im in images if im.getbbox()]
    return (min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes))


def board(images, labels, scale=4, box=None, root=False):
    box = box or (0, 0, *CANVAS)
    w, h = box[2] - box[0], box[3] - box[1]
    result = Image.new("RGB", (len(images) * w * scale, h * scale + 36), (66, 72, 76))
    draw = ImageDraw.Draw(result)
    font = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 16)
    for i, (im, label) in enumerate(zip(images, labels)):
        bg = Image.new("RGBA", (w, h), (100, 107, 112, 255))
        bg.alpha_composite(im.crop(box))
        result.paste(bg.convert("RGB").resize((w * scale, h * scale), Image.Resampling.NEAREST), (i * w * scale, 36))
        draw.text((i * w * scale + 4, 5), label, font=font, fill="white")
        if root and box[0] <= ORIGIN[0] < box[2] and box[1] <= ORIGIN[1] < box[3]:
            x = (i * w + ORIGIN[0] - box[0]) * scale
            y = (ORIGIN[1] - box[1]) * scale + 36
            draw.line((x - 7, y, x + 7, y), fill="#00ffff", width=1)
            draw.line((x, y - 7, x, y + 7), fill="#00ffff", width=1)
    return result


def coordinate_board(image, index):
    """Pixel coordinates on a diagnostic only; never alters source input art."""
    scale, margin = 10, 32
    result = Image.new("RGB", (image.width * scale + 42, image.height * scale + 42), (90, 100, 108))
    bg = Image.new("RGBA", image.size, (100, 107, 112, 255))
    bg.alpha_composite(image)
    result.paste(bg.convert("RGB").resize((image.width * scale, image.height * scale), Image.Resampling.NEAREST), (margin, margin))
    draw = ImageDraw.Draw(result)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    for x in range(0, image.width + 1, 5):
        draw.line((margin + x * scale, margin, margin + x * scale, margin + image.height * scale), fill=(120, 125, 130))
        draw.text((margin + x * scale, 12), str(x), font=font, fill="white")
    for y in range(0, image.height + 1, 5):
        draw.line((margin, margin + y * scale, margin + image.width * scale, margin + y * scale), fill=(120, 125, 130))
        draw.text((3, margin + y * scale), str(y), font=font, fill="white")
    result.save(DIAG / f"source-{index}-coordinates-10x.png")


def map_npc_records(native):
    reader = Reader((ROOT / native["source"]).read_bytes(), 3, native["tailOffset"])
    for _ in range(reader.short()):
        for _ in range(4):
            reader.short()
        reader.string()
    result = []
    for i in range(reader.short()):
        start = reader.pos
        values = [reader.short() for _ in range(4)]
        name = reader.string()
        script_field = reader.pos
        script = reader.string()
        npc = native["npcs"][i]
        assert values == [npc[k] for k in ["x", "y", "appearance", "direction"]]
        assert name == npc["name"] and script == npc["script"]
        result.append({"source_record_offset": start, "source_record_end": reader.pos,
                       "script_field_offset": script_field, "script_sha256_utf8": sha_bytes(script.encode())})
    return result


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    DIAG.mkdir(parents=True, exist_ok=True)
    native_map = ROOT / "原版游戏/Data/Map/A13.lpMap"
    native_pack = ROOT / "原版游戏/Data/Npc.lpRes"
    map_path = P / "data/maps/A13.json"
    manifest_path = P / "assets/original/manifest.json"
    ref_index = ROOT / "参考项目/public/assets/sprites/Npc/index.json"
    frozen = [native_map, native_pack, map_path, manifest_path, ref_index,
              ROOT / "参考项目/src/map-effects.js", ROOT / "参考项目/src/game.js"]
    before = {str(f.relative_to(ROOT)): sha(f) for f in frozen}
    native = parse_map(native_map)
    current = json.loads(map_path.read_text())
    assert all(native[k] == current[k] for k in native)
    native_records = map_npc_records(native)
    pack = json.loads(manifest_path.read_text())["packs"]["Npc"]
    reference = json.loads(ref_index.read_text())
    assert sha(native_pack) == pack["source_sha256"]
    data, records, animated, key = read_pack(native_pack)
    assert animated == pack["nativeAnimation"] and key == pack["container_key"]
    atlas_cache = {}
    groups = defaultdict(list)
    for i, npc in enumerate(native["npcs"]):
        groups[(npc["appearance"], npc["direction"])].append(i)
    decoded, frames, comparisons = {}, {}, []
    for appearance, direction in groups:
        for phase in range(4):
            index = 1 + appearance * 12 + direction * 4 + phase
            im, meta = decode_frame(data, records[index], "Npc", animated)
            frame = pack["frames"][str(index)]
            assert all(meta[k] == frame[k] for k in meta)
            for source_pack, base, tag in [(pack, P, "project"), (reference, ROOT / "参考项目/public/assets", "reference")]:
                f = source_pack["frames"][str(index)] if tag == "project" else source_pack["frames"][index]
                atlas_path = base / source_pack["pages"][f["page"]]["file"].removeprefix("res://")
                if atlas_path not in atlas_cache:
                    atlas_cache[atlas_path] = Image.open(atlas_path).convert("RGBA")
                x, y, w, h = f["rect"]
                crop = atlas_cache[atlas_path].crop((x, y, x + w, y + h))
                assert crop.tobytes() == im.crop(tuple(meta["reference_extraction_bounds"])).tobytes()
                assert all(f[k] == frame[k] for k in ["original", "offset", "crop"])
                comparisons.append({"index": index, "atlas": tag, "rgba_and_metadata_equal": True})
            file = OUT / "original_rgba" / f"npc-{index:04}.png"
            file.parent.mkdir(exist_ok=True)
            im.save(file)
            assert Image.open(file).convert("RGBA").tobytes() == im.tobytes()
            decoded[index] = im
            frames[str(index)] = {**meta, "file": str(file.relative_to(OUT)), "file_sha256": sha(file),
                "phase": phase, "appearance": appearance, "direction_slot": direction,
                "root_in_original_canvas": [-meta["offset"][0], -meta["offset"][1]],
                "registered_top_left": [ORIGIN[0] + meta["offset"][0], ORIGIN[1] + meta["offset"][1]],
                "visible_alpha_bbox_original_xyxy": list(im.getbbox()),
                "root_meaning": "Native cell draw origin; NOT a confirmed anatomical foot contact.",
                "atlas_reference": {k: frame[k] for k in ["page", "rect", "crop"]}}
    group_records, overview = [], []
    for (appearance, direction), ids in groups.items():
        first = 1 + appearance * 12 + direction * 4
        indices = list(range(first, first + 4))
        images = [registered(decoded[i], frames[str(i)]["offset"]) for i in indices]
        pairs = [{"source_indices": [indices[a], indices[b]], **delta(images[a], images[b])}
                 for a, b in itertools.combinations(range(4), 2)]
        names = [native["npcs"][i]["name"] for i in ids]
        slug = f"appearance-{appearance:02}-direction-{direction}"
        directory = DIAG / slug
        directory.mkdir(exist_ok=True)
        labels = [f"{names[0]} | source {i} | phase {j}" for j, i in enumerate(indices)]
        board(images, labels, 4, root=True).save(directory / "all-four-registered-4x.png")
        bbox = union_bbox(images)
        box = (max(0, bbox[0] - 4), max(0, bbox[1] - 4), min(CANVAS[0], bbox[2] + 4), min(CANVAS[1], bbox[3] + 4))
        board(images, labels, 6, box, root=True).save(directory / "all-four-common-crop-6x.png")
        board(images, [str(i) for i in indices], 8, (box[0], max(box[1], box[3] - 40), box[2], box[3]), root=True).save(directory / "all-four-lower-8x.png")
        overview.append(board(images, [f"{names[0]} {i}" for i in indices], 2, box))
        strip = Image.new("RGBA", (CANVAS[0] * 4, CANVAS[1]))
        for phase, im in enumerate(images):
            strip.paste(im, (phase * CANVAS[0], 0))
        strip.save(directory / "source-four-registered-native.png")
        art_inputs = []
        if (appearance, direction) in KEYS:
            key_dir = OUT / KEYS[(appearance, direction)]
            key_dir.mkdir(exist_ok=True)
            file = key_dir / "source-four-pose-canvas-4x.png"
            strip.resize((strip.width * 4, strip.height * 4), Image.Resampling.NEAREST).save(file)
            art_inputs.append({"purpose": "complete original four-phase pose only; no identity transfer from another NPC",
                               "file": str(file.relative_to(OUT)), "sha256": sha(file), "scale": 4,
                               "cell_size": [CANVAS[0] * 4, CANVAS[1] * 4],
                               "root_in_each_cell": [v * 4 for v in ORIGIN]})
            coordinate_board(decoded[first], first)
            for label, raw_box, limit in KEY_PARTS[KEYS[(appearance, direction)]]:
                part = decoded[first].crop(raw_box)
                file = key_dir / f"source-local-{label}-8x.png"
                part.resize((part.width * 8, part.height * 8), Image.Resampling.NEAREST).save(file)
                art_inputs.append({"purpose": "local original identity/material evidence only; not an approved new-style design",
                    "source_index": first, "source_box_xyxy": raw_box, "scale": 8, "limitation": limit,
                    "file": str(file.relative_to(OUT)), "sha256": sha(file)})
        # Inspect all 12 original family records, without substituting other direction slots.
        family_images, family_meta = [], []
        for index in range(1 + appearance * 12, 13 + appearance * 12):
            im, meta = decode_frame(data, records[index], "Npc", animated)
            family_images.append(im)
            family_meta.append({"index": index, "direction_slot": (index - 1 - appearance * 12) // 4,
                                "phase": (index - 1) % 4, **meta})
        exact_groups = defaultdict(list)
        for f in family_meta:
            exact_groups[(tuple(f["original"]), tuple(f["offset"]), f["rgba_sha256"])].append(f["index"])
        mirrors = []
        for a, b in itertools.combinations(range(12), 2):
            if a // 4 == b // 4:
                continue
            ia, ib = family_images[a], family_images[b]
            if ia.size == ib.size and ia.tobytes() != ib.tobytes() and ImageOps.mirror(ia).tobytes() == ib.tobytes():
                mirrors.append([family_meta[a]["index"], family_meta[b]["index"]])
        # Full source canvases; different directions may have distinct offsets/extents.
        rows = []
        for d in range(3):
            fs = family_meta[d * 4:d * 4 + 4]
            ims = [registered(im, f["offset"]) for im, f in zip(family_images[d * 4:d * 4 + 4], fs)]
            rows.append(board(ims, [f"slot {d}: {f['index']}" for f in fs], 3, root=True))
        family_board = Image.new("RGB", (rows[0].width, sum(row.height for row in rows)))
        yy = 0
        for row in rows:
            family_board.paste(row, (0, yy)); yy += row.height
        family_board.save(directory / "family-three-slots-four-phases-3x.png")
        group_records.append({"id": slug, "appearance": appearance, "direction_slot": direction,
            "npc_record_indices": ids, "npc_names": names, "source_indices": indices,
            "unique_registered_rgba_phases": len({im.tobytes() for im in images}),
            "remaster_phase_policy": ("One static remastered pose may be reused by all four source indices while preserving 17-tick indexing. Do not invent breathing or jitter."
                if len({im.tobytes() for im in images}) == 1 else "Generate/review all four phases as one group. Preserve each source offset/root and phase difference; never align by crop top."),
            "pairwise_registered_comparison": pairs,
            "all_12_family_record_metadata": family_meta,
            "identical_registered_family_groups": [v for v in exact_groups.values() if len(v) > 1],
            "exact_horizontal_mirror_pairs_cross_direction_cropped_rgba": mirrors,
            "mirror_test_limits": "Exact raster test only; not semantic equivalence or permission to mirror. Current runtime has no NPC flip.",
            "generation_inputs": art_inputs})
    for batch_start in range(0, len(overview), 3):
        rows = overview[batch_start:batch_start + 3]
        b = Image.new("RGB", (max(row.width for row in rows), sum(row.height for row in rows)), (66, 72, 76))
        yy = 0
        for row in rows:
            b.paste(row, (0, yy)); yy += row.height
        b.save(DIAG / f"all-a13-groups-{batch_start // 3 + 1}.png")
    npcs = []
    for i, n in enumerate(native["npcs"]):
        first = 1 + n["appearance"] * 12 + n["direction"] * 4
        npcs.append({"record_index": i, **{k: n[k] for k in ["name", "appearance", "direction", "x", "y"]},
            **native_records[i], "source_indices": list(range(first, first + 4)),
            "source_group": f"appearance-{n['appearance']:02}-direction-{n['direction']}",
            "world_cell_draw_origin": [n["x"] * 48, n["y"] * 32],
            "layer": 1, "sort_y": n["y"], "stable_order": native["width"] * native["height"] + i,
            "visibility_scope": "Native map record only. Actual visibility remains controlled by original scripts, not by art preparation."})
    contract = {"schema": "a13-npc-original-source-v1", "status": "source-only; no generated art or runtime edits",
        "sources": before, "counts": {"npc_records": len(npcs), "appearance_direction_groups": len(groups), "required_original_frames": len(frames)},
        "index_formula": "1 + appearance * 12 + direction_slot * 4 + phase_0_to_3",
        "source_clock": {"fps": 50, "ticks_per_phase": 17, "seconds_per_phase": .34, "ticks_per_loop": 68, "seconds_per_loop": 1.36,
            "order": [0, 1, 2, 3], "tick_windows_inclusive": [[0, 16], [17, 33], [34, 50], [51, 67]],
            "phase_formula": "floor(tick / 17) % 4", "sync": "shared current/reference global tick, not one per NPC",
            "evidence": ["Project/data/maps/A13.json render_contract", "Project/scripts/world_view.gd", "参考项目/src/map-effects.js", "参考项目/src/game.js", "参考项目/tools/inspect-map-effects.py"],
            "scope": "Current/reference cadence. Reference inspection records a native 0x11 constant, but this preparation does not execute or independently trace native EXE lifecycle."},
        "registration": {"canvas_size": list(CANVAS), "cell_draw_origin": list(ORIGIN),
            "raw_world_top_left": "cell_world + original offset", "atlas_world_top_left": "cell_world + original offset + atlas crop",
            "registered_raw_top_left": "cell_draw_origin + original offset", "root_warning": "Native cell draw origin is not anatomical foot/pelvis center. Do not align by alpha bbox, shadow extremum, or per-phase recentering.",
            "direction_warning": "NPC has three stored direction slots. These are not the hero's 8-direction indices. No mirroring is authorized or introduced."},
        "alpha_and_shadow": {"decoder": "Project/tools/lp_original.py decode_frame", "policy": "Original black key policy only; retain exact original RGB and nonblack baked checker pixels. No shadow/body segmentation.",
            "baked_shadow_mask": None, "anatomical_foot_contacts": None,
            "warning": "Alpha bounds include baked shadows, props and dark hems. They are not a floor contact mask. Exact black was already keyed by decoder; further color thresholding could erase body/prop pixels."},
        "npcs": npcs, "groups": group_records, "frames": frames,
        "generation_boundary": ["Process one NPC identity and its four source phases together.", "Use source-four-pose-canvas-4x only as the pose, facing, scale and offset authority.", "Future clean science-fiction cultivation identity/material input must be approved separately; use local material/identity crops, not another full-body pose.", "Preserve existing visible head/hair/clothing/prop evidence; do not invent age, role, equipment or anatomy from name alone.", "Static identical source phases may share one remastered pose under all four original indices and unchanged 17-tick cadence. Do not invent breathing or jitter.", "Appearance72 is a humanoid holding a long diagonal pole-shaped object despite names 混元之气 and 终极试炼. Never replace it with a gas/orb effect based on the names.", "Preserve all original NPC names, map placement and story functions. This art preparation never edits scripts.", "Preserve occluded hands/feet as occluded; do not fill hidden anatomy or add a wooden staff to explain ambiguous pixels.", "Future generated body/shadow separation requires a new explicit review. Original checker shadow is evidence, not a correct generated shadow or an anatomical anchor."]}
    review_path = OUT / "MANUAL_VISUAL_REVIEW.json"
    if review_path.exists():
        review = json.loads(review_path.read_text())
        assert {(g["appearance"], g["direction_slot"]) for g in review["groups"]} == set(groups)
        contract["manual_visual_review"] = {"file": review_path.name, "sha256": sha(review_path),
            "scope": "Human-viewed complete four-phase enlarged source boards; uncertain anatomy/props are explicitly unresolved."}
    write(OUT / "source-contract.json", contract)
    assert before == {str(f.relative_to(ROOT)): sha(f) for f in frozen}
    unique_registered = len({registered(decoded[int(i)], frame["offset"]).tobytes() for i, frame in frames.items()})
    assert (len(npcs), len(groups), len(frames), unique_registered) == (11, 10, 40, 31)
    report = {"status": "PASS", **contract["counts"], "distinct_registered_rgba_canvases": unique_registered, "atlas_comparisons": len(comparisons),
              "original_rgba_roundtrip": len(frames), "frozen_input_hashes_unchanged": len(frozen),
              "all_three_direction_families_inspected_as_data": len(groups),
              "source_contract_sha256": sha(OUT / "source-contract.json"), "comparisons": comparisons}
    write(DIAG / "extraction-audit.json", report)
    # Explicit source-owned list, not a recursive add of future candidates/import sidecars.
    files = [Path(__file__), OUT / "source-contract.json"]
    files += [OUT / name for name in ["README.md", "VISUAL_REVIEW.md", "MANUAL_VISUAL_REVIEW.json"] if (OUT / name).exists()]
    files += [OUT / frame["file"] for frame in frames.values()]
    files += [OUT / source["file"] for group in group_records for source in group["generation_inputs"]]
    files = sorted(set(files))
    write(OUT / "PRODUCTION_FILES_SHA256.json", {"schema": "minimal-a13-npc-source-files-v1", "scope": "Only new owned script, contracts, documentation and necessary original inputs; diagnostics excluded.",
        "files": [{"file": str(f.relative_to(ROOT)), "sha256": sha(f), "bytes": f.stat().st_size} for f in files]})
    print(json.dumps({k: v for k, v in report.items() if k != "comparisons"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
