# Source-driven material v2 review

Status: raw saved; offline candidate only, awaiting parent visual decision. Exactly one generation per material in this version. No third generation, runtime change, RGB repair or source map change.

Both raw images are 1254 square. Four exact input crops and their original atlas coordinates or accepted context rectangles are preserved under inputs/. The reference images exclude both rejected standalone v1 materials.

Compared with v1, grass is finer and less bright clover-like; soil has smaller grains and fewer conspicuous stones. At period768 the full field is still yellower/brighter than the original and details remain more explicit. This is a design comparison, not accepted sameness.

Independent periodic tests find regular repeat still discontinuous: at world period768, grass vertical/horizontal edge jump 18.60/21.20 and edge-minus-internal gradient 7.13/8.05; soil 16.40/17.34 and net 6.65/6.18. Mirrored repeat eliminates the discrete wrap jump by repeating boundary samples; reflected grass dark forms and paired soil texture remain observable. It is sampling-assisted continuity, never proof of naturally seamless raw generation. The full143 repeat/mirror board was actually inspected.

The original20 and143 placements are recomposed at world periods512/768/1024 without moving their bounds. Shared world UV removes per-ID material restarts; the two original pure-soil IDs missing from the first context now use the same soil field in this diagnostic. Masks cover each context once with zero uncovered/multiply-owned pixels, which is not aesthetic acceptance.

The rejected11px constant curb ribbon is replaced by six explicitly bounded visible generated stone faces. The right-side vegetation-covered gap is not filled with invented hidden stone. Source road centerline uncertainty remains +/-3 native pixels; stone-face reading +/-1 native pixel. Individual curb RGB is retained unchanged from the uniformly registered accepted context. This narrowing excludes most adjacent grass/soil, but an uncertain one-pixel material fringe is still a visual-review item. Source/generated curb geometry is not claimed exactly identical.

Reproduce offline assembly: python Project/art_source/a13_ground_materials_v2/diagnose_world_materials.py. It reads the frozen production source contract/atlases and accepted context raw directly; same-ID curb sample choices are frozen in the script and research JSON. It only writes ignored outputs. Semantic face coordinates and assumptions are saved in semantic-mask-research.json. Sampling uses uniformly resampled immutable textures and repeat or mirror addressing, not per-tile recoloring or drawn stone artwork.

Important boards under diagnostics/art_source/a13-ground/world-material-v2/: first143-comparison.jpg, first143-repeat-mirror.jpg, context20-repeat-mirror.jpg, stone-mask-boundary-proof.png. Independent density and repeat/mirror measurements are under materials-v2-tiling/. No native terrain test has yet occurred.
