#!/usr/bin/env python3
"""CPU attribution only. Frozen v1 untouched; diagnostics only, no receiver install."""
from pathlib import Path
import hashlib,json,importlib.util
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import distance_transform_edt,label as ndi_label,find_objects,maximum
P=Path(__file__).resolve().parents[2];OUT=P/'diagnostics/earth-shadow-receiver-v2';OUT.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('gate',P/'tools/earth/build_flat_shadow_gate.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
inputs={str(Path(__file__).relative_to(P)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
def load(p):
 q=P/p;inputs[p]=hashlib.sha256(q.read_bytes()).hexdigest();return json.loads(q.read_text())
def img(p):
 p=p.removeprefix('res://');q=P/p;inputs[p]=hashlib.sha256(q.read_bytes()).hexdigest();return np.array(Image.open(q).convert('RGBA'))
def raster(r):return g.raster(r,np.array([2496,960]),[1536,1024])
def bbox(a):
 y,x=np.nonzero(a);return None if not len(x) else [2496+int(x.min())/2,960+int(y.min())/2,2496+int(x.max()+1)/2,960+int(y.max()+1)/2]
m=load('data/maps/A13.json');scope=load('data/earth/a13_hall_source_scope.json');hall=load('assets/earth/environment/training_hall_v1/registration.json');manifest=load('assets/original/manifest.json');baseline=load('art_source/earth_shadow_next_stage_v1/measurements.json');gateinfo=load('assets/earth/shadows/se_flat_v1/manifest.json');forbid=img(gateinfo['forbidden']['texture'])[:,:,0]>0
assert inputs['data/maps/A13.json']==scope['source_map_sha256']
for dep in ['tools/earth/build_flat_shadow_gate.py','scripts/core/movement.gd','scripts/world_view.gd','scripts/earth/sample_world.gd','scripts/earth/hall_candidate.gd','scripts/earth/flat_shadow_gate.gd','scripts/earth/sample_floor_pass.gd','scripts/art/density_alpha_ground_shadow.gd','shaders/density_alpha_ground_shadow.gdshader','art_source/earth_training_hall_registration_v1/build_registration.py']:
 inputs[dep]=hashlib.sha256((P/dep).read_bytes()).hexdigest()
pack=manifest['packs']['Map/Res/Building'];pages={};owners=[]
for variant in ['source','new']:
 for o in (scope['owners'] if variant=='source' else hall['owners']):
  if variant=='source':
   f=pack['frames'][str(o['frame_index'])];p=pack['pages'][f['page']]['file']
   if p not in pages:pages[p]=img(p)
   x,y,w,h=f['rect'];a=pages[p][y:y+h,x:x+w,3];origin=np.array(o['cell'])*[48,32]+f['crop']+[0,32-f['original'][1]];scale=1
  elif o['empty']:a=np.zeros((1,1),np.uint8);origin=np.array([0,0]);scale=1
  else:
   a=img(o['texture'])[:,:,3];assert inputs[o['texture'][6:]]==o['texture_sha256'];origin=np.array(o['world_top_left']);scale=o['scale']
  masks={}
  for threshold,label in [(0,'alpha_positive'),(127,'alpha_128'),(254,'alpha_255')]:
   masks[label]=raster(g.rects_for(a>threshold,origin,scale,0))
  masks['dilated4']=raster(g.rects_for(a>0,origin,scale,4))
  owners.append(dict(alpha=a,origin=origin,scale=scale,raw_rect=o.get('raw_rect'),variant=variant,key=o['key'],frame_index=o['frame_index'],layer=o['layer'],cell=o['cell'],source_cell=o['source_cell'],masks=masks))
union=np.logical_or.reduce([o['masks']['dilated4'] for o in owners]);assert np.array_equal(union,forbid),'reconstructed30+30 mask differs'
groups={}
for variant in ['source','new']:
 for layer in [0,1]:
  for mode in ['alpha_positive','alpha_128','alpha_255','dilated4']:
   groups[f'{variant}_layer{layer}_{mode}']=np.logical_or.reduce([o['masks'][mode]for o in owners if o['variant']==variant and o['layer']==layer])
# Nearest-sampled composite opaque coverage at all points of each mask cell.
# Cell AABB maps to raw ranges; one non-255 texel means not strictly opaque.
whole=img(hall['raw_texture']);assert inputs[hall['raw_texture'][6:]]==hall['raw_sha256'];scale=hall['whole_building_registration']['scale'];origin=np.array(hall['whole_building_registration']['world_top_left']);hh,ww=whole.shape[:2]
yy,xx=np.indices((1024,1536));wx0=2496+xx/2;wy0=960+yy/2
x0=np.floor((wx0-origin[0])/scale).astype(int);y0=np.floor((wy0-origin[1])/scale).astype(int);x1=np.ceil((wx0+.5-origin[0])/scale).astype(int);y1=np.ceil((wy0+.5-origin[1])/scale).astype(int)
inside=(x0>=0)&(y0>=0)&(x1<=ww)&(y1<=hh)
x0c=np.clip(x0,0,ww);x1c=np.clip(x1,0,ww);y0c=np.clip(y0,0,hh);y1c=np.clip(y1,0,hh)
table=np.pad((whole[:,:,3]!=255).astype(np.int64),((1,0),(1,0))).cumsum(0).cumsum(1)
nonopaque=table[y1c,x1c]-table[y0c,x1c]-table[y1c,x0c]+table[y0c,x0c];opaque=inside&(nonopaque==0)
# World/grid relation: nearest rounded actor-origin cell and floor tile box both reported.
cx=np.floor((wx0+.25)/48+.5).astype(int);cy=np.floor((wy0+.25)/32+.5).astype(int)
flags=np.array([c[1]for c in m['cells']]).reshape(100,100);walk=~np.isin(flags[cx,cy],[-1,-2,-3])
# Static source connectivity without diagonal corner cut; dynamic actors are not blockers in sample configure.
seen={(61,39)};todo=[(61,39)]
while todo:
 x,y=todo.pop()
 for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
  a,b=x+dx,y+dy
  if not(0<=a<100 and 0<=b<100) or (a,b)in seen or flags[a,b]in[-1,-2,-3]:continue
  if dx and dy and (flags[x+dx,y]in[-1,-2,-3] or flags[x,y+dy]in[-1,-2,-3]):continue
  seen.add((a,b));todo.append((a,b))
# Footprint source data, no v1 tool execution or mutation.
f=load('assets/earth/npc/lingyunzi_v2/manifest.json');fa=img(f['texture'])[:,:,3];tr=load('assets/earth/environment/first_tree_v1/registration.json');ta=img(tr['raw_texture'])[:,:,3]
subjects=[]
for r in baseline['records']:
 if r['name']=='fangzhang0':continue
 a=ta if r['name']=='first_tree' else fa[:,int(r['name'][-1])*512:(int(r['name'][-1])+1)*512]
 y,x=np.nonzero(a>0);lo=np.stack((x,y),1)/4-.125;hi=lo+.5;corners=np.stack([lo,np.stack((hi[:,0],lo[:,1]),1),hi,np.stack((lo[:,0],hi[:,1]),1)],1)@np.array(r['matrix_rows']).T+np.array(r['translation_logical'])+r['world_origin'];rects=np.concatenate((corners.min(1)-1.8,corners.max(1)+1.8),1)
 pts=np.array(r['proxy_points_logical'])+r['world_origin'];rects=np.concatenate((rects,np.concatenate((pts-1.8,pts+1.8),1)));env=raster(rects);bad=env&forbid
 assert int(bad.sum())==r['conservative_overlap_forbidden_cells']
 subjects.append((r['name'],env,bad))
subjects.append(('lingyunzi_all',np.logical_or.reduce([s[1]for s in subjects if s[0].startswith('lingyunzi')]),np.logical_or.reduce([s[2]for s in subjects if s[0].startswith('lingyunzi')])))
def intersecting_texels(mask,rects):
 r=np.asarray(rects);lo=np.maximum(np.floor((r[:,:2]-[2496,960])*2).astype(int),0);hi=np.minimum(np.ceil((r[:,2:]-[2496,960])*2).astype(int),[1536,1024]);valid=np.all(hi>lo,1);out=np.zeros(len(r),bool);lo=lo[valid];hi=hi[valid];table=np.pad(mask.astype(np.int64),((1,0),(1,0))).cumsum(0).cumsum(1);out[valid]=(table[hi[:,1],hi[:,0]]-table[lo[:,1],hi[:,0]]-table[hi[:,1],lo[:,0]]+table[lo[:,1],lo[:,0]])>0;return out
material_dist=distance_transform_edt(whole[:,:,3]<128)*scale
component_labels,n_components=ndi_label(whole[:,:,3]>0,structure=np.ones((3,3),int));component_sizes=np.bincount(component_labels.ravel());component_slices=find_objects(component_labels);component_max=maximum(whole[:,:,3],component_labels,index=np.arange(n_components+1))
support_distance=distance_transform_edt(~groups['new_layer0_alpha_positive'])/2
source_plan=load('art_source/earth_training_hall_edit_plan_v1/edit-plan.json')
source_grass_probes=[r for r in source_plan['support_owner_rows']if r['cell']==[66,37]]
# These traces are documentation evidence, never a new receiver mask.
source_trace=source_plan['stair_boundary_guides']['left_stair']['source_visible_support_boundary'] if isinstance(source_plan['stair_boundary_guides'],dict) else None

rows=[]
for name,env,bad in subjects:
 contributions=[]
 for o in owners:
  counts={k:int((bad&v).sum())for k,v in o['masks'].items()}
  if counts['dilated4']:
   aa=o['alpha'];ay,ax=np.nonzero(aa>0);direct=intersecting_texels(bad,g.rects_for(aa>0,o['origin'],o['scale'],0));seed=intersecting_texels(bad,g.rects_for(aa>0,o['origin'],o['scale'],4));unique,count=np.unique(aa[ay[seed],ax[seed]],return_counts=True)
   positions=np.stack((ax[seed],ay[seed]),1)*o['scale']+o['origin']
   evidence={'seed_texel_count':int(seed.sum()),'direct_texel_count':int(direct.sum()),'dilation_seed_alpha_histogram':{str(int(v)):int(c)for v,c in zip(unique,count)},'direct_local_texel_xy':np.stack((ax[direct],ay[direct]),1).tolist(),'direct_world_texel_origins':(np.stack((ax[direct],ay[direct]),1)*o['scale']+o['origin']).tolist(),'dilation_seed_local_bbox_xyxy':[int(ax[seed].min()),int(ay[seed].min()),int(ax[seed].max()+1),int(ay[seed].max()+1)]}
   if o['variant']=='new':
    rx,ry,_,_=o['raw_rect'];ds=material_dist[ay[seed]+ry,ax[seed]+rx];evidence['seed_distance_to_whole_alpha128_logical_minmax']=[float(ds.min()),float(ds.max())];evidence['seed_whole_raw_xy']=np.stack((ax[seed]+rx,ay[seed]+ry),1).tolist()
    ids=sorted(set(component_labels[ay[seed]+ry,ax[seed]+rx].tolist()));comps=[]
    for cid in ids:
     sl=component_slices[cid-1];comps.append({'id':int(cid),'size_texels':int(component_sizes[cid]),'max_alpha':int(component_max[cid]),'bbox_whole_raw_xyxy':[sl[1].start,sl[0].start,sl[1].stop,sl[0].stop]})
    evidence['positive_alpha_8connected_components']=comps
   contributions.append({k:v for k,v in o.items()if k not in ['masks','alpha','origin','scale','raw_rect']}|{'overlap_cells':counts,'dilated_overlap_world_bbox':bbox(bad&o['masks']['dilated4']),'seed_evidence':evidence})
   if name=='first_tree' and o['variant']=='source':
    ff=pack['frames'][str(o['frame_index'])];px,py,pw,ph=ff['rect'];rgba=pages[pack['pages'][ff['page']]['file']][py:py+ph,px:px+pw];canvas=Image.new('RGBA',(pw,ph),(90,95,90,255));canvas.alpha_composite(Image.fromarray(rgba));mark=np.zeros_like(rgba);mark[ay[seed],ax[seed]]=[255,185,0,130];mark[ay[direct],ax[direct]]=[255,0,180,230];canvas.alpha_composite(Image.fromarray(mark));ylo=max(0,int(ay[seed].min())-20);yhi=min(ph,int(ay[seed].max())+10);canvas.crop((0,ylo,pw,yhi)).resize((pw*8,(yhi-ylo)*8),Image.Resampling.NEAREST).convert('RGB').save(OUT/f"source-{o['frame_index']}-seed-detail.png")
 support=groups['source_layer0_dilated4']|groups['new_layer0_dilated4'];upper=groups['source_layer1_dilated4']|groups['new_layer1_dilated4'];upper_only=bad&upper&~support
 exact=np.logical_or.reduce([o['masks']['alpha_positive']for o in owners]);fringe=bad&~exact
 cells=[]
 for x,y in sorted(set(zip(cx[bad].tolist(),cy[bad].tolist()))):
  q=bad&(cx==x)&(cy==y);c=m['cells'][x*100+y]
  cells.append({'nearest_actor_cell':[x,y],'source_cell':c,'flag_walkable':c[1]not in[-1,-2,-3],'static_reachable_from_61_39':(x,y)in seen,'overlap_cells':int(q.sum()),'new_support_direct_cells':int((q&groups['new_layer0_alpha_positive']).sum()),'upper_only_cells':int((q&upper_only).sum()),'opaque_hidden_full_cells':int((q&opaque).sum())})
 row={'subject':name,'envelope_cells':int(env.sum()),'min_envelope_distance_new_support_logical':float(support_distance[env].min()),'forbidden_overlap_cells':int(bad.sum()),'world_bbox':bbox(bad),'groups_overlap_cells':{k:int((bad&v).sum())for k,v in groups.items()},'support_dilated_union_cells':int((bad&support).sum()),'upper_only_dilated_cells':int(upper_only.sum()),'dilation_only_no_alpha_any_owner_cells':int(fringe.sum()),'all_building_new_whole_fully_opaque_cells':int((bad&opaque).sum()),'upper_only_fully_opaque_cells':int((upper_only&opaque).sum()),'upper_only_not_opaque_cells':int((upper_only&~opaque).sum()),'upper_only_walkable_cells':int((upper_only&walk).sum()),'upper_only_walkable_and_opaque_cells':int((upper_only&walk&opaque).sum()),'owner_contributions_nonadditive':contributions,'nearest_actor_grid_cells':cells}
 rows.append(row)
 if name not in ['lingyunzi_all','first_tree']:continue
 # Diagnostic annotations only; no candidate art or cast rendered.
 bg=Image.new('RGBA',(1536,1024),(50,56,61,255));ov=np.zeros((1024,1536,4),np.uint8);ov[env]=[125,145,155,80];ov[groups['source_layer0_dilated4']]=[0,130,255,90];ov[groups['new_layer0_dilated4']]=[0,255,170,100];ov[upper_only]=[255,190,0,255];ov[bad&support]=[255,30,60,255];ov[upper_only&opaque]=[170,70,230,255];bg.alpha_composite(Image.fromarray(ov));d=ImageDraw.Draw(bg)
 for x,y in [(x,y)for x in range(52,69)for y in range(30,47)]:
  sx,sy=(x*48-2496)*2,(y*32-960)*2;d.line((sx,0,sx,1024),fill=(90,90,90,70));d.line((0,sy,1536,sy),fill=(90,90,90,70));d.text((sx+2,sy+2),f'{x},{y} f{flags[x,y]}',fill='white')
 d.rectangle((0,0,1536,32),fill=(20,20,20));d.text((5,8),f'{name}: RED support conflict / AMBER upper-only / PURPLE fully opaque upper / BLUE old support / GREEN new support',fill='white');bg.convert('RGB').save(OUT/f'{name}-attribution.png')
 # Actual building nearest CPU background, at 2 mask samples/logical unit, then highlight queried overlap.
 rawx=np.floor((wx0+.25-origin[0])/scale).astype(int);rawy=np.floor((wy0+.25-origin[1])/scale).astype(int);valid=(rawx>=0)&(rawy>=0)&(rawx<ww)&(rawy<hh);sample=np.zeros((1024,1536,4),np.uint8);sample[valid]=whole[rawy[valid],rawx[valid]]
 base=Image.new('RGBA',(1536,1024),(85,93,86,255));base.alpha_composite(Image.fromarray(sample));mark=np.zeros_like(sample);mark[upper_only]=[255,160,0,160];mark[bad&support]=[255,0,70,180];base.alpha_composite(Image.fromarray(mark));bb=bbox(bad);x0,y0,x1,y1=bb;crop=(max(0,int((x0-2496-20)*2)),max(0,int((y0-960-20)*2)),min(1536,int((x1-2496+20)*2)),min(1024,int((y1-960+20)*2)));base.crop(crop).convert('RGB').save(OUT/f'{name}-building-detail.png')
# Conditional receiver feasibility only: retain EVERY support pixel and all upper
# pixels except the explicitly inspected isolated components listed in the report.
review_ids=set()
for row in rows:
 for o in row['owner_contributions_nonadditive']:
  if o['variant']=='new':review_ids.update(c['id']for c in o['seed_evidence']['positive_alpha_8connected_components'])
reviewed=np.isin(component_labels,sorted(review_ids));assert np.all(whole[:,:,3][reviewed]==1)
conditional=np.zeros((1024,1536),bool)
conditional4=np.zeros_like(conditional);geometry=np.zeros_like(conditional);conditional_owner_rows=[]
for o in owners:
 if o['variant']!='new':continue
 a=o['alpha']>0
 if o['raw_rect'] is not None and o['layer']==1:
  x,y,w,h=o['raw_rect'];a=a&~reviewed[y:y+h,x:x+w]
 c4=raster(g.rects_for(a,o['origin'],o['scale'],4));c6=raster(g.rects_for(a,o['origin'],o['scale'],6));conditional |= c6;conditional4 |= c4;geometry |= raster(g.rects_for(a,o['origin'],o['scale'],0))
 conditional_owner_rows.append({'key':o['key'],'layer':o['layer'],'retained_positive_alpha_texels':int(a.sum()),'excluded_noise_texels':int(((o['alpha']>0)&~a).sum()),'mask4':c4,'mask6':c6})
 if o['layer']==0:assert np.array_equal(a,o['alpha']>0)
candidate_gap=distance_transform_edt(~conditional4)/2
geometry_distance=distance_transform_edt(~geometry)/2
core_geometry=raster(g.rects_for(whole[:,:,3]>=128,origin,scale,0));core_distance=distance_transform_edt(~core_geometry)/2
for row,(name,env,bad) in zip(rows,subjects):
 assert row['subject']==name
 row['conditional_new_only_geometry_plus6_overlap_cells']=int((env&conditional).sum())
 row['candidate_new_only_geometry_plus4_overlap_cells']=int((env&conditional4).sum())
 row['min_distance_candidate_forbidden_mask_cell_centers_logical']=float(candidate_gap[env].min())
 row['distance_interpretation']='All distance-transform values are half-logical raster cell-center distances; subtract sqrt(2)/2 = .707107 for conservative distance between covered cell AREAS. Not a measured 3D height.'
 row['min_envelope_distance_retained_new_geometry_logical']=float(geometry_distance[env].min())
 row['min_envelope_distance_new_alpha128_core_logical']=float(core_distance[env].min())
 sensitivity_seeds=[]
 for o in owners:
  if o['variant']!='new' or o['raw_rect'] is None:continue
  x,y,w,h=o['raw_rect'];aa=o['alpha'];valid=aa>0
  if o['layer']==1:valid &= ~reviewed[y:y+h,x:x+w]
  ay,ax=np.nonzero(valid);seeds=intersecting_texels(env,g.rects_for(valid,o['origin'],o['scale'],6))
  if seeds.any():
   uv,uc=np.unique(aa[ay[seeds],ax[seeds]],return_counts=True);sensitivity_seeds.append({'key':o['key'],'seed_alpha_histogram':{str(int(v)):int(c)for v,c in zip(uv,uc)},'seed_whole_raw_xy':np.stack((ax[seeds]+x,ay[seeds]+y),1).tolist()})
 row['plus6_remaining_seed_evidence']=sensitivity_seeds
 row['plus6_overlap_world_bbox']=bbox(env&conditional)
 row['conditional_owner_contributions']=[{'key':o['key'],'layer':o['layer'],'overlap_plus4_cells':int((env&o['mask4']).sum()),'overlap_plus6_cells':int((env&o['mask6']).sum())}for o in conditional_owner_rows if (env&o['mask6']).any()]
 if name=='lingyunzi_all':
  direct=bad&groups['new_layer1_alpha_positive'];dy,dx=np.nonzero(direct);row['direct_four_cells_world_xywh']=[[2496+int(x)/2,960+int(y)/2,.5,.5]for x,y in zip(dx,dy)]
# Wide same-world source/new context, marked conflicts are diagnostics, not cast art.
source_canvas=Image.new('RGBA',(796,665))
for o in scope['owners']:
 f=pack['frames'][str(o['frame_index'])];px,py,pw,ph=f['rect'];rgba=pages[pack['pages'][f['page']]['file']][py:py+ph,px:px+pw];pos=np.array(o['cell'])*[48,32]+f['crop']+[0,32-f['original'][1]]-[2948,642];source_canvas.alpha_composite(Image.fromarray(rgba),tuple(pos))
src=np.array(source_canvas);wx=wx0+.25;wy=wy0+.25;sx=np.floor(wx-2948).astype(int);sy=np.floor(wy-642).astype(int);valid=(sx>=0)&(sy>=0)&(sx<796)&(sy<665);srcsample=np.zeros((1024,1536,4),np.uint8);srcsample[valid]=src[sy[valid],sx[valid]]
for name,env,bad in subjects:
 if name not in ['lingyunzi_all','first_tree']:continue
 panels=[]
 for title,arr in [('SOURCE (retired grass/apron retained)',srcsample),('NEW (body pixels unchanged)',sample)]:
  im=Image.new('RGBA',(1536,1024),(85,93,86,255));im.alpha_composite(Image.fromarray(arr));mk=np.zeros_like(arr);mk[bad]=[255,50,140,180];im.alpha_composite(Image.fromarray(mk));crop=im.crop((940,200,1536,620)).convert('RGB');d=ImageDraw.Draw(crop);d.rectangle((0,0,596,24),fill=(20,20,20));d.text((4,7),title,fill='white');panels.append(crop)
 board=Image.new('RGB',(1192,420));board.paste(panels[0],(0,0));board.paste(panels[1],(596,0));board.save(OUT/f'{name}-source-new-context.png')
for name,env,bad in subjects:
 if name not in ['lingyunzi_all','first_tree']:continue
 diagram=np.zeros((1024,1536,3),np.uint8);diagram[:]=[45,52,58];diagram[env]=[120,150,165];diagram[conditional4]=[165,50,65];diagram[groups['new_layer0_dilated4']]=[40,200,130];diagram[bad&~conditional4]=[255,190,20]
 im=Image.fromarray(diagram);draw=ImageDraw.Draw(im);draw.rectangle((0,0,1536,28),fill=(20,20,20));draw.text((5,8),f'{name} CPU CANDIDATE: gray=whole envelope / red=retained new geometry+4 / green=new support+4 / amber=retired false conflict',fill='white');im.save(OUT/f'{name}-candidate-receiver.png')
candidate_files={}
for fname,arr in [('allowed-candidate.png',~conditional4),('forbidden-candidate.png',conditional4)]:
 q=OUT/fname;Image.fromarray(arr.astype(np.uint8)*255,'L').save(q);assert np.array_equal(np.array(Image.open(q)),arr.astype(np.uint8)*255);candidate_files[fname]={'sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'size':[1536,1024],'set_cells':int(arr.sum())}
# Candidate proposal binds exact components and current 30-owner inputs; no runtime install.
parameter_records=[{'name':r['name'],'reference_logical':r['reference_logical'],'slope':r['slope'],'world_origin':r['world_origin'],'density':4,'cast':[1.2,.55],'opacity':.25,'blur_logical':.8}for r in baseline['records']if r['name']!='fangzhang0']
parameter_sha=hashlib.sha256(json.dumps(parameter_records,sort_keys=True,separators=(',',':')).encode()).hexdigest()
candidate={'parameter_records':parameter_records,'parameter_records_canonical_json_sha256':parameter_sha,'schema':'earth-new-hall-flat-receiver-cpu-candidate-v2','status':'CPU candidate only; parent review required before GPU','scope_world_rect':[2496,960,768,512],'mask_density':2,'outside_sample_allowed':False,'semantic_forbidden_dilation_logical':4,'enabling_conditions':['T uses exact approved new hall and all30 owner identities/resources validated atomically','source A13 map/flags/owner scope unchanged and SHA-bound','candidate body/alpha, fixed parameters and full envelope SHA-bound','disable whole cast immediately on T source hall, failed hall validation, any mismatch or footprint outside allowed'],'existing_se_and_fangzhang_gates':'unchanged and independent','noise_exclusion':'only exact28 texels in15 reviewed positive-alpha8connected components, all alpha1 and remote from alpha128 core; pixels remain drawn unchanged','excluded_noise_texels_whole_raw_xy':np.stack(np.nonzero(reviewed)[::-1],1).tolist(),'noise_components':[{k:v for k,v in c.items()}for cid in sorted(review_ids)for c in [next(c for row in rows for o in row['owner_contributions_nonadditive'] if o['variant']=='new' for c in o['seed_evidence']['positive_alpha_8connected_components'] if c['id']==cid)]],'all30_owner_geometry_counts':[{k:v for k,v in o.items()if k not in ['mask4','mask6']}for o in conditional_owner_rows],'parameters_frozen_v1':{'cast':[1.2,.55],'opacity':.25,'blur_logical':.8,'measurement_report_sha256':inputs['art_source/earth_shadow_next_stage_v1/measurements.json']},'files_diagnostic_relative':candidate_files,'input_sha256':inputs}
(OUT/'receiver-candidate.json').write_text(json.dumps(candidate,indent=2)+'\n')
report={'schema'  :'earth-shadow-receiver-attribution-v2','status':'read-only CPU research; no existing gate change or forbidden shadow enable','raster_density':2,'sample_world_rect':[2496,960,768,512],'original_gate_reconstructed_exact':True,'owner_count_each_variant':30,'contributions_nonadditive':True,'opaque_method':'all overlapped nearest whole-building texels alpha255 over each half-logical cell; assumes frozen disjoint owner assembly and nearest grid; CPU visibility bound not GPU proof or receiver geometry','grid_method':'nearest actor cell floor(world/(48,32)+.5); flags[-1,-2,-3] block, static no-corner-cut flood from61,39. Cell walkability is not surface height.','subjects':rows,'conditional_feasibility':{'not_installed':True,'new_hall_required':True,'source_hall_or_invalid_hall_disable':True,'retained_new_support_all_alpha_positive':True,'retained_upper_except_exact_reviewed_components':True,'candidate_semantic_clearance_logical':4,'sensitivity_clearance_logical':6,'reason_for_6':'original4 plus ceil(max material trace uncertainty4raw * .4841293)=2','reviewed_positive_alpha_component_ids':sorted(review_ids),'reviewed_component_total_texels':int(reviewed.sum()),'no_body_pixel_mutations':True,'no_shadow_clipping_or_parameter_changes':True},'source_grass_apron_probes':source_grass_probes,'source_left_stair_boundary_guide':source_trace,'input_sha256':inputs}
(OUT/'attribution.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps([{k:v for k,v in r.items()if k not in ['owner_contributions_nonadditive','nearest_actor_grid_cells']}for r in rows],indent=2))
