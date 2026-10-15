"""Research only. Freeze AC, partition source-owner strips, validate guards/CPU. No runtime edit."""
from pathlib import Path
import json,hashlib,sys,collections
import numpy as np
from PIL import Image,ImageDraw
O=Path(__file__).parent;P=O.parents[1];R=P.parent;A=P/'art_source';D=P/'diagnostics/art_source/earth-bamboo-b-registration-study-v1';D.mkdir(parents=True,exist_ok=True);(O/'owners').mkdir(exist_ok=True)
sys.dont_write_bytecode=True;sys.path.insert(0,str(P/'tools'));from lp_original import Reader,read_pack,decode_frame
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda n,v:(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
AC=A/'earth_bamboo_b_right_fans_edit_v1/composite_candidate.png';assert sha(AC)=='36731fe0e2ffad2ee8c6772ff8433b14d60fb66f4ae1b5a4455251815eb858c2';(O/'raw_frozen.png').write_bytes(AC.read_bytes());raw=Image.open(O/'raw_frozen.png').convert('RGBA');ar=np.array(raw);H,W=ar.shape[:2];m=json.loads((P/'data/maps/A13.json').read_text());src=json.loads((A/'earth_bamboo_b_input_plan_v1/source_contract.json').read_text());v2=json.loads((A/'earth_bamboo_b_candidate_v2/measurements.json').read_text());density=v2['density'];t=v2['raw_from_source_translation'];bounds=src['world_bounds'];origin=[bounds[0]-t[0]/density,bounds[1]-t[1]/density];pk=json.loads((P/'assets/original/manifest.json').read_text())['packs']['Map/Res/Plant'];lp,recs,anim,key=read_pack(R/pk['source']);mr=(R/m['source']).read_bytes();assert sha(R/pk['source'])==pk['source_sha256'];assert sha(R/m['source'])==m['sourceSha256']
# Actual non-overlapping source crop x intervals; frame316 is independent cast-only.
body_ids=[317,319,321,322,320,318];source_edges=[31,79,127,175,223];raw_edges=[density*x+t[0]for x in source_edges];assign_x=np.searchsorted(raw_edges,np.arange(W)+.5,side='right');assignment=np.tile(np.array(body_ids,dtype=np.uint16)[assign_x],(H,1));parts={};owners=[];native=[]
for so in src['source_owners_in_draw_order']:
 idx=so['index'];x,y=so['cell'];order=x*m['height']+y;c=m['cells'][order];rd=Reader(mr,3,m['cellByteOffsets'][order]);assert [rd.short()for _ in range(4)]==c==so['source_cell'];assert c[2:]==[2,idx];assert so['flag']==c[1];layer=0 if c[1]in[1,-2]else 2 if c[1]==2 else 1;assert so['layer']==layer and so['sort_y']==y and so['stable_source_order']==order
 f=pk['frames'][str(idx)];full,meta=decode_frame(lp,recs[idx],'Map/Res/Plant',anim);xx,yy=f['crop'];aw,ah=f['rect'][2:];crop=full.crop((xx,yy,xx+aw,yy+ah));frame_record=next(z for z in src['frames']if z['index']==idx);assert hashlib.sha256(crop.tobytes()).hexdigest()==frame_record['crop_rgba_sha256'];assert meta['original']==f['original'] and meta['offset']==f['offset'];native.append({'index':idx,'original':f['original'],'crop':f['crop'],'offset':f['offset'],'LP_crop_RGBA_rechecked':True,'world_rect':so['all_frame_bounds_xyxy']})
 part=np.zeros_like(ar);mask=assignment==idx
 if idx!=316:part[mask]=ar[mask]
 parts[idx]=part;file=O/f'owners/owner-{idx}.png';Image.fromarray(part).save(file)
 own={'pack':'Map/Res/Plant','key':f'Plant:{idx}@{x},{y}','frame_index':idx,'cell':[x,y],'source_cell':c,'flag':c[1],'layer':layer,'sort_y':y,'stable_source_order':order,'source_map_byte_offset':m['cellByteOffsets'][order],'source_frame_original':f['original'],'source_frame_crop':f['crop'],'source_frame_offset_preserved_ignored_for_ordinary_objects':f['offset'],'source_world_rect':so['all_frame_bounds_xyxy'],'texture':'res://'+str(file.relative_to(P)),'texture_size':[W,H],'raw_rect':[0,0,W,H],'texture_sha256':sha(file),'empty':idx==316,'world_top_left':origin,'scale':1/density,'draw_offset_from_original_cell_origin':[origin[0]-x*48,origin[1]-y*32],'visible_pixel_count':int((part[:,:,3]>0).sum()),'low_alpha_1_to15_count':int(((part[:,:,3]>0)&(part[:,:,3]<16)).sum()),'assigned_raw_pixel_count':int(mask.sum())}
 owners.append(own)
# NativeRGBA reconstruction via disjoint assignment; exactly one owner for EVERY pixel incl invisibleRGB.
stack=np.stack([parts[i]for i in body_ids]);rebuilt=stack.astype(np.uint16).sum(0);assert np.array_equal(rebuilt,ar);counts=np.stack([assignment==i for i in body_ids]).sum(0);assert counts.min()==counts.max()==1
comp=Image.new('RGBA',raw.size)
for o in owners:comp.alpha_composite(Image.fromarray(parts[o['frame_index']]))
over=np.array(comp);alpha_comp_equal=bool(np.array_equal(over,ar));rgba_zero_nonzero=int(((ar[:,:,3]==0)&np.any(ar[:,:,:3]!=0,axis=2)).sum())
# Boundary pixel-center convention and fractional linear source-over seam risk, not aGPU assertion.
seams=[]
for i,e in enumerate(raw_edges):
 cut=int(np.searchsorted(np.arange(W)+.5,e));left=body_ids[i];right=body_ids[i+1];strip=ar[:,max(0,cut-2):cut+2];aa=strip[:,:,3];risk=[]
 # At half-texel blend between lastleft and firstright samples, each owner contributes half alpha.
 al=ar[:,cut-1,3].astype(float)/255/2;rr=ar[:,cut,3].astype(float)/255/2;reference=al+rr;source_over=al+rr*(1-al);deficit=reference-source_over
 for lo,hi in [(0,300),(300,600),(600,900),(900,H)]:
  risk.append({'raw_y_interval':[lo,hi],'nonzero_alpha_pixels':int((aa[lo:hi]>0).sum()),'alpha_1_to15_pixels':int(((aa[lo:hi]>0)&(aa[lo:hi]<16)).sum()),'alpha128plus_pixels':int((aa[lo:hi]>=128).sum()),'max_half_texel_alpha_deficit':float(deficit[lo:hi].max())})
 seams.append({'source_group_x':source_edges[i],'world_x':bounds[0]+source_edges[i],'raw_continuous_boundary_x':e,'first_right_pixel_x':cut,'left_owner':left,'right_owner':right,'left_sort_y':next(o['sort_y']for o in owners if o['frame_index']==left),'right_sort_y':next(o['sort_y']for o in owners if o['frame_index']==right),'native_pixel_center_boundary_error_logical':(cut-e)/density,'border_alpha_stats_4px':risk,'max_half_texel_alpha_deficit':float(deficit.max()),'y_at_max_deficit':int(deficit.argmax()),'max_deficit_byte_equivalent':float(deficit.max()*255)})
# Static original-grid routes, no script execution orGUI.
start=(61,39);q=collections.deque([start]);parent={start:None}
def free(x,y):return 0<=x<100 and 0<=y<100 and m['cells'][x*100+y][1]not in[-1,-2,-3]
while q:
 x,y=q.popleft()
 for dx,dy in [(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1)]:
  z=(x+dx,y+dy)
  if z in parent or not free(*z)or dx and dy and(not free(x+dx,y)or not free(x,y+dy)):continue
  parent[z]=(x,y);q.append(z)
routes=[]
for target in [(71,53),(72,54),(72,55),(72,56),(73,54),(73,55),(74,55),(74,56),(75,54),(75,55),(75,56),(75,57),(77,54),(78,53)]:
 path=[];z=target
 if z in parent:
  while z is not None:path.append(z);z=parent[z]
 routes.append({'target_cell':target,'source_cell':m['cells'][target[0]*100+target[1]],'reachable':target in parent,'steps':len(path)-1 if path else None,'path':path[::-1]})
# CPU renderer order proof: player order follows map NPCs on exact y ties.
player_order=m['width']*m['height']+len(m['npcs']);ordercases=[]
for y in [53,53.99,54,54.01,54.99,55,55.01,55.99,56,56.01]:
 sequence=sorted([(o['layer'],o['sort_y'],o['stable_source_order'],str(o['frame_index']))for o in owners]+[(1,y,player_order,'PLAYER')]);ordercases.append({'player_y':y,'draw_order':[z[3]for z in sequence]})
save('registration_research.json',{'schema':'earth-bamboo-b-first-instance-research-v1','status':'NOT PRODUCTION; not installed; first instance only','instance_root_cell':[78,53],'raw_texture':'res://'+str((O/'raw_frozen.png').relative_to(P)),'raw_sha256':sha(O/'raw_frozen.png'),'source_map_sha256':sha(P/'data/maps/A13.json'),'source_contract_sha256':sha(A/'earth_bamboo_b_input_plan_v1/source_contract.json'),'density':density,'whole_group_registration':{'scale':1/density,'world_top_left':origin,'raw_from_source_translation':t,'rotation':0,'shear':0,'refit_performed':False},'suppress_source_keys':[o['key']for o in owners],'owners':owners,'partition':{'method':'source actual vertical strip ownership; pixel center rounding; outermost bodies inherit tiny out-of-source fringe','body_order_left_to_right':body_ids,'source_edges':source_edges,'raw_edges':raw_edges,'full_canvas':True},'shadow':{'new_shadow':False,'owner316':'explicit empty only as part of complete7-owner group suppression','fallback':'all7 source owners restored atomically on any failure'},'cpu_validation':{'all_raw_pixels_assigned_exactly_once':True,'integer_RGBA_sum_reconstruction_exact':True,'source_over_native_RGBA_exact':alpha_comp_equal,'alpha0_nonzeroRGB_pixels':rgba_zero_nonzero,'no_alpha_threshold':True},'limits':'fullcanvas does not prove bilinear seam-free rendering; GPU/native whole-vs-split not run'})
save('source_guards.json',{'map_sha':sha(P/'data/maps/A13.json'),'LP_map_sha':m['sourceSha256'],'LP_plant_sha':pk['source_sha256'],'owners':[{k:o[k]for k in ['key','pack','frame_index','cell','source_cell','flag','layer','sort_y','stable_source_order','source_map_byte_offset','source_frame_original','source_frame_crop','source_frame_offset_preserved_ignored_for_ordinary_objects','source_world_rect']}for o in owners],'native_frame_rechecks':native,'atomic_gate':'all expected7 exact owner identities and raw/textureSHAs mandatory; never publish partial set'})
save('boundary_sampling_risks.json',{'analysis':'Four native columns around each strip boundary; alpha only at halftexel is a theoretical linear source-over risk. Not native GPU validation.','boundaries':seams});save('routes_and_draw_order.json',{'source_grid_only':True,'player_order':player_order,'routes':routes,'draw_order_cases':ordercases})
# Labeled study board only.
bg=Image.new('RGBA',raw.size,(65,70,67,255));bg.alpha_composite(raw);dr=ImageDraw.Draw(bg)
for s in seams:
 x=s['first_right_pixel_x'];dr.line((x,0,x,H),fill=(0,230,255,255),width=2);dr.text((x+4,30),f"{s['left_owner']}|{s['right_owner']} x{x}",fill='white')
bg.save(D/'actual-partition-boundaries.png')
Image.fromarray(rebuilt.astype('uint8')).save(D/'cpu-rebuilt.png')
# Freeze complete artistic lineage by explicit file hashes, not by rewriting previous stages.
lineage=[]
for name,files in [('earth_bamboo_b_candidate_v1',['raw.png','prompt_actual.txt','INPUT_SHA256.json','measurements.json']),('earth_bamboo_b_candidate_v2',['raw.png','prompt_actual.txt','INPUT_SHA256.json','measurements.json']),('earth_bamboo_b_upper_crown_edit_v1',['generated_crop_raw.png','composite_candidate.png','prompt_actual.txt','INPUT_SHA256.json','contract_before_generation.json','final_composite_weight.png','connection_guards.png','measurements.json']),('earth_bamboo_b_right_fans_edit_v1',['generated_crop_raw.png','composite_candidate.png','prompt_actual.txt','INPUT_SHA256.json','contract_before_generation.json','final_composite_weight.png','connection_guards.png','measurements.json'])]:
 for f in files:
  p=A/name/f;lineage.append({'path':str(p.relative_to(P)),'sha256':sha(p),'bytes':p.stat().st_size})
save('FROZEN_ART_LINEAGE.json',lineage)
inputs=[P/'data/maps/A13.json',P/'assets/original/manifest.json',R/m['source'],R/pk['source'],P/'tools/lp_original.py',P/'scripts/world_view.gd',P/'scripts/earth/sample_world.gd',P/'scripts/earth/asset_guard.gd',A/'earth_bamboo_b_input_plan_v1/source_contract.json',A/'earth_bamboo_b_candidate_v2/measurements.json',AC];save('INPUT_SHA256.json',[{'path':str(p.relative_to(R)),'sha256':sha(p)}for p in inputs])
print('origin',origin,'density',density,'edges',raw_edges);print('rebuild',alpha_comp_equal,rgba_zero_nonzero);print('seams',[(s['first_right_pixel_x'],round(s['max_deficit_byte_equivalent'],3))for s in seams]);print('routes',[(r['target_cell'],r['reachable'],r['steps'])for r in routes])
# Read-only preparation gate simulation; no publication/runtime modification.
import copy
reg=json.loads((O/'registration_research.json').read_text());expected=copy.deepcopy(reg['owners'])
def valid(r,live_map):
 try:
  if sha(P/'data/maps/A13.json')!=r['source_map_sha256']or len(r['owners'])!=7:return False
  if r['instance_root_cell']!=[78,53]or r['density']!=density or r['whole_group_registration']!=reg['whole_group_registration']:return False
  if sha(O/'raw_frozen.png')!=r['raw_sha256']or r['suppress_source_keys']!=reg['suppress_source_keys']:return False
  for a,e in zip(r['owners'],expected):
   for field in ['key','pack','frame_index','cell','source_cell','flag','layer','sort_y','stable_source_order','source_map_byte_offset','source_frame_original','source_frame_crop','source_frame_offset_preserved_ignored_for_ordinary_objects','source_world_rect','texture_size','raw_rect','world_top_left','scale','empty','texture','texture_sha256']:
    if a[field]!=e[field]:return False
   if live_map['cells'][a['stable_source_order']]!=e['source_cell']:return False
   if sha(P/a['texture'][6:])!=a['texture_sha256']:return False
  return True
 except (KeyError,TypeError,IndexError,FileNotFoundError):return False
assert valid(reg,m);tests=[]
for field,value in [('cell',[79,53]),('source_cell',[0,0,2,999]),('flag',2),('layer',0),('sort_y',50),('stable_source_order',1),('source_frame_crop',[0,0]),('source_frame_offset_preserved_ignored_for_ordinary_objects',[1,0]),('empty',True),('scale',1),('world_top_left',[0,0]),('texture_sha256','bad')]:
 r=copy.deepcopy(reg);r['owners'][1][field]=value;ok=valid(r,m);assert not ok;tests.append({'mutated_owner':317,'field':field,'gate_rejected':True,'would_publish_owner_count':0})
r=copy.deepcopy(reg);r['owners'].pop();assert not valid(r,m);tests.append({'field':'missing owner','gate_rejected':True,'would_publish_owner_count':0})
r=copy.deepcopy(reg);r['owners'][0]['empty']=False;assert not valid(r,m);tests.append({'field':'316 must be explicit empty','gate_rejected':True,'would_publish_owner_count':0})
live=copy.deepcopy(m);live['cells'][7254][1]=-1;assert not valid(reg,live);tests.append({'field':'live map flag changed','gate_rejected':True,'would_publish_owner_count':0})
save('guard_failure_cases.json',{'read_only_CPU_gate_only':True,'valid_complete_set_passed':True,'failure_cases':tests,'no_runtime_gate_installed':True})
reg['cpu_validation']['source_over_alpha_exact']=bool(np.array_equal(over[:,:,3],ar[:,:,3]));reg['cpu_validation']['source_over_visible_RGBA_exact']=bool(np.array_equal(over[ar[:,:,3]>0],ar[ar[:,:,3]>0]));reg['cpu_validation']['source_over_RGBA_difference_pixels']=int(np.any(over!=ar,axis=2).sum());save('registration_research.json',reg)
# Dense seam columns at native resolution; labelled diagnostics only.
board=Image.new('RGB',(5*180,920),(65,70,67));dr=ImageDraw.Draw(board)
for n,s in enumerate(seams):
 k=s['first_right_pixel_x'];patch=raw.crop((k-90,240,k+90,1120));board.paste(patch,(n*180,40),patch);dr.text((n*180+4,8),f"x{k} {s['left_owner']}|{s['right_owner']}",fill='white');dr.line((n*180+90,40,n*180+90,920),fill='cyan')
board.save(D/'seam-material-native-y240-1120.png')
