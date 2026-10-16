# A13 Plant248–250: one bounded 2D generation attempt

## Result
Research candidate only. **Do not adopt, integrate, split, or register this result.** High confidence in this rejection: the generated foliage has yellow/green edge contamination, denser larger leaves and thicker consolidated woody stems. The broad asymmetric rising-right family shape survives, but fine branch topology does not. One attempt was made using built-in image generation, with no CLI fallback. No runtime, Git, GUI, map, owner, or Project file changes were made.

## Files
- `candidate-board.png`: source, generated full padded canvas and silhouette diagnostic.
- `candidate-raw.png`: untouched generator output, including original alpha and metadata.
- `contract.json`: pre-generation coordinates, three complete source owners and exact references/hashes.
- `prompt.txt`: actual submitted prompt.
- `measurements.json`: exact diagnostics and uncertainty.
- `source-padded-density8.png`: nearest-neighbor magnification of original pixels solely for geometry reference, not generated detail.
- `OUTPUT_SHA256.json`: file integrity manifest.

## Coordinates and source identity
Original complete group is 117×72 logical units, world bounds (3037,1772)–(3154,1844), three simultaneous spatial owners Plant248/249/250 at (63,57)/(64,57)/(65,57). All original flags0, layer1, sort_y57, stable orders6357/6457/6557 are preserved as a contract only; nothing was installed. Original cell origins are exact registration evidence, not physical roots.

Requested canvas was 1024×1024, uniform density8, source origin (44,224), envelope (44,224)–(980,800). Actual tool returned 1254×1254. Therefore exact requested canvas contract FAILED. Diagnostics use only whole-canvas proportional coordinates, factor1254/1024=1.224609375 (nominal density9.796875). No bbox fitting, asset resizing, crop, alpha cleanup, or anisotropic transform was performed. This proportional comparison is not a retroactive acceptance of the output canvas.

## Measurements and limits
Source opaque pixels2767 include777 pixels of exact checker color RGB(8,0,0). Excluding this exact color produces a diagnostic vegetation mask, not a verified botanical segmentation. Comparing it to raw candidate alpha≥128 under the whole-canvas mapping gives IoU0.5650, source coverage84.11%, candidate area1.3297×source vegetation-mask area, and36.75% of candidate mask outside source vegetation mask. Thus preserved broad bounds cannot be mistaken for preserved silhouette.

Large negative-space diagnostic uses the source vegetation convex hull minus a dilation of1 logical unit: only3.66% of these LARGE gaps are filled. This means the larger silhouette gaps broadly survive; it does not contradict visible loss of fine intra-branch spaces. Do not use that large-gap statistic to claim every opening is preserved. Fine twigs and many small openings changed visibly.

Manually registered source basal proxies (26,63),(51,69),(62,66),(73,59), uncertainty4–6 logical units. Candidate visible stem ends map approximately to(27.47,64.78),(51.46,72.03),(61.15,66.42); fourth source proxy cannot be independently identified. Left/central positional correspondence is plausible; physical root identity and complete branching preservation are low confidence. Source lowest checker pixel was never treated as a root.

Actual RGBA transparency exists:1,202,352 zero-alpha pixels,370,062 partial-alpha pixels,102 fully opaque pixels. However nonzero-alpha bounds reach(0,25)–(1230,1254), with very faint alpha noise far outside the plant. At alpha≥8 bounds are(52,268)–(1059,983); alpha≥128 bounds(53,269)–(1058,983). Median nonzero alpha237; bottom10% alpha≤2. This is not a clean production alpha. Raw retained unchanged; no thresholding fix was applied. Fluorescent-color heuristic counts3288 pixels at alpha≥128, R>150,G>180,B<80; this is a diagnostic warning, not a color-science acceptance threshold.

## Confidence and stopping point
High: raw dimensions, alpha statistics, source owner metadata, no-adoption conclusion.
Moderate: diagnostic silhouette mask and broad branch-direction correspondence.
Low: exact botanical root identity, fine topology equivalence, runtime depth/occlusion suitability.
No native movement/depth checks were authorized or performed. No owner split/reconstruction proof is claimed. The single authorized attempt is exhausted. Further art revision needs parent/user direction; do not turn this failed candidate into production by fitting or trimming it.
