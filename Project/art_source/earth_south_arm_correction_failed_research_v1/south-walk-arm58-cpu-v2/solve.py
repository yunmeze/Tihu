from pathlib import Path
import numpy as np,json,time,hashlib
from PIL import Image
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import factorized
from scipy.spatial import cKDTree
O=Path(__file__).parent;R=O.parent;start=time.time();base=R/'south-walk-arap58-cpu-v1/render_orientation_safe58.npz';z=np.load(base);uv=z['uv'];rest=z['vertices'].copy();tri=z['triangles'];n=len(uv);mid=np.floor(uv[tri].mean(1)).astype(int);delta=np.zeros_like(rest);isfix=np.zeros(n,bool);isrigid=np.zeros(n,bool);cloth=np.zeros(n,bool)
cs=[np.array(Image.open(R/f'south-walk-arm58-support-proposal-v1/58-{k}-classes.png')) for k in ['L','R']];merged=np.maximum(cs[0],cs[1]);tc=merged[mid[:,1],mid[:,0]]
for target,sel in [(isfix,tc==0),(isrigid,tc==2),(cloth,np.isin(tc,[1,3]))]:target[np.unique(tri[sel])]=True
assert not np.any(isfix&isrigid)
constraints=json.load(open(R/'south-walk-arm5861-proposal-v1/CONSTRAINTS.json'))[0]['screen_sides'];rigids={}
for k,c in zip(['L','R'],cs):
 ids=np.unique(tri[c[mid[:,1],mid[:,0]]==2]);rigids[k]=ids;delta[ids]=constraints[k]['translation_output_HD']
assert not len(np.intersect1d(rigids['L'],rigids['R']))
fixed=isfix|isrigid;fi=np.where(fixed)[0];fr=np.where(~fixed)[0]
edges,count=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0,return_counts=True);boundary=edges[count==1];i,j=edges.T;w=np.ones(len(edges));L=coo_matrix((np.r_[w,w,-w,-w],(np.r_[i,j,i,j],np.r_[i,j,j,i])),shape=(n,n)).tocsc();solve=factorized(L[fr][:,fr]);Lfc=L[fr][:,fi];e=rest[i]-rest[j]
def area(q):
 a=q[tri[:,1]]-q[tri[:,0]];b=q[tri[:,2]]-q[tri[:,0]];return a[:,0]*b[:,1]-a[:,1]*b[:,0]
a0=area(rest);assert a0.min()>0

def boundary_hits(q):
 A=q[boundary[:,0]];B=q[boundary[:,1]];cent=(A+B)/2;lens=np.linalg.norm(B-A,axis=1);pairs=cKDTree(cent).query_pairs(float(lens.max()+1e-7),output_type='ndarray')
 if not len(pairs):return []
 s,t=pairs.T;keep=(boundary[s,0]!=boundary[t,0])&(boundary[s,0]!=boundary[t,1])&(boundary[s,1]!=boundary[t,0])&(boundary[s,1]!=boundary[t,1]);s=s[keep];t=t[keep];lo=np.minimum(A,B);hi=np.maximum(A,B);keep=np.all(hi[s]>=lo[t]-1e-8,axis=1)&np.all(hi[t]>=lo[s]-1e-8,axis=1);s=s[keep];t=t[keep]
 def cross(x,y):return x[:,0]*y[:,1]-x[:,1]*y[:,0]
 ab=B[s]-A[s];cd=B[t]-A[t];o1=cross(ab,A[t]-A[s]);o2=cross(ab,B[t]-A[s]);o3=cross(cd,A[s]-A[t]);o4=cross(cd,B[s]-A[t]);hit=((o1*o2<0)&(o3*o4<0))|((abs(o1)<1e-8)&(np.sum((A[t]-A[s])*(A[t]-B[s]),axis=1)<=1e-8))|((abs(o2)<1e-8)&(np.sum((B[t]-A[s])*(B[t]-B[s]),axis=1)<=1e-8))|((abs(o3)<1e-8)&(np.sum((A[s]-A[t])*(A[s]-B[t]),axis=1)<=1e-8))|((abs(o4)<1e-8)&(np.sum((B[s]-A[t])*(B[s]-B[t]),axis=1)<=1e-8));return np.stack([s[hit],t[hit]],axis=1).tolist()
