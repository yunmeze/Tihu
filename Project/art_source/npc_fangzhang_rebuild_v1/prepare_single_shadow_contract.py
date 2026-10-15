"""Read immutable NPC pixels; write fixed-receiver research contracts/diagnostics.

No image generation, body editing, shader/runtime edits, or Godot execution.
The only source color exclusion is a READ-ONLY measurement inside reviewed boot
ROIs. It never creates a mask and must never become a runtime color key.
"""
from pathlib import Path
import hashlib
import json
import math

from PIL import Image, ImageDraw

P = Path(__file__).resolve().parents[2]
OWNER = Path(__file__).resolve().parent
SOURCE = P / "art_source/a13_npc_source"
DIAG = P / "diagnostics/a13-npc/single-shadow-v1"
ROOT = (32, 104)
CAST = (148 / 279, -111 / 279)
CHECKER = (16, 8, 8, 255)
THRESHOLDS = (8, 32, 96, 128, 224)
EXPECTED = {
    "fangzhang": ("b921d590ab2e53550bf6225eb0c83a15bd2adf3e9e30f603ab268fc2ac79ce46", [44.0, 118.0], 12 / 17),
    "lingyunzi": ("517e11d9d9661966d154d9272dfa0c643bf02e3e550d66b3172b22ed8b367c85", [56.0, 125.0], 0.0),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def uri(path):
    return "res://" + path.relative_to(P).as_posix()


def lowest_edge(image, roi, threshold, exclude_checker=False):
    points = [(x, y) for y in range(roi[1], roi[3]) for x in range(roi[0], roi[2])
              if image.getpixel((x, y))[3] >= threshold
              and (not exclude_checker or image.getpixel((x, y)) != CHECKER)]
    last = max(y for _, y in points)
    xs = [x for x, y in points if y == last]
    return {"roi_xyxy": roi, "alpha_threshold": threshold, "last_row_index": last,
            "last_row_x_indices": xs,
            "visible_edge_proxy": [(min(xs) + max(xs) + 1) / 2, last + 1],
            "checker_excluded_only_for_this_measurement": exclude_checker}


def projection(reference, slope):
    b = reference[1] - slope * reference[0]
    return {"x": [1 + CAST[0] * slope, slope * (1 + CAST[1])],
            "y": [-CAST[0], -CAST[1]],
            "origin": [CAST[0] * b, (1 + CAST[1]) * b]}


def project(point, matrix):
    return [matrix["x"][k] * point[0] + matrix["y"][k] * point[1] + matrix["origin"][k] for k in (0, 1)]


def residual(point, reference, slope):
    g = reference[1] + slope * (point[0] - reference[0])
    h = g - point[1]
    delta = [CAST[0] * h, (1 + CAST[1]) * h]
    return {"point": point, "receiver_y_at_x": g, "signed_receiver_minus_visible_y": h,
            "shadow_sample_delta": delta, "shadow_sample_distance": math.hypot(*delta)}


def source_canvas(image, offset):
    canvas = Image.new("RGBA", (128, 160))
    canvas.paste(image, (ROOT[0] + offset[0], ROOT[1] + offset[1]))
    return canvas


def measurement_board(subject, originals, candidates, measurements, reference, slope):
    # Diagnostic overlays only. Source and candidate body RGBA are unchanged.
    roi = (36, 106, 72, 136) if subject == "fangzhang" else (40, 108, 72, 132)
    z, gap, label = 6, 8, 18
    w, h = (roi[2] - roi[0]) * z, (roi[3] - roi[1]) * z
    board = Image.new("RGB", (4 * (w + gap), 2 * (h + label + gap)), (56, 62, 68))
    draw = ImageDraw.Draw(board)
    for row, images in enumerate((originals, candidates)):
        for phase, image in enumerate(images):
            x, y = phase * (w + gap), row * (h + label + gap)
            bg = Image.new("RGBA", image.size, (99, 105, 111, 255))
            bg.alpha_composite(image)
            board.paste(bg.crop(roi).convert("RGB").resize((w, h), Image.Resampling.NEAREST), (x, y + label))
            draw.text((x, y), f"{'SRC' if row == 0 else 'NEW'} {measurements[phase]['source_id']}", fill="white")
            yy = lambda xx: y + label + (reference[1] + slope * (xx - reference[0]) - roi[1]) * z
            draw.line((x, yy(roi[0]), x + w, yy(roi[2])), fill=(65, 220, 240), width=1)
            for foot in measurements[phase]["source_boots" if row == 0 else "candidate_boots"]:
                pt = foot["registered_edge_proxy"] if row == 0 else foot["by_alpha_threshold"]["96"]["visible_edge_proxy"]
                px, py = x + (pt[0] - roi[0]) * z, y + label + (pt[1] - roi[1]) * z
                draw.line((px - 3, py, px + 3, py), fill=(255, 175, 75), width=1)
                draw.line((px, py - 3, px, py + 3), fill=(255, 175, 75), width=1)
    board.save(DIAG / f"{subject}-all-four-boots-fixed-line-6x.png")


def main():
    DIAG.mkdir(parents=True, exist_ok=True)
    source = json.loads((SOURCE / "source-contract.json").read_text())
    written, links = [], []
    for subject, (atlas_sha, reference, slope) in EXPECTED.items():
        directory = P / f"art_source/npc_{subject}_rebuild_v1"
        pose_path = directory / "v1-pose-interface.json"
        pose = json.loads(pose_path.read_text())
        atlas_path = directory / "v1-pose-atlas-128x160.png"
        assert sha(atlas_path) == atlas_sha == pose["atlas_sha256"]
        assert sha(directory / "raw-v1.png") == pose["raw"]["sha256"]
        atlas = Image.open(atlas_path).convert("RGBA")
        snapshots = {path: sha(path) for path in (atlas_path, pose_path, directory / "raw-v1.png", SOURCE / "source-contract.json")}
        measurements, originals, candidates = [], [], []
        for phase, index in enumerate(pose["source_ids"]):
            sf = source["frames"][str(index)]
            original = Image.open(SOURCE / sf["file"]).convert("RGBA")
            assert hashlib.sha256(original.tobytes()).hexdigest() == sf["rgba_sha256"]
            r = pose["frames"][str(index)]["rect"]
            candidate = atlas.crop((r[0], r[1], r[0] + r[2], r[1] + r[3]))
            assert hashlib.sha256(candidate.tobytes()).hexdigest() == pose["frames"][str(index)]["rgba_sha256"]
            source_rois = [(13, 51, 25, 58), (29, 60, 40, 69)] if subject == "fangzhang" else [(4, 64, 12, original.height), (19, 64, 27, original.height)]
            candidate_rois = [(40, 114, 50, 121), (57, 126, 66, 134)] if subject == "fangzhang" else [(43, 120, 54, 129), (58, 120, 69, 129)]
            src_feet, new_feet = [], []
            for roi in source_rois:
                edge = lowest_edge(original, roi, 1, True)
                edge["registered_edge_proxy"] = [edge["visible_edge_proxy"][k] + ROOT[k] + sf["offset"][k] for k in (0, 1)]
                edge["residual_to_candidate_receiver"] = residual(edge["registered_edge_proxy"], reference, slope)
                src_feet.append(edge)
            for roi in candidate_rois:
                edges = {str(t): lowest_edge(candidate, roi, t) for t in THRESHOLDS}
                new_feet.append({"by_alpha_threshold": edges,
                                 "residuals": {t: residual(v["visible_edge_proxy"], reference, slope) for t, v in edges.items()}})
            exposed_roi = [44 if subject == "fangzhang" else 32, 0, original.width, original.height]
            exposed = [(x, y) for y in range(original.height) for x in range(exposed_roi[0], original.width) if original.getpixel((x, y))[3]]
            assert all(original.getpixel(p) == CHECKER for p in exposed)
            checker_evidence = {"reviewed_exposed_roi_xyxy": exposed_roi, "pixel_count": len(exposed),
                "all_nontransparent_rgba": list(CHECKER),
                "bounds_xyxy": [min(x for x, y in exposed), min(y for x, y in exposed), max(x for x, y in exposed) + 1, max(y for x, y in exposed) + 1]}
            measurements.append({"source_id": index, "phase": phase, "original_offset": sf["offset"],
                "source_rgba_sha256": sf["rgba_sha256"], "candidate_rgba_sha256": pose["frames"][str(index)]["rgba_sha256"],
                "source_boots": src_feet, "candidate_boots": new_feet, "source_exposed_checker_evidence": checker_evidence})
            originals.append(source_canvas(original, sf["offset"]))
            candidates.append(candidate)
        matrix = projection(reference, slope)
        determinant = matrix["x"][0] * matrix["y"][1] - matrix["x"][1] * matrix["y"][0]
        assert determinant > 0.025
        corners = [project(p, matrix) for p in ((0, 0), (128, 0), (128, 160), (0, 160))]
        max_primary = max(f["residuals"]["96"]["shadow_sample_distance"] for m in measurements for f in m["candidate_boots"])
        assert max_primary < 1e-10
        alternate = {"ground_reference": [52.5, 124.0], "ground_slope": 0.0,
            "status": "comparison_only_not_selected; forces both static staggered boots away from their local receiver",
            "foot_residuals": [residual([44, 118], [52.5, 124], 0), residual([61, 130], [52.5, 124], 0)]} if subject == "fangzhang" else {
            "ground_reference": [56.0, 124.0], "ground_slope": 0.0,
            "status": "threshold-sensitivity comparison only; broad alpha224 sole row ends at124, fine tip alpha8..128 ends at125",
            "foot_residuals": [residual([48.5, 125], [56, 124], 0), residual([63.5, 125], [56, 124], 0)]}
        contract = {"schema": "lp-npc-fixed-single-shadow-candidate-v1", "subject": subject,
            "status": "pure_pose_accepted_by_parent; single_shadow_candidate_not_runtime_accepted",
            "pose_interface": uri(pose_path), "pose_interface_sha256": sha(pose_path),
            "atlas": pose["atlas"], "atlas_sha256": atlas_sha, "frame_size": [128, 160],
            "source_ids": pose["source_ids"], "draw_offset": [-32, -104], "world_cell": pose["map_cell_evidence_only"],
            "source_contract_sha256": sha(SOURCE / "source-contract.json"),
            "pixel_convention": "coordinates are geometric pixel edges; row y has lower edge y+1; mean x uses pixel centers; ROIs xyxy exclusive",
            "measurement_only_alpha_thresholds": list(THRESHOLDS),
            "manual_uncertainty_native_px": {"source_visible_boot": 2, "candidate_visible_boot": 1},
            "ground_reference": reference, "ground_slope": slope,
            "ground_reference_relative_to_original_cell_origin": [reference[0] - 32, reference[1] - 104],
            "fixed_for_all_four_phases": True,
            "receiver_basis": "fixed line through reviewed candidate staggered boot edge proxies (44,118),(61,130), corroborated by source (43.5,119),(59.5,129)" if subject == "fangzhang" else "source four-phase BOTH boot edges register to y125; candidate alpha8..128 edge envelope also y125 in all phases; fixed horizontal receiver",
            "receiver_interpretation": "2D visual projection proxy only, not recovered physical plane, support/weight-bearing proof, skeletal contacts, or elevation",
            "cast_per_height": list(CAST), "cast_rational": ["148/279", "-111/279"],
            "cast_basis": "Same established screen-right/up cast as hero/tree; NPC exposed checker corroborates direction only, not exact magnitude, light elevation or receiver slope.",
            "opacity": 0.30, "blur_radius_px": 0.9, "tint_rgb": [0.035, 0.045, 0.055],
            "helper": "res://scripts/art/hero_alpha_ground_shadow.gd",
            "helper_api": "configure_ground_frame", "projection_matrix": matrix, "projection_determinant": determinant,
            "projected_full_canvas_corners_before_1p9_padding": corners,
            "primary_alpha96_max_foot_sample_displacement_px": max_primary,
            "alternative_not_selected": alternate,
            "measurements": measurements,
            "runtime_contract": {
                "body_to_parent": "exact same transform as candidate body, normally Transform2D(0,npc_world_cell_origin+Vector2(-32,-104)); no added source offset/crop",
                "region": "read unchanged pose_interface.frames[source_id].rect; Fangzhang same rectangle for all four IDs",
                "timing": pose["timing"], "parameter_changes_by_phase": False,
                "shadow_compositing_passes": 1, "shadow_uses_full_unchanged_candidate_alpha": True,
                "original_checker_with_new_shadow": False,
                "draw_order": "floor pass, one new shadow, unchanged normally depth-sorted objects and replacement body",
                "fallback": "atomic original checker-bearing NPC body + no new shadow on any resource/configuration failure",
                "required_review": ["exact 1screen-pixel/world-pixel capture verified from viewport/window dimensions", "both NPCs native off/on and full17tick cycle including3-to0; Fangzhang remains static", "contact remains tied to same root with no phase changes to line/scale/offset", "one shadow only; no foot/crown cut or alpha halo; regular NPC/object depth ordering", "no R6, clicks, names, story or collision change; no normal-world promotion from this contract alone"]},
            "known_risks": ["A 2D line cannot recover actual 3D foot elevation or receiver topology; do not pin animated landmarks every phase.",
                "Fangzhang staggered sole contours touch source checker; selected visible material edges carry approximately2px source reading uncertainty.",
                "Lingyunzi finest sole tip reaches y125 while the broad alpha224 edge ends y124; approximately1px contact ambiguity is retained.",
                "Same cast does not establish stairs/platform receiver clipping or shadows on other actors/buildings.",
                "Lingyunzi richer gold ornament/tassel design remains a recorded design residual, not a shadow problem to repair.",
                "Alpha thresholds and checker color are measurement evidence only; do not edit raw, atlas alpha, body colors, or source pixels."]}
        out = directory / "single-shadow-candidate.json"
        write(out, contract)
        written.append(out)
        links.append({"subject": subject, "contract": uri(out), "sha256": sha(out)})
        measurement_board(subject, originals, candidates, measurements, reference, slope)
        for path, digest in snapshots.items():
            assert sha(path) == digest, f"Immutable input changed: {path}"
    set_path = OWNER / "npc-single-shadow-diagnostic-set.json"
    write(set_path, {"schema": "lp-npc-single-shadow-diagnostic-set-v1", "status": "offline candidate; next gate is native single-shadow contact", "contracts": links,
        "pure_pose_evidence_review": uri(OWNER / "runtime-pose-evidence-review.json"),
        "shared_cast_per_height": list(CAST), "separate_receiver_parameters_per_npc": True,
        "raw_or_runtime_changes": False, "normal_world_promotion": False})
    written += [set_path, Path(__file__), OWNER / "SINGLE_SHADOW_HANDOFF.md", OWNER / "runtime-pose-evidence-review.json"]
    assert all(path.is_file() for path in written)
    manifest = OWNER / "GIT_SAVE_SINGLE_SHADOW.json"
    write(manifest, {"stage": "reviewed pose evidence plus offline per-NPC fixed single-shadow candidates; no runtime edits", "files": [
        {"file": path.relative_to(P.parent).as_posix(), "sha256": sha(path), "bytes": path.stat().st_size} for path in written],
        "manifest_itself": "include this file as well; its hash is delivered externally", "diagnostics_ignored": True})
    print(json.dumps({"manifest": str(manifest), "sha256": sha(manifest), "files_plus_manifest": len(written) + 1}, indent=2))


if __name__ == "__main__":
    main()
