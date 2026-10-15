from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent;R=P.parents[1];sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
r=json.loads((P/'request-v1.json').read_text());assert (P/'prompt-v1.txt').read_text()==r['prompt']
deps=[Path(x) for x in r['referenced_image_paths']]+[P.parent/'earth_hero_s_idle_v1/registration-v1.json',P.parent/'earth_hero_s_idle_edit_plan_v1/EDIT_PLAN.md',P.parent/'earth_hero_s_input_plan_v1/SOURCE_PHASE_ANALYSIS.json',R/'assets/earth/hero/se_idle_v1/body.png',R/'assets/earth/hero/e_idle_v1/body.png']
for x in r['referenced_image_paths']:assert sha(Path(x))==r['input_sha256'][Path(x).name]
assert sha(P/'frozen-original-registration.json')==r['frozen_original_registration_sha256']
files=[x for x in sorted(P.rglob('*')) if x.is_file() and x.name not in ['MINIMAL_SHA_MANIFEST.json','ARCHIVE_ALLOWLIST.json']];m={'status':'static_candidate_submitted_for_parent_review_not_runtime','files':[{'path':str(x.relative_to(P)),'sha256':sha(x)} for x in files],'read_only_dependencies':[{'path':str(x.relative_to(R.parent)),'sha256':sha(x)} for x in deps],'exclude':['Project/diagnostics/**','runtime assets/manifests'],'git_performed':False};(P/'MINIMAL_SHA_MANIFEST.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
for x in m['files']:assert sha(P/x['path'])==x['sha256']
print('Verified',len(files),'candidate files,',len(deps),'dependencies. Frozen original registration exact.')
