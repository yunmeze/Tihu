#!/usr/bin/env python3
"""Read-only CPU4caster numeric comparison. Writes this diagnostic JSON only."""
from pathlib import Path
import json,hashlib,itertools
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates
P=Path(__file__).resolve().parents[2];OUT=P/'diagnostics/earth-max-shadow-study';OUT.mkdir(parents=True,exist_ok=True);inputs={}
def load(p):
 q=P/p;inputs[p]=hashlib.sha256(q.read_bytes()).hexdigest();return json.loads(q.read_text())
def rgba(p):
 p=p.removeprefix('res://');q=P/p;inputs[p]=hashlib.sha256(q.read_bytes()).hexdigest();return np.array(Image.open(q).convert('RGBA'))
measure=load('art_source/earth_shadow_next_stage_v1/measurements.json');regs={r['name']:r for r in measure['records']};gate=load('assets/earth/shadows/se_flat_v1/manifest.json');allowed=rgba(gate['allowed']['texture'])[:,:,0]>0;env=rgba(gate['envelope']['texture'])[:,:,0]>0;source=load('data/maps/A13.json')
y,x=np.indices((1024,1536));world=np.stack((2496+(x+.5)/2,960+(y+.5)/2),axis=0)
def projected(a,r):
 inv=np.linalg.inv(np.array(r['matrix_rows']));base=world-np.array(r['world_origin'])[:,None,None];T=np.array(r['translation_logical']);h,w=a.shape;result=np.zeros((1024,1536),float)
 for iy in [-1,0,1]:
  for ix in [-1,0,1]:
   p=np.einsum('ij,jhw->ihw',inv,base+np.array([ix*.8,iy*.8])[:,None,None]-T[:,None,None])*4;valid=(p[0]>=0)&(p[1]>=0)&(p[0]<w)&(p[1]<h);coords=np.stack((np.clip(p[1],.5,h-.5)-.5,np.clip(p[0],.5,w-.5)-.5));v=map_coordinates(a.astype(float)/255,coords,order=1,mode='nearest',prefilter=False);result+=v*valid*(2 if ix==0 else 1)*(2 if iy==0 else 1)/16
 return result*.25
f=load('assets/earth/npc/fangzhang_v1/manifest.json');l=load('assets/earth/npc/lingyunzi_v2/manifest.json');t=load('assets/earth/environment/first_tree_v1/registration.json');fa=rgba(f['texture'])[:,:,3];la=rgba(l['texture'])[:,:,3];ta=rgba(t['raw_texture'])[:,:,3];tp=np.pad(ta,((0,2),(0,2)));static={'fang':projected(fa,regs['fangzhang0']),'ling':projected(la[:,:512],regs['lingyunzi0']),'tree':projected(tp,regs['first_tree'])}
def stats(arrays):
 keys=list(arrays);aa=np.stack(list(arrays.values()));maximum=aa.max(0);over=1-np.prod(1-aa,axis=0);multiplicity=(aa>1/255).sum(0)
 return {'independent_blend_alpha_max':float(over.max()),'max_composite_alpha_max':float(maximum.max()),'max_extra_alpha_removed':float((over-maximum).max()),'overlap_samples_alpha_gt_1_255':int((multiplicity>=2).sum()),'triple_overlap_samples':int((multiplicity>=3).sum()),'quad_overlap_samples':int((multiplicity>=4).sum()),'pairs':{a+'+'+b:int(((arrays[a]>1/255)&(arrays[b]>1/255)).sum())for a,b in itertools.combinations(keys,2)},'single_caster_idempotent':bool(np.array_equal(np.maximum(aa[0],aa[0]),aa[0])),'order_independent':bool(np.array_equal(np.maximum.reduce(aa),np.maximum.reduce(aa[::-1]))),'max_composite_opacity_le_025':bool((maximum<=.25+1e-12).all())}
def hero_allowed(cell):
 origin=np.array(cell)*[48,32]+[-16,-64];base=(origin+gate['envelope']['offset_logical']-[2496,960])*2;assert np.all(base==np.floor(base));bx,by=base.astype(int);h,w=env.shape
 if bx<0 or by<0 or bx+w>1536 or by+h>1024:return False
 return bool(allowed[by:by+h,bx:bx+w][env].all())
rows=[]
for cell,action,sid in [([61,39],'idle',13),([61,37],'idle',13),([63,38],'idle',13),([63,38],'walk',51),([62,36],'idle',13)]:
 m=load(f'assets/earth/hero/se_{action}_v1/manifest.json');record=next(r for r in m['records']if r['source_id']==sid);x,y,w,h=record['region_px'];a=rgba(m['texture'])[y:y+h,x:x+w,3];s=-.342818;ref=np.array([40,85.2463]);b=ref[1]-s*ref[0];r={'matrix_rows':[[1+1.2*s,-1.2],[s*1.55,-.55]],'translation_logical':[1.2*b,1.55*b],'world_origin':(np.array(cell)*[48,32]+[-16,-64]).tolist()};enabled=hero_allowed(cell);ha=projected(a,r) if enabled else np.zeros((1024,1536));arrays=static|{'hero':ha};row={'hero_cell':cell,'action':action,'source_id':sid,'hero_original_gate_allows':enabled,'source_flag':source['cells'][cell[0]*100+cell[1]][1],'static_three':stats(static),'four_casters':stats(arrays)};rows.append(row)
for dep in ['scripts/earth/sample_world.gd','scripts/earth/flat_shadow_gate.gd','scripts/earth/fangzhang_shadow_gate.gd','scripts/art/density_alpha_ground_shadow.gd','shaders/density_alpha_ground_shadow.gdshader']:
 inputs[dep]=hashlib.sha256((P/dep).read_bytes()).hexdigest()
report={'schema':'earth-four-caster-max-alpha-study-v1','status':'CPU proposal only; production renderer/gates/art unchanged; noGUI/GPU','parameters':{'cast':[1.2,.55],'opacity_each':.25,'blur_logical':.8,'sample_density':2,'ling_phase':0,'tree_padding':'2px right/bottom transparent, original1254 unchanged'},'definitions':{'independent':'1-product(1-a_i)','proposed':'max(a_i) AFTER each existing9tap blur and its own gate','theoretical_n_full_casters':{'one':.25,'two':.4375,'three':.578125,'four':.68359375,'proposed_any_1_to4':.25},'sample_scope':'five explicit actor states only; not exhaustive movement or native occlusion; rejected hero contributes zero'},'cases':rows,'input_sha256':inputs};(OUT/'measurements.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(rows,indent=2))
