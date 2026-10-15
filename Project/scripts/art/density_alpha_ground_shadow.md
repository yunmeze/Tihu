# Density-aware single alpha ground shadow

This separate helper supports the HD hero texture-density change without altering
HeroAlphaGroundShadow, its shader, constants, existing hero/tree parameters or
historical entry points. It remains one bounded2D fixed-receiver approximation.
It does not infer support feet, physical height, terrain, stairs or platforms.

## Public contract

```
configure_density_ground_frame(body_atlas: Texture2D,
    logical_region: Rect2i, texture_density: float,
    logical_body_to_parent: Transform2D,
    logical_ground_reference: Vector2, ground_slope: float,
    cast_per_height: Vector2, opacity = 0.30,
    logical_blur_px = 0.9,
    tint = Color(0.035, 0.045, 0.055)) -> bool
set_logical_body_transform(logical_body_to_parent: Transform2D) -> bool
configuration() -> Dictionary
clear_frame()
```

Use `res://scripts/art/density_alpha_ground_shadow.gd` and its independent
`res://shaders/density_alpha_ground_shadow.gdshader`. The explicit input texture
is the complete raw-density atlas. The helper never loads body/source paths.

All caller positions, dimensions and blur are in density-one logical image
pixels. The supplied density must be an exact integer1..4. The logical region
includes its atlas position, not just its frame dimensions. Keep every phase's
receiver fixed. These conversions happen inside the helper exactly once:

- raw region position and size = logical region position and size times density
- raw receiver reference = logical reference times density
- raw body transform basis = logical basis divided by density
- raw body transform origin = logical origin, unchanged
- slope and cast vector = unchanged, dimensionless
- raw blur radius = clamped logical blur times density
- raw quad padding = (clamped logical blur +1 logical pixel) times density

Do not pre-scale the arguments. Camera/actor updates likewise use the logical
transform through set_logical_body_transform. The global HD canvas transform is
a separate outer transform, applied equally to body, shadow, floors and objects.

For the approved SE fixed receiver and a4x atlas, a logical frame remains128x128,
its phase position is phase_index*128, reference remains(40,86), slope0 and cast
(148/279,-111/279). The body origin is unchanged: actor origin minus(16,64).
With logical blur0.9, the shader receives raw radius3.6 and the quad grows7.6raw
pixels, equivalent to1.9logical pixels. A later2x screen/canvas transform changes
both body and shadow consistently; it does not turn texture density4 into8.

## Projection and sampling

The affine projection is the legacy fixed-receiver formula. If P is the logical
projection and Pd its raw-density counterpart, then Pd(d*p)/d=P(p). Receiver-line
points remain fixed under this normalization. The raw transform then maps the
result to exactly the same parent-space geometry.

The shader uses only alpha, one normalized3x3 blur kernel and one capped opacity
pass. It rejects inverse-projected points outside the explicit raw atlas region,
then clamps the bilinear footprint between that region's texel centers and uses
LOD0. No adjacent frame or mipmap may bleed into this cast. RGB is never classified
or deleted. The density-aware shader's only computational-resource declaration
change from the old shader is the blur editor range0..12; its projection/sampling,
weights and final opacity expression are otherwise identical.

Geometry, receiver contact, blur spacing and padded support are density-invariant.
A newly sampled high-resolution alpha image need not produce the same rendered
pixels as the old low-resolution atlas. The half-texel boundary guard is in actual
raw texels, as required for safe filtering. Do not claim photometric or GPU pixel
identity across different body art rasters from the math regression.

## Bounds, failures and compositing

Logical blur is explicitly clamped to0..3, matching the old logical-domain cap;
configuration records requested logical blur, actual logical blur and raw blur.
At density4, maximum raw radius is12, never silently clamped to the legacy raw3.
Opacity is capped at0.42 in both helper and shader. Raw frames must be1..2048
texels on each axis, projected-frame extent before padding is bounded by8192raw
texels, and density is1..4. Slope, cast and logical transform validity use the
legacy finite/invertible bounded domain. A valid raw transform can have a smaller
determinant after division by density; validation is intentionally in logical units.

The reference must be inside the logical frame with a one-logical-pixel edge
allowance. The atlas must be loaded and cannot be a nested AtlasTexture. Invalid
configuration or invalid movement clears the shadow and its saved state. The
caller must switch the high-density body and shadow atomically, or restore its
complete source fallback. This helper draws no body and cannot enforce source
suppression by itself.

Order remains floors, then one whole-character shadow, then all normally sorted
objects and body. Never overlay this with source body/checker or stack one cast per
cutout. No platform/stair/compound-building receiver claim follows from this API.

## Validation and acceptance gate

Headless tests:57,430 checks, zero failures. They cover density1..4, six atlas
regions, three slopes, normalized projection/contact/quad/parent-space positions,
explicit guard edges, density1 exact legacy configuration and shader uniforms,
logical movement,3.6raw default blur,12raw capped blur, malformed input, invalid
regions/overflow, nonfinite values, nested atlases and cleared failure state.

Existing suites were rerun unchanged: original idle3007, fixed receiver4917, tree
8751 checks all pass. The old helper SHA remains
3eeebe50bfdd235fee24b30bfbdaaad5517a5254bd7e318b73abc80adb5ccdd2,
and old shader SHA remains
d8f4894fd16458a3a7aabb5db5af4a95f39320f5e2549c33467f79f5a5089c24.

Reproduce locally with Godot headless and tests/test_density_alpha_ground_shadow.gd.
The test and logs under diagnostics/hero/density-shadow are local regression
evidence, excluded from the production stage. Runtime/GPU review remains with the
sole runtime owner: real HD idle/walk and start/stop, shadow on/off, source/new
atomic replacement, atlas-phase boundaries and object front/back depth. No GUI
or default-runtime changes were performed for this helper package.
