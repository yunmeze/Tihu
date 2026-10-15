# Single alpha-projected ground shadow: isolated R5 technical pilot

`hero_alpha_ground_shadow.gd` is a generic `Node2D` with one shader quad. It does
not load art, know an actor origin, draw a body, edit RGBA, or replace the default
renderer. The raw image-generated source and registered body atlas are immutable.
No procedural character is created. The shader reads only existing body alpha.

## Calling contract

Create one node for one actor, and call:

```
configure_frame(body_atlas: Texture2D, region: Rect2i,
    body_to_parent: Transform2D, sole_a: Vector2, sole_b: Vector2,
    cast_per_height: Vector2, opacity = 0.30, blur_px = 0.9,
    tint = Color(0.035, 0.045, 0.055)) -> bool
```

- Supply the underlying body-only atlas, not an `AtlasTexture`. Region and all
  anchors use local image pixels, with y increasing downwards.
- `body_to_parent` is the exact replacement-body frame-to-parent transform.
  There is no automatic recentering, rescaling, y-offset, foot adjustment or pose
  correction. Use `set_body_transform()` for camera/actor translation afterward.
- `clear_frame()` disables the shadow. Invalid configuration also clears it.
- `configuration()` reports the effective projection, bounds, opacity, blur and
  transform; `last_error` explains validation failures.
- Opacity is capped at 0.42 in both helper and shader. Blur is 0..3 local projected
  pixels, default 0.9. One normalized 3x3 kernel is composited once. Do not add a
  separate contact ellipse, source checker, or second cast pass.
- Tint is clamped to [0,1]. Coordinates must be finite; texture region is checked;
  frames are limited to 2048 px, contact slope magnitude to 2, cast-vector length
  to 2, determinant magnitude to at least 0.025, and shadow extent to 8192 px.
- The sampler rejects every out-of-region tap before clamping in-region samples
  to texel centers. Explicit texture LOD 0 avoids atlas mipmap contamination.

The render owner must put floors before this node and original objects afterward.
Then the replacement body participates in the normal object/actor depth ordering.
A shader material applies to an entire CanvasItem; do not apply this material to
the CanvasItem that draws floors, objects or bodies. Split passes or insert a
dedicated CanvasItem at the appropriate draw index.

Choose the body and shadow together for the same immutable frame ID. On failure,
disable this shadow before falling back to the complete original body/head set.
Never display original checker-bearing body plus this shadow. The helper cannot
enforce the caller's draw order or prevent someone creating a duplicate node.

## Projection

Given the two planted-sole proxies A and B, let `g(x) = m*x+b` be their line. For
image pixel p=(x,y), `h = g(x)-y` and `q = (x,g(x)) + h*cast`. The helper constructs
this affine transform and passes its inverse to the shader. Every point on the
contact line stays fixed, including the high-screen planted foot. Different
screen y values of two planted feet therefore do not imply a raised leg.

This is a flat-ground 2D approximation. It does not reconstruct a 3D body, light,
receiver geometry, limb depth or physical joints. Small outsole pixels below the
proxy line remain part of the same affine mapping; there is no hidden body mask
or art deformation. Rotating/scaling `body_to_parent` also rotates/scales the
shadow and blur, so world-light direction after arbitrary body rotation is not
claimed by this pilot.

## R5 SE idle 13–16 measured parameters

Source evidence is `art_source/hero_se_idle_rebuild_v1/source-13.png` and the
source13 measurement grid. The visible source checker extends right/up. In its
exposed ROI x=56..89, y=50..87, the highest checker sample is (77,57). Source crown
surface proxy (40,15) and source sole proxies (36,86)/(52,81) give g(40)=84.75 and
h=69.75. Matching that endpoint gives cast=(37/69.75,-27.75/69.75), approximately
(+0.530466,-0.397849). The direction is observed; exact crown/end correspondence
and magnitude remain a visual estimate, not a calibrated physical light.

New-body atlas: `v1-registered-atlas-128.png`, 512×128, four 128×128 frames. Its
SHA256 is `91e7fb445775116ae2894900b76811757eda3898e78bf1e6881e38f933670ac9`.
The runtime owner must supply an importable production/pilot path explicitly;
the helper has no dependency on ignored `art_source` or diagnostic assets.

The original draw origin in each cell is (16,64). For native scale1,
body_to_parent origin is `actor_draw_origin - Vector2(16,64)`. The logical actor
draw origin is not a foot contact.

Candidate visible lower-outsole proxies, from alpha>=96 lower-edge pixels:

| Source ID | Atlas region | Near/left sole A | Far/right sole B |
| --- | --- | --- | --- |
| 13 | (0,0,128,128) | (36,89) | (52,81) |
| 14 | (128,0,128,128) | (36.5,89) | (51.5,81) |
| 15 | (256,0,128,128) | (36.5,89) | (51.5,81) |
| 16 | (384,0,128,128) | (36,89) | (52.5,81) |

These proxies have ±1 px uncertainty. Alpha96 is only a measurement threshold;
the shader uses full continuous alpha and never thresholds/re-encodes the body.
These are lower visible outsole edges, distinct from registration-file boot-tip
surface landmarks. Neither set is a proven physical contact point or ankle.
The already-observed frame15 nod and foot projection residual remain unchanged.

## Tests and remaining acceptance

Run from the project directory with a writable temporary user-data directory:

```
HOME=/tmp/tihu-shadow-test-home XDG_CACHE_HOME=/tmp/tihu-shadow-test-cache \
XDG_DATA_HOME=/tmp/tihu-shadow-test-data \
godot --headless --path . --script tests/test_hero_alpha_ground_shadow.gd
python tests/test_hero_alpha_ground_shadow_source.py
```

Headless checks cover both planted soles, contact-line invariance, affine inverse
round trips, projection bounds, all four atlas regions, no-neighbor sampling
coordinates, normalized blur, opacity limits, invalid-input fail-closed behavior,
and shader-resource loading. The read-only source test verifies raw/body/source
hashes, source shadow direction, native outsole proxies and atlas/frame identity.
They do not prove native GPU rendering, visual softness, lighting match or depth.

Native acceptance belongs to the runtime/GUI owner: same-phase shadow off/on
comparison at real flat-ground map positions, original object in front and behind
the actor, uninterrupted 13–16 loop, alpha/region edge inspection, and confirmation
that the source checker is absent only because the entire source body was replaced.
No platform, bridge, stair, elevation or occlusion-receiver claim is made. Keep the
pilot separate from the normal entry until parent review accepts the result.
