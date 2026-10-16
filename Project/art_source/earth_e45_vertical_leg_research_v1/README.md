# Phase45 vertical front-leg research candidate

Research only. This package does not replace the archived six-frame sequence, ordinary runtime art or native validation. Canvas 512×512 (HD4); logical canvas 128×128, logical root (16,64), HD4 root (64,256).

## Actual generation and replay correction

Attempt2 raw.png, PROMPT.txt, request record and four ordered references are byte copies of the actual generation materials. Its raw output is 1254×1254 and maps once to the full 512×512 canvas with Pillow BICUBIC. There is no fitted limb scale, translation, rotation or post-hoc registration.

IMPORTANT: the actual ref1 and ref3 retained an obsolete 178-pixel knee bridge. A PIL Image.fromarray shared-buffer bug allowed a later NumPy knee assignment to mutate the saved purported waist-only snapshot. The reference hashes are accurate; the old claim that those images lacked the bridge was false. Do not silently substitute the corrected replay for the actual generation input. The original buggy helper is preserved as non-executable text in provenance, with its inaccurate claims explicitly superseded here. The pre-correction request is historical only; REQUEST_PROVENANCE.json contains the disclosure.

reproduce.py rebuilds the split core from tracked raw art and masks, replays the original fixed layers with explicit copy-based snapshots, and omits the knee stage. Corrected replay differs from actual ref1 in exactly 178 pixels, all within original bridge ownership. This is separate from the explicit 96-pixel cloth-removal exception, which removes alpha only at frozen owned pixels and preserves RGB. Seven of those pixels were opaque; a blanket claim that all original opaque pixels survive would be false. All other opaque fixed pixels survive unchanged.

Support is the frozen 5,253-pixel domain plus exactly 21 approved instep AA pixels, totaling 5,274. The generated full-context sample is placed beneath the corrected fixed plate after the 96-pixel cloth cleanup. Final ownership also includes old-front and obsolete-bridge ownership. Original frozen RGBA is restored outside that combined domain. This remains a bounded flattened donor, not a recovered isolated-alpha component; possible edge-darkening and cross-phase/material differences remain research issues.

## Reproduce

From repository root:

    python Project/art_source/earth_e45_vertical_leg_research_v1/reproduce.py --output /tmp/e45-reproduction

Use a nonexistent output directory. Python, Pillow 12.3.0 and NumPy 2.3.5 were verified. Inputs are hash-checked against ARCHIVE_PROVENANCE.json. The script rebuilds all needed layers from selected files and tracked dependencies, verifies exact final RGBA and writes HD4, derived128 and corrected replay. No diagnostic files are required. PNG encoder changes may affect compressed bytes without changing RGBA.

## Rejected attempt1

attempt1-rejected preserves only its actual raw, prompt, request and four nontracked references. Its first reference, ref2-frozen45-full512.png, is byte-identical to ../earth_e_walk_layered_research_v1/45-HD4-RESEARCH.png and is dependency-linked in ARCHIVE_PROVENANCE.json. This failed isolated-component approach is historical context, not input to attempt2 or the selected composition.

No CPU GIF, native capture, diagnostic board, test harness or runtime integration is included. Static research acceptance does not establish native timing, motion continuity or production approval. Source files and the archived six-frame package are unchanged.
