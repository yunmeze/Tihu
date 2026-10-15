"""Deterministic source/layout preparation only. No generated art or runtime writes.

Run from any cwd: python Project/art_source/earth_ground_plate_source_v1/prepare_source.py
Requires Pillow and NumPy. Reads only extracted Project source assets; never runs EXEs.
"""
from collections import Counter, deque
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
P = HERE.parents[1]
BOUNDS = (2496, 960, 3264, 1472)  # half-open world XYXY
DENSITY = 2
SIZE = (BOUNDS[2] - BOUNDS[0], BOUNDS[3] - BOUNDS[1])
BLOCKED = {-1, -2, -3}
DIRS = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(rel):
    return json.loads((P / rel).read_text())


def write(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def intersects(r):
    x, y, w, h = r
    return x < BOUNDS[2] and y < BOUNDS[3] and x + w > BOUNDS[0] and y + h > BOUNDS[1]


def local(point):
    return (point[0] - BOUNDS[0], point[1] - BOUNDS[1])


def main():
    # Hash authoritative files before and after to prove this recipe does not edit them.
    refs = ["data/maps/A13.json", "assets/original/manifest.json", "scripts/world_view.gd",
            "scripts/core/movement.gd", "project.godot",
            "art_source/a13_main_temple_source/source-group-contract.json",
            "art_source/a13_ground_source/source-group-contract.json",
            "art_source/earth_base_style_concept_v1/concept.png",
            "art_source/a13_ground_materials_v2/semantic-mask-research.json",
            "art_source/earth_training_hall_source_v1/input-contract.json"]
    before = {r: sha(P / r) for r in refs}
    m = load(refs[0])
    packs = load(refs[1])["packs"]
    hall = load(refs[5])
    hall_interface_path = "art_source/earth_training_hall_source_v1/input-contract.json"
    hall_interface = load(hall_interface_path)
    door_observations = hall_interface["geometry"]["approximate_door_visual_evidence"]
    pages, frames, images, contributors = {}, {}, {}, []
    all_floor = Image.new("RGBA", SIZE)
    selected_floor = Image.new("RGBA", SIZE)
    owner_index = np.zeros((SIZE[1], SIZE[0]), dtype=np.uint16)
    overlap = np.zeros_like(owner_index)
    selected, passthrough = [], []
    for i, c in enumerate(m["cells"]):
        sid = c[0]
        if not sid:
            continue
        name = "Map/Res/FloorBig" if sid < 0 else "Map/Res/FloorSmall"
        pack = packs[name]
        f = pack["frames"][str(abs(sid))]
        x, y = divmod(i, m["height"])
        ax, ay, w, h = f["rect"]
        rect = [x * 48 + f["crop"][0], y * 32 + f["crop"][1], w, h]
        if not intersects(rect):
            continue
        assert rect[0] >= BOUNDS[0] and rect[1] >= BOUNDS[1]
        assert rect[0] + w <= BOUNDS[2] and rect[1] + h <= BOUNDS[3]
        page = pack["pages"][f["page"]]["file"]
        if page not in pages:
            pages[page] = Image.open(P / page[6:]).convert("RGBA")
        key = f"{name}:{abs(sid)}"
        if key not in images:
            tile = pages[page].crop((ax, ay, ax + w, ay + h))
            images[key] = tile
            frames[key] = {"signed_id": sid, "pack": name, "frame_index": abs(sid),
                           "atlas_page": page, "atlas_page_sha256": sha(P / page[6:]),
                           "atlas_rect": f["rect"], "crop": f["crop"], "original": f["original"],
                           "ignored_frame_offset": f["offset"],
                           "rgba_sha256": hashlib.sha256(tile.tobytes()).hexdigest(),
                           "alpha_sha256": hashlib.sha256(tile.getchannel("A").tobytes()).hexdigest(),
                           "alpha_extrema": list(tile.getchannel("A").getextrema())}
        tile = images[key]
        owner = {"key": f"{key}@{x},{y}", "signed_id": sid, "pack": name,
                 "frame_index": abs(sid), "cell": [x, y], "stable_source_order": i,
                 "source_cell": c, "source_map_byte_offset": m["cellByteOffsets"][i],
                 "world_rect": rect, "source_frame_key": key}
        contributors.append(owner)
        xy = local(rect)
        all_floor.alpha_composite(tile, xy)
        if sid > 0:
            passthrough.append(owner)
            continue
        assert (w, h) == (96, 64) and tile.getchannel("A").getextrema() == (255, 255)
        selected.append(owner)
        selected_floor.alpha_composite(tile, xy)
        xx, yy = xy
        overlap[yy:yy + h, xx:xx + w] += 1
        owner_index[yy:yy + h, xx:xx + w] = len(selected)
    assert len(selected) == 64 and len(passthrough) == 0
    assert int(overlap.max()) == 1
    coverage = np.asarray(selected_floor.getchannel("A"))
    assert int((coverage == 255).sum()) == 393216
    assert int((coverage == 0).sum()) == 0
    all_floor.save(HERE / "source-floor-native.png")
    selected_floor.save(HERE / "selected-floor-native.png")
    Image.fromarray(owner_index).save(HERE / "source-owner-index-native.png")
    alpha = selected_floor.getchannel("A")
    alpha.save(HERE / "source-alpha-native.png")
    alpha.resize((SIZE[0] * 2, SIZE[1] * 2), Image.Resampling.NEAREST).save(HERE / "source-alpha-2x.png")

    # Source-only road interpretation. The historical generated-stone masks/RGB are NOT inputs.
    # These manually read source curb points have +/-3 native-pixel uncertainty.
    context_origin = [2688, 1152]
    curb_local = [(-1, 225), (192, 97), (288, 99), (332, 126), (332, 195), (244, 256)]
    assert [list(q) for q in curb_local] == load(refs[8])["source_curb_centerline"]
    road = Image.new("L", (480, 256))
    ImageDraw.Draw(road).polygon(curb_local + [(0, 256)], fill=255)
    uncertain = Image.new("L", (480, 256))
    ImageDraw.Draw(uncertain).line(curb_local, fill=255, width=7, joint="curve")
    examples = {-577: [56, 40], -608: [58, 40], -579: [60, 38], -581: [60, 42],
                -580: [62, 38], -588: [62, 40], -604: [62, 42]}
    semantic = np.zeros((SIZE[1], SIZE[0]), dtype=np.uint8)
    for o in selected:
        sid = o["signed_id"]
        x, y, w, h = o["world_rect"]
        codes = np.full((h, w), 32, dtype=np.uint8)
        if sid in examples:
            cx, cy = examples[sid]
            ox, oy = cx * 48 - context_origin[0], cy * 32 - context_origin[1]
            box = (ox, oy, ox + w, oy + h)
            codes[np.asarray(road.crop(box)) > 0] = 128
            codes[np.asarray(uncertain.crop(box)) > 0] = 224
        elif sid in [-587, -595, -594, -586]:
            codes[:] = 128
        else:
            assert sid in [-406, -399, -398, -407], sid
        xx, yy = local((x, y))
        semantic[yy:yy + h, xx:xx + w] = codes
    Image.fromarray(semantic).save(HERE / "source-material-zones-native.png")
    for name, value in [("grass", 32), ("paving", 128), ("curb-review-band", 224)]:
        Image.fromarray(np.where(semantic == value, 255, 0).astype(np.uint8)).save(HERE / f"{name}-guide-native.png")
    # Coverage is an allowed flat receiver envelope, never a ready-to-use cast shape.
    alpha.save(HERE / "flat-receiver-envelope-native.png")

    def can_enter(c):
        x, y = c
        return 0 <= x < m["width"] and 0 <= y < m["height"] and m["cells"][x * m["height"] + y][1] not in BLOCKED

    def route(target):
        start = (61, 39)
        prev = {start: None}
        todo = deque([start])
        while todo and target not in prev:
            a = todo.popleft()
            for dx, dy in DIRS:
                b = (a[0] + dx, a[1] + dy)
                if b in prev or not can_enter(b):
                    continue
                if dx and dy and (not can_enter((a[0] + dx, a[1])) or not can_enter((a[0], a[1] + dy))):
                    continue
                prev[b] = a
                todo.append(b)
        assert target in prev, target
        result = []
        p = target
        while p is not None:
            result.append(list(p))
            p = prev[p]
        return result[::-1]

    routes = []
    for o in hall["owners_in_draw_order"]:
        if o["layer"] == 0:
            cells = route(tuple(o["cell"]))
            routes.append({"target_source_owner": o["key"], "target_cell": o["cell"], "source_flag": o["flag"],
                           "cells": cells, "world_actor_origins": [[c[0] * 48, c[1] * 32] for c in cells]})
    cell_rows = []
    for x in range(BOUNDS[0] // 48, BOUNDS[2] // 48):
        for y in range(BOUNDS[1] // 32, BOUNDS[3] // 32):
            i = x * m["height"] + y
            cell_rows.append({"cell": [x, y], "source_order": i, "source_cell": m["cells"][i],
                              "can_enter_by_static_flags": can_enter((x, y))})
    base = Image.new("RGBA", SIZE, (52, 57, 58, 255))
    base.alpha_composite(all_floor)
    owner_board = base.convert("RGB")
    dr = ImageDraw.Draw(owner_board)
    for o in selected:
        x, y, w, h = o["world_rect"]
        xx, yy = local((x, y))
        dr.rectangle((xx, yy, xx + w - 1, yy + h - 1), outline=(150, 65, 65))
        dr.text((xx + 2, yy + 2), f'{o["signed_id"]}@{o["cell"][0]},{o["cell"][1]}', fill="white")
    owner_board.save(HERE / "source-owners-board.png")
    palette = np.zeros((256, 3), dtype=np.uint8)
    palette[32], palette[128], palette[224] = [67, 117, 72], [170, 170, 166], [220, 85, 186]
    Image.fromarray(palette[semantic]).save(HERE / "material-layout-board.png")
    # Composite original building only to inspect spatial interfaces. Never an art/render candidate.
    for o in hall["owners_in_draw_order"]:
        page = o["atlas_page"]
        if page not in pages:
            pages[page] = Image.open(P / page[6:]).convert("RGBA")
        x, y, w, h = o["atlas_rect"]
        base.alpha_composite(pages[page].crop((x, y, x + w, y + h)), local(o["world_rect"]))
    overlay = Image.new("RGBA", SIZE)
    d = ImageDraw.Draw(overlay)
    for row in cell_rows:
        if not row["can_enter_by_static_flags"]:
            x, y = local((row["cell"][0] * 48, row["cell"][1] * 32))
            d.rectangle((x, y, x + 47, y + 31), fill=(230, 30, 30, 48))
    base.alpha_composite(overlay)
    d = ImageDraw.Draw(base)
    for r in routes:
        if not (BOUNDS[0] <= r["target_cell"][0] * 48 < BOUNDS[2] and BOUNDS[1] <= r["target_cell"][1] * 32 < BOUNDS[3]):
            continue
        d.line([local(q) for q in r["world_actor_origins"]], fill=(30, 245, 240), width=1)
    for a in hall["manual_visible_landmarks"][:5]:
        x, y = local(a["world_xy"])
        d.ellipse((x - 4, y - 4, x + 4, y + 4), outline="yellow", width=2)
        d.text((x + 6, y - 7), a["id"].split("_")[0], fill="yellow")
    for a in door_observations:
        x, y = local(a["world_xy"])
        d.ellipse((x - 4, y - 4, x + 4, y + 4), outline="cyan", width=2)
        d.text((x + 6, y - 7), a["id"].split("_")[0], fill="cyan")
    x, y = local((61 * 48, 39 * 32))
    d.ellipse((x - 5, y - 5, x + 5, y + 5), outline="magenta", width=2)
    d.text((x + 7, y + 6), "ACTOR ORIGIN 61,39", fill="magenta")
    d.text((8, 8), "ORIGINAL SOURCE + STATIC FLAG/ROUTE DIAGNOSTIC; NOT NEW ART OR ENGINE CAPTURE", fill="white")
    base.convert("RGB").save(HERE / "source-layout-routes-board.png")

    seams = []
    for a in selected:
        ax, ay, aw, ah = a["world_rect"]
        for b in selected:
            bx, by, bw, bh = b["world_rect"]
            if ax + aw == bx and max(ay, by) < min(ay + ah, by + bh):
                seams.append({"axis": "vertical", "line": [bx, max(ay, by), bx, min(ay + ah, by + bh)], "owners": [a["key"], b["key"]]})
            if ay + ah == by and max(ax, bx) < min(ax + aw, bx + bw):
                seams.append({"axis": "horizontal", "line": [max(ax, bx), by, min(ax + aw, bx + bw), by], "owners": [a["key"], b["key"]]})
    # A per-owner split/reassemble of original bytes proves this scope, not a generated asset.
    rebuilt = Image.new("RGBA", SIZE)
    for o in selected:
        x, y, w, h = o["world_rect"]
        xx, yy = local((x, y))
        rebuilt.alpha_composite(selected_floor.crop((xx, yy, xx + w, yy + h)), (xx, yy))
    assert rebuilt.tobytes() == selected_floor.tobytes()
    after = {r: sha(P / r) for r in refs}
    assert after == before
    contract = {
        "schema": "earth-ground-plate-source-layout-v1", "status": "source/layout preparation only; no generated art, runtime installation or native validation",
        "source_hashes": before, "world_bounds_xyxy_half_open": list(BOUNDS), "logical_size": list(SIZE),
        "density_texels_per_logical": DENSITY, "target_plate_size": [SIZE[0] * 2, SIZE[1] * 2],
        "coordinate_contract": {"cell_size": [48, 32], "map_order": "x*height+y", "floor_origin": "cell*[48,32]+crop; ignore frame.offset; no object top adjustment",
                                "orientation": "screen/world +X right, +Y down; source curb rays approx (+3,-2) and (+3,+2); not new isometric cell transform",
                                "raw_texel_to_world": "world = [2496,960] + (texel_index+0.5)/2", "filter": "world-locked one shared raw canvas; no modulo, repeat, mirror or per-owner rotation"},
        "scope": {"all_floor_contributors": len(contributors), "selected_floor_owners": len(selected), "selected_signed_ids": sorted({o["signed_id"] for o in selected}),
                  "passthrough_floor_owners": len(passthrough), "excluded_top_right_rect": None,
                  "plate_alpha_255_pixels_native": int((coverage == 255).sum()), "plate_alpha_0_pixels_native": int((coverage == 0).sum()),
                  "max_coverage_multiplicity": int(overlap.max()), "alpha_rule": "Selected source owners are individually fully opaque. Exact source coverage union fills this bounded rectangle. Preserve every owner's source alpha, nearest-expanded 2x; never infer alpha from material masks. This all-opaque result is not a general rule for other source areas."},
        "selected_owners_in_source_draw_order": selected, "passthrough_owners_in_source_draw_order": passthrough,
        "source_frames": list(frames.values()), "touching_edges": seams,
        "road_geometry": {"provenance": "Original source floor pixels and prior source-only manual read in a13_ground_materials_v2/semantic-mask-research.json; no generated RGB/stone mask reused",
                          "manual_curb_centerline_world": [[x + context_origin[0], y + context_origin[1]] for x, y in curb_local],
                          "read_uncertainty_native_px": 3, "guide_codes": {"0": "outside selected floor", "32": "source grass interior", "128": "source tan road interior; modern paving material allowed", "224": "source curb center +/-3px review band; not final generated alpha or surveyed geometry"},
                          "same_frame_geometry_examples": {str(k): v for k, v in examples.items()},
                          "road_head_right_edge_world_x_approx": 3020, "left_stair_ground_edge_world_x_approx": 3206,
                          "no_new_connection": "Do not pave the approximately 186-logical-pixel grass/apron gap to imitate the concept; floor road boundary and building support remain separate."},
        "building_read_only_interface": {"source_contract": refs[5], "source_bounds": hall["world_bounds_xyxy"],
                                         "landmarks": hall["manual_visible_landmarks"][:5], "support_owner_keys": [o["key"] for o in hall["owners_in_draw_order"] if o["layer"] == 0],
                                         "door_threshold_authority": hall_interface_path,
                                         "door_threshold_observations": door_observations,
                                         "door_observation_not_portal": True,
                                         "ground_does_not_own": ["stairs", "platform", "building apron geometry", "roof", "rail", "wall", "pillar", "foreground vegetation"]},
        "static_receiver_contract": {"envelope": "flat-receiver-envelope-native.png", "meaning": "coverage eligibility only, not a shadow image or elevated receiver", "draw_order": "floor -> one static ground cast -> original support/object/actor streams", "light": "shared Earth Art Bible: upper-left light, lower-right cast; exact vector pending motherplate", "cast_generated": False, "elevated_receiver_verified": False, "actor_receives_environment_shadow_verified": False},
        "static_route_evidence": {"start_cell": [61, 39], "blocked_flags": sorted(BLOCKED), "diagonal_rule": "only if both orthogonal neighbor cells are open", "method": "offline BFS reachability using movement.gd graph rules, not Godot AStar tie-break or native walk proof", "npc_occupation": "No extra occupation injected, matching world_view.setup(movement) source preview; story state may add constraints", "support_routes": routes},
        "source_cells_in_bounds": cell_rows, "nearby_original_npcs": hall["nearby_original_npcs"],
        "portals_in_rect": [p for p in m["portals"] if BOUNDS[0] <= p["x"] * 48 < BOUNDS[2] and BOUNDS[1] <= p["y"] * 32 < BOUNDS[3]],
        "portal_policy": "All source portals preserved. None falls in this small rectangle; no new main-building portal",
        "qa": {"authoritative_source_hashes_unchanged": True, "source_split_roundtrip_byte_exact": True, "source_alpha_2x_method": "nearest exact duplication", "static_support_targets_reachable_full_hall": len(routes), "static_support_targets_in_plate": sum(BOUNDS[0] <= r["target_cell"][0]*48 < BOUNDS[2] and BOUNDS[1] <= r["target_cell"][1]*32 < BOUNDS[3] for r in routes), "generated_asset_count": 0, "runtime_files_written": 0, "native_checks_run": False}}
    write("source-layout-contract.json", contract)
    output_files = [p for p in sorted(HERE.iterdir()) if p.suffix in [".png", ".json"] and p.name != "preparation-report.json"]
    report = {"status": contract["status"], "scope": contract["scope"], "qa": contract["qa"],
              "outputs": [{"path": p.name, "bytes": p.stat().st_size, "sha256": sha(p)} for p in output_files]}
    write("preparation-report.json", report)
    print(json.dumps({"selected": len(selected), "passthrough": len(passthrough), "bounds": BOUNDS,
                      "alpha_pixels": contract["scope"]["plate_alpha_255_pixels_native"], "seams": len(seams), "qa": contract["qa"]}))


if __name__ == "__main__":
    main()
