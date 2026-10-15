#!/usr/bin/env python3
"""CPU diagnostic-only texture, shader-alpha overlays and two runner interfaces.
Run analyze_receiver.py first. No runtime or original asset edits; no GPU.
"""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import map_coordinates
P=Path(__file__).resolve().parents[2];OUT=P/'diagnostics/earth-shadow-receiver-v2';OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads((P/p).read_text())
def write(n,v):(OUT/n).write_text(json.dumps(v,indent=2)+'\n')
receiver=json.loads((OUT/'receiver-candidate.json').read_text());measure=load('art_source/earth_shadow_next_stage_v1/measurements.json');regs={r['name']:r for r in measure['records']};tree=load('assets/earth/environment/first_tree_v1/registration.json');npc=load('assets/earth/npc/lingyunzi_v2/manifest.json');hall=load('assets/earth/environment/training_hall_v1/registration.json');ground=load('assets/earth/environment/ground_plate_v4/registration.json')
rawpath=P/tree['raw_texture'][6:];raw=np.array(Image.open(rawpath).convert('RGBA'));assert list(raw.shape)==[1254,1254,4];assert sha(rawpath)==tree['raw_sha256'];padded=np.zeros((1256,1256,4),np.uint8);padded[:1254,:1254]=raw;path=OUT/'first-tree-shadow-padded-1256.png';Image.fromarray(padded).save(path);decoded=np.array(Image.open(path));assert np.array_equal(decoded[:1254,:1254],raw);assert not decoded[1254:].any() and not decoded[:,1254:].any()
pad={'schema':'earth-first-tree-shadow-only-padding-v1','status':'technical diagnostic texture only; not installed','source_texture':tree['raw_texture'],'source_sha256':sha(rawpath),'source_size':[1254,1254],'output_texture':'res://diagnostics/earth-shadow-receiver-v2/'+path.name,'output_sha256':sha(path),'output_size':[1256,1256],'copy_rect_xywh':[0,0,1254,1254],'right_bottom_transparent_px':[2,2],'all_original_rgba_equal':True,'padding_all_rgba_zero':True,'density':4,'logical_region_xywh':[0,0,314,314],'raw_root_unchanged':[523,1224],'logical_root':[130.75,306.0],'world_origin':[2630.25,784.0],'registration_sha256':sha(P/'assets/earth/environment/first_tree_v1/registration.json'),'producer_sha256':sha(Path(__file__)),'sampling_caveat':'right/bottom edge interpolates to new transparent texels instead of old frame-edge clamp; CPU/GPU review required; no original texture changed'};write('tree-shadow-padding-contract.json',pad)
# CPU mirror of inverse projected alpha and helper's normalized3x3 filter.
y,x=np.indices((1024,1536));world=np.stack((2496+(x+.5)/2,960+(y+.5)/2),axis=0)
def projected(a,r):
 inv=np.linalg.inv(np.array(r['matrix_rows']));base=world-np.array(r['world_origin'])[:,None,None];T=np.array(r['translation_logical']);h,w=a.shape;result=np.zeros((1024,1536),float)
 for iy in [-1,0,1]:
  for ix in [-1,0,1]:
   q=base+np.array([ix*.8,iy*.8])[:,None,None]-T[:,None,None];p=np.einsum('ij,jhw->ihw',inv,q)*4;valid=(p[0]>=0)&(p[1]>=0)&(p[0]<w)&(p[1]<h);coords=np.stack((np.clip(p[1],.5,h-.5)-.5,np.clip(p[0],.5,w-.5)-.5));v=map_coordinates(a.astype(float)/255,coords,order=1,mode='nearest',prefilter=False);result+=v*valid*(2 if ix==0 else 1)*(2 if iy==0 else 1)/16
 return result*.25
