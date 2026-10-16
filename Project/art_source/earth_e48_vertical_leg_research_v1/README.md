# Phase48 vertical front-leg research archive

Research only. This candidate does not replace archived48, the six-frame package or ordinary runtime art. No native motion/timing validation is claimed. Logical canvas 128×128/root(16,64); HD4 canvas512×512/root(64,256).

## Actual inputs and distinct decisions

raw.png, PROMPT.txt and REQUEST_PROVENANCE.json preserve the actual first generation. Ordered references1–3 are in references; reference4 is an exact tracked dependency at ../earth_e45_vertical_leg_research_v1/references/ref4-neutral-material-details.png. Generation is stochastic; raw bytes, not a prompt rerun, are authoritative.

The initial fixed-canvas mapping failed. Its original rejection measurements and frozen contract remain archived. Later global density registration was separately accepted from five independent upper-body anchors: head, shoulder, chest, forearm, hand. Rear shin and rear boot were held out; the target front leg did not enter that fit. GLOBAL_REGISTRATION.json preserves the full measurements, residuals, uncertainty and exact no-rotation transform:

- Uniform reference-to-fixed-map scale:1.278850545546816
- Translation HD4:(−29.583397614818637,−16.581466632834406)
- Rotation:0

These describe the measured forward relationship; rendering uses the exact saved output-HD4-to-raw affine, once with BICUBIC. No intermediate image resampling is used. reproduce.py independently recomputes the uniform fit from saved five-anchor coordinates and checks its exact agreement. The front-part rejection and residuals remain separate from a successful global density correction.

After registration, a separately approved bounded donor is translated rigidly by(−10,0)HD4 only. There is no further scale, rotation, warp or repaint. Its proximal377 alpha-positive pixels are a deliberate flattened joint/cloth underlap, not independently recovered shin alpha. Of those pixels,127 lie where fixed alpha is0,245 under partial fixed alpha and5 under opaque fixed alpha. The donor is under the original reconstructed fixed layers via ordinary source-over. All opaque fixed pixels remain unchanged;306 partial-fixed pixels change. Frozen support does not expand. Original frozen RGBA is restored outside old-right ownership or shifted donor alpha.

The candidate changes3,516 pixels versus archived48. Toe residual is approximately(+0.93,+0.37)logical, with proxy uncertainty±1logical. This does not establish a0.5-pixel pose tolerance, true skeletal landmarks, perfect isolated-alpha extraction or native validation. Flattened underlap can retain edge-darkening/material limitations.

## Reproduce

    python Project/art_source/earth_e48_vertical_leg_research_v1/reproduce.py --output /tmp/e48-reproduction

Output directory must not exist. Verified with Python, Pillow12.3.0 and NumPy2.3.5. The script checks all input hashes; reconstructs original fixed layers and registered pants from tracked source; registers raw; checks support/ownership/377-pixel underlap; composites and verifies exact final RGBA. PNG byte identity additionally depends on encoder version. No diagnostic file is needed.

## Failed targeted edit, unused

attempt2-rejected preserves its actual raw, prompt, request, failure explanation and two unique references. Its ref2 links to references/ref1-context-missing-right.png; ref3 links to references/ref2-source48-pose.png. Its ref1 is the exact registered first raw and also provides a compact reproducibility reference. This second generation failed front placement despite passing framing checks and is not used in the final donor.

No diagnostic boards, CPU GIFs, test harnesses, native captures or runtime integration are archived. Original six-frame and source assets remain untouched.
