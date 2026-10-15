# A13 first-screen ground: source-only production plan

Reproduce from repository root: python Project/tools/prepare_a13_ground_source.py

Inputs are the extracted A13 map, original atlases and original manifest. The script writes only this contract and ignored Project/diagnostics/art_source/a13-ground files. It does not write original sources, runtime, terrain or Git state.

## Scope and evidence

A13 has 2,553 floor placements and 70 signed IDs: FloorBig 2,481/47 and FloorSmall 72/23 (placements/unique IDs). Dominant IDs are -406 (888), -402 (853), -394 (306), -395 (143). Zero floor cells are not missing tile assets.

At actor/camera (61,39), 1024x768 and screen origin (.5,.54), initial world viewport is [2416,833.28,3440,1601.28]. The floor-only coverage set is 143 placements / 15 IDs, all FloorBig with actual 96x64 original canvases. The logical 48x32 grid is not the tile texture size. Includes tiny visible bottom-row intersections; do not silently drop them. Native source board encloses the fractional view and is not a GPU screenshot.

## Inspect before producing

1. Inspect first-screen-view.png and first-screen-complete-tiles.png for the source floor composition; owner-board labels placements. These omit objects intentionally and do not claim final scene visibility.
2. Inspect road-head-context-complete-tiles.png and its 2x board for a smaller genuine grass/road junction, including the flat road cap, corner, diagonal edges and tan interior. Contract lists full tile contributors and exact world bounds.
3. Inspect first-screen-unique-source-tiles.png and both owners-and-seams JSON files. Pack + signed ID matters. -406 is repeated grass; -398/-399/-407 add grass variants. Narrow stone borders surround tan earth/gravel road. Do not label the entire tan area silver bricks or infer temple apron/checker material from this floor-only group.

## Future production and acceptance

Approve a coherent assembled-region style and scale before generation. Work on shared texture/edge families and assembled junction context, then register back to native owners; avoid separately generating each tile with independent seams. Keep source dimensions, crop, positions and draw order. Validate every recorded adjacent pair, diagonal/flat/corner border continuation and repeated grass at native 1x and 2x. Do not add building shadows/aprons to the floor. Expand beyond the 15-ID stationary view only when movement scope requires it. Replacement art, runtime installation and actual camera/movement validation are not included here.
