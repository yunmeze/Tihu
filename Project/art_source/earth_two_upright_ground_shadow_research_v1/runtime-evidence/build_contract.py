from pathlib import Path
from PIL import Image
import json,hashlib,shutil,numpy as np
O=Path(__file__).resolve().parent;W=O.parent.parent;P=O/'Project';B=W/'recovery-work/earth-unified-candidate-v2';CPU=W/'recovery-work/upright-51-70-cpu-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
frozen=json.loads((B/'FROZEN_INPUTS_v3.json').read_text());assert sha(B/'FROZEN_INPUTS_v3.json')=='73f602cdc29dd927586df01df4bc1a00de38ff39aa562e9a81452921c4be352c'
assert sha(B/'SUPPLEMENTAL_RAW_FREEZE.json')=='f053d2b0b2ef68cd17302a81445a98bfdf3801aff5a1ff09a5d62f984a2e3d20'
supp=json.loads((B/'SUPPLEMENTAL_RAW_FREEZE.json').read_text())['files'];frozen.update({r['path'][6:]:r['sha256'] for r in supp});frozen['tools/earth/build_snapshot_registration.py']='bc8d441fa63268fb67d2ca1d4f3d5b81d86d38ccbf9917f3019c85be8e178053'
for r in supp:
 rel=r['path'][6:];src=B/'Project'/rel;dst=P/rel;assert sha(src)==r['sha256']
 if not dst.exists():
  for a in dst.parents:
   if a==P.parent:break
   assert not a.is_symlink(),a
  dst.parent.mkdir(parents=True,exist_ok=True)
  if src.suffix=='.png':dst.symlink_to(src.resolve())
  else:shutil.copyfile(src,dst)
# Complete every explicit declared resource, even legacy art_source paths omitted
# by the narrower runtime-directory convenience list. Never copy a parent symlink.
extra=[]
for decl in ['assets/earth/snapshot_opening/snapshot_runtime_registration.json','assets/earth/shadows/s_walk_contact_v3/runtime_registration.json','assets/earth/hero/s_walk_arap_v1/s_walk_runtime_registration.json']:
 for row in (lambda d:d.get('runtime_files',d.get('files',[])))(json.loads((P/decl).read_text())):
  rel=row['path'][6:];dst=P/rel
  if dst.exists():assert sha(dst)==row['sha256'];continue
  src=B/'Project'/rel;assert frozen[rel]==sha(src)==row['sha256']
  for a in dst.parents:
   if a==P.parent:break
   assert not a.is_symlink(),a
  dst.parent.mkdir(parents=True,exist_ok=True)
  if src.suffix=='.png':dst.symlink_to(src.resolve())
  else:shutil.copyfile(src,dst)
  extra.append(rel)
  meta=rel+'.import'
  if meta in frozen:
   assert sha(B/'Project'/meta)==frozen[meta];shutil.copyfile(B/'Project'/meta,P/meta)
reg=json.loads((CPU/'contract.json').read_text());tree=reg['tree'];source=json.loads((P/'data/maps/A13.json').read_text());manifest=json.loads((P/'assets/original/manifest.json').read_text());inv=json.loads((W/'tihu-legend/recovery-work/full-a13-coverage/inventory.json').read_text());enum=json.loads((CPU/'SOURCE_ENUMERATION.json').read_text());keys={r['key'] for r in enum['objects'] if not r['key'].startswith('Npc:')};keys|={r['key'] for r in tree['owners']}
objects=[o for o in inv['owners'] if o['key'] in keys];frame_ids={}
for row in objects+enum['floors']:
 pack=row.get('pack',row['key'].split(':')[0]);index=row.get('index',int(row['key'].split(':')[1].split('@')[0]));frame_ids.setdefault(pack,set()).add(str(index))
