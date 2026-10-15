"""Read-only uniform-scale tree geometry diagnostic. Does not mutate raw RGBA."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent;G=P/'diagnostics/art_source/a13-first-tree';raw=Image.open(D/'raw.png').convert('RGBA');source=Image.open(G/'source-composite.png').convert('RGBA')
points=[('root_wood_contact',[119,300],[498,1224],4,8),('central_leader_tip',[141,2],[575,20],3,10),('upper_left_tip',[67,27],[275,118],3,10),('upper_right_tip',[183,44],[756,186],3,10),('long_right_branch_tip',[273,176],[1120,730],4,12),('lower_left_tip',[69,242],[281,1000],4,12),('left_mid_outer_cluster',[3,123],[35,505],4,12)]
y=np.array([p[1]for p in points],float);x=np.array([p[2]for p in points],float);dx=x[1:]-x[0];dy=y[1:]-y[0];s=float(np.sum(dx*dy)/np.sum(dx*dx));t=y[0]-s*x[0];pred=x*s+t;errors=np.linalg.norm(pred-y,axis=1)
# Root-preserving similarity with no rotation/shear: actual entire-image registration.
transformed=raw.transform(source.size,Image.Transform.AFFINE,(1/s,0,-t[0]/s,0,1/s,-t[1]/s),resample=Image.Resampling.BICUBIC)
board=Image.new('RGBA',(624,341),(88,98,88,255));board.alpha_composite(source,(0,30));board.alpha_composite(transformed,(312,30));d=ImageDraw.Draw(board);d.text((6,7),'SOURCE with original baked cast',fill='white');d.text((318,7),'NEW root-locked uniform scale',fill='white')
for off in [0,312]:
 q=(119+off,300+30);d.ellipse((q[0]-3,q[1]-3,q[0]+3,q[1]+3),outline='cyan',width=1)
board.convert('RGB').save(G/'candidate-v1-native-scale-ab.jpg')
land=board.copy();ld=ImageDraw.Draw(land)
for i,p in enumerate(points):
 for q,off in [(y[i],0),(pred[i],312)]:
  px,py=q[0]+off,q[1]+30;ld.ellipse((px-3,py-3,px+3,py+3),outline='cyan',width=1);ld.text((px+4,py),str(i),fill='white')
land.convert('RGB').save(G/'candidate-v1-landmark-ab.jpg')
a=np.array(raw);edges={'top':int(a[0,:,3].max()),'bottom':int(a[-1,:,3].max()),'left':int(a[:,0,3].max()),'right':int(a[:,-1,3].max())};result={'status':'geometry/material candidate only; no owner partition or native test','raw_sha256':hashlib.sha256((D/'raw.png').read_bytes()).hexdigest(),'registration':{'kind':'one uniform scale plus translation, root exactly anchored; no rotation/shear/warp','scale':s,'translation_source_canvas':t.tolist(),'source_world_origin':[2642,790],'raw_world_origin':(t+[2642,790]).tolist()},'landmarks':[{'id':p[0],'source_xy':p[1],'candidate_raw_xy':p[2],'source_manual_uncertainty_px':p[3],'candidate_manual_uncertainty_raw_px':p[4],'mapped_source_xy':pred[i].tolist(),'residual_source_px':float(errors[i])}for i,p in enumerate(points)],'crown_independent_check':{'rms_source_px':float(np.sqrt(np.mean(errors[1:]**2))),'max_source_px':float(errors[1:].max()),'method':'six visible branch/cluster landmarks; actual species/leaf outline remains a design comparison, not pixel identical'},'alpha_edge_max':edges,'limits':['No threshold, color change, trimming or alpha normalization applied to raw.','Requested4% padding not achieved: very faint alpha1 touches three edges; strong visible crown/root remains inset. Preserve these pixels.','Root read is visible wood contact band +/-4source and +/-8raw, not alpha bottom or ground shadow.','Source baked checker extends right and is intentionally absent in candidate; source full alpha bbox cannot be a crown-width target.','A/B preview uses diagnostic bicubic resampling only. No runtime or per-owner textures created.','Golden highlights are noticeably brighter/cleaner than low-resolution source; parent material review pending.']}
(D/'geometry-diagnostic.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'scale':s,'translation':t.tolist(),'crown_rms':result['crown_independent_check']['rms_source_px'],'max':result['crown_independent_check']['max_source_px'],'edges':edges}))
if __name__=='__main__':pass
