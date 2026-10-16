"""Re-pin the owned single-tree entry DAG. No engine, no receiver geometry changes.
Run only against an owned overlay; all write leaves and ancestors must be ordinary.
"""
from pathlib import Path
import json,hashlib,re,subprocess,argparse
ap=argparse.ArgumentParser();ap.add_argument('--project',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();P=args.project.absolute();O=args.output.absolute();O.mkdir(parents=True,exist_ok=True)
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(rel,s):
 p=P/rel
 for q in [p,*p.parents]:
  if q==P.parent:break
  assert not q.is_symlink(),'linked write '+str(q)
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
def dump(rel,v):put(rel,json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def update_const(rel,key,sha):put(rel,re.sub('const '+key+'="[a-f0-9]+"','const '+key+'="'+sha+'"',(P/rel).read_text()))
def records(paths):return [{'path':u,'sha256':h(P/u[6:]),'bytes':(P/u[6:]).stat().st_size} for u in sorted(set(paths))]
main='assets/earth/snapshot_opening/snapshot_runtime_registration.json';consumer='scripts/earth/snapshot_receiver_qualification.gd'
cmd=['python3',str(P/'tools/earth/build_snapshot_registration.py'),'--project',str(P),'--output',str(O)]
a=subprocess.run(cmd,capture_output=True,text=True)
assert (O/'snapshot_runtime_registration.json').is_file(),a.stderr
# This builder can first report the expected old consumer mismatch before repinning.
put(main,(O/'snapshot_runtime_registration.json').read_text());update_const(consumer,'RUNTIME_REGISTRATION_SHA',h(P/main))
a=subprocess.run(cmd,capture_output=True,text=True);assert a.returncode==0,a.stdout+a.stderr
assert (O/'receiver_contract.json').read_bytes()==(P/'assets/earth/snapshot_opening/receiver_contract.json').read_bytes(),'old receiver changed'
root='assets/earth/shadows/s_walk_contact_v3/';c=json.loads((P/root/'receiver_contract.json').read_text())
for group in c.values():
 for u in group['pins']:group['pins'][u]=h(P/u[6:])
dump(root+'receiver_contract.json',c)
r=json.loads((P/root/'runtime_registration.json').read_text());r['runtime_files']=records(x['path'] for x in r['runtime_files']);dump(root+'runtime_registration.json',r)
for key,name in [('WALK_CONTRACT_SHA','receiver_contract.json'),('WALK_REGISTRATION_SHA','runtime_registration.json')]:update_const('scripts/earth/s_walk_contact_v3_qualification.gd',key,h(P/root/name))
# Existing body/walk publication root remains upstream of the independent tree bootstrap.
sw='assets/earth/hero/s_walk_arap_v1/s_walk_runtime_registration.json';r=json.loads((P/sw).read_text());r['files']=records(x['path'] for x in r['files']);dump(sw,r)
tree='assets/earth/shadows/upright_51_70_v1/runtime_registration.json';r=json.loads((P/tree).read_text())
for u in r['pins']:r['pins'][u]=h(P/u[6:])
for rel in ['scripts/earth/upright_51_70_controller.gd','scenes/earth_new_game_candidate.tscn','tools/earth/build_upright_controller_registration.py']:r['pins']['res://'+rel]=h(P/rel)
r['status']='owned production-controller integration; qualification pending';dump(tree,r)
update_const('scripts/earth/upright_51_70_qualification.gd','SHA',h(P/tree))
paths=set(r['pins'])|{'res://'+tree,'res://scripts/earth/upright_51_70_qualification.gd'}
dump('assets/earth/shadows/upright_51_70_v1/controller_runtime_registration.json',{'schema':'upright-51-70-controller-root-v1','base_commit':'3e9a8ffaec0c1a8bb4b247d02fb2ea92acfd16a7','files':records(paths),'hash_graph':'main leaves -> snapshot qualifier -> walk contract/declaration/qualifier -> body root -> tree sidecar -> tree qualifier -> this publication root; excludes own digest'})
print(json.dumps({'main_sha256':h(P/main),'tree_sha256':h(P/tree),'publication_records':len(paths)}))
