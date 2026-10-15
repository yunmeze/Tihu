# Diagnostic implementation read-only review

2026-10-15. Read-only review of the runner implementation; no implementation edits or GUI/GPU performed by this reviewer.

The four explicit samplers preserve raw body transform inversion, original inverse projection, raw region guard before texel-center clamp, textureLod0, normalized3×3 blur and opacity before max. Disabled slots branch to zero before any sampling. One common source_color tint and one blend_mix pass remain. The driver refreshes original helpers/gates before reading valid states, then hides their draws, so hiding is not retained as eligibility on the next refresh. Single invalid v2 inputs do not redefine the old SE/Fang gates.

The diagnostic quad draws the fixed768×512 sample viewport rather than the tighter transformed union AABB. This is an acceptable conservative superset for the current fixed camera: each slot rejects outside its original padded raw bounds, and all qualified supports are inside the approved sample. No aggregate receiver clipping occurs. This does not establish dynamic-camera correctness and retains the full-screen performance upper bound. No redraw optimization is requested for this diagnostic.

Common tint equality is currently enforced with assert. This is adequate for the controlled debug diagnostic with frozen inputs, but future production adoption requires explicit fail-closed handling because release builds may strip assertions. No promotion is approved by this review.

The runner reported singleton max RGB deltas1/1/0/1 with zero pixels above2; the full route/all-phase verification was still running at this review. Treat later runner evidence as the authority for completed native acceptance, not this source review.

Reviewed file hashes at this checkpoint:

- shaders/earth_shadow_max_diagnostic.gdshader: 468a56b98e5eb57bac5c3cf9c554f0bf31c22bbfd4d5969b1e4719a64d88a85a
- scripts/diagnostics/earth_shadow_max_quad.gd: 1572ce864438081f5de58cc5997944538a7bfd525d266445b52b694f081f2147
- scripts/diagnostics/earth_shadow_max_native.gd: a531a2e76cf786f1ca0454e2371287a5bfcfc9b3d23ed4e9add5e6579d046661
