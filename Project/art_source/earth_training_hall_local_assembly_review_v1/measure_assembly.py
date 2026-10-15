"""Review 24 fixed source-foot samples and unchanged-pixel ownership; no image edits."""
from pathlib import Path
from PIL import Image
import json,numpy as np,math,hashlib
HERE=Path(__file__).resolve().parent;A=HERE.parent

def main():
 a=np.asarray(Image.open(HERE/'full-building-candidate-review.png'));base=np.asarray(Image.open(A/'earth_training_hall_candidate_v2/raw.png'));c=json.loads((A/'earth_training_hall_local_stair_plan_v1/local-input-contract.json').read_text());qa=[];allowed=np.zeros(a.shape[:2],bool)
 for side,s in c['sides'].items():
  ox,oy=s['raw_v2_crop_xyxy_half_open'][:2];new=np.asarray(Image.open(HERE/f'{side}-new-material-selection.png'))>0;old=np.asarray(Image.open(HERE/f'{side}-old-stair-retirement.png'))>0;allowed[oy:oy+512,ox:ox+512]|=new|old
  for row in s['source_foot_and_ground_constraints']:
   rr={'owner':row['owner'],'cell':row['cell'],'source_flag':row['source_flag'],'side':side,'samples':[]}
   for q in row['samples']:
    x,y=q['raw_xy'];r=2*c['fixed_reference']['density'];ys,xs=np.mgrid[max(0,math.floor(y-r)):min(a.shape[0],math.ceil(y+r)+1),max(0,math.floor(x-r)):min(a.shape[1],math.ceil(x+r)+1)];vals=a[ys,xs,3][(xs-x)**2+(ys-y)**2<=r*r];ix,iy=round(x),round(y)
    rr['samples'].append({'foot':q['foot'],'whole_raw_xy':[x,y],'source_material':q['source_material'],'center_alpha':int(a[iy,ix,3]),'uncertainty_disk_min_alpha':int(vals.min()),'uncertainty_disk_max_alpha':int(vals.max()),'uncertainty_disk_alpha_gt128_fraction':float((vals>128).mean()),'manual_classification':'edge-uncertain vertical front-riser silhouette; within original +/-2 source px read budget'if side=='right'and q['critical_for_this_edit']else'tread_or_landing'if q['required_support']else'tread_at_source_uncertain_edge'if q['source_material']=='uncertain_cheek_edge'else'clear_transparent_ground'})
   qa.append(rr)
 assert np.array_equal(a[~allowed],base[~allowed]);pm=np.asarray(Image.open(HERE/'left-original-main-pier-selection.png'))>0;assert np.array_equal(a[550:1062,130:642][pm],base[550:1062,130:642][pm]);changed=np.any(base!=a,axis=2);ys,xs=np.where(changed)
 r={'status':'candidate combined review, not runtime pass','source_support_owner_count':12,'foot_sample_count':24,'sample_rows':qa,'source_owner_flags_and_runtime':'Read only; no owner, flag, collision or runtime modifications. Foot material class manually reviewed, alpha alone not support.','changed_whole_raw_bbox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'changed_pixel_count':int(changed.sum()),'outside_stair_selections_rgba_exact':True,'original_left_main_pier_selection_rgba_exact':True,'notes':['Left seven clear support samples remain stair/landing; all four left grass uncertainty disks transparent.','Right seven clear support samples remain stair/landing; four outer grass disks transparent; one edge proxy remains uncertain, not a certified transparent clearance.','Full native route, height ordering, platform receiver and final registration remain unverified.'],'reproduce':'python Project/art_source/earth_training_hall_local_assembly_review_v1/measure_assembly.py'}
 (HERE/'measurements.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items()if k!='sample_rows'}))
if __name__=='__main__':main()
