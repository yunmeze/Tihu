# First-map pool and fine-clump integration

Only the explicitly opened `scenes/earth_first_map_review.tscn` includes these two bounded static-prop groups. Default F5, `earth_sample_preview`, R6, map data, collision, paths, actor phases and shadows are unchanged. This remains a local art research review, not whole-map art acceptance or Windows validation.

## Selected support and immutable art

- Pool55–61: all seven original source rectangles, density2, world origin(3086,1800), unchanged640×496 registered master. Twelve alpha1 texel centers in that finite master remain outside renderer support. Separately, the archived finite master already excludes36 alpha1 samples from the larger raw-mapped view. No additional alpha cleanup is performed.
- Fine clump248–250: unchanged512×512 full-canvas master, density4, world origin(3031.5,1744). Selected half-open pixel rectangles are[20.5,176,162,375.5),[162,104.5,354,402.5),[354,105.5,490,356). These add only a bounded half-texel outer LINEAR-filter halo to the earlier proposal, preserving the internal x boundaries. They leave551 alpha1–2 texel centers outside support. Those pixels, including zero-alpha colored pixels, remain in the complete master.

Each group owns one shared full-master texture. Its original7/3 draw calls use LINEAR `draw_texture_rect_region` with `clip_uv=false`; there are no per-owner image files, masked textures, alpha thresholds, rebased anchors or collapsed group sprites. Original layer/y/stable-order positions remain authoritative. Enlarged archival full-height strips and distant-dust all-alpha supports are not integrated.

## Runtime and fallback

`assets/earth/first_map_review/static_props_registration.json` pins both masters, original source map and source atlas metadata, exact source cells/flags/frames, selected support and omissions. Its six `runtime_files` records list only the actual two masters, map, atlas manifest and two source atlas PNGs. Historical contracts/proposals are separate provenance records and are not runtime dependencies.

`static_props_guard.gd` pins the registration SHA. It verifies every group dependency and complete source map/manifest identity before returning a whole group. Missing, invalid, duplicated or changed source owners reject the entire corresponding7/3 group. Reload clears the previous group before preparation; live disappearance/identity change also withdraws the complete group. Original source rendering handles fallback. No diagnostic or recovery-work resource is loaded.

## Controls

Q toggles the complete pool group; W toggles the complete fine-clump group. L moves only the camera to the pool/clump context. Home moves only the camera back to the birthpoint view. Neither relocates the actor, clears its path, changes its action or modifies collision. F retains actor-follow behavior. Click/Shift/Space preserve ordinary walk/run/stop. H hides instructions only: permanent Chinese research status still shows terrain121/2553 and current pool7/clump3 status or fallback reasons.

## Reproduction and evidence boundaries

Run `python Project/tools/build_first_map_static_props.py --check` from the repository root. `--output <path>` emits a deterministic registration elsewhere. The builder verifies immutable master hashes, original atlas RGBA, source cells, nonoverlapping support and exact omitted-center counts; it never edits artwork. Changing the selected support or input identities requires deliberate registration/guard-hash review.

External Linux Godot4.6.3 GL Compatibility/llvmpipe diagnostics tested2× and4× true framebuffer raster scales, integer and.125/.25/.5 logical camera offsets. Shared internal seams and full-master reference partitions matched exactly. Selected bounded clump support differed from the full master by observed RGB≤1 on tested new/source grass and≤2 on the tested road patch. These finite renderer observations are not universal blending-space bounds. Source-path/occlusion, whole-group fallback, existing18 phases, sixE-walk phases and121-ground regression are separately checked before publication. Tests, captures and mutation fixtures remain outside Git.

## Completed integration regression

The integrated optional scene passed52 headless assertions, including complete map/object/floor/sort parity, all10,000 movement cells, real A* trajectories, existing18/E6/121 readiness, malformed page and short-map fail-closed cases, and dependency-group withdrawal. Eleven default/sample/source/movement/ground resources remained byte-identical to published872c292.

Fresh native regression against immutable872c292 produced exact RGBA equality in54 full-world actor/terrain comparisons (18 existing phases, sixE-walk phases and three source examples at integer and true0.125-logical-pixel actor offsets),12 props-area source-toggle comparisons and10 registration/dependency fallback comparisons. Another12 integrated selected-prop captures exactly matched the previously validated bounded-support trial at six actor-depth positions and camera offsets0/.125. Shared registration/map/manifest loss withdraws both dependent groups; a group-specific master loss withdraws only that group. Real same-path fixtures in an isolated copied project also rejected each missing master, a valid same-size PNG with one opaque-pixel channel changed, and altered registration bytes. Real project files were untouched.

CPU-only refresh benchmarking used1156 source objects,100 warm-ups and1000 refreshes per world at spawn and props locations, alternating100-call batches. On the measured AMD EPYC9V74 / Linux X11 / llvmpipe environment, integrated native mean refresh cost was11.08–11.09ms versus8.97–9.24ms for872c292, an extra1.85–2.11ms. Integrated median was10.81–10.90ms and p9512.42–13.00ms; observed isolated refresh outliers reached27.77ms. Headless mean was10.68–11.16ms versus8.89–9.10ms. These timings exclude deferred draw generation, GPU rendering and presentation, and do not certify frame rate or hardware-GPU performance. These figures describe the original integration before the lookup optimization below.


## Per-refresh lookup optimization

The reviewed optimization based on commit `01d5f0fc7ec788cfe54e53ab6a0a916328b7074d` builds one fresh targeted-owner index and file-existence snapshot per synchronous refresh. It preserves duplicate detection, stable-order field and complete owner/cell/atlas validation, original failure precedence, and whole-group withdrawal. The snapshot is discarded after each refresh; dependency availability is checked anew on the next refresh. Preparation/reload still verifies original byte identities. Pure object-array permutation remains accepted, as in the baseline; changing a stable-order field or introducing a matching duplicate is rejected.

In paired Linux Godot4.6.3 headless CPU measurements with1,156 objects and10 owners,100 warm-ups and1,000 refreshes per variant/location, mean refresh cost changed from11.165 to9.609ms at spawn and10.524 to9.360ms near the props. Guard-only mean, including construction of the fresh snapshot, changed from1.629 to0.523ms. The differential matrix matched both group decisions and exact failure text for62 live mutations; dependency withdrawal and explicit reload recovery also matched. An independent clean frozen-source rebuild passed the 62-case differential matrix and two reload pairs. The benchmark figures remain isolated headless CPU observations, not a native or Windows result. They exclude deferred draw, GPU and presentation; the observed candidate maximum22.142ms does not establish a50Hz guarantee. Tests and profiling outputs remain external to Git.

The existing export-closure tool remains a historical reproducible build pinned to source commit `3d1cbee54f1f5a64753148cb0908761c7a9725ec`. This optimization does not upgrade that tool's source or code pins automatically. A future package containing the optimization needs a deliberately reviewed new frozen source/policy and complete controlled-pack revalidation; retain fail-closed checks.
