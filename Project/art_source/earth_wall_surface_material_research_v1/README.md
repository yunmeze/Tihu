# Wall surface microtextures: source-only research

Four unique original RGB outputs and their exact prompts, ordered actual references and call records are retained unchanged. M2/M3/M1 each used the already-published house body as the sole material reference. M1-edit used only the first M1 raw. No extra generation, seam blending, grading, alpha changes or wall sampling is included.

- M2 concrete: root accepted the material candidate, with the blue edge-band bias 3.136/255 WARN preserved. Not certified mathematically seamless.
- M3 concrete: root accepted the material candidate.
- M1 graphite and its sole edit: both failed gradient/periodicity gates. Edge-band peak 21.572 to 7.045/255; jump ratio 3.434 to 2.473. This generation route stopped.

The surface-plan contains manually proposed Q267/Q322 two-dimensional partitions, original 8-owner geometry/order, four flag0 tail pieces, and pure-rotation uniform-screen-density UV constraints. It does not recover physical 3D or implement wall mapping. Ridge, folds, seams, eave shading, corner interfaces and real occlusion remain unfinished. The subsequent structured-metal contract is a proposal, not another generated result.

## Portable read-only replay

    python replay_sources.py --repo /path/to/tihu-legend --report /outside/archive/wall-replay.json

Requires Python 3, Pillow, NumPy and Git. Checks all archived bytes and exact Git blobs; resolves actual reference order; recalculates raw edge/interior jump ratios and edge-band RGB values. It does not reproduce omitted review boards, apply UVs or run an engine. Original files use 1254 square canvases; the proposed shared period is 64*sqrt(13) logical pixels and density 5.434328484894042. Actual square size replaces only the initially requested 1024 size gate, not failed content/periodicity gates.

The already-published house reference and original wall geometry/source support are referenced by exact Git blob and SHA in DEPENDENCIES.json, not duplicated. PATH_MAP.json resolves historical call paths without needing recovery-work or /tmp. Original report paths and superseded pending statuses remain historical provenance; FINAL_HANDOFF and this README explain the final research judgment. No executable here opens those historical absolute paths. .gdignore excludes the research from editor scanning. No runtime assets or activation are supplied.
