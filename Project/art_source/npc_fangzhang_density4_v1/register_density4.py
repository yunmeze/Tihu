"""Direct-from-immutable-raw 4x texture-density derivatives of accepted NPC poses.

No new generation, pose fit, alpha cleanup, runtime or previous-asset edits.
All logical geometry is identical; texture-local lengths alone are multiplied4.
"""
from pathlib import Path
import hashlib
import json
import math

from PIL import Image, ImageDraw

P = Path(__file__).resolve().parents[2]
OWNER = Path(__file__).resolve().parent
DIAG = P / "diagnostics/a13-npc/density4-v1"
DENSITY = 4
LOGICAL = (128, 160)
TEX_FRAME = (512, 640)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rgba_sha(image):
    return hashlib.sha256(image.tobytes()).hexdigest()


def uri(path):
    return "res://" + path.relative_to(P).as_posix()


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def sample_raw(raw_cell, scale, translation, density):
    # p_tex = density * (scale * p_raw + logical_translation).
    s = density * scale
    tx, ty = [density * v for v in translation]
    inverse = [1 / s, 0, -tx / s, 0, 1 / s, -ty / s]
    image = raw_cell.transform((LOGICAL[0] * density, LOGICAL[1] * density),
        Image.Transform.AFFINE, inverse, resample=Image.Resampling.BICUBIC)
    return image, inverse


def projection(point, reference, slope, cast):
    ground_y = reference[1] + slope * (point[0] - reference[0])
    height = ground_y - point[1]
    return [point[0] + height * cast[0], ground_y + height * cast[1]]


def alpha_edge(image, logical_roi, threshold):
    box = [v * DENSITY for v in logical_roi]
    points = [(x, y) for y in range(box[1], box[3]) for x in range(box[0], box[2]) if image.getpixel((x, y))[3] >= threshold]
    last = max(y for x, y in points)
    xs = [x for x, y in points if y == last]
    point = [(min(xs) + max(xs) + 1) / 2, last + 1]
    return {"alpha_threshold_measurement_only": threshold, "roi_texture_xyxy": box,
            "last_row_index_texture": last, "edge_proxy_texture": point,
            "edge_proxy_logical": [v / DENSITY for v in point]}


def comparison_board(subject, old_frames, hd_frames):
    # Technical display comparisons only; no character pixels are redrawn.
    scale, label = 2, 22
    size = (LOGICAL[0] * scale, LOGICAL[1] * scale)
    board = Image.new("RGB", (size[0] * 4, (size[1] + label) * 2), (62, 68, 74))
    draw = ImageDraw.Draw(board)
    for row, frames in enumerate((old_frames, hd_frames)):
        for phase, im in enumerate(frames):
            small = im.resize(size, Image.Resampling.BILINEAR)
            bg = Image.new("RGBA", size, (100, 107, 113, 255)); bg.alpha_composite(small)
            x, y = phase * size[0], row * (size[1] + label)
            board.paste(bg.convert("RGB"), (x, y + label))
            draw.text((x + 4, y + 4), f"{'OLD1x->2x' if row == 0 else 'RAW->4x->2x'} p{phase}", fill="white")
    board.save(DIAG / f"{subject}-old-vs-density4-at-logical2x.png")


