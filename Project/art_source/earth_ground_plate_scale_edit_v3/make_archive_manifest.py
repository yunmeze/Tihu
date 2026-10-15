"""Explicit minimal asset/research allowlist. Never includes runtime test evidence."""
from pathlib import Path
import json,hashlib
HERE=Path(__file__).resolve().parent
P=HERE.parents[1]
relative=[
    "art_source/earth_ground_plate_scale_edit_v3/"+name for name in
    ["raw.png","prompt.txt","generation.json","review_candidate.py","review.json","README.md","make_archive_manifest.py"]]
relative += ["art_source/earth_ground_scale_edit_plan_v3/"+name for name in
    ["input-plan.json","inputs/same-frame-actor-scale-reference.png","scale-comparison-reference.png","inputs/concept-green-tone-native.png"]]
relative += ["art_source/earth_ground_clean_regen_plan_v4/"+name for name in
    ["README.md","prepare_inputs.py","prompt-draft.txt","input-plan.json","inputs/source-layout-empty-2x.png","inputs/source-layout-with-scale-actor-2x.png","inputs/concept-only-material-and-scale.png"]]
items=[]
for rel in relative:
    f=P/rel;assert f.is_file();items.append({"path":"Project/"+rel,"bytes":f.stat().st_size,"sha256":hashlib.sha256(f.read_bytes()).hexdigest()})
report={"schema":"earth-ground-v3-minimal-archive-v2","status":"Frozen minimal assets/raw/prompts/geometry reports/recipes plus clean-source v4 inputs; runtime screenshots/logs excluded",
        "files":items,"payload_count":len(items),"payload_bytes":sum(x["bytes"] for x in items),
        "baseline_dependencies":["Project/art_source/earth_ground_plate_grass_edit_v2/archive-manifest.json","Project/art_source/earth_ground_plate_source_v1/source-layout-contract.json","Project/art_source/earth_base_style_concept_v1/concept.png"],
        "excluded":["ALL evidence/ runtime screenshots and native.log; SHA/conclusions retained in review.json only","Any test scripts or temporary diagnostic PNGs","Godot caches/imports","Redundant concept crop PNGs reproducible from accepted concept","Unrelated runtime changes"],
        "reproduction_note":"Prepared generation inputs are the archival authority. Actor-only references are frozen GPU-derived inputs; their original full test scene screenshots/logs are deliberately local-only. Source-semantic/concept derivatives can be reproduced from included recipe and existing baseline assets."}
(HERE/"archive-manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
files=[x["path"] for x in items]+["Project/"+str((HERE/name).relative_to(P)) for name in ["archive-manifest.json","ARCHIVE_FILES.txt"]]
(HERE/"ARCHIVE_FILES.txt").write_text("\n".join(files)+"\n")
print(json.dumps({"payload_files":len(items),"payload_bytes":report["payload_bytes"],"runtime_test_evidence_included":False}))