npca=np.array(Image.open(P/npc['texture'][6:]).convert('RGBA'))[:,:,3];treealpha=projected(padded[:,:,3],regs['first_tree']);ling=[projected(npca[:,i*512:(i+1)*512],regs[f'lingyunzi{i}'])for i in range(4)]
allowed=np.array(Image.open(OUT/'allowed-candidate.png'))>0;forbidden=~allowed
# Sampling alpha outside conservative allowed must be zero for candidate overlays.
assert not (treealpha[forbidden]>1e-10).any()
for a in ling:assert not (a[forbidden]>1e-10).any()
base=np.array(Image.open(P/ground['shared_plate']['texture'][6:]).convert('RGB')).astype(float);assert base.shape==(1024,1536,3)
whole=np.array(Image.open(P/hall['raw_texture'][6:]).convert('RGBA'));scale=hall['whole_building_registration']['scale'];origin=np.array(hall['whole_building_registration']['world_top_left']);rx=np.floor((world[0]-origin[0])/scale).astype(int);ry=np.floor((world[1]-origin[1])/scale).astype(int);valid=(rx>=0)&(ry>=0)&(rx<whole.shape[1])&(ry<whole.shape[0]);building=np.zeros((1024,1536,4),np.uint8);building[valid]=whole[ry[valid],rx[valid]];ba=building[:,:,3:4]/255
color=np.array([.035,.045,.055])*255
for name,a in [('lingyunzi-phase0',ling[0]),('first-tree',treealpha),('both-phase0',1-(1-treealpha)*(1-ling[0]))]:
 rgb=base*(1-a[:,:,None])+color*a[:,:,None];rgb=rgb*(1-ba)+building[:,:,:3]*ba;im=Image.fromarray(np.clip(rgb,0,255).astype(np.uint8));d=ImageDraw.Draw(im);d.rectangle((0,0,1536,30),fill=(20,20,20));d.text((5,10),name+' CPU alpha only; floor -> full un-clipped shadow -> hall. NO body sprites / NO GPU.',fill='white');im.save(OUT/f'{name}-cpu-alpha-overlay.png')
 # Ground image is visualization context only; the numerical projection does not sample its RGB.
 im.crop((900,340,1536,620)).save(OUT/f'{name}-cpu-alpha-detail.png')
# Material mask review explicitly distinguishes entity-forbidden area from currently visible building.
rgb=base*(1-ba)+building[:,:,:3]*ba;rgb[forbidden]=rgb[forbidden]*.65+np.array([220,40,55])*.35;im=Image.fromarray(np.uint8(rgb));d=ImageDraw.Draw(im);d.rectangle((0,0,1536,30),fill=(20,20,20));d.text((5,10),'CPU candidate receiver: RED retained new building geometry +4; elsewhere allowed INSIDE sample only',fill='white');im.save(OUT/'receiver-material-review.png')
overlap=[]
for i,a in enumerate(ling):
 both=(a>0)&(treealpha>0);combined=1-(1-a)*(1-treealpha);y1,x1=np.nonzero(both);overlap.append({'phase':i,'positive_sample_overlap_cells':int(both.sum()),'world_sample_bounds_xyxy':None if not len(x1)else[2496+int(x1.min())/2,960+int(y1.min())/2,2496+(int(x1.max())+1)/2,960+(int(y1.max())+1)/2],'max_combined_opacity':float(combined.max()),'max_added_darkening_over_stronger_single':float((combined-np.maximum(a,treealpha)).max()),'not_a_union_compositor':'two independent blend_mix casts darken overlap; future native review required'})
