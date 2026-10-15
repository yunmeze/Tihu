# A13 complete NPC source review

The reviewer inspected every group's complete original four phases and nearest-neighbor 6× enlarged board, plus key NPC 3-direction × 4-phase family boards, key lower-detail boards and original-pixel coordinate grids. Observations below are source evidence, not new character design. Native numeric direction slots are retained; they are not mapped onto the hero's eight directions.

## All 11 original map records

Order is the original NPC-list order. `unique` counts exact registered RGBA phases, not semantic poses. Offsets are `(x,y)` from the original map-cell draw origin.

| Record/name | Cell | appearance / slot | Actual source phases | unique | Offsets, phase order |
|---|---|---|---|---:|---|
| 0 方丈 | 64,37 | 21 / 2 | 261–264 | 1 | (-6,-40) ×4 |
| 1 凌云子 | 62,36 | 9 / 1 | 113–116 | 4 | (9,-51), (9,-49), (9,-49), (9,-50) |
| 2 老药师 | 20,26 | 2 / 2 | 33–36 | 4 | (1,-42), (1,-41), (1,-41), (0,-42) |
| 3 道童 | 76,37 | 24 / 1 | 293–296 | 4 | (3,-20) ×4 |
| 4 张天师 | 35,34 | 16 / 2 | 201–204 | 4 | (-1,-44), (0,-44), (-1,-44), (-1,-44) |
| 5 虚云道人 | 29,42 | 19 / 2 | 237–240 | 1 | (-1,-23) ×4 |
| 6 廖毅 | 38,37 | 22 / 2 | 273–276 | 4 | (-11,-44), (-11,-44), (-12,-44), (-12,-44) |
| 7 一弘道长 | 64,63 | 15 / 2 | 189–192 | 4 | (-5,-43), (-5,-43), (-5,-44), (-5,-43) |
| 8 混元之气 | 78,23 | 72 / 0 | 865–868 | 4 | (-25,-65) ×4 |
| 9 一阳道长 | 55,72 | 69 / 2 | 837–840 | 1 | (-20,-90) ×4 |
| 10 终极试炼 | 61,70 | 72 / 0 | 865–868 | 4 | (-25,-65) ×4 |

11 placements share 10 source groups / 40 source indices / 31 distinct registered source RGBA canvases. 混元之气 and 终极试炼 are exactly the same source family and direction, at different map placements with different scripts. Art identity sharing does not merge those game records or functions.

Every examined appearance has 12 stored records, three slots × four phases. Appearance21 and19 are static within each direction but the three directions differ. Appearance69 is identical across all twelve records, including offsets. No exact raw-RGBA horizontal mirror pair was found across direction slots in these ten families. This narrow raster test does not establish anatomical equivalence or authorize mirroring; the current/reference NPC draw path does not flip images.

## 方丈: static source, 261–264

- All four native 64 × 69 RGBA canvases and offsets `(-6,-40)` are identical. Native root-in-image is `(6,40)`, visibly far from a central sole contact.
- Visible: dark head top, white horizontal headband; beige upper torso and exposed arms; dark forearm/wrist areas; light belt and yellow-brown trousers; dark boots. One arm reaches toward screen-left while the other bends across the waist; knees are bent and depth is asymmetric.
- The name does not justify inventing a bald monk, long robe, staff, beads, armor or another standing pose. Dark head top could contain hair/headwear; its detailed construction is unresolved at source resolution.
- No separate long wooden staff is visible in these four frames. The dark horizontal mass around the waist includes the bent forearm/hand and clothing overlap. Keep the observed overlap; do not turn it into a weapon or remove it as shadow.
- Baked checker cast lies chiefly screen-right and touches both lower-leg/boot regions. Approximate visible boot-edge review regions in raw261 are `[14,49,25,57]` and `[29,59,40,67]`, with about 2–3 source pixels of boundary uncertainty. These are diagnostic review regions, not solved heel/toe contacts, a ground line, or a body mask. Some dark boot and checker pixels are contiguous.
- One new static pose can be shared by indices261–264. The original 17-tick slot progression stays intact; no invented breathing or jitter.

## 凌云子: four registered phases, 113–116

