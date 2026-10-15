# R5 selected SE idle art preview

Run `res://scenes/art_preview.tscn` separately. Default R1 source movement is unchanged. This viewer covers only new SE idle frames13–16. It is not a complete new character, eight-direction movement, natural game or combat integration.

## Selected resources and controls
- `assets/scifi/hero/se_idle_v1/body.png`: identical SHA256 `91e7fb445775116ae2894900b76811757eda3898e78bf1e6881e38f933670ac9` to the registered AI atlas. Four128×128 regions, actor-origin offset(-16,-64), no further scale.
- `assets/scifi/hero/se_idle_v1/manifest.json`: frame/sole/projection/filter metadata.
- `scripts/art/hero_alpha_ground_shadow.gd` and `shaders/hero_alpha_ground_shadow.gdshader`: one alpha-derived soft shadow, body pixels unchanged. See helper contract for approximation/uncertainty.
- `scripts/art/preview_world_pass.gd`: floor and original ordered-object passes for this viewer only. Rendering order is floors, one shadow, original objects before actor, replacement body, original objects after actor. No original body/checker is drawn in new-body mode.

The viewer opens on clear road at(60,41), new body LINEAR, source/map art NEAREST. F1 selects the road-edge comparison(61,39); F4 returns to road interior. F2/F3 select tree-back(61,49)/front(61,53). S toggles only the new shadow; B selects complete original body/head and disables new shadow; L compares new-body sampling only; P advances13–16; C loops at12ticks. These are technical fixed positions, not claimed natural travel. Invalid shadow setup atomically chooses the complete original body/head without a new shadow.

## Fresh evidence and limitations
On2026-10-15 native GPU on/off at(60,41) had821 scene pixels differing by>2RGB, max55; both feet and visible shadow lie on the interior road away from the low edge. The earlier(61,39) pair had845 pixels/max55 but lies near a painted low curb; it proves shader visibility, not a platform receiver solution. A second intermediate(61,42) pair has foliage over feet and is not the primary contact evidence.

Four new poses with the same sole contract were viewed on interior ground, and a12tick loop was sampled. Tree-back body was covered by the original tree; tree-front body was visible with original foreground foliage still in front. Parent reviewed the same-frame nearest/linear comparison and selected linear for the new high-detail body. Original pixel art remains nearest. No mipmap comparison was needed for this selection.

The source shadow direction estimate is(+37/69.75,-27.75/69.75), screen-right/up. Near/far soles use different screen y as ground depth; neither foot is declared airborne from screen y alone. Projection is a2D ground approximation. No building, stair, bridge or platform receiver support is claimed. Frame15 nod and approximately2.9source-pixel boot projection residual remain recorded. This limited sampled loop is not full motion quality approval for unmade actions.

Evidence stays under ignored `diagnostics/r5` and shared verification paths. The selected atlas, metadata, generic shader/helper and normal-path standalone viewer form the publishable dependency closure. No ignored diagnostic asset or temporary test scene is needed by this viewer.
