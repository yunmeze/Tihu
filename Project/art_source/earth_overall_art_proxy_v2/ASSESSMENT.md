# EXPERIMENTAL — requires root review and native validation, not approved for installation

This is a separate 12-file delta candidate. It does not change any existing Project file or any SHA registration. The earlier overall-art-candidate-v1 shared-seam patch is BLOCKED because those scripts are pinned by existing A13 registrations.

## Pure-render isolation

- A00 only. A13 factory, renderer, floor pass and shadows remain untouched.
- Authority world remains the exact original map_load_world.gd LoadedWorld; the original controller's get_script()==LoadedWorld check remains intact.
- New renderer inherits map_load_world.gd -> world_view.gd solely to reuse the original _draw, ordered_objects, _draw_hero and Mon offset adapter. Neither ancestor defines _ready, _process, _physics_process, input callbacks, child creation, lights or shadow nodes.
- Never call proxy setup/setup_snapshot/refresh: no movement.configure, tick advance or input side effects. Input callbacks and physics processing explicitly disabled. The only _process action is queue_redraw.
- Read source render arrays, actor, tick, camera and show_grid at draw time. screen_origin delegates to the original authoritative world. No separate camera calculation, action clocks, world clone or persistent old-world snapshot.
- WeakRef avoids ownership cycles. Proxy is a child of the detached original world; failed staging/free/replacement frees the entire subtree. _exit_tree restores parent self_modulate if the parent still exists.
- Bind requires a plain A00 LoadedWorld with zero existing children, no material and disabled clip_children. This rejects unexpected layered/shader worlds instead of guessing. Base is Node2D, not CollisionObject2D or Control, and has no independent picking/input surface. It copies texture_filter/light_mask; no new light or shadow nodes.
- Only after entire registry preparation succeeds is the child attached and original.self_modulate alpha set to zero. UI is separate and retains original layout/click regions.

## Required native checks (not established by static analysis)

The design relies on CanvasItem.self_modulate applying only to that node, while child rendering remains visible. Native validation must confirm that the parent becomes visually silent, the child draws once, source/child alpha do not combine, and no source command/shadow passes leak or double draw. Also check inherited clip/visibility/light behavior, viewport transform/camera at world edges, and frame timings. The extra original _draw command generation may cost CPU even while transparent; profile full-map panning.

The same complete transaction test is mandatory: A13 opening -> natural A00 arrival -> mother -> chief A1–A5 -> exact rewards, nine gate flags, duplicate-action prevention and original rollback cases. Test hiding a texture/wrong hash before staging: leave source world visible, do not attach proxy, preserve success/failure behavior of the original transaction. Do not treat a single static screenshot as this validation.

## A5 source-contract fix

Original A5 applies Bridge.prepare_events to next_context.map before prepare_trial_world. Full cells equality would retract art after the reward. Registry now compares all floor/kind/index fields and all unchanged metadata/NPCs, and allows only the nine original A00 NORTH cells to change flag -1 to 0. The original gameplay context/authorization gates still determine whether that change is legal. No other flag transition is accepted. Source map file SHA, pack/frame metadata and generated image SHA remain strict.

_draw_frame origin is source cell origin plus screen_origin; top is a separate argument, so cell lookup excludes top correctly. NPC offsets are applied only after lookup. Floor top is zero. The nine NORTH flags retain source layer1 (-1 and 0 both resolve to layer1), and layer calculation remains authoritative.

## Assets

Seven actual unmodified raw images: 3915 A00 floor owners, 40 mother-house owners, 679 tree owners, four-phase mother NPC, and UI. There are 4635 owner groups / 4638 phase records. No A13 art changes and no default main/F5 change. Native candidate entry is scenes/earth_overall_art_review_v2.tscn.

## If proxy fails isolation

Do not weaken checks or update hashes blindly. ../overall-art-candidate-proxy-v1/shared-patch-pin-impact.json records the conservative SHA consumer closure for the three possible edited source files. It includes provenance/qualification metadata as well as runtime consumers, so it is an impact graph, not a claim that all 155 consumers must be changed. A legitimate shared-render version migration needs source review, exact impacted runtime-contract regeneration, dependent hash updates, and their original regression suites. No registrations were edited here.
