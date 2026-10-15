#!/usr/bin/env python3
"""CPU-only E/S idle shadow proposal; writes only new study and diagnostic paths.
No engine, GUI, image generation, asset changes, source modifications or Git.
"""
from pathlib import Path
import json, hashlib, importlib.util, sys, io
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates
P=Path(__file__).resolve().parents[2]; OUT=P/'diagnostics/earth-es-idle-shadow-study-v1'; HERE=Path(__file__).parent
inputs={}
def track(q):
 q=Path(q); inputs[str(q.relative_to(P)) if q.is_relative_to(P) else str(q)]=hashlib.sha256(q.read_bytes()).hexdigest();return q
def load(p):return json.loads(track(P/p).read_text())
def image(p):return np.array(Image.open(track(P/p.removeprefix('res://'))).convert('RGBA'))
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
spec=importlib.util.spec_from_file_location('gate',track(P/'tools/earth/build_flat_shadow_gate.py'));g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
gate=load('assets/earth/shadows/se_flat_v1/manifest.json'); allowed=image(gate['allowed']['texture'])[:,:,0]>0; forbidden=image(gate['forbidden']['texture'])[:,:,0]>0
assert hashlib.sha256((P/gate['allowed']['texture'][6:]).read_bytes()).hexdigest()==gate['allowed']['sha256']; assert np.array_equal(~allowed,forbidden)
bindings=[]
for p,h in gate['runtime_input_sha256'].items():bindings.append({'path':p,'matches':hashlib.sha256(track(P/p).read_bytes()).hexdigest()==h})
source=load('data/maps/A13.json')
# Trusted original byte decoder plus explicit native offsets, independently compare frozen full frames.
sys.path.insert(0,str(P/'tools'));from lp_original import read_pack,decode_frame
packs=[]
for p in ['Data/Hero/2.lpRes','Data/Hero/Head/0.lpRes']:
 q=P.parent/'原版游戏'/p;track(q);packs.append(read_pack(q))
proof=[]
for direction,ids in [('e',range(9,13)),('s',range(17,21))]:
 for sid in ids:
  full=Image.new('RGBA',(128,128));part=[]
  for layer,(b,recs,anim,key) in enumerate(packs):
   rec=recs[sid];off,n,ox,oy=rec;raw=Image.open(io.BytesIO(b[off:off+n]));indices=np.array(raw);rgba,meta=decode_frame(b,rec,'Hero/2' if layer==0 else 'Hero/Head/0',True);a=np.array(rgba);kept=a.copy();cut=a.copy();kept[indices==18,3]=0;cut[indices!=18,3]=0
   assert Image.alpha_composite(Image.fromarray(kept),Image.fromarray(cut)).tobytes()==rgba.tobytes()
   full.alpha_composite(rgba,(16+ox,64+oy));part.append({'layer':layer,'native_offset':[ox,oy],'index18_count':int((indices==18).sum()),'non18_pixels_unchanged':True,'partition_recomposes_exactly':True})
  frozen=Image.open(track(P/f'art_source/earth_hero_{direction}_input_plan_v1/source-{sid}.png')).convert('RGBA');assert frozen.tobytes()==full.tobytes();proof.append({'direction':direction,'source_id':sid,'full128_matches_frozen_source':True,'layers':part})
# Actor atlas source boot registration is supporting evidence, not fitted ground truth.
ereg=load('art_source/earth_hero_e_idle_v1/registration-v1.json');sreg=load('art_source/earth_hero_s_idle_edit_v1/registration-review.json')
rois={'e':[(29,81,45,91),(41.5,73,51,80)],'s':[(26,78,38,87),(42,80,54,91)]}
def boot(a,roi,threshold):
 x0,y0,x1,y1=[int(v*4)for v in roi];b=a[y0:y1,x0:x1];ys,xs=np.nonzero(b>=threshold);assert len(xs);yb=ys.max();assert yb+1<b.shape[0], 'ROI clips sole'
 xs=np.where(b[yb]>=threshold)[0]+x0
 return [(float(xs.mean())+.5)/4,(int(yb)+y0+1)/4]
def matrix(s,b):return np.array([[1+1.2*s,-1.2],[s*1.55,-.55]]),np.array([1.2*b,1.55*b])
def projected_rects(a,A,T):
 y,x=np.nonzero(a>0);lo=np.stack((x,y),1)/4-.125;hi=lo+.5
 corners=np.stack([lo,np.stack((hi[:,0],lo[:,1]),1),hi,np.stack((lo[:,0],hi[:,1]),1)],1)@A.T+T
 return np.concatenate((corners.min(1)-1.8,corners.max(1)+1.8),1)
