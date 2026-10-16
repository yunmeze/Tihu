from pathlib import Path
import numpy as np,json
from PIL import Image,ImageDraw
O=Path(__file__).parent;z=np.load(O/'render_orientation_safe61.npz');uv=z['uv'];r=z['rest'];q=z['vertices'];t=z['triangles'];a=np.array(Image.open(O.parent/'south-walk-mesh-correction-v1/raw/61.png'))[:,:,3];c=np.floor(uv[t].mean(1)).astype(int);alpha=a[c[:,1],c[:,0]].astype(float)
R=np.stack([r[t[:,1]]-r[t[:,0]],r[t[:,2]]-r[t[:,0]]],2);Q=np.stack([q[t[:,1]]-q[t[:,0]],q[t[:,2]]-q[t[:,0]]],2);J=Q@np.linalg.inv(R);sv=np.linalg.svd(J,compute_uv=False);ratio=sv[:,0]/sv[:,1];det=np.linalg.det(J)
edges,cnt=np.unique(np.sort(np.concatenate([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]),axis=1),axis=0,return_counts=True);b=edges[cnt==1];A=q[b[:,0]];B=q[b[:,1]];hits=[];touch=[]
def cross(v,w):return v[...,0]*w[...,1]-v[...,1]*w[...,0]
for k in range(len(b)):
 idx=np.arange(k+1,len(b));idx=idx[(b[idx,0]!=b[k,0])&(b[idx,0]!=b[k,1])&(b[idx,1]!=b[k,0])&(b[idx,1]!=b[k,1])];C=A[idx];D=B[idx];ab=B[k]-A[k];cd=D-C;t1=cross(ab,C-A[k]);t2=cross(ab,D-A[k]);t3=cross(cd,A[k]-C);t4=cross(cd,B[k]-C);v=idx[(t1*t2< -1e-12)&(t3*t4< -1e-12)];hits.extend([[k,int(j)] for j in v])
result={'raw_nonzero_pixel_count':int((a>0).sum()),'covered_unique_pixel_count':len(np.unique(c,axis=0)),'newly_painted_or_dropped_alpha_pixels':0,'triangles':len(t),'flips':int((det<=0).sum()),'signed_area_ratio_min_max':[float(det.min()),float(det.max())],'proper_render_boundary_intersections':len(hits),'proper_intersection_pairs':hits[:20],'scope':'proper boundary crossings checked; tangency/near-contact still needs visual inspection','all_alpha_weighted_area_fraction_anisotropy_gt1_5':float(alpha[ratio>1.5].sum()/alpha.sum()),'distributions':{}}
for name,mask in [('core_alpha64plus',alpha>=64),('fringe_alpha1to63',alpha<64),('visible_alpha128plus',alpha>=128)]:
 s=sv[mask];v=ratio[mask];aa=alpha[mask];result['distributions'][name]={'triangles':int(mask.sum()),'singular_min_max':[float(s.min()),float(s.max())],'max_anisotropy':float(v.max()),'anisotropy_percentiles_50_95_99':np.percentile(v,[50,95,99]).tolist(),'alpha_weighted_fraction_gt1_5':float(aa[v>1.5].sum()/aa.sum())}
# Raw-coordinate distortion locator only, never a fake Godot render.
im=Image.open(O.parent/'south-walk-mesh-correction-v1/raw/61.png').convert('RGBA');bg=Image.new('RGBA',im.size,(75,80,85,255));bg.alpha_composite(im);d=ImageDraw.Draw(bg)
for k in np.where((ratio>1.5)&(alpha>=64))[0]:d.polygon([tuple(v) for v in uv[t[k]]],outline=(255,70,50,255))
bg.save(O/'DISTORTION_LOCATOR_RAW61.png');(O/'FINAL_CPU_AUDIT.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
