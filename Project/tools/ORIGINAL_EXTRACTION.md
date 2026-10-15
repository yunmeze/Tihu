# Original LP resource extraction, recovery R1

Run from the repository root with Python 3 and Pillow installed:

```sh
python Project/tools/extract_a13_original.py
```

Inputs are the checked-in `原版游戏/Data/Map/A13.lpMap` and referenced `原版游戏/Data/**/*.lpRes`. They are read-only. The original EXE and map/NPC gameplay scripts are never executed by extraction. `lp_original.py` contains verbatim Reader/container/image-signature definitions from `参考项目/tools/extract-lp.py`, with that file's SHA256 recorded. The image transparency normalization also follows `参考项目/tools/native-color-key.py`: exact RGB(0,0,0) becomes transparent for animated packs and non-floor map objects, including PNG. It does not remove nonblack checker shadow colors. Original RGB is preserved.

## Production interfaces

- `data/maps/A13.json`: original x-major cells. Lookup `cells[x * height + y]`, with four signed values `[floor, flag, kind, index]`. Exact NPCs, portals, spawn names, loadScript and unparsed tail remain as data. Source byte offsets and hash are included.
- `assets/original/manifest.json`: `packs[pack_name]`, each with `pages` and a `frames` dictionary keyed by decimal source-index string. A page has `file` (res:// path), `size`, and SHA256. A frame has `page`, `rect=[x,y,w,h]`, native `original=[w,h]`, `offset=[x,y]`, and `crop=[x,y]`. All atlas regions have a transparent one-pixel packing gutter.
- The extraction owns map scenery/NPC atlas paths. Hero extraction owns the separate `assets/original/hero` subtree and its own manifest. Do not overwrite one with the other.

## Drawing and flags

These rules are sourced from reference `src/map-effects.js`, `src/map-flags.js`, `src/batch.js`, and `src/game.js`; they are reference-adaptation evidence, not a claim that this R1 has executed the original EXE.

- Ground origin is `(48*x,32*y)`. Negative floor selects FloorBig; positive selects FloorSmall; absolute value is source frame index; zero means no ground sprite. Ignore native frame offset, add crop offset.
- Object kinds1–5 map to Debris, Plant, Wall, Building, Dynamic. Draw origin is `(48*x,32*y + 32 - original_height)`, ignoring pack offset and adding crop offset. Dynamic uses five frames from base index, eight source ticks per frame.
- Kind8 uses Data4 55–59, top−52, eight-tick ping-pong55,56,57,58,59,59,58,57,56,55. Kind6 is a spawn; kind7 refers to the NPC list, not a second scenery sprite. A13 currently has no dynamic or kind8 object.
- NPC draw origin is cell world position plus original frame offset plus crop. Four frames from `1 + appearance*12 + direction*4`, seventeen source ticks each; source clock50Hz. Preserved scripts can hide NPCs later; R1 does not execute them.
- Flag1 or−2 draws object layer0; flag2 layer2; otherwise layer1. Sort by layer, then original rowy, keeping stable insertion order. Render all floors first. Collision is separate: player excludes flags−2,−1,−3; monster excludes−2,−1,−4. Portal values10+ are not automatically blocked.

## Validation and boundaries

`diagnostics/maps/` receives extraction audit, individual reference-frame comparison and derived placement proof. These are ignored diagnostics, not runtime dependencies. The final R1 proves all384 requested source frames (seven atlas pages, including forty unique NPC phases) match the checked-in reference atlas RGBA and original/crop/offset metadata. All map cells, NPCs, portals, scripts and declared source hash match reference A13 JSON. Sixty-eight trailing source bytes remain explicitly unmapped. Floor/object derivation gives2553 ground placements,1145 scenery owners (Plant621,Wall379,Building126,Debris19), eleven NPC records, zero spawns.

Reference normalization applies the final black key after its initial crop. `reference_extraction_bounds` preserves that pre-normalization crop so the reproduced atlas metadata remains exact. It is not a physical footprint or collision box.

## Incremental maps after the frozen A13 stage

```sh
python Project/tools/extract_original_map.py A00
python Project/tools/verify_original_assets.py --manifest assets/original/maps/A00/manifest.json
```

Each new map has a `texture_manifest` res:// URI; the A13 default remains `assets/original/manifest.json`. The new manifest uses the same packs/pages/frames schema, retaining inherited atlas URIs and adding only missing frames under `assets/original/maps/<map>/sprites/`. Existing atlas files and the base manifest are hash-checked before/after extraction. Map-specific `required_frames` records new/reused indices. A later map can pass `--base assets/original/maps/A00/manifest.json` to reuse that frozen cumulative index without rewriting it.

`data/maps/<map>-entities.json` is a source text/index artifact: original portal and NPC record locations, scripts with UTF-8 hashes, spawn records and load-script location. These strings are not executed by extraction. Monster appearances and gameplay systems are not implemented or inferred by the presence of spawn records. Trailing68 source bytes remain preserved/uninterpreted. A00 contains fifteen kind8 records; its future nine-cell story gate must be scoped by original scripts rather than globally deleting all fifteen instances.
