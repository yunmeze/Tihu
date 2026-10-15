# First A13 tree: one reusable alpha-projected cast

Status: bounded first-instance working candidate. Native root/on-off/three-depth
review and complete-source failure fallback checks passed.
No new artwork is generated. The tree raw RGBA, uniform scale, root registration,
seven body-owner partitions, hero helper and shader are unchanged.

## Runtime closure and call

The ordinary runtime sibling directory is
`assets/scifi/environment/a13_first_tree_shadow_v1/`:

- `whole_tree.png`: byte-identical copy of the complete 1254×1254 generated raw.
  SHA256 `057572f4e5f7f5d48b30a4aa28d30f28842006f5b169887d6415316765569554`.
- `shadow.json`: explicit parameters, provenance, observed source ROIs, bounds,
  suppression requirements and failure behavior.

Import `whole_tree.png` normally and load it as a `Texture2D`. Do not load a raw
image from an ignored research path in production. RGB remains untouched, but the
shader samples alpha only. There is no alpha extraction, painting, color removal,
thresholding, resizing or re-encoding of this runtime copy.

Reuse `HeroAlphaGroundShadow.configure_ground_frame()` with:

```
region = Rect2i(0, 0, 1254, 1254)
ground_reference = Vector2(498, 1224)
ground_slope = 0.0
cast_per_height = Vector2(148.0 / 279, -111.0 / 279)
opacity = 0.30
blur_radius_px = 3.0
tint = Color(0.035, 0.045, 0.055)
```

The exact existing whole-tree transform has uniform scale
0.2472072097078169, no rotation/shear, and world origin
(2637.890809565507,787.4183753176321). Add the current camera offset to that origin.
It maps raw wood root (498,1224) to world (2761,1090), corresponding to source
composite root (119,300). The projected root remains fixed. Root uncertainty is
±4 source pixels / ±8 raw pixels; it is a visible woody contact-band proxy, not
a surveyed 3D coordinate. Do not substitute the alpha bbox, bottom row, grass tuft
or root-owner cell origin.

Blur is in raw image pixels, so 3 raw pixels become about 0.742 native pixels.
The original helper cap remains 3; no hero behavior is changed. The helper's
single normalized nine-tap kernel and total alpha cap of 0.42 are retained.

## Render and fallback requirements

Draw this complete-tree shadow once after every floor and before every object
and actor. Do not create a shadow per owner slice. Keep the seven replacement
body pieces in their existing source depth order: owner292 at y34, owners293–298
at y37. A separate shadow pass does not flatten those body depths.

All seven original source keys in `shadow.json` must be suppressed together when
the replacement tree is active. Those original pieces contain baked checker
pixels, including the outer shadow-only source298. Retaining any source checker
while enabling this cast would double the tree shadow. There is no global color
deletion rule and no new contact ellipse.

Validate the full seven-owner body set, normally imported whole texture and
successful shadow configuration before selecting this replacement. On failure,
disable this shadow and restore the entire original seven-owner source group.
An explicit same-frame shadow-off diagnostic may retain the new body; that is a
deliberate comparison mode rather than accidental partial fallback.

Only the selected tree at root-owner cell (57,34) is covered. Other instances of
the same original tree family remain unchanged.

## Independent source direction evidence

The source composite is reconstructed from the original seven atlas regions and
their documented world positions, with no color masking. Its decoded RGBA hash is
`4f4cb846e9a8b6e69c84f74ab3c7c0cca51794472e4726fb65db9d69d7741dc8`.

Three visually independent exposed regions contain only checker RGBA(8,0,0,255)
where nontransparent; this differs from the hero source checker color. Coordinates
below are source-composite pixels, with exclusive ROI upper bounds:

| ROI | Nontransparent samples | Inclusive occupied bbox | Pixel-center centroid |
| --- | ---: | --- | --- |
| (278,180)..(312,260) | 378 | (278,197)..(311,245) | (291.788,227.947) |
| (180,250)..(280,300) | 735 | (180,250)..(259,290) | (212.640,261.354) |
| (140,270)..(200,300) | 427 | (140,270)..(189,291) | (165.081,279.350) |

The first centroid is (+172.788,−72.053) from the visible wood root, confirming
right/up source cast exposure. Its angle is not used as an exact lighting fit:
the visible lobes also reflect tree branch width, depth and source occlusion.

For each raw body pixel p=(x,y), the inherited projection is
q=(x,g)+(g−y)·cast, with g=1224. Cast=(+.530466,−.397849) points right/up from
the ground reference. The displacement from the elevated body pixel itself is
q−p=(g−y)·(+.530466,+.602151), normally down/right because it includes descent to
ground. These are different reference vectors, not conflicting light directions.

## Bounded approximation and verification

The whole raw quad projects to less than 500×130 native pixels including padding.
For a measurement-only alpha≥96 contour, projected world support lies approximately
within (2726.554,971.241)..(2982.456,1091.229). Runtime continues to use full alpha,
including faint edge pixels. This envelope is not a new trim or opacity threshold.

The crown occupies multiple depths. A single 2D alpha projection cannot recover
physical canopy lighting, exact original shadow shape, terrain, self-shadowing or
height. Same-scene cast parameters preserve the chosen right/up direction; source
checker evidence does not uniquely establish the magnitude or horizontal plane.
There is no stairs, platform, elevated receiver or general terrain claim.

Local headless tests:

- `tests/test_tree_alpha_ground_shadow.gd`: actual whole texture dimensions,
  registered fixed root, exact normally imported alpha, affine round trips,
  bounded quad, opacity/blur units,
  camera translation, region guards, one-pass declaration and fail-closed input
- `tests/test_tree_alpha_ground_shadow_source.py`: immutable whole RGBA and alpha,
  ordinary-path closure, original composite reconstruction, all three exposed
  ROIs, exact seven-key/body registration agreement and frozen hero helper/shader
- Existing idle 3007-check and fixed-receiver 4917-check suites remain applicable

Native root/on-off and back/mixed-owner/front probes at (57,32), (57,35) and
(59,38) were reviewed in `shared/legend-rebuild-tree/cast-root-detail.jpg` and
`cast-three-points.jpg`. The observed cast is on right/up grass, continuous near
the woody root, with no observed old-tree checker duplication or shadow overlay
on the actor/building facade. This remains a bounded flat-ground visual review.

`shadow-fallback.log` confirms invalid texture disables the shadow and all three
replacement object passes, restoring all seven original source owners. The scene
also asserts floors → one tree-shadow node → all object passes.
`shadow-fallback-uniforms.log` records actual material color(.035,.045,.055,.30),
blur3 raw pixels, and one compositing pass. Screenshot difference maxima are only
visible-change evidence; they are not a calibrated measurement of final pixel
opacity and are not used to infer exact lighting. Headless tests separately
confirm the unchanged shader's configured alpha cap and exact imported alpha.
