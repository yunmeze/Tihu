"""Exact cross-directory whitelist of required tree deliverables/inputs, not a copy/export."""
from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;P=O.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=[]
def add(base,names,role):
 for n in names:files.append({'path':str(Path(base)/n),'role':role})
add('art_source/earth_first_tree_candidate_v1',['raw.png','prompt.txt'],'first generation raw + actual prompt')
add('art_source/earth_first_tree_boundary_repair_v2',['raw.png','prompt.txt'],'one approved repair raw + actual prompt')
add('art_source/earth_first_tree_registration_v1',['README.md','build_registration.py','registration.json','validation.json','owner-labels.png']+[f'owners/owner-{n}.png'for n in range(292,299)],'one-instance7owner candidate + exact reproducible partition')
add('art_source/earth_vegetation_input_plan_v1',['broad_tree_57_34_source_native.png','concept_tree_branch_foliage.png','concept_bark_detail.png','concept_crops.json','source_contract.json'],'actual generation inputs + crop provenance + source-owner contract')
add('art_source/earth_base_style_concept_v1',['concept.png'],'approved authority underlying cropped material references')
add('docs',['EARTH_ART_BIBLE_V1.md'],'approved style and technical authority')
for f in files:
 p=P/f['path'];assert p.is_file();f.update({'bytes':p.stat().st_size,'sha256':sha(p)})
old=P/'art_source/earth_vegetation_input_plan_v1/ARCHIVE_SHA256.json';d=json.loads(old.read_text())
for f in d['files']:assert sha(old.parent/f['path'])==f['sha256']
# Current map must be preserved with the base project; no new full-original-game duplicate is requested.
deps=['data/maps/A13.json','assets/original/manifest.json','art_source/earth_vegetation_input_plan_v1/ARCHIVE_SHA256.json']
out={'schema':'earth-first-tree-minimal-merged-archive-v1','path_base':'Project/','scope':'v1raw,v2raw,actual prompts,7owner partition recipe/registration/resources,actual image inputs and their authorities. No diagnostics/logs, no shrub, no other tree instances.','files':sorted(files,key=lambda f:f['path']),'existing_project_dependencies':[{'path':n,'sha256':sha(P/n),'note':'Keep existing source dependency; not a newly generated archive duplicate.'}for n in deps],'frozen_input_40_verified':True,'excluded_reproducible_material':['v1/v2 gray/dark/light and registration screenshots','v1/v2 intermediate measurement scripts/reports; final registration validation captures relevant immutable transform and reconstruction','obsolete pending repair plan (executed prompt is archived)','unused other-instance native/alpha/owner maps','logs,GUIcaptures,generated_images duplicate originals'],'manifest_note':'This file is the exact whitelist, not a claim Git was operated. Metadata README/build_minimal_manifest.py can be archived alongside this manifest if desired; they are not dependencies of the candidate.'}
(O/'MINIMAL_SHA256.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('FILES',len(files));print('MANIFEST_SHA256',sha(O/'MINIMAL_SHA256.json'))
