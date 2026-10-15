"""Reproducible static-only review of the two first NPC candidates.

Only crops, uniform scales and translates immutable generated rasters for diagnostics.
No character painting, warps, per-frame fitting, alpha cleanup, runtime or GUI changes.
"""
from pathlib import Path
import hashlib
import json
import math

from PIL import Image, ImageDraw, ImageFont

P = Path(__file__).resolve().parents[2]
SOURCE = P / "art_source/a13_npc_source"
DIAG = P / "diagnostics/a13-npc/remaster-v1"
ORIGIN = (32, 104)
CANVAS = (128, 160)
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)

# Manually read visible material features, with finite uncertainties. Not solved
# 3-D joints, ground contacts, body masks, or a promise of exact registration.
LANDMARKS = {
    "fangzhang": [
        ("white_headband_middle", (30, 7), (548, 114)),
        ("screen_left_hand_middle", (3, 21), (52, 418)),
        ("waist_hand_middle", (18, 30), (319, 557)),
        ("upper_screen_boot_visible_toe", (19, 53), (335, 999)),
        ("lower_screen_boot_visible_toe", (35, 64), (662, 1235)),
    ],
    "lingyunzi": [
        ("crown_top_middle", (15, 0), (273, 38)),
        ("overlapping_hands_middle", (15, 39), (270, 377)),
        ("screen_left_boot_visible_toe", (7, 70), (210, 665)),
        ("screen_right_boot_visible_toe", (23, 70), (338, 665)),
    ],
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def fit_uniform(points):
    src = [p[1] for p in points]
    raw = [p[2] for p in points]
    sm = [sum(p[k] for p in src) / len(src) for k in [0, 1]]
    rm = [sum(p[k] for p in raw) / len(raw) for k in [0, 1]]
    scale = sum((r[k] - rm[k]) * (s[k] - sm[k]) for r, s in zip(raw, src) for k in [0, 1]) / sum((r[k] - rm[k]) ** 2 for r in raw for k in [0, 1])
    translation = [sm[k] - scale * rm[k] for k in [0, 1]]
    rows = []
    for name, target, observed in points:
        mapped = [scale * observed[k] + translation[k] for k in [0, 1]]
        rows.append({"feature": name, "source_raw_xy": target, "generated_raw_xy": observed,
                     "source_read_uncertainty_px": 2, "generated_read_uncertainty_px": 12,
                     "mapped_source_raw_xy": mapped,
                     "residual_source_px": math.dist(target, mapped)})
    return scale, translation, rows


def alpha_stats(image):
    alpha = image.getchannel("A")
    values = alpha.tobytes()
    return {"size": list(image.size), "alpha_zero_pixels": values.count(0),
        "alpha_opaque_pixels": values.count(255), "alpha_1_to_7_pixels": sum(0 < v < 8 for v in values),
        "alpha_8_to_254_pixels": sum(8 <= v < 255 for v in values),
        "bounds_by_minimum_alpha": {str(t): alpha.point(lambda v: 255 if v >= t else 0).getbbox() for t in [1, 8, 32, 128, 250]},
        "thresholds_are_measurements_only": True}


def registered_source(image, offset):
    canvas = Image.new("RGBA", CANVAS)
    canvas.paste(image, (ORIGIN[0] + offset[0], ORIGIN[1] + offset[1]))
    return canvas


def registered_candidate(image, scale, translation, reference_offset):
    # Same transform for every generated phase; original phase0 offset is used
    # for the group, never original per-phase offsets added a second time.
    tx = ORIGIN[0] + reference_offset[0] + translation[0]
    ty = ORIGIN[1] + reference_offset[1] + translation[1]
    return image.transform(CANVAS, Image.Transform.AFFINE,
        (1 / scale, 0, -tx / scale, 0, 1 / scale, -ty / scale),
        resample=Image.Resampling.BICUBIC)


def board(rows, labels, file, scale=3):
    cols = len(rows[0])
    w, h = CANVAS
    result = Image.new("RGB", (cols * w * scale, len(rows) * (h * scale + 30)), (70, 76, 82))
    draw = ImageDraw.Draw(result)
    for row, images in enumerate(rows):
        yy = row * (h * scale + 30)
        for col, im in enumerate(images):
            x = col * w * scale
            bg = Image.new("RGBA", CANVAS, (105, 112, 118, 255))
            bg.alpha_composite(im)
            result.paste(bg.convert("RGB").resize((w * scale, h * scale), Image.Resampling.NEAREST), (x, yy + 30))
            label = labels[row][col]
            if scale == 1:
                label = f"SRC {label.split()[1]}" if row == 0 else f"NEW phase {col}"
            draw.text((x + 5, yy + 5), label, fill="white", font=FONT)
    result.save(file)


def main():
    DIAG.mkdir(parents=True, exist_ok=True)
    contract = json.loads((SOURCE / "source-contract.json").read_text())
    for name, indices in [("fangzhang", [261]), ("lingyunzi", [113, 114, 115, 116])]:
        directory = P / f"art_source/npc_{name}_rebuild_v1"
        raw_file = directory / "raw-v1.png"
        raw_sha_before = sha(raw_file)
        raw = Image.open(raw_file).convert("RGBA")
        count = len(indices)
        assert raw.width % count == 0
        cell_width = raw.width // count
        phases = [raw.crop((i * cell_width, 0, (i + 1) * cell_width, raw.height)) for i in range(count)]
        scale, translation, landmarks = fit_uniform(LANDMARKS[name])
        reference_offset = contract["frames"][str(indices[0])]["offset"]
        source_images = []
        mapped_images = []
        for index, phase in zip(indices, phases):
            f = contract["frames"][str(index)]
            source_images.append(registered_source(Image.open(SOURCE / f["file"]).convert("RGBA"), f["offset"]))
            mapped_images.append(registered_candidate(phase, scale, translation, reference_offset))
        labels = [[f"SOURCE {i} (checker retained)" for i in indices], [f"RAW v1 phase {j}, same group scale" for j in range(count)]]
        board([source_images, mapped_images], labels, DIAG / f"{name}-native-source-generated-3x.png")
        board([source_images, mapped_images], labels, DIAG / f"{name}-native-source-generated-1x.png", scale=1)
        stats = alpha_stats(raw)
        per_phase_stats = [alpha_stats(im) for im in phases]
        first_bbox = per_phase_stats[0]["bounds_by_minimum_alpha"]["128"]
        relative_tops = [(s["bounds_by_minimum_alpha"]["128"][1] - first_bbox[1]) * scale for s in per_phase_stats]
        relative_bottoms = [(s["bounds_by_minimum_alpha"]["128"][3] - first_bbox[3]) * scale for s in per_phase_stats]
        source_top_deltas = [contract["frames"][str(i)]["offset"][1] - reference_offset[1] for i in indices]
        # For the frontal Lingyunzi source, visible boot bottoms coincide with
        # native height-1 by manual inspection; no exact floor plane is inferred.
        source_bottom_deltas = [contract["frames"][str(i)]["offset"][1] + contract["frames"][str(i)]["original"][1]
            - reference_offset[1] - contract["frames"][str(indices[0])]["original"][1] for i in indices]
        report = {"status": "STATIC_REVIEW_ONLY_NOT_APPROVED", "subject": name, "raw_sha256": raw_sha_before,
            "source_contract_sha256": sha(SOURCE / "source-contract.json"), "generation_count": 1,
            "registration": {"model": "one positive uniform scale plus XY translation, no rotation or warp",
                "scale_generated_to_original": scale, "translation_to_source_phase0_raw": translation,
                "fixed_reference_phase_offset": reference_offset, "native_cell_origin": ORIGIN, "native_canvas": CANVAS,
                "phases_share_exact_transform": True, "phase_extraction": "equal-width original cells, no content recentering",
                "scale_basis": "Manual visible material landmarks, fit from first phase only. Not auto-bbox scaling, a body mask, or solved anatomical contacts.",
                "sampling": "one bicubic affine sampling of unchanged raw for diagnostic only",
                "manual_landmarks": landmarks, "max_landmark_residual_source_px": max(p["residual_source_px"] for p in landmarks),
                "anatomical_contacts_solved": False},
            "alpha": stats, "per_phase_alpha": per_phase_stats,
            "phase_screen_vertical_checks": {"source_top_deltas": source_top_deltas, "generated_top_deltas_native_scale": relative_tops,
                "source_visible_bottom_deltas": source_bottom_deltas, "generated_alpha_bottom_deltas_native_scale": relative_bottoms,
                "interpretation": "Crown/top and visible-foot extent checks only; source checker is not a body mask. Differences are not corrected by per-phase fitting."},
            "raw_unchanged": sha(raw_file) == raw_sha_before, "runtime_integrated": False,
            "diagnostic_directory": str(DIAG.relative_to(P)), "review_notes_file": "REVIEW.md"}
        assert report["raw_unchanged"]
        dump(directory / "static-review.json", report)
        print(name, "uniform_scale", scale, "translation", translation, "max_residual", report["registration"]["max_landmark_residual_source_px"], "top_deltas", relative_tops, "bottom_deltas", relative_bottoms)


if __name__ == "__main__":
    main()
