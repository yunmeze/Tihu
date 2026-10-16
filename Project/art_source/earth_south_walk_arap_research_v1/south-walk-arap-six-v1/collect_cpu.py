from pathlib import Path
import json,numpy as np,hashlib
O=Path(__file__).parent;R=O.parent;items=[]
for p in range(57,63):
 folder=R/('south-walk-arap-cpu-v1' if p==59 else f'south-walk-arap{p}-cpu-v1');typ='collision' if p in [57,59,61] else 'orientation';path=folder/f'render_{typ}_safe{p}.npz';z=np.load(path);q=z['vertices'];uv=z['uv'];t=z['triangles'];e,c=np.unique(np.sort(np.concatenate([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]),axis=1),axis=0,return_counts=True);b=e[c==1];A=q[b[:,0]];B=q[b[:,1]];low=np.minimum(A,B);high=np.maximum(A,B);contacts=[]
 def cross(x,y):return x[...,0]*y[...,1]-x[...,1]*y[...,0]
 for k in range(len(b)):
  idx=np.where((np.arange(len(b))>k)&np.all(high>=low[k]-1e-8,axis=1)&np.all(low<=high[k]+1e-8,axis=1))[0];idx=idx[(b[idx,0]!=b[k,0])&(b[idx,0]!=b[k,1])&(b[idx,1]!=b[k,0])&(b[idx,1]!=b[k,1])]
  if not len(idx):continue
  C=A[idx];D=B[idx];o1=cross(B[k]-A[k],C-A[k]);o2=cross(B[k]-A[k],D-A[k]);o3=cross(D-C,A[k]-C);o4=cross(D-C,B[k]-C)
  hit=((o1*o2<0)&(o3*o4<0))|((abs(o1)<1e-8)&(np.sum((C-A[k])*(C-B[k]),axis=1)<=1e-8))|((abs(o2)<1e-8)&(np.sum((D-A[k])*(D-B[k]),axis=1)<=1e-8))|((abs(o3)<1e-8)&(np.sum((A[k]-C)*(A[k]-D),axis=1)<=1e-8))|((abs(o4)<1e-8)&(np.sum((B[k]-C)*(B[k]-D),axis=1)<=1e-8))
  contacts.extend([[k,int(j)] for j in idx[hit]])
 cpu=json.load(open(folder/('COLLISION_SAFE_CPU_AUDIT.json' if typ=='collision' else 'FINAL_CPU_AUDIT.json')));core=json.load(open(folder/'SOLVE_AUDIT.json'));iterations=json.load(open(folder/'ITERATIONS.json'))
 items.append({'phase':p,'mesh_file':str(path.resolve()),'mesh_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'all_alpha_pixels':cpu['covered_unique_pixel_count'],'triangles':len(t),'flips':cpu['flips'],'boundary_intersections_including_nonshared_touches':len(contacts),'intersection_pairs':contacts[:15],'core_target_error_HD':core['final_driving_error_HD'],'core_upper_movement_HD':core['max_upper_movement_HD'],'signed_area_ratio_min':cpu['signed_area_ratio_min_max'][0],'visible_anisotropy_p99':cpu['distributions']['visible_alpha128plus']['anisotropy_percentiles_50_95_99'][2],'visible_alpha_weighted_fraction_anisotropy_gt1_5':cpu['distributions']['visible_alpha128plus']['alpha_weighted_fraction_gt1_5'],'fringe_max_anisotropy':cpu['distributions']['fringe_alpha1to63']['max_anisotropy'],'last_max_vertex_change_HD':iterations[-1]['max_change_HD'],'not_full_energy_convergence':True})
(O/'SIX_CPU_GATE.json').write_text(json.dumps(items,indent=2));print(json.dumps(items,indent=2))
