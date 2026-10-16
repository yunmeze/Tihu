from pathlib import Path
import numpy as np,json,time
O=Path(__file__).parent;d=np.load(O/'render_support58.npz');core=np.load(O/'candidate58.npz');uv=d['uv'];rest=d['rest'];goal=d['vertices'];tri=d['triangles'];corekeys=set(map(tuple,core['uv']));fixed=np.array([tuple(v) in corekeys for v in uv])|(uv[:,1]<=230)
def areas(q):
 a=q[tri[:,1]]-q[tri[:,0]];b=q[tri[:,2]]-q[tri[:,0]];return a[:,0]*b[:,1]-a[:,1]*b[:,0]
A0=areas(rest);floor=A0*.2;current=rest.copy();log=[];status='feasible';start=time.time()
for stage in range(1,6):
 f=stage/5;harmonic=rest+f*(goal-rest);q=harmonic.copy();projections=0
 for it in range(1000):
  ar=areas(q);bad=np.where(ar<floor+1e-8)[0]
  if not len(bad):break
  moved=0
  for k in bad:
   ids=tri[k];p=q[ids];g=np.array([[p[1,1]-p[2,1],p[2,0]-p[1,0]],[p[2,1]-p[0,1],p[0,0]-p[2,0]],[p[0,1]-p[1,1],p[1,0]-p[0,0]]]);g[fixed[ids]]=0;den=(g*g).sum()
   if den<1e-16:status='infeasible_fixed_triangle';break
   v=p[1]-p[0];w=p[2]-p[0];area=v[0]*w[1]-v[1]*w[0];step=(floor[k]+2e-6-area)/den
   if step>0:q[ids]+=step*g;moved+=1;projections+=1
  if status!='feasible' or not moved:break
 ar=areas(q); minratio=float((ar/A0).min())
 if minratio<.1:status='projection_failed';break
 # Exact minimum signed area along straight interpolation between accepted states.
 a=areas(current);b=areas(q);mid=areas((current+q)/2);coef=2*(a+b-2*mid);lin=b-a-coef;t=np.zeros_like(a);np.divide(-lin,2*coef,out=t,where=abs(coef)>1e-16);t=np.clip(t,0,1);pathmin=np.minimum(np.minimum(a,b),a+lin*t+coef*t*t)
 if (pathmin/A0).min()<.1:status='positive_area_path_failed';break
 current=q;log.append({'stage':stage,'drive_fraction':f,'projection_iterations':it+1,'local_projections':projections,'min_signed_area_ratio':minratio,'minimum_ratio_along_entire_step':float((pathmin/A0).min()),'max_fringe_adjustment_from_harmonic_HD':float(np.linalg.norm(q-harmonic,axis=1).max()),'fixed_core_error_HD':float(np.linalg.norm(q[fixed]-harmonic[fixed],axis=1).max())})
np.savez_compressed(O/'render_orientation_safe58.npz',uv=uv,rest=rest,vertices=current,triangles=tri)
j={'status':status,'method':'Five target stages; orientation projection only on non-core render fringe; accept only if every triangle and entire straight step retain area ratio>=0.1. Original invalid harmonic map retained. No raw pixels removed or edited.','stages':log,'accepted_fraction':log[-1]['drive_fraction'] if log else 0,'full_target_remaining_HD':float(np.linalg.norm(current[fixed]-goal[fixed],axis=1).max()),'render_flips':int((areas(current)<=0).sum()),'min_signed_area_ratio':float((areas(current)/A0).min()),'seconds':time.time()-start,'no_gpu':True};(O/'FRINGE_ORIENTATION_AUDIT.json').write_text(json.dumps(j,indent=2));print(json.dumps(j,indent=2))
