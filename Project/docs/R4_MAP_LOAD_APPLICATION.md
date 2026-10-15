# R4: detached application of four original map-load scripts

## Pure stage

`scripts/core/map_load_bridge.gd` consumes the frozen dialogue VM. `prepare(source_map, story, actor, context, registry, resource_preflight)` evaluates the original source loadScript and returns one detached candidate `{ok,map,story,actor,silent,events,error}`. No source JSON, input dictionary, scene, file, or random generator is modified. Failure returns no map/story/actor/events.

Actor input is `{cell:[x,y],stopped:bool,random_cursor:int}`. The caller supplies explicit story `level`, `clear_count`, `game_mode`, and `context={map_load:true,rnd_values:[int 0..100]}`. The cursor advances only in the returned successful candidate. RND is already resolved integer input; this stage does not implement the VB PRNG or silently reroll a failed chicken spawn.

The entire event list, bounds, registration and required resource preflight must succeed before returning the candidate. The runtime caller must still prepare its renderer/resources before publishing all fields together. The preflight callback is a trusted, side-effect-free authority supplied by the caller, not a script-controlled predicate. Tests use actual ResourceLoader validation of every registered chicken atlas page.

## Application contract

- STOP/UNSTOP prepare actor control state.
- MOVE validates the final source-map collision and prepares the local cell.
- DELNPC removes matching coordinates from NPC, source-spawn and dynamically-added-unit records. Duplicate removals are harmless. A02's `(35,35)` monster spawn is covered.
- SETMAPFLAG follows the reference apply order: apply all flags before other world effects. Flag 0 clears collision and clears kind/index only for kind 8. Flags 1/2 affect only flag-0 cells; both block, and 2 adds kind8/index1.
- ADDMON resolves exact registered name/definition ID and resource manifest, validates location and a local safety limit of 512 added records, then prepares an entity record. It has no AI, combat, action clock or inferred initial facing/layer. 512 is an adapter safety bound, not an original capacity claim.

The application-order claim is limited to the original A13/A00/A01/A02 load scripts and tested synthetic boundaries. It does not establish equivalence for arbitrary event sequences. Only the explicitly registered chicken can currently be added; ordinary source monster spawns remain source records without rendered units.

## Fresh validation

`tests/test_map_load_bridge.gd` runs 80 four-map cases over ET0 1/3/4/6/28 and explicit RND 0/4/5/100. It checks source/state/actor immutability, hidden NPCs, STOP/MOVE, north nine collision+pillar cells at their original condition, and A02 boss-record removal. It also tests missing registration/resources/draw, late invalid coordinate/event, malformed result/event/registry fields, source object preservation under clear flag, blocked MOVE, and added-unit capacity failure.

`diagnostics/r4/test.log` records the current assertion count and zero failures; import/test logs contain no ERROR. An early malformed-input test incorrectly expected a trusted preflight returning true to fail; its log is retained. A second malformed manifest-path case exposed an unguarded test resource callback; the adapter now rejects non-res JSON manifest paths and the test callback checks file existence/parse result before reading packs. That failure log is also retained. The check harness now explicitly counts failures and exits nonzero rather than relying on an assertion helper alone.

No GUI/default entry or source map files changed in this stage. R3 remains a separately labelled no-map-load dialogue fixture. Native map-load integration is the next stage, not a claim made by this pure test.

## Parent cycle finding and fix

The parent independently supplied `parent_bridge_cycle.gd`: a valid STOP event carrying a self-referential extra field previously reached `duplicate(true)`, emitted the engine's maximum-recursion error, and still returned success. That was a real fail-open boundary and blocks the earlier 812-only result from being treated as final.

The repaired bridge validates the complete source map, actor, VM result and registry before any deep copy. Traversal tracks ancestor identity and refuses cycles, non-JSON values (including Resource, Callable, vector and packed buffers), nonfinite floats, depth over 32, over 2,000,000 visited nodes, or over 8,388,608 text characters. The node budget accommodates full map cells/byte-offset metadata; it is a local safety limit. Dictionary keys may be String or Godot's equivalent StringName property keys. Shared acyclic containers are allowed. Actor accepts exactly cell/stopped/random_cursor. Each supported event accepts exactly its documented fields, even if an extra field would otherwise be valid JSON.

Fresh repaired runs: the exact parent probe returns false with no engine errors; `test_map_load_bridge_cycles.gd` has 41 checks/0 failures; the original suite still has 812 checks/0 failures. Both logs contain zero ERROR/SCRIPT ERROR. The parent finding is not relabelled a test-fixture problem.

Future inventory integration must pass only a small ET/BT/read-only-query snapshot to this VM, not a duplicated mutable inventory. Inventory remains a single authority and any future item-event application requires an outer atomic transaction; no such integration is implemented here.
