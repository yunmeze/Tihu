"""Exact minimal source/AI-raw/registration archive, excludes disposable review images."""
from pathlib import Path
import json,hashlib
HERE=Path(__file__).resolve().parent;P=HERE.parents[1];A=P/'art_source'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write_inventory(folder,names,extra=None):
 files=[]
 for name in names:
  f=folder/name;assert f.is_file(),f;files.append({'path':str(f.relative_to(P)),'bytes':f.stat().st_size,'sha256':sha(f)})
 j={'status':'Minimal reproducible archive; no Git operations by this worker','files':files,'count':len(files),'bytes':sum(f['bytes']for f in files)}
 if extra:j.update(extra)
 (folder/'ARCHIVE_FILES.json').write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n');return files
local=['build_local_inputs.py','measure_local_candidates.py','build_archive_inventory.py','local-input-contract.json','LOCAL_EDIT_PROPOSAL.md']
for side in ['left','right']:
 local+=[f'{side}/prompt-draft.txt']+[f'{side}/{n}'for n in ['current-2x-reference.png','local-target-guide-2x.png','source-context-4x-reference.png']]
new=write_inventory(HERE,local,{'note':'Six imagegen inputs are retained even though technically reproducible, because they are exact sent bytes. Native crops and side-by-side/grid boards are rebuildable diagnostics.'})
for side in ['left','right']:
 new+=write_inventory(A/f'earth_training_hall_{side}_stair_candidate_v1',['raw.png','prompt.txt','generation-input.json','measurements.json','REVIEW.md'])
new+=write_inventory(A/'earth_training_hall_local_assembly_review_v1',['build_review.py','measure_assembly.py','partition-contract.json','measurements.json','REVIEW.md','full-building-candidate-review.png'],{'note':'Transparent layer/mask images, gray-background full view and seam boards are derived by build_review.py and excluded from minimal archive.'})
reg=A/'earth_training_hall_registration_v1';names=['build_registration.py','verify_registration.py','registration.json','validation.json','HANDOFF.md']+[str(p.relative_to(reg))for p in sorted((reg/'owners').glob('owner-*.png'))];new+=write_inventory(reg,names,{'note':'Runtime source cutouts and registration retained. Label/support masks and material-review board are deterministic diagnostics.'})
old=[]
for folder in ['earth_training_hall_edit_plan_v1','earth_training_hall_candidate_v2']:
 old+=json.loads((A/folder/'ARCHIVE_FILES.json').read_text())['files']
all_files={f['path']:f for f in old+new}
# Validate every historic frozen file, do not silently rewrite historic hashes.
for f in all_files.values():assert sha(P/f['path'])==f['sha256'],f['path']
out={'scope':'Complete Earth training-hall source package, v1/v2 raw history, local input/edit raws, approved joint-review assembly and30-owner candidate. Excludes temporary/reproducible image diagnostics; never excludes actual imagegen inputs. Ordinary runtime-assets bundle, if later approved, has its own inventory.','files':list(all_files.values()),'count':len(all_files),'bytes':sum(f['bytes']for f in all_files.values()),'reproduce_order':['python Project/art_source/earth_training_hall_source_v1/build_inputs.py','python Project/art_source/earth_training_hall_candidate_v1/measure_candidate.py','python Project/art_source/earth_training_hall_edit_plan_v1/build_plan.py','python Project/art_source/earth_training_hall_candidate_v2/measure_fixed_reference.py','python Project/art_source/earth_training_hall_local_stair_plan_v1/build_local_inputs.py','python Project/art_source/earth_training_hall_local_stair_plan_v1/measure_local_candidates.py','python Project/art_source/earth_training_hall_local_assembly_review_v1/build_review.py','python Project/art_source/earth_training_hall_local_assembly_review_v1/measure_assembly.py','python Project/art_source/earth_training_hall_registration_v1/build_registration.py','python Project/art_source/earth_training_hall_registration_v1/verify_registration.py'],'ai_reproducibility':'Image generation is stochastic, not replay-byte deterministic. Actual input bytes, exact prompts, raw outputs and hashes are archived; technical crop/measurement/partition steps are deterministic.'}
(HERE/'COMPLETE_ARCHIVE_FILES.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'count':out['count'],'bytes':out['bytes'],'inventory':str((HERE/'COMPLETE_ARCHIVE_FILES.json').relative_to(P))}))
