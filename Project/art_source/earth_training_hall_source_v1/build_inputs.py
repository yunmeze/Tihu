"""Reconstruct source evidence and crop an approved reference. No art synthesis/runtime edits.

Run from any cwd: python Project/art_source/earth_training_hall_source_v1/build_inputs.py
All writes stay beside this script. Original/extracted source files are read-only.
"""
from pathlib import Path
import hashlib
import json
from collections import Counter

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent
PROJECT = OUT.parents[1]
FROZEN = {
    "art_source/a13_main_temple_source/source-group-contract.json": "30a726db95de66c5ec266ebea7d5d0903a84ebd5f478b3f2778f9e649123d0d3",
    "data/maps/A13.json": "d09549838963c8157307cc5406d3118baf69259d82459bcba0a3a8be5b34aa27",
    "assets/original/manifest.json": "506fba1f0fd826589046d38e4ebd5285ee9a11e3235cd78495cdd133c2e63837",
    "assets/original/Map/Res/Building/0.png": "6fc88a1aa96eb18687eea798bcb4eae1f0ebf6d546a5a076fb1c2546550b3343",
    "art_source/earth_base_style_concept_v1/concept.png": "1beaf20bbda18d0e04fcf2f6e81a0028750e1b87224f21780393b00c36cc4fc5",
}
CONCEPT_CROP = (704, 0, 1448, 352)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def main():
    for relative, expected in FROZEN.items():
        actual = sha(PROJECT / relative)
        assert actual == expected, ("Input changed; review before rebuilding", relative, actual)

    source = json.loads((PROJECT / "art_source/a13_main_temple_source/source-group-contract.json").read_text())
    map_data = json.loads((PROJECT / "data/maps/A13.json").read_text())
    manifest = json.loads((PROJECT / "assets/original/manifest.json").read_text())
    pack = manifest["packs"]["Map/Res/Building"]
    owners = source["owners_in_draw_order"]
    bounds = source["world_bounds_xyxy"]
    size = tuple(source["composite_size"])
    assert len(owners) == 30
    assert sorted(o["frame_index"] for o in owners) == list(range(3966, 3996))
    assert Counter(o["layer"] for o in owners) == {0: 12, 1: 18}
    assert bounds == [2948, 642, 3744, 1307] and size == (796, 665)
    assert owners == sorted(owners, key=lambda o: (o["layer"], o["sort_y"], o["stable_source_order"]))

    pages = {}
    composite = Image.new("RGBA", size)
    support = Image.new("RGBA", size)
    for o in owners:
        cell_index = o["cell_linear_index"]
        assert map_data["cells"][cell_index] == o["source_cell"]
        assert [cell_index // map_data["height"], cell_index % map_data["height"]] == o["cell"]
        assert o["sort_y"] == o["cell"][1] and o["stable_source_order"] == cell_index
        frame = pack["frames"][str(o["frame_index"])]
        assert frame["rect"] == o["atlas_rect"] and frame["crop"] == o["crop"]
        assert frame["original"] == o["original_canvas"]
        assert frame["offset"] == o["source_frame_offset_ignored"]
        path = PROJECT / o["atlas_page"].removeprefix("res://")
        assert str(path.relative_to(PROJECT)) in FROZEN
        if path not in pages:
            pages[path] = Image.open(path).convert("RGBA")
        x, y, w, h = o["atlas_rect"]
        piece = pages[path].crop((x, y, x + w, y + h))
        assert sum(a > 0 for a in piece.getchannel("A").tobytes()) == o["visible_alpha_pixels"]
        wx = o["cell"][0] * 48 + frame["crop"][0]
        wy = o["cell"][1] * 32 + 32 - frame["original"][1] + frame["crop"][1]
        assert [wx, wy, w, h] == o["world_rect"]
        xy = (wx - bounds[0], wy - bounds[1])
        composite.alpha_composite(piece, xy)
        if o["layer"] == 0:
            support.alpha_composite(piece, xy)
    composite.save(OUT / "source-full.png")

    concept = Image.open(PROJECT / "art_source/earth_base_style_concept_v1/concept.png")
    assert concept.size == (1448, 1086)
    crop = concept.crop(CONCEPT_CROP)
    crop.save(OUT / "concept-building-crop.png")
    assert Image.open(OUT / "concept-building-crop.png").tobytes() == crop.tobytes()

    # Annotated source-only diagnostics. No new architectural pixels are drawn.
    # Door points are approximate physical threshold samples, not portal/collision edits.
    door_points = [
        {"id": "D0_left_visible_threshold", "source_composite_xy": [264, 441], "world_xy": [3212, 1083],
         "manual_read_uncertainty_px": 8, "approximate_visible_opening_region_xyxy": [243, 336, 286, 458],
         "note": "Manual visible floor/sill sample in left-facing facade; upper extent partly roof-occluded. Not a portal anchor, route target or exact aperture mask."},
        {"id": "D1_right_visible_threshold", "source_composite_xy": [550, 482], "world_xy": [3498, 1124],
         "manual_read_uncertainty_px": 8, "approximate_visible_opening_region_xyxy": [523, 373, 580, 503],
         "note": "Manual visible floor/sill sample in right-facing facade; partly obscured by door leaf/foreground. Not a portal anchor, route target or exact aperture mask."},
    ]
    board = Image.new("RGB", (size[0] * 2, size[1] + 32), (66, 76, 79))
    left = Image.new("RGBA", size, (86, 96, 99, 255))
    left.alpha_composite(composite)
    right = Image.new("RGBA", size, (86, 96, 99, 255))
    right.alpha_composite(support)
    board.paste(left.convert("RGB"), (0, 32))
    board.paste(right.convert("RGB"), (size[0], 32))
    draw = ImageDraw.Draw(board)
    draw.text((10, 9), "SOURCE ONLY: C/S support anchors; D approximate door samples; E coverage only", fill="white")
    draw.text((size[0] + 10, 9), "12 SOURCE LAYER-0 OWNERS: cell outlines, not a new floor/collision polygon", fill="white")
    for point in source["manual_visible_landmarks"] + door_points:
        x, y = point["source_composite_xy"]
        y += 32
        code = point["id"].split("_")[0]
        color = "cyan" if code[0] in "CS" else "orange" if code[0] == "D" else "yellow"
        draw.ellipse((x - 4, y - 4, x + 4, y + 4), outline=color, width=2)
        draw.text((x + 7, y - 9), code, fill=color)
    for o in owners:
        if o["layer"] != 0:
            continue
        x = o["cell"][0] * 48 - bounds[0] + size[0]
        y = o["cell"][1] * 32 - bounds[1] + 32
        draw.rectangle((x, y, x + 47, y + 31), outline="cyan")
        draw.text((x + 2, y + 2), str(o["frame_index"]), fill="white")
    board.save(OUT / "source-geometry-review.png")

    support_owners = [
        {"key": o["key"], "cell": o["cell"], "flag": o["flag"], "layer": o["layer"],
         "sort_y": o["sort_y"], "stable_source_order": o["stable_source_order"],
         "logical_cell_rect_xywh": [o["cell"][0] * 48, o["cell"][1] * 32, 48, 32],
         "actual_source_draw_rect_xywh": o["world_rect"]}
        for o in owners if o["layer"] == 0
    ]
    artifacts = {}
    for name, role in [
        ("source-full.png", "generation image 1: complete original RGBA assembly; geometry/camera only"),
        ("concept-building-crop.png", "generation image 2: approved concept crop; architecture/material/light only"),
        ("source-geometry-review.png", "review-only diagram; not a generated asset and not an imagegen input"),
    ]:
        im = Image.open(OUT / name)
        artifacts[name] = {"sha256": sha(OUT / name), "size": list(im.size), "mode": im.mode, "role": role}

    document_paths = ["docs/ART_DIRECTION_EARTH_RESET.md", "docs/EARTH_ART_BIBLE_V1.md", "docs/EARTH_SAMPLE_AREA_V1_ACCEPTANCE.md"]
    contract = {
        "schema": "earth-training-hall-source-v1",
        "status": "SOURCE/DESIGN INPUT ONLY. No image generation, registration, runtime edit or production approval.",
        "generation_gate": "Parent must inspect inputs and freeze the art specification/source-layout working master before approving any generation. Prompt is a draft.",
        "approved_direction": {"approval_utc": "2026-10-15T07:38:00Z", "feedback": "这个方向还可以", "scope": "overall Earth-era concept direction; not exact concept layout/props nor implementation"},
        "source_dependencies_sha256": FROZEN,
        "aligned_documents_at_build": {p: sha(PROJECT / p) for p in document_paths},
        "legacy_extraction_tool": {"path": "tools/prepare_a13_main_temple_source.py", "sha256": sha(PROJECT / "tools/prepare_a13_main_temple_source.py"), "role": "Read for original extraction/coordinate provenance; not executed or modified by this package."},
        "source_resource_hashes": {"map_native_sha256": source["map_source_sha256"], "building_resource_native_sha256": source["building_resource_source_sha256"]},
        "artifacts": artifacts,
        "concept_crop": {"source": "art_source/earth_base_style_concept_v1/concept.png", "source_size": [1448, 1086], "xyxy_half_open": list(CONCEPT_CROP), "operation": "Pillow integer crop only; no resize, repaint, AI edit, sharpening, recolor or alpha synthesis", "allowed": ["layered broad flat overhangs", "black/gunmetal diagonal supports", "metal/glass/concrete material relationships", "restrained cyan identification and warm recesses", "upper-left warm daylight with cool fill"], "forbidden_geometry_transfer": ["single central broad stair", "new planter beds/foliage", "new pavement, drainage, props or collisions", "cropped roof interpreted as full building topology", "door count/locations or camera inferred from this style crop"]},
        "geometry": {
            "world_bounds_xyxy_half_open": bounds, "source_composite_size": list(size),
            "source_canvas_origin_world": bounds[:2], "source_pixel_to_world_scale": 1,
            "bounds_are_not_collision_footprint": True,
            "coordinate_contract": source["coordinate_contract"],
            "owner_count": 30, "frame_range": [3966, 3995], "layer_counts": {"0": 12, "1": 18},
            "owners_in_draw_order": owners, "source_support_owners": support_owners,
            "hard_support_landmarks": [p for p in source["manual_visible_landmarks"] if p["id"][0] in "CS"],
            "coverage_only_old_eave_landmarks": [p for p in source["manual_visible_landmarks"] if p["id"][0] == "E"],
            "approximate_door_visual_evidence": door_points,
            "nearby_original_npcs_unchanged": source["nearby_original_npcs"],
            "visible": ["Two differently oriented adjacent facades meet at the visible front corner.", "Two distinct recessed visible openings and two distinct stair flights/upper landings are visible.", "Source supporting strip material includes narrow inter-step risers, not just horizontal top faces.", "The source composite includes baked checker cast, rock/grass apron and temple roof ornament; these are not new structural requirements."],
            "unknown_or_not_proven": ["Hidden/rear elevation and full three-dimensional structure are not recoverable from this one 2D source view.", "Exact aperture boundaries, concealed treads, numeric stair heights and exact orthographic camera angles are unmeasured.", "Door appearance alone does not establish portal or trigger semantics.", "No generated-building correspondence, new alpha partition, walk test or platform shadow receiver exists yet.", "The concept shows a partial building; it cannot supply missing whole-building geometry."]
        },
        "design_constraints": [
            "Rebuild visual architecture as an Earth-era martial training branch with broad layered flat canopies and dark diagonal supports. No roof tiles, temple upturned eaves, red timber pillars or religious ornament.",
            "Retain the original two facade/door/stair approach relationships, support boundaries and front corner anchor. Do not merge them into one broad central stair.",
            "Keep every original owner key, cell, flag, layer, sort_y and stable_source_order unchanged. Keep all 12 support-owner records and logical footprints; do not infer a new walkable polygon from the visual bbox.",
            "New sloping piers, canopy supports and rails must stay out of original traversable approaches. Shrink/redesign structure if needed; never move doors/actors or alter collision to rescue art.",
            "Later slicing must assign each generated RGBA pixel to exactly one owner. Explicit empty owner records are allowed only where justified by removed source apron/other absent visible material; never fabricate floor pixels to force nonempty owners.",
            "Keep original NPC identity/position/scripts and trigger data. Opening protagonist remains unarmed; no characters in this building asset.",
            "Output only one whole building with its real stair treads, landings, structural plinth and self-shading. Real negative spaces and exterior background must have genuine alpha.",
            "Exclude terrain apron, grass, vegetation, paving rectangle/diamond, route changes, cast shadow onto external ground, painted checkerboard, text, logos, watermark and extra props."
        ],
        "lighting": {"reference": "approved concept; EARTH_ART_BIBLE_V1 section 6", "key": "warm directional daylight from screen upper-left", "fill": "soft cool sky fill, readable dark faces", "external_cast_direction": "screen lower-right; exact common vector deferred until source-layout master is frozen", "inside_asset": "material response, self-shading and near contact contained on the actual structure", "outside_asset": "no ground projection/contact-shadow patch; a single separate cast is a later asset after registration", "platform_receiver": "unproven and separate; do not assume the old flat-ground shadow system works on elevated stairs"},
        "density_draft": {"minimum_texels_per_logical_unit": 2, "source_coverage_sizing_reference_px": [1592, 1330], "suggested_generation_canvas_px": [2048, 1792], "suggested_canvas_status": "request only, not an imagegen capability guarantee or approved final size", "required_verification": "Measure native generated effective density after support registration, exclude alpha margins, check PNG/atlas/import/draw/screenshot dimensions; reject a low-resolution output rather than upscale it."},
        "next_checks_before_any_runtime": ["Parent inspection and art/master freeze", "One whole-building generation only after separate approval", "Inspect complete new geometry against both source stairs/doors and all five support anchors with honest uncertainty", "Verify true alpha and no external ground cast/apron", "Native density and non-repeating material review", "Document any residual before ownership partition; no local warping or invented geometry", "Exact 30-owner metadata and one-owner RGBA reconstruction checks before engine integration"],
        "generation_prompt": {"path": "prompt-draft.txt", "sha256": sha(OUT / "prompt-draft.txt"), "state": "draft; not executed"},
        "reproduction": "python Project/art_source/earth_training_hall_source_v1/build_inputs.py",
    }
    write_json(OUT / "input-contract.json", contract)
    print(json.dumps({"status": "source package rebuilt", "owners": len(owners), "support_owners": len(support_owners), "source_size": list(size), "concept_crop_size": list(crop.size), "source_full_sha256": artifacts["source-full.png"]["sha256"], "contract_sha256": sha(OUT / "input-contract.json"), "image_generation_calls": 0, "runtime_edits": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
