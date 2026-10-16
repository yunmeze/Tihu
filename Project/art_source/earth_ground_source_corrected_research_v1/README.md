# Source-corrected ground research archive

Research only. No production registration or runtime change. The original generated G1, G2 and C fields remain unchanged in their source packages. G2 is sampled at 5/8 scale and composed through two disjoint donor regions; G1 and the cross-seam candidate are retained as source-generation provenance, not selected final material.

The final PNG is an exact byte copy of the frozen source-corrected result. Canvas: 1536×1152 pixels; world origin (2400,1296), two pixels per world unit. Native C donor mapping is C(x,y−64); the frozen assembled G donor uses G(x,y). Source geometry and fixed replace mask are in earth_ground_cross_seam_revision_plan_v3.

The upstream join alone changes geometry at local y=72..99: smoothstep displacement 4.5 raw pixels and width reduction 3 raw pixels, decaying to zero at y=100. This adds 42 curb pixels and restores 84 from G. Three immutable support masks identify deep seam, bright lip and grass contact. Their union is 7,617 pixels. Seam and lip sample original continuous C before applying the frozen mapping once; grass samples frozen G. Contact lighting never reuses already contact-shaded pixels.

Run from repository root:

    python Project/art_source/earth_ground_source_corrected_research_v1/reproduce.py --output /tmp/reproduced-ground.png

Requires Python, Pillow and NumPy. Verified with Pillow 12.3.0 and NumPy 2.3.5. The script verifies every direct input hash, rebuilds geometry and contact, checks exact RGBA equality, and refuses to overwrite output. PNG byte identity additionally depends on encoder version.

To regenerate donor intermediates, run prepare_domains.py, prepare_sampling.py, compose_research.py and assemble_research.py in that order in a disposable checkout. These historical scripts also produce excluded diagnostics; SciPy 1.17.0 was used. Only selected necessary inputs, selected intermediates and original generation provenance are archived. Diagnostic images, stage differences, alternate scale samples, unused hard-join composites and upload manifests are omitted.

Remaining visual limitations: B grass seam; fine/coarse G texture transition; C grain/brightness mismatch; bright-lip contrast compression; exit guard material junction. Corrected double shading is not whole-ground acceptance. Runtime owner registrations and source originals remain untouched.
