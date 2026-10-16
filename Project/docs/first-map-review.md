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

The optional review now also includes the original seven pool55–61 owners and three fine-clump248–250 owners. Q/W compare each complete group against source; L locates their context and Home returns the camera, without relocating the actor or changing its active path. The permanent status names the current178/2553 terrain scope (existing121 plus57 extension) and7/3 static-prop scopes. See [first-map-static-props.md](first-map-static-props.md) for exact half-open support, retained master pixels, explicit weak-alpha omissions and group-atomic fallback. Full-map art and Windows acceptance remain unfinished.

## East corridor and complete plant instances (candidate)

The optional scene now stages a separately guarded 57-floor east-corridor extension, for 178/2553 floor owners total (existing121 + new57), plus 24 additional complete plant instances containing81 owners. These counts exclude the existing sample vegetation and the separately guarded pool7/clump3. This remains research integration: repeated yellow-green grass motifs and the23 outer source boundary contacts are explicitly unfinished art work.

P toggles both ground groups; E compares just the57 extension. R compares the24 plant groups. Keys1/2/3 locate east/west/south contexts; L locates pool/clump and Home locates birthpoint. Every shortcut moves only the camera: actor position, current path, collisions and flags remain authoritative. F resumes actor following.

The57 group and121 union are independently qualified. Missing57 tile/registration leaves121 intact; missing121 union/registration leaves57 intact. Shared source map/manifest dependency failure closes both. At live refresh, a change only to a57 source cell withdraws57; the immutable complete2553-entry floor-stream contract is shared, so any floor-record change or reorder (including a57 floor record) withdraws both groups. This preserves the older121 guard rather than broadening its eligibility. A768×768 periodic tile is deterministically rebuilt by the tracked expansion builder; the2304×2304 sampling neighborhood is constructed only in runtime memory. Density2, world-anchored period384,192×128 regions, LINEAR filtering and unclipped cross-owner sampling retain the isolated native contract. The original complete floor stream and owner positions are not reordered.

Each of the24 complete plant groups is published or withdrawn atomically, using existing immutable textures and original per-owner draw order/half-open ownership. A single fresh source-object index and dependency-existence cache are shared with pool/clump for each synchronous refresh. No new group acquires an old caster's shadow eligibility. Existing18 generated hero phases, E45–50, original unsupported-action fallback,121 union and7/3 props retain their separate contracts.

The combined scene passed its own bounded Linux/X11 native technical checks: real continuous mouse movement from birth through east, pool/clump, west and south contexts; three tree-front/tree-behind occlusion checks; camera-only shortcuts; E/R and Q/W source comparisons; and actual E45–50 playback. Its manual window used the unchanged1536×1024 raster displayed in a1152×768 client. An additional native matrix rendered genuine768×512 and1536×1024 rasters: all34 dependency cases at each density visibly differed from normal, matched explicit complete-group fallback pixel-for-pixel, and recovered exactly to normal (68 comparisons). Integer and0.5-logical-pixel camera views retained shared sampling without visible black owner cracks. These checks do not accept repeated grass motifs, the23 source boundary contacts, overall art or Windows. Tests and captures remain outside the shipped project.

The combined headless run measured100 synchronous refresh calls at about15.42ms mean; this is CPU refresh time, not an FPS or complete-frame budget guarantee. The release touches13 files: four optional-review implementation/document files, seven expansion guard/builder/registration/tile files, and the two entry READMEs. Default F5, ordinary sample scenes and R6 code are unchanged. The newly reused plant instances receive no new shadow qualification.
