# Fixed-scene density probe native review — 2026-10-15

The sole runtime operator captured256/384/512 world periods with two whole-material resamplers (point/NEAREST and lowpass/LANCZOS), plus the previous768-LANCZOS baseline. World sampling remained nearest mirrored addressing. Original143 keys,15 semantic masks, narrow-stone geometry/RGB, camera61,39, new South17 pose, selected temple/tree and existing shadows were held fixed. The768 baseline was already low-pass resized, not unfiltered raw.

Both runtime and environment reviewers actually viewed same-native-crops.jpg.256-lowpass gives the quietest grass and compacted-soil detail relative to the roughly70px hero; the curb remains legible.384-lowpass is a possible higher-detail alternative. Point-sampled variants are conspicuously sharper/noisier.512 and768 retain oversized/bright grain relative to the hero. Shorter mirror periods still contain paired/symmetric dark vegetation motifs; this is not naturally seamless material.

Recommendation pending parent decision: prefer256-lowpass for one bounded follow-up motion test, with384-lowpass retained as comparison rather than automatically selected. This fixed-pose comparison does not prove motion stability or long-field absence of symmetry. It did not repeat the earlier480tick route and does not expand143-placement scope. All raw images are immutable. No additional art generation took place.

Evidence: /workspace/shared/legend-rebuild-ground/density/
- 256-point.png /256-lowpass.png
- 384-point.png /384-lowpass.png
- 512-point.png /512-lowpass.png
- 768-lowpass.png
- same-native-crops.jpg (native crops, not resized before board composition)

Probe descriptor SHA256: e33c60ed00c4f9683255785e23c0fefe03accc9f27579efe0916e6c35fc6e131.
