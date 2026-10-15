# Round shrub four-owner technical candidate

The parent accepted the generated whole/native-size shrub as a bounded working
candidate. This package registers that same immutable image to only the selected
A13 shrub centered at (57,38). Native GPU and actor-depth review remain pending.

## Transform and four original owners

Every owner texture is **1363x1154**, with the same world top-left
**(2690.9773371104817,1138.8451369216242)** and uniform scale
**0.09442870632672333**. Texture rectangles are the complete raw canvas. Use
nearest filtering without mipmaps, rotation, shear or per-owner translation.
The four textures contain disjoint raw RGBA pixels, with transparent black outside
their ownership. No original raw RGBA channel is cleaned, repainted or thresholded.
Original nonzero RGB under zero alpha is also preserved exactly once.

- Plant:143@57,35: layer1, sort_y35, stable order5735, original flag0
- Plant:144@56,38: layer1, sort_y38, stable order5638, original flag-1
- Plant:145@57,38: layer1, sort_y38, stable order5738, original flag-1
- Plant:146@58,38: layer1, sort_y38, stable order5838, original flag-1

All four draw at their original object-list positions; do not collapse them into a
single sorted body. The actual root and receiver remain null. Alignment was by
visible foliage envelope only. The logical map draw origin is not a root.

## Reproducible ownership

Source nontransparent pixels retain the owner of the original four source images.
The candidate raw texel center is mapped through the one approved transform to a
source pixel-grid cell. Where source coverage is absent, the nearest occupied
source cell supplies draw ownership via scipy.ndimage.distance_transform_edt.
The padded source grid and SciPy version are in registration.json. The retained
owner-index.png records the exact full-resolution owner map, values1..4.

This extrapolation controls sorting only. It does not infer botanical depth or
physical contact. No source RGB value is classified or deleted, including its
leaf-interior dark checker. All four original source objects are suppressed
atomically when the new four-owner body is selected.

## Why a common full canvas

Tightly cropped owner textures reconstructed every raw byte, but separate floating
crop offsets could choose different adjacent texels at exact nearest-sampling
boundaries. A CPU half-pixel camera test exposed a one-column difference. Keeping
all four textures at the identical size, origin and UV extent removes that source
of inconsistency. All25 native/fractional/clipped CPU cases now match full raw
exactly. This is still not an engine GPU acceptance.

The four RGBA8 textures require25,166,432 uncompressed bytes (about24MiB), before
runtime overhead, with no mipmaps. Their PNG files total about2.3MiB. This is an
explicit single-pilot tradeoff. Do not silently tighten crops or enable independent
linear filtering as an optimization. Any later optimization needs parity review.

## Atomic activation and scope

Load and validate all four textures/config first. Either select all four new
owners while suppressing all four source keys, or restore the complete source
group. A partial body or a new/source blend is not valid. This stage adds no cast.
Any later ground shadow must be derived once from the whole shrub, not four times
from owner textures. Actual source root is unknown; future foliage-edge proxies
must be identified as such.

Only the (57,38) group is authorized for the first native review. The other seven
translated groups remain source. Nominal first-screen context has whole bounding
boxes for(57,38),(64,45), left-clipped(51,44), and bottom-clipped(58,51). The second
whole bounding box also overlaps an original tree; geometry alone does not prove
visibility. Check that these remaining source groups and viewport edges stay intact.

## Validation and review handoff

Rebuild:

    python3 art_source/a13_round_shrub_candidate_v1/measure_candidate.py
    python3 art_source/a13_round_shrub_candidate_v1/build_technical_partition.py

The builder compares all6,291,608 raw RGBA bytes; all978,043 stored nonzero RGBA
pixels have one owner; all977,318 nonzero-alpha pixels survive. The four original
sort tuples are unchanged. The25 CPU nearest tests include fractional camera
positions and clipping. Local tests/reports live under diagnostics and are not
production dependencies or part of the minimal stage.

Required sole-runtime-owner checks: exact same-phase whole-vs-four GPU parity,
selected-shrub actor front/back and source/new toggle, first-screen remaining
source groups and clipping, and invalid-resource complete four-source fallback.
Keep the default entry unchanged. Native scale white dots and alpha1..15 green
fringe remain the parent-reviewed raw residuals; no image cleanup is authorized.

The working-grass board uses the bounded working256 material sampled in world
coordinates onto an offline flat texture plane. It is not a claim that the whole
map has that material or a receiver/depth acceptance. The earlier native-grass
strip used original FloorBig406 and is labeled separately in REVIEW.md.

## Direct high-density rendering and bounded reuse

For the current HD review, render these raw-resolution textures directly through
the same2x canvas transform while keeping the logical1024x768 world/camera.
Do not pre-bake a124x105 body and then magnify it. A separate local25-case CPU
check at direct2x physical sampling also produced zero whole/four RGBA differences.
The direct-HD comparison is distinct from the earlier diagnostic pixel enlargement.
`first-screen-reuse-index.json` retains all eight existing source groups and their
original sort tuples, but marks only four as first-screen candidates. After the
pilot passes, other first-screen groups require their own depth/clipping review.
No distant-map rollout or extra generation is part of this package.
