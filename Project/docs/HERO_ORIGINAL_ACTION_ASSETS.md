# Original hero actions: R2 asset recovery

The extractor `tools/hero/extract_actions.py` reads immutable Hero/2 and Hero/Head/0. All 152 action source poses (304 layers) are available in `data/hero/actions.json`; movement.json is unchanged. Frame0 is metadata. Attack129–176, cast177–224, hurt225–248, death249–280; direction order N clockwise. Index = base + direction × phases + phase.

Two action atlases preserve full untrimmed source rectangles and native offsets. Render body then head at the same native draw origin + offset. No source colors are removed except exact RGB0,0,0 transparency. Native checker remains part of the body. Extraction validates every nonblack RGBA byte, explicitly including RGB16,8,8, and every atlas rectangle against the decoded layer hash. No guessed skeleton or normalized bounding box is used.

`action-frame-index.json` records each source ID, phase, actual layer offset and alpha bounding box. Bounds include native shadow and must not be treated as body joint measurements. Preview pages use192×192 and a common48,80 draw origin only for presentation; the runtime uses original offsets. Every original rectangle fits without clipping.

## Actual visual review
All32 direction/action strips were inspected after extraction. Attack48 and hurt24 have per-frame qualitative observations in `attack-hurt-visible-analysis.json`. Those72 entries do not restore the missing old joint-point tables: hidden hands, knees and support identity remain unknown. Original attack last poses differ from both first pose and idle; never force a seamless attack loop. E142 turns left before E143 shifts right; N130 and NW172 sink before rising. W168/169 retain short bent rear-leg projections; SW attack short-boot visibility must not be copied from S.

Hurt recovery differs by direction. N/NE lift from forward compression; E/S/SE recover from backward tilt. E233 has a more upright trunk and low hand near the pelvis. Do not freeze the first hurt head angle or mirror another direction. The24 original poses do not establish damage admission or full action duration.

Cast48 and death32 were visually reviewed as ordered source strips, but detailed per-joint annotations are not claimed. Cast typically gathers arms before raising/extension and returns toward a different terminal pose; death progresses from standing/imbalance to a distinct fallen silhouette, with original head layers preserved. No source-drawn shadow is independently duplicated.

## Timing boundary
See HERO_ACTION_TIMING_EVIDENCE.md for current original-EXE byte/instruction audit versus reference code assumptions. Asset order does not prove uniform playback, first displayed phase, event time, attack interruption or state exit. No combat logic is enabled by this extraction.

Diagnostics (source strips, comparison sheets and validation JSON) live under ignored `diagnostics/hero/actions/`. Only source assets, reproducible tools and compact runtime data belong in the production snapshot.
