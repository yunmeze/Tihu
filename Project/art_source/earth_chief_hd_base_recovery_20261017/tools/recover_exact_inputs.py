#!/usr/bin/env python3
"""Recover the two exact historical generation inputs, read-only against repo.

No Godot, game EXE, image generation, runtime asset writes, or Git writes.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
from PIL import Image


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    repo, out = args.repo.resolve(), args.out.resolve()
    if out == repo or repo in out.parents:
        raise ValueError("Output must be outside the read-only source repository")
    pins_path = Path(__file__).resolve().parents[1] / "SOURCE_INPUT_PINS.json"
    pins = json.loads(pins_path.read_text())
    for pin in pins["repository_dependencies"]:
        if sha(repo / pin["path"]) != pin["sha256"]:
            raise ValueError("Source pin mismatch: " + pin["path"])
    sys.path.insert(0, str(repo / "Project/tools"))
    from lp_original import read_pack, decode_frame
    data, records, animated, key = read_pack(repo / "原版游戏/Data/Npc.lpRes")
    original, metadata = decode_frame(data, records[125], "Npc", animated)
    manifest = json.loads((repo / "Project/assets/original/maps/A00/manifest.json").read_text())
    assert metadata["rgba_sha256"] == manifest["packs"]["Npc"]["frames"]["125"]["rgba_sha256"]
    hero_manifest = json.loads((repo / "Project/assets/earth/hero/s_idle_v1/manifest.json").read_text())
    assert hero_manifest["source_ids"][0] == 17
    assert hero_manifest["records"][0]["region_px"] == [0,0,512,512]
    hero = Image.open(repo / "Project/assets/earth/hero/s_idle_v1/body.png").convert("RGBA").crop((0,0,512,512))
    images = [original, hero]
    for entry, image in zip(pins["recovered_inputs"], images):
        target = out / entry["package_path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        image.save(target)
        file_exact = sha(target) == entry["expected_historical_file_sha256"]
        rgba_exact = hashlib.sha256(image.tobytes()).hexdigest() == entry["rgba_sha256"]
        print(json.dumps({"file": str(target), "file_sha256":sha(target),
                          "historical_file_bytes_exact":file_exact,"rgba_exact":rgba_exact}))
        if not file_exact or not rgba_exact:
            raise ValueError("Not exact recovery; file encoding and RGBA identity are separate checks")
    for pin in pins["repository_dependencies"]:
        assert sha(repo / pin["path"]) == pin["sha256"]


if __name__ == "__main__":
    main()
