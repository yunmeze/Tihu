# S idle contact shadow runtime package

Scope: S idle source IDs 17–20, unchanged d4 body and 12-tick phase timing. SE keeps its existing projection. E and S walk/run remain disabled.

The envelope PNG is an exact byte copy of the frozen CPU full-alpha union: 208×96 at density 2, offset (26.5,79), 6901 occupied cells, 171 integer placements. It includes every nonzero source texel, bilinear support, nine-tap ground-space filtering and boot-read error. Whole-caster receiver gating is required; no clipped shadows.

Manifest fixes the forward/inverse formulas, constants, q-space taps, actual atlas regions, body SHA and runtime dependency SHAs. Three ownership regions reconstruct the same original alpha; they are shadow sampling regions only. The body manifest original “shadow disabled” delivery note is superseded solely for S idle by this independent contract.

Residual limitations: S18 boot-proxy displacement up to 0.9801 logical pixels; approximately 1.15% of opaque lower-shin texels have high anisotropy, maximum 53.18. Thin local contact stretch remains. This is a fixed 2D approximation, not physical height reconstruction. No measured frame-time performance claim.

Native AABB validation: 53 matching captures RGB-identical before/after optimization. Final cleanup validation: 7 captures RGB-identical, no ERROR or resource-leak messages in final run; only environment VSync warning. Production cold import, 12480 owner checks, R1/R6 regressions and three-entry startup checks subsequently passed. Production native 51 matching captures are RGB-identical to diagnostic captures; final native log exits without ERROR. Independent cached-resource probes confirm missing body/envelope PNG disables only hero and restoring bytes recovers all five slots (17 checks, zero failures). The first probe launch failed before testing because HOME was not writable; the recorded retry used a writable HOME and exited cleanly. The first startup command used an incorrect entry path; the corrected three-entry run is the accepted evidence.

Runtime reads production paths only. Research files are immutable provenance, not runtime dependencies. Gate code embeds the manifest hash; its own hash is excluded from manifest to avoid cyclic hashing.
