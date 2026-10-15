from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[1];sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
r=json.loads((P/'request-v1.json').read_text());deps=[Path(x) for x in r['referenced_image_paths']]+[P.parent/'earth_hero_s_input_plan_v1/INPUT_PROVENANCE.json',P.parent/'earth_hero_s_input_plan_v1/SOURCE_PHASE_ANALYSIS.json',R/'assets/earth/hero/se_idle_v1/body.png',R/'assets/earth/hero/e_idle_v1/body.png']
assert (P/'prompt-v1.txt').read_text()==r['prompt']
for x in r['referenced_image_paths']:assert sha(Path(x))==r['input_sha256'][Path(x).name]
files=[q for q in sorted(P.iterdir()) if q.is_file() and q.name!='MINIMAL_SHA_MANIFEST.json']
m={'purpose':'candidate allowlist only; no Git','files':[{'path':q.name,'sha256':sha(q)} for q in files],'read_only_dependencies':[{'path':str(q.relative_to(R.parent)),'sha256':sha(q)} for q in deps],'excluded':['Project/diagnostics/**','runtime assets and manifests']}
(P/'MINIMAL_SHA_MANIFEST.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print('Verified candidate files',len(files),'dependencies',len(deps))
