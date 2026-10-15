# Earth entrance candidate: SE idle/walk and 64 ground owners

Run `godot --path Project res://scenes/earth_sample_preview.tscn` (or open that scene in Godot). The default R1 scene and R6 natural opening remain unchanged.

This entry now offers the approved candidate SE idle sequence 13–16 and SE walk sequence 51–56, directly sampled from its density-4 atlas. The bounded v4 ground plate replaces exactly 64 original FloorBig owners. The hall now has a bounded 30-owner candidate, along with the two exact opening NPCs, the first tree and center shrub described below. Other NPCs/vegetation and unsupported actor actions/directions remain source. It is not a completed new-style sample. SE walking uses all six approved candidate frames, never a translated single pose. A single candidate SE shadow is now enabled only inside the SHA-bound conservative flat-ground gate; S toggles it independently. Press B to compare source/new SE idle and walk.

## Fixed review geometry

- World rectangle: `[2496,960,768,512]`.
- Logical viewport: 768×512; actual SubViewport raster: 1536×1024.
- Original actor starts at cell `(61,39)`; it is not moved to manufacture the composition.
- Original A13 cells, collision flags, A*, actor frames, NPC shared 17-tick clock and layer/Y/stable order remain in use.
- The window is resizable. A 3:2 letterbox preserves this exact visible rectangle; screen input is converted through its display rectangle and inverse 2× stretch.

Click to request an original-map route. Shift uses the existing reference-adapted run speed; Space stops. F switches fixed/follow camera, G toggles the source grid, H hides the explanatory HUD; B changes the retained source/new SE-body preference; P independently switches all 64 ground owners; T the hall, N the two NPC preferences, V the first tree and J the center shrub. Routes are not restricted to the sample rectangle. Follow mode explicitly leaves unconverted surroundings as source. This is an art sample, not execution of map load scripts, NPC conversations or portals.

## New asset preparation interface

The new assets must remain detached until their whole group is prepared. `scripts/earth/asset_guard.gd` returns either all validated owner resources or an empty dictionary. Its trusted expected identities must be built from the original approved owner scope, not the incoming registration. The current actor preparation validates the complete four-frame mapping, dimensions, density, logical offset, 12-tick schedule and actual source PNG hash before publishing one CanvasTexture. Missing or malformed dependencies clear the entire candidate and retain source body/head. SE walk uses its independently validated complete six-frame group at the original 7-tick schedule. Run and all other directions use source automatically; returning to supported SE idle/walk restores the saved B preference. Each failed actor group reverts its body/head together and disables its new shadow. The ground hook overrides only the original floor-frame drawing call, retaining its exact order before every object. Trusted scope is independently derived from original A13 cells at x52..66/y30..44, both step2. It requires exactly 64 identities, original source_cell, world origin cell*[48,32], 192×128 texture and scale .5; any failed record restores the entire source ground group. Tiles use nearest sampling of the direct 2× plate crops; no repeating texture or camera-relative UV is introduced.

Environment registration should provide exact original key, pack, frame_index, cell, layer, sort_y, stable_source_order and source_cell, plus high-density texture path/SHA/dimensions, logical world_top_left and common scale. Building fragments must preserve raw pixels once and source ordering. Ground is a separate 64-placement sample with original rectangles/alpha; it must not be treated as a background covering object ordering. Actor interfaces require complete approved source-frame mappings and density/anchor units. New Earth illumination must be reviewed independently; the retired courtyard cast direction must not be reused by assumption.

## Fresh verification on 2026-10-15

- Headless startup and mapping/source-flags/A* test passed.
- Actual native window 1152×768: click mapped to logical `(432,320)`, cell `(61,40)`, and actor arrived.
- Actual resized window 998×698 with visible top/bottom letterbox: click mapped to logical approximately `(431.7114,287.9519)`, cell `(61,39)`, and actor returned.
- Candidate raw SHA: `60f89f65dd817ec80065de941e62e36e1068302c3f2bc4eb5014d8d56f450c02`. The source and independent 1×/2× body-only diagnostic ran two complete 12-tick loops including 16→13. The same fixed map point repeated both loops, then an original A* move used source frame 58 and arrived at 61,40.
- Ordinary-entry B toggle was checked visually. Candidate preparation/fallback/recovery passed 128 checks. Empty-cache import of the newly added actor PNG and the same tests are recorded in the stage handoff. These internal images are not a claim that the new environment style is complete.

Original movement speeds and animation schedules retain their documented reference-adaptation boundary; this stage does not establish new original-EXE timing evidence.

## Ground v2 bounded native stage

Registration `assets/earth/environment/ground_plate_v2/registration.json` uses 64 exact source identities. Its source review measured six curb centers within approximately 2.5 logical pixels (manual source uncertainty ±3); this is an art-layout tolerance, not a collision alteration. All flags remain original. Shared full-plate PNG is provenance/optional comparison data, not loaded by this renderer. No new ground or actor shadow is added.

