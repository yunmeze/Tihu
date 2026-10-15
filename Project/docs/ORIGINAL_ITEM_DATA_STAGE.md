# Original item catalogue and initial-character evidence

Validated locally 2026-10-15. This is a data-only stage; it does not modify inventory_state, runtime, UI, saves, combat or the original materials.

## Source layout and counts

The shipped Data/Item0.lpRes contains **720 physical records**, of which 690 have names other than `0`; 30 placeholder records retain their original IDs. The final 148 bytes remain uninterpreted and preserved verbatim. The old 633-record expectation does not describe this shipped source.

Records on disk are variable length: a keyed u32 byte count and GB18030 name, 39 keyed signed16 fields, keyed u32 price, and signed16 reserved. A 140-byte native instance is a separate runtime structure, not the serialized template format. No synthetic 140-byte records or pointers are produced.

Each catalogue record preserves source byte offset/length, encoded record hex and hash, all raw words, per-word byte offsets/encoded bytes, requirements, icon and appearance indices, and unknown fields. No unknown values are replaced with defaults. Meaning/offset annotations are explicitly sourced to the reference parser/native-analysis scripts; direct byte verification is distinguished from semantic attribution.

Confirmed examples:
- 252 布衣: type 9, icon 767, appearance [2,3], weight 2, defense [0,1], price 25.
- 298 木剑: type 14, icon 923, appearance [1,0], weight 1, attack [0,1], price 50.
- 299 乌木剑: type 14, icon 1014, appearance [1,0], weight 2, attack/tao/magic each [0,1], price 150.

## Integration contract

Read catalogue.records by original numeric ID; keep templates immutable and reject placeholder records as usable items. Instance field values override templates, including weight and requirements. raw36 corresponds to runtime +0x7c usage counter, not heroAP; raw38 corresponds to +0x80 weight. raw28 and raw29 are retained separately despite the reference loader's shared +0x6c destination.

Named ordinary equipment slots come from reference character.js. Item types 13/14 mean shield/weapon and must not be confused with appearance slot indices 13/14. Native numeric slot mapping remains unresolved by this stage; consult the independent inventory contract rather than assigning unverified numbers.

The initial-character file is explicitly reference-derived, not a fully reconstructed native save. Normal creation equips only cloth252, with empty inventory/no learned skills and one skill/attribute point. The older createCharacter fixture grants a wooden sword and potions; it must not become normal initialization. Class cached totals already include cloth defense. heroAP and a complete native initial record remain null/unresolved.

Static objdump evidence covers the item loader and three creation branches and records executable SHA, VA/file offsets, raw spans and hashes. The original EXE is never executed. Class values remain attributed to the reference implementation pending independent full field tracing.

## Verification and reproduction

Run `python Project/tools/extract_original_items.py` from the repository root. It requires Python, the shared lp_original parser and objdump.

- All 720 decoded records exactly equal the committed reference catalogue.
- 28,080 numeric words independently decoded at recorded source offsets.
- Header + every encoded record + uninterpreted tail reconstruct the original bytes exactly.
- Original file hash unchanged.
- Two complete extraction runs produce identical four production JSON hashes.

Detailed validation remains under ignored Project/diagnostics/items. Production scope is one extractor, four data JSON files, and this document. Remote persistence is established separately by the parent Git checkpoint.
