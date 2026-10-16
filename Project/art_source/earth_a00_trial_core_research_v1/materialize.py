"""Build a small isolated pure-core source bundle from pinned Git blobs. No Godot/tests/UI."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,importlib
sys.dont_write_bytecode=True
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parent;out=a.output.resolve();assert not out.exists(),'Require a new external directory'
d=json.loads((root/'DEPENDENCIES.json').read_text());commit=d['commit'];sha=lambda b:hashlib.sha256(b).hexdigest()
def git_bytes(path):
 assert not path.startswith('/') and '..' not in Path(path).parts
 return subprocess.check_output(['git','-C',str(a.repo),'show',commit+':'+path])
for rel,h in json.loads((root/'SHA256.json').read_text()).items():assert sha((root/rel).read_bytes())==h,rel
# Research sources can be larger; verify sequentially, never copy their data tree.
index=json.loads((root/'source-study/SOURCE_INDEX.json').read_text());verified=[]
for r in index['sources']:
 b=git_bytes(r['path']);assert sha(b)==r['sha256'] and len(b)==r['bytes'],r['path'];verified.append(r['path'])
blobs={}
for r in d['files']:
 b=git_bytes(r['path']);assert sha(b)==r['sha256'] and len(b)==r['bytes'];blobs[r['path']]=b
out.mkdir();project=out/'Project';(project/'scripts/core').mkdir(parents=True);(project/'data').mkdir()
for name in ('a00_trial_core','dialogue_vm'):(project/f'scripts/core/{name}.gd').write_bytes((root/f'scripts/core/{name}.gd').read_bytes())
for name in ('inventory_state','default_warrior','npc_source_identity','map_load_bridge'):(project/f'scripts/core/{name}.gd').write_bytes(blobs[f'Project/scripts/core/{name}.gd'])
(project/'project.godot').write_text('config_version=5\n[application]\nconfig/name="A00 pure core source research"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
(project/'data/A00.json').write_bytes(blobs['Project/data/maps/A00.json'])
records=json.loads(blobs['Project/data/items/catalogue.json'])['records'];selected=[records[i] for i in (0,5,252)];assert [r['id'] for r in selected]==[0,5,252]
(project/'data/records.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2)+'\n')
# Invoke only the tracked read-only parser function, never its extraction main().
parsers=out/'parsers';parsers.mkdir()
for name in ('lp_original','extract_a13_original'):(parsers/(name+'.py')).write_bytes(blobs[f'Project/tools/{name}.py'])
source_root=out/'original';raw=source_root/'Data/Map/A00.lpMap';raw.parent.mkdir(parents=True);raw.write_bytes(blobs['原版游戏/Data/Map/A00.lpMap']);sys.path.insert(0,str(parsers));parser=importlib.import_module('extract_a13_original');parser.SOURCE=source_root;parsed=parser.parse_map(raw)
extracted=json.loads(blobs['Project/data/maps/A00.json']);assert all(parsed[k]==extracted[k] for k in parsed)
itemraw=blobs['原版游戏/Data/Item0.lpRes']
for i,offset in ((0,10),(5,494)):assert bytes.fromhex(records[i]['raw_record_hex'])==itemraw[offset:offset+96]
result={'status':'SOURCE_MATERIALIZATION_AND_READONLY_PARSE_PASS','historical_references_verified':len(verified),'core_sha256':sha((project/'scripts/core/a00_trial_core.gd').read_bytes()),'map_bytes_exact':True,'parsed_map_keys_equal':list(parsed),'records':[0,5,252],'solver_or_engine_run':False,'tests_included':False,'can_rerun_539':False,'playable_scene':False}
(out/'MATERIALIZATION_RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
