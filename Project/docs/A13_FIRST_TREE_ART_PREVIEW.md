# First A13 golden tree: bounded structural preview

The optional `scenes/art_preview.tscn` exposes G to toggle the original/selected first tree. F6 places the source hero at the reviewed trunk-front point (57,35). T still controls the temple independently. The default source game and natural new-game candidate are unchanged.

The selected registration is `assets/scifi/environment/a13_first_tree_v1/registration.json`; its seven cutout PNGs are byte-identical to technical_v1. Only Plant292@(57,34),293@(55,37),294@(56,37),295@(58,37),296@(59,37),297@(60,37),298@(61,37) are suppressed and replaced. Source cell flags, layer, sort_y and original stable owner order are retained. The other tree of the same family remains original.

Nearest sampling is retained. A native whole-image versus seven-piece comparison at the same world origin produced exactly zero changed scene pixels (UI label rows excluded). The original A* route from (61,39) to (57,32), then (57,35), then (59,38) completed 512 movement updates. Original and selected versions were captured at each stop with explicit source South17 diagnostic pose. The crown obscures the back point, while trunk-front and all-front points remain visible in original ordering.

Eight captured moving samples showed no whole-cluster disappearance, cutout seam or trunk/crown displacement. Fine leaf brightness varies under nearest sampling; this is a bounded sample review, not a continuous-video proof of zero shimmer. Source/new foliage silhouette and color differences remain intentional visual changes.

## Accepted bounded ground cast

The later shadow stage uses `assets/scifi/environment/a13_first_tree_shadow_v1/shadow.json` and its byte-identical whole raw PNG. A single alpha projection is drawn after all floors and before every object/body pass. It is never repeated for the seven cutouts. G toggles the whole selected tree and cast together; H explicitly disables/enables only the new cast for comparison. Any failed shadow-resource preparation or configuration restores all seven source owners and hides the new cast.

The accepted explicit parameters are raw root(498,1224), horizontal receiver, common scale0.2472072097078169, cast(148/279,-111/279), opacity.30 and blur3raw pixels (about.742 native). Native same-phase on/off checks at(57,32),(57,35),(59,38) retained the original depth categories and placed the cast on grass toward screen-right/up. The observed RGB differences prove visible changes, not a direct measurement of shader opacity. ShaderMaterial reads independently confirmed color alpha.30, blur3 and one pass. Invalid texture testing restored the complete source tree.

This is a stable2D silhouette approximation for this one ground instance. It does not establish physical tree height, canopy self-shadow, platform receiving, or exact original checker shape. The original opaque checker belongs only to source mode; no checker overlay or contact ellipse is added to the selected tree.
