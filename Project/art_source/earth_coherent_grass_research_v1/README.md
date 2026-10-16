# Coherent grass research baseline

Research-only CPU composition, not a production terrain replacement or complete grass semantic mask. No default scene, runtime, source asset or character sequence is changed. This archive freezes one canonical conservative core-only baseline PNG, with a separately selectable exact-support contact-material variant represented by recipe and hash.

## Scope and world mapping

World rectangle [2400,960,3264,1920), density 2, canvas 1728×1920. Initial64 owners plus57 new south owners yield121 unique owners. Seven overlapping south owners resolve to initial ownership, never duplicate. Original map cells, atlas frames, owner positions and opaque source alpha are verified. The base union is rebuilt from tracked initial/south raw art, the frozen source-corrected patch and exact fixed patch mask; no ignored diagnostic registration, plate or test harness is needed.

Core contains exactly2,373,576 texels:2,039,808 confirmed grass-base texels plus333,768 manually reviewed mixed-frame grass-interior texels. SOURCE_INTERIOR_POLYGONS.json preserves source-pixel polygons, atlas metadata, owner occurrences and source RGBA hashes. Source frames588 and597 are proven RGBA-identical before polygon reuse. Every unassigned mixed-frame pixel stays uncertain. Entire385/386/388 earth-transition owners remain excluded, even where a polygon marks a grass interior. Frame598 upper-left details remain unresolved. This is a conservative reviewed interior, not a full surveyed grass silhouette or RGB-based classification.

The original road/curb interiors, tan base, earth transitions, uncertainty, authored corrected curb and all frozen seam/lip/grass-contact supports remain unchanged. Reproduction verifies zero core overlap and zero output changes in all nine protection categories. Core SHA256:

d40582eddfc1b8b86c57aabcdf420c954e7f96cc7e2b1c53b2493f8674b9cb84

## Material and transforms

raw.png is the unchanged1254×1254 generated periodic-material source. prompt.txt and GENERATION_INPUTS.json preserve the actual prompt and references. Both exact reference images already exist in tracked source packages and are dependency-linked in ARCHIVE_PROVENANCE.json rather than duplicated.

Sequence:1254→1024 uniform LANCZOS; one global encoded-sRGB per-channel affine; then1024→768 uniform LANCZOS. The affine matches channel means/standard deviations to the full approved1536×512 grass reference. It is not linear-light grading or local fitting. Gain RGB=[0.8910818574512701,0.8733941836778478,0.899700263950368]; bias RGB=[0.08599077854143994,0.05856649093649219,0.0838099046949888]. No pixels clipped. Full metrics are preserved in PALETTE_TRANSFORM.json.

The resulting768×768 tile has period384 world units, world phase(0,0), fixed orientation and no per-owner phase reset. Union pixel(x,y) samples tile[(1920+y)%768,(4800+x)%768]. Replace RGB only at the frozen conservative core; retain every alpha value. Exactly2,373,527 pixels change, with49 coincidentally equal pixels inside scope and zero changes outside.

Final SHA256:

d6bf26a3bd518798ca1ecdde9ebc3be9e722f64034acc42303bc87128a72a4c4

## Reproduce

    python Project/art_source/earth_coherent_grass_research_v1/reproduce.py --output /tmp/coherent-grass-reproduction

Use a nonexistent output directory. Verified with Python, Pillow12.3.0 and NumPy2.3.5. The script checks hashes, independently reconstructs base plates/owners/semantic core/protections, computes palette coefficients and periodic field, then verifies exact final RGBA and PNG bytes. It writes only into the requested output directory. Compressed-byte identity depends on encoder version. Generation itself is stochastic; archived raw bytes are authoritative.

The broader B material split is removed within this coherent core. Coarse/color halos remain in protected road-contact guards; curled blades, repeated motifs and excess x-wrap discontinuity remain unresolved. Do not call this seamlessly accepted production grass. Original contact lighting is preserved, not reapplied to this core.

Excluded:failed strip trials, diagnostic boards/GIFs/tests/native captures, alternate period outputs, redundant base union and intermediate tiles, runtime integration and temporary reproduction files. Historical provenance files retain original research paths/statuses; executable code uses only repository-relative inputs.

## Optional exact grass-contact material refresh

Add --contact-refresh to the reproduction command to emit a separate OPTIONAL-contact-refreshed-union-RESEARCH.png. The baseline PNG stays unchanged. OPTIONAL_CONTACT_REFRESH.json freezes the result hash and exact original support/parameter hashes; no second large union PNG is archived.

Only the existing3,283-pixel grass-contact support at local offset(0,672) is eligible. Sample the fresh unshaded periodic tile at unchanged world phase(0,0), decode sRGB to linear RGB, multiply once by the original k=0.5314862566564135, encode sRGB and round floor(255*v+.5). Never darken baseline-shaded RGB again. Exactly3,282 pixels change; alpha and all pixels outside support remain unchanged, including seam/lip/authored curb. No support, lighting coefficient or geometry changes. The broad uncertainty/coarse-grass halo remains unresolved.

Optional variant SHA256:

8d936f99af4308cf028a905db79e7a7d39b71fee316308cbe20871f8cf6ede6d
