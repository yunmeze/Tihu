"""Build independent original-skin research project; never runs Godot or original EXE."""
from pathlib import Path
import argparse,json,hashlib,shutil
p=argparse.ArgumentParser();p.add_argument('--repo',required=True);p.add_argument('--output',required=True);a=p.parse_args();R=Path(a.repo).resolve();O=Path(a.output).resolve();P=Path(__file__).resolve().parent;H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();d=json.loads((P/'DEPENDENCIES.json').read_text())
assert not O.exists()
for x in d['repo_dependencies']:assert H(R/x['repo_path'])==x['sha256'],x['repo_path']
shutil.copytree(P/'isolated',O)
for name in ['inventory_state.gd','default_warrior.gd']:shutil.copyfile(R/'Project/scripts/core'/name,O/'scripts/core'/name)
records=json.loads((R/'Project/data/items/catalogue.json').read_text())['records'];byid={int(r['id']):r for r in records};selected=[byid[x] for x in d['stock_ids']]
source={'map_id':'A13','source_index':2,'record':json.loads((R/'Project/data/maps/A13.json').read_text())['npcs'][2],'source_file_sha256':H(R/'Project/data/maps/A13.json')}
for name,data in [('records.json',selected),('source.json',source)]:
 f=O/'data'/name;f.write_text(json.dumps(data,ensure_ascii=False,indent=2) if name=="records.json" else json.dumps(data,ensure_ascii=False));assert H(f)==d['derived_data'][name]['sha256'],name
print('PASS exact13records/source2; original3candidate scripts copied; no engine execution')