def permitted(env,off,cell):
 base=(np.array(cell)*[48,32]+[-16,-64]+off-[2496,960])*2;bx,by=np.floor(base).astype(int);ex,ey=np.ceil(base+np.array(env.shape[::-1])).astype(int)
 if bx<0 or by<0 or ex>1536 or ey>1024:return False
 # Each fractional mask area touches floor and ceil positions; includes all overlaps.
 for dx in range(int(np.ceil(base[0])-bx)+1):
  for dy in range(int(np.ceil(base[1])-by)+1):
   if not allowed[by+dy:by+dy+env.shape[0],bx+dx:bx+dx+env.shape[1]][env].all():return False
 return True
reports={};masks={};alphas={};models={}
for direction in ['e','s']:
 m=load(f'assets/earth/hero/{direction}_idle_v1/manifest.json');atlas=image(m['texture']);assert inputs[m['texture'][6:]]==m['texture_sha256'];assert m['frame_ticks']==12 and m['texture_density']==4 and m['logical_draw_offset']==[-16,-64] and atlas.shape==(512,2048,4)
 frames=[];points=[];rects=[];aa=[]
 for r in m['records']:
  x,y,w,h=r['region_px'];a=atlas[y:y+h,x:x+w,3];aa.append(a);pts=[boot(a,roi,128)for roi in rois[direction]];points+=pts
  thresholds={str(t):[boot(a,roi,t)for roi in rois[direction]]for t in [64,128,192,254]}
  frames.append({'source_id':r['source_id'],'visible_bottom_edge_points_logical':pts,'alpha_threshold_sensitivity':thresholds,'alpha_positive_texels':int((a>0).sum()),'alpha_1_to15_texels':int(((a>0)&(a<=15)).sum())})
 pts=np.array(points);s,b=np.linalg.lstsq(np.c_[pts[:,0],np.ones(len(pts))],pts[:,1],rcond=None)[0];A,T=matrix(s,b);res=pts[:,1]-(s*pts[:,0]+b)
 for a in aa:rects.append(projected_rects(a,A,T))
 boots=np.concatenate((pts-1.8,pts+1.8),1);rr=np.concatenate(rects+[boots]);off=np.floor(rr[:,:2].min(0)*2)/2;end=np.ceil(rr[:,2:].max(0)*2)/2;size=np.rint((end-off)*2).astype(int);env=g.raster(rr,off,size);g.verify_coverage(env,rr,off)
 threshold_fits=[]
 for t in ['64','128','192','254']:
  p=np.array([p for f in frames for p in f['alpha_threshold_sensitivity'][t]]);sl,bi=np.linalg.lstsq(np.c_[p[:,0],np.ones(len(p))],p[:,1],rcond=None)[0];threshold_fits.append({'threshold':t,'slope':sl,'reference_y_at_x40':sl*40+bi,'determinant':float(np.linalg.det(matrix(sl,bi)[0]))})
 valid=[];blocked=[]
 for x in range(50,70):
  for y in range(28,48):
   if permitted(env,off,[x,y]):valid.append([x,y]);
 probes=[{'cell':cell,'whole_envelope_allowed':permitted(env,off,cell)}for cell in [[61,39],[63,41],[61,37],[63,38],[62,36],[66,35],[66,36],[61.6875,39.6875],[51,39],[67,45]]]
 npts=np.array([f['visible_bottom_edge_points_logical']for f in frames]);
 reports[direction]={'ids':m['source_ids'],'frames':frames,'fixed_line':{'reference_logical':[40,float(s*40+b)],'slope':float(s),'intercept':float(b),'matrix_rows':A.tolist(),'translation_logical':T.tolist(),'determinant':float(np.linalg.det(A)),'fits_all_four_phases_once':True,'maximum_vertical_residual':float(abs(res).max()),'rms_vertical_residual':float(np.sqrt(np.mean(res**2))),'maximum_projected_sole_offset':float(abs(res).max()*np.linalg.norm([1.2,1.55])),'threshold_fits':threshold_fits,'per_phase_point_residuals_y':res.reshape(4,2).tolist(),'visible_proxy_uncertainty_logical_xy':[1,.75],'uncertainty_not_a_statistical_confidence_interval':True},'envelope':{'offset_logical':off.tolist(),'size_logical':(end-off).tolist(),'mask_density':2,'positive_cells':int(env.sum()),'logical_area':float(env.sum()/4),'includes_all_alpha_gt0':True,'full_raw_texel_footprints_and_half_texel_linear_support':True,'padding_logical':1.8,'independent_rectangle_coverage_check':True},'eligible_integer_cells_in_scan_x50_69_y28_47':valid,'eligible_count':len(valid),'probe_results':probes,'source_flags_at_eligible_cells':{'flag_'+str(flag):sum(source['cells'][x*100+y][1]==flag for x,y in valid)for flag in sorted(set(source['cells'][x*100+y][1]for x,y in valid))}}
 masks[direction]=(env,off);alphas[direction]=aa;models[direction]=(A,T)
 np.savez_compressed(OUT/f'{direction}-four-phase-envelope.npz',envelope=env,offset_logical=off)
