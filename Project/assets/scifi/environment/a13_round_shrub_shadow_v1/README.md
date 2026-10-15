# First-screen shrub cast candidate

One complete raw-alpha projection per selected shrub; native acceptance pending.
The PNG is byte-identical to the parent-approved1363x1154 generated raw. Its RGB
and alpha, including faint fringes and white points, are untouched. Four original
body owners keep their depth ordering. They do not receive four separate casts.

## Visible leaf proxy, not root

The physical root is hidden and remains null. At alpha>=96 the last visible row is
1102, pixels x777..778; the measured lower texel edge is(778,1103). This maps to
source-composite-local(69.44287,100). Across alpha thresholds32,64,96,128,192 the
edge y changes at most1raw pixel, about0.0944logical pixel. Thresholds are only
measurements; the shader still uses every raw alpha value. Reference x does not
change the chosen horizontal receiver line.

The source contract proves only13 exposed right checker points and62 lower points,
not a complete separated shadow. Similar dark RGB also appears inside foliage.
There is no global color deletion or source-checker mask. The shared field cast is
(148/279,-111/279), the same measured direction used by hero/tree, rather than a
new direction fitted to this small ambiguous halo.

The first candidate uses opacity0.30, raw blur3 and tint(.035,.045,.055). Raw blur3
is only0.283286logical pixels at this shrub scale, so softness needs actualHD review.
The projected alpha>=96 center bounds are approximately source-local
(21.429,60.234)..(151.390,99.981); the right edge can extend31pixels beyond the
new foliage envelope. This is not reconstruction of the original tiny exposed
checker. A round bush has depth; the one-line cast is a bounded2D approximation.

## Exact transform and draw contract

Use the existing HeroAlphaGroundShadow.configure_ground_frame with the full raw
region, raw reference(778,1103), slope0, shared cast, opacity0.30 and blur3. Put
that helper under a dedicated raw-space Node2D parent. Its own body_to_parent is
Transform2D.IDENTITY. The raw-space parent's basis is the uniform approved scale
0.09442870632672333 and its position is the instance's whole_raw_world_origin plus
logical camera offset. The composition is exactly the raw body mapping. This
coordinate hierarchy does not change any frozen helper validation constants.
Apply the globalHD canvas transform outside this hierarchy, just as for bodies.

All four first-screen instances are enumerated, but pilot(57,38) comes first.
Other groups(51,44),(58,51),(64,45) are candidates only after their body/depth review.
Each selected group draws one cast after all floors and before every object/actor.
Its four original source owners, including checker, must be suppressed together
with full replacement-body activation. On missing texture/config, disable the
cast and restore the entire four-source group. Shared-resource failure applies to
all affected groups. An intentional same-phase shadow-off A/B is a separate mode.

The entire raw texture has a normal runtime path in this directory, independent
of ignored diagnostics. Source and registration hashes, source ROI records,
threshold measurements, world proxies, owner keys/sorting and explicit units are
in shadow.json. Rebuild using
art_source/a13_round_shrub_candidate_v1/build_shadow_candidate.py. Native on/off,
root-area appearance, actor front/back and first-screen clipping remain required.
No stairs/platform receivers or3D tree/foliage lighting are claimed.

## Conservative B: lower-foliage band

Parent review flagged the full-crown A projection's31pixel right extension as a
risk. Keep A for comparison. B uses the identical whole texture, receiver and cast,
but attenuates only shadow samples with smoothstep(900,964,p.y). It completely
excludes the upper crown from casting and smoothly introduces the lower foliage
band, avoiding a hard crop boundary. Body pixels are not changed. Parameters and
shared-instance rules are in contact-band.json; the small separate helper/shader
are foliage_band_ground_shadow.gd/.gdshader. They do not modify the frozen helpers.

Before fade attenuation, the projected alpha96 band bounds are source-local
(24.257,92.392)..(116.976,99.981), inside the crown envelope; its largest positive
proxy-height is about19.17logical pixels. That reduces maximum rightward shift to
about10.17logical pixels. These are design support bounds, not physical height.
The6.04logical-pixel smooth fade can make an already hidden contact cast subtle.
The sole runtime owner must show A/B in the same actualHD scene and select one.
Never draw A and B together. No claim of a complete original building/plant shadow
reconstruction follows from this contact-shadow design.
