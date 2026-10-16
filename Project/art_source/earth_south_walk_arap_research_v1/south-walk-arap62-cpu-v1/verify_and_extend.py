from pathlib import Path
import numpy as np,json
from PIL import Image
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
O=Path(__file__).parent;d=np.load(O/'candidate62.npz');uv=d['uv'];q=d['vertices'];rest=d['rest'];tri=d['triangles']
def area(q,t):
 a=q[t[:,1]]-q[t[:,0]];b=q[t[:,2]]-q[t[:,0]];return a[:,0]*b[:,1]-a[:,1]*b[:,0]
# Domain triangles are each literal alpha>=64 pixel half-squares, no edge bridges empty pixels.
a=np.array(Image.open(O.parent/'south-walk-mesh-correction-v1/raw/62.png'))[:,:,3];mid=np.floor(uv[tri].mean(1)).astype(int);domain_violations=int((a[mid[:,1],mid[:,0]]<64).sum())
# Exact boundary pair crossing check, all non-neighbor edges, original and deformed.
edges,cnt=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0,return_counts=True);boundary=edges[cnt==1]
def intersections(pos):
 A=pos[boundary[:,0]];B=pos[boundary[:,1]];N=len(A);hits=[]
 def cross(x,y):return x[...,0]*y[...,1]-x[...,1]*y[...,0]
 for k in range(N):
  valid=np.arange(k+1,N);valid=valid[(boundary[valid,0]!=boundary[k,0])&(boundary[valid,0]!=boundary[k,1])&(boundary[valid,1]!=boundary[k,0])&(boundary[valid,1]!=boundary[k,1])]
  C=A[valid];D=B[valid];ab=B[k]-A[k];cd=D-C
  t1=cross(ab,C-A[k]);t2=cross(ab,D-A[k]);t3=cross(cd,A[k]-C);t4=cross(cd,B[k]-C)
  z=valid[(t1*t2< -1e-12)&(t3*t4< -1e-12)]
  hits.extend([[k,int(v)] for v in z])
 return hits
crossings=intersections(q)
# Rendering support preserves EVERY nonzero-alpha pixel, including the low-alpha tail.
y,x=np.where(a>0);cor=np.stack([np.stack([x,y],1),np.stack([x+1,y],1),np.stack([x+1,y+1],1),np.stack([x,y+1],1)],1);rv,inv=np.unique(cor.reshape(-1,2),axis=0,return_inverse=True);quad=inv.reshape(-1,4);rt=np.concatenate([quad[:,[0,1,2]],quad[:,[0,2,3]]]);re=np.unique(np.sort(np.concatenate([rt[:,[0,1]],rt[:,[1,2]],rt[:,[2,0]]]),axis=1),axis=0);n=len(rv);lookup={tuple(v):k for k,v in enumerate(uv.astype(int))};known=np.array([tuple(v) in lookup for v in rv]);disp=np.zeros((n,2))
for k in np.where(known)[0]:disp[k]=q[lookup[tuple(rv[k])]]-rest[lookup[tuple(rv[k])]]
# Upper non-mechanical fringe fixed; disconnected alpha1 specks fixed if no core anchor.
known|=rv[:,1]<=230
from scipy.sparse.csgraph import connected_components
u,v=re.T;G=coo_matrix((np.ones(2*len(re)),(np.r_[u,v],np.r_[v,u])),shape=(n,n)).tocsr();nc,labs=connected_components(G)
for c in range(nc):
 ids=labs==c
 if not known[ids].any():
  center=rv[ids].mean(axis=0);nearest=int(np.argmin(np.sum((uv-center)**2,axis=1)));disp[ids]=q[nearest]-rest[nearest];known[ids]=True
weights=np.ones(len(re));L=coo_matrix((np.r_[weights,weights,-weights,-weights],(np.r_[u,v,u,v],np.r_[u,v,v,u])),shape=(n,n)).tocsc();fr=np.where(~known)[0];fi=np.where(known)[0];disp[fr]=spsolve(L[fr][:,fr],-L[fr][:,fi]@disp[fi]);rr=rv*.72+np.array([162-.72*233,62-.72*41]);rq=rr+disp;ratio=area(rq,rt)/area(rr,rt)
# Core is fixed in extension, so low-alpha tails never change physical deformation.
err=max(np.linalg.norm(rq[k]-q[lookup[tuple(rv[k])]]) for k in np.where(np.array([tuple(v) in lookup for v in rv]))[0])
np.savez_compressed(O/'render_support62.npz',uv=rv,vertices=rq,triangles=rt,rest=rr)
j={'mechanical_domain_triangle_alpha_violations':domain_violations,'mechanical_boundary_edges':len(boundary),'proper_boundary_crossings':len(crossings),'crossing_pairs':crossings[:20],'boundary_check_limit':'proper crossings checked; tangential touches need visual inspection','render_support':'all raw alpha>0 occupied pixel squares; no alpha values changed and no new pixels painted','raw_nonzero_pixels':int((a>0).sum()),'render_vertices':n,'render_triangles':len(rt),'render_alpha_coverage_missing_pixels':0,'render_low_alpha_extension':'harmonic extension with core vertices fixed; disconnected unanchored alpha1 fragments translated with nearest core surface; same rigid displacement per fragment; no mechanical coupling through fringe','core_vertex_displacement_change_HD':float(err),'render_triangle_flips':int((ratio<=0).sum()),'render_area_ratio_min_max':[float(ratio.min()),float(ratio.max())],'render_extension_free_vertices':len(fr),'no_gpu_run':True}
(O/'TOPOLOGY_AND_ALPHA_AUDIT.json').write_text(json.dumps(j,indent=2));print(json.dumps(j,indent=2))
