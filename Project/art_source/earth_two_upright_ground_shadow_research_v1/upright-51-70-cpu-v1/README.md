# Upright 51,70 local ground-only CPU candidate

Status: parent-authorized CPU construction; semantic boundary review and single native pilot pending. No production files, hero v3 parameters, old receivers, or old caster gates modified. No Godot execution. This is not a new caster implementation or runtime-ready gate.

## Read first
- SEMANTIC_SUPPORT.png: actual source scene with nominal blue, root-error amber, pool exclusion red, fixed root white. Original checker shadows remain in this source-reference board. This is NOT the new shadow or the modern rendered scene.
- SOURCE_FLOOR_FRAMES.png: all six actual complete floor frames meeting the envelope bounding box, with precise nonzero support counts. Grass/soil transition texture, no visible tree silhouette/checker shadow in these six frames. Their opaque alpha alone does not establish global terrain planarity.
- CPU_RESULT.json, CPU_ALPHA_EDGE_RESULT.json, CPU_GATE_RESULT.json: measured construction and rejection checks.
- SOURCE_ENUMERATION.json: actual floor identities and affected foreground objects.

## Local geometry and mask
The registered body has 776650 positive-alpha texels, including 142511 alpha1..127 texels. All six owner images reconstruct the shared raw RGBA exactly, without overlap. The sixth owner304 is empty and suppresses the old source cast only while the complete six-owner body group is valid. Raw root(560,1329), density4.5, world root(2484,2254), cast(+1.2,+.55), opacity.25, nine-tap blur.8logical are unchanged from this tree family's design.

All positive-alpha texels contribute bilinear-expanded projected support rectangles, plus the fixed root footprint. Nominal 134420 and root-error 213244 half-logical cells. Root-error expands projected support by(7.2,9.3)logical, the existing conservative +/-2logical raw-root reading plus +/-4logical source anchor uncertainty. Complete geometry verified by independent summed-area rectangle coverage; nothing was trimmed to pass.

Complete error support has actual opaque floor coverage, but 26875 cells meet the conservative pool exclusion; nominal overlap13809. Thus complete-support qualification FAILS. New ground-only candidate explicitly clips to allowed floor186369 cells; it is not a retroactive full-support PASS. The CPU nine-tap sample loses 6.1145% of alpha mass to exclusion. This visible clipping requires parent review.

Pool exclusion uses ALL alpha>0 of actual source Debris55..61, including wall, water, grass apron, and weak edges, with5logical expansion(4 uncertainty+1 filter allowance). No alpha128 shortcut. This is intentionally conservative: some true ground apron is excluded. No pool wall/water reception claimed. The lower pool here is still the original source group; the separately modernized pool at(3086,1800) is outside this patch. Source pool identity changes must invalidate this local candidate.

## Floor mapping and limitations
2553 actual A13 floor entries agree with the inventory count. Receiver construction starts transparent; floor-pass background color is never coverage. The local patch touches28 floor bounding boxes and six frames. The actual root-error support touches only24 grass owners, frames399/406. The three modern C owners409/410/412 and the original398 owner touch the patch bbox but have ZERO actual support hit. Thus this pilot does not demonstrate shadow crossing a modern/source material boundary; it does demonstrate a new receiver independent of old178 region. No-floor and unknown semantics remain excluded; no rest-of-map authorization follows.

Ground pins point to the actual tested res://ground_candidate resource namespace (registration cb5dd2ea3aa288e2f37faa058c11b0da1ad8fc9ce7137e16a42f55aced142e80; freeze0d914454a7d64078a317fc0c47ba4ea9c6de59caf92853c4ee7a3b2830e7121b). These names are not yet the final production placement. Relocation requires an explicit new pin closure, including the ground candidate's current transitive source references. CPU gate resolves them to the tested owned tree; no Godot resource loader is pointed at absolute research paths. A future controller must provide verified floor-mode/generation and revoke state; no fake generation interface is presumed here.

Original foreground Npc837(throne), grass246/247 and bamboo intersect the cast. The common max compositor prevents doubled GENERATED shadow opacity; it cannot remove checker shadow baked into original object RGB/alpha. Retain exact object order and judge this mixing in the single native scene. No claim of physical light recovery, full-map planarity or foreground/water leak-free native rendering yet.

## CPU checks and next approval
cpu_gate.py verifies the pinned input closure, exact receiver equation, empty304, and deliberate missing304/missingmask/missingground-registration rejection plus restore. It is only a CPU artifact validator, not a Godot live guard. sample_edges.py checks the unchanged nine-tap body alpha mirror, zero clipped sample in pool/exclusion, and +/-0.5logical mask lookup cannot reach original pool alpha. Native linear filtering/fractional-camera and foreground edges still require GPU evidence.

After semantic approval: freeze one independent actual compositor/guard/controller adapter closure, prove old5+idle/hero v3 equality, one spur on/off frame, gray/half-pixel local edge, hero occlusion and dependency removal/restoration. No five-tree or24-group visual matrix; no performance exercise. Parent owns approval and publication.
