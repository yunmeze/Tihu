"""Prepare source-only A13 Daotong293-296 inputs. No generation or runtime work."""
from pathlib import Path
import hashlib
import itertools
import json
import sys

from PIL import Image, ImageDraw

P = Path(__file__).resolve().parents[2]
REPO = P.parent
OUT = Path(__file__).resolve().parent
SOURCE = P / "art_source/a13_npc_source"
DIAG = P / "diagnostics/a13-npc/daotong-source-v1"
sys.path.insert(0, str(P / "tools"))
from lp_original import read_pack, decode_frame
from npc.prepare_a13_npc_source import registered, delta, board

IDS = [293, 294, 295, 296]
LOCAL = [
    ("head-collar", [10, 0, 32, 19], "Narrow gold-brown head mass and broad light-gold collar. Face/age/headwear construction unresolved."),
    ("forearm-material", [0, 16, 12, 30], "Gray/light bands and warm forearm/sleeve masses. Not evidence of exposed skin or exact hidden fingers."),
    ("front-bands-material", [12, 36, 29, 54], "Paired gray front forms, white bands and small ochre bottom edges. Not proof of boot construction or contact."),
]
REVIEW_ROIS = {
    "head_core": [17, 0, 25, 10],
    "broad_collar": [10, 8, 33, 21],
    "diagonal_and_adjacent_arms": [5, 16, 41, 35],
    "lower_front_forms": [12, 40, 29, 54],
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rgba_sha(image):
    return hashlib.sha256(image.tobytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def coordinate_board(image, index):
    scale, margin = 12, 30
    background = Image.new("RGBA", image.size, (100, 107, 112, 255))
    background.alpha_composite(image)
    canvas = Image.new("RGB", (image.width * scale + margin, image.height * scale + margin), (90, 98, 105))
    canvas.paste(background.convert("RGB").resize((image.width * scale, image.height * scale), Image.Resampling.NEAREST), (margin, margin))
    draw = ImageDraw.Draw(canvas)
    for x in range(0, image.width + 1, 2):
        draw.line((margin + x * scale, margin, margin + x * scale, canvas.height), fill=(125, 130, 135))
        draw.text((margin + x * scale, 8), str(x), fill="white")
    for y in range(0, image.height + 1, 2):
        draw.line((margin, margin + y * scale, canvas.width, margin + y * scale), fill=(125, 130, 135))
        draw.text((2, margin + y * scale), str(y), fill="white")
    canvas.save(DIAG / f"source-{index}-coordinates-12x.png")


def main():
    DIAG.mkdir(parents=True, exist_ok=True)
    source_path = SOURCE / "source-contract.json"
    source = json.loads(source_path.read_text())
    npc = source["npcs"][3]
    assert (npc["name"], npc["x"], npc["y"], npc["appearance"], npc["direction"], npc["source_indices"]) == ("道童", 76, 37, 24, 1, IDS)
    native_path = REPO / "原版游戏/Data/Npc.lpRes"
    manifest_path = P / "assets/original/manifest.json"
    manifest = json.loads(manifest_path.read_text())["packs"]["Npc"]
    assert sha(native_path) == manifest["source_sha256"]
    frozen = {path: sha(path) for path in [source_path, native_path, manifest_path] + [SOURCE / source["frames"][str(i)]["file"] for i in IDS]}
    data, records, animated, key = read_pack(native_path)
    assert animated == manifest["nativeAnimation"] and key == manifest["container_key"]
    raw, canvases, frame_records, cache = [], [], [], {}
    for index in IDS:
        original = source["frames"][str(index)]
        image, meta = decode_frame(data, records[index], "Npc", animated)
        f = manifest["frames"][str(index)]
        assert all(meta[k] == f[k] for k in meta)
        assert image.size == (48, 54) and meta["offset"] == [3, -20]
        assert rgba_sha(image) == original["rgba_sha256"]
        saved = Image.open(SOURCE / original["file"]).convert("RGBA")
        assert saved.tobytes() == image.tobytes()
        atlas_path = P / manifest["pages"][f["page"]]["file"].removeprefix("res://")
        if atlas_path not in cache:
            cache[atlas_path] = Image.open(atlas_path).convert("RGBA")
        x, y, w, h = f["rect"]
        assert cache[atlas_path].crop((x, y, x + w, y + h)).tobytes() == image.tobytes()
        raw.append(image)
        canvases.append(registered(image, meta["offset"]))
        frame_records.append({"source_id": index, **original})
        coordinate_board(image, index)
    assert len({rgba_sha(im) for im in canvases}) == 4
    strip = Image.new("RGBA", (512, 160))
    for phase, im in enumerate(canvases):
        strip.paste(im, (phase * 128, 0))
    native_file = OUT / "source-four-pose-canvas-native.png"
    input_file = OUT / "source-four-pose-canvas-4x.png"
    strip.save(native_file)
    strip.resize((2048, 640), Image.Resampling.NEAREST).save(input_file)
    assert Image.open(native_file).convert("RGBA").tobytes() == strip.tobytes()
    for phase, im in enumerate(raw):
        assert strip.crop((phase * 128 + 35, 84, phase * 128 + 83, 138)).tobytes() == im.tobytes()
    inputs = [{"file": input_file.name, "sha256": sha(input_file), "role": "SOLE full-body geometry/camera/four-phase reference",
               "size": [2048, 640], "cells": [4, 1], "cell_size": [512, 640], "cell_root": [128, 416],
               "nearest_scale": 4, "contains_source_checker": True, "annotations": False}]
    written = [native_file, input_file]
    for name, box, note in LOCAL:
        crop = raw[0].crop(box)
        path = OUT / f"source-local-{name}-8x.png"
        crop.resize((crop.width * 8, crop.height * 8), Image.Resampling.NEAREST).save(path)
        inputs.append({"file": path.name, "sha256": sha(path), "source_id": 293, "raw_roi_xyxy": box, "nearest_scale": 8,
            "role": "local color/material/visible identity only; never replace whole four-phase geometry", "note": note})
        written.append(path)
    pairwise = []
    for a, b in itertools.combinations(range(4), 2):
        pairwise.append({"source_ids": [IDS[a], IDS[b]], **delta(canvases[a], canvases[b]),
            "manual_roi_pixel_changes_not_disjoint": {name: delta(raw[a].crop(box), raw[b].crop(box))["changed_visible_pixels"] for name, box in REVIEW_ROIS.items()}})
    group = next(g for g in source["groups"] if g["appearance"] == 24 and g["direction_slot"] == 1)
    assert [p["changed_visible_pixels"] for p in pairwise] == [p["changed_visible_pixels"] for p in group["pairwise_registered_comparison"]]
    for scale in (1, 6):
        board(canvases, [f"Daotong {i} p{p}" for p, i in enumerate(IDS)], scale,
              (31, 80, 87, 142), root=True).save(DIAG / f"all-four-common-crop-{scale}x.png")
    board(canvases, [str(i) for i in IDS], 10, (38, 99, 78, 121), root=False).save(DIAG / "all-four-diagonal-and-hands-10x.png")
    contract = {
        "schema": "lp-a13-daotong-source-input-v1", "status": "source preparation and constraints only; awaiting parent visual review; no generation",
        "npc": npc, "frames": frame_records, "source_contract": "res://art_source/a13_npc_source/source-contract.json", "source_contract_sha256": sha(source_path),
        "native_pack_sha256": sha(native_path), "manifest_sha256": sha(manifest_path),
        "source_verification": {"native_rgba_equals_prior_source_exports": True, "native_rgba_equals_project_atlas": True, "all_four_rgba_unique": True},
        "registration": {"native_canvas": [128, 160], "native_root": [32, 104], "raw_original_size_all_phases": [48, 54],
            "original_offset_all_phases": [3, -20], "root_in_original_raw_all_phases": [-3, 20], "registered_top_left_all_phases": [35, 84],
            "additional_per_phase_translation": [[0, 0]] * 4, "additional_per_phase_scale": [1] * 4,
            "root_is_not_anatomical_contact": True, "bbox_top_or_bottom_alignment_forbidden": True},
        "timing": {"source_fps": 50, "frame_ticks": 17, "phase_order": IDS, "loop_ticks": 68, "loop_seconds": 1.36, "global_clock": True},
        "inputs": inputs, "manual_roi_definitions": REVIEW_ROIS, "pairwise_comparisons": pairwise,
        "pairwise_limits": "RGBA deltas include shading and baked checker changes; counts are not body motion magnitude or source segmentation. ROIs overlap.",
        "family_limits": {"appearance": 24, "other_direction_slots": {"0": [289, 290, 291, 292], "2": [297, 298, 299, 300]},
            "all_12_unique_registered": len(group["identical_registered_family_groups"]) == 0,
            "exact_horizontal_mirror_pairs": group["exact_horizontal_mirror_pairs_cross_direction_cropped_rgba"],
            "other_slots_are_review_evidence_not_generation_inputs": True, "no_direction_mirroring_or_substitution": True},
        "visible_motion_read": [
            "293 diagonal shallowest, 294 upper-right end lifts inward, 295 steepest, 296 returns partway; lower-left end remains nearly anchored.",
            "Adjacent bent forearms/grip masses vary with the slender feature; head/torso/low base remain essentially fixed with minor shading/edge changes.",
            "Seated/folded describes compact silhouette only. Crossed-leg anatomy, chair, exact hands/fingers, object category and support contacts are unresolved."],
        "identity_limits": ["Name does not establish age, gender, facial features, hair, robe type or equipment.",
            "Tall narrow gold-brown upper form is a head/headwear mass; do not confidently invent a crown, hair knot, hood or helmet subtype.",
            "Two gray front forms have white bands and ochre bottoms; do not impose detailed boots, bare feet or support claims.",
            "Diagonal brown-and-pale feature must keep silhouette/angle without becoming an invented sword, staff, instrument, whisk or tool.",
            "Dark checker is baked source shadow, not solid clothing/seat/prop. Source remains untouched; a future replacement body must omit baked shadow."],
        "generation_boundary": {"generation_calls_this_stage": 0, "future_generation_requires_parent_review": True,
            "eventual_group": "one complete four-phase group in order293-296; no static duplication or per-frame replacement",
            "geometry_source": input_file.name, "identity_inputs": [i["file"] for i in inputs[1:]],
            "hero_full_body_reference": False, "new_facial_or_hidden_limb_design": False,
            "preserve_names_story_cells_clicks": True, "runtime_changes": False, "prior_two_npc_shadow_stage_changes": False},
        "review_files": ["SOURCE_REVIEW.md", "GENERATION_GUIDANCE.md"],
        "diagnostics": "diagnostics/a13-npc/daotong-source-v1"}
    path = OUT / "source-input-contract.json"
    write(path, contract)
    written += [path, Path(__file__), OUT / "SOURCE_REVIEW.md", OUT / "GENERATION_GUIDANCE.md"]
    for path, digest in frozen.items():
        assert sha(path) == digest, f"Source changed: {path}"
    assert all(p.is_file() for p in written)
    manifest_file = OUT / "GIT_SAVE_SOURCE.json"
    write(manifest_file, {"stage": "Daotong293-296 source preparation only; no generated art or runtime", "files": [
        {"file": p.relative_to(REPO).as_posix(), "sha256": sha(p), "bytes": p.stat().st_size} for p in written],
        "include_manifest_itself": True, "diagnostics_ignored": True})
    print(json.dumps({"file": str(manifest_file), "sha256": sha(manifest_file), "files_plus_manifest": len(written) + 1}, indent=2))


if __name__ == "__main__":
    main()
