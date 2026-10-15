# A00 original-source data stage (local, runtime not integrated)

Verified 2026-10-15 03:09 UTC. This stage contains original source data and reproducible extraction only. It does not restore A00 gameplay, execute its scripts, render monsters, or imply a completed runtime test. Remote Git persistence is owned and verified by the parent; a local commit is not evidence of a remote archive.

## Outputs and hashes

- `data/maps/A00.json`: SHA256 `0f921a2714cab0a29383a8a25631b515b2de98fa38c02ed4701f0a19d3355868`
- `data/maps/A00-entities.json`: SHA256 `73ea3f80135fc58cacd0f910f466ca63e2f489c0681bcc1d878814dffd78fa8a`
- `assets/original/maps/A00/manifest.json`: SHA256 `f80e4a7e9c22be64b10ebfb395a88bec9adf42d5bd4136f509077665cea9811c`
- Seven new PNG atlas pages below `assets/original/maps/A00/sprites/`; their exact hashes are in the manifest. Existing A13 atlases remain referenced in place.

A00 is150×150 with22500 original cells,5338 ground placements,551 Wall,368 Building,752 Plant,88 Debris,15 Data4 effect placements,16 NPC records,19 portals and25 spawn records. The original source tail of68 bytes is preserved without interpretation.

## Verified boundaries

- All map cells, dimensions, home, names, NPC records, portal records, spawn records, load script and unparsed tail match the checked-in reference A00 extraction.
-554 newly needed frame RGBA values and original/crop/offset metadata match reference atlases exactly. Four requested frames reuse existing atlas samples.
- Independent re-decoding from original LP resources verifies all938 cumulative atlas frames across14 atlas pages; zero sampling bounds violations. Eight source resource hashes checked.
- Nine frozen files (A13 map, base manifest and seven A13 atlas pages) have identical before/after hashes.
- Kind8's fifteen instances remain original records. No nine-cell story gate is prematurely cleared or globally replaced.
- Scripts are indexed as text with source byte offsets and hashes, not executed. No runtime scripts are changed by this stage.

## Reproduce and audit

```sh
python Project/tools/extract_original_map.py A00
python Project/tools/verify_original_assets.py --manifest assets/original/maps/A00/manifest.json
```

The scripts depend on the already frozen R1 `tools/lp_original.py` and `tools/extract_a13_original.py`. Audit outputs are intentionally under ignored `diagnostics/maps/`: A00-incremental-extraction-audit.json, A00-reference-frame-comparison.json and A00-raw-atlas-verification.json. The production summary here records the gate without committing temporary test captures.

## Minimal stage paths

- `Project/tools/extract_original_map.py`
- `Project/tools/verify_original_assets.py`
- `Project/tools/ORIGINAL_EXTRACTION.md`
- `Project/data/maps/A00.json`
- `Project/data/maps/A00-entities.json`
- `Project/assets/original/maps/A00/manifest.json`
- The seven PNG files below `Project/assets/original/maps/A00/sprites/`
- This document.

Do not include another worker's unverified runtime or hero-action changes merely because they share the working tree. A01/A02 extraction is paused until remote persistence is confirmed.