# Compare physical-light CPU nine-tap projected alpha, not screenshots.
base=load('art_source/earth_shadow_next_stage_v1/measurements.json');regs={r['name']:r for r in base['records']}
y,x=np.indices((1024,1536));world=np.stack((2496+(x+.5)/2,960+(y+.5)/2),axis=0)
def render(a,A,T,origin):
 inv=np.linalg.inv(A);local=world-np.array(origin)[:,None,None]-np.array(T)[:,None,None];h,w=a.shape;out=np.zeros((1024,1536))
 for iy in [-1,0,1]:
  for ix in [-1,0,1]:
   p=np.einsum('ij,jhw->ihw',inv,local+np.array([ix*.8,iy*.8])[:,None,None])*4;ok=(p[0]>=0)&(p[1]>=0)&(p[0]<w)&(p[1]<h);coords=np.stack((np.clip(p[1],.5,h-.5)-.5,np.clip(p[0],.5,w-.5)-.5));out+=map_coordinates(a.astype(float)/255,coords,order=1,mode='nearest',prefilter=False)*ok*(2 if ix==0 else 1)*(2 if iy==0 else 1)/16
 return out*.25
f=load('assets/earth/npc/fangzhang_v1/manifest.json');l=load('assets/earth/npc/lingyunzi_v2/manifest.json');t=load('assets/earth/environment/first_tree_v1/registration.json');fa=image(f['texture'])[:,:,3];la=image(l['texture'])[:,:,3];ta=np.pad(image(t['raw_texture'])[:,:,3],((0,2),(0,2)))
static={}
for name,a,key in [('fang',fa,'fangzhang0'),('tree',ta,'first_tree')]+[(f'ling{i}',la[:,i*512:(i+1)*512],f'lingyunzi{i}')for i in range(4)]:
 r=regs[key];static[name]=render(a,np.array(r['matrix_rows']),np.array(r['translation_logical']),r['world_origin'])
overlap=[]
for direction in ['e','s']:
 A,T=models[direction];env,off=masks[direction]
 for cell in [[61,39],[61,37],[63,38],[62,36],[63,41]]:
  enabled=permitted(env,off,cell);rows=[]
  for i,a in enumerate(alphas[direction]):
   hero=render(a,A,T,np.array(cell)*[48,32]+[-16,-64]) if enabled else np.zeros((1024,1536));pairs={k:int(((hero>1/255)&(v>1/255)).sum())for k,v in static.items()};unionling=np.maximum.reduce([static[f'ling{i}']for i in range(4)]);total=np.maximum.reduce([hero,static['fang'],unionling,static['tree']]);assert total.max()<=.25+1e-12
   rows.append({'source_id':reports[direction]['ids'][i],'pair_overlap_d2_samples_alpha_gt_1_255':pairs,'max_composite_alpha':float(total.max())})
  overlap.append({'direction':direction,'cell':cell,'hero_enabled':enabled,'phases':rows})
for p in ['scripts/earth/flat_shadow_gate.gd','scripts/earth/max_ground_shadow.gd','scripts/earth/sample_world.gd','shaders/earth_max_ground_shadow.gdshader','docs/EARTH_SOURCE_SAMPLE_ENTRY.md','docs/EARTH_ART_BIBLE_V1.md']:track(P/p)
track(Path(__file__))
report={'status':'CPU_ONLY_PROPOSAL_NOT_APPROVED_NOT_RUNTIME','parameters':{'cast':[1.2,.55],'opacity':.25,'logical_blur':.8,'raw_blur_d4':3.2,'density':4,'unchanged_idle_ticks':12,'walk_run_excluded':True},'source_byte_proof':proof,'source_index18_role':'exact index partition only; shadow semantics inferred; candidate alpha never removes index/color/low alpha','receiver':{'sample_world_rect':[2496,960,768,512],'allowed_d2_cells':int(allowed.sum()),'forbidden_d2_cells':int(forbidden.sum()),'allowed_logical_area':float(allowed.sum()/4),'allowed_fraction':float(allowed.mean()),'runtime_input_checks':bindings,'no_envelope_reuse':True},'directions':reports,'overlap':overlap,'input_sha256':inputs}
dump(HERE/'measurements.json',report);dump(OUT/'measurements.json',report)
print(json.dumps({d:{'fixed_line':r['fixed_line'],'envelope':r['envelope'],'eligible_count':r['eligible_count'],'probes':r['probe_results']}for d,r in reports.items()},indent=2));print('existing gate mismatches:',[r for r in bindings if not r['matches']]);print('Wrote isolated diagnostics only.')
