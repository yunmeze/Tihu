# Paused HD technical checkpoint — 2026-10-15

The user rejected the current overall art direction on 2026-10-15 at approximately 07:24 UTC. Further integration, visual expansion, and optimization stopped. These files preserve engineering work for reference; they do not represent approved style or a completed production HD entry.

## Verified diagnostic implementation

The three `verified-diagnostic-*.gd.txt` snapshots correspond to the existing local diagnostic implementation. They rendered a real 2048×1536 SubViewport with 1024×768 logical coordinates. The final complete-candidate capture SHA-256 is `a2e709b852041ed292e9a8a228f9c84eb47c71fa409d86ddf8964aac88f1ede3`. This was direct GPU readback, not an enlarged 1024 image. Rendering detail, exact owner scope, frame mappings, cast units, and two window/input sizes were tested in this bounded diagnostic. See `capture-evidence.json` for scene scope and limitations.

The snapshots retain diagnostic and art_source resource paths intentionally. They are text records, not installed scripts, public scenes, or export dependencies. Their automatic screenshot paths are local evidence paths and must not be carried into a public entry. Reconstructing this experiment requires restoring the named source/diagnostic assets, importing them, and re-running verification; the snapshots alone are not a launchable package. Existing source gameplay and 1× art_preview entries were not changed.

## Partially implemented production connection

`unfinished-hd-art-world.gd.txt`, `unfinished-hd-floor-pass.gd.txt`, and `unfinished-hd-art-resources.gd.txt` preserve the interrupted ordinary-path integration. The world controller does not yet define `install_environment`; it must not be installed as a runnable script. There was no final ordinary HD scene, cold-import closure, or production acceptance.

The resource helper's 45 initial malformed-input checks passed, but independent follow-up testing found uncorrected issues: very large finite doubles can overflow float32 Vector2; tiny positive scale can underflow to zero; some declared identity fields are not checked; a textual assets prefix permits `../` traversal outside that directory. The independent snapshot and saved helper differ because a later hero preparation method was added; no final-version audit was completed. The independent report is preserved as `unfinished-guard-audit.json`. These are known blockers, not waived tests. No production code currently references the unfinished helper.

## Resume boundary

First obtain approval for an overall same-view art direction. Only then decide whether these technical results are useful. If reusing the HD implementation, complete and re-audit resource preparation before any atomic owner/body/shadow publication; keep actual source geometry and input mapping, unsupported-frame source fallback, and single-pass shadow units. Re-run current-code GPU, fault/recovery, source entry, and clean-import tests. Historical counts and images cannot replace that revalidation.

Original raw art, source registrations, and promoted resource directories remain owned by their respective asset maintainers. No files were deleted to abandon this work, and no unfinished scene was made default.
