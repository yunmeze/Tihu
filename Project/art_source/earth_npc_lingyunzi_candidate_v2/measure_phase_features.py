"""Bounded local pixel-patch temporal measurement only; never moves artwork."""
from pathlib import Path
from PIL import Image
import numpy as np,json
O=Path(__file__).parent;P=O.parents[1]
s=Image.open(P/'art_source/earth_npc_input_plan_v1/lingyunzi/source-four-registered-native.png').convert('RGBA');g=Image.open(O/'raw-v2.png').convert('RGBA')
ss=[np.array(s.crop((j*128,0,(j+1)*128,160))).astype(float)for j in range(4)]
gg=[np.array(g.crop((j*543,0,(j+1)*543,724))).astype(float)for j in range(4)]
source_rois={'face':[53,73,60,80],'left_shoulder':[43,76,51,83],'right_shoulder':[62,78,69,86],'hands':[51,89,60,97],'left_boot':[45,119,51,125],'right_boot':[60,119,66,125]}
raw_rois={'face':[272,125,312,170],'left_shoulder':[187,180,224,215],'right_shoulder':[367,181,399,214],'hands':[271,337,315,381],'left_boot':[198,650,235,681],'right_boot':[365,650,398,681]}
def track(imgs,rois,limit):
 out={}
 for name,(x0,y0,x1,y1) in rois.items():
  template=imgs[0][y0:y1,x0:x1,:3];results=[]
  for im in imgs:
   vals=[]
   for dy in range(-limit,limit+1):
    for dx in range(-limit,limit+1):
     patch=im[y0+dy:y1+dy,x0+dx:x1+dx,:3]
     if patch.shape!=template.shape:continue
     mse=float(np.mean((patch-template)**2));vals.append((mse,dx,dy))
   vals.sort();v=vals[0];results.append({'dx':v[1],'dy':v[2],'rgb_rmse':v[0]**.5,'runner_up_rmse':vals[1][0]**.5})
  out[name]={'roi_phase0_xyxy': [x0,y0,x1,y1],'deltas':results}
 return out
sc=json.loads((O/'review.json').read_text())['uniform_registration']['scale_raw_to_logical']
r={'method':'Exhaustive integer local RGB SSD tracking against phase0; source range +/-5px and generated +/-48rawpx. Diagnostic surface patches only, not skeleton or subpixel exactness; changed cloth/face appearance can bias minima. No artwork transforms applied.','source':track(ss,source_rois,5),'generated':track(gg,raw_rois,70),'generated_scale_to_logical':sc}
for feature,entry in r['generated'].items():
 for d in entry['deltas']:d['logical_dx']=d['dx']*sc;d['logical_dy']=d['dy']*sc
(O/'phase-feature-measurements.json').write_text(json.dumps(r,indent=2)+'\n')
for k in source_rois:
 print(k,'source',[(d['dx'],d['dy'],round(d['rgb_rmse'],1))for d in r['source'][k]['deltas']],'generated logical',[(round(d['logical_dx'],2),round(d['logical_dy'],2),round(d['rgb_rmse'],1))for d in r['generated'][k]['deltas']])
