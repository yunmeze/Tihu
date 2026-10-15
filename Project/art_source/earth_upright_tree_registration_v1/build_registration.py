from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt
O=Path(__file__).resolve().parent;P=O.parents[1];D=P/'diagnostics/art_source/earth_upright_tree_registration_v1';D.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
R=P/'art_source/earth_upright_tree_candidate_v1/raw.png';raw=np.asarray(Image.open(R).convert('RGBA'));h,w=raw.shape[:2];assert (w,h)==(1162,1353)
planpath=P/'art_source/earth_upright_tree_input_plan_v1/INPUT_PLAN.json';plan=json.loads(planpath.read_text());left,bottom=plan['instances'];owners=bottom['owners_in_draw_order'];scale=1/4.5;origin=[2964-560*scale,1646-1329*scale];leftorigin=[origin[0]-528,origin[1]-320];yy,xx=np.indices((h,w));wx=origin[0]+(xx+.5)*scale;wy=origin[1]+(yy+.5)*scale
best=np.full((h,w),np.inf);labels=np.zeros((h,w),np.uint8);source_union=np.zeros((h,w),bool)
for i,o in enumerate(owners,1):
 x,y,bw,bh=o['world_rect'];inside=(wx>=x)&(wx<x+bw)&(wy>=y)&(wy<y+bh);source_union|=inside
 if o['frame_index']==304:continue
 dx=np.maximum(np.maximum(x-wx,0),wx-x-bw);dy=np.maximum(np.maximum(y-wy,0),wy-y-bh);d=dx*dx+dy*dy;take=d<best;labels[take]=i;best[take]=d[take]
assert np.all((labels>=1)&(labels<=5));Image.fromarray(labels).save(O/'owner-labels.png')
assembly=np.zeros_like(raw);coverage=np.zeros((h,w),np.uint8);texture_records=[]
for i,o in enumerate(owners,1):
 mask=labels==i;a=np.zeros_like(raw);a[mask]=raw[mask];assembly[mask]=a[mask];coverage[mask]+=1;fn=O/f'owners/owner-{o["frame_index"]}.png';Image.fromarray(a).save(fn)
 texture_records.append({'texture':'res://'+str(fn.relative_to(P)),'texture_size':[w,h],'raw_rect':[0,0,w,h],'sha256':sha(fn),'texture_sha256':sha(fn),'empty':o['frame_index']==304,'visible_pixel_count':int(np.count_nonzero(raw[:,:,3][mask])),'nonzero_rgba_pixel_count':int(np.count_nonzero(np.any(raw[mask]!=0,axis=1))),'assigned_raw_pixel_count':int(mask.sum())})
assert np.all(coverage==1)and np.array_equal(raw,assembly)
rebuilt=np.zeros_like(raw)
for i,t in enumerate(texture_records,1):
 a=np.asarray(Image.open(P/t['texture'][6:]));mask=labels==i;rebuilt[mask]=a[mask]
assert np.array_equal(raw,rebuilt)
mp=P/'data/maps/A13.json';m=json.loads(mp.read_text());regs=[]
for g,org,short in[(left,leftorigin,'left_50_41'),(bottom,origin,'bottom_61_51')]:
 entries=[]
 for o,t in zip(g['owners_in_draw_order'],texture_records):
  e={k:o[k]for k in['pack','key','cell','source_cell','flag','layer','sort_y','stable_source_order','frame_index']};e.update(t);e.update({'world_top_left':org,'scale':scale})
  if e['empty']:e['empty_reason']='Source304cast-only; explicit empty identity suppresses old cast. No new foliage allocated.'
  x,y=e['cell'];assert m['cells'][x*m['height']+y]==e['source_cell'];entries.append(e)
 reg={'schema':'earth-upright-tree-candidate-registration-v1','status':'static fullcanvas candidate for this instance independent native GPU/route review only','instance':short,'scope':'Only50,41 and61,51 family instances authorized; no all-map reuse','raw_texture':'res://'+str(R.relative_to(P)),'raw_sha256':sha(R),'source_contract_sha256':sha(planpath),'source_map_sha256':sha(mp),'density':4.5,'whole_tree_registration':{'scale':scale,'world_top_left':org,'rotation':0,'shear':0,'root_raw_xy':[560,1329],'root_world_xy':g['anchor']['world_xy'],'manual_root_uncertainty_raw_px':9,'source_root_uncertainty_logical_px':4},'suppress_source_keys':[e['key']for e in entries],'owners':entries,'partition':{'method':'Nearest original299..303cropped rectangle at fixed world coordinates, ties draw order.304empty. Same shared owner textures for both exact translation instances.','owner_labels':'res://'+str((O/'owner-labels.png').relative_to(P)),'owner_labels_sha256':sha(O/'owner-labels.png'),'rgba_reassembly_exact':True},'shadow':'None; suppress full6source identities atomically, including old baked cast.','registration_unit':'Each6ownerinstance validated atomically, failures revert that complete source group.'}
 f=O/f'registration_{short}.json';f.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n');regs.append({'path':str(f.relative_to(P)),'sha256':sha(f),'instance':short})
