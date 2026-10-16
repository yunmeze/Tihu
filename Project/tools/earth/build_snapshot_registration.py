#!/usr/bin/env python3
"""Build exact optional opening receiver/runtime documents from tracked Project inputs.
Only writes --output. No diagnostic/recovery inputs, Godot, Git, or source edits.
"""
from pathlib import Path
import argparse,json,hashlib,struct,re
ap=argparse.ArgumentParser();ap.add_argument('--project',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
P=args.project.resolve();d=args.output.resolve();d.mkdir(parents=True,exist_ok=True)
assert d!=P and P not in d.parents, 'Output must be outside Project'
h=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
source=json.loads((P/'data/maps/A13.json').read_text())
inv=json.loads((P/'art_source/a13_full_map_inventory_v1/inventory.json').read_text())
assert h(P/'data/maps/A13.json')=='d09549838963c8157307cc5406d3118baf69259d82459bcba0a3a8be5b34aa27'
assert h(P/'assets/original/manifest.json')=='506fba1f0fd826589046d38e4ebd5285ee9a11e3235cd78495cdd133c2e63837'
for owner in inv['owners']:
 if owner['category']!='npc':assert source['cells'][owner['stable_source_order']]==owner['source_cell']
def intersect(a,b):return a[0]<b[2] and a[2]>b[0] and a[1]<b[3] and a[3]>b[1]
# Whole original allowed/forbidden domain, deliberately wider than fixed-caster envelope.
rects={k:[2496,960,3264,1472] for k in ['hero_se','hero_s','fangzhang','lingyunzi','first_tree']};rects['left_upright']=[2319,1311,2924,1501]
casters={'fangzhang':{'npc':[64,37]},'lingyunzi':{'npc':[62,36]},'first_tree':{'cells':[[57,34],[55,37],[56,37],[58,37],[59,37],[60,37],[61,37]]},'left_upright':{'cells':[[50,41],[48,45],[49,45],[51,45],[52,45],[53,45]]},'hero_se':{},'hero_s':{}}
closure={}
for name,rect in rects.items():
 orders=set()
 for x in range(100):
  for y in range(100):
   if intersect([48*x-48,32*y-32,48*(x+1)+48,32*(y+1)+32],rect):orders.add(x*100+y)
 rows=[v for v in inv['owners'] if v['category']!='npc' and intersect(v['all_frame_bounds_xyxy'],rect)]
 orders.update(v['stable_source_order'] for v in rows)
 orders.update(x*100+y for x,y in casters[name].get('cells',[]))
 # Receiver-v2 explicitly requires the entire 30-owner hall identity, not merely local intersections.
 if name in ['lingyunzi','first_tree']:orders.update(i for i,c in enumerate(source['cells']) if c[2]==4 and 3966<=c[3]<=3995)
 closure[name]={'receiver_xyxy':rect,'cell_orders':sorted(orders),'source_owner_keys':[v['key'] for v in rows],'source_values':{str(i):source['cells'][i] for i in sorted(orders)},'caster':casters[name]}
def scan(v,pins):
 if isinstance(v,dict):
  path=v.get('path',v.get('texture'));sha=v.get('sha256')
  if isinstance(path,str) and path.startswith('res://') and isinstance(sha,str):pins[path]=sha
  for key in ['runtime_input_sha256','required_runtime_inputs','input_sha256','inputs']:
   if isinstance(v.get(key),dict):
    for f,h in v[key].items():
     if isinstance(h,str) and len(h)==64:pins[f if f.startswith('res://') else 'res://'+f]=h
  for item in v.values():scan(item,pins)
 elif isinstance(v,list):
  for item in v:scan(item,pins)
manifest={'hero_se':['se_flat_v1'],'hero_s':['se_flat_v1','s_idle_contact_v1'],'fangzhang':['fangzhang_flat_v1'],'lingyunzi':['receiver_v2'],'first_tree':['receiver_v2'],'left_upright':['left_upright_v1']}
for name,paths in manifest.items():
 pins={}
 for folder in paths:
  path='res://assets/earth/shadows/'+folder+'/manifest.json';file=P/path[6:];reg=json.loads(file.read_text())
  # receiver_v2's two caster inputs are independent; common files remain old gate prerequisites.
  if folder=='receiver_v2':
   reg['casters']={name:reg['casters'][name]}
   reg['files']={k:v for k,v in reg['files'].items() if k in ['allowed','forbidden',name+'_envelope']}
  scan(reg,pins);pins[path]=hashlib.sha256(file.read_bytes()).hexdigest()
 for f in ['data/maps/A13.json','scripts/map_load_world.gd','assets/original/monsters/a13-chicken/manifest.json']:
  pins['res://'+f]=hashlib.sha256((P/f).read_bytes()).hexdigest()
 closure[name]['pins']=pins

(d/'receiver_contract.json').write_text(json.dumps(closure,ensure_ascii=False,indent=2))
assert h(d/'receiver_contract.json')=='0292fcd96402ec0b26cd4b2d6d99cd069aa7e77a973e434f39fa6f15e1ce3534'
paths={}
def add(path,role=None):
 f=d/'receiver_contract.json' if path=='res://assets/earth/snapshot_opening/receiver_contract.json' else P/path[6:];ext=f.suffix[1:]
 if path=='res://tools/earth/build_flat_shadow_gate.py':return # explicit receiver adapter hash-only leaf, outside generic v1 types
 if ext not in ['png','json','gdshader','gd']:raise ValueError('Unsupported v1 type: '+path)
 if role is None:role='source-map' if '/data/maps/' in path else 'source-atlas-manifest' if path.endswith('/manifest.json') else 'source-atlas' if '/assets/original/' in path and ext=='png' else 'texture' if ext=='png' else 'shader' if ext=='gdshader' else 'raw-contract'
 r={'path':path,'sha256':h(f),'bytes':f.stat().st_size,'type':ext,'role':role}
 if ext=='png':r['width'],r['height']=struct.unpack('>II',f.read_bytes()[16:24])
 if path in paths and paths[path]['role']=='registration':return
 paths[path]=r
c=json.loads((d/'receiver_contract.json').read_text());add('res://assets/earth/snapshot_opening/receiver_contract.json','registration')
for group in c.values():
 for path in group['pins']:add(path)
for name in ['registration.json','static_props_registration.json','east_ground_registration.json','plant_reuse_registration.json']:
 path='res://assets/earth/first_map_review/'+name;add(path,'registration');r=json.loads((P/path[6:]).read_text())
 if name!='registration.json':
  for item in r['runtime_files']:add(item['path'],item['role'])
 else:
  for key in ['source_map','source_manifest']:add(r[key]['path'])
  for pin in r['source_atlas_pages']:add(pin['path'])
  add(r['ground']['texture'])
  for frame in r['actor']['frames']:add(frame['path'])
# Exact R6 dynamic data roots and their already-parsed texture links; no original EXE/resources.
for path in ['res://data/maps/A00.json','res://data/items/catalogue.json','res://data/story/opening.json','res://data/monsters/a13-chicken.json','res://data/hero/movement.json','res://assets/ui/original_dialog.png']:
 add(path)
for root in ['data/maps/A00.json','data/monsters/a13-chicken.json']:
 doc=json.loads((P/root).read_text());manifest=doc.get('texture_manifest')
 if manifest:
  add(manifest,'source-atlas-manifest');atlas=json.loads((P/manifest[6:]).read_text())
  for pack in atlas['packs'].values():
   for page in pack['pages']:add(page['file'],'source-atlas')
move=json.loads((P/'data/hero/movement.json').read_text())
for layer in move['layers'].values():add(layer['atlas'],'source-atlas')
# Explicit static Xuyun display group. Source frames/atlas already enter the closure above.
# Original source archive remains reproducible input, not a runtime dependency.
add('res://assets/earth/xuyun_static_v1/registration.json','registration')
add('res://assets/earth/xuyun_static_v1/body.png','texture')
add('res://scripts/earth/xuyun_guard.gd','raw-contract')
# Complete source-bound ten-owner house; raw generation research is not loaded.
for path,role in [("body.png","texture"),("ownership-id-data.png","texture"),("registration.json","registration"),("owner_bounds.json","raw-contract")]:
 add("res://assets/earth/house_280_289_v1/"+path,role)
add("res://scripts/earth/house_owner_guard.gd","raw-contract")
add("res://scripts/earth/house_owner_mask.gdshader","shader")
reg={'schema':'earth-runtime-files-v1','status':'isolated house-local visual eligibility; inherited correct runtime retained; this revision regression pending','runtime_files':sorted(paths.values(),key=lambda x:x['path']),'provenance':{'base_commit':'44db593064164f8d43a6e75dc0a0b9510a470d53','note':'Explicit domain roots. Export adapter must traverse receiver_contract caster pins and original R6/A00 fallback graph. Not a claim whole game export closure is contained here.'}}
reg['house_live_scope']={'schema':'house-building-ten-frame-live-v1','pack':'Map/Res/Building','frames':list(range(280,290)),'reload_source_sha_unchanged':True,'unrelated_pack_and_mon220_independent':True,'other_global_guards_unchanged':True}
out=d/'snapshot_runtime_registration.json';out.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n')

# Output reproduction alone is insufficient: the runtime consumer must accept its exact SHA.
consumer=P/'scripts/earth/snapshot_receiver_qualification.gd'
match=re.search(r'^const RUNTIME_REGISTRATION_SHA="([0-9a-f]{64})"$',consumer.read_text(),re.MULTILINE)
expected=h(out)
if match is None or match.group(1)!=expected:
 raise SystemExit('Receiver consumer pin mismatch: '+str(consumer)+' must pin '+expected+'; generated output is not runtime-qualified. Source was not modified.')

# V5 hash is frozen after explicit published east/plant closure merge.
print(json.dumps({'receiver_sha256':h(d/'receiver_contract.json'),'runtime_sha256':h(out),'runtime_records':len(paths),'status':'exact frozen reproduction'},indent=2))
