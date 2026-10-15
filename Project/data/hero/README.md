# R1 original hero movement

Run from any working directory:

`python Project/tools/hero/extract_movement.py`

Requires Python 3 + Pillow. Reads only the repository's original `Data/Hero/2.lpRes` and `Data/Hero/Head/0.lpRes`; uses shared `tools/lp_original.py`. Generates two 2048×1024 atlases with 128 full-size untrimmed source images each. All 256 atlas rectangles are decoded back and checked against source RGBA SHA-256; source files are verified unchanged.

`movement.json` is the renderer interface. Read `layers.body/head.atlas`, then `frames[str(source_id)].rect` and `.offset`. Draw body first, head second, at the SAME actor draw origin plus the respective native offset. Disable automatic texture centering. The native origin is not a per-frame measured boot contact and must not be recentered from a bounding box.

Frame 0 is metadata, not an idle phase. Direction order is N, NE, E, SE, S, SW, W, NW. Index = action base + direction × phase count + zero-based phase. Idle base1/count4, walk33/count6, run81/count6. Reference clip cadences 12/7/5 actor ticks are included; this extractor does not independently prove action transition/clock rules or movement speed.

Only exact pure-black BMP pixels become transparent. Every other color is preserved, including RGB(16,8,8) native checker shadow and any same-colored body/head pixels. The native body already includes its shadow; do not add a second one. This is original art, not recovered sci-fi art.

Review JPEGs and extraction-validation.json are under ignored diagnostics/hero/. Review JPEGs are offline alpha-composited references, not runtime assets. Their shared draw origin (16,64) is only a page-layout translation; it is not a new game anchor. All full source rectangles fit these preview tiles without clipping. Runtime must use native offset fields, not copy the preview translation.
