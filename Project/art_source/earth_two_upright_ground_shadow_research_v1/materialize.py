"""Portable source/overlay materializer, not a complete runnable v2 game."""
from pathlib import Path
import argparse,json,hashlib,shutil
from PIL import Image,ImageChops
p=argparse.ArgumentParser();p.add_argument('--repo',required=True);p.add_argument('--output');p.add_argument('--legacy-project');a=p.parse_args();P=Path(__file__).resolve().parent;R=Path(a.repo).resolve();H=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();d=json.loads((P/'DEPENDENCIES.json').read_text())
for path,r in d['tracked_sources'].items():assert H(R/r['repo_path'])==r['sha256'],path
for folder in ['upright-51-70-cpu-v1','upright-40-72-cpu-v1']:
 D=P/folder;c=json.loads((D/'contract.json').read_text());s=json.loads((D/'CPU_RESULT.json').read_text());load=lambda n:Image.open(D/(n+'.png')).convert('1')
 expected=ImageChops.logical_and(ImageChops.logical_and(load('root-error-envelope'),load('floor-opaque-coverage')),ImageChops.invert(load('pool-filter-uncertainty-excluded')))
 assert expected.tobytes()==load('allowed-provisional').tobytes();assert expected.convert('L').histogram()[255]==s['provisional_allowed_cells']
 for f in D.glob('*.png'):assert H(f)==c['files'][f.name],f
empty=R/d['tracked_sources']['res://assets/earth/environment/upright_tree_v1/owners/owner-304.png']['repo_path'];assert Image.open(empty).convert('RGBA').getbbox(alpha_only=False) is None
missing=[]
for row in d['historical_nonmatching_or_untracked_bindings']:
 f=Path(a.legacy_project)/row['path'][6:] if a.legacy_project else None
 if f is None or not f.is_file() or H(f) not in row['accepted_historical_hashes']:missing.append(row['path'])
if a.output:
 O=Path(a.output).resolve();assert not O.exists();shutil.copytree(P/'runtime-overlay',O/'Project')
 # Explicit read-only links to original published dependencies save space. These are not a publishable Git tree.
 for path,r in d['tracked_sources'].items():
  target=O/'Project'/path[6:]
  if not target.exists():target.parent.mkdir(parents=True,exist_ok=True);target.symlink_to((R/r['repo_path']).resolve())
 (O/'MATERIALIZATION_STATUS.json').write_text(json.dumps({'status':'overlay and source links only; NOT runnable full v2','unresolved_historical_bindings':missing,'full_inventory_required':d['external_full_inventory'],'complete_engine_contract':'runtime-overlay assets runtime_registration.json410pins; all must be separately resolved'},indent=2)+'\n')
print(json.dumps({'tracked_dependencies_exact':len(d['tracked_sources']),'both_mask_relations_and_frozen_hashes_exact':True,'historical_bindings_missing':missing,'full_cpu_geometry_replay':False,'Godot_replay':False},indent=2))
