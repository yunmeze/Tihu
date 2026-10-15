"""Prepare one tree's seven identities; no runtime installation or image edits."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt
O=Path(__file__).resolve().parent;P=O.parents[1];D=P/'diagnostics/art_source/earth_first_tree_registration_v1';D.mkdir(parents=True,exist_ok=True);(O/'owners').mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rawp=P/'art_source/earth_first_tree_boundary_repair_v2/raw.png';raw=np.asarray(Image.open(rawp).convert('RGBA'));h,w=raw.shape[:2];assert sha(rawp)=='c639ad6e35e10f3a4c61d13a38258b2db1f077cea3f757ec8e064762601cc9e6'
sourcep=P/'art_source/earth_vegetation_input_plan_v1/source_contract.json';g=json.loads(sourcep.read_text())['groups'][0];owners=g['owners_in_draw_order'];assert [o['frame_index'] for o in owners]==[292,293,294,295,296,297,298]
scale=.25;origin=[2630.25,784.];yy,xx=np.indices((h,w));wx=origin[0]+(xx+.5)*scale;wy=origin[1]+(yy+.5)*scale
# Nearest original cropped rectangle, excluding verified original cast-only298.
# Inside any of292..297 preserves that source owner. Outside uses Euclidean distance;
# exact ties resolve original draw order. Never uses RGB/alpha to erase pixels.
best=np.full((h,w),np.inf);labels=np.zeros((h,w),np.uint8)
for i,o in enumerate(owners[:-1],1):
 x,y,bw,bh=o['world_rect'];dx=np.maximum(np.maximum(x-wx,0),wx-(x+bw));dy=np.maximum(np.maximum(y-wy,0),wy-(y+bh));d=dx*dx+dy*dy;take=d<best;labels[take]=i;best[take]=d[take]
assert np.all((labels>=1)&(labels<=6));Image.fromarray(labels).save(O/'owner-labels.png')
assembly=np.zeros_like(raw);coverage=np.zeros((h,w),np.uint8);records=[]
for i,o in enumerate(owners,1):
 m=labels==i;entry={k:o[k]for k in['pack','key','cell','source_cell','flag','layer','sort_y','stable_source_order','frame_index']};entry['scale']=scale
 if np.any(m):
  ys,xs=np.where(m);x,y,X,Y=int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1);crop=np.zeros((Y-y,X-x,4),np.uint8);local=m[y:Y,x:X];crop[local]=raw[y:Y,x:X][local]
  # Byte exact replacement preserves even fully transparent RGB, not alpha-over blend.
  assembly[y:Y,x:X][local]=crop[local];coverage[m]+=1
  entry.update({'raw_rect':[x,y,X-x,Y-y],'world_top_left':[origin[0]+x*scale,origin[1]+y*scale],'empty':False,'assigned_raw_pixel_count':int(m.sum()),'visible_pixel_count':int(np.count_nonzero(raw[:,:,3][m])),'nonzero_rgba_pixel_count':int(np.count_nonzero(np.any(raw[m]!=0,axis=1))),'alpha_gt127_count':int(np.count_nonzero(raw[:,:,3][m]>127)),'source_rectangle_expanded':True})
 else:
  crop=np.zeros((1,1,4),np.uint8);entry.update({'raw_rect':[0,0,0,0],'world_top_left':o['world_rect'][:2],'empty':True,'assigned_raw_pixel_count':0,'visible_pixel_count':0,'nonzero_rgba_pixel_count':0,'alpha_gt127_count':0,'empty_reason':'Original298 is cast-only. No new cast is made; identity remains to suppress original shadow, with no new crown allocation.'})
 fn=f'owners/owner-{o["frame_index"]}.png';Image.fromarray(crop).save(O/fn);entry.update({'texture':'res://'+str((O/fn).relative_to(P)),'texture_size':[crop.shape[1],crop.shape[0]],'sha256':sha(O/fn),'texture_sha256':sha(O/fn)});records.append(entry)
assert np.all(coverage==1);assert np.array_equal(raw,assembly)
# Validate current original map identities, and raw resources reconstructed from written slices.
mp=P/'data/maps/A13.json';m=json.loads(mp.read_text());reread=np.zeros_like(raw)
for i,o in enumerate(records,1):
 x,y=o['cell'];assert m['cells'][x*m['height']+y]==o['source_cell']
 if o['empty']:continue
 x,y,bw,bh=o['raw_rect'];c=np.asarray(Image.open(P/o['texture'][6:]).convert('RGBA'));mask=labels[y:y+bh,x:x+bw]==i;reread[y:y+bh,x:x+bw][mask]=c[mask]
assert np.array_equal(raw,reread)
alpha=raw[:,:,3];distance=distance_transform_edt(alpha<=16);low=(alpha>0)&(alpha<=16);far=low&(distance>16)
lowstats={'definition':'0<alpha<=16 and distance>16raw pixels (4logical units) from alpha>16 body; statistics only, none removed','all_low_alpha_count':int(low.sum()),'far_low_alpha_count':int(far.sum()),'far_alpha_max':int(alpha[far].max())if np.any(far)else 0,'by_owner':[{ 'key':o['key'],'far_low_alpha_count':int(np.count_nonzero(far&(labels==i)))}for i,o in enumerate(records,1)]}
reg={'schema':'earth-first-tree-candidate-registration-v1','status':'one-instance registered candidate for runner static/route/occlusion review, not final accepted','approval_scope':'Only Plant292–298 rooted57,34; small crown extension approved for review. No source flags/collision/order changed; no new tree shadow.','raw_texture':'res://'+str(rawp.relative_to(P)),'raw_sha256':sha(rawp),'source_contract_sha256':sha(sourcep),'source_map_sha256':sha(mp),'density':4,'whole_tree_registration':{'scale':scale,'world_top_left':origin,'rotation':0,'shear':0,'manual_root_raw_xy':[523,1224],'root_world_xy':[2761,1090],'manual_uncertainty_raw_px':8,'source_manual_uncertainty_logical_px':4},'suppress_source_keys':[o['key']for o in owners],'owners':records,'partition':{'method':'Nearest Euclidean original cropped source rectangle among292..297; retain owner inside rect; ties original draw order; applies every raw pixel including alpha0.298 explicit empty.','owner_labels':'res://'+str((O/'owner-labels.png').relative_to(P)),'owner_labels_sha256':sha(O/'owner-labels.png'),'no_pixels_dropped':True,'no_pixels_duplicated':True,'no_rgb_cleanup':True,'empty_owner_298':True},'shadow':'None. Suppress all seven original source sprites atomically, including original baked checker cast; do not generate a new environmental shadow.','low_alpha_statistics':lowstats}
(O/'registration.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n')
validation={'source_owner_count':7,'nonempty_owner_count':6,'empty_owner_count':1,'complete_raw_pixel_count':w*h,'coverage_min':int(coverage.min()),'coverage_max':int(coverage.max()),'reassembled_all_rgba_bytes_equal':True,'written_slice_reassembly_equal':True,'raw_rgba_sha256':hashlib.sha256(raw.tobytes()).hexdigest(),'reassembled_rgba_sha256':hashlib.sha256(reread.tobytes()).hexdigest(),'original_identities_match_current_map':True,'source_map_sha256':sha(mp),'raw_png_sha256':sha(rawp),'low_alpha':lowstats,'limits':['No runtime integration or route executed here','Expanded canvas is not new collision','Per-owner sorting still requires runner front/back review','Do not generalize this instance to other trees']}
(O/'validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n')
colors=np.array([[0,0,0],[240,160,50],[100,180,230],[210,100,200],[80,200,130],[240,220,70],[150,130,240]],np.uint8);rgb=colors[labels].copy();rgb[alpha==0]=[65,65,65];Image.fromarray(rgb).save(D/'owner_partition_raw.png')
files=['README.md','build_registration.py','registration.json','validation.json','owner-labels.png']+[f'owners/owner-{i}.png'for i in range(292,299)]
(O/'ARCHIVE_SHA256.json').write_text(json.dumps({'diagnostics_excluded':True,'files':[{'path':n,'sha256':sha(O/n),'bytes':(O/n).stat().st_size}for n in files]},indent=2)+'\n')
print(json.dumps({'owners':len(records),'raw_pixel_count':w*h,'equal':True,'lowalpha':lowstats,'slices':[(o['frame_index'],o['texture_size'],o['visible_pixel_count'])for o in records]},indent=2))
