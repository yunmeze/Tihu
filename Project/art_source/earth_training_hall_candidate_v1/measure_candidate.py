"""Read-only candidate QA. Writes diagnostics only; never edits raw or runtime.

Point correspondence is manually interpreted, not a surveyed registration.
The common-scale fit is a rejection diagnostic, not an approved placement.
"""
from pathlib import Path
import hashlib
import json
from collections import Counter

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "earth_training_hall_source_v1"
FROZEN_RAW_SHA = "a81ff1d6ac235d80e5d948a804c2959b1b9b3babaed054897d396620b4bf9033"

# Corresponding visible material samples, read in the full image and local crops.
# These describe where the candidate actually put each feature, not requested positions.
RAW_POINTS = [
    ("C0", (836, 996), 10, "Bottom cap of the visible front-corner diagonal structural pier, above its concrete foundation; not the foundation's lower-most tip."),
    ("S0", (383, 884), 8, "Lower front tread lip near the right side of the left stair, inside the side cheek."),
    ("S1", (353, 748), 8, "Upper left stair/landing junction, beside inner edge of the left cheek."),
    ("S2", (1098, 1008), 8, "Lowest right-stair tread/front lip near its left end; not the outer cheek foot."),
    ("S3", (1145, 851), 8, "Upper right stair/landing junction near its far/right cheek.")
]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert sha(HERE / "raw.png") == FROZEN_RAW_SHA
    raw = Image.open(HERE / "raw.png").convert("RGBA")
    original = Image.open(SOURCE / "source-full.png").convert("RGBA")
    contract = json.loads((SOURCE / "input-contract.json").read_text())
    source_points = {p["id"].split("_")[0]: p for p in contract["geometry"]["hard_support_landmarks"]}
    a = np.asarray(raw)[:, :, 3]
    positive = a[a > 0]
    alpha_boxes = {}
    for threshold in [0, 1, 8, 32, 128, 240]:
        yy, xx = np.where(a > threshold)
        alpha_boxes[str(threshold)] = {"count": int(len(xx)), "bbox_xyxy": [int(xx.min()), int(yy.min()), int(xx.max() + 1), int(yy.max() + 1)]}
    sp = np.array([source_points[k]["source_composite_xy"] for k, _, _, _ in RAW_POINTS], dtype=float)
    rp = np.array([xy for _, xy, _, _ in RAW_POINTS], dtype=float)
    sc, rc = sp - sp.mean(axis=0), rp - rp.mean(axis=0)
    density = float((sc * rc).sum() / (sc * sc).sum())
    translation = rp.mean(axis=0) - density * sp.mean(axis=0)
    mapped = (rp - translation) / density
    residual = mapped - sp
    points = []
    for i, (key, xy, uncertainty, note) in enumerate(RAW_POINTS):
        source_unc = source_points[key]["manual_read_uncertainty_px"]
        points.append({
            "id": key, "source_xy": sp[i].tolist(), "raw_xy": list(xy),
            "raw_read_uncertainty_px": uncertainty, "source_read_uncertainty_px": source_unc,
            "material_interpretation": note, "mapped_source_xy_under_diagnostic_fit": mapped[i].tolist(),
            "source_residual_xy": residual[i].tolist(), "source_residual_distance": float(np.linalg.norm(residual[i])),
            "combined_reading_budget_source_px": source_unc + uncertainty / density,
        })

    # Review plates preserve raw asset bytes. Gray background reveals low-alpha fringe.
    gray = Image.new("RGBA", raw.size, (90, 100, 105, 255))
    gray.alpha_composite(raw)
    gray.convert("RGB").save(HERE / "raw-on-gray.jpg", quality=95)
    marked = gray.convert("RGB")
    draw = ImageDraw.Draw(marked)
    for key, (x, y), uncertainty, _ in RAW_POINTS:
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), outline="cyan", width=2)
        draw.rectangle((x - uncertainty, y - uncertainty, x + uncertainty, y + uncertainty), outline="orange")
        draw.text((x + 11, y - 10), key, fill="white")
    marked.save(HERE / "candidate-support-points.png")
    locals_board = Image.new("RGB", (5 * 200, 222), (65, 75, 80))
    ld = ImageDraw.Draw(locals_board)
    for n, (key, (x, y), uncertainty, _) in enumerate(RAW_POINTS):
        sample = gray.crop((x - 30, y - 30, x + 31, y + 31)).resize((183, 183), Image.Resampling.NEAREST).convert("RGB")
        locals_board.paste(sample, (n * 200, 34))
        ld.text((n * 200 + 2, 3), f"{key} raw({x},{y}) +/-{uncertainty}", fill="white")
        ld.rectangle((n * 200 + 87, 121, n * 200 + 95, 129), outline="cyan", width=2)
    locals_board.save(HERE / "candidate-support-locals.png")
    # One uniform scale+translation only. A labeled diagnostic, never output art.
    comparison = Image.new("RGB", (796 * 2, 665 + 32), (90, 100, 105))
    source_bg = Image.new("RGBA", original.size, (90, 100, 105, 255))
    source_bg.alpha_composite(original)
    diagnostic_bg = Image.new("RGBA", original.size, (90, 100, 105, 255))
    reduced = raw.resize((round(raw.width / density), round(raw.height / density)), Image.Resampling.LANCZOS)
    origin = np.rint(-translation / density).astype(int)
    diagnostic_bg.alpha_composite(reduced, tuple(origin))
    comparison.paste(source_bg.convert("RGB"), (0, 32))
    comparison.paste(diagnostic_bg.convert("RGB"), (796, 32))
    cd = ImageDraw.Draw(comparison)
    cd.text((8, 8), "SOURCE: original logical scale", fill="white")
    cd.text((804, 8), "DIAGNOSTIC FIT ONLY: common scale/translation; support gate FAILS", fill="white")
    for p in points:
        x, y = p["source_xy"]
        cd.ellipse((x - 3, y + 29, x + 3, y + 35), outline="cyan", width=2)
        tx, ty = p["mapped_source_xy_under_diagnostic_fit"]
        cd.line((796 + x, 32 + y, 796 + tx, 32 + ty), fill="orange", width=2)
        cd.ellipse((796 + x - 3, y + 29, 796 + x + 3, y + 35), outline="cyan", width=2)
        cd.ellipse((796 + tx - 3, ty + 29, 796 + tx + 3, ty + 35), outline="orange", width=2)
        cd.text((796 + tx + 4, ty + 24), p["id"], fill="white")
    comparison.save(HERE / "common-scale-diagnostic.jpg", quality=95)

    measurements = {
        "status": "Structure/style candidate only. NOT registered, NOT production-ready, NO runtime change.",
        "raw_sha256": FROZEN_RAW_SHA, "raw_size": list(raw.size), "raw_mode": "RGBA",
        "alpha": {"zero_pixels": int((a == 0).sum()), "positive_pixels": int((a > 0).sum()), "partial_pixels": int(((a > 0) & (a < 255)).sum()), "fully_opaque_pixels": int((a == 255).sum()), "most_common_positive_values": Counter(positive.tolist()).most_common(8), "threshold_bboxes_for_measurement_only": alpha_boxes, "interpretation": "Background is genuinely transparent, no visible detached ground-cast component. Most material alpha is 253, with low-alpha fringe/strays reaching x=0. Raw is preserved; no thresholding or opacity normalization performed."},
        "density": {"requested_canvas": [2048, 1792], "actual_canvas": list(raw.size), "source_coverage_target_at_2x": [1592, 1330], "actual_canvas_vs_old_full_canvas_ratio": [raw.width / 796, raw.height / 665], "visible_alpha_gt_128_bbox_size": [1293, 1065], "conclusion": "The delivered raster is smaller than the requested full-coverage target. It cannot be certified at >=2 texels/logical unit until valid support correspondence exists. The diagnostic fit's ~2.07 ratio is NOT a passing density because its geometry residuals fail. No enlargement performed."},
        "manual_support_correspondence": points,
        "common_scale_translation_diagnostic": {"model": "raw_xy = density * source_xy + translation; no rotation, shear, per-plane scale or local warp", "density_raw_px_per_source_unit": density, "raw_translation": translation.tolist(), "source_space_rms": float(np.sqrt((residual ** 2).sum(axis=1).mean())), "source_space_max_residual": float(np.linalg.norm(residual, axis=1).max()), "gate": "FAIL: C0, S0 and S3 exceed conservative combined reading uncertainty. The front pier/left stair relationship is not source-compatible under one scale/translation. This is a diagnostic, not approved registration."},
        "visible_findings": ["Both differently oriented entrances and both separate stairs exist; the approved black-gray sloping-pier/flat-canopy material language is present.", "Relative stair/pier geometry has drifted; matching two stairs by count is insufficient.", "The left visible door reads as a luminous largely closed leaf while the right opening is visibly open. Exact source-door access/threshold interpretation needs review.", "Stairs/plinth are more monumental, canopies flatter and the upper silhouette lower than the old temple; roof-shape change itself is allowed.", "Cyan accents and warm recesses are present, but cyan use is denser than the approved crop's restrained target.", "No external ground plate, grass apron, trees, people or source checker shadow is visibly reproduced."],
        "next_step": "Parent review of frozen raw and these real residuals; request a source-guided structural correction if approved. Do not use local warp, moved doors, actor offsets, sorting tricks or collision edits. Density/detail plan follows a valid structure.",
        "reproduce": "python Project/art_source/earth_training_hall_candidate_v1/measure_candidate.py",
    }
    (HERE / "measurements.json").write_text(json.dumps(measurements, ensure_ascii=False, indent=2) + "\n")
    assert sha(HERE / "raw.png") == FROZEN_RAW_SHA
    print(json.dumps({"raw_size": list(raw.size), "diagnostic_density": density, "source_space_rms": measurements["common_scale_translation_diagnostic"]["source_space_rms"], "residuals": {p["id"]: p["source_residual_distance"] for p in points}, "raw_unchanged": True, "gate": "NOT REGISTERED; SUPPORT GEOMETRY FAILS"}))


if __name__ == "__main__":
    main()
