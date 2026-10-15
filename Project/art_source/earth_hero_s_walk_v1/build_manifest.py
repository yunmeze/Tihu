from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((P/'request-v1.json').read_text());assert (P/'prompt-v1.txt').read_text()==r['prompt'];deps=[Path(x) for x in r['referenced_image_paths']]+[P.parent/'earth_hero_s_input_plan_v1/SOURCE_PHASE_ANALYSIS.json',R/'assets/earth/hero/s_idle_v1/body.png']
for x in r['referenced_image_paths']:assert sha(Path(x))==r['input_sha256'][Path(x).name]
files=[x for x in sorted(P.rglob('*')) if x.is_file() and x.name!='MINIMAL_SHA_MANIFEST.json' and not x.name.endswith('.import')];m={'status':'static_not_passed_parent_authorized_isolated_motion_research_only_no_production','files':[{'path':str(x.relative_to(P)),'sha256':sha(x)} for x in files],'read_only_dependencies':[{'path':str(x.relative_to(R.parent)),'sha256':sha(x)} for x in deps],'exclude':['Project/diagnostics/**','runtime assets'],'generation_calls':1,'edit_calls':0,'git_performed':False};(P/'MINIMAL_SHA_MANIFEST.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
for f in m['files']:assert sha(P/f['path'])==f['sha256']
print('verified',len(files),'candidate files;',len(deps),'dependencies')
