#!/usr/bin/env python3
"""Create a NEW isolated staging tree, export only data PCK, verify before naming it validated."""
import argparse,io,json,os,pathlib,shutil,subprocess,tarfile
from generate_allowlist import run
P=pathlib.Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('repository');p.add_argument('new_output_directory');a=p.parse_args();repo=pathlib.Path(a.repository).resolve();out=pathlib.Path(a.new_output_directory).resolve()
if out.exists():raise SystemExit('Use a new output directory; existing output will not be overwritten')
out.mkdir(parents=True);stage=out/'staging';stage.mkdir();policy=json.loads((P/'policy.json').read_text())
if policy.get('pending_reviewed_overlay'):raise SystemExit('Pending source changes: bind a reviewed committed source tree before reproducible export')
tree=subprocess.check_output(['git','-C',str(repo),'rev-parse',policy['source_commit']+'^{tree}']).decode().strip()
if tree!=policy['source_tree']:raise SystemExit('Frozen source tree mismatch')
archive=subprocess.check_output(['git','-C',str(repo),'archive',policy['source_commit'],'Project'])
with tarfile.open(fileobj=io.BytesIO(archive)) as t:t.extractall(stage,filter='data')
project=stage/'Project';manifest=run(project,policy);mf=out/'allowlist.json';mf.write_text(json.dumps(manifest,indent=2)+'\n')
addon=project/'addons/raw_allowlist';shutil.copytree(P/'plugin',addon);shutil.copy2(mf,addon/'allowlist.json')
f=project/'project.godot';f.write_text(f.read_text().replace('run/main_scene="res://scenes/game.tscn"','run/main_scene="res://scenes/earth_first_map_review.tscn"')+'\n[editor_plugins]\nenabled=PackedStringArray("res://addons/raw_allowlist/plugin.cfg")\n')
files=[f['path'] for f in manifest['files'] if f['type'] in ('gd','tscn','gdshader','tres','png') and not f['path'].startswith('res://art_source/')]
(project/'export_presets.cfg').write_text('[preset.0]\nname="Closure probe"\nplatform="Linux"\nrunnable=true\nexport_filter="resources"\nexport_files=PackedStringArray('+','.join(json.dumps(s) for s in files)+')\ninclude_filter=""\nexclude_filter="addons/*,docs/*,recovery/*"\nexport_path=""\nscript_export_mode=0\n[preset.0.options]\nbinary_format/architecture="x86_64"\n')
env=os.environ.copy()
for key in ('XDG_DATA_HOME','XDG_CONFIG_HOME','XDG_CACHE_HOME'):
 d=out/key.lower();d.mkdir();env[key]=str(d)
def command(name,args,extra=None):
 e=env.copy();e.update(extra or {})
 r=subprocess.run(args,env=e,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=240)
 (out/(name+'.log')).write_text(r.stdout)
 if r.returncode or 'ERROR:' in r.stdout or 'SCRIPT ERROR' in r.stdout:raise RuntimeError(name+' failed; output is NOT validated')
 return r.stdout
command('import',['godot','--headless','--editor','--path',str(project),'--import'])
pack=out/'UNVERIFIED.pck'
log=command('export',['godot','--headless','--path',str(project),'--export-pack','Closure probe',str(pack)])
if 'RAW_ALLOWLIST_EXPORT_ADDED '+str(len(manifest['files'])) not in log:raise RuntimeError('export callback not confirmed')
empty=out/'empty-runtime';empty.mkdir();(empty/'project.godot').write_text('config_version=5\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
for name,path,pk in [('source',project,''),('packed',empty,str(pack))]:
 command(name,['godot','--headless','--path',str(path),'--script',str(P/'verify_data_pack.gd')],{'ALLOWLIST':str(mf),'PACK':pk,'RESULT':str(out/(name+'-status.json'))})
if (out/'source-status.json').read_bytes()!=(out/'packed-status.json').read_bytes():raise RuntimeError('runtime status mismatch')
pack.rename(out/'LINUX_DATA_PACK_VERIFIED_NOT_WINDOWS.pck')
print('PASS: exact raw bytes, callbacks, 178 ground, plants 24/81, pool7/clump3, actor18+E6, source fallback and walk6+6, all source/packed readiness equal. Windows NOT tested.')