- Offset/root differences are real. Raw roots are `(-9,51), (-9,49), (-9,49), (-9,50)`; the root is outside the source image to its left. This alone disproves treating the raw image origin or alpha bottom as an anatomical foot anchor.
- Visible: frontal tall tan/gold head-attached vertical form, small face, gray wide sleeves, dark folds, purple lower-front robe/panels, light pink/tan hanging detail near overlapping hands, and two tan boots.
- The tall form rises from the head in all reviewed directions. Keep it as the observed tall headwear silhouette; it is not a freestanding wooden staff to be extended down to the ground. Exact hat construction and decorative material remain uncertain.
- Four phases show small changes in headwear/upper-body height, sleeve/hand fold pixels, lower clothing and checker cast. Hat top is higher in113 and lower in114/115, returning partway in116 under the native registration. Do not substitute independent full-body poses or top-align the four crops.
- The thin central hanging detail and overlapping hands are visible, but its object category, finger count, rear-hand contour and attachment are unresolved. Do not add a staff, sword, electronic tool or extra hand to explain it.
- Both tan boots remain visible. In raw113, lower-boot review regions are approximately `[4,64,11,72]` and `[19,64,26,72]`; checker lies between and screen-right. Their lowest visible edges do not identify a unique three-dimensional ground contact. The other three frames must be inspected using their own source coordinates/offsets rather than copied raw113 landmarks.
- Registered pairwise changed-visible-pixel counts are 1030,1130,965,876,526,963 for113/114,113/115,113/116,114/115,114/116,115/116. These include shadow changes and cannot be described as equivalent counts of body motion.

## Remaining source identities and uncertainties

- **老药师:** hatted, slightly inclined torso, a raised arm near the face, bright sleeves, brown center garment, dark lower legs and pale shoes. Four low-amplitude source variations. Small hand/face/held-item distinctions are unresolved; the name alone does not establish medicine props.
- **道童:** compact seated/front-facing silhouette with dark/gold clothing, a brown diagonal rod-like element across the lap, and pale lower-foot/cloth area. All four phases differ subtly around the upper body/lap/rod. Rod is visible, but precise wood/staff/weapon category and supporting seat are not resolved; do not make this into a standing adult/child solely from the name.
- **张天师:** tall dark robe, gold collar, high dark cap, raised screen-left arm/hand with a thin brown horizontal element near the head. Small variations in arm/cloth and cast. Exact held-object type and hidden hand anatomy are unresolved. Long hem partly hides feet; do not use its shadow bottom as a sole.
- **虚云道人:** identical seated/crossed-leg light blue/white figure across237–240, hand near the face and large folded cloth/lap area. Bent legs and garment obscure true support points. No new standing legs or idle motion.
- **廖毅:** white tall hat, dark/gold long garment, extended arm holding a small red hanging object. Four subtle arm/object/hem changes with real x-offset changes. Preserve the red object silhouette, but bottle/pouch/lantern identity and rear hand remain unresolved. Hem hides one foot; white visible shoe/boot fragments do not establish both ground contacts.
- **一弘道长:** green/dark/gold long outfit, swept-back dark head ornament/hair, one forward arm and a thin light horizontal object, a vertical brown accessory at the side. Four phases vary hand/object/cloth and shadow. Exact weapon type and hidden hand are unresolved. Preserve narrow visible solid props and separate them from the thin projected checker branches.
- **混元之气 / 终极试炼:** shared standing humanoid with dark upper clothing, brown head/hair area, bright blue/white lower legs, long tan diagonal pole-shaped object crossing the body. Four subtle source phases. These names do **not** mean the raster is a gas cloud or orb. The pole is solid source geometry; exact weapon classification and which hidden fingers hold it remain unresolved. Pole/feet/shadow overlap near the bottom requires separate contact review.
- **一阳道长:** identical seated figure plus a large brown carved chair and stepped base, ornate yellow/blue robe and broad headwear, across all12 appearance69 records. The complete chair is part of the NPC sprite. Feet are hidden by robe/chair; chair base is visible support evidence, not a pair of inferred foot contacts. Do not cut it away or turn this into a standing figure.

## Timing and scope

Current/reference cadence is 50 source ticks/second, 17ticks/phase = 0.34seconds; loop0,1,2,3 lasts68ticks = 1.36seconds. Tick windows are0–16,17–33,34–50,51–67. All current NPCs share the global phase clock. The reference inspection script records native constant0x11, but this task did not run the EXE or independently verify original lifecycle/initialization. Keep that confidence boundary.

All names, scripts, cells, visibility rules, ordering and interaction roles are unchanged. Source data and source art can disagree with a modern expectation of a name; preserve the source evidence and do not rewrite the story to make an invented outfit fit.
