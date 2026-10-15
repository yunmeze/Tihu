# Earth-base entrance sample: implementation boundary

The user accepted the broad direction of `art_source/earth_base_style_concept_v1/concept.png` on 2026-10-15. This is direction approval, not approval of its exact stairs, route, planter geometry, or a completed engine scene. The current task is one playable entrance sample. No new assets or runnable Earth-style scene have been connected yet.

## Smallest useful deliverable

One independently launchable pure-2D sample containing the A13 main-building entrance, its immediately adjacent original ground placements, and a movable protagonist. Keep the original A13 coordinate transform (48×32 logical cell steps), source flags, original A* rules, actor origins, NPC identities, and existing animation clocks. The new entrance must register to the original source owner's footprint and both stair approaches. Existing gameplay entries stay unchanged.

The concept has a central wide stair and new raised planters, whereas the source entrance has two access stairs and specific traversable and blocked cells. Rebuild the visual design around source geometry. Do not flatten the source into the concept, shift doors, add collisions for decorative planters, or place visually solid objects over a traversable route. Door/portal semantics must come from source data, not from an apparent opening in the concept.

## Asset contract and draw order

- Generate separate high-density ground, building, actor, and shadow inputs. Never use the entire concept as the game background.
- Ground remains exact original placement rectangles and stable keys. Material detail is world-locked; camera movement does not move the texture pattern.
- Building registration retains each original owner, source cell, layer, sort Y, and stable order. Classify continuous support surfaces and narrow stair risers according to the source support strips; keep side cheeks, walls, rails, and roof occluders in their source ordering. All generated pixels must have exactly one owner.
- Draw ground first, then single static casts received by that ground, then the original ordered object/actor stream. Buildings' supported top surfaces remain in their verified source layers; character shadows on elevated surfaces require a separately proven receiver and must not be globally raised over side walls.
- A static cast is generated from the approved whole object once, not once per fragment. Atomically replace the complete source owner group and its baked checker only when every replacement and shadow dependency is prepared. Any failed preparation leaves the complete source group and suppresses its new cast.
- Actors retain their logical origin, frame map and source timing. Dense textures use explicit density and logical dimensions. Unsupported actions/directions fall back to source body/head together, with the new shadow off; the user's art preference survives that temporary fallback.

## True high-density display

The locked entrance sample now uses a real 1536×1024 SubViewport with 768×512 logical size override, covering world [2496,960,768,512]. Show it through a resizable 3:2 letterbox. The earlier whole-screen HD experiment used 2048×1536 / 1024×768; that is historical evidence, not this sample’s rectangle. Convert mouse coordinates through the display rectangle and inverse viewport stretch before querying the original map. Verify actual mouse paths at two window sizes. Directly save the 1536×1024 render texture for evidence; enlarging a low-resolution capture does not qualify.

New actor artwork must be sampled directly from its generated high-resolution raw registration, not from the old reduced atlas. For density 4, a 512-pixel frame can occupy 128 logical pixels. The density-aware shadow API takes logical region, reference, transform and blur; it performs the internal ×4 / ÷4 conversions once. Material style, illumination and palette await the new Art Bible; old courtyard assets are not the new sample's approved art.

## Preparation guard

`scripts/earth/asset_guard.gd` is a standalone preparation utility, currently not connected to a scene. It rejects non-finite or out-of-float32-range coordinates by a tighter ±1,048,576 logical bound, and rejects scales outside 1/65,536 through 4. Asset paths must be canonical `res://assets/...png` paths without dot segments, repeated separators, backslashes, percent escapes or control characters. Owner identity matches a caller-owned frozen source scope before textures load. Returned values contain only validated fields, and the group returns empty on any failure.

The caller must independently construct the trusted scope from the approved original map. It must not derive expected identity from the incoming replacement manifest. Loose source PNG bytes are SHA-256 checked when available; imported texture dimensions are checked. Packed exports require an independently verified import/build manifest and must not claim runtime raw-byte verification when the PNG is absent.

Initial author tests: 120 checks, zero failures on Godot 4.6.3. These exercise a source-derived existing fixture solely for guard validation; they do not test new Earth-base assets. Independent final review on helper SHA `c5a0718736b91ceac6aea417a464840e61b33c03b19d8dc3f61272339a7cdf4e` passed 332 main checks and 64 control-character checks, with no engine errors or partial publication. It also verified integer-valued JSON floats against trusted integer cell/source-cell identity. This covers the independent preparation module only, not runtime publication or packed-export byte verification. The previous incomplete HD helper and its findings remain historical recovery records.

## Acceptance order

1. Freeze the Art Bible and new source-registered entrance/ground/actor interfaces.
2. Validate resource closure, exact owner scope, raw provenance, density and one-owner alpha reconstruction before GUI launch.
3. Compare whole/partition GPU output at the actual world origin; record rounding differences honestly.
4. Walk original approaches and stop on source-reachable stair/door-edge points. Inspect boot contact, side-rail occlusion and layer boundaries. Do not force blocked positions and call them walks.
5. Check static and actor shadows on/off at fixed phase, object-before/after depth, failure fallback, and two window mouse mappings.
6. Present the real sample and its style for review. Only after it runs can it be described as a playable new-style sample. General map coverage, full action coverage and new-game reskin remain separate work.
