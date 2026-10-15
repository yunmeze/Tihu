"""Prepare closed NPC pose-only diagnostic interfaces from immutable first raws.

Writes technical art_source derivatives and ignored diagnostics only. No Godot,
runtime, source, raw, click/interaction, story, shader or shadow modifications.
"""
from pathlib import Path
import hashlib
import json

from PIL import Image, ImageDraw, ImageFont

P = Path(__file__).resolve().parents[2]
SOURCE = P / "art_source/a13_npc_source"
DIAG = P / "diagnostics/a13-npc/pose-interface-v1"
CANVAS = (128, 160)
ORIGIN = (32, 104)
EXPECTED_RAW = {
    "fangzhang": "f40575b118ee673d0e4233e001ad16fb79180e136e3ff8a3def8e349caa60faf",
    "lingyunzi": "e8ed826d7fc5582d0a0910b8c885dee42581650a68723ac8ed8e4697f453f30f",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def uri(path):
    return "res://" + str(path.relative_to(P))


def border_measurement(image):
    alpha = image.getchannel("A")
    edges = {"top": alpha.crop((0, 0, image.width, 1)).tobytes(),
             "bottom": alpha.crop((0, image.height - 1, image.width, image.height)).tobytes(),
             "left": alpha.crop((0, 0, 1, image.height)).tobytes(),
             "right": alpha.crop((image.width - 1, 0, image.width, image.height)).tobytes()}
    return {edge: {"max_alpha": max(values), **{f"pixels_alpha_gt_{t}": sum(v > t for v in values) for t in [0, 16, 32, 128]}} for edge, values in edges.items()}


def source_canvas(frame, image):
    canvas = Image.new("RGBA", CANVAS)
    canvas.paste(image, (ORIGIN[0] + frame["offset"][0], ORIGIN[1] + frame["offset"][1]))
    return canvas


def candidate_canvas(image, registration):
    scale = registration["scale_generated_to_original"]
    translation = registration["translation_to_source_phase0_raw"]
    offset = registration["fixed_reference_phase_offset"]
    tx, ty = [ORIGIN[k] + offset[k] + translation[k] for k in [0, 1]]
    # The same matrix is used for all phases. No crop-relative recentering.
    return image.transform(CANVAS, Image.Transform.AFFINE,
        (1 / scale, 0, -tx / scale, 0, 1 / scale, -ty / scale),
        resample=Image.Resampling.BICUBIC)


def comparison_board(old, new, source_ids, path, scale):
    w, h = CANVAS
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12 if scale == 1 else 16)
    board = Image.new("RGB", (w * 4 * scale, (h * scale + 26) * 2), (70, 76, 82))
    draw = ImageDraw.Draw(board)
    for row, frames in enumerate([old, new]):
        y = row * (h * scale + 26)
        for phase, image in enumerate(frames):
            x = phase * w * scale
            bg = Image.new("RGBA", CANVAS, (105, 112, 118, 255))
            bg.alpha_composite(image)
            board.paste(bg.convert("RGB").resize((w * scale, h * scale), Image.Resampling.NEAREST), (x, y + 26))
            label = f"{'SRC' if row == 0 else 'NEW'} {source_ids[phase]} p{phase}"
            draw.text((x + 4, y + 4), label, font=font, fill="white")
    board.save(path)


