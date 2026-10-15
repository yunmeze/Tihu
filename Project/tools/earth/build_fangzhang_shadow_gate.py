#!/usr/bin/env python3
"""Build the fixed record0 envelope from immutable body alpha and approved proxy.
Research measurements are refreshed only in ignored diagnostics, never the frozen v1 archive.
"""
from pathlib import Path
import runpy,hashlib,json
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parents[2]
m=runpy.run_path(str(P/'tools/earth/measure_shadow_next_stage.py'))
name,a,d,origin,ref,slope,points=m['records'][0]
cast=np.array([1.2,.55]);b=ref[1]-slope*ref[0]
A=np.array([[1+cast[0]*slope,-cast[0]],[slope*(1+cast[1]),-cast[1]]]);T=np.array([cast[0]*b,(1+cast[1])*b])
y,x=np.nonzero(a>0);lo=np.stack((x,y),1)/d-.5/d;hi=lo+2/d
corners=np.stack([lo,np.stack((hi[:,0],lo[:,1]),1),hi,np.stack((lo[:,0],hi[:,1]),1)],1)@A.T+T+origin
rects=np.concatenate((corners.min(1)-1.8,corners.max(1)+1.8),1)
bp=np.array(points)+origin;rects=np.concatenate((rects,np.concatenate((bp-1.8,bp+1.8),1)))
mask=m['gate'].raster(rects,np.array([2496,960]),[1536,1024]);m['gate'].verify_coverage(mask,rects,np.array([2496,960]))
assert np.all(rects[:,:2]>=[2496,960]) and np.all(rects[:,2:]<=[3264,1472])
assert not np.any(mask&~m['allowed'])
out=P/'assets/earth/shadows/fangzhang_flat_v1';out.mkdir(parents=True,exist_ok=True)
Image.fromarray(mask.astype('uint8')*255,'L').save(out/'envelope.png')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((P/'diagnostics/earth-shadow-next-stage/fangzhang-diagnostic-interface.json').read_text())
r['schema']='earth-fixed-fangzhang-flat-shadow-v1';r['status']='Bounded record0 candidate; no other NPC or environment shadows'
r['envelope']={'texture':'res://assets/earth/shadows/fangzhang_flat_v1/envelope.png','texture_size':[1536,1024],'sha256':sha(out/'envelope.png'),'origin_world':[2496,960],'density':2}
r['allowed']=m['gm']['allowed']
inputs=dict(m['gm']['runtime_input_sha256'])
for p in ['assets/earth/npc/fangzhang_v1/manifest.json','assets/earth/npc/fangzhang_v1/body.png','scripts/earth/fangzhang_candidate.gd','scripts/earth/instance_identity_guard.gd','scripts/earth/sample_world.gd','scripts/art/density_alpha_ground_shadow.gd','shaders/density_alpha_ground_shadow.gdshader']:
 inputs[p]=sha(P/p)
r['runtime_input_sha256']=inputs
r['provenance_input_sha256']=r.pop('input_sha256')
r['scope']='Only original A13 record0 at64,37, fixed world origin3040,1080; full envelope must fit source/new-hall conservative allowed mask. Source-project byte verification; packed export unverified.'
(out/'manifest.json').write_text(json.dumps(r,indent=2)+'\n')
print('FANGZHANG_FIXED_GATE',sha(out/'manifest.json'),'pixels',int(mask.sum()))
