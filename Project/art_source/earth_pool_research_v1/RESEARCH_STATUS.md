# Complete pool: registered research candidate and proposed ownership

## Scope and result

Parent approved the previously frozen single uniform rim-landmark map as a **research candidate**, not exact-art/collision acceptance. `pool-registered-research-2x.png` is 640×496 RGBA representing original world [3086,1800,3406,2048], density2. It was sampled once directly from unchanged raw with scalar affine bilinear mapping; it exactly equals the corresponding crop of the earlier padded diagnostic. No water-alpha cleanup or color changes were performed.

The original failed fixed-canvas contract, prompt, reference hashes and raw remain preserved. New mapping is deliberately a separately approved research registration, not a retroactive claim that generation honored the first contract.

Preview files, inspected:
- pool-registered-light.png
- pool-registered-dark.png
- pool-registered-original-ground-context.png

The last is original source floor-only context, reconstructed from actual atlas owners at nearest2×, with the coherent candidate overlaid. It is not current Earth-ground artwork, native runtime, foreground-depth validation or gameplay acceptance. No invented cast shadow added.

## Explicit loss and residuals

Frame crop discards 36 sampled nonzero pixels outside the original320×248 rectangle, all at alpha1. Zero samples above alpha8 discarded. These counts refer to the frozen padded diagnostic at2× and bilinear sampling; original raw remains authoritative. No strong art clipped.

Within the retained frame, 12 nonzero pixels lie outside the union of original seven draw rectangles; none exceeds alpha8. They remain in the whole research PNG. This is a small unresolved ownership issue for any later strict-rectangle renderer; do not silently clean them or expand owner bounds. A future proposal must explicitly choose how to handle those faint samples before claiming exact full/split reconstruction.

Notch contact shifts approximately6.04 logical left/3.91 down under this registration; lower-left bank retracts2.44 right/6.09 up. Held-out rim RMS5.23 logical; plants RMS5.05. Measurements have ±4 source logical/±8 raw-pixel visual uncertainty. Source grass apron is absent; candidate is mineral rim only. Waterline/rim height, exact foliage shapes and collision agreement remain unaccepted.

## Original ownership and order

See registration-and-ownership.json for exact world and2× bounds, flags, layers, sort_y and stable order. All seven owners are layer0; flags are1 for55–58,61 and−2 for59–60. Their rectangles share half-open vertical boundaries at world x3120,3168,3216,3264,3312,3360. In local2× texture these are68,164,260,356,452,548. Rectangles have different original y extents and are **disjoint: zero rectangle-overlap pixels**. Original x-major ordering remains:

55: y60/order6460
56: y61/order6561
57: y62/order6662
58: y63/order6763
59: y63/order6863
60: y63/order6963
61: y63/order7063

There are8 foreign original owner rectangles intersecting pool rectangles: Plant250@65,57; Plant246@67,56; Plant244@67,64; Plant246@68,58; Plant245@68,64; Plant322@69,73; Plant317@70,67; NPC189@64,63. All are layer1 in current inventory. These are rectangle overlaps, not proven opaque-pixel occlusions. Full coordinates/order are in foreign-rectangle-overlap.json. Do not collapse the pool into one newly sorted object or flatten foreground on top of a hand-made context to claim depth parity. Future actors and runtime behavior still require original scheduling.

## Atomic shared-texture proposal, not implemented

1. Retain one whole coherent texture, single origin and density. Never crop seven RGBA sprites and then linearly sample each independently: their artificial transparent/clamped boundaries create seams and potentially doubled alpha.
2. Preserve seven original owner records, coordinates, flags, source_cell, draw bounds and sort order. Each owner samples the SAME whole texture using shared world-to-UV mapping, with sampling footprints free to cross internal owner borders in the texture.
3. Determine draw ownership in world space by original half-open rectangles, after shared texture sampling. Ownership is categorical and disjoint, not a linearly filtered alpha mask. One raster sample has one owner. Shared texture supplies color/alpha neighbors across the owner boundary; owner gating must not pre-zero those neighbors. Keep edge coordinate/pixel-center conventions identical across owners.
4. A possible implementation is seven draws of shared geometry/texture with world-rectangle fragment ownership; preserve original node order. Exact rasterization edges and filter semantics need native proof. No local texture-region clamp or per-fragment UV reset.
5. Treat all seven records as one atomic resource transaction: validate shared texture/hash/density/origin and seven expected IDs first. If any record or texture is missing, fall back for the **entire original pool**, not a mixed subset. This must not expand the ground replacement mask or switch the second source instance automatically.
6. Retain original floor owners intact. Resolve the12 faint unowned samples explicitly before any claim of total-pixel ownership; preserving the whole texture alone does not solve draw ownership. No shadow receiver/contact invention.

## Lessons actually consulted

Bamboo SINGLE_LAYERED_REVISION_RESULT.md: original foreground ordering matters; hidden-group background plus whole overlay did not reconstruct original native image. Premultiplied capture handling matters; wrong straight-alpha math can be misdiagnosed as occlusion. Hence preserve original owner order and validate full scene/transparent foreground separately.

Ground-material-seam/README.md: shared-atlas sampling eliminated measured interior LINEAR interface discrepancies in previous ground diagnostics, but unchanged material art still retained real seams. That motivates shared whole-texture sampling here; it is not proof that this new pool is renderer-correct. Preserve visual/material and sampling decisions as separate gates.

Required future evidence if integration is authorized: source/off exact parity; whole-vs-owner reconstruction; no double coverage or missing strong pixels; NEAREST/LINEAR seams at1×/2× and fractional camera positions; alpha-edge/premultiplication checks on light/dark/floor backgrounds; original order with actual foreground and actor traversals; atomic fallback; unchanged collision/source fields and floor resources. Native GUI remains with its designated owner. No tests or runtime integration performed here.

## Dependencies and provenance

prepare_research_candidate.py regenerates candidate/previews and ownership metrics from unchanged raw plus landmark-diagnostic.json, source-group.json and original inventory/atlases. registered-provenance.json hashes all direct reconstruction inputs. Raw generation provenance remains prompt.txt and frozen-contract.json. Requires Python, Pillow and NumPy. It does not execute project/runtime code. Source floor crops validate RGBA hashes against inventory before use.

All work remains outside Project. No production asset, runtime manifest, collision, source field, Git state or GUI was modified. No owner texture fragments were saved.
