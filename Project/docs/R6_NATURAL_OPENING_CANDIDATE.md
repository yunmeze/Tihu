# R6 normal-warrior new-game candidate

Optional entry: `res://scenes/new_game_candidate.tscn`. Default R1 remains unchanged.

## User-visible flow

Click **踏入江湖 · 创建角色**, read the five original Config opening pages, and click **进入梦境**. Speak to 方丈, then 凌云子. The original B6 commits ET3, UNSTOP, A00(138,12), and the A00 load script together. The bounded result is arrival in the village's first room. This entry has no game save, combat, monster AI, character creation choices, or subsequent quest implementation.

The normal male warrior uses the verified factory: HP25/MP5, level1, one independently identified cloth252 in the armor slot, ET0=1 and original BT defaults. The runtime has exactly one `authority.inventory`. VM receives only the factory's small derived ET/BT/level/clear-count/mode projection. Factory `entry` remains the original creation request; current world/actor/reading-page are session state.

## Opening source

`tools/story/extract_opening.py` reads original Config.dat with the shared native Reader(kind8), at record96, 850 bytes. It checks the actual Config SHA, decoded script SHA, and exact equality with the reference opening. Its five-page reflow matches reference `storyPages`. Original text is retained; current responsive typography is an adaptation, not proof of the original executable's layout. Chinese display uses system Noto fallback; Windows has not been tested.

## Randomness and atomicity

The visible header labels the compatibility RNG. This is the separately reviewed Godot-based transactional provider, not the original VB PRNG. A newly created session receives cryptographic entropy once for its namespace/seed; it reserves actual provider values for map-load RND. It does not replace the sample with100, change BT to hide the chicken branch, or use the JavaScript reference's +1 conversion.

A failed creation keeps its pending factory state and RNG state for retry. Repeated creation or opening-final clicks cannot grant another cloth or consume another sample. Successful A13 load consumes one draw; ordinary A00 ET3 load consumes zero. The chicken branch is a registered, static source-image entity with no AI or combat; initial display facing remains an explicitly bounded display adaptation.

For dialogue, VM candidates must preserve readonly factory scalar queries. Only ET/BT changes are projected back into a copy of authority. All events, target identity, map-load script, collision target, and rendering resource closure are prepared before swapping authority, RNG, actor, world and STOP. Failure retains the previous dialogue and runtime state. Scene callbacks are synchronous; the inherited choice revision guards stale button callbacks.

## Rendering preflight

`world_resource_preflight.gd` validates JSON objects using structured parse results, actual map pack/frame references (all NPC and dynamic phases), all declared atlas pages, texture type and dimensions, rect/UV/crop/original/offset data, and both hero layers'128 frames before WorldView setup. Source JSON is never modified. Successful publication restores the ready gate. Startup UI is constructed without eagerly loading an unvalidated map. Restored dialogue texture is rebound on successful input preparation.

Original source movement, checker shadows, collision flags and depth ordering are reused. R5 SE art is a separate viewer and is not part of this new-game entry.

## Verification boundary

Native screenshots and logs are local test evidence, not runtime dependencies. Actual creation, all five pages, original two-NPC chain and A00 arrival were observed. Headless tests separately cover repeated calls, stale choices, failed resource preparation and state rollback. Malformed-resource failures found during independent review are preserved in that review's logs; only a final same-hash clean review establishes the corresponding safety claim. There is no persistence/reload claim for this scene.

Final frozen native verification (2026-10-15 UTC): candidate `bec1859c`, preflight `38ea536f`. Actual mouse clicks traversed creation, all five pages, A1–A5, B1–B6, then walked from A00(138,12) via (137,12) to (137,13). ET3, STOP=false, HP25/MP5 and consumed RNG count1 remained visible. The final independent headless audit passed the natural chain, 61 atomic checks, 51 malformed-resource cases and all six original failure reproductions. Linux native logging has no ERROR; the software graphics driver emits its known V-Sync unsupported warning.
