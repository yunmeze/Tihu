# Bounded first143 true2x sampling recipe

Run export_probe.py from any cwd. Output PNGs and native registration are local validation resources, not promoted production terrain. Original logical world rectangles,143 keys,15 ID masks,road width and flags remain unchanged. First-screen outer scope is still source.

World material period stays256 logical pixels, mirror superperiod512. Immutable1254 materials are uniformly LANCZOS downsampled to512 texels, then world sampled at2 texels per logical unit. This is not the earlier512-world-period test and not an enlargement of the256 sampled texture. Source raw is never modified. Generated stone is sampled directly from immutable1717x916 context raw to960x512 with the original uniform geometry fit; no enlargement of the old480x192 stone atlas. Existing semantic masks are duplicated exactly2x so this density test does not change layout or blend boundaries. All143 original source floor alphas were independently checked255.

Actual renderer must render2048x1536 pixels while retaining1024x768 logical composition and original world mapping. Each192x128 PNG draws into its original96x64 world rect. A screenshot enlarged after1024 rendering does not establish this result. Fine detail/noise and mirror motifs still require native review with the same character/building/tree at this physical density.

Inputs are tracked A13 source-group contract, historical mirror-v2 registration and semantic/stone atlas, immutable v2 material raws and accepted context raw. No ignored input is required. The diagnostic script also emits a same-world-period baseline/candidate board; those tests are not in this source stage.
