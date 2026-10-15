from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((P/'request-v1.json').read_text());assert (P/'prompt-v1.txt').read_text()==r['prompt'];deps=[Path(x) for x in r['referenced_image_paths']]+[P.parent/'earth_hero_s_walk_v1/registration-v1.json']
for x in r['referenced_image_paths']:assert sha(Path(x))==r['input_sha256'][Path(x).name]
assert sha(P/'frozen-registration.json')==r['frozen_registration_sha256']
files=[x for x in sorted(P.iterdir()) if x.is_file() and x.name!='MINIMAL_SHA_MANIFEST.json'];m={'status':'FAILED_FROZEN_S_GENERATION_PAUSED_SOURCE_WALK_REMAINS','files':[{'path':x.name,'sha256':sha(x)} for x in files],'read_only_dependencies':[{'path':str(x.relative_to(R.parent)),'sha256':sha(x)} for x in deps],'exclude':['Project/diagnostics/**','runtime assets/scripts'],'edit_calls':1,'retry_calls':0,'alpha_cleanup':False,'refit':False,'git_performed':False};(P/'MINIMAL_SHA_MANIFEST.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
for f in m['files']:assert sha(P/f['path'])==f['sha256']
print('Frozen',len(files),'files;',len(deps),'dependencies; raw',sha(P/'raw-edit-v1.png'))
