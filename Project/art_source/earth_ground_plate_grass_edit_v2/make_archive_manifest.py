"""Explicit minimal archive allowlist; no Git operations or source changes."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
P = HERE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
files = ["docs/EARTH_GROUND_PLATE_V1.md"]
files += ["art_source/earth_ground_plate_source_v1/" + n for n in [
    "prepare_source.py", "source-layout-contract.json", "source-floor-native.png",
    "source-material-zones-native.png", "material-layout-board.png", "source-alpha-native.png"]]
files += ["art_source/earth_ground_plate_candidate_v1/" + n for n in [
    "raw.png", "prompt.txt", "generation.json", "review.json", "review_candidate.py", "README.md",
    "inputs/concept-paving-material.png", "inputs/concept-grass-material.png", "inputs/reference-crops.json"]]
files += ["art_source/earth_ground_plate_grass_edit_v2/" + n for n in [
    "raw.png", "prompt.txt", "generation.json", "review.json", "layout-review.json", "export-review.json", "README.md",
    "review_edit.py", "review_layout.py", "export_candidate.py", "make_archive_manifest.py",
    "inputs/concept-grass-green-material.png", "inputs/concept-grass-midgreen-material.png",
    "inputs/protected-road-mask.png", "inputs/reference-crops.json"]]
registration_path = P / "assets/earth/environment/ground_plate_v2/registration.json"
registration = json.loads(registration_path.read_text())
files += [str(registration_path.relative_to(P)), registration["shared_plate"]["texture"][6:]]
files += [o["texture"][6:] for o in registration["owners"]]
assert len(files) == len(set(files))
assert len(registration["owners"]) == 64
for rel in files:
    assert (P / rel).is_file(), rel
    assert "diagnostic" not in Path(rel).name
    assert not rel.endswith(".import")
entries = [{"path": "Project/" + rel, "bytes": (P / rel).stat().st_size, "sha256": sha(P / rel)} for rel in sorted(files)]
self_files = ["Project/art_source/earth_ground_plate_grass_edit_v2/archive-manifest.json",
              "Project/art_source/earth_ground_plate_grass_edit_v2/ARCHIVE_FILES.txt"]
dependency_paths = ["data/maps/A13.json", "assets/original/manifest.json", "assets/original/Map/Res/FloorBig/0.png",
                    "assets/original/Map/Res/Building/0.png", "scripts/world_view.gd", "scripts/core/movement.gd", "project.godot",
                    "art_source/a13_main_temple_source/source-group-contract.json",
                    "art_source/a13_ground_source/source-group-contract.json",
                    "art_source/a13_ground_materials_v2/semantic-mask-research.json",
                    "art_source/earth_training_hall_source_v1/input-contract.json",
                    "art_source/earth_base_style_concept_v1/concept.png"]
manifest = {"schema": "earth-ground-archive-allowlist-v1", "status": "explicit archival allowlist only; no Git operation performed",
            "files": entries, "also_archive_manifest_files": self_files,
            "listed_payload_files": len(entries), "payload_bytes": sum(e["bytes"] for e in entries),
            "scope": "Source layout, both immutable raws, their exact prompts/references, deterministic review/export recipes, complete64-owner production candidate resource closure.",
            "excluded": ["All temporary *diagnostic.png comparisons/overlays", "source-owners-board.png and source-layout-routes-board.png",
                         "selected-floor-native.png duplicate of source-floor-native.png", "reproducible guide/receiver/2x-alpha derivatives not used as generation inputs",
                         "Godot .import and .godot cache", "unrelated source/game files and runtime integration changes owned by another task"],
            "baseline_read_only_dependencies_not_new_deliverables": [{"path": "Project/" + rel, "sha256": sha(P / rel)} for rel in dependency_paths],
            "archive_note": "Copy the exact listed files plus the two manifest files. Baseline dependencies must remain available from the existing project; do not add unrelated game/reference directories."}
(HERE / "archive-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
(HERE / "ARCHIVE_FILES.txt").write_text("\n".join(e["path"] for e in entries) + "\n" + "\n".join(self_files) + "\n")
print(json.dumps({"payload_files": len(entries), "manifest_files": len(self_files), "payload_bytes": manifest["payload_bytes"],
                  "production_owners": len(registration["owners"]), "temporary_diagnostics_included": False}))
