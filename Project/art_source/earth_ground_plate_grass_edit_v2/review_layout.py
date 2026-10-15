"""Reproduce the recorded manual v2 layout audit; no fit/warp or new measurements."""
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib
import json
import math

HERE = Path(__file__).resolve().parent
points = [(382, 834), (768, 578), (960, 582), (1048, 636), (1048, 774), (872, 896)]
observed = [(386, 832), (771, 577), (963, 579), (1052, 639), (1051, 772), (875, 897)]
raw_sha = hashlib.sha256((HERE / "raw.png").read_bytes()).hexdigest()
assert raw_sha == "7dd080bb54897b878ac7743cad1dfb865217bdb76266fc441adb56d750edcb7b"
im = Image.open(HERE / "raw.png").convert("RGB")
assert im.size == (1536, 1024)
d = ImageDraw.Draw(im)
d.line(points, fill="magenta", width=2)
for i, g in enumerate(observed):
    d.ellipse((g[0] - 3, g[1] - 3, g[0] + 3, g[1] + 3), outline="cyan", width=1)
    d.text((g[0] + 7, g[1] - 15), str(i + 1), fill="cyan")
im.save(HERE / "source-layout-review-diagnostic.png")
report = {"status": "v2 independently reviewed as complete plate; source-layout candidate within manual source-read budget, not exact boundary or native approval",
          "raw_sha256": raw_sha, "world_bounds": [2496, 960, 3264, 1472], "effective_density": [2, 2],
          "samples": [{"source_center_raw": list(s), "v2_center_raw_approx": list(g),
                       "delta_logical": [(g[0] - s[0]) / 2, (g[1] - s[1]) / 2],
                       "distance_logical": math.hypot(g[0] - s[0], g[1] - s[1]) / 2,
                       "source_uncertainty_logical": 3, "v2_manual_read_uncertainty_raw": 3}
                      for s, g in zip(points, observed)],
          "maximum_center_distance_logical": max(math.hypot(g[0] - s[0], g[1] - s[1]) / 2 for s, g in zip(points, observed)),
          "manual_shape_check": ["Same bottom-opening diagonal road, short near-horizontal cap, upper-right chamfer, right vertical edge and lower-right diagonal.",
                                 "No added connector toward source left stair; approximately186-logical-pixel horizontal grass interval remains.",
                                 "All broad paving lies in original lower-field footprint; upper/right remains low grass.",
                                 "Curb thickness and material edge read differ at fine scale; center correspondence is within finite source-read precision, not zero-error outer-edge approval."],
          "no_v1_pixels_mixed": True, "no_warp_or_resize": True,
          "next": "After parent report, export every one of64 original floor owners only from immutable v2 raw, with source alpha and exact2x crop."}
(HERE / "layout-review.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"maximum_center_distance_logical": report["maximum_center_distance_logical"], "raw_sha256": raw_sha}))
