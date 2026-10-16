# Upper-body evidence and smallest 57/59 proposal (read-only)

## Conclusion
The hands already alternate in the source screen-space direction. The remaining mismatch is not a reversed swing: it is larger discrete swing changes, different visible forearm/fist orientation, broader shoulder armor, and reduced vertical head motion. Moving hand centers by 1–2 logical pixels cannot establish the original upper-body pose. A mesh cannot reveal a different palm or hidden forearm surface from existing pixels.

No mesh, texture, exported frame, or original source was changed in this investigation. UPPER_VISIBLE_SOURCE_AI_6X.png is a nearest-neighbor diagnostic crop board. VISIBLE_ARM_EVIDENCE.json records the original skin boxes/cuff proxies, mapped AI skin components, temporal differences, and head references. All L/R are screen sides.

## Native visible source evidence
Original skin boxes and sleeve-edge proxies are independently recorded in Project/art_source/hero_s_walk_source_r8/SOURCE_VISIBLE_CHAIN_ANALYSIS.json. A skin bbox means the visible warm-colored end only. Source cuff proximity hides the proximal hand; fingers, palm orientation, wrist center, elbow and shoulder joints are unresolved. Source skin tolerance is ±2 logical pixels; cuff/clothing proxy tolerance is ±3. Do not use the long sleeve tip as a bare hand.

AI skin boxes come from warm-component selection in explicit hand ROIs, then visual checking. The boxes exclude the adjacent dark gauntlet. They are patch centers, not wrist centers; skin lighting and fist rotation affect the bbox. Do not treat subpixel transformed coordinates as subpixel anatomical accuracy.

## Phase readings (logical coordinates; y down)
Phase | Source L/R skin y | AI L/R skin y | Visible sleeve/armor reading
57 | 44.5 / 53.0 | 43.85 / 52.13 | L end high, R low. Source white L sleeve bends outward into a dark cuff; AI L metal forearm/fist presents a broad frontal surface. Source R cuff/skin hangs lower. AI shoulder caps are broader and rounder than source white shoulder clothing.
58 | 47.0 / 50.5 | 45.38 / 51.86 | Source approaches a less separated hand-height state. AI remains more like57: L too high and R too low relative to center readings; this concentrates the following swing into58→59.
59 | 51.0 / 46.5 | 51.59 / 45.02 | L low, R high. Source R sleeve has a sideways dark outer silhouette and tiny skin end. AI R black gauntlet curves back with a different visible surface; translating its skin end cannot recreate that sleeve silhouette.
60 | 53.0 / 44.5 | 52.04 / 43.85 | Reverse extreme: source L end down, R up. AI directions agree but visible elbow-area clothing folds and fist presentation differ. No anatomical elbow is assigned.
61 | 50.5 / 47.0 | 51.86 / 45.74 | Source begins returning; AI holds the reverse extreme longer (L lower, R higher), concentrating the following swing into61→62.
62 | 46.5 / 50.5 | 47.00 / 51.59 | Returns toward57. Source shoulder/clothing silhouette is slightly asymmetric; AI red caps remain relatively stable while forearm silhouettes change. Different garment designs prevent equating white shoulder boundary with red armor boundary.

Shoulder descriptions are qualitative surface observations, not numerical shoulder-joint localization. White cloth versus red armor does not provide a reliable shared outer-width target. Do not narrow the approved modern design merely to fit source clothing.

## Transitions and upper-body bob
58→59: source skin y deltas L +4 / R −4; AI +6.21 / −6.84. 61→62: source −4 / +3.5; AI −4.86 / +5.85. 62→57: source −2 / +2.5; AI −3.15 / +0.54. These are observed patch trajectories; ±2 source uncertainty means magnitudes are approximate, but the redistribution is consistent with the transition boards.

Source native head-layer x,y:57(36,16),58(37,15),59(37,15),60(37,16),61(36,15),62(37,15). AI alpha-crown logical y:15.68,15.32,15.14,15.68,15.32,15.14. The source layer top is not identical to an alpha crown, so use these only as temporal registration evidence. AI has ~0.54 px crown excursion versus source layer's1 px excursion, and appears flatter vertically. Do not pin heads per frame or manufacture bob from a sleeve edge. Head/chest remains unchanged in an arm-only trial.

## Smallest conditional57/59 trial
A diagnostic local arm warp is technically possible, but the available coordinates do not justify a unique source-exact forearm rotation. Before solving, freeze visible AI material masks on the crop board: each skin patch plus adjoining dark gauntlet, a transition band along the visible forearm cloth, and a fixed shoulder/chest boundary. Masks must follow actual alpha/material boundaries, not inferred elbow or shoulder centers. An ambiguous arm–torso join must be fixed or rejected, not cut across guessed anatomy.

Use the existing final full-alpha mesh and boot-corrected positions. All non-arm vertices, head/chest, leg geometry and shoulder attachment band fixed. All alpha>0 support retained. Skin plus hard gauntlet forms a near-rigid patch; initially translation only (no guessed rotation or hidden-surface reconstruction). Forearm cloth takes continuous local ARAP strain; no propagation through transparent gaps or across the torso. Existing positive-area and full boundary-intersection/contact gates remain unchanged; bounded steps/backtracking stop on failure.

Possible nominal patch translations, measured in logical pixels (multiply4 for HD output), if an explicitly labeled center-matching diagnostic is wanted:
57 L(−1.31,+0.65), R(−1.68,+0.87)
59 L(−0.54,−0.59), R(−1.13,+1.48)
These are hypotheses derived from the same hand centers and become DRIVERS, not evidence of success. Most lie inside the original ±2px uncertainty; the scientifically conservative default is a ±2px deadband, which may result in no forced motion. Exact matching is not more truthful than retaining the existing patch. A trial should be rejected as unnecessary if only center error improves and the visible pose does not.

Do not use source cuff proxy and skin center simultaneously to solve a precise arm angle: their distance is comparable to combined uncertainty. Rotation would require separate frozen visible material-edge evidence first. A57/59 trial cannot by itself repair58→59 or61→62 pacing; those phases remain frozen until reviewed.

## Independent acceptance, frozen before trial
1. Visible source sleeve direction and source cuff region held out qualitatively/with ±3px tolerance, not fitted. Record an inconclusive result where garment design changes the region.
2. Independent AI metal-panel width/length ratios and skin-patch shape versus undeformed baseline, measured on landmarks excluded from the rigid driver. No new skew, collapsed fist, doubled edge, or contact across alpha gaps. A rigidity-constrained panel is a deformation safety check, not source-action fidelity evidence.
3. Unchanged shoulder/chest/head/legs pixel projection and original shared registration; no torso width reduction or erased bob.
4. Alpha support, orientation and all nonneighbor boundary intersections; inspect gray/dark/light at true1x and2x.
5. Existing58 and62 as held-out transition neighbors: compare58→59 and62→57 at140ms. Evaluate observed hand-swing distribution and upper-body flicker, not just fitted centers.61→62 cannot be fixed by57/59; preserve that limitation.
6. Stop if perspective/visible fist surface remains wrong: existing pixels cannot supply the missing view. Report that limitation rather than enlarging allowable strain.

## Recommendation
Do not start another six-frame solve from center residuals alone. First review this visible-evidence board and choose whether a bounded translation-only57/59 diagnostic is useful. Its likely gain is small; the more material pacing problem is in58 and61, and the modern forearm/fist presentation may need source-guided redrawing rather than further mesh distortion. No such redraw or solver run is authorized by this proposal.