# Conservative envelope intersection from identical source-defined geometry.
import importlib.util
spec=importlib.util.spec_from_file_location('g',P/'tools/earth/build_flat_shadow_gate.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
def envelope(a,r):
 yy,xx=np.nonzero(a>0);lo=np.stack((xx,yy),1)/4-.125;hi=lo+.5;c=np.stack((lo,np.stack((hi[:,0],lo[:,1]),1),hi,np.stack((lo[:,0],hi[:,1]),1)),1)@np.array(r['matrix_rows']).T+np.array(r['translation_logical'])+r['world_origin'];rect=np.concatenate((c.min(1)-1.8,c.max(1)+1.8),1);pts=np.array(r['proxy_points_logical'])+r['world_origin'];rect=np.concatenate((rect,np.concatenate((pts-1.8,pts+1.8),1)));return g.raster(rect,np.array([2496,960]),[1536,1024])
te=envelope(raw[:,:,3],regs['first_tree']);le=[envelope(npca[:,i*512:(i+1)*512],regs[f'lingyunzi{i}'])for i in range(4)]
for i in range(4):overlap[i]['conservative_envelope_overlap_cells']=int((te&le[i]).sum())
write('multi-caster-overlap.json',{'schema':'earth-tree-lingyunzi-overlap-cpu-v1','cast':[1.2,.55],'opacity_each':.25,'blur_logical':.8,'max_two_fully_opaque_alpha_shadows':.4375,'method':'same shader inverse and normalized3x3 alpha filter at2samples/logical; color preview is CPU sRGB approximation, not native parity','phases':overlap,'union_conservative_envelope_overlap_cells':int((te&np.logical_or.reduce(le)).sum())})
for name in ['lingyunzi','first_tree']:
 r=regs['lingyunzi0' if name=='lingyunzi'else 'first_tree'];interface={'schema':'earth-v2-shadow-diagnostic-interface-'+name,'status':'CPU prepared only; parent visual review and explicit GPU authorization still required','scope':'exact current sample instance, no existingSE/Fanggate change','parameter_contract_sha256':receiver['parameter_records_canonical_json_sha256'],'receiver_candidate_sha256':sha(OUT/'receiver-candidate.json'),'receiver_contract_diagnostic_path':'res://diagnostics/earth-shadow-receiver-v2/receiver-candidate.json','mandatory_hall_conditions':receiver['enabling_conditions'],'failure_policy':'hide whole dependent cast immediately; no clipping; no source-hall fallback receiver; body pixels/position unchanged','shadow':{'reference_logical':r['reference_logical'],'slope':r['slope'],'cast':[1.2,.55],'opacity':.25,'blur_logical':.8,'raw_blur':3.2,'density':4,'tint_rgb':[.035,.045,.055]},'world_body_origin':r['world_origin'],'world_transform':'identity logical basis; add existing camera screen_origin once','source_measurement_sha256':sha(P/'art_source/earth_shadow_next_stage_v1/measurements.json'),'producer_sha256':sha(Path(__file__))}
 if name=='lingyunzi':interface.update(body_texture=npc['texture'],body_sha256=npc['texture_sha256'],body_manifest_sha256=sha(P/'assets/earth/npc/lingyunzi_v2/manifest.json'),logical_regions_xywh=[[i*128,0,128,160]for i in range(4)],source_ids=[113,114,115,116],identity={k:npc[k]for k in ['map_id','npc_record_index','map_cell','layer','sort_y','stable_order']},clock='unchanged shared floor(tick/17)%4; common footline for all4 phases')
 else:interface.update(body_texture_unchanged=tree['raw_texture'],shadow_texture=pad['output_texture'],shadow_texture_sha256=pad['output_sha256'],logical_region_xywh=[0,0,314,314],padding_contract_sha256=sha(OUT/'tree-shadow-padding-contract.json'),body_registration_sha256=pad['registration_sha256'],identity={'original_root_cell':[57,34],'source_keys':tree['suppress_source_keys']},one_shadow_for_whole_tree=True,body_depth='seven owners remain original y34/y37 order; no duplicated per-owner casts',root_uncertainty='raw wood root +/-8texels and source +/-4logical; fixed slope0 is2D hypothesis, not recovered3D geometry')
 write(name+'-diagnostic-interface.json',interface)
print(json.dumps({'padding':pad,'overlap':overlap},indent=2))
