"""Read-only source inventory. Writes only its own research/diagnostic directories."""
from pathlib import Path
import json, hashlib, collections
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent;D=P/'diagnostics/art_source/a13-full-map-inventory-v1';D.mkdir(exist_ok=True,parents=True)
inputs=set()
def read(p):
 p=P/p;inputs.add(p);return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,data): (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
m=read('data/maps/A13.json');manifest=read('assets/original/manifest.json');packs=manifest['packs'];pages={};ims={};frames={};owners=[]
fixed=[2496,960,3264,1472]
def intersect(a,b):return a[0]<b[2] and a[1]<b[3] and a[2]>b[0] and a[3]>b[1]
def union(bs):return [min(b[0] for b in bs),min(b[1] for b in bs),max(b[2] for b in bs),max(b[3] for b in bs)]
def frame(pack,idx):
 key=f'{pack}:{idx}'
 if key not in frames:
  f=packs[pack]['frames'][str(idx)];page=packs[pack]['pages'][f['page']]['file'];path=P/page[6:];inputs.add(path)
  if page not in pages:pages[page]=Image.open(path).convert('RGBA')
  x,y,w,h=f['rect'];im=pages[page].crop((x,y,x+w,y+h));ims[key]=im
  frames[key]={'key':key,'pack':pack,'frame_index':idx,'original':f['original'],'crop':f['crop'],'offset':f['offset'],'size':[w,h],'rgba_sha256':hashlib.sha256(im.tobytes()).hexdigest(),'alpha_bbox':im.getbbox(),'atlas':page,'atlas_rect':f['rect'],'native_source_offset':f['sourceOffset'],'native_source_bytes':f['sourceBytes']}
 return frames[key]
regfiles=['ground_plate_v4/registration.json','training_hall_v1/registration.json','first_tree_v1/registration.json','upright_tree_v1/registration_left_50_41.json','upright_tree_v1/registration_bottom_61_51.json','round_shrub_v1/registration.json','round_shrub_v1/registration_51_44.json','round_shrub_v1/registration_64_45.json','grass_pair_v1/registration_A.json','grass_pair_v1/registration_B.json']
converted=set();regs=[]
for f in regfiles:
 r=read('assets/earth/environment/'+f);regs.append(r)
 for o in r.get('owners',r.get('tiles',[])):
  if 'cell' in o:converted.add((o.get('pack','Map/Res/FloorBig'),o.get('frame_index',o.get('index')),tuple(o['cell'])))
# Ground trusted scope independent from registration schema.
for x in range(52,67,2):
 for y in range(30,45,2):converted.add(('Map/Res/FloorBig',abs(m['cells'][x*100+y][0]),(x,y)))
G={1:'Map/Res/Debris',2:'Map/Res/Plant',3:'Map/Res/Wall',4:'Map/Res/Building',5:'Map/Res/Dynamic',8:'Data4'}
def add(pack,idx,x,y,category,order,cell,phase_ids,npc=None):
 bs=[];records=[]
 for k in phase_ids:
  f=frame(pack,k); ox,oy=(f['offset'] if category=='npc' else [0,0]);top=0 if category in ['floor','npc'] else (-52 if cell[2]==8 else 32-f['original'][1]);a=x*48+ox+f['crop'][0];b=y*32+oy+top+f['crop'][1];w,h=f['size'];bounds=[a,b,a+w,b+h];bs.append(bounds);records.append({'frame_key':f['key'],'draw_bounds_xyxy':bounds})
 bounds=union(bs);layer=0 if category=='floor' else 1 if category=='npc' else 0 if cell[1] in [1,-2] else 2 if cell[1]==2 else 1
 owner={'key':f'{pack}:{idx}@{x},{y}'+(f'#npc{npc}' if npc is not None else ''),'category':category,'pack':pack,'index':idx,'cell':[x,y],'source_cell':cell,'flag':cell[1] if cell else None,'layer':layer,'sort_y':y,'stable_source_order':order,'frames':records,'all_frame_bounds_xyxy':bounds,'intersects_fixed_by_full_draw_bounds':intersect(bounds,fixed),'extends_outside_fixed':not(bounds[0]>=fixed[0] and bounds[1]>=fixed[1] and bounds[2]<=fixed[2] and bounds[3]<=fixed[3]),'converted_exact_instance':(pack,idx,(x,y)) in converted or category=='npc' and npc in [0,1]}
 if npc is not None:owner.update(npc_record_index=npc,name=m['npcs'][npc]['name'],appearance=m['npcs'][npc]['appearance'],direction=m['npcs'][npc]['direction'])
 owners.append(owner)
for i,c in enumerate(m['cells']):
 x,y=divmod(i,m['height']);floor,flag,kind,idx=c
 if floor:add('Map/Res/FloorBig' if floor<0 else 'Map/Res/FloorSmall',abs(floor),x,y,'floor',i,c,[abs(floor)])
 if kind in G and idx>0:add(G[kind],idx,x,y,'object',i,c,list(range(55,60)) if kind==8 else list(range(idx,idx+(5 if kind==5 else 1))))
for i,n in enumerate(m['npcs']):
 idx=1+n['appearance']*12+n['direction']*4;add('Npc',idx,n['x'],n['y'],'npc',10000+i,None,list(range(idx,idx+4)),i)
lookup={(o['pack'],o['index'],tuple(o['cell'])):o for o in owners};families=[]
templates=[('first_tree',292,(57,34),{292:(0,0),293:(-2,3),294:(-1,3),295:(1,3),296:(2,3),297:(3,3),298:(4,3)}),('upright_tree',299,(50,41),{299:(0,0),300:(-2,4),301:(-1,4),302:(1,4),303:(2,4),304:(3,4)}),('round_shrub',145,(57,38),{143:(0,-3),144:(-1,0),145:(0,0),146:(1,0)}),('grass_A',239,(54,30),{239:(0,0),240:(1,0)}),('grass_B',241,(54,31),{241:(0,0),242:(1,0)})]
for name,root,baseline,offsets in templates:
 baseline_os=[lookup[('Map/Res/Plant',idx,(baseline[0]+dx,baseline[1]+dy))] for idx,(dx,dy) in offsets.items()];instances=[]
 for o in owners:
  if o['pack']!='Map/Res/Plant' or o['index']!=root:continue
  x,y=o['cell'];os=[lookup.get(('Map/Res/Plant',idx,(x+dx,y+dy))) for idx,(dx,dy) in offsets.items()];complete=all(os)
  assert complete
  delta=[(x-baseline[0])*48,(y-baseline[1])*32];bd=union([z['all_frame_bounds_xyxy'] for z in os]);flagdiff=[];celldiff=[]
  for a,b in zip(os,baseline_os):
   if a['flag']!=b['flag']:flagdiff.append({'frame':a['index'],'baseline':b['flag'],'target':a['flag']})
   if a['source_cell']!=b['source_cell']:celldiff.append({'frame':a['index'],'baseline':b['source_cell'],'target':a['source_cell']})
  exact_layout=all(a['all_frame_bounds_xyxy']==[b['all_frame_bounds_xyxy'][j]+delta[j%2] for j in range(4)] and a['layer']==b['layer'] for a,b in zip(os,baseline_os))
  all_done=all(z['converted_exact_instance'] for z in os)
  # Relevant surrounding source floor/occluder set; never assert translated context equivalence.
  neighborhood=[z['key'] for z in owners if z not in os and intersect(z['all_frame_bounds_xyxy'],bd)]
  instances.append({'root_cell':[x,y],'converted':all_done,'complete':complete,'rgba_crop_original_equal':True,'relative_layout_and_layers_equal':exact_layout,'flags_equal':not flagdiff,'full_source_cell_equal':not celldiff,'flag_differences':flagdiff,'source_cell_differences':celldiff,'world_translation_from_baseline':delta,'bounds_xyxy':bd,'owners':[z['key'] for z in os],'overlapping_source_context_owner_keys':neighborhood,'classification':'already_bounded' if all_done else 'rgba_crop_flags_sourcecell_exact_translation_context_unverified' if not celldiff else 'rgba_crop_flags_exact_translation_ground_context_differs' if not flagdiff else 'rgba_crop_translation_flag_context_differs'})
 families.append({'family':name,'baseline_root':baseline,'frame_indices':list(offsets),'owner_count_per_group':len(offsets),'instance_count':len(instances),'unconverted_instances':sum(not z['converted'] for z in instances),'instances':instances})
# Source-reference reachability only, not runtime A* or script execution.
from collections import deque
start=(61,39);parents={start:None};q=deque([start]);dirs=[(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1)]
def free(x,y):return 0<=x<100 and 0<=y<100 and m['cells'][x*100+y][1] not in [-1,-2,-3]
while q:
 x,y=q.popleft()
 for dx,dy in dirs:
  z=(x+dx,y+dy)
  if z in parents or not free(*z) or dx and dy and (not free(x+dx,y) or not free(x,y+dy)):continue
  parents[z]=(x,y);q.append(z)
def route(target):
 if target not in parents:return None
 r=[]
 while target is not None:r.append(target);target=parents[target]
 return r[::-1]
regions=[]
for rank,name,bounds,target in [(1,'south_continuity',[2400,1408,3168,1920],(56,50)),(2,'east_hall_daotong',[3168,1024,3936,1536],(74,39)),(3,'west_path_link',[1920,1024,2688,1536],(45,42))]:
 os=[o for o in owners if intersect(o['all_frame_bounds_xyxy'],bounds)];im=Image.new('RGBA',(768,512),(35,38,40,255))
 for o in sorted(os,key=lambda z:(0 if z['category']=='floor' else 1,z['layer'],z['sort_y'],z['stable_source_order'])):
  f=o['frames'][0];b=f['draw_bounds_xyxy'];im.alpha_composite(ims[f['frame_key']],(b[0]-bounds[0],b[1]-bounds[1]))
 im.convert('RGB').save(D/(name+'-source.png'))
 regs_here=[{'family':f['family'],'root_cell':a['root_cell'],'converted':a['converted'],'classification':a['classification']} for f in families for a in f['instances'] if intersect(a['bounds_xyxy'],bounds)]
 regions.append({'priority':rank,'id':name,'bounds_xyxy':bounds,'target_cell':target,'source_grid_route':route(target),'potential_owner_count_by_category':dict(collections.Counter(o['category'] for o in os)),'remaining_count_by_pack':dict(collections.Counter(o['pack'] for o in os if not o['converted_exact_instance'])),'known_reusable_groups':regs_here,'npcs':[{'name':o['name'],'record':o['npc_record_index'],'converted':o['converted_exact_instance']} for o in os if o['category']=='npc'],'intersecting_owner_keys':[o['key'] for o in os],'source_composite':str((D/(name+'-source.png')).relative_to(P))})
# Exact per-frame type inventory with all placements, not an inferred semantic/object count.
types=[]
for pack,idx in sorted(set((o['pack'],o['index']) for o in owners)):
 os=[o for o in owners if o['pack']==pack and o['index']==idx];types.append({'pack':pack,'base_frame_index':idx,'instances':len(os),'remaining':sum(not o['converted_exact_instance'] for o in os),'remaining_wholly_outside_fixed':sum(not o['converted_exact_instance'] and not o['intersects_fixed_by_full_draw_bounds'] for o in os),'remaining_crossing_or_inside_fixed':sum(not o['converted_exact_instance'] and o['intersects_fixed_by_full_draw_bounds'] for o in os),'owner_keys':[o['key'] for o in os],'source_frame_keys':list(dict.fromkeys(f['frame_key'] for o in os for f in o['frames']))})
summary={'scope':'A13 full source draw bounds, no visibility/occlusion or runtime acceptance claim','fixed_rect_xyxy':fixed,'map_cells':10000,'counts_by_pack':{},'source_grid_reachable_cells':len(parents),'npc_records':[{k:v for k,v in o.items() if k not in ['source_cell','frames']} for o in owners if o['category']=='npc']}
for pack in sorted(set(o['pack'] for o in owners)):
 os=[o for o in owners if o['pack']==pack];summary['counts_by_pack'][pack]={'owners':len(os),'base_frame_types':len(set(o['index'] for o in os)),'all_animation_frame_types':len(set(f['frame_key'] for o in os for f in o['frames'])),'converted':sum(o['converted_exact_instance'] for o in os),'remaining':sum(not o['converted_exact_instance'] for o in os),'remaining_wholly_outside_fixed':sum(not o['converted_exact_instance'] and not o['intersects_fixed_by_full_draw_bounds'] for o in os),'remaining_intersecting_fixed':sum(not o['converted_exact_instance'] and o['intersects_fixed_by_full_draw_bounds'] for o in os)}
save('inventory.json',{'summary':summary,'frame_types':types,'frames':list(frames.values()),'owners':owners});save('reusable_families.json',families);save('expansion_regions.json',regions)
# Small frame contact sheets for new-type review, preserving labels (not assets).
for pack in sorted(set(f['pack'] for f in frames.values())):
 fs=[f for f in frames.values() if f['pack']==pack];cols=8;cw,ch=144,150;board=Image.new('RGB',(cols*cw,((len(fs)+cols-1)//cols)*ch),(60,64,62));draw=ImageDraw.Draw(board)
 for n,f in enumerate(fs):
  x,y=(n%cols)*cw,(n//cols)*ch;thumb=ims[f['key']].copy();thumb.thumbnail((140,120));board.paste(thumb,(x+(140-thumb.width)//2,y+23),thumb);draw.text((x+3,y+3),str(f['frame_index']),fill='white')
 board.save(D/(pack.replace('/','_')+'-source-contact.png'))
for f in ['docs/EARTH_ART_BIBLE_V1.md','docs/EARTH_SOURCE_SAMPLE_ENTRY.md','scripts/world_view.gd','scripts/core/movement.gd']:inputs.add(P/f)
for reg in regs:
 for o in reg.get('owners',reg.get('tiles',[])):
  t=o.get('texture');
  if t and t.startswith('res://') and (P/t[6:]).is_file():inputs.add(P/t[6:])
save('INPUT_SHA256.json',[{'path':str(p.relative_to(P)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(inputs)])
print(json.dumps(summary['counts_by_pack'],indent=2));print('families',[(f['family'],f['instance_count'],f['unconverted_instances'],dict(collections.Counter(z['classification'] for z in f['instances']))) for f in families]);print('regions',[(r['id'],len(r['source_grid_route']) if r['source_grid_route'] else None,r['remaining_count_by_pack'],r['known_reusable_groups']) for r in regions])
# Infer repeated complete spatial families conservatively from maximally recurring cell deltas.
newfamilies=[]
for lo,hi,label in [(181,188,'broadleaf_tree_A'),(189,195,'broadleaf_tree_B'),(221,222,'low_plant_A'),(223,224,'low_plant_B'),(243,245,'grass_dense_A'),(246,247,'grass_dense_B'),(248,250,'grass_dense_C'),(268,270,'tree_small'),(271,276,'tree_red_A'),(277,283,'tree_red_B'),(310,315,'bamboo_A'),(316,322,'bamboo_B')]:
 candidates=[o for o in owners if o['pack']=='Map/Res/Plant' and lo<=o['index']<=hi];roots=[o for o in candidates if o['index']==lo];offsets={lo:(0,0)};evidence={}
 for idx in range(lo+1,hi+1):
  ct=collections.Counter((b['cell'][0]-a['cell'][0],b['cell'][1]-a['cell'][1]) for a in roots for b in candidates if b['index']==idx and abs(b['cell'][0]-a['cell'][0])<=8 and abs(b['cell'][1]-a['cell'][1])<=10)
  best=ct.most_common();offsets[idx]=best[0][0];evidence[idx]={'selected_offset':best[0][0],'support':best[0][1],'runner_up':best[1] if len(best)>1 else None}
 instances=[]
 for root in roots:
  x,y=root['cell'];os=[lookup.get(('Map/Res/Plant',idx,(x+dx,y+dy))) for idx,(dx,dy) in offsets.items()]
  if not all(os):continue
  instances.append({'root_cell':[x,y],'owners':[a['key'] for a in os],'bounds_xyxy':union([a['all_frame_bounds_xyxy'] for a in os]),'source_cells':[a['source_cell'] for a in os],'flags':[a['flag'] for a in os],'layers':[a['layer'] for a in os]})
 assigned=[key for a in instances for key in a['owners']];valid=len(assigned)==len(set(assigned))==len(candidates)
 newfamilies.append({'frame_range':[lo,hi],'visual_label_provisional':label,'source_owner_count':len(candidates),'complete_translated_groups':len(instances),'all_owners_assigned_exactly_once':valid,'relative_offsets':offsets,'offset_evidence':evidence,'instances':instances,'status':'new art concept and complete owner partition required; cannot use approved other-family texture'})
 # Compose one full group without context, for independent visual family confirmation.
 if instances:
  z=instances[0];b=z['bounds_xyxy'];im=Image.new('RGBA',(b[2]-b[0],b[3]-b[1]));os=[a for a in candidates if a['key'] in z['owners']]
  for a in sorted(os,key=lambda a:(a['layer'],a['sort_y'],a['stable_source_order'])):
   f=a['frames'][0];rect=f['draw_bounds_xyxy'];im.alpha_composite(ims[f['frame_key']],(rect[0]-b[0],rect[1]-b[1]))
  im.save(D/f'family-{lo}-{hi}-source.png')
save('new_plant_families.json',newfamilies)
# Actual unoccluded source-only pixels at tick 0, evaluated on each cropped owner, no giant map image.
from PIL import ImageChops
ordered=sorted(owners,key=lambda a:(0 if a['category']=='floor' else 1,a['layer'],a['sort_y'],a['stable_source_order']))
bins=collections.defaultdict(list);visible=[]
def binkeys(b):return [(x,y) for x in range(b[0]//128,(b[2]-1)//128+1) for y in range(b[1]//128,(b[3]-1)//128+1)]
for o in reversed(ordered):
 f=o['frames'][0];b=f['draw_bounds_xyxy'];a=ims[f['frame_key']].getchannel('A').copy();ids=set(j for k in binkeys(b) for j in bins[k])
 for j in ids:
  other=visible[j];r=other['_bounds'];l=max(b[0],r[0]);t=max(b[1],r[1]);rr=min(b[2],r[2]);bb=min(b[3],r[3])
  if l>=rr or t>=bb:continue
  oc=ims[other['_frame']].getchannel('A').crop((l-r[0],t-r[1],rr-r[0],bb-r[1])).point(lambda v:255 if v==255 else 0)
  here=a.crop((l-b[0],t-b[1],rr-b[0],bb-b[1]));a.paste(ImageChops.subtract(here,oc),(l-b[0],t-b[1]))
 count=sum(a.histogram()[1:]);item={'key':o['key'],'pack':o['pack'],'category':o['category'],'converted_exact_instance':o['converted_exact_instance'],'unoccluded_nonzero_alpha_pixels':count,'_bounds':b,'_frame':f['frame_key']};n=len(visible);visible.append(item)
 for k in binkeys(b):bins[k].append(n)
vis_summary={pack:{'remaining_source_tick0_exposed_owners':sum(v['pack']==pack and not v['converted_exact_instance'] and v['unoccluded_nonzero_alpha_pixels']>0 for v in visible),'remaining_source_tick0_fully_hidden_owners':sum(v['pack']==pack and not v['converted_exact_instance'] and v['unoccluded_nonzero_alpha_pixels']==0 for v in visible)} for pack in summary['counts_by_pack']}
save('source_exposure_tick0.json',{'limitations':'Original source only, phase0 NPC; higher opaque source pixels only. Not new Earth exposure, animation coverage or gameplay validation. All-frame bounds remain authoritative scope.','summary':vis_summary,'owners':[{k:v for k,v in a.items() if not k.startswith('_')} for a in visible]})
print('NEW FAMILIES',[(a['frame_range'],a['complete_translated_groups'],a['all_owners_assigned_exactly_once']) for a in newfamilies]);print('EXPOSURE',vis_summary)
ground_old=read('art_source/a13_ground_full_map_plan/source-inventory.json');assert ground_old['source_sha256']['map']==sha(P/'data/maps/A13.json') and ground_old['source_sha256']['manifest']==sha(P/'assets/original/manifest.json')
ground=[]
for name,c in ground_old['classifications'].items():
 os=[o for o in owners if o['category']=='floor' and (-o['index'] if o['pack'].endswith('FloorBig') else o['index']) in c['ids']]
 ground.append({'source_visual_category':name,'signed_ids':c['ids'],'all_owners':len(os),'converted_owners':sum(o['converted_exact_instance'] for o in os),'remaining_owners':sum(not o['converted_exact_instance'] for o in os),'remaining_frame_types':len(set((o['pack'],o['index']) for o in os if not o['converted_exact_instance'])),'caution':'Historical source category only; old material generator/repetition proposals are not current Earth art approval.'})
save('ground_categories.json',ground)
# Explicit integrity over all approved ordinary plant/building/ground owner textures, including empty suppressions.
registration_checks=[]
for rel,r in zip(regfiles,regs):
 texture_checks=[]
 for a in r.get('owners',r.get('tiles',[])):
  t=a.get('texture');expected=a.get('texture_sha256',a.get('sha256'))
  if t and t.startswith('res://'):
   path=P/t[6:];inputs.add(path);actual=sha(path);texture_checks.append({'path':t,'actual_sha256':actual,'declared_sha256':expected,'match':expected==actual if expected else None})
 registration_checks.append({'registration':'assets/earth/environment/'+rel,'actual_registration_sha256':sha(P/'assets/earth/environment'/rel),'texture_checks':texture_checks})
save('approved_dependency_checks.json',registration_checks)
save('INPUT_SHA256.json',[{'path':str(p.relative_to(P)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(inputs)])
print('GROUND',ground)
