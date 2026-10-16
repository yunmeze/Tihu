from pathlib import Path
import numpy as np,json,time,hashlib
from PIL import Image
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import factorized
from scipy.ndimage import label
O=Path(__file__).parent;src=O.parent/'south-walk-mesh-correction-v1/raw/61.png';a=np.array(Image.open(src))[:,:,3];start=time.time()
# Each alpha>=64 occupied raster pixel owns its square. No domain filling/dilation.
mask=a>=64;yy,xx=np.where(mask);corners=np.stack([np.stack([xx,yy],1),np.stack([xx+1,yy],1),np.stack([xx+1,yy+1],1),np.stack([xx,yy+1],1)],1)
uv,inv=np.unique(corners.reshape(-1,2),axis=0,return_inverse=True);quad=inv.reshape(-1,4);tri=np.concatenate([quad[:,[0,1,2]],quad[:,[0,2,3]]]);uv=uv.astype(float);rest=uv*.72+np.array([162-.72*268,62-.72*41]);n=len(uv)
edges=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0);i,j=edges.T;w=np.ones(len(edges));cent=(uv[i]+uv[j])/2
# Visible armor plates only; no joint interpretation. These rectangles remain frozen.
patches=[{'name':'screen-left visible armor/boot material patch','box':[229, 307, 268, 340]},{'name':'screen-right visible armor/boot material patch','box':[282, 304, 326, 340]}]
for pat in patches:
 x0,y0,x1,y1=pat['box'];v=(cent[:,0]>=x0)&(cent[:,0]<=x1)&(cent[:,1]>=y0)&(cent[:,1]<=y1);w[v]=20
upper=uv[:,1]<=230;toeL=(uv[:,0]<273)&(uv[:,1]>=338);toeR=(uv[:,0]>280)&(uv[:,1]>=435);fixed=upper|toeL|toeR;free=~fixed;fi=np.where(fixed)[0];fr=np.where(free)[0]
delta=np.zeros_like(rest);delta[toeL]=[-8.320000000000022, 7.920000000000016];delta[toeR]=[-2.8400000000000034, -11.680000000000007]
L=coo_matrix((np.r_[w,w,-w,-w],(np.r_[i,j,i,j],np.r_[i,j,j,i])),shape=(n,n)).tocsc();solve=factorized(L[fr][:,fr]);Lfc=L[fr][:,fi];e=rest[i]-rest[j]
def areas(q):
 x=q[tri[:,1]]-q[tri[:,0]];y=q[tri[:,2]]-q[tri[:,0]];return x[:,0]*y[:,1]-x[:,1]*y[:,0]
A0=areas(rest);assert np.all(A0>0)
def b_rhs(q):
 de=q[i]-q[j];C=np.zeros((n,2,2));outer=w[:,None,None]*de[:,:,None]*e[:,None,:];np.add.at(C,i,outer);np.add.at(C,j,outer);U,S,Vh=np.linalg.svd(C);R=U@Vh;bad=np.linalg.det(R)<0;U[bad,:,1]*=-1;R=U@Vh
 v=.5*w[:,None]*np.einsum('nij,nj->ni',R[i]+R[j],e);b=np.zeros((n,2));np.add.at(b,i,v);np.add.at(b,j,-v);return b
q=rest.copy();log=[];status='bounded_iteration_candidate'
for stage in range(1,6):
 target=rest+delta*(stage/5)
 for it in range(40):
  b=b_rhs(q);candidate=q.copy();candidate[fi]=target[fi];candidate[fr]=solve(b[fr]-Lfc@target[fi]);step=1.;accepted=False
  for back in range(24):
   trial=q+step*(candidate-q);ratios=areas(trial)/A0
   if ratios.min()>.1:accepted=True;break
   step*=.5
  if not accepted:status='orientation_backtracking_failed';break
  change=np.max(np.linalg.norm(trial-q,axis=1));q=trial;drive=float(np.max(np.linalg.norm(q[fi]-target[fi],axis=1)));log.append({'stage':stage,'iteration':it,'step':step,'max_change_HD':float(change),'stage_drive_error_HD':drive,'min_signed_area_ratio':float(ratios.min())})
  if change<.003 and drive<.01:break
 if status!='bounded_iteration_candidate':break
 if log[-1]['step']<1e-5 or log[-1]['stage_drive_error_HD']>.05:status='stalled_before_target';break
np.savez_compressed(O/'candidate61.npz',uv=uv,rest=rest,vertices=q,triangles=tri,edges=edges,weights=w,upper=upper,toeL=toeL,toeR=toeR)
# Relative deformation singular values on exact mechanical triangles.
u=rest[tri];v=q[tri];Ar=np.stack([u[:,1]-u[:,0],u[:,2]-u[:,0]],axis=2);Br=np.stack([v[:,1]-v[:,0],v[:,2]-v[:,0]],axis=2);J=Br@np.linalg.inv(Ar);sv=np.linalg.svd(J,compute_uv=False);ratio=sv[:,0]/sv[:,1];dets=np.linalg.det(J)
patch_stats=[]
for pat in patches:
 x0,y0,x1,y1=pat['box'];sel=(uv[:,0]>=x0)&(uv[:,0]<=x1)&(uv[:,1]>=y0)&(uv[:,1]<=y1);X=rest[sel];Y=q[sel];xc=X-X.mean(0);yc=Y-Y.mean(0);U,S,Vh=np.linalg.svd(xc.T@yc);R=U@Vh;res=np.linalg.norm(xc@R-yc,axis=1);patch_stats.append(dict(pat,vertices=int(sel.sum()),rigid_fit_rms_HD=float(np.sqrt((res**2).mean())),rigid_fit_max_HD=float(res.max())))
result={'phase':61,'status':status,'raw_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'seconds':time.time()-start,'domain':'union of alpha>=64 pixel squares,1HD, no fill/dilation; rendering fringe NOT built yet','foreground_pixels':int(mask.sum()),'vertices':n,'triangles':len(tri),'upper_fixed_vertices':int(upper.sum()),'toeL_translation_vertices':int(toeL.sum()),'toeR_translation_vertices':int(toeR.sum()),'max_upper_movement_HD':float(np.linalg.norm(q[upper]-rest[upper],axis=1).max()),'final_driving_error_HD':float(np.linalg.norm(q[fi]-(rest+delta)[fi],axis=1).max()),'negative_area_triangles':int((dets<=0).sum()),'area_ratio_min_max':[float(dets.min()),float(dets.max())],'relative_singular_value_min_max':[float(sv.min()),float(sv.max())],'anisotropy_max':float(ratio.max()),'triangle_area_fraction_anisotropy_gt1_25':float(A0[ratio>1.25].sum()/A0.sum()),'triangle_area_fraction_anisotropy_gt1_5':float(A0[ratio>1.5].sum()/A0.sum()),'patches':patch_stats,'antialias_remaining':'raw unchanged; mechanical domain excludes low alpha only from solve; no export or hard-alpha render performed','boundary_collision_check':'pending','iterations':len(log)}
(O/'SOLVE_AUDIT.json').write_text(json.dumps(result,indent=2));(O/'ITERATIONS.json').write_text(json.dumps(log,indent=2));print(json.dumps(result,indent=2))