Actual GPU captures at 768×512 and 1536×1024 compare the same SE frame13 and world rectangle with ground on/off. Four original A* legs 61,39→66,35→61,39→61,43→61,39 completed 576 movement ticks; moving and unsupported idle directions visibly use original body/head. No piece seams were apparent in the reviewed joint image. Source building/vegetation/checker shadows remain visible and must not be described as the completed Earth style. Ground malformed/preparation/recovery checks: 101 PASS; actor regression: 128 PASS.

Parent review accepts this as an engineering candidate checkpoint only: grass scale/frequency still attracts too much attention and its visual design is not approved. The new 64 PNGs were imported into the existing isolated source-stage checkout with no previous cache for these textures; the 101 checks passed there. This is an incremental fresh-texture import, not a claim of rebuilding every historical resource cache.

## SE walk candidate extension

The same raw-density4 body atlas now supplies all six frames 51–56, with unchanged logical 128×128 draw rectangle and offset (-16,-64). Runtime does not add per-frame position corrections, change original movement speed or change the 7-tick schedule. Frame54 retains a visibly larger boot relationship (approximately +2.7 X/+3.6 Y logical pixels versus source); absence of a new shadow limits contact assessment. This is bounded body acceptance, not complete eight-direction replacement.

Native body diagnostics sampled idle16→two full walk loops→idle13 at independent 1× and true2×. A real original-map route 61,39→63,41 stopped after22 updates at (61.6875,39.6875): frame54→idle13 kept actor position unchanged; resuming covered all six phases and arrived in idle13. Returning NW used source. Ordinary renderer then repeated this route using only production asset paths. Preparation/malformed/unsupported/retained preference/recovery tests passed821 checks, plus128 idle regression; a newly imported walk texture in the isolated prior source checkout passed the same821. No environment art approval is implied.


## Ground v4 current bounded candidate

The independent entry now defaults to `assets/earth/environment/ground_plate_v4/registration.json`; P still restores original source ground. The 64 identities, floor order, flags, drawing rectangles and group-atomic failure behavior are unchanged. The old v2 resources remain historical. This v4 uses shorter grass detail; warm/yellow high-frequency highlights remain subject to joint lighting review. Six manually read road centers reach about 3.04 logical pixels difference, with source ±3 and candidate ±1.5 logical pixel reading uncertainty; this is not exact geometric agreement.

Actual 1×/2× same-pose comparison was reviewed before promotion. The 101 malformed-resource/identity/source-immutability/original-route checks pass for v4. Fresh import of all 64 new v4 textures is tested in the existing isolated source checkout; historical caches there are retained. No new character or environment shadow is enabled by this stage.


## Training hall candidate

T toggles the selected new hall and its original source group. Preparation binds the registration SHA and the trusted original 30-owner identity table, checks all 28 imported textures, and retains empty upper owners 3966/3978 as explicit source suppression records. Any preparation failure restores the entire original 30-owner group. Replacement draws occur at the original object calls, preserving the original 12 support / 18 upper records, sort Y, stable order and source flags. No whole-building sprite substitutes for the layered renderer.

Eight original A* destinations on both stairs and near doors were reached in 896 ticks. Source/new depth captures then intentionally used fixed original South17 for same-pose comparison; this does not certify all new actor poses on stairs. The independent 184 preparation/fallback assertions passed, including explicit empty owners and resource recovery. All 28 new textures were freshly imported into the existing isolated source checkout and the same 184 checks passed. R1 and R6 startup regressions remained clean. The ordinary entry still has no new shadow enabled at this checkpoint.


## Bounded Earth flat-shadow candidate

All ten selected SE idle/walk phases share one fixed 2D receiver proxy: reference (40,85.2463), slope -0.342818, cast (1.2,0.55), opacity .25 and logical blur .8. Density4 translates the blur to 3.2 texture pixels. The line was fitted to visible idle boot edges (manual uncertainty approximately ±1 x / ±.75 y logical pixels); it is not a surveyed 3D plane and does not pin individual walking feet. The original body pixels, anchors, movement and frame clocks remain unchanged.

Floors draw first, one shadow quad second, and all original support/object/actor streams follow. The eligibility mask is the sample rectangle minus the union of all original and selected hall alpha footprints expanded by four logical pixels. A common ten-phase projected-alpha envelope includes texel/filter support, blur/padding and visible boot proxies. Every translated envelope cell must fit entirely inside the allowed mask; fractional positions use area overlap, not rounded center samples. Roof projection in the exclusion makes this deliberately conservative. Building platforms/stairs, unknown inputs, out-of-sample footprints, unsupported/source body frames and B-source all disable the whole new shadow. The new body may remain visible with its shadow off. This is not coverage of every flat area or a platform receiver implementation.

S changes only shadow preference. The complete allowed/forbidden/envelope input chain is SHA-bound to ordinary runtime resources; offline raw/registration provenance is not loaded. An alternate structurally valid body atlas cannot borrow this envelope: the exact approved idle/walk manifests must also be bound. Source-project loose files are verified. Packed-export hashing has not been validated; missing required verifiable bytes fails closed rather than claiming export support.

