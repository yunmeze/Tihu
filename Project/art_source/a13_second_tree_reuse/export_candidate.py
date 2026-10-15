"""Exact source-family second-instance reuse; no image regeneration or pixel changes."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parents[2];O=P/'assets/scifi/environment/a13_second_tree_reuse_v1';O.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,a):p.write_text(json.dumps(a,indent=2)+'\n')
s=P/'assets/scifi/environment/a13_first_tree_v1/registration.json';a=json.loads(s.read_text());m=json.loads((P/'data/maps/A13.json').read_text());dx,dy=624,416
for o in a['owners']:
 x,y=[v+13 for v in o['cell']];c=m['cells'][x*100+y];assert c[1:]==o['source_cell'][1:];o.update(cell=[x,y],source_cell=c,key=f'Plant:{o["frame_index"]}@{x},{y}',sort_y=y,stable_source_order=x*100+y,world_top_left=[o['world_top_left'][0]+dx,o['world_top_left'][1]+dy])
a['suppress_source_keys']=[o['key']for o in a['owners']];a['whole_tree_registration']['world_top_left']=[a['whole_tree_registration']['world_top_left'][0]+dx,a['whole_tree_registration']['world_top_left'][1]+dy];a['schema']='a13-second-tree-exact-source-family-reuse-v1';a['status']='parent-authorized HD candidate; second-instance native pending';a['limits']=['Exact source object frame/flag/type family translation; original floor fields differ and are retained.','Same seven PNGs and uniform scale; no mirror, no new generation.','Each source owner keeps its own y/depth; no whole-tree root sorting.','Single cast for this instance must use translated root; do not overlay two casts.'];a['acceptance_scope']={'first_instance_registration_sha256':sha(s),'translation_cells':[13,13],'translation_world':[624,416],'object_fields_equal':True,'whole_source_cell_equal':False,'floor_fields_preserved':True,'native_second_instance':'pending','world_root':[3385,1506]};dump(O/'registration.json',a);reg=a
s=P/'assets/scifi/environment/a13_first_tree_shadow_v1/shadow.json';a=json.loads(s.read_text());a['schema']='a13-second-tree-reused-single-cast-v1';a['status']='same alpha/parameters translated624,416; second-instance HD native pending';a['whole_tree_registration']=reg['whole_tree_registration'];a['world_wood_root']=[3385.0,1506.0];a['draw_contract']['requires_suppressed_source_keys']=reg['suppress_source_keys'];a['reuse_first_shadow_sha256']=sha(s);a['reuse_native_acceptance']='first-instance historical evidence does not prove second-instance depth';a['historical_first_instance_native_review']=a.pop('native_review');a['limitations']=[v for v in a['limitations']if 'second source-family'not in v];a['limitations'].append('Only second instance exact7 keys; native verification pending.')
for k,v in a['bounded_projection_check'].items():
 if 'world'in k and isinstance(v,list)and len(v)==2:a['bounded_projection_check'][k]=[v[0]+624,v[1]+416]
a['source_evidence_scope']='source_evidence records original first-instance direction study; reused vector unchanged';dump(O/'shadow.json',a)
print(sha(O/'registration.json'),sha(O/'shadow.json'))
