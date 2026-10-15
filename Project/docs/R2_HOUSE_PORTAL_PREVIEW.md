# R2 optional original A00 house preview

Open `scenes/portal_preview.tscn` and run the current scene. Default F5 remains the previously tested A13 R1 preview. This optional scene starts at original A00 room cell138,12 as a diagnostic; it does not claim the original story has transported the player there.

`world.setup(actor, map_path)` now reads the selected map's `texture_manifest` (fallback: R1 A13 manifest), clears prior per-map draw lists and texture cache, and preserves all source cells. A13 default setup remains unchanged. Game root exposes initial map/cell/title, while the independent portal subclass alone enables house transfers.

Included: original A00 ground/buildings/NPC images, same original layer/y/stable-order rendering, original house exit135,15 and135,16 →64,72, exterior64,71 →136,15. Portal radius `<0.25` cell and150 ticks/3seconds delay derive from the committed reference `game.js::checkPortal`, not a new original EXE timing proof. Transfers stop the old path and use the source destination exactly. Same-map portals are supported; cross-map targets are visibly reported as unsupported.

Scripts, ET, STOP, NPC visibility conditions, dialogue, combat, monsters, saving and inventory are deliberately not executed. All original NPC records are rendered, including any that eventual story conditions might hide. The nine northern barrier cells37,55/37,56/38,56/38,57/39,57/39,58/40,58/40,59/41,59 remain originally blocked; they are distinct from the nine northern portal cells near61,37. A first test mistakenly conflated those sets; its failure log is retained, and no map flags were changed to satisfy it.

Fresh headless test `tests/test_portal_preview.gd` walks first exit, returns, walks second exit, returns (four transfers), verifies all cells unchanged and all nine barriers closed, then reloads A13 and A00 without accumulating draw objects. Both existing R1 tests are rerun. GUI validation uses actual mouse clicks and source rendering, with screenshots and log in `diagnostics/r2`.

No save is read or written. Neither lost natural progression nor old code is represented as recovered. The optional scene remains a small new reconstruction stage.
