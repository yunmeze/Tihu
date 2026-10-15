# Exact S-only diagnostic map contract

This is a detached experimental shadow map, not a change to body imagery or character layers. Current ordinary E/SE and every nonhero caster stay untouched. The current compositor has changed since the earlier CPU study; bind current files listed by interface.json, and replace only its hero contribution in the independent diagnostic. Do not restore the older four-caster compositor.

## Units and constants

p=(x,y): logical coordinate inside128×128 body frame. q: logical projected-ground coordinate relative to the exact same frame origin. World body-frame origin is actor_cell*(48,32)+(-16,-64); retain camera translation independently. Density4 only converts these coordinates to texture units.

b0=85.3125; d=2.0625; y0=60; y1=80; L=20; tL=−39.46875; tR=−35.46875.
cast=(1.2,.55); v=(1.2,1.55). tint=(.035,.045,.055); opacity=.25.

b0 is the pooled mean of8 previously read S sole y values; b0−d=83.25 is left mean, b0+d=87.375 right mean. Start y60 comes from the all-four-phase all-alpha transparent leg gap. End y80=floor(min sole y82.75)−2. t endpoints come from all-alpha lower source support including its bilinear footprint. See the frozen preimplementation plan; none was fitted after viewing the resulting shadow.

## Forward map

1. t=1.55x−1.2y.
2. f(t)=−d if t<=tL; f(t)=−d+(2d)(t−tL)/(tR−tL) if tL<t<tR; f(t)=+d if t>=tR.
3. w(y)=0 if y<=60; w(y)=(y−60)/20 if60<y<80; w(y)=1 if y>=80.
4. b=b0+w(y)f(t); h=b−y.
5. q=(x+1.2h,y+1.55h).

Negative h is not clamped. All body alpha is retained. This is an artistic2D shadow sampling construction, not recovered physical heights or a3D model.

## Exact inverse, applied separately to every blur tap

Given q=(qx,qy):
1. t=1.55qx−1.2qy. This equals source t exactly in real arithmetic.
2. Compute f=f(t) using the same three intervals above.
3. Q0=1.55b0−.55*60=99.234375.
4. Q1(f)=1.55(b0+f)−.55*80=88.234375+1.55f.
5. Choose y:
   - qy>=Q0: y=(132.234375−qy)/.55.
   - Q1<qy<Q0: y=(qy−132.234375+4.65f)/(−.55+.0775f).
   - qy<=Q1: y=(132.234375+1.55f−qy)/.55.
6. x=(t+1.2y)/1.55.

At equality both adjacent formulas agree; use the stated comparisons consistently. Since Q1<Q0 for every allowed f, intervals do not overlap or leave a gap. Denominator in the middle is strictly[−.70984375,−.39015625]. No iterative solver, nearest inverse selection or determinant clamping is allowed.

q and b are continuous at every piece boundary; derivatives may jump. det(J)=−.55+1.55*w'(y)*f(t), negative with margin.39015625. Invariant t plus strict monotonic qy(y) establishes global one-to-one mapping, including the central contact transition. This does not bound local shear: high anisotropy remains a visual risk.

## Original9tap kernel: exact coordinate space

For each final ground pixel q, evaluate the9 taps at:
q_ij=q+(.8*i,.8*j), i,j∈{−1,0,1}.

These offsets are **projected-ground logical axes, before inverse mapping**. They are not source sprite offsets, UV offsets, or post-inverse blur. In a density4 projected varying, equivalent offsets are(3.2*i,3.2*j), then divide the complete ground tap by4 before this logical inverse. Do not divide or multiply world translations by4.

For each q_ij, inverse to p_ij. Convert p_raw=4p. Reject if either raw coordinate lies outside[0,512) before clamping. Clamp valid raw positions to[.5,511.5], then add raw atlas frame origin(512*(source_id−17),0); divide by full2048×512 texture dimensions. Sample original RGBA alpha with bilinear filtering at LOD0. Never sample a neighboring phase or alter source alpha.

Weights are rows[1,2,1],[2,4,2],[1,2,1], normalized by16. At each tap, form one coverage from exact source ownership. Then sum weighted coverage/16, multiply opacity.25 exactly once. Finally max this finished hero contribution against every current independently gated other caster. Do not max separately blurred anatomical pieces or add a contact-opacity pass.

Ownership: left iff y>=60 and t<=tL; right iff y>=60 and t>=tR; otherwise body/remainder. All owners restrict the same continuous original bilinear alpha function. A globally unique inverse means exactly one nonzero owner per valid tap; ownership can be an assertion rather than3 texture reads. Do not filter three cropped/masked atlases separately.

## Complete envelope and qualification

Use only the new diagnostic mask at diagnostics/earth-s-idle-contact-projection-cpu-v1/full-four-phase-envelope.png, SHA a731de3104eccc3e35aa50b2a2cce5ac994b781cee19ea3e027fd3b57a0a9047.

Offset(26.5,79),size104×48logical,d2 raster208×96,6901setcells. Its support comes from interval bounds of every alpha>0 raw texel plus fulltexel/.125bilinear support,1.8logical expansion and fixed proxy read-error boxes, across all4 phases. Interval bounding is conservative and includes nonlinear interior extrema by enclosure; it is not only a corner fit. Old S4575/SE envelopes are invalid for this map.

Only unchanged existing se_flat_v1 allowed-domain semantics are reused with exact hashes. Whole translated new envelope must fit in that domain. Test every floor/ceil-overlapped destination area at fractional positions. Any forbidden/outside/unknown/platform position clears the entire experimental hero shadow. This admits171 integer placements; previous S candidate's175 are not inherited. Newly rejected positions include61,33;62,35;62,37;65,37.

## High-shear closeup target

Affected opaque source alpha is the **screen-left lower shin/boot shaft**, not the torso: union source localx31.625..36.875,y70.625..79.125; rawd4 y rows282..316. Most affected texels are in logical source rows73..77. Per phase counts are235,231,233,234 (~1.14–1.15% opaque source texels).

Mapped shadow union is localx41.058..50.467,y85.850..94.867, just between/beyond the feet toward the first right-down shadow branch. It contains the highest localized shear (opaque anisotropy49.18..53.18), so inspect both the very near-contact branch and its transition into the main silhouette. At actor61,39, add body-frame world origin(2912,1184): approximatelyworld[2953.06,1269.85,2962.47,1278.87]. Include blur and context outside this box in captures.

Detailed per-phase rows and bounds are in interface.json / diagnostics/earth-s-idle-contact-projection-interface-v1/high-shear-locations.json. The annotation colors original source centers orange and their projected locations magenta; it is a technical annotation, not altered character art.

## Finite-cost and failure contract

One hero pixel can remain9alpha reads, with added invariant, piecewise scalar inverse and clamps for each tap. Current CPU sampling does not establish GPU timings. A verified tight208×96d2 output box would need about179,712 texture reads/frame or182,457 with one extra destination cell peraxis. No assertion that the existing generic raw-frame bound is already this tight.

Fail closed on missing/changed bound inputs, invalid frame/group/action/direction, unknown or nonfinite coordinates, parameter mismatch, inverse outside source frame, incomplete envelope or forbidden overlap. Failed support does not permit clipping, changing feet, widening the receiver, changing body or dropping low-alpha pixels.

Native parity must verify the tap space and phase region before visual judgment. Check S18 left sole's retained .9801logical proxy displacement, near-contact shear, two12tick loops, switches from unchanged ordinary SE through S/E/S back to SE, and all current nonhero overlap/preferences. This interface does not authorize ordinary promotion.
