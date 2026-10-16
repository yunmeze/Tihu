#!/usr/bin/env python3
"""Finite one-parameter path checks, not additional optimization or mesh export."""
import json,itertools,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--report',required=True,type=Path);args=parser.parse_args()
out=Path(__file__).resolve().parent/'failed-mesh-design';r=json.loads((out/'CONSTRAINT_DESIGN.json').read_text())
S=1254/128
nom={t['group']:np.array(t['nominal_translation_raw']) for t in r['target_error_regions']}
base={'H':nom['H'],'C':np.array([-10.,-8.]),'R':np.array([-10.,-10.]),'G':nom['G'],'P':np.array([-10.,-14.]),'N':nom['N'],'F':nom['F']}
cases=[]
for name,merged in [('A_separate_shoulder_and_guard_hand',False),('B_shared_shoulder_guard_hand_rigid_unit',True)]:
 d={k:v.copy() for k,v in base.items()}
 if merged:d['R']=d['G'].copy()
 records=[]
 for fraction in np.linspace(0,1,201):
  worst={'min_singular':999.,'max_singular':0.,'min_area':999.};bad=[]
  for st in r['soft_strips']:
   old=np.array(st['xy'],float);owners=st.get('owners',[st['a'],st['a'],st['b'],st['b']]);new=old+fraction*np.array([d[g] for g in owners])
   for tri in [(0,1,2),(0,2,3)]:
    i,j,k=tri;J=np.column_stack([new[j]-new[i],new[k]-new[i]])@np.linalg.inv(np.column_stack([old[j]-old[i],old[k]-old[i]]));sv=np.linalg.svd(J,compute_uv=False);det=np.linalg.det(J)
    worst['min_singular']=min(worst['min_singular'],float(sv.min()));worst['max_singular']=max(worst['max_singular'],float(sv.max()));worst['min_area']=min(worst['min_area'],float(det))
    if sv.min()<.8-1e-8 or sv.max()>1.2+1e-8 or det<.64-1e-8:bad.append(st['id'])
  targets=[]
  for t in r['target_error_regions']:
   p=np.array(t['raw'])+fraction*d[t['group']];c=np.array(t['allowed_raw_center']);e=np.array(t['allowed_raw_half_width']);targets.append(bool(np.all(np.abs(p-c)<=e+1e-8)))
  records.append({'fraction':float(fraction),'local_strip_limits_pass':not bad,'all_error_targets_reached':all(targets),'failed_strips':sorted(set(bad)),**worst})
 safe=[z for z in records if z['local_strip_limits_pass']];target=[z for z in records if z['all_error_targets_reached']];maxsafe=max(z['fraction'] for z in safe);firsttarget=min(z['fraction'] for z in target) if target else None
 safe_displacements={k:(v*maxsafe/S).tolist() for k,v in d.items()}
 cases.append({'case':name,'path_definition':'q(lambda)=p+lambda*group_translation, rotations0; lambda grid0..1 by0.005. This is a sufficient local-strip seed path, not the whole feasible set or a full image mesh.','group_translation_at_lambda1_raw':{k:v.tolist() for k,v in d.items()},'last_local_strip_safe_fraction_on_grid':maxsafe,'first_all_error_targets_fraction_on_grid':firsttarget,'last_safe_displacement_native_by_group':safe_displacements,'first_local_failure':next(z for z in records if not z['local_strip_limits_pass']),'lambda1_metrics':records[-1],'target_and_local_strain_intersection_empty_on_sampled_path':not any(z['local_strip_limits_pass'] and z['all_error_targets_reached'] for z in records),'limits':'No claim between grid samples, at uncertain material boundaries, or about global nonintersection. This local seed path is not accepted movement.'})
outdata={'schema':'sw-two-bounded-rigid-paths-v1','cases':cases,'interpretation':'No acceptable target-reaching path shown. Do not confuse a small safe local-strip seed with production mesh feasibility. No further numerical retries.','material_assignment_correction':'P1 screen-left vertical metal panel is anatomically ambiguous (could be far forearm/side armor). Its early exploratory coupling to hip P is not an approved assignment. Exclude P1-related overlap counts from conclusions; keep this panel protected and its existing far-hand occlusion unchanged pending a separate visible-surface boundary review. Arm/leg strip conflicts reported here do not depend on P1.'}
assert outdata==json.loads((out/'BOUNDED_PATH_CHECKS.json').read_text())
args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(outdata,ensure_ascii=False,indent=2)+'\n');print('Both finite numerical paths match archived results exactly; neither is accepted.')
