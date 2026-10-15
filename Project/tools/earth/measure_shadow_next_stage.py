#!/usr/bin/env python3
"""CPU-only measurement of immutable art/manifests. Writes ignored diagnostics only.
Run from any cwd: python Project/tools/earth/measure_shadow_next_stage.py
Requires numpy and Pillow. No GPU, production texture, runtime or source-archive writes."""
from pathlib import Path
import hashlib,json,importlib.util
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parents[2]
OUT=P/'diagnostics/earth-shadow-next-stage'
OUT.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('gate',P/'tools/earth/build_flat_shadow_gate.py');gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
inputs={}
def read(p):
 q=P/p;inputs[p]=hashlib.sha256(q.read_bytes()).hexdigest();return json.loads(q.read_text())
def image(p):
 p=p.removeprefix('res://');q=P/p;inputs[p]=hashlib.sha256(q.read_bytes()).hexdigest();return np.array(Image.open(q).convert('RGBA'))
f=read('assets/earth/npc/fangzhang_v1/manifest.json');l=read('assets/earth/npc/lingyunzi_v2/manifest.json');t=read('assets/earth/environment/first_tree_v1/registration.json')
fr=read('art_source/earth_npc_fangzhang_candidate_v1/review.json');lr=read('art_source/earth_npc_lingyunzi_candidate_v2/review.json')
read('art_source/earth_npc_lingyunzi_candidate_v2/x-only-registration.json');read('art_source/earth_npc_lingyunzi_candidate_v2/phase-feature-measurements.json')
gm=read('assets/earth/shadows/se_flat_v1/manifest.json');allowed=image(gm['allowed']['texture'])[:,:,0]>0
assert inputs[gm['allowed']['texture'].removeprefix('res://')]==gm['allowed']['sha256']
for dep,expected in gm['runtime_input_sha256'].items():
 q=P/dep;actual=hashlib.sha256(q.read_bytes()).hexdigest();assert actual==expected,(dep,actual,expected);inputs[dep]=actual
for dep in ['scripts/earth/sample_world.gd','scripts/earth/flat_shadow_gate.gd','scripts/earth/fangzhang_candidate.gd']:
 inputs[dep]=hashlib.sha256((P/dep).read_bytes()).hexdigest()
records=[]
for name,m,review in [('fangzhang',f,fr),('lingyunzi',l,lr)]:
 if name=='fangzhang':
  s=m['registration']['uniform_scale_raw_to_logical'];tr=np.array(m['registration']['translation_to_logical_canvas']);points=[np.array(x['raw_generated'])*s+tr for x in review['landmarks'] if 'boot' in x['name']]
 else:
  s=m['registration']['shared_scale_raw_to_logical'];tr=np.array(m['registration']['shared_translation_logical']);points=[np.array(x['generated_raw'])*s+tr for x in review['landmarks_phase0'] if 'boot' in x['name']]
 slope=float((points[1][1]-points[0][1])/(points[1][0]-points[0][0]));a=image(m['texture'])[:,:,3]
 for i in range(1 if name=='fangzhang' else 4): records.append((name+str(i),a[:,i*512:(i+1)*512],4,np.array(m['world_cell_origin'])+m['logical_draw_offset'],points[0],slope,points))
a=image(t['raw_texture'])[:,:,3];r=t['whole_tree_registration'];records.append(('first_tree',a,4,np.array(r['world_top_left']),np.array(r['manual_root_raw_xy'])/4,0,[np.array(r['manual_root_raw_xy'])/4]))
result=[]
for name,a,d,origin,ref,slope,points in records:
 cast=np.array([1.2,.55]);b=ref[1]-slope*ref[0];A=np.array([[1+cast[0]*slope,-cast[0]],[slope*(1+cast[1]),-cast[1]]]);T=np.array([cast[0]*b,(1+cast[1])*b]);y,x=np.nonzero(a>0)
 lo=np.stack((x,y),1)/d-.5/d;hi=lo+2/d
 corners=np.stack([lo,np.stack((hi[:,0],lo[:,1]),1),hi,np.stack((lo[:,0],hi[:,1]),1)],1)@A.T+T+origin
 rects=np.concatenate((corners.min(1)-1.8,corners.max(1)+1.8),1)
 bp=np.array(points)+origin;rects=np.concatenate((rects,np.concatenate((bp-1.8,bp+1.8),1)))
 bounds=np.r_[rects[:,:2].min(0),rects[:,2:].max(0)];inside=bool(np.all(bounds[:2]>=[2496,960]) and np.all(bounds[2:]<=[3264,1472]))
 mask=gate.raster(rects,np.array([2496,960]),[1536,1024]);gate.verify_coverage(mask,rects,np.array([2496,960]));bad=mask&~allowed
 frame=np.array([[0,0],[a.shape[1]/d,0],[a.shape[1]/d,a.shape[0]/d],[0,a.shape[0]/d]])@A.T+T+origin
 nz=np.nonzero(bad);bb=None if not len(nz[0]) else [2496+float(nz[1].min())/2,960+float(nz[0].min())/2,2496+float(nz[1].max()+1)/2,960+float(nz[0].max()+1)/2]
 result.append(dict(name=name,raw_size=list(a.shape[::-1]),density=d,world_origin=origin.tolist(),reference_logical=ref.tolist(),proxy_points_logical=[p.tolist() for p in points],slope=slope,determinant=float(np.linalg.det(A)),matrix_rows=A.tolist(),translation_logical=T.tolist(),cast=cast.tolist(),blur_logical=.8,raw_blur=3.2,frame_draw_bounds_world_xyxy=np.r_[frame.min(0)-1.8,frame.max(0)+1.8].tolist(),alpha_support_bounds_world_xyxy=bounds.tolist(),envelope_inside_sample=inside,conservative_overlap_forbidden_cells=int(bad.sum()),overlap_bounds_world_xyxy=bb,whole_shadow_gate_pass=inside and not bool(bad.any()),positive_alpha_texels=len(x),helper_exact_region_compatible=all(n%d==0 for n in a.shape)))
