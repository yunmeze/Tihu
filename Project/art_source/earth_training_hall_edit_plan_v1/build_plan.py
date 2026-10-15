"""Technical plan only: source flags, real material samples and target marks.
No image synthesis, no candidate edits/warps, no runtime writes.
"""
from pathlib import Path
import hashlib
import json
from collections import deque

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
SRC = HERE.parent / 'earth_training_hall_source_v1'
CAND = HERE.parent / 'earth_training_hall_candidate_v1'
RAW_SHA = 'a81ff1d6ac235d80e5d948a804c2959b1b9b3babaed054897d396620b4bf9033'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert sha(CAND / 'raw.png') == RAW_SHA
    raw = Image.open(CAND / 'raw.png').convert('RGBA')
    source = Image.open(SRC / 'source-full.png').convert('RGBA')
    original = json.loads((SRC / 'input-contract.json').read_text())
    initial = json.loads((CAND / 'measurements.json').read_text())
    ref = initial['common_scale_translation_diagnostic']
    d = ref['density_raw_px_per_source_unit']
    t = np.array(ref['raw_translation'])
    m = json.loads((PROJECT / 'data/maps/A13.json').read_text())
    h = m['height']
    to_raw = lambda p: (d * np.array(p, dtype=float) + t).tolist()
    to_source = lambda p: ((np.array(p, dtype=float) - t) / d).tolist()
    origin = np.array([2948, 642])
    gray = Image.new('RGBA', raw.size, (90, 100, 105, 255))
    gray.alpha_composite(raw)
    source_bg = Image.new('RGBA', source.size, (90, 100, 105, 255))
    source_bg.alpha_composite(source)

    def can(x, y):
        return 0 <= x < m['width'] and 0 <= y < h and m['cells'][x * h + y][1] not in [-1, -2, -3]

    def route(target):
        start = (61, 39)
        queue = deque([start])
        parents = {start: None}
        while queue:
            p = queue.popleft()
            if p == target:
                result = []
                while p is not None:
                    result.append(list(p))
                    p = parents[p]
                return result[::-1]
            for dx, dy in [(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1)]:
                q = (p[0] + dx, p[1] + dy)
                if q in parents or not can(*q):
                    continue
                if dx and dy and (not can(p[0] + dx, p[1]) or not can(p[0], p[1] + dy)):
                    continue
                parents[q] = p
                queue.append(q)
        return None

    target_defs = [
        ('S0', [258,543], [383,884], 5, 8, 'mandatory left lower tread correction'),
        ('S1', [231,455], [353,748], 5, 8, 'preserve existing upper-left mouth within source uncertainty'),
        ('S2', [596,578], [1098,1008], 5, 8, 'preserve existing right lower tread within source uncertainty'),
        ('S3', [622,489], [1145,851], 5, 8, 'mandatory right upper tread/landing junction correction'),
        ('P0', [449,600], [797,1047], 6, 8, 'shared upper plinth/platform outside front corner; preserve, no forced movement'),
    ]
    targets = []
    for key, sp, current, su, ru, instruction in target_defs:
        target = to_raw(sp)
        delta = (np.array(target) - np.array(current)).tolist()
        targets.append({'id':key,'source_xy':sp,'current_raw_xy':current,'target_raw_xy':target,'delta_raw_xy':delta,'source_read_uncertainty_px':su,'current_raw_read_uncertainty_px':ru,'combined_conservative_budget_raw_px':su*d+ru,'instruction':instruction})

    # Source stair connected material, including narrow risers; all corners approximate.
    # Not a segmentation mask or invented quad to fill gameplay cells.
    guides = {
        'left_stair': {'source_visible_support_boundary': [[231,455],[296,495],[262,546],[185,503]], 'current_raw_boundary': [[353,748],[477,817],[396,899],[277,824]], 'source_boundary_uncertainty_px':6, 'current_boundary_uncertainty_raw_px':8, 'edit_roi_raw_xyxy':[235,700,530,975]},
        'right_stair': {'source_visible_support_boundary': [[560,532],[622,489],[671,538],[596,578]], 'current_raw_boundary': [[1012,912],[1145,851],[1233,940],[1098,1008]], 'source_boundary_uncertainty_px':6, 'current_boundary_uncertainty_raw_px':8, 'edit_roi_raw_xyxy':[980,795,1290,1040]},
    }
    for g in guides.values():
        g['target_raw_boundary'] = [to_raw(p) for p in g['source_visible_support_boundary']]
        g['corner_deltas_raw'] = [(np.array(q)-np.array(p)).tolist() for p,q in zip(g['current_raw_boundary'],g['target_raw_boundary'])]
        g['interpretation'] = 'Manual visible stair support edge guide, includes narrow risers; finite uncertainty. Do not fill a solid quadrilateral or stretch these pixels. Repaint real steps/cheeks through approved image editing.'

    # Manual source material classes after viewing both original and candidate crops.
    material = {
        (66,34): [('support','tread'),('support','tread')],
        (65,35): [('uncertain_cheek_edge','transparent'),('support','transparent')],
        (66,35): [('support','tread'),('support','tread')],
        (73,35): [('support','landing'),('support','landing')],
        (65,36): [('source_grass_apron','transparent'),('source_grass_apron','transparent')],
        (66,36): [('support','near_transparent'),('support','solid_side_cheek')],
        (73,36): [('support','tread'),('support','tread')],
        (74,36): [('support','tread'),('support','tread')],
        (66,37): [('source_grass_apron','transparent'),('source_grass_apron','transparent')],
        (74,37): [('support','lower_tread'),('source_grass_apron','transparent')],
        (75,37): [('source_grass_apron','transparent'),('source_grass_apron','transparent')],
        (74,38): [('source_grass_apron','transparent'),('source_grass_apron','transparent')],
    }
    feet = [[17,17],[31,22]]
    rows = []
    feet_board = gray.convert('RGB')
    fd = ImageDraw.Draw(feet_board)
    fd.text((10,10),'SOURCE FLAG + FOOT PROBES ON UNCHANGED RAW; NOT A COLLISION MASK', fill='white')
    sheet = Image.new('RGB',(600,12*126),(65,75,80))
    sd = ImageDraw.Draw(sheet)
    for i,o in enumerate(original['geometry']['source_support_owners']):
        x,y = o['cell']
        assert m['cells'][x*h+y][1] == 1
        base = np.array([x*48,y*32]) - origin
        p0,p1=to_raw(base),to_raw(base+[48,32])
        fd.rectangle((*p0,*p1),outline=(80,155,165),width=1)
        fd.text((p0[0]+2,p0[1]+2),f'{x},{y}',fill='white')
        row = {'owner':o['key'],'cell':[x,y],'source_flag':1,'source_layer':0,'static_no_corner_cut_route':route((x,y)),'samples':[]}
        box = [*(base+[-6,2]),*(base+[48,37])]
        raw_box = [*to_raw(box[:2]),*to_raw(box[2:])]
        old_crop=source_bg.crop(tuple(box)).resize((194,100),Image.Resampling.NEAREST).convert('RGB')
        raw_crop=gray.crop(tuple(round(v) for v in raw_box)).resize((194,100),Image.Resampling.NEAREST).convert('RGB')
        sheet.paste(old_crop,(90,i*126+24));sheet.paste(raw_crop,(350,i*126+24))
        sd.text((3,i*126+3),f'cell {x},{y} / frame {o["owner"] if "owner" in o else o["key"].split(":")[1].split("@")[0]}',fill='white')
        sd.text((190,i*126+3),'SOURCE',fill='white');sd.text((350,i*126+3),'FIXED-REFERENCE CANDIDATE',fill='white')
        for j,rel in enumerate(feet):
            sp=(base+rel).tolist();rp=to_raw(sp);ix,iy=map(round,rp)
            alpha=raw.getpixel((ix,iy))[3] if 0<=ix<raw.width and 0<=iy<raw.height else None
            old_class,new_class=material[(x,y)][j]
            color='orange' if old_class=='support' and new_class in ['transparent','near_transparent','solid_side_cheek'] else 'cyan' if old_class=='support' else 'yellow' if old_class=='uncertain_cheek_edge' else (125,210,130)
            fd.ellipse((rp[0]-4,rp[1]-4,rp[0]+4,rp[1]+4),outline=color,width=2)
            row['samples'].append({'phase17_foot_index':j,'source_canvas_xy':sp,'candidate_raw_xy':rp,'candidate_alpha':alpha,'source_material_read':old_class,'candidate_material_read':new_class,'must_restore_support':old_class=='support','manual_sample_uncertainty_source_px':2,'meaning':'Stationary source South phase17 toe/contact read; not all moving phases or full boot polygons.'})
            qx=(sp[0]-box[0])/(box[2]-box[0])*194;qy=(sp[1]-box[1])/(box[3]-box[1])*100
            for off in [90,350]:sd.ellipse((off+qx-3,i*126+24+qy-3,off+qx+3,i*126+24+qy+3),outline=color,width=2)
        rows.append(row)
    feet_board.save(HERE/'raw-source-foot-probes.png')
    sheet.save(HERE/'source-candidate-support-feet.png')

    # Front corner structure extends through already blocked source cells, but we also
    # inspect adjacent reachable foot samples; alpha overlap alone is not a collision test.
    front_points = {'old_C0_outer_diagonal_foot':[836,996], 'visible_vertical_core_base':[764,982], 'shared_outer_platform_corner_P0':[797,1047]}
    front=[]
    for label,rp in front_points.items():
        sp=to_source(rp);world=(np.array(sp)+origin).tolist();cell=[int(world[0]//48),int(world[1]//32)]
        front.append({'label':label,'raw_xy':rp,'mapped_world_xy':world,'screen_projected_cell':cell,'source_flag_at_projected_cell':m['cells'][cell[0]*h+cell[1]][1],'warning':'Screen projection only; tall pixels can overlap other cells. Not sufficient collision evidence by itself.'})
    adjacent=[]
    for y in range(37,42):
        for x in range(67,74):
            if not can(x,y):continue
            base=np.array([x*48,y*32])-origin
            samples=[]
            for rel in feet:
                rp=to_raw(base+rel);ix,iy=map(round,rp)
                samples.append({'raw_xy':rp,'alpha':raw.getpixel((ix,iy))[3] if 0<=ix<raw.width and 0<=iy<raw.height else 0,'outside_canvas':not(0<=ix<raw.width and 0<=iy<raw.height)})
            adjacent.append({'cell':[x,y],'source_flag':m['cells'][x*h+y][1],'samples':samples,'static_route_exists':route((x,y)) is not None})

    target_board=gray.convert('RGB');bd=ImageDraw.Draw(target_board)
    bd.text((10,10),'EDIT PLAN ONLY | UNCHANGED RAW COORDINATES | cyan=current, magenta=target',fill='white')
    for name,g in guides.items():
        oldpoly=[tuple(p) for p in g['current_raw_boundary']];newpoly=[tuple(p) for p in g['target_raw_boundary']]
        bd.line(oldpoly+[oldpoly[0]],fill='cyan',width=2);bd.line(newpoly+[newpoly[0]],fill='magenta',width=2)
    for p in targets:
        x,y=p['current_raw_xy'];u,v=p['target_raw_xy'];color='magenta' if p['id'] in ['S0','S3'] else 'yellow'
        bd.ellipse((x-5,y-5,x+5,y+5),outline='cyan',width=2)
        bd.line((x,y,u,v),fill=color,width=2);bd.line((u-7,v,u+7,v),fill=color,width=2);bd.line((u,v-7,u,v+7),fill=color,width=2)
        bd.text((u+10,v-8),p['id'],fill=color)
    bd.ellipse((831,991,841,1001),outline=(170,170,170),width=2)
    bd.text((850,990),'old C0: NOT homologous',fill='white')
    target_board.save(HERE/'raw-edit-targets.png')

    corners=Image.new('RGB',(900,370),(65,75,80));cd=ImageDraw.Draw(corners)
    panels=[('SOURCE C0 vertical pillar / P0 outer platform',source_bg,(397,523,475,625),[(437,553,'C0'),(449,600,'P0')]),('NEW core, diagonal foot, and P0',gray,(718,930,880,1075),[(764,982,'core'),(836,996,'diagonal'),(797,1047,'P0')])]
    for n,(label,im,box,pts) in enumerate(panels):
        ww,hh=box[2]-box[0],box[3]-box[1];factor=min(420/ww,325/hh);sz=(round(ww*factor),round(hh*factor));crop=im.crop(box).resize(sz,Image.Resampling.NEAREST).convert('RGB');ox=n*450+10;oy=36;corners.paste(crop,(ox,oy));cd.text((ox,10),label,fill='white')
        for x,y,label2 in pts:
            u=ox+(x-box[0])*factor;v=oy+(y-box[1])*factor;cd.ellipse((u-4,v-4,u+4,v+4),outline='cyan',width=2);cd.text((u+6,v-8),label2,fill='white')
    corners.save(HERE/'front-corner-semantic-review.png')

    # Additional sampled full transverse tread boundaries, not only S point pairs.
    failures=[{'cell':r['cell'],'foot':q['phase17_foot_index'],'raw_xy':q['candidate_raw_xy'],'candidate_material':q['candidate_material_read']} for r in rows for q in r['samples'] if q['must_restore_support'] and q['candidate_material_read'] in ['transparent','near_transparent','solid_side_cheek']]
    report={
        'status':'LOCAL STRUCTURE EDIT PLAN ONLY; awaits approval. No image generation/edit/warp/runtime change.',
        'frozen_raw_sha256':RAW_SHA,'raw_size':list(raw.size),
        'reference':{'kind':'Freeze previous common scale+translation solely as an editing reference. It is NOT approved runtime registration. No refit to make new measurements pass.','density':d,'raw_translation':t.tolist(),'source_canvas_origin_world':origin.tolist(),'why_usable_for_edit_plan':'Existing S1 and S2 fall inside conservative source+candidate read budgets; preserve those mouths/bottoms and correct deficient stair geometry. A valid remeasurement is mandatory after editing.'},
        'C0_semantic_correction':{'old_source':[437,553],'old_candidate':[836,996],'finding':'The source point is a vertical column face bottom; the previous candidate point is an outboard diagonal buttress toe. They are not strict homologues. Preserve old failed-fit files as historical evidence but do not force that new toe onto old C0.','new_vertical_core_sample':[764,982],'core_uncertainty_raw_px':8,'core_status':'Visible vertical facade termination, useful context but not established as exact shared pillar axis. Do not force it to old C0.','replacement_control':'P0: continuous upper platform/plinth OUTSIDE front corner, original (449,600) +/-6 and new (797,1047) +/-8 raw. These identify the actual common platform perimeter, not a decorative toe.','P0_action':'Retain within uncertainty; no front-corner redesign required merely to reduce C0 residual. Retain blocked-area containment and inspect adjacent reachable feet.'},
        'targets':targets,'stair_boundary_guides':guides,
        'foot_evidence':{'phase':17,'body_offset':[7,-47],'local_boot_samples':[[10,64],[24,69]],'relative_to_actor_origin':feet,'source_manifest_sha256':sha(PROJECT/'data/hero/movement.json'),'limitation':'Two stationary South-phase17 samples only. Original map flags and source owner/collision semantics remain unchanged. No full movement or native depth pass claimed.'},
        'support_owner_rows':rows,'source_support_count':12,'all_source_support_cells_flag1':True,'all_source_support_cells_static_route_found':all(r['static_no_corner_cut_route'] for r in rows),
        'clear_support_samples_currently_failing':failures,
        'front_projected_samples':front,'front_adjacent_reachable_samples':adjacent,
        'important_limits':['12 layer0 owner cells are NOT 12 solid replacement floor rectangles. Several source samples are grass/apron, so candidate transparency there is correct; do not fill them.','The source (65,35) first toe is a cheek/tread boundary with uncertainty. Its second toe is clear supporting stair material and currently falls into alpha=0; left flight needs real width as well as depth.','Both (66,36) source toes need step material; candidate first is near-transparent and second hits a solid side cheek. This is independent evidence of a deficient left staircase.','One (74,37) source sample is lower tread and the other source grass. Preserve that distinction; do not broaden right stairs into grass just to cover all markers.','The raw alpha of a sampled boot says only material presence, not surface height or correct depth; source/new material inspection and later native route/depth validation are required.','Blocked front-projected cells do not authorize ignoring physical overlap. Adjacent reachable foot probes are recorded separately, and finite probes do not prove the entire silhouette harmless.'],
        'planned_edit':'One localized generated structural edit of both complete staircase assemblies including appropriate tread/riser/side-cheek contours and immediately adjoining landing seams. Preserve full raw canvas/camera, roof, doors, main facade/piers, shared platform outer front corner, material/light, transparency and no ground cast. No pixel warp or global redraw.',
        'parent_review_files':['raw-edit-targets.png','front-corner-semantic-review.png','source-candidate-support-feet.png','raw-source-foot-probes.png'],
        'reproduce':'python Project/art_source/earth_training_hall_edit_plan_v1/build_plan.py'
    }
    report['proposal']='EDIT_PROPOSAL.md'
    report['prompt_draft']='edit-prompt-draft.txt'
    report['prompt_draft_sha256']=sha(HERE/'edit-prompt-draft.txt')
    (HERE/'edit-plan.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    assert sha(CAND/'raw.png')==RAW_SHA
    print(json.dumps({'targets':[{k:p[k] for k in ['id','target_raw_xy','delta_raw_xy']} for p in targets],'clear_support_failures':failures,'all12_static_routes':report['all_source_support_cells_static_route_found'],'front_adjacent_reachable_nonzero_alpha':sum(q['alpha']>0 for r in adjacent for q in r['samples']),'raw_unchanged':True}))


if __name__=='__main__':
    main()
