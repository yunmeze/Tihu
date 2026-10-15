"""Minimal v4 source and complete production texture closure; no tests/screenshots."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
P=HERE.parents[1]
OUT=P/"assets/earth/environment/ground_plate_v4"
relative=["art_source/earth_ground_plate_clean_regen_v4/"+name for name in
          ["raw.png","prompt.txt","generation.json","review_candidate.py","review.json","export_candidate.py","export-review.json","runtime-handoff-report.json","README.md","make_archive_manifest.py"]]
relative += ["art_source/earth_ground_clean_regen_plan_v4/"+name for name in
             ["prepare_inputs.py","input-plan.json","inputs/source-layout-empty-2x.png","inputs/source-layout-with-scale-actor-2x.png","inputs/concept-only-material-and-scale.png"]]
reg=json.loads((OUT/"registration.json").read_text())
relative += [str((OUT/"registration.json").relative_to(P)),str((OUT/"plate.png").relative_to(P))]
relative += [owner["texture"][6:] for owner in reg["owners"]]
assert len(reg["owners"])==64 and len(relative)==len(set(relative))
items=[]
for rel in relative:
    f=P/rel;assert f.is_file();items.append({"path":"Project/"+rel,"bytes":f.stat().st_size,"sha256":hashlib.sha256(f.read_bytes()).hexdigest()})
for owner in reg["owners"]:
    assert hashlib.sha256((P/owner["texture"][6:]).read_bytes()).hexdigest()==owner["texture_sha256"]
report={"schema":"earth-ground-v4-minimal-source-production-archive-v1","status":"Frozen current bounded independent-sample candidate source and complete production closure; runtime test material excluded",
        "files":items,"payload_count":len(items),"payload_bytes":sum(x["bytes"] for x in items),
        "production_closure":{"owner_textures":64,"optional_shared_plate":1,"registration":1},
        "baseline_dependencies":["Project/art_source/earth_ground_plate_source_v1/source-layout-contract.json","Project/art_source/earth_ground_plate_source_v1/material-layout-board.png","Project/art_source/earth_base_style_concept_v1/concept.png","Project/data/maps/A13.json","Project/assets/original/manifest.json","Project/art_source/earth_ground_plate_grass_edit_v2/archive-manifest.json","Project/art_source/earth_ground_plate_scale_edit_v3/archive-manifest.json"],
        "excluded":["ALL runtime screenshot/log evidence, including shared/earth-ground-v4","Test scripts and temporary diagnostic images","Godot .import/.godot caches","Redundant concept crop PNGs reproducible from source","Runtime scripts/docs owned by designated runtime worker, to be archived through that worker's separate explicit allowlist"],
        "reproduction_note":"Prepared GPU actor-scale image is retained as an actual generation input; full runtime screenshots/logs are deliberately local-only. Imagegen itself is stochastic; all actual input/raw/prompts are retained. Direct64-owner export is deterministic and byte-exact."}
(HERE/"archive-manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
names=[x["path"] for x in items]+["Project/"+str((HERE/name).relative_to(P)) for name in ["archive-manifest.json","ARCHIVE_FILES.txt"]]
(HERE/"ARCHIVE_FILES.txt").write_text("\n".join(names)+"\n")
print(json.dumps({"payload_count":len(items),"payload_bytes":report["payload_bytes"],"complete_production_owner_count":64,"runtime_test_evidence_included":False}))
