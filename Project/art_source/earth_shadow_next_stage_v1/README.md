# Earth shadow next-stage CPU source archive v1

2026-10-15. Frozen CPU evidence and Fangzhang-only diagnostic handoff, not runtime assets or GPU acceptance. Parent authorized the next Fangzhang-only GPU diagnostic. Lingyunzi and first-tree casts remain disabled: the existing flat receiver rejects their conservative envelopes. No image generation, body edit, helper/runtime change or GPU test was performed by this measurement stage.

## Files and reproduction

- `fangzhang-diagnostic-interface.json`: exact A13 record0 identity, density4 atlas/region, immutable world transform, independently measured fixed footline, cast/opacity/blur, receiver policy and input SHA closure.
- `measurements.json`: CPU projection/bounds/determinants, conservative forbidden-area counts, four-phase Lingyunzi fixed boot-ROI checks and uncertainty-related below-line measurements.
- `ARCHIVE_SHA256.json`: SHA256 of these two JSON files, this README, and the reproducible tool. Paths are Project-relative. The checksum file does not checksum itself.

From repository root: `python Project/tools/earth/measure_shadow_next_stage.py` (numpy and Pillow). The tool reads existing input resources and writes only `Project/diagnostics/earth-shadow-next-stage/measurements.json` and `fangzhang-diagnostic-interface.json`. It never refreshes this archive automatically. Compare both emitted files byte-for-byte with this archive. Frozen input changes require explicit remeasurement/review; do not silently refresh SHA to bypass a failed receiver. Runtime must continue to depend only on ordinary resources, never this source archive or diagnostics.

No screenshots, PNG derivatives, test logs or environment-private absolute paths are included. Full plan: `Project/docs/EARTH_SHADOW_NEXT_STAGE_PLAN.md`. Shader and input SHA binding is technical reproducibility, not proof of physical 3D grounding, platform receivers or GPU appearance.