alpha=raw[:,:,3];outside=(alpha>127)&~source_union;ys,xs=np.where(outside)
# Wood-foot continuation criterion remains original302domain; do not collapse root to299.
foot=(wx>=2839+104)&(wx<2839+152)&(wy>=1352+278)&(wy<1352+298)&(alpha>127)
footstats={str(o['frame_index']):int(np.count_nonzero(foot&(labels==i)))for i,o in enumerate(owners,1)}
far=(alpha>0)&(alpha<=16)&(distance_transform_edt(alpha<=16)>18)
validation={'owner_count_per_instance':6,'instances':2,'shared_png_count':6,'nonempty_png_count':5,'empty304':True,'complete_raw_pixel_count':w*h,'coverage_min':int(coverage.min()),'coverage_max':int(coverage.max()),'all_raw_rgba_bytes_equal_after_disk_read':True,'raw_rgba_sha256':hashlib.sha256(raw.tobytes()).hexdigest(),'rebuilt_rgba_sha256':hashlib.sha256(rebuilt.tobytes()).hexdigest(),'source_identities_flags_order_current_map_match':True,'world_translation':[528,320],'source_rectangle_union_overflow':{'alpha_threshold':127,'raw_pixel_count':int(outside.sum()),'fraction_of_alpha127_body':float(outside.sum()/np.count_nonzero(alpha>127)),'bottom_world_bbox_xyxy':[float(wx[ys,xs].min()-.5*scale),float(wy[ys,xs].min()-.5*scale),float(wx[ys,xs].max()+.5*scale),float(wy[ys,xs].max()+.5*scale)]if len(xs)else None,'all_retained_and_assigned':True},'original_woodfoot_region_alpha127_owner_counts':footstats,'woodfoot_302_preserved':footstats['302']>0,'low_alpha_far':{'criterion':'alpha1..16 >18rawpixels(4logical)fromalpha>16','count':int(far.sum()),'max_alpha':int(alpha[far].max())if np.any(far)else 0,'removed':False},'no_runtime_or_routes_executed':True}
assert validation['woodfoot_302_preserved'];(O/'validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n');(O/'instances.json').write_text(json.dumps({'instances':regs,'shared_raw_sha256':sha(R),'shared_scale':scale,'strict_world_translation':[528,320]},indent=2)+'\n')
colors=np.array([[0,0,0],[240,160,50],[100,180,230],[210,100,200],[80,200,130],[240,220,70]],np.uint8);rgb=colors[labels].copy();rgb[alpha==0]=[65,65,65];Image.fromarray(rgb).save(D/'owner_partition.png')
files=['README.md','build_registration.py','validation.json','instances.json','owner-labels.png','registration_left_50_41.json','registration_bottom_61_51.json']+[f'owners/owner-{n}.png'for n in range(299,305)];(O/'ARCHIVE_SHA256.json').write_text(json.dumps({'files':[{'path':n,'sha256':sha(O/n),'bytes':(O/n).stat().st_size}for n in files]},indent=2)+'\n')
print(json.dumps({'registrations':regs,'overflow':validation['source_rectangle_union_overflow'],'foot_counts':footstats,'far':validation['low_alpha_far']},indent=2))
