"""Prepare four detached candidate registrations. No production/Godot/GUI/image writes."""
from pathlib import Path
import json,hashlib,copy,collections
from PIL import Image
P=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent
MAP_SHA='d09549838963c8157307cc5406d3118baf69259d82459bcba0a3a8be5b34aa27';WINDOW=[2400,1408,3168,1920]
inputs={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bind(path):
 p=P/path;h=sha(p);inputs[path]={'path':path,'sha256':h,'bytes':p.stat().st_size};return p
def read(path):return json.loads(bind(path).read_text())
def save(name,obj):(OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
m=read('data/maps/A13.json');assert sha(P/'data/maps/A13.json')==MAP_SHA
manifest=read('assets/original/manifest.json');pk=manifest['packs']['Map/Res/Plant'];pages={}
def source(idx,c):
 f=pk['frames'][str(idx)];path=pk['pages'][f['page']]['file'][6:]
 if path not in pages:pages[path]=Image.open(bind(path)).convert('RGBA')
 a,b,w,h=f['rect'];im=pages[path].crop((a,b,a+w,b+h));x,y=c;sc=m['cells'][x*100+y];assert sc[2:]==[2,idx]
 return {'frame_index':idx,'cell':c,'source_cell':sc,'flag':sc[1],'layer':0 if sc[1] in [1,-2] else 2 if sc[1]==2 else 1,'sort_y':y,'stable_source_order':x*100+y,'source_byte_offset':m['cellByteOffsets'][x*100+y],'original':f['original'],'crop':f['crop'],'offset_ignored':f['offset'],'rgba_sha256':hashlib.sha256(im.tobytes()).hexdigest(),'rgba_size':[w,h],'world_bounds_xyxy':[x*48+f['crop'][0],y*32+32-f['original'][1]+f['crop'][1],x*48+f['crop'][0]+w,y*32+32-f['original'][1]+f['crop'][1]+h]}
def union(bs):return [min(b[0] for b in bs),min(b[1] for b in bs),max(b[2] for b in bs),max(b[3] for b in bs)]
def intersect(a,b):return a[0]<b[2] and a[2]>b[0] and a[1]<b[3] and a[3]>b[1]
# Independent fixed intended scope, never accept additional roots from incoming registrations.
SPECS=[('upright_47_66','tree',[47,66]),('upright_55_57','tree',[55,57]),('upright_59_61','tree',[59,61]),('shrub_58_51','shrub',[58,51])]
BASE={'tree':('assets/earth/environment/upright_tree_v1/registration_bottom_61_51.json',[61,51],{299:[0,0],300:[-2,4],301:[-1,4],302:[1,4],303:[2,4],304:[3,4]},'whole_tree_registration'),'shrub':('assets/earth/environment/round_shrub_v1/registration.json',[57,38],{143:[0,-3],144:[-1,0],145:[0,0],146:[1,0]},'whole_shrub_registration')}
ledger=[];unique_textures={};proofs=[];trusted=[]
for ident,kind,root in SPECS:
 path,base_root,offsets,wkey=BASE[kind];base=read(path);delta=[(root[0]-base_root[0])*48,(root[1]-base_root[1])*32];r=copy.deepcopy(base)
 # Remove old instance-specific claims rather than inheriting an authorization/status.
 for k in ['scope','approval_scope','instance','translation_from_center_world','center_registration_sha256','fallback_contract','registration_unit']:r.pop(k,None)
 r.update(status='DETACHED RESEARCH CANDIDATE ONLY; not runtime integrated or visually accepted',instance=ident,approval_scope='Preparation only for exact '+ident+'; no frame-ID/global replacement authorization',source_map_sha256=MAP_SHA,shadow='DISABLED for this candidate; no gate, receiver, mask, compositor slot or cast inherited',registration_unit='Atomic exact-instance group; any invalid owner returns every source owner of this group',reuse_provenance={'baseline_registration':path,'baseline_registration_sha256':sha(P/path),'baseline_root':base_root,'target_root':root,'world_translation':delta,'transforms':'Translation only; no resize, rotation, mirror, shear, trim, recrop or new texture','current_candidate_scope':'Independent study; ordinary entry unchanged'})
 r[wkey]['world_top_left']=[base[wkey]['world_top_left'][i]+delta[i] for i in range(2)]
 if 'root_world_xy' in r[wkey]:r[wkey]['root_world_xy']=[base[wkey]['root_world_xy'][i]+delta[i] for i in range(2)]
 r['owners']=[];ps=[]
 for idx,(dx,dy) in offsets.items():
  c=[root[0]+dx,root[1]+dy];bc=[base_root[0]+dx,base_root[1]+dy];s=source(idx,c);b=source(idx,bc);old=next(a for a in base['owners'] if a['frame_index']==idx);a=copy.deepcopy(old)
  for k in ['cell','source_cell','flag','layer','sort_y','stable_source_order']:a[k]=s[k]
  a['key']=f'Plant:{idx}@{c[0]},{c[1]}';a['world_top_left']=r[wkey]['world_top_left'];r['owners'].append(a)
  equal_fields=['frame_index','original','crop','offset_ignored','rgba_sha256','rgba_size','flag','layer'];eq={k:s[k]==b[k] for k in equal_fields}
  layout=s['world_bounds_xyxy']==[b['world_bounds_xyxy'][i]+delta[i%2] for i in range(4)];assert all(eq.values()) and layout
  ps.append({'baseline':b,'target':s,'field_equalities':eq,'relative_world_bounds_equal':layout,'source_cell_equal':s['source_cell']==b['source_cell'],'expected_texture_path':old['texture'],'expected_texture_sha256':old['texture_sha256'],'expected_fullcanvas_size':old['texture_size'],'unchanged_scale':old['scale'],'empty':old['empty']})
  tex=old['texture'][6:];p=bind(tex);assert sha(p)==old['texture_sha256'];im=Image.open(p);assert list(im.size)==old['texture_size'];unique_textures[tex]={'path':tex,'sha256':sha(p),'size':list(im.size),'explicit_empty_texture':old['empty'],'candidate_references':unique_textures.get(tex,{}).get('candidate_references',[])+[ident]}
 r['suppress_source_keys']=[a['key'] for a in r['owners']];r['partition']['method']='Reuse unchanged baseline fullcanvas owner partition, translated with the complete group; explicit empty owner remains present.'
 filename=f'registration_{ident}.json';save(filename,r)
 bounds=union([p['target']['world_bounds_xyxy'] for p in ps]);assert intersect(bounds,WINDOW)
 trusted.append({'id':ident,'family':kind,'root_cell':root,'expected_registration_path':'res://'+str((OUT/filename).relative_to(P)),'expected_registration_sha256':sha(OUT/filename),'source_map_sha256':MAP_SHA,'owner_count':len(r['owners']),'expected_owners':[{k:a[k] for k in ['pack','key','cell','source_cell','flag','layer','sort_y','stable_source_order','frame_index','texture','texture_sha256','texture_size','raw_rect','empty','world_top_left','scale']} for a in r['owners']],'shadow_enabled':False,'baseline_registration_sha256':sha(P/path)})
 ledger.append({'id':ident,'family':kind,'root_cell':root,'owner_count':len(ps),'source_bounds_xyxy':bounds,'crosses_window':not(bounds[0]>=WINDOW[0] and bounds[1]>=WINDOW[1] and bounds[2]<=WINDOW[2] and bounds[3]<=WINDOW[3]),'whole_registration':r[wkey],'world_translation':delta,'full_source_cell_equal':all(p['source_cell_equal'] for p in ps),'source_cell_differences':[{'frame_index':p['target']['frame_index'],'baseline':p['baseline']['source_cell'],'target':p['target']['source_cell']} for p in ps if not p['source_cell_equal']],'candidate_registration':filename,'candidate_registration_sha256':sha(OUT/filename)})
 proofs.append({'id':ident,'owner_checks':ps})
 for key in ['raw_texture']:
  if base.get(key):bind(base[key][6:])
 if base.get('partition',{}).get('owner_labels'):bind(base['partition']['owner_labels'][6:])
# Source-grid path proposals. No hidden NPC occupation, forced movement, or engine claims.
DIRS=[(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1)]
def free(c):
 x,y=c;return 0<=x<100 and 0<=y<100 and m['cells'][x*100+y][1] not in [-1,-2,-3]
def bfs(start):
 parents={tuple(start):None};q=collections.deque([tuple(start)])
 while q:
  x,y=q.popleft()
  for dx,dy in DIRS:
   n=(x+dx,y+dy)
   if n in parents or not free(n) or dx and dy and (not free((x+dx,y)) or not free((x,y+dy))):continue
   parents[n]=(x,y);q.append(n)
 return parents
def route(start,target):
 parents=bfs(start);t=tuple(target)
 if t not in parents:return None
 result=[]
 while t is not None:result.append(list(t));t=parents[t]
 return result[::-1]
reachable=bfs([61,39]);routes=[]
for ident,kind,root in SPECS:
 x,y=root;tests=([('rear_before_trunk',(x,y-1),lambda a:a[1]<y),('side_left',(x-3,y+1),lambda a:a[0]<x),('middle_split_depth',(x,y+2),lambda a:y<a[1]<y+4),('front_crown_sort_tie',(x+1,y+4),lambda a:a[1]==y+4),('front_after_all',(x,y+5),lambda a:a[1]>y+4)] if kind=='tree' else [('rear_before_shadow_owner',(x,y-4),lambda a:a[1]<y-3),('middle_split_depth',(x,y-1),lambda a:y-3<a[1]<y),('side_left',(x-2,y),lambda a:a[0]<x),('front_sort_tie',(x+2,y),lambda a:a[1]==y),('front_after_all',(x,y+1),lambda a:a[1]>y)])
 points=[];previous=[61,39]
 for label,wanted,predicate in tests:
  opts=[c for c in reachable if predicate(c) and max(abs(c[0]-wanted[0]),abs(c[1]-wanted[1]))<=4];opts.sort(key=lambda c:(max(abs(c[0]-wanted[0]),abs(c[1]-wanted[1])),abs(c[0]-wanted[0])+abs(c[1]-wanted[1]),c))
  assert opts,(ident,label);target=list(opts[0]);rr=route(previous,target);assert rr
  depth=[{'frame_index':a['frame_index'],'owner_sort_y':a['sort_y'],'actor_after_owner_at_same_layer':target[1]>=a['sort_y']} for a in next(z for z in trusted if z['id']==ident)['expected_owners']]
  points.append({'id':label,'desired_cell':list(wanted),'actual_reachable_cell':target,'adjusted_for_source_blocking':list(wanted)!=target,'target_source_cell':m['cells'][target[0]*100+target[1]],'route_from_previous':rr,'route_steps':len(rr)-1,'source_sort_relation':depth,'visual_requirement':'At the same tick and source South17 pose, compare source/candidate. Sort relation is not proof of actual alpha overlap; runner must verify body/canopy silhouette exposure and may add reachable flank points without moving source objects.'});previous=target
 routes.append({'instance':ident,'start_cell':[61,39],'points':points,'total_steps':sum(p['route_steps'] for p in points),'camera_requirement':'Follow or separately labeled audit camera; include whole actor and relevant full group. World-fixed window cannot contain all cross-edge tests.','shadow_requirement':'All four NEW candidate instances remain without cast in every state; do not disable or copy existing scene casters.'})
code_path='scripts/earth/sample_world.gd';code=bind(code_path).read_text();line=next((s.strip() for s in code.splitlines() if 'shadow_compositor.configure' in s),'not found')
for path in ['docs/EARTH_ART_BIBLE_V1.md','docs/EARTH_SOURCE_SAMPLE_ENTRY.md','scripts/earth/asset_guard.gd','scripts/earth/instance_identity_guard.gd','scripts/earth/upright_candidate.gd','scripts/earth/translated_shrub_candidate.gd','scripts/core/movement.gd']:bind(path)
save('candidate_ledger.json',{'status':'detached planning only','review_window_xyxy':WINDOW,'new_groups':ledger,'new_owner_count':sum(g['owner_count'] for g in ledger),'existing_context_only':[{'family':'tree','root':[61,51]},{'family':'shrub','root':[51,44]},{'family':'shrub','root':[64,45]}],'shadow_policy':{'new_groups_enabled':False,'observed_sample_world_sha256':sha(P/code_path),'observed_configuration_line':line,'baseline_discrepancy':'Parent mentioned four casters; current source contains five. Freeze with sole runner; this plan does not alter existing slots.'}})
save('source_equivalence_proof.json',proofs);save('trusted_expected_scope.json',{'purpose':'Fixed reviewed expectations for sole runner; do not derive trusted scope from incoming registration','groups':trusted});save('shared_asset_dependencies.json',{'distinct_owner_png_count':len(unique_textures),'texture_files':list(unique_textures.values()),'copy_policy':'No texture copy or generated PNG. References existing ordinary files. Empty304 kept in manifests, may remain an explicit empty runtime entry.'});save('route_acceptance_points.json',{'method':'Read-only source flags, 8-neighbor no corner-cut BFS; not executed Godot A* or visual acceptance','groups':routes});save('INPUT_SHA256.json',list(inputs.values()))
print('groups',[(g['id'],g['owner_count'],g['world_translation'],g['whole_registration']['world_top_left']) for g in ledger]);print('paths',[(g['instance'],[(p['id'],p['actual_reachable_cell'],p['route_steps']) for p in g['points']]) for g in routes]);print('texture_count',len(unique_textures));print('observed',line)