def main():
    DIAG.mkdir(parents=True, exist_ok=True)
    source_contract = json.loads((SOURCE / "source-contract.json").read_text())
    summaries = []
    all_written = []
    for subject, record_index in [("fangzhang", 0), ("lingyunzi", 1)]:
        directory = P / f"art_source/npc_{subject}_rebuild_v1"
        raw_file = directory / "raw-v1.png"
        assert sha(raw_file) == EXPECTED_RAW[subject]
        raw = Image.open(raw_file).convert("RGBA")
        review_file = directory / "static-review.json"
        review_sha_before = sha(review_file)
        review = json.loads(review_file.read_text())
        assert review["source_contract_sha256"] == sha(SOURCE / "source-contract.json")
        registration = review["registration"]
        npc = source_contract["npcs"][record_index]
        indices = npc["source_indices"]
        unique_count = 1 if subject == "fangzhang" else 4
        assert raw.width % unique_count == 0
        raw_cell = [raw.width // unique_count, raw.height]
        atlas = Image.new("RGBA", (CANVAS[0] * unique_count, CANVAS[1]))
        generated = []
        for phase in range(unique_count):
            image = raw.crop((phase * raw_cell[0], 0, (phase + 1) * raw_cell[0], raw_cell[1]))
            registered = candidate_canvas(image, registration)
            assert registered.getchannel("A").getbbox() is not None
            assert all(v["max_alpha"] == 0 for v in border_measurement(registered).values()), "Registered canvas needs more margin"
            atlas.paste(registered, (phase * CANVAS[0], 0))
            generated.append(registered)
        atlas_file = directory / "v1-pose-atlas-128x160.png"
        atlas.save(atlas_file)
        assert Image.open(atlas_file).convert("RGBA").tobytes() == atlas.tobytes()
        frames = {}
        originals = []
        for phase, index in enumerate(indices):
            original = source_contract["frames"][str(index)]
            candidate_frame = 0 if unique_count == 1 else phase
            rect = [candidate_frame * CANVAS[0], 0, *CANVAS]
            x, y, w, h = rect
            assert atlas.crop((x, y, x + w, y + h)).tobytes() == generated[candidate_frame].tobytes()
            frames[str(index)] = {"phase": phase, "candidate_frame": candidate_frame, "rect": rect,
                "draw_offset": [-ORIGIN[0], -ORIGIN[1]], "draw_size": list(CANVAS),
                "rgba_sha256": hashlib.sha256(generated[candidate_frame].tobytes()).hexdigest(),
                "original_offset_evidence_only": original["offset"], "original_size_evidence_only": original["original"],
                "original_rgba_sha256": original["rgba_sha256"]}
            original_image = Image.open(SOURCE / original["file"]).convert("RGBA")
            assert hashlib.sha256(original_image.tobytes()).hexdigest() == original["rgba_sha256"]
            originals.append(source_canvas(original, original_image))
        new_four = [generated[0 if unique_count == 1 else phase] for phase in range(4)]
        for scale in [1, 3]:
            comparison_board(originals, new_four, indices, DIAG / f"{subject}-four-native-source-v1-{scale}x.png", scale)
        interface = {"schema": "lp-npc-pose-diagnostic-v1", "status": "candidate_for_bounded_native_pose_loop_only",
            "subject": subject, "npc_name": npc["name"], "map_id": "A13", "npc_record_index": record_index,
            "appearance": npc["appearance"], "direction_slot": npc["direction"], "source_ids": indices,
            "map_cell_evidence_only": [npc["x"], npc["y"]], "original_layer": 1, "original_sort_y": npc["y"],
            "atlas": uri(atlas_file), "atlas_sha256": sha(atlas_file), "atlas_size": list(atlas.size),
            "frame_size": list(CANVAS), "grid": [unique_count, 1], "unique_candidate_images": unique_count,
            "frames": frames, "draw_offset": [-ORIGIN[0], -ORIGIN[1]], "draw_size": list(CANVAS),
            "timing": {"source_fps": 50, "frame_ticks": 17, "phase_count": 4, "loop_ticks": 68,
                "loop_seconds": 1.36, "phase_order": [0, 1, 2, 3], "global_clock": True,
                "phase_formula": "floor(nonnegative_tick / 17) % 4", "source_index_formula": f"{indices[0]} + phase"},
            "sampling": {"source": "nearest", "candidate": "linear", "diagnostic_atlas_build": "one uniform bicubic sample from unchanged raw per source cell"},
            "draw_contract": {"position": "npc_world_cell_origin + draw_offset", "world_cell_origin": "Vector2(npc.x * 48, npc.y * 32)",
                "additional_original_offset": False, "additional_original_crop": False,
                "warning": "Original offset/root semantics are baked into the fixed registered canvas. Do not add source offset/crop a second time. Never auto-align each frame's top or bottom."},
            "registration": {"source": uri(review_file), "source_sha256": review_sha_before,
                "model": registration["model"], "scale": registration["scale_generated_to_original"],
                "translation_to_source_phase0_raw": registration["translation_to_source_phase0_raw"],
                "fixed_reference_phase_offset": registration["fixed_reference_phase_offset"],
                "native_cell_origin": list(ORIGIN), "per_phase_extra_translation": [[0, 0]] * 4,
                "per_phase_extra_scale": [1] * 4, "fit_from_first_phase_only": True,
                "anatomical_contacts_solved": False, "static_residuals_are_not_animation_acceptance": True},
            "raw": {"file": uri(raw_file), "sha256": EXPECTED_RAW[subject], "cell_size": raw_cell, "generation_calls": 1, "immutable": True},
            "source_comparison": {"manifest": "res://assets/original/manifest.json", "pack": "Npc", "indices": indices,
                "use_original_offset_and_crop_for_original_only": True, "original_checker_retained": True},
            "scope": {"pose_only": True, "normal_world_appearance_override": False, "r6_changes": False,
                "click_changes": False, "story_changes": False, "new_shadow": False,
                "runtime_approved": False, "static_fangzhang_reuses_one_rect_for_four_indices": subject == "fangzhang"},
            "required_runtime_review": ["Show all four source phases and the candidate at native scale before judgment.",
                "Use shared 50Hz simulation ticks and exact 17tick changes through the 3-to-0 seam.",
                "Compare at least two complete loops against original sources; freeze/manual phase is useful but not a replacement for loops.",
                "Do not add ground shadow or use click/story behavior as part of this pose diagnostic.",
                "Treat about-one-native-pixel first-fit phase discrepancies as evidence to inspect in motion, not automatic rejection or approval."]}
        interface_file = directory / "v1-pose-interface.json"
        write(interface_file, interface)
        audit = {"status": "PASS_TECHNICAL_INTERFACE_ONLY", "raw_sha256_unchanged": sha(raw_file) == EXPECTED_RAW[subject],
            "static_review_unchanged": sha(review_file) == review_sha_before,
            "raw_border_alpha_counts": border_measurement(raw),
            "raw_border_interpretation": "Faint boundary alpha is measured only. No raw cleanup or new generation. Strong subject cut is not established by all-alpha bounds.",
            "candidate_canvas_border_max_alpha": [border_measurement(image) for image in generated],
            "index_rect_roundtrip_checks": 4, "all_four_phase_aliases_equal": unique_count == 1,
            "shared_transform_for_all_phases": True, "per_phase_fit_or_recenter": False,
            "atlas_rgba_roundtrip_equal": True, "runtime_loop_viewed": False,
            "timing_boundary_checks": [{"tick": tick, "phase": (tick // 17) % 4, "source_index": indices[(tick // 17) % 4]} for tick in [0,16,17,33,34,50,51,67,68,135,136]],
            "atlas_sha256": sha(atlas_file), "interface_sha256": sha(interface_file)}
        audit_file = directory / "pose-interface-validation.json"
        write(audit_file, audit)
        all_written += [atlas_file, interface_file, audit_file]
        # The parent saved the source/raw stage separately. Include all still-new
        # static-review dependencies so this handoff is reproducible after checkout.
        all_written += [review_file, directory / "REVIEW.md", directory / "GIT_SAVE_MANIFEST.json"]
        summaries.append({"subject": subject, "name": npc["name"], "interface": uri(interface_file), "interface_sha256": sha(interface_file)})
    owner = P / "art_source/npc_fangzhang_rebuild_v1"
    set_file = owner / "npc-pose-diagnostic-set.json"
    write(set_file, {"schema": "lp-npc-pose-diagnostic-set-v1", "status": "pose-only candidate set, no normal-world promotion",
        "interfaces": summaries, "shared_clock": {"fps":50,"frame_ticks":17,"phase_count":4},
        "handoff": "POSE_DIAGNOSTIC_HANDOFF.md", "no_runtime_or_gui_executed_by_this_script": True})
    all_written += [set_file, Path(__file__), owner / "POSE_DIAGNOSTIC_HANDOFF.md", owner / "review_static_candidates.py"]
    manifest = owner / "GIT_SAVE_POSE_INTERFACE.json"
    write(manifest, {"stage": "technical pose atlas/interface and bounded handoff only",
        "files": [{"file": str(path.relative_to(P.parent)), "sha256": sha(path), "bytes": path.stat().st_size} for path in all_written]})
    print(json.dumps({"status":"PASS_TECHNICAL_INTERFACE_ONLY","subjects":summaries,"new_files":len(all_written),"manifest_sha256":sha(manifest)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