The runtime uses row-prefix counts for area intersection. Actual original A* routes verified flat on at 61,39 and 63,41, off at stair samples 66,35/66,36, then on after return. B-source, missing gate, recovery and the explicit S preference were checked. The gate does not raise a shadow above an object to make it visible. Warm ground highlights and overall shared lighting remain under review.

## Single-instance Fangzhang candidate

N switches only original A13 NPC record 0, Fangzhang at (64,37). The ordinary manifest and actual PNG SHA are checked before publication, and the renderer matches its original kind/index/layer/y/stable order/world origin. All four original IDs 261–264 use the same approved density-4 static region under the existing shared 17-tick clock. This is one static pose, not four animated poses. No new NPC shadow is included. Missing/invalid resources restore the complete original NPC including its baked checker; other NPCs and all gameplay scenes remain original.

The source/new 1× and actual 2× samples cover two complete clock cycles plus the return at tick 136. The candidate-only ROI is byte-identical across all nine samples. Beside the current hero/hall its body scale remains readable; the approximate +3.76 logical-pixel boot-spread residual remains. Independent N does not change B/P/T/S preferences. The single-instance guard, missing-resource recovery, source-record mismatch and shared clock were retested in 309 checks. A separate checkout freshly imported this new NPC texture and repeated all 309 checks; older checkout assets retained their existing cache. No clean packed-export hash verification is claimed.

## First-tree candidate

V switches only the seven original Plant owners rooted at (57,34), IDs 292–298 at their exact original cells. Six nonempty high-density textures share one full 1254-square canvas, world origin (2630.25,784) and scale .25. Owner 298 is explicitly empty and still suppresses the old baked checker. The fixed registration SHA, actual texture hashes and original source cells are checked before publishing the entire group. Failure restores all seven original pieces; no new tree shadow is drawn.

The cropped technical version was rejected after nearest GPU sampling produced large internal differences. The same-canvas version preserves raw pixel ownership and reduces actual 2× whole/split differences to 39 pixels, max2 RGB, none above2. It is not GPU byte-identical. Original A* walked 512 ticks through rear (57,32), trunk-front (57,35) and all-front (59,38) positions; source South17 was used only as an explicit same-pose depth comparison after arrival. Original flags, ordering and movement remain unchanged. Only this one tree is covered; other trees remain source.

The production guard/identity/source fallback and the 512-tick route passed 1245 checks. An isolated checkout freshly imported the new tree textures and repeated the checks; previously imported unrelated resources remained cached. Initial integration rejected JSON float arrays against integer arrays; componentwise numeric identity checks corrected this without widening the approved identity set. The failed first log is retained as diagnostic history.

## Adjacent Lingyunzi four-phase candidate

N now switches both approved NPC candidates. Each NPC prepares independently and atomically, so an invalid Lingyunzi group restores all four source phases without disabling the valid Fangzhang group. Lingyunzi matches only original A13 record 1 at (62,36), order10001/layer1/y36, source113–116. Its four density-4 regions follow the unchanged shared 17-tick clock. No new NPC shadow is drawn.

Actual 1× and 2× nine-state samples cover two cycles plus return. Same phases across cycles are pixel-identical. Phase115's head dips approximately 2.26 logical pixels more than the source; 116 rises before returning to113. This bounded residual is retained, not corrected by per-frame Y shifts. The fixed boots and armor remain visually stable in this reviewed sequence. The production guard and independent recovery passed 310 checks, repeated after fresh import of the new texture in the isolated checkout. Other cached assets were retained.

## Center shrub and exact-instance guard follow-up

J switches only the four original Plant owners of the shrub at (57,38): 143@(57,35), 144@(56,38), 145@(57,38), 146@(58,38). Four full 1363×1154 canvases share world origin (2695,1141) and canonical scale 1/11. The leaf-bottom support band is a visual proxy, not a physical root. No shrub shadow is added. The other shrubs remain source. Original flags and sort Y 35/38 are retained.

Actual 2× whole/full-canvas rendering differs at three pixels by at most one RGB level. Five original A* destinations were reached over 480 ticks and source/new depth inspected; blocked cells remained blocked. Warm foliage highlights remain a shared-lighting residual. The ordinary entry passed 1219 guard/route checks, also in the isolated checkout with the new resource imports. The final native run repeated the 480-tick route and whole-group missing-resource/restore behavior.

Independent malformed-input review found unsafe Variant comparisons in the four exact NPC/tree/shrub guards, missing loose PNGs being accepted through retained import cache, and candidate state surviving WorldView setup reuse. The bounded follow-up validates consumed map/record/entry types before comparison, requires source PNG bytes before imported loading, and clears prepared groups and shadow bindings at setup entry. Invalid inputs return source fallback without engine exceptions. Successful reprepare restores the retained preferences. Hash checks here cover readable source-project bytes; packed-export support is not claimed.
