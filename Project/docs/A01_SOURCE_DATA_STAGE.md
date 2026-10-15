# A01 original-source data stage

Local extraction and validation completed 2026-10-15 03:20 UTC. Runtime not integrated; no monsters, scripts, combat, or portal transitions executed. This data stage depends on the remotely archived A00 baseline b76078f4ecdaba86e51355c0ccf241067fb981b5.

A01 海曦村北:150×150 /22500 original cells;7922 floor placements;251Wall,1193Plant,32Debris,190Building;0NPC,16portals,48spawn records. Original68-byte tail preserved uninterpreted. All map arrays and script/entity fields match the checked-in reference.

23 missing source frames added in one new atlas;333 required frames reuse previous atlases. All23 new RGBA/offset/crop samples equal reference. Independent raw-resource re-decoding verified961 cumulative frames across15 atlas pages, eight source hashes and zero out-of-bounds samples. Sixteen frozen baseline files remain byte-identical. Spawns are data records only, not rendered monsters.

Reproduce:

```sh
python Project/tools/extract_original_map.py A01 --base assets/original/maps/A00/manifest.json
python Project/tools/verify_original_assets.py --manifest assets/original/maps/A01/manifest.json
```

Production files: data/maps/A01.json, data/maps/A01-entities.json, assets/original/maps/A01/manifest.json, its one new PNG, and this document. Detailed audit/canonical comparisons stay ignored under diagnostics/maps. Remote persistence of this stage must be confirmed separately.

SHA256:
- map: `b36adeead3d3e868075e609622e8e6dde3975bb93ec8b4929fa7dad8359f3c95`
- entity_index: `7d3365b4094c329fa07665d7074dd25d31358353f8abc66b694b24b0b0bd6bb6`
- texture_manifest: `33f582c914ae7aab5ccea6d06c6f136629086d695171e7238e7feebb039a000c`