def main():
    DIAG.mkdir(parents=True, exist_ok=True)
    written, links = [], []
    for subject in ("fangzhang", "lingyunzi"):
        src = P / f"art_source/npc_{subject}_rebuild_v1"
        dst = P / f"art_source/npc_{subject}_density4_v1"; dst.mkdir(exist_ok=True)
        frozen = {p: sha(p) for p in src.iterdir() if p.is_file()}
        pose = json.loads((src / "v1-pose-interface.json").read_text())
        shadow = json.loads((src / "single-shadow-candidate.json").read_text())
        raw_path = src / "raw-v1.png"; assert sha(raw_path) == pose["raw"]["sha256"]
        old_path = src / "v1-pose-atlas-128x160.png"; assert sha(old_path) == pose["atlas_sha256"]
        raw = Image.open(raw_path).convert("RGBA")
        old = Image.open(old_path).convert("RGBA")
        reg = pose["registration"]
        scale = reg["scale"]
        translation = [reg["native_cell_origin"][k] + reg["fixed_reference_phase_offset"][k] + reg["translation_to_source_phase0_raw"][k] for k in (0, 1)]
        count = pose["unique_candidate_images"]
        assert raw.width % count == 0
        raw_width = raw.width // count
        atlas = Image.new("RGBA", (TEX_FRAME[0] * count, TEX_FRAME[1]))
        hd_frames, native_frames = [], []
        for phase in range(count):
            cell = raw.crop((phase * raw_width, 0, (phase + 1) * raw_width, raw.height))
            low, _ = sample_raw(cell, scale, translation, 1)
            assert low.tobytes() == old.crop((phase * 128, 0, (phase + 1) * 128, 160)).tobytes(), "The accepted old registration was not reproduced exactly"
            hd, inverse = sample_raw(cell, scale, translation, DENSITY)
            alpha = hd.getchannel("A")
            assert all(max(alpha.crop(b).tobytes()) == 0 for b in [(0, 0, 512, 1), (0, 639, 512, 640), (0, 0, 1, 640), (511, 0, 512, 640)])
            atlas.paste(hd, (phase * 512, 0)); hd_frames.append(hd); native_frames.append(low)
        atlas_path = dst / "body-atlas-4x.png"; atlas.save(atlas_path)
        assert Image.open(atlas_path).convert("RGBA").tobytes() == atlas.tobytes()
        reference = shadow["ground_reference"]
        texture_reference = [v * DENSITY for v in reference]
        slope, cast = shadow["ground_slope"], shadow["cast_per_height"]
        invariance_checks = []
        for point in [[0, 0], [128, 160], reference, [44, 118], [61, 130], [56, 125], [72.5, 87.25]]:
            expected = projection(point, reference, slope, cast)
            textured = projection([v * DENSITY for v in point], texture_reference, slope, cast)
            actual = [v / DENSITY for v in textured]
            error = math.dist(expected, actual); assert error < 1e-10
            invariance_checks.append({"logical_point": point, "logical_projected": expected, "hd_then_quarter_scale_projected": actual, "error": error})
        frames, foot_measurements = {}, []
        rois = [(40, 114, 50, 121), (57, 126, 66, 134)] if subject == "fangzhang" else [(43, 120, 54, 129), (58, 120, 69, 129)]
        for phase, index in enumerate(pose["source_ids"]):
            cell_index = 0 if count == 1 else phase
            frames[str(index)] = {"phase": phase, "texture_rect": [cell_index * 512, 0, 512, 640],
                "logical_draw_rect_size": [128, 160], "logical_draw_offset": [-32, -104],
                "rgba_sha256": rgba_sha(hd_frames[cell_index]),
                "original_offset_evidence_only": pose["frames"][str(index)]["original_offset_evidence_only"]}
            foot_measurements.append({"source_id": index, "measurements_not_refit": [
                [alpha_edge(hd_frames[cell_index], roi, t) for t in (8, 32, 96, 128, 224)] for roi in rois]})
        interface = {"schema": "lp-npc-density4-candidate-v1", "status": "technical density derivative; existing logical pose accepted; HD rendering not yet reviewed",
            "subject": subject, "npc_name": pose["npc_name"], "npc_record_index": pose["npc_record_index"],
            "map_id": "A13", "map_cell": pose["map_cell_evidence_only"], "appearance": pose["appearance"], "direction_slot": pose["direction_slot"],
            "source_ids": pose["source_ids"], "density": DENSITY,
            "atlas": uri(atlas_path), "atlas_sha256": sha(atlas_path), "texture_size": list(atlas.size), "texture_frame_size": list(TEX_FRAME),
            "logical_frame_size": list(LOGICAL), "logical_draw_offset": [-32, -104], "frames": frames,
            "sampling": "linear; choose screen density separately from logical world layout",
            "generation_calls": 0, "direct_from_immutable_raw": True, "upscaled_old_small_atlas": False,
            "raw": {"sha256": pose["raw"]["sha256"], "size": list(raw.size), "cell_size": [raw_width, raw.height]},
            "accepted_native_atlas_sha256": pose["atlas_sha256"],
            "registration": {"raw_to_logical_scale": scale, "raw_to_logical_translation": translation,
                "raw_to_texture_scale": DENSITY * scale, "raw_to_texture_translation": [v * DENSITY for v in translation],
                "raw_to_texture_inverse_sampling_matrix": inverse, "sampling_passes_per_raw_cell": 1, "resampler": "BICUBIC",
                "native_root": [32, 104], "texture_root": [128, 416], "phase_refit": False, "phase_extra_scale": [1] * 4, "phase_extra_translation": [[0, 0]] * 4},
            "body_draw": {"logical_rect": "Rect2(npc_world_origin+Vector2(-32,-104),Vector2(128,160))", "source_rect": "frames[source_id].texture_rect",
                "sprite_alternative": "Sprite2D centered=false; region512x640; scale(.25,.25); position=npc_world_origin+(-32,-104)",
                "do_not_scale_logical_offset_again": True, "do_not_add_original_source_offset_again": True},
            "shadow": {"mode": "fixed_receiver_line", "logical_ground_reference": reference, "texture_ground_reference": texture_reference,
                "ground_slope": slope, "cast_per_height": cast, "opacity": shadow["opacity"], "tint_rgb": shadow["tint_rgb"],
                "logical_blur_radius_px": shadow["blur_radius_px"], "requested_texture_blur_radius_px": DENSITY * shadow["blur_radius_px"],
                "body_to_parent_linear_scale": [0.25, 0.25], "body_to_parent_origin": "same logical NPC world origin+(-32,-104) used by body",
                "current_helper_max_texture_blur": 3.0, "current_helper_would_clamp_requested_3p6": True,
                "do_not_pass_0p9_as_texture_blur": True,
                "runtime_decision_required": "Preserve0.9 logical blur by explicitly supporting3.6 texture px in bounded HD path, or retain approved native shadow alpha/transform. Do not silently clamp3.6 to3 or use0.9 texture pixels.",
                "native_shadow_fallback_is_distinct": "May reuse old128x160 alpha with its original logical reference and scale1; do not combine HD reference with native texture.",
                "compositing_passes": 1, "fixed_all_phases": True},
            "timing": pose["timing"],
            "scope": {"new_identity_or_pose": False, "previous_assets_overwritten": False, "per_phase_geometry_changes": False, "runtime_or_R6_changes": False,
                "pixel_identical_shadow_claim": False, "note": "Projection geometry is invariant; higher-density alpha/filtering can change subpixel edges and needs visual verification."}}
        ipath = dst / "density4-interface.json"; write(ipath, interface)
        validation = {"schema": "lp-npc-density4-validation-v1", "subject": subject,
            "old_native_registration_reproduced_rgba_exactly": True, "all_texture_borders_alpha_zero": True,
            "atlas_roundtrip_rgba_match": True, "unique_hd_frames": len({rgba_sha(im) for im in hd_frames}),
            "projection_unit_invariance": invariance_checks, "body_transform_determinant": 0.25 ** 2,
            "body_transform_passes_helper_min_determinant0p025": 0.25 ** 2 >= 0.025,
            "frame_size_within_helper_max2048": True, "foot_edge_measurements_not_new_receiver_fit": foot_measurements,
            "raw_and_previous_stage_files_unchanged": True, "HD_runtime_test_executed": False}
        vpath = dst / "density4-validation.json"; write(vpath, validation)
        written += [atlas_path, ipath, vpath]
        links.append({"subject": subject, "interface": uri(ipath), "sha256": sha(ipath)})
        comparison_board(subject, [native_frames[0 if count == 1 else i] for i in range(4)], [hd_frames[0 if count == 1 else i] for i in range(4)])
        for path, digest in frozen.items(): assert sha(path) == digest, f"Frozen input changed: {path}"
    set_path = OWNER / "npc-density4-set.json"
    write(set_path, {"schema": "lp-npc-density4-set-v1", "status": "4x texture density, unchanged logical geometry; exact2x display review pending",
        "members": links, "texture_density": DENSITY, "logical_frame_size": list(LOGICAL), "no_image_generation": True,
        "existing_ordinary_assets_retained": True, "HD_shadow_blur_unit_resolution_required": True})
    written += [set_path, Path(__file__), OWNER / "DENSITY4_HANDOFF.md"]
    assert all(p.is_file() for p in written)
    manifest_path = OWNER / "GIT_SAVE_DENSITY4.json"
    write(manifest_path, {"stage": "direct raw to4x texture density; no pose changes; previous native assets retained", "files": [
        {"file": p.relative_to(P.parent).as_posix(), "sha256": sha(p), "bytes": p.stat().st_size} for p in written], "include_manifest_itself": True})
    print(json.dumps({"file": str(manifest_path), "sha256": sha(manifest_path), "files_plus_manifest": len(written) + 1}, indent=2))


if __name__ == "__main__":
    main()
