#!/usr/bin/env python3
"""Freeze exact Git blobs into a new external directory; export/verify Linux PCK."""
import pathlib,json,sys,os,shutil,subprocess,hashlib,argparse
from generate_allowlist import run
B=pathlib.Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('repository');p.add_argument('new_output_directory');p.add_argument('--static-only',action='store_true');a=p.parse_args()
repo=pathlib.Path(a.repository).resolve();frozen=pathlib.Path(a.new_output_directory).resolve();policy=json.loads((B/'policy.json').read_text())
if frozen.exists():raise SystemExit('New output directory required')
if frozen==repo or (repo/'Project')==frozen or (repo/'Project') in frozen.parents:raise SystemExit('Output must be outside Project')
def git(*args):return subprocess.check_output(['git','-C',str(repo),*args])
if git('rev-parse',policy['source_commit']+'^{tree}').decode().strip()!=policy['source_tree']:raise SystemExit('Frozen source tree mismatch')
frozen.mkdir(parents=True);P=frozen/'Project';P.mkdir();rows=[]
for row in policy['files']+[dict(policy['project_config'],path='res://project.godot')]:
 rel=row['path'][6:];data=git('show',policy['source_commit']+':Project/'+rel)
 if len(data)!=row['bytes'] or hashlib.sha256(data).hexdigest()!=row['sha256']:raise ValueError(('Frozen Git blob differs',rel))
 f=P/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data);rows.append({'path':rel,'bytes':len(data),'sha256':row['sha256']})
proof={'commit':policy['source_commit'],'tree':policy['source_tree'],'files':rows}
(frozen/'FROZEN_SOURCE.json').write_text(json.dumps(proof,indent=2)+'\n')
manifest=run(P,policy);(frozen/'allowlist.json').write_text(json.dumps(manifest,indent=2)+'\n')
if a.static_only:
 print('PASS: frozen 280-file static closure; Godot NOT run');raise SystemExit(0)
O=frozen/'pack-run'
if O.exists():raise SystemExit('New pack-run required')
O.mkdir();manifest=json.loads((frozen/'allowlist.json').read_text());mf=frozen/'allowlist.json'
addon=P/'addons/raw_allowlist';shutil.copytree(B/'plugin',addon);shutil.copy2(mf,addon/'allowlist.json')
config=P/'project.godot';config.write_text(config.read_text().replace('run/main_scene="res://scenes/game.tscn"','run/main_scene="res://scenes/earth_new_game_candidate.tscn"')+'\n[editor_plugins]\nenabled=PackedStringArray("res://addons/raw_allowlist/plugin.cfg")\n')
files=[r['path'] for r in manifest['files'] if r['type'] in ('gd','tscn','gdshader','tres','png') and not r['path'].startswith('res://art_source/')]
(P/'export_presets.cfg').write_text('[preset.0]\nname="Closure probe"\nplatform="Linux"\nrunnable=true\nexport_filter="resources"\nexport_files=PackedStringArray('+','.join(json.dumps(p) for p in files)+')\ninclude_filter=""\nexclude_filter="addons/*,docs/*,recovery/*"\nexport_path=""\nscript_export_mode=0\n[preset.0.options]\nbinary_format/architecture="x86_64"\n')
env=os.environ.copy()
for key in ('XDG_DATA_HOME','XDG_CONFIG_HOME','XDG_CACHE_HOME'):
 d=O/key.lower();d.mkdir();env[key]=str(d)
def command(name,args,extra={}):
 e=env.copy();e.update(extra);r=subprocess.run(args,env=e,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=300);(O/(name+'.log')).write_text(r.stdout)
 if r.returncode or any(s in r.stdout for s in ('ERROR:','SCRIPT ERROR','Parse Error')):raise RuntimeError(name+' failed; NOT VALIDATED')
 return r.stdout
command('import',['godot','--headless','--editor','--path',str(P),'--import'])
pack=O/'UNVERIFIED.pck';log=command('export',['godot','--headless','--path',str(P),'--export-pack','Closure probe',str(pack)])
assert 'RAW_ALLOWLIST_EXPORT_ADDED '+str(len(manifest['files'])) in log
empty=O/'empty-runtime';empty.mkdir();(empty/'project.godot').write_text('config_version=5\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
for name,path,pk in [('source',P,''),('packed',empty,str(pack))]:
 log=command(name,['godot','--headless','--path',str(path),'--script',str(B/'verify_data_pack.gd')],{'ALLOWLIST':str(mf),'PACK':pk,'RESULT':str(O/(name+'-status.json'))})
 assert 'OPTIONAL_SNAPSHOT_148_SIX_RECEIVERS_XUYUN_OPENING_A00_PASS' in log
assert (O/'source-status.json').read_bytes()==(O/'packed-status.json').read_bytes()
pack.rename(O/'LINUX_DATA_PACK_VERIFIED_NOT_WINDOWS.pck')
(O/'RESULT.json').write_text(json.dumps({'status':'passed','source_commit':proof['commit'],'source_tree':proof['tree'],'raw_files':len(manifest['files']),'source_packed_equal':True,'platform':'Linux Godot data PCK; Windows not tested'},indent=2)+'\n')
print('PASS Linux data pack, raw closure, review/walk, optional opening and A00; NOT Windows')
