#!/usr/bin/env python3
"""Read-only source evidence: exact NPC pixels, registration, masks and metrics.
No art generation, Godot, runtime changes or Git mutation.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def dump(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2)+"\n")


def bbox(mask):
    y,x=np.where(mask)
    return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)] if len(x) else None


def shifted(box,offset):
    return [box[0]+offset[0],box[1]+offset[1],box[2]+offset[0],box[3]+offset[1]]


def runs(xs):
    out=[]
    for x in xs:
        x=int(x)
        if out and out[-1][1]==x: out[-1][1]=x+1
        else: out.append([x,x+1])
    return out


def edge(mask):
    inside=mask.copy()
    padded=np.pad(mask,1)
    for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
        inside &= padded[1+dy:1+dy+mask.shape[0],1+dx:1+dx+mask.shape[1]]
    return mask & ~inside


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo',type=Path,required=True)
    ap.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1])
    a=ap.parse_args();r=a.repo.resolve();o=a.out.resolve();p=r/'Project'
    if o==r or r in o.parents: raise ValueError('Output must remain outside the source repository')
    deps=['原版游戏/Data/Npc.lpRes','原版游戏/Data/Map/A00.lpMap',
          'Project/tools/lp_original.py','Project/data/maps/A00.json','Project/data/maps/A00-entities.json',
          'Project/assets/original/maps/A00/manifest.json','Project/assets/original/maps/A00/sprites/Npc/1.png']
    before={v:sha(r/v) for v in deps}
    sys.path.insert(0,str(p/'tools'))
    from lp_original import read_pack,decode_frame,Reader
    mapdata=json.loads((p/'data/maps/A00.json').read_text())
    entity=json.loads((p/'data/maps/A00-entities.json').read_text())['npcs'][1]
    native_map=(r/'原版游戏/Data/Map/A00.lpMap').read_bytes()
    reader=Reader(native_map,3,entity['source_offset'])
    npc=dict(zip(['x','y','appearance','direction'],[reader.short() for _ in range(4)]))
    npc.update(name=reader.string(),script=reader.string())
    assert npc==mapdata['npcs'][1] and reader.pos==entity['source_end']
    assert all(npc[k]==entity[k] for k in npc)
    pack=json.loads((p/'assets/original/maps/A00/manifest.json').read_text())['packs']['Npc']
    native,records,animated,key=read_pack(r/'原版游戏/Data/Npc.lpRes')
    assert before['原版游戏/Data/Npc.lpRes']==pack['source_sha256']
    assert before['原版游戏/Data/Map/A00.lpMap']==mapdata['sourceSha256']
    ids=[1+npc['appearance']*12+npc['direction']*4+i for i in range(4)]
    assert ids==[125,126,127,128]
    root=(12,56); canvas=(96,96); world=(3600,1728)
    frames=[];aligned=[];body_masks=[];shadow_masks=[];atlas={}
    for idx in ids:
        im,meta=decode_frame(native,records[idx],'Npc',animated)
        m=pack['frames'][str(idx)];page=p/pack['pages'][m['page']]['file'].removeprefix('res://')
        if page not in atlas:
            assert sha(page)==pack['pages'][m['page']]['sha256'];atlas[page]=Image.open(page).convert('RGBA')
        x,y,w,h=m['rect'];cx,cy=m['crop']
        assert atlas[page].crop((x,y,x+w,y+h)).tobytes()==im.crop((cx,cy,cx+w,cy+h)).tobytes()
        assert meta['rgba_sha256']==m['rgba_sha256'] and meta['offset']==m['offset']
        target=o/f'source/frame-{idx}.png';target.parent.mkdir(parents=True,exist_ok=True);im.save(target)
        ar=np.array(im);vis=ar[:,:,3]>0;shadow=vis&np.all(ar[:,:,:3]==[16,8,8],axis=2);body=vis&~shadow
        offset=meta['offset'];reg=Image.new('RGBA',canvas);reg.paste(im,(root[0]+offset[0],root[1]+offset[1]));ra=np.array(reg)
        aligned.append(ra);rs=(ra[:,:,3]>0)&np.all(ra[:,:,:3]==[16,8,8],axis=2);rb=(ra[:,:,3]>0)&~rs
        body_masks.append(rb);shadow_masks.append(rs)
        features={'crown_top_row_center':[float((np.flatnonzero(body[0])+offset[0]).mean()),-47],
                  'screen_left_foot_material_lower_row_center':[15,19],
                  'screen_right_foot_material_lower_row_center':[32,19]}
        for name,(x,y,right,bottom) in [('screen_left_hand_lower_edge',(0,26,7,40)),('screen_right_hand_lower_edge',(40,26,50,40))]:
            ys,xs=np.where(body[y:bottom,x:right]);bottom_y=int(ys.max())+y
            xx=np.flatnonzero(body[bottom_y,x:right])+x+offset[0]
            features[name]=[float(xx.mean()),bottom_y+offset[1]]
        foot_runs=runs(np.flatnonzero(body[66])+offset[0]);assert foot_runs==[[13,18],[30,35]]
        sy,sx=np.where(shadow)
        frame={'source_id':idx,'phase':idx-125,'native':meta,'atlas':m,
               'source_png':f'source/frame-{idx}.png','source_png_sha256':sha(target),
               'alpha_bbox_local':bbox(vis),'body_palette_proxy_bbox_local':bbox(body),
               'body_palette_proxy_bbox_world_relative':shifted(bbox(body),offset),
               'body_palette_proxy_bbox_world':shifted(shifted(bbox(body),offset),world),
               'visible_pixels':int(vis.sum()),'body_proxy_pixels':int(body.sum()),'shadow_palette_pixels':int(shadow.sum()),
               'shadow_parity_local':sorted(set(((sx+sy)%2).tolist())),
               'source_image_top_left_world':[world[0]+offset[0],world[1]+offset[1]],
               'feature_extrema_world_relative':features,
               'foot_material_lower_row':{'relative_y':19,'x_runs_half_open':foot_runs,'bottom_edge_relative_y':20}}
        frames.append(frame)
        rows=[{'relative_y':yy+offset[1],'body_proxy_runs':runs(np.flatnonzero(body[yy])+offset[0]),
               'original_alpha_runs':runs(np.flatnonzero(vis[yy])+offset[0])} for yy in range(im.height)]
        dump(o/f'evidence/row-runs-{idx}.json',rows)
        dump(o/f'evidence/contour-{idx}.json',{'kind':'unordered 4-connected boundary pixel set; analysis proxy only',
             'points_world_relative_xy':[[int(xx+offset[0]),int(yy+offset[1])] for yy,xx in np.argwhere(edge(body))]})
    diffs=[]
    rois={'head':[16,-47,34,-30],'left_arm_hand':[-2,-34,14,-8],
          'right_arm_hand':[34,-34,49,-7],'torso':[10,-38,39,1],
          'lower_coat':[6,-2,44,18],'foot_material':[11,17,37,20]}
    for i,j in itertools.combinations(range(4),2):
        visible=(aligned[i][:,:,3]>0)|(aligned[j][:,:,3]>0)
        changed=np.any(aligned[i]!=aligned[j],axis=2)&visible
        xor=body_masks[i]^body_masks[j];common=body_masks[i]&body_masks[j]
        rgb=np.any(aligned[i][:,:,:3]!=aligned[j][:,:,:3],axis=2)&common
        regions={}
        for name,(x,y,right,bottom) in rois.items():
            sl=(slice(y+root[1],bottom+root[1]),slice(x+root[0],right+root[0]))
            regions[name]={'silhouette_xor_pixels':int(xor[sl].sum()),'common_body_rgb_changed_pixels':int(rgb[sl].sum())}
        diffs.append({'a':ids[i],'b':ids[j],'visible_rgba_changed_pixels':int(changed.sum()),
                      'body_proxy_silhouette_xor_pixels':int(xor.sum()),'body_proxy_iou':float(common.sum()/(body_masks[i]|body_masks[j]).sum()),
                      'common_body_rgb_changed_pixels':int(rgb.sum()),'per_region':regions})
    dump(o/'evidence/pairwise-differences.json',diffs)
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
    scale=5;pw=96*scale
    board=Image.new('RGB',(pw*4,96*scale+62),(45,51,57));d=ImageDraw.Draw(board)
    contourboard=board.copy();cd=ImageDraw.Draw(contourboard)
    for n,idx in enumerate(ids):
        bg=Image.new('RGBA',canvas,(103,110,118,255));bg.alpha_composite(Image.fromarray(aligned[n]))
        board.paste(bg.convert('RGB').resize((pw,480),Image.Resampling.NEAREST),(n*pw,62))
        d.text((n*pw+8,7),f'Source {idx} offset {frames[n]["native"]["offset"]}',font=font,fill='white')
        d.text((n*pw+8,30),'cyan + cell origin; yellow foot material',font=font,fill='white')
        ox=n*pw+root[0]*scale;oy=62+root[1]*scale
        d.line((ox-8,oy,ox+8,oy),fill=(0,255,255),width=2);d.line((ox,oy-8,ox,oy+8),fill=(0,255,255),width=2)
        for x in [15,32]:
            xx=n*pw+(root[0]+x)*scale;yy=62+(root[1]+19)*scale
            d.rectangle((xx-4,yy-4,xx+4,yy+4),outline=(255,230,40),width=2)
        layer=np.zeros((96,96,3),dtype=np.uint8)+[55,61,67]
        layer[body_masks[n]]=[180,190,198];layer[edge(body_masks[n])]=[245,225,75];layer[shadow_masks[n]]=[160,100,220]
        contourboard.paste(Image.fromarray(layer.astype('uint8')).resize((pw,480),Image.Resampling.NEAREST),(n*pw,62))
        cd.text((n*pw+8,7),f'Source {idx} body / contour / checker',font=font,fill='white')
        cd.text((n*pw+8,30),'PALETTE PROXY, not production segmentation',font=font,fill='white')
    board.save(o/'evidence/source-contactsheet-registered-5x.png')
    contourboard.save(o/'evidence/contour-shadow-contactsheet-5x.png')
    contract={'schema':'chief-source-contract-v2','status':'SOURCE_EVIDENCE_ONLY; no accepted base or warp',
              'identity':{'map':'A00','name':npc['name'],'source_npc_zero_based_index':1,'cell':[75,54],
                          'appearance':10,'direction_slot':1,'layer':1,'sort_y':54,'stable_source_order':22501,
                          'native_record_offset':entity['source_offset'],'native_record_end':entity['source_end'],
                          'script_utf8_sha256':hashlib.sha256(npc['script'].encode()).hexdigest()},
              'coordinates':{'unit':'logical pixel','axes':'x right, y down','bbox_and_runs':'half-open right/bottom',
                             'tile_size':[48,32],'cell_origin_world':[3600,1728],'cell_origin_is_foot_anchor':False,
                             'world_pixel_formula':'cell*(48,32) + source_frame.offset + source_local_pixel',
                             'body_proxy_height':67,'raw_size':[68,70],'common_analysis_canvas':[96,96],'root':[12,56],
                             'visible_foot_material_centers_world':[[3615,1747],[3632,1747]],'foot_material_bottom_edge_world_y':1748},
              'animation':{'index_formula':'1 + appearance*12 + direction_slot*4 + phase_0_to_3','phase_order':ids,
                           'current_project_ticks_per_phase':17,'current_project_reference_fps_field':50,
                           'native_exe_50Hz_verified':False,'timing_caution':'17 ticks / 50Hz is existing project/reference evidence, not native EXE timing proof'},
              'palette_analysis':{'shadow_rgb':[16,8,8],'body_proxy':'alpha>0 and RGB!=(16,8,8)',
                                  'semantic_segmentation_approved':False,'warning':'Near-foot dark material/contact meaning is not fully established. Exact source pixels remain unchanged.'},
              'landmark_caution':'Surface extrema are visible material locations, not known skeleton joints, toe anatomy, support-foot identity or a proved 3D ground plane.',
              'frames':frames,'pairwise_differences':'evidence/pairwise-differences.json','observation_rois':rois,
              'input_sha256_pins':before,'generation_inputs_exact_package':'../chief-source-inputs-v2',
              'art_state':{'v1_candidate_accepted':False,'v2_candidate_accepted':False,'old_accepted_chief_recovered':False,
                           'new_art_generated':False,'warp_performed':False,'Godot_run':False,'main_repo_written':False,'Git_pushed':False},
              'next_stage':'Approve one new base in source125 geometry first. Only then plan same-base four-phase 2D warp. Do not mirror, duplicate125 as128, normalize per-frame bbox or generate four independent identities.'}
    dump(o/'source-contract.json',contract)
    assert before=={v:sha(r/v) for v in deps}
    print(json.dumps({'source_frames':ids,'native_and_atlas_rgba_match':True,'source_input_hashes_unchanged':True,
                      'out':str(o),'pairwise_xor':[v['body_proxy_silhouette_xor_pixels'] for v in diffs]}))


if __name__=='__main__': main()
