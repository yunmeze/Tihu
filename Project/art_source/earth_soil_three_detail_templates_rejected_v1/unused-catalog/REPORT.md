# Native detail region assessment: revised visible-cut criterion

Final decision: NOT ADOPTED. Stop catalog recovery and retain RAW as unused material/failure evidence. The exact wider regions are numerically cropable, but complete sampling does not establish a match to the original short marks. Their large D1 footprints and added nearby visible structures are unacceptable for that purpose. Do not shrink, fit, force, extract, place or apply. RAW_GATE remains FAIL.

The earlier alpha>0 connectivity STOP did not establish visible truncation. Positive-alpha completeness measurements remain in REGION_ASSESSMENT.json, but its visible-use decision is superseded by VISIBLE_CUT_ASSESSMENT.json.

CPU formula: per-channel source-over contribution = alpha/255 × |raw RGB − background RGB|. The real AI soil texture is sampled at the existing diagnostic phase; a separate real-texture color envelope removes dependence on that phase. Dark/light backgrounds are RGB 32 and 224. No new image or renderer was produced.

## Exact candidates and cut contribution

- G3_first: local [32, 8, 224, 206], native D1 [24.0, 24.75]; source rough size [10, 7]. Across the cut's inside/outside 1px band: alpha max 2; max RGB contribution AI 0.946, dark 0.118, light 1.624; any actual-soil phase bound 1.867; any RGB background bound 1.867 levels out of 255.
- G3_second: local [264, 272, 464, 464], native D1 [25.0, 24.0]; source rough size [21, 15]. Across the cut's inside/outside 1px band: alpha max 1; max RGB contribution AI 0.609, dark 0.110, light 0.863; any actual-soil phase bound 0.984; any RGB background bound 0.984 levels out of 255.
- F413_main: local [336, 192, 656, 392], native D1 [40.0, 25.0]; source rough size [22, 9]. Across the cut's inside/outside 1px band: alpha max 2; max RGB contribution AI 1.061, dark 0.180, light 1.686; any actual-soil phase bound 1.929; any RGB background bound 1.929 levels out of 255.

All three exact cuts cross residual alpha 1–2 only. No pixel in these cut bands contributes ≥3/255 to any RGB channel on any 8-bit background. Thus the measured candidates do not cut a high-contrast main structure or visible-strength continuous tail at their boundaries; literal alpha>0 connectivity alone is not a reason to reject them. This is a numerical statement, not a claim that sub-2/255 residue is universally imperceptible.

## Important limits

- These are wider samples, not three tight isolated dark cores. Additional smaller visible structures are fully included; the D1 footprints are materially larger than the coarse references. Nothing is renamed or fitted to conceal that difference.
- Simple compact main-window +8/16/24/32 D8 margins are unsafe: they cut substantially higher-contribution structures. Their measurements are included in the revised JSON.
- G3 first and F413 have visible content near wider 2–8px bands. Use of a different boundary, inset, UV/filtering behavior, or intended placement needs its own check. No runtime/filtering approval is claimed.
- Location and scale remain explicit construction inputs, never evidence that the original fixed-template generation succeeded.
- No raw edits, threshold cleanup, masks, image files, art generation, rendering, Godot, placement or runtime changes occurred.

Artifacts: VISIBLE_CUT_ASSESSMENT.json (revised numeric evidence), REGION_ASSESSMENT.json (retained topology measurements with corrected decision scope).

RAW SHA-256 unchanged: b4e8fdbf318a3b81e7e5f146c734ef634f88abdb192ec90f74b8183c926edeb6
