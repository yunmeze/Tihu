"""Read-only candidate checks + diagnostic copies; never warp/edit raw or install assets."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = Path(__file__).resolve().parent
P = HERE.parents[1]
raw = HERE / "raw.png"
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
before = digest(raw)
im = Image.open(raw).convert("RGB")
assert im.size == (1536, 1024), "Do not resize a failed-density image to pass this check."
source = Image.open(P / "art_source/earth_ground_plate_source_v1/source-floor-native.png").convert("RGB")
guide = np.asarray(Image.open(P / "art_source/earth_ground_plate_source_v1/source-material-zones-native.png"))
guide2 = np.repeat(np.repeat(guide, 2, 0), 2, 1)
a = np.asarray(im).astype(float)
# Color proxy is NOT a segmentation truth or production matte. Grass can overlap curb.
proxy = (a[:, :, 2] >= a[:, :, 1] * .69) & (a[:, :, 0] >= a[:, :, 1] * .94) & (a[:, :, 0] - a[:, :, 1] < 55)
labels, _ = ndimage.label(proxy)
counts = np.bincount(labels.ravel())
counts[0] = 0
proxy = labels == counts.argmax()
scanlines = []
for y in [578, 600, 636, 650, 700, 750, 774, 800, 834, 850, 896, 950, 1000, 1023]:
    expected = np.flatnonzero(guide2[y] >= 128)
    found = np.flatnonzero(proxy[y])
    scanlines.append({"raw_y": y, "source_guide_including_review_band_x": [int(expected.min()), int(expected.max())] if expected.size else None,
                      "generated_neutral_material_proxy_x": [int(found.min()), int(found.max())] if found.size else None})
expected = [(382, 834), (768, 578), (960, 582), (1048, 636), (1048, 774), (872, 896)]
# Manually inspected central curb read points on raw; finite uncertainty, not fitted control points.
observed = [(386, 832), (771, 577), (963, 578), (1052, 638), (1051, 772), (874, 897)]
manual = [{"source_raw_center": list(s), "generated_raw_center_approx": list(g),
           "delta_logical": [(g[0] - s[0]) / 2, (g[1] - s[1]) / 2],
           "source_uncertainty_logical": 3, "generated_read_uncertainty_raw_px": 3}
          for s, g in zip(expected, observed)]
board = Image.new("RGB", (2020, 492), (30, 30, 30))
box = (80, 560, 1090, 1024)
board.paste(source.resize((1536, 1024), Image.Resampling.NEAREST).crop(box), (0, 28))
board.paste(im.crop(box), (1010, 28))
d = ImageDraw.Draw(board)
d.text((8, 8), "SOURCE x2 NEAREST for geometry comparison ONLY", fill="white")
d.text((1018, 8), "GENERATED NATIVE 2x, same world registration; NO WARP", fill="white")
board.save(HERE / "geometry-comparison-diagnostic.png")
overlay = im.copy()
d = ImageDraw.Draw(overlay)
d.line(expected, fill=(255, 0, 255), width=2)
d.text((16, 16), "DIAGNOSTIC: magenta = manual source curb center, uncertainty +/-6 raw pixels", fill=(255, 0, 255))
overlay.save(HERE / "source-centerline-overlay-diagnostic.png")
report = {
    "status": "one raw candidate only; source-layout/material review pending; not approved or installed",
    "raw": {"file": "raw.png", "sha256": before, "size": list(im.size), "mode": "RGB", "opaque": True,
            "world_bounds": [2496, 960, 3264, 1472], "logical_size": [768, 512],
            "effective_texels_per_logical": [2.0, 2.0], "raw_resized_or_warped": False, "generated_attempts": 1},
    "manual_visual_findings": {
        "topology": "Original capped diagonal road remains in lower field; the grass gap to the left stairs is retained. No connector path, people, buildings, large trees or their cast silhouettes are baked in.",
        "centerline": "Six manual central-curb samples remain near the prior source read within its approximate precision; this is not zero-error registration or exact boundary approval.",
        "edge_limit": "Generated curb has more pronounced width/contact contrast; local outer material edges fluctuate against the approximate source band. No warp was applied. Source guide has per-frame approximation steps and cannot prove exact original curb geometry.",
        "style": "Concrete slabs are coherent and restrained; grass remains too busy/high-contrast and warm-yellow relative to the desired quiet natural green. Needs joint review with hall/actor before acceptance.",
        "light": "Warm upper-left material lighting is plausible; no shared hall/actor composite has been tested. No claim of accepted unified lighting.",
        "repetition": "No obvious exact mirror/tile seams seen in this plate; natural-looking density variation and visual quietness are still insufficiently established at game scale."},
    "manual_curb_samples": manual,
    "color_proxy_diagnostics": {"definition": "largest connected neutral-color component, B/G>=.69 and R/G>=.94 and R-G<55; NOT exact material alpha", "scanlines": scanlines,
                                "road_guide_core_pixels": int((guide2 == 128).sum()), "core_pixels_not_in_proxy": int(((guide2 == 128) & ~proxy).sum()),
                                "proxy_pixels_beyond_review_band": int(((guide2 == 32) & proxy).sum()),
                                "limitations": "Colored blades can hide edge pixels; old semantic guide uses manual source centerline and per-frame copies. Neither metric authorizes width changes, trimming or runtime masks."},
    "not_performed": ["raw warp", "raw color correction", "second generation", "64-owner export", "static shadow generation", "runtime edit", "native scene validation"],
    "decision": "Keep immutable raw for parent review. Do not promote to production or claim source-edge acceptance. Any follow-up generation/retouch must be separately scoped."}
assert digest(raw) == before
(HERE / "review.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
meta = json.loads((HERE / "generation.json").read_text())
meta["status"] = report["status"]
meta["review"] = "review.json"
(HERE / "generation.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"size": im.size, "density": [2, 2], "raw_sha256": before, "raw_unchanged": True,
                  "proxy_beyond_band_pixels_not_exact_error": report["color_proxy_diagnostics"]["proxy_pixels_beyond_review_band"]}))
