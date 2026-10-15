# A02 original-source data stage

Local extraction and validation completed 2026-10-15 03:22 UTC. Runtime not integrated; monsters, scripts, combat, and portal transitions have not been executed. This stage uses the cumulative A01 data manifest; remote persistence of A01 and A02 must be confirmed separately.

A02 树林深处: 150×150 / 22500 original cells; 6952 floor placements and 1524 Plant placements; 0 NPC, 7 portals, and 84 spawn records. Original 68-byte tail preserved uninterpreted. All map arrays and entity/script fields match the checked-in reference. Spawn records are data only, not rendered monsters.

Eight missing frames added in one FloorBig atlas; 56 required frames reuse previous atlases. All eight new RGBA/offset/crop samples equal reference. Independent original-resource re-decoding verified 969 cumulative frames across 16 atlas pages, eight source-file hashes, and zero out-of-bounds samples. Seventeen frozen baseline files remain byte-identical.

Reproduce:

```sh
python Project/tools/extract_original_map.py A02 --base assets/original/maps/A01/manifest.json
python Project/tools/verify_original_assets.py --manifest assets/original/maps/A02/manifest.json
```

Production files: data/maps/A02.json, data/maps/A02-entities.json, assets/original/maps/A02/manifest.json, its one new PNG, and this document. Detailed validation reports stay ignored under diagnostics/maps. No runtime files were changed by this stage.

SHA256:
- map: `5bee9e9cd7e800b75eccd63b7dd5a907a17c620fdcab90266043ea12116cabc1`
- entity_index: `227337c9e825e078dd98bb87dfbc375f3d548f1b64a4d1a738e6e39ffd03bc3b`
- texture_manifest: `8f878ca4bc6c38954a6bfc87aa5394ab78730a9bcc64aff2bd0780a27057da3f`
