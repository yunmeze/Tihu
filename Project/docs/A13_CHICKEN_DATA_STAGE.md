# A13 original monster data pilot

Validated locally 2026-10-15. Original EXE was not run. No AI, spawn runtime, combat, VM random rule or map mutation is implemented here.

## Exact resolution

The original A13 load script contains `#if rnd < 5` followed by `#addmon 49 53 彩蛋鸡`. The raw map parser agrees with the frozen A13 JSON. There is exactly one matching monster definition: **ID 508, 彩蛋鸡, appearance 220**, from Data/Mon/0.lpRes at byte offset118383. The required sprite resource is Data/Mon/220.lpRes, not the definition ID's sprite file.

Fields preserved directly: sound鸡, HP500, regenFrames2, attack5, defense/magicDefense0, vision0, speed2, attackFrames50, behavior6, experience10, color[255,255,255,255], event `0`. rawExtra is [50,1,0,0,0,0,0,6,0,0,0]. Unassigned extra fields remain raw; initial direction/layer and native action lifecycle remain unresolved. Drop text and parsed tokens are data only; no probability behavior is implemented.

## Bounded assets and definition provenance

All600 monster definition records are decoded and preserved with source field offsets, raw signed fields, strings, encoded record hex, source SHA and reference provenance. The9020-byte unparsed tail is retained without interpretation. This is a definition table, not600 imported monster appearances.

Only Mon/220 is extracted:217 source records, including preserved frame0, into one2048×2048 atlas. The reference action mapping is idle1–32, walk33–80, attack81–128, death129–208 and corpse209–216, grouped by eight directions. These action indices/durations are explicitly reference-derived; generic attack animation duration is not substituted for the definition's attackFrames50. Frame0 is not assigned to idle. No direction, layer or initial action is invented for runtime.

The existing exact-black color key, reference pre-normalization crop, original canvas dimensions and per-frame offsets are retained. Original checker shadows remain part of the source sprite; no new shadow is generated. An eight-direction idle contact sheet was visually inspected: identifiable colored chicken sprites with clean transparent background.

## Verification

-600 definitions exactly match the checked-in reference catalogue.
-16200 signed words independently decoded at recorded offsets.
-Header, encoded records and preserved tail reconstruct original definition bytes exactly.
-217 sprite RGBA/crop/original/offset comparisons exactly match reference.
-Independent original-resource re-decoding verifies217 frames/one page, zero out-of-bounds samples.
-35 previous production asset/map/item files remain byte-identical.

Reproduce from repository root:

```sh
python Project/tools/extract_original_monster_pilot.py
python Project/tools/verify_original_assets.py --manifest assets/original/monsters/a13-chicken/manifest.json
```

Production outputs: data/monsters/definitions.json, data/monsters/a13-chicken.json, assets/original/monsters/a13-chicken/{manifest.json,0.png}, extractor and this document. Validation logs/contact sheet remain ignored under diagnostics/monsters. The sprite manifest uses the existing packs/pages/frames schema, isolated from all earlier manifests. Runtime integration and native rendering remain pending.
