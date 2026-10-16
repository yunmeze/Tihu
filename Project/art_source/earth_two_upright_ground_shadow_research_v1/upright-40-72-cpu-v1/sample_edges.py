"""CPU mirror of unchanged upright nine-tap alpha. No runtime/GPU claim."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
O=Path(__file__).resolve().parent;P=O.parent.parent/'recovery-work/upright-51-70-runtime-v1/Project';c=json.loads((O/'contract.json').read_text());a=np.array(Image.open(P/'assets/earth/environment/upright_tree_v1/raw.png').convert('RGBA'))[:,:,3]/255.;allowed=np.array(Image.open(O/'allowed-provisional.png'))>0;pool=np.array(Image.open(O/'pool-positive-alpha.png'))>0;excluded=np.array(Image.open(O/'pool-filter-uncertainty-excluded.png'))>0
B=c['world_rect_xyxy'];y,x=np.indices(allowed.shape,dtype=float);gx=(B[0]+(x+.5)/2-c['body_origin'][0])*4.5;gy=(B[1]+(y+.5)/2-c['body_origin'][1])*4.5

def sample(x,y):
 valid=(x>=0)&(y>=0)&(x<a.shape[1])&(y<a.shape[0]);x=np.clip(x,.5,a.shape[1]-.5)-.5;y=np.clip(y,.5,a.shape[0]-.5)-.5;i=x.astype(int);j=y.astype(int);fx=x-i;fy=y-j;ii=np.minimum(i+1,a.shape[1]-1);jj=np.minimum(j+1,a.shape[0]-1)
 return ((a[j,i]*(1-fx)+a[j,ii]*fx)*(1-fy)+(a[jj,i]*(1-fx)+a[jj,ii]*fx)*fy)*valid
alpha=np.zeros_like(gx)
for ky in [-1,0,1]:
 for kx in [-1,0,1]:
  qx=gx+kx*3.6;qy=gy+ky*3.6;sy=(1.55*1329-qy)/.55;sx=qx+1.2*sy-1.2*1329;alpha+=sample(sx,sy)*(2 if kx==0 else 1)*(2 if ky==0 else 1)/16*.25
clip=alpha*allowed
assert not clip[excluded].any(); assert not (alpha[np.array(Image.open(O/'nominal-envelope.png'))==0]>0).any()
# Receiver is applied after body blur. A future linear mask sampler must remain
# within the 5logical exclusion margin; test +/-0.5logical lookup footprint.
leaks=[]
for dy in [-1,0,1]:
 for dx in [-1,0,1]:leaks.append(int((np.roll(allowed,(dy,dx),(0,1))&pool).sum()))
assert max(leaks)==0
r={'sampling':'half-logical centers; exact original body alpha floats, 9tap blur3.6raw, opacity .25','uncut_positive_samples':int((alpha>0).sum()),'clipped_positive_samples':int((clip>0).sum()),'removed_alpha_mass_fraction':float((alpha-clip).sum()/alpha.sum()),'pool_or_margin_nonzero_after_clip':int((clip[excluded]>0).sum()),'allowed_lookup_plusminus_half_logical_pool_hits':leaks,'nominal_support_contains_all_positive_samples':True,'max_clip_alpha':float(clip.max()),'max_duplicate_idempotent':bool(np.array_equal(np.maximum(clip,clip),clip)),'limitations':'CPU centers and mask lookup only. Native bilinear/camera/water edge still requires requested GPU check. Embedded foreground checker shadows not deduplicated.'}
(O/'CPU_ALPHA_EDGE_RESULT.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))

e=np.array(Image.open(O/'root-error-envelope.png'))>0
hit=e&excluded; hy,hx=np.nonzero(hit)
r['error_exclusion_centers_world']=[[B[0]+(int(xx)+.5)/2,B[1]+(int(yy)+.5)/2] for yy,xx in zip(hy,hx)]
r['error_exclusion_actual_blur_positive_samples']=int((alpha[hit]>0).sum())
r['error_exclusion_actual_blur_max_alpha']=float(alpha[hit].max()) if hit.any() else 0
r['error_exclusion_nominal_overlap']=int((hit&(np.array(Image.open(O/'nominal-envelope.png'))>0)).sum())
(O/'CPU_ALPHA_EDGE_RESULT.json').write_text(json.dumps(r,indent=2))