# Foot-region alpha edge checks are observations, never per-frame ground fitting.
for rr in result:
 name=rr['name']
 if name.startswith('lingyunzi'):
  phase=int(name[-1]);body=image(l['texture'])[:,phase*512:(phase+1)*512,3]; probes=[]
  for p in rr['proxy_points_logical']:
   x0,y0=np.floor((np.array(p)-[3,2])*4).astype(int);x1,y1=np.ceil((np.array(p)+[3,2])*4).astype(int)
   yy,xx=np.nonzero(body[y0:y1,x0:x1]>=128); maxy=int(yy.max()+y0)
   probes.append({'roi_raw_xyxy':[int(x0),int(y0),int(x1),int(y1)],'alpha128_lower_edge_logical_y':(maxy+1)/4,'proxy_logical_y':p[1]})
  rr['fixed_boot_roi_observations']=probes
for rr,record in zip(result,records):
 _,a,d,origin,ref,slope,points=record;y,x=np.nonzero(a>=128);h=ref[1]+slope*((x+.5)/d-ref[0])-(y+.5)/d
 rr['opaque_proxy_height_range']=[float(h.min()),float(h.max())];rr['opaque_below_receiver_fraction']=float((h<0).mean())
assert inputs[f['texture'].removeprefix('res://')]==f['texture_sha256']
assert inputs[l['texture'].removeprefix('res://')]==l['texture_sha256']
assert inputs[t['raw_texture'].removeprefix('res://')]==t['raw_sha256']
report=dict(schema='earth-shadow-next-stage-cpu-v1',status='CPU measurements only; parent authorized Fangzhang-only GPU diagnostic; no GPU result claimed',method='same conservative full raw-texel plus half-texel bilinear support and 1.8 logical AABB growth as existing gate; includes visible proxies. No PNG emitted. Fixed Lingyunzi phase0 receiver; body phases untouched.',records=result,input_sha256=inputs)
(OUT/'measurements.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(result,indent=2))

rr=result[0]
interface={
 'schema':'earth-fangzhang-shadow-diagnostic-interface-v1',
 'status':'parent accepted Fangzhang-only next GPU diagnostic; no runtime changed; runner must verify inputs before use',
 'identity':{k:f[k] for k in ['map_id','npc_record_index','map_cell','appearance','direction_slot','source_ids','layer','sort_y','stable_order']},
 'body':{'texture':f['texture'],'sha256':f['texture_sha256'],'raw_atlas_size':[512,640],'logical_region_xywh':[0,0,128,160],'density':4,'world_origin':[3040,1080],'logical_basis':[[1,0],[0,1]],'camera_translation':'add sample_world.screen_origin() once; never divide translation by density','body_transform_unchanged':True},
 'shadow':{'reference_logical':rr['reference_logical'],'slope':rr['slope'],'cast':[1.2,.55],'opacity':.25,'logical_blur':.8,'raw_blur':3.2,'tint_rgb':[.035,.045,.055],'determinant':rr['determinant'],'single_compositing_pass':True,'four_ids_same_region':True,'phase_clock':'floor(shared_tick/17)%4; unchanged'},
 'feet':{'local':rr['proxy_points_logical'],'world':(np.array(rr['proxy_points_logical'])+[3040,1080]).tolist(),'fixed_all_phases':True,'raw_landmark_uncertainty_px':15,'registration_scale':f['registration']['uniform_scale_raw_to_logical']},
 'receiver':{'allowed':gm['allowed'],'sample_world_rect':gm['sample_world_rect'],'mask_density':2,'forbidden_dilation_logical':4,'alpha_support_world_xyxy':rr['alpha_support_bounds_world_xyxy'],'forbidden_overlap_cells':rr['conservative_overlap_forbidden_cells'],'whole_envelope_required':True,'do_not_call_hero_gate_allows_with_npc_cell':True,'envelope_recipe':'tools/earth/measure_shadow_next_stage.py per-texel AABB, alpha>0, half-texel bilinear support, plus1.8logical and fixed feet; fixed world origin, no PNG emitted','envelope_gate_result':rr['whole_shadow_gate_pass']},
 'failure_policy':'hide new shadow on any mismatch; never change body pixels/position; source fallback means new shadow off; do not resurrect checker behind valid candidate',
 'scope':'diagnostic scene only; Fangzhang record0 only; no Lingyunzi/tree cast, no helper/runtime changes authorized by this artifact',
 'input_sha256':inputs,
 'measurement_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'measurement_report_sha256':hashlib.sha256((OUT/'measurements.json').read_bytes()).hexdigest()
}
(OUT/'fangzhang-diagnostic-interface.json').write_text(json.dumps(interface,indent=2)+'\n')
