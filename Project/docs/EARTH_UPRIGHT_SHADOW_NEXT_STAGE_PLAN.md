# Two upright-tree shadows: CPU next-stage plan

## Decision

Both remain **disabled under the current receiver**. This is failure to establish a complete receiver, not a claim that an offscreen root cannot cast a physical shadow. No current mask, four-caster contract, production helper, shader, tree body or registration is changed by this study.

Source: `assets/earth/environment/upright_tree_v1/raw.png` (SHA `ada0e0fd8952fe1dcc6b60dafb9d64be96476ed7736a881f1e5e401436b3db0f`), 1162×1353, 776650 positive-alpha texels. Both registered instances use the same raw image at **density 4.5**, strictly translated by world (528,320). Each retains its six exact Plant:299–304 identities; owner304 is intentionally empty, but its identity still matters.

| Instance | Registered wood root world | Full conservative world bounds xyxy | Outside current sample, half-logical cells |
|---|---|---|---:|
| (50,41) | (2436,1326) | (2329.2889,1321.2056,2913.1556,1490.2944) | 30560 / 134420 |
| (61,51) | (2964,1646) | (2857.2889,1641.2056,3441.1556,1810.2944) | 134420 / 134420 |

Current sample is world [2496,960,768,512]. The left shadow has 103860 envelope cells inside it, but must not be clipped to those cells. The bottom shadow has none. Two upright envelopes do not overlap. Their intersections with the current Lingyunzi four-phase and first-tree envelopes are zero. Current Fang envelope ends at y1245.893, so is disjoint. Moving SE is not a permanently fixed shadow: future approved locations can overlap these regions; current tests do not claim a universal SE/non-overlap result. Existing world-bound SE gate remains authoritative.

## Ground contact and projection confidence

Registered wood root raw (560,1329), logical (124.4444444,295.3333333). Its 5×5 raw neighborhood is alpha247–251: it is real material, not a lowest-alpha fringe chosen each frame. Registration uncertainty is ±9 raw pixels (±2 logical), with source anchoring ±4 logical. These are manual registration bounds, not recovered ground-plane geometry. Common slope0 is only a fixed wood-root flat-ground hypothesis; do not reuse an NPC footline.

For the unchanged cast (1.2,.55), opacity .25, logical blur .8, use logical projection matrix [[1,-1.2],[0,-.55]], translation (354.4,457.7666667), determinant −.55. Raw blur is **3.6**, not3.2. All alpha>0 texels are retained. CPU envelopes include half-texel bilinear support, transformed per-texel AABBs, blur .8 plus safety1 logical, and the fixed root proxy. There is no receiver clipping in the validity calculation.

## Minimal additional receiver verification, if separately authorized

Do not expand to the whole map or equate the screen boundary with a physical boundary. Validate two small world-space patches, separately from the current receiver:

- Exact integer enclosure, left: Rect(2329,1321,585,170).
- Exact integer enclosure, bottom: Rect(2857,1641,585,170).
- Recommended review windows allowing the present root uncertainty: Rect(2319,1311,605,190) and Rect(2847,1631,605,190). The extra10 is a review allowance: combined root-y uncertainty6 changes projected x by7.2 and y by9.3. It does not authorize changing body placement or shadow parameters.

An all-map source-frame AABB scan, including tall objects whose owning cell lies well outside these patches, found the following review supersets:

- Left window:28 FloorBig records,9 Plant records; no Building or Wall source frame intersects.
- Bottom window:28 FloorBig records,14 Plant records,3 Debris records; no Building or Wall source frame intersects. Debris57@(66,62),58@(67,63),59@(68,63) must be materially inspected despite their distant owner cells.
- Left floor IDs:406,577,581,586,587,594,595,604,608. Bottom floor ID406. All per-record source cell, order, pack, frame, atlas page SHA and true source render bounds are archived in measurements.json.

These counts are a review inventory, **not proof of flatness**. Minimum additional evidence: inspect those floor transitions and the three debris materials in original atlas pixels; establish coverage/no holes across the complete projected envelopes; distinguish raised platforms, slopes, walls, ground decorations and transparent margins; retain all real support exclusions with clearance. Check exact source map flags and connectivity as supporting navigation evidence only, never as elevation. Check currently drawn replacements (including other trees/shrubs/grass) and draw order, not just source placeholders. Bind final frame/atlas resources and owner identities. Existing approved hall support/upper mask is disjoint inside the current sample, but that does not certify all outside ground.

Prefer two bounded added receiver patches or a specifically verified disconnected union rather than one large rectangle spanning the empty gap. Changing camera position must not alter physical eligibility; offscreen raster clipping is presentation only, and is distinct from truncating an unverified shadow to pass a gate. Any missing source/body/registration, wrong instance, incomplete six-owner identity, unverified patch, or full envelope crossing its validated domain disables that whole new cast.

## Smallest technical path after receiver approval

Do not set density to4, resample the raw, alter body scale, or pad merely to force an integer logical frame. The actual logical size is (258.2222222,300.6666667); the raw pixel region is the exact integer Rect2i(0,0,1162,1353).

An isolated raw-region descriptor API is smaller and less ambiguous than changing the frozen integer-density helper: accept raw Rect2i and finite positive float density, plus logical root/transform/blur. Build raw projection using root_raw = logical_root ×density, raw blur=logical blur×density, and raw body transform=logical body transform×scale(1/density). Validate raw-region integer bounds directly. Do not round density or infer logical region from an integer Rect2i. For this bounded trial, allow exactly4.5 (and existing4 only if equivalence-tested); keep existing four helper call sites unchanged.

The current max shader already operates in raw pixel coordinates, so its sampling mathematics needs no special4.5 branch. More casters require a separate reviewed six-slot variant: preserve the original four slots byte-for-byte in semantics and append two independent sampler/descriptor slots. Each slot applies its own inverse transform, raw projection, normalized9tap blur and opacity; then take max across all six and blend the common tint once. Do not add a second overlapping max-composite draw, which would reintroduce alpha stacking. New slot failure must not disable the original four; common compositor shader/tint failure must close the shared pass. Six samplers mean up to54 taps/covered fragment before early rejection, so profile the bounded viewport before any promotion; this is not a timing claim.

Required later diagnostics: density4 existing-slot parity, exact4.5 root pinning and alpha envelope containment, six-slot singleton equivalence, permutation/idempotence, camera movement, all source toggles, independent resource failures, and overlap crossover appearance. No GPU or implementation is authorized by this document.

## Reproduction and evidence

Run `python art_source/earth_upright_shadow_study_v1/measure.py`, then `python art_source/earth_upright_shadow_study_v1/inventory.py` from the Project root. Outputs stay in diagnostics/earth-upright-shadow-study. Frozen measurement snapshot and input hashes: art_source/earth_upright_shadow_study_v1/measurements.json. Diagnostic mask diagrams: left_50_41-envelope.png and bottom_61_51-envelope.png. Blue is full envelope, black is current sample boundary, red is current forbidden material, orange is fixed wood root. Diagrams are CPU technical masks, not body art or native visual proof.
