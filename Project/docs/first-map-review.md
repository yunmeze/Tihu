# First-map research review

Open `scenes/earth_first_map_review.tscn` and run the current scene (F6). Default F5 and the existing sample/walk viewers are unchanged. This is a playable, optional art research scene, not whole-map replacement or final art/Windows acceptance. Linux native technical checks are described below.

The scene retains the original map, flags, A*, movement, phase timing, spawn `(61,39)` facing 3, object ordering, and existing shadow gates. Click to walk, hold Shift to run, Space to stop, F for follow camera. Walk east naturally to see E45–50; there is no forced animation or relocated spawn.

B compares research/full original actor; P compares the new union/original terrain. H hides controls only: Chinese research status, actual actor/terrain modes and fallback warnings remain visible. Other existing object toggles remain inherited and do not make B/P a whole-scene source comparison.

## Atomic fallback contract

The six E-walk selections are complete 512×512 canvases, drawn at 128×128 logical size, root `(16,64)`, with inherited seven-tick timing at project 50 Hz. Generated frames receive no extra original head. If any selected image or registration fails, all six use complete original body+head. Existing 18 generated phases keep their existing readiness behavior. Unsupported actions/directions use complete original body+head, with explicit status. No new E shadow is inferred or borrowed.

The 121 ground owners cover the birthpoint and south road only, out of 2553 original floor entries. All share one 1728×1920 density-two union over world `[2400,960,3264,1920)`. Each owner occupies its original stream position and draws a 96×64 quad from a 192×128 region, using linear filtering without per-region UV clipping. Seven overlap aliases create no extra owners. If anything in the registration, original map/manifest, complete floor stream, selected owner identity, or union fails, all 121 revert to original terrain. The old 64-owner candidate is never loaded by this scene.

Runtime dependencies contain no diagnostic or recovery-work paths. `tools/build_first_map_registration.py` deterministically reproduces frozen registration from pinned source evidence; the guard pins the emitted registration bytes. Regeneration with changed approved inputs requires deliberate source-pin and guard-hash review. Tests, mutation fixtures and captures are kept outside Git.

Headless validation covers parsing and logic only. Native interaction, seams, fonts and Windows acceptance require their own evidence; the permanent research label intentionally makes no acceptance claim.

## Verified Linux review scope

Godot 4.6.3 / X11 / OpenGL Compatibility / Mesa llvmpipe software-renderer checks passed: real mouse movement, readable Chinese status, H retaining status, B/P source comparisons, 768×512 and 1536×1024 display windows with the unchanged 1536×1024 production raster. External native checks covered six E phases/root placement, all 18 inherited phases, source path/movement parity, and exact rendered equality of rejected complete E/121 groups against explicit source fallback. Headless corruption/reload and deterministic registration-builder checks also passed.

This is bounded technical/native UI evidence, not final art or contact-shadow acceptance, hardware-GPU certification, exported-package acceptance or Windows verification. The south follow view visibly exposes the research/original coverage boundary; grass motifs/contact halos and boundary blending remain research limitations. The permanent research/unverified wording remains.

## Sampling contract

In-world E-walk uses LINEAR sampling, matching the existing 18 in-world candidate phases in `sample_world.gd`. Ground union also uses LINEAR for shared-plate owner seams. The standalone `earth_walk_review.tscn` deliberately uses NEAREST for its ×3 side-by-side inspection; its sampling is not the in-world sampling contract. No existing actor sampling was changed. An independent native direct-PNG reference at the same logical root, size and LINEAR sampling matched all six rendered E frames exactly, at both integer and fractional actor positions (12 RGBA-equal comparisons), confirming that no extra original head or other layer is added.

The final Chinese status reads “第一地图局部美术研究稿 · 未完成整图美术验收 / Windows 未测”, distinguishing completed native technical checks from unfinished art/full-map acceptance. Native wide/tall letterbox checks found opaque black margins and rejected all four margin clicks; the apparent terminal strip in an earlier desktop-wide capture was outside the smaller Godot window.

## Bounded static props

The optional review now also includes the original seven pool55–61 owners and three fine-clump248–250 owners. Q/W compare each complete group against source; L locates their context and Home returns the camera, without relocating the actor or changing its active path. The permanent status names all121/2553 terrain and7/3 static-prop scopes. See [first-map-static-props.md](first-map-static-props.md) for exact half-open support, retained master pixels, explicit weak-alpha omissions and group-atomic fallback. Full-map art and Windows acceptance remain unfinished.
