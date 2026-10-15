"""Reproduce A13 ground source groups. No generated textures or runtime writes.
Run from any directory: python Project/tools/prepare_a13_ground_source.py
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
import math
from PIL import Image, ImageDraw

P = Path(__file__).resolve().parents[1]
OUT = P / 'art_source/a13_ground_source'
DIAG = P / 'diagnostics/art_source/a13-ground'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def intersect(r, b):
    x, y, w, h = r
    return x < b[2] and y < b[3] and x+w > b[0] and y+h > b[1]

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    DIAG.mkdir(parents=True, exist_ok=True)
    mp = P/'data/maps/A13.json'
    mf = P/'assets/original/manifest.json'
    m = json.loads(mp.read_text())
    packs = json.loads(mf.read_text())['packs']
    pages, images, owners, frames = {}, {}, [], {}
    for i, c in enumerate(m['cells']):
        signed = c[0]
        if not signed:
            continue
        x, y = divmod(i, m['height'])
        name = 'Map/Res/FloorBig' if signed < 0 else 'Map/Res/FloorSmall'
        pack = packs[name]
        f = pack['frames'][str(abs(signed))]
        a, b, w, h = f['rect']
        page = pack['pages'][f['page']]['file']
        if page not in pages:
            pages[page] = Image.open(P/page[6:]).convert('RGBA')
        if signed not in images:
            images[signed] = pages[page].crop((a,b,a+w,b+h))
            frames[signed] = {'signed_id': signed, 'pack': name, 'frame_index': abs(signed),
                'original_canvas': f['original'], 'crop': f['crop'], 'atlas_rect': f['rect'],
                'atlas_page': page, 'source_offset_ignored': f['offset'],
                'native_source_offset': f['sourceOffset'], 'native_source_bytes': f['sourceBytes'],
                'rgba_sha256': hashlib.sha256(images[signed].tobytes()).hexdigest(),
                'alpha_extrema': list(images[signed].getchannel('A').getextrema())}
        owners.append({'key': f'{name}:{abs(signed)}@{x},{y}', 'signed_id': signed,
            'cell': [x,y], 'stable_source_order': i, 'source_cell': c,
            'source_map_byte_offset': m['cellByteOffsets'][i],
            'world_rect': [x*48+f['crop'][0], y*32+f['crop'][1], w,h]})
    def counts(seq):
        return [{'signed_id': k, 'placements': n} for k,n in Counter(o['signed_id'] for o in seq).most_common()]
    def compose(seq, bounds):
        result = Image.new('RGBA', (bounds[2]-bounds[0],bounds[3]-bounds[1]))
        for o in seq:
            x,y,_,_ = o['world_rect']
            result.alpha_composite(images[o['signed_id']], (x-bounds[0],y-bounds[1]))
        return result
    # Continuous renderer view; diagnostic native pixels use its integer containing rectangle.
    viewport = [1024,768]
    camera = [61,39]
    origin = [viewport[0]*.5-camera[0]*48, viewport[1]*.54-camera[1]*32]
    view = [-origin[0],-origin[1],viewport[0]-origin[0],viewport[1]-origin[1]]
    region_specs = [('first-screen',view), ('road-head-context',[56*48,36*32,66*48,44*32])]
    regions = []
    for slug,bounds in region_specs:
        selected = [o for o in owners if intersect(o['world_rect'],bounds)]
        raster = [math.floor(bounds[0]),math.floor(bounds[1]),math.ceil(bounds[2]),math.ceil(bounds[3])]
        context = [min(o['world_rect'][0] for o in selected),min(o['world_rect'][1] for o in selected),
            max(o['world_rect'][0]+o['world_rect'][2] for o in selected),
            max(o['world_rect'][1]+o['world_rect'][3] for o in selected)]
        # Include every contributor to the expanded rectangle, not just the clipped viewport owners.
        full = [o for o in owners if intersect(o['world_rect'],context)]
        composite = compose(full,context)
        composite.save(DIAG/f'{slug}-complete-tiles.png')
        cropped = compose(selected,raster)
        cropped.save(DIAG/f'{slug}-view.png')
        board = composite.convert('RGB')
        draw = ImageDraw.Draw(board)
        for o in full:
            x,y,w,h = o['world_rect']; x-=context[0]; y-=context[1]
            draw.rectangle((x,y,x+w-1,y+h-1),outline=(230,80,90))
            draw.text((x+2,y+2),f"{o['signed_id']} @{o['cell'][0]},{o['cell'][1]}",fill=(255,40,40))
        board.save(DIAG/f'{slug}-owner-board.png')
        seams = []
        for a in full:
            ax,ay,aw,ah = a['world_rect']
            for b in full:
                bx,by,bw,bh = b['world_rect']
                if ax+aw==bx and max(ay,by)<min(ay+ah,by+bh):
                    seams.append({'axis':'vertical','world_line':[bx,max(ay,by),bx,min(ay+ah,by+bh)],'before':a['key'],'after':b['key']})
                if ay+ah==by and max(ax,bx)<min(ax+aw,bx+bw):
                    seams.append({'axis':'horizontal','world_line':[max(ax,bx),by,min(ax+aw,bx+bw),by],'before':a['key'],'after':b['key']})
        save(DIAG/f'{slug}-owners-and-seams.json', {'owners_in_draw_order':full,'touching_edges':seams})
        regions.append({'id':slug,'continuous_world_bounds_xyxy':bounds,'diagnostic_raster_bounds_xyxy':raster,
            'complete_tile_context_bounds_xyxy':context,'intersecting_placements':len(selected),
            'unique_signed_ids':sorted(set(o['signed_id'] for o in selected)), 'placement_counts':counts(selected),
            'complete_context_placements':len(full),'touching_edge_count':len(seams),
            'source_alpha_extrema':list(cropped.getchannel('A').getextrema()),
            'owners_in_draw_order':selected,'diagnostic_manifest':f'Project/diagnostics/art_source/a13-ground/{slug}-owners-and-seams.json'})
    ids=regions[0]['unique_signed_ids']
    board=Image.new('RGB',(5*132,math.ceil(len(ids)/5)*92),(48,48,48)); d=ImageDraw.Draw(board)
    for i,k in enumerate(ids):
        x,y=i%5*132,i//5*92
        board.paste(images[k],(x,y+24),images[k]);d.text((x,y),str(k)+' '+str(images[k].size),fill='white')
    board.save(DIAG/'first-screen-unique-source-tiles.png')
    # Actual junction pixels at native scale and nearest-neighbor magnification; no new material.
    full=regions[1]['owners_in_draw_order']; b=regions[1]['diagnostic_raster_bounds_xyxy']; patch=compose(full,b)
    patch.resize((patch.width*2,patch.height*2),Image.Resampling.NEAREST).save(DIAG/'road-head-context-2x.png')
    total=counts(owners)
    save(DIAG/'all-map-floor-statistics.json', {'nonzero_placements':len(owners),'zero_floor_cells':sum(c[0]==0 for c in m['cells']), 'unique_signed_ids':len(images),'counts':total,'frames':[frames[k]for k in sorted(frames)]})
    contract={'schema':'a13-ground-original-group-v1','status':'Source preparation only. No generated art, runtime edit, terrain replacement or GUI validation.',
        'source':{'map_source_sha256':m['sourceSha256'],'map_json_sha256':sha(mp),'manifest_sha256':sha(mf),
            'world_view_sha256':sha(P/'scripts/world_view.gd'),
            'floor_pack_source_sha256':{n:packs[n]['source_sha256']for n in ['Map/Res/FloorBig','Map/Res/FloorSmall']}},
        'coordinate_contract':{'logical_cell':[48,32],'map_order':'x * height + y','id_dispatch':'negative -> FloorBig abs(id); positive -> FloorSmall id; zero -> no owner',
            'floor_origin':'cell * [48,32] + crop; ignore frame.offset; no 32-original_height top adjustment',
            'draw_order':'all floors, stable map x-major order; then objects and actors',
            'camera_cell':camera,'viewport':viewport,'screen_origin':origin,'screen_origin_rule':'viewport*[.5,.54] - camera*[48,32]',
            'native_raster_note':'Native source diagnostic is integer world-space, NOT a pixel-exact fractional camera/GPU screenshot. View spans 768 continuous pixels; containing raster is 769 rows.'},
        'map_totals':{'placements':len(owners),'unique_signed_ids':len(images),'zero_floor_cells':sum(c[0]==0 for c in m['cells']),
            'FloorBig':{'placements':sum(o['signed_id']<0 for o in owners),'unique_ids':sum(k<0 for k in images)},
            'FloorSmall':{'placements':sum(o['signed_id']>0 for o in owners),'unique_ids':sum(k>0 for k in images)},'counts':total},
        'minimum_first_screen_group':{'definition':'Exact unique source IDs for every floor rectangle intersecting initial viewport, BEFORE object occlusion. Not a proof of minimum visible-after-occlusion assets or entire A13 coverage.',
            'unique_signed_ids':ids,'unique_count':len(ids),'placements':regions[0]['intersecting_placements'],
            'frames':[frames[k]for k in ids]},'regions':regions,
        'material_read':{'evidence':'Actual original RGBA mosaics and unique tile board; manual visual interpretation, not semantic tags from game.',
            'first_screen_grass':[-406,-398,-399,-407],
            'first_screen_tan_road_interior':[-594,-595,-586,-587],
            'first_screen_grass_road_edges_with_narrow_stone_border':[-577,-579,-580,-581,-588,-604,-608],
            'caution':'Tan road/soil texture is not wholesale silver brick. These floor images do not establish the temple object apron, object checker shadow, or building shape. Keep those contracts independent.',
            'global_dominant_ids':[{'id':-406,'read':'grass'},{'id':-402,'read':'tan earth/gravel'},{'id':-394,'read':'tan earth/gravel variant'},{'id':-395,'read':'tan earth/gravel variant'}]},
        'production_contract':{'phase':'Future art production requires separately approved style/scale. No art generation in this task.',
            'strategy':'Design and validate the assembled road-head region and shared grass/road edge network together, then register/cut to original owners. Do not generate 15 independent tiles with unconstrained borders.',
            'preserve':['Signed pack identities and original owner cell positions.','Actual original/crop/atlas dimensions; never resize FloorBig to the 48x32 logical grid.','Road outline, narrow stone-border continuity, grass/earth transitions and every recorded neighbor relationship.','RGBA transparency and original floor draw order; do not add checker shadow or painted building apron to floor art.'],
            'seam_acceptance':'Compare complete source and replacement mosaics at 1x and 2x and along every recorded touching edge. Edge colors need not be identical (natural texture); boundary geometry and texture continuity must be judged in combination. Test repeated -406 tiles and mixed corner/diagonal/straight road boundaries.',
            'limits':['15 IDs cover this stationary initial floor viewport only; camera movement requires additional IDs.','Road-head small board intentionally crops the continuing southwest road; full intersecting source tiles remain supplied.','Floor 0 is no draw, not necessarily a hole; a 96x64 tile commonly covers four 48x32 logical cells.','No gameplay, object-occlusion, shader, GPU or replacement seam validation performed.']}}
    save(OUT/'source-group-contract.json',contract)
    (OUT/'PLAN.md').write_text('''# A13 first-screen ground: source-only production plan

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
''')
    print(json.dumps({'map_placements':len(owners),'map_unique_ids':len(images),'regions':[{k:r[k]for k in ['id','intersecting_placements','unique_signed_ids','complete_tile_context_bounds_xyxy','source_alpha_extrema']}for r in regions]},ensure_ascii=False))

if __name__=='__main__':
    main()
