from pathlib import Path
import numpy as np,json
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
O=Path(__file__).parent;d=np.load(O/'render_orientation_safe57.npz');core=np.load(O/'candidate57.npz');uv=d['uv'];r=d['rest'];q=d['vertices'];t=d['triangles'];keys=set(map(tuple,core['uv']));fixed=np.array([tuple(v) in keys for v in uv])|(uv[:,1]<=230)
e,c=np.unique(np.sort(np.concatenate([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]),axis=1),axis=0,return_counts=True);b=e[c==1];u,v=b.T;G=coo_matrix((np.ones(2*len(b)),(np.r_[u,v],np.r_[v,u])),shape=(len(uv),len(uv))).tocsr();nc,labs=connected_components(G);components=[int(labs[b[k,0]]) for k in [1515,1536,1524,1556]]
def area(x):
 a=x[t[:,1]]-x[t[:,0]];b=x[t[:,2]]-x[t[:,0]];return a[:,0]*b[:,1]-a[:,1]*b[:,0]
a0=area(r)
def cross(x,y):return x[...,0]*y[...,1]-x[...,1]*y[...,0]
def hits(pos):
 A=pos[b[:,0]];B=pos[b[:,1]];out=[]
 for k in range(len(b)):
  z=np.arange(k+1,len(b));z=z[(b[z,0]!=b[k,0])&(b[z,0]!=b[k,1])&(b[z,1]!=b[k,0])&(b[z,1]!=b[k,1])];C=A[z];D=B[z];ab=B[k]-A[k];cd=D-C;v=z[(cross(ab,C-A[k])*cross(ab,D-A[k])< -1e-12)&(cross(cd,A[k]-C)*cross(cd,B[k]-C)< -1e-12)];out.extend([[k,int(j)] for j in v])
 return out
center=np.array([230,320]);sel=(np.linalg.norm(core['uv']-center,axis=1)<24)&(core['uv'][:,0]<=225);X=core['rest'][sel];Y=core['vertices'][sel];x=X-X.mean(0);y=Y-Y.mean(0);U,S,Vh=np.linalg.svd(x.T@y);R=U@Vh
if np.linalg.det(R)<0:U[:,-1]*=-1;R=U@Vh
local=(r-X.mean(0))@R+Y.mean(0);records=[];winner=None
for radius in [10,16,22]:
 dist=np.linalg.norm(uv-center,axis=1);w=np.clip(1-dist/radius,0,1);w=w*w*(3-2*w);w[fixed]=0
 for amount in [.5,1.]:
  v=q+amount*w[:,None]*(local-q)
  for iteration in range(500):
   ar=area(v);bad=np.where(ar<a0*.2+1e-8)[0]
   if not len(bad):break
   for k in bad:
    ids=t[k];pp=v[ids];gg=np.array([[pp[1,1]-pp[2,1],pp[2,0]-pp[1,0]],[pp[2,1]-pp[0,1],pp[0,0]-pp[2,0]],[pp[0,1]-pp[1,1],pp[1,0]-pp[0,0]]]);gg[fixed[ids]]=0;den=(gg*gg).sum()
    if den<1e-16:continue
    aa=cross(pp[1]-pp[0],pp[2]-pp[0]);step=(a0[k]*.2+2e-6-aa)/den
    if step>0:v[ids]+=step*gg
  ar=area(v)/a0;inter=hits(v) if ar.min()>.1 else None
  rec={'radius_raw_HD':radius,'blend_amount':amount,'min_signed_area_ratio':float(ar.min()),'intersections':len(inter) if inter is not None else None,'max_fringe_adjustment_HD':float(np.linalg.norm(v-q,axis=1).max()),'changed_core_max_HD':float(np.linalg.norm(v[fixed]-q[fixed],axis=1).max())};records.append(rec)
  if inter==[]:winner=v;break
 if winner is not None:break
j={'classification':'same connected boundary local foldback' if len(set(components))==1 else 'different boundary components collision','boundary_components':components,'method':'local proper-rigid fit from nearby left-boot core; smooth limited influence only on non-core fringe; all raw alpha retained','attempts':records,'status':'candidate_feasible' if winner is not None else 'no_candidate','local_rigid_reference_vertices':int(sel.sum()),'no_gpu':True}
if winner is not None:np.savez_compressed(O/'render_collision_safe57.npz',uv=uv,rest=r,vertices=winner,triangles=t)
(O/'FRINGE_COLLISION_AUDIT.json').write_text(json.dumps(j,indent=2));print(json.dumps(j,indent=2))
