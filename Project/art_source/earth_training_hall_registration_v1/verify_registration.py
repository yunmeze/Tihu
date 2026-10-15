"""Independent pixel inverse, metadata and frozen world-grid verification; no runtime."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;P=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 r=json.loads((HERE/'registration.json').read_text());source=P/'art_source/a13_main_temple_source/source-group-contract.json';c=json.loads(source.read_text());original={o['key']:o for o in c['owners_in_draw_order']};rawpath=P/r['raw_texture'][6:];a=np.asarray(Image.open(rawpath).convert('RGBA'));out=np.zeros_like(a);counts=np.zeros(a.shape[:2],np.uint8);owner_at=np.full(a.shape[:2],-1,np.int16);s=r['whole_building_registration']['scale'];t=np.array(r['whole_building_registration']['world_top_left'])
 assert sha(rawpath)==r['raw_sha256'];assert sha(source)==r['source_contract_sha256'];assert len(r['owners'])==len({o['key']for o in r['owners']})==30;assert set(r['suppress_source_keys'])==set(original)
 for i,o in enumerate(r['owners']):
  old=original[o['key']]
  for k in ['cell','source_cell','flag','layer','sort_y','stable_source_order','frame_index']:assert o[k]==old[k],(o['key'],k)
  if o['texture']is None:assert o['visible_pixel_count']==0;continue
  p=P/o['texture'][6:];assert sha(p)==o['sha256'];im=np.asarray(Image.open(p).convert('RGBA'));x,y,w,h=o['raw_rect'];assert im.shape==(h,w,4);assert 0<=x<x+w<=a.shape[1] and 0<=y<y+h<=a.shape[0];assert np.max(np.abs(np.array(o['world_top_left'])-(t+np.array([x,y])*s)))<1e-9;used=np.any(im!=0,axis=2);out[y:y+h,x:x+w][used]=im[used];counts[y:y+h,x:x+w][used]+=1;owner_at[y:y+h,x:x+w][used]=i
 assert np.array_equal(out,a);assert np.all(counts[np.any(a!=0,axis=2)]==1);assert counts.max()==1
 yy,xx=np.indices((665,796));rx=np.floor((2948+xx+.5-t[0])/s).astype(int);ry=np.floor((642+yy+.5-t[1])/s).astype(int);valid=(rx>=0)&(rx<a.shape[1])&(ry>=0)&(ry<a.shape[0]);assert np.array_equal(out[ry[valid],rx[valid]],a[ry[valid],rx[valid]])
 contract=json.loads((P/'art_source/earth_training_hall_local_stair_plan_v1/local-input-contract.json').read_text());probes=[]
 for side,v in contract['sides'].items():
  for row in v['source_foot_and_ground_constraints']:
   for q in row['samples']:
    x,y=map(round,q['raw_xy']);idx=int(owner_at[y,x]);owner=r['owners'][idx]if idx>=0 else None
    sample={'source_cell':row['cell'],'foot':q['foot'],'source_material':q['source_material'],'raw_xy':q['raw_xy'],'alpha_at_nearest_raw_pixel':int(a[y,x,3]),'candidate_owner':owner['key']if owner else None,'candidate_layer':owner['layer']if owner else None,'required_support':q['required_support']}
    if q['required_support']:assert owner and owner['layer']==0 and a[y,x,3]>128,sample
    probes.append(sample)
 result={'status':'PASS static metadata, complete RGBA inverse and nearest-world-grid parity; native joint review pending','registration_sha256':sha(HERE/'registration.json'),'whole_raw_sha256':sha(rawpath),'source_metadata_30_exact':True,'layer_counts':{'0':sum(o['layer']==0 for o in r['owners']),'1':sum(o['layer']==1 for o in r['owners'])},'whole_rgba_bytes_equal':True,'nonzero_rgba_pixels_unique':True,'source_key_set_exact':True,'crop_world_compensation_max_error':0,'nearest_world_grid_parity':True,'clear_support_probes_all_layer0':True,'foot_probes':probes,'empty_owner_ids':[o['frame_index']for o in r['owners']if o['texture']is None],'runtime_modified':False,'known_uncertainty':'Right74,37 foot1 is a source edge proxy within +/-2px uncertainty; nearest-pixel alpha is not a clearance proof.'}
 (HERE/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='foot_probes'}))
if __name__=='__main__':main()