def rhs(q):
 de=q[i]-q[j];C=np.zeros((n,2,2));out=w[:,None,None]*de[:,:,None]*e[:,None,:];np.add.at(C,i,out);np.add.at(C,j,out);U,S,Vh=np.linalg.svd(C);rot=U@Vh;bad=np.linalg.det(rot)<0;U[bad,:,1]*=-1;rot=U@Vh;v=.5*w[:,None]*np.einsum('nij,nj->ni',rot[i]+rot[j],e);b=np.zeros((n,2));np.add.at(b,i,v);np.add.at(b,j,-v);return b
assert not boundary_hits(rest)
q=rest.copy();log=[];rejected=[];status='bounded_candidate'
for stage in range(1,6):
 target=rest+delta*stage/5
 for it in range(40):
  b=rhs(q);candidate=q.copy();candidate[fi]=target[fi];candidate[fr]=solve(b[fr]-Lfc@target[fi]);step=1.;ok=False
  for back in range(24):
   trial=q+step*(candidate-q);ratio=area(trial)/a0;hits=[] if ratio.min()<=.1 else boundary_hits(trial)
   if ratio.min()>.1 and not hits:ok=True;break
   rejected.append({'stage':stage,'iteration':it,'backtrack':back,'step':step,'min_area_ratio':float(ratio.min()),'flips':int((ratio<=0).sum()),'boundary_hits':hits[:4]});step*=.5
  if not ok:status='backtracking_failed';break
  change=float(np.linalg.norm(trial-q,axis=1).max());q=trial;err=float(np.linalg.norm(q[fi]-target[fi],axis=1).max());log.append({'stage':stage,'iteration':it,'step':step,'max_change_HD':change,'stage_driver_error_HD':err,'min_area_ratio':float(ratio.min())})
  if change<.003 and err<.01:break
 if status!='bounded_candidate':break
 if log[-1]['stage_driver_error_HD']>.01:status='stage_target_not_reached';break
np.savez_compressed(O/'candidate58.npz',uv=uv,rest=rest,vertices=q,triangles=tri)
r=area(q)/a0;hits=boundary_hits(q);actual_err=float(np.linalg.norm(q[isrigid]-(rest+delta)[isrigid],axis=1).max());fixed_err=float(np.linalg.norm(q[isfix]-rest[isfix],axis=1).max());u=rest[tri];v=q[tri];J=np.stack([v[:,1]-v[:,0],v[:,2]-v[:,0]],axis=2)@np.linalg.inv(np.stack([u[:,1]-u[:,0],u[:,2]-u[:,0]],axis=2));sv=np.linalg.svd(J,compute_uv=False);anis=sv[:,0]/sv[:,1];a=np.array(Image.open(R/'south-walk-mesh-correction-v1/raw/58.png'))[:,:,3];alpha=a[mid[:,1],mid[:,0]]
result={'phase':58,'status':status,'seconds':time.time()-start,'base_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'free_vertices':len(fr),'rigid_vertices':int(isrigid.sum()),'fixed_external_vertices':int(isfix.sum()),'fixed_rigid_conflicts':int((isfix&isrigid).sum()),'remaining_driver_error_HD':actual_err,'max_fixed_external_movement_HD':fixed_err,'min_incremental_area_ratio':float(r.min()),'flips':int((r<=0).sum()),'boundary_intersections_including_touches':len(hits),'all_alpha_cells_preserved':len(np.unique(mid,axis=0))==int((a>0).sum()),'visible_anisotropy_percentiles_50_95_99_max':np.percentile(anis[alpha>=128],[50,95,99,100]).tolist(),'fringe_max_anisotropy':float(anis[alpha<64].max()),'iterations':len(log),'rejected_trial_count':len(rejected),'passed_for_gpu_request_only':status=='bounded_candidate' and actual_err<.01 and fixed_err==0 and not hits,'claim':'translation hypothesis only; no original unique-pose or visual acceptance'}
(O/'AUDIT.json').write_text(json.dumps(result,indent=2));(O/'ITERATIONS.json').write_text(json.dumps(log,indent=2));(O/'REJECTED_TRIALS.json').write_text(json.dumps(rejected,indent=2));print(json.dumps(result,indent=2),flush=True)
