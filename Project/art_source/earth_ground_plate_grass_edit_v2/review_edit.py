"""Verify dimensions and non-target changes. Analysis only; never modify either raw."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image
from scipy import ndimage

HERE = Path(__file__).resolve().parent
P = HERE.parents[1]
OLD = P / "art_source/earth_ground_plate_candidate_v1/raw.png"
NEW = HERE / "raw.png"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
hashes_before = {"v1": sha(OLD), "v2": sha(NEW)}
old_image, new_image = Image.open(OLD), Image.open(NEW)
assert old_image.size == new_image.size == (1536, 1024)
a = np.asarray(old_image.convert("RGB")).astype(np.int16)
b = np.asarray(new_image.convert("RGB")).astype(np.int16)
protected = np.asarray(Image.open(HERE / "inputs/protected-road-mask.png")) > 0
core = ndimage.binary_erosion(protected, iterations=16)
grass = ~ndimage.binary_dilation(protected, iterations=16)
diff = np.abs(a - b)
changed = np.any(diff != 0, axis=2)


def difference(mask):
    return {"pixels": int(mask.sum()), "changed_pixels": int(changed[mask].sum()),
            "unchanged_pixels": int((~changed)[mask].sum()), "changed_fraction": float(changed[mask].mean()),
            "mean_absolute_channel_difference_0_255": float(diff[mask].mean()),
            "max_channel_difference": int(diff[mask].max()),
            "p95_max_channel_difference": float(np.percentile(diff.max(axis=2)[mask], 95))}


def grass_stats(arr):
    f = arr.astype(float)
    luma = f[:, :, 0] * .2126 + f[:, :, 1] * .7152 + f[:, :, 2] * .0722
    horizontal = grass[:, 1:] & grass[:, :-1]
    vertical = grass[1:, :] & grass[:-1, :]
    gradient = np.concatenate((np.abs(np.diff(luma, axis=1))[horizontal], np.abs(np.diff(luma, axis=0))[vertical]))
    rgb = f[grass].mean(axis=0)
    return {"mean_srgb": rgb.tolist(), "mean_red_over_green": float(rgb[0] / rgb[1]),
            "mean_display_luma_neighbor_difference": float(gradient.mean()),
            "note": "Descriptive sRGB/display-luma proxies only; not a perceptual acceptance or physical lighting metric."}


def paved_proxy(arr):
    f = arr.astype(float)
    mask = (f[:, :, 2] >= f[:, :, 1] * .69) & (f[:, :, 0] >= f[:, :, 1] * .94) & (f[:, :, 0] - f[:, :, 1] < 55)
    labels, _ = ndimage.label(mask)
    counts = np.bincount(labels.ravel())
    counts[0] = 0
    mask = ndimage.binary_fill_holes(labels == counts.argmax())
    return mask


pa, pb = paved_proxy(a), paved_proxy(b)
geometry = {"material_proxy_iou": float((pa & pb).sum() / (pa | pb).sum()),
            "proxy_symmetric_difference_pixels": int((pa ^ pb).sum()),
            "limitation": "Color-based footprint diagnostic only. Does not establish pixel-exact curb layout or source registration."}
report = {
    "status": "grass is visually improved, but edit failed exact non-target pavement preservation; not accepted or installed",
    "review_scope": "Grass-only edit invariance checkpoint. A later independent whole-plate review/export is tracked separately in layout-review.json and export-review.json.",
    "raw": {"v1_sha256": hashes_before["v1"], "v2_sha256": hashes_before["v2"], "size": [1536, 1024],
            "mode": new_image.mode, "effective_texels_per_logical": [2, 2], "raw_resized_blurred_recolored_warped_or_composited": False},
    "protected_pixels": difference(protected), "road_core_eroded_16_raw_pixels": difference(core),
    "grass_descriptive_metrics": {"v1": grass_stats(a), "v2": grass_stats(b)}, "geometry": geometry,
    "mask_definition": "Read-only v1 largest neutral-material connected component, holes filled and dilated 5 raw pixels. White = entire road/curb plus safety fringe. Core is eroded 16 pixels to exclude fringe/grass.",
    "manual_review": {"grass": "Clearly deeper green with fewer golden bright needle strands and calmer contrast; it remains a fairly dense low leafy grass field, so final density/quietness needs joint scene review.",
                      "paving": "Capped shape and major seams are visually close, but concrete surface detail was re-rendered. This is real non-target change, not only grass overlap near the border.",
                      "scene_content": "No added people, buildings, trees, planters, route connectors or large cast shadows observed.",
                      "lighting": "Upper-left warm material light remains, with a greener body tone. No common hall/actor scene lighting validation performed."},
    "actions_taken": ["one built-in imagegen edit", "unchanged raw copy to separate v2 directory", "read-only pixel comparison"],
    "actions_not_taken": ["third imagegen call", "programmatic recolor", "blur", "warp", "composite v1 pavement back", "runtime modification by this review"],
    "next_boundary": "Return both immutable candidates and this evidence to parent. Do not promote v2 as a successful grass-only edit."}
assert hashes_before == {"v1": sha(OLD), "v2": sha(NEW)}
(HERE / "review.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
meta = json.loads((HERE / "generation.json").read_text())
meta["grass_only_review_status"] = report["status"]
if not meta.get("whole_plate_candidate"):
    meta["status"] = report["status"]
meta["review"] = "review.json"
(HERE / "generation.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"protected": report["protected_pixels"], "road_core": report["road_core_eroded_16_raw_pixels"],
                  "grass": report["grass_descriptive_metrics"], "geometry": geometry, "raws_unchanged": True}))
