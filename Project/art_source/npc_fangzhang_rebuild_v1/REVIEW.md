# 方丈 v1: static source-coordinate review

Status: first raw candidate retained; **not runtime-approved**. Exactly one built-in image-generation call. No retries, repaint, local deformation, frame substitution or alpha cleanup.

## Evidence and preservation

- Immutable generated `raw-v1.png`: RGBA 1207 × 1303, SHA256 `f40575b118ee673d0e4233e001ad16fb79180e136e3ff8a3def8e349caa60faf`.
- `tool-request.json` is the actual submitted prompt and reference-path/transparent-background payload. `input-provenance.json` records input hashes and art-direction/source-contract hashes.
- Source261 was enlarged8× as `source-static-pose-8x.png`; local original headband and arm-wrap crops are the only other references. No hero full-body reference was used.
- Original261–264 are identical. The intended future interface is one static candidate shared by all four indices with unchanged17tick cadence, not four invented motion phases. No runtime mapping has been installed.

## Visual result

The white headband, dark head top, cream/tan sleeveless training garment, exposed arms, yellow-brown trousers and dark wraps/boots are retained. The bent knees, screen-left-reaching arm and waist-crossing other forearm broadly follow the source. Both boots and both hand regions remain visible; no staff, weapon, beard, robe, large light core, floor or cast-shadow blob was added.

The generated upper arms and shoulder anatomy are more muscular and explicit than the tiny source, and hair/headband tail details are more elaborate. These are visible design expansions, not proven original anatomy. The result has restrained silver hardware and a very small cyan seam rather than the hero's wine-red armor. At native size, fine textile/skin detail reduces to a readable broad silhouette; a game-scene review is still required.

## One-scale source-coordinate check

`review_static_candidates.py` fits a single uniform scale and XY translation using five manually read material landmarks: white headband middle, two visible hand regions, and two visible boot-toe regions. Those are not solved anatomical joints or ground contacts.

- Generated-to-original scale: `0.05185459624901814`
- Translation into raw source261 coordinates: `(1.129318717376247, 0.5374353329025396)`
- Add original offset `(-6,-40)` and diagnostic native cell origin `(32,104)` for the common 128 × 160 canvas.
- Maximum fitted landmark residual: about1.47 native pixels, within the declared rough manual reading uncertainty of ±2 source pixels / ±12 raw pixels. This is a diagnostic fit, **not** proof that every contour or limb matches.
- Only uniform sampling and translation were used. No local warp, stretched legs, per-part fitting, silhouette clipping or painted anatomy.

Source and candidate are shown at the same native coordinate scale in `Project/diagnostics/a13-npc/remaster-v1/fangzhang-native-source-generated-1x.png` and `...-3x.png`. The source still includes checker shadow; the candidate has no new shadow. Differences in their total alpha bounds must not be read as body-size differences.

## Alpha and border caution

True transparent pixels exist. Alpha≥128 bounds are `[7,2,795,1269]`; visible left hand and boots are not clearly cut. The head is extremely close to the top, with only2 pixels before the strong-alpha contour. Small alpha values reach the top and left boundaries, so generous transparent margin was not achieved. No confident missing scalp/hand fragment was identified; do not claim either perfect framing or definite amputation from the all-alpha bounding box alone.

There are20,101 pixels with alpha1–7, including low-alpha outliers away from the strong silhouette. Alpha≥8 bounds are `[6,0,796,1270]`, while alpha≥1 expands to `[0,0,1169,1285]`. Most body pixels have alpha252–253 rather than255. Thresholds were measured only; the raw alpha remains unchanged. Any later padding or technical matte decision must preserve the immutable raw and be reviewed separately.

## Next gate

The static candidate is usable for a further explicit silhouette/style decision, not ready for silent promotion. Confirm the stronger musculature/head detail, decide safe padding/alpha handling, then review native game placement and a separate single-shadow treatment. This task did not run the GUI, animate, shadow-fit, or change name/story/interaction data.