frames={k:{i:manifest['packs'][k]['frames'][i] for i in v} for k,v in frame_ids.items()};pages={k:manifest['packs'][k]['pages'] for k in frames}
floor_stream=[]
for i,cell in enumerate(source['cells']):
 if cell[0]:floor_stream.append({'pack':'Map/Res/FloorBig' if cell[0]<0 else 'Map/Res/FloorSmall','index':abs(cell[0]),'origin':[(i//100)*48,(i%100)*32]})
pins={}
for rel,h in frozen.items():
 # Close actual executed runtime scripts, declarations and their resources.
 if rel.startswith(('scripts/','shaders/','ground_candidate/')) and not rel.endswith('.uid') and not rel.endswith('.import'):
  if (P/rel).is_file():assert sha(P/rel)==h;pins['res://'+rel]=h
for decl in ['assets/earth/snapshot_opening/snapshot_runtime_registration.json','assets/earth/shadows/s_walk_contact_v3/runtime_registration.json','assets/earth/hero/s_walk_arap_v1/s_walk_runtime_registration.json']:
 for row in (lambda d:d.get('runtime_files',d.get('files',[])))(json.loads((P/decl).read_text())):pins[row['path']]=row['sha256']
for rel in ['scripts/earth/upright_51_70_gate.gd','scripts/earth/upright_51_70_compositor.gd','scripts/earth/upright_51_70_world.gd','shaders/earth_upright_51_70.gdshader']+[str(f.relative_to(P)) for f in (P/'assets/earth/shadows/upright_51_70_v1').glob('*.png')]:pins['res://'+rel]=sha(P/rel)
for row in tree['source_dependencies']:pins[row['path']]=row['sha256']
for pack in frames:
 for page in pages[pack]:
  uri=page['file'];pins[uri]=sha(P/uri[6:])
pins['res://assets/earth/environment/upright_tree_v1/raw.png']=sha(P/'assets/earth/environment/upright_tree_v1/raw.png')
for uri,h in json.loads((P/'ground_candidate/registration.json').read_text())['pins'].items():pins[uri]=h
owner_rgba={str(r['index']):hashlib.sha256(np.array(Image.open(P/r['texture'][6:]).convert('RGBA')).tobytes()).hexdigest() for r in tree['owners']}
c={'schema':'upright-51-70-live-local-ground-only-v1','caster':'upright_tree_51_70','status':'independent candidate; CPU semantic review accepted; GPU pending','tree':tree,'body_path':'res://assets/earth/environment/upright_tree_v1/raw.png','receiver_path':'res://assets/earth/shadows/upright_51_70_v1/allowed-provisional.png','map_cells':source['cells'],'floor_stream':floor_stream,'frames':frames,'pages':pages,'source_owners':objects,'owner_rgba':owner_rgba,'pins':pins,'cpu_contract_sha256':sha(CPU/'contract.json'),'base_input_manifest_sha256':sha(B/'FROZEN_INPUTS_v3.json'),'ground_registration_sha256':sha(P/'ground_candidate/registration.json'),'policy':'one tree only, generated alpha common max, pool positive-alpha+5logical excluded, full-support FAIL retained; only modern floor snapshot accepted; arbitrary external ImageTexture.update outside controlled lifecycle'}
dest=P/'assets/earth/shadows/upright_51_70_v1/runtime_registration.json';assert not dest.is_symlink() and all(not a.is_symlink() for a in dest.parents)
dest.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
qualification='''extends RefCounted
const PATH="res://assets/earth/shadows/upright_51_70_v1/runtime_registration.json"
const SHA="REPLACE"
var contract:Dictionary={}
var error="not prepared"
func prepare()->bool:
 contract={};error="tree registration closure"
 if not FileAccess.file_exists(PATH) or FileAccess.get_sha256(PATH)!=SHA:return false
 var data=JSON.parse_string(FileAccess.get_file_as_string(PATH))
 if not data is Dictionary or data.get("caster")!="upright_tree_51_70":return false
 for path in data.pins:
  if not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=data.pins[path]:error="tree pin "+path;return false
 contract=data;error="";return true
'''.replace('REPLACE',sha(dest));q=P/'scripts/earth/upright_51_70_qualification.gd';assert not q.is_symlink() and all(not a.is_symlink() for a in q.parents);q.write_text(qualification)
(O/'CONTRACT_BUILD.json').write_text(json.dumps({'extra_legacy_declared_files':extra,'pins':len(pins),'registration_sha':sha(dest),'bootstrap_sha':sha(P/'scripts/earth/upright_51_70_qualification.gd')},indent=2));print('pins',len(pins),'extra',len(extra))
