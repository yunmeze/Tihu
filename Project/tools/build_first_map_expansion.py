#!/usr/bin/env python3
"""Rebuild the bounded first-map east ground and complete plant reuse candidates.

No diagnostic files, Godot import cache, network, or original art writes are used.
--check rebuilds all three outputs in memory and compares their exact bytes.
--output-dir permits an isolated reproduction outside the source tree.
"""
from __future__ import annotations

import argparse
import hashlib
from io import BytesIO
import json
from pathlib import Path

import numpy as np
from PIL import Image

PROJECT = Path(__file__).resolve().parents[1]
OUTPUT = Path('assets/earth/first_map_review')
RECIPE = 'tools/earth/first_map_expansion_recipe.json'
RECIPE_SHA256 = 'c412d969ef5ce25569d973e37a4245703f40ac1b75a08d148c8afc4e96c1cfcc'
MAP = 'data/maps/A13.json'
MANIFEST = 'assets/original/manifest.json'
RAW = 'art_source/earth_coherent_grass_research_v1/raw.png'
PALETTE = 'art_source/earth_coherent_grass_research_v1/PALETTE_TRANSFORM.json'
TILE = str(OUTPUT / 'east_ground_period384.png')


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def resource(path: str) -> str:
    return 'res://' + path


def payload(data: object) -> bytes:
    return (json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()


def build(project: Path = PROJECT) -> dict[str, bytes]:
    recipe_bytes = (project / RECIPE).read_bytes()
    require(digest(recipe_bytes) == RECIPE_SHA256, 'Frozen expansion recipe changed')
    recipe = json.loads(recipe_bytes)
    inputs = {}
    for path, expected in recipe['input_sha256'].items():
        data = (project / path).read_bytes()
        require(digest(data) == expected, f'Input changed: {path}')
        inputs[path] = data
    source = json.loads(inputs[MAP])
    packs = json.loads(inputs[MANIFEST])['packs']
    require((source['id'], source['width'], source['height'], len(source['cells'])) ==
            ('A13', 100, 100, 10000), 'Source map shape changed')
    require(source['cellOrder'] == 'x-major' and source['tile_size'] == [48, 32],
            'Source coordinate convention changed')

    def pin(path: str, role: str, data: bytes | None = None) -> dict:
        data = (project / path).read_bytes() if data is None else data
        record = {'path': resource(path), 'sha256': digest(data), 'bytes': len(data),
                  'type': Path(path).suffix[1:], 'role': role}
        if record['type'] == 'png':
            with Image.open(BytesIO(data)) as image:
                require(image.format == 'PNG', f'Expected PNG: {path}')
                record.update(width=image.width, height=image.height)
        return record

    shared = [pin(MAP, 'source-map'), pin(MANIFEST, 'source-atlas-manifest')]
    provenance_recipe = pin(RECIPE, 'provenance-only-not-runtime')
    pages: dict[str, Image.Image] = {}

    def source_frame(pack_name: str, number: int) -> tuple[dict, dict]:
        pack = packs[pack_name]
        frame = pack['frames'][str(number)]
        page = pack['pages'][frame['page']]
        path = page['file'].removeprefix('res://')
        atlas_pin = pin(path, 'source-atlas')
        require(atlas_pin['sha256'] == page['sha256'], f'Source atlas changed: {path}')
        if path not in pages:
            pages[path] = Image.open(project / path).convert('RGBA')
        x, y, width, height = frame['rect']
        rgba = pages[path].crop((x, y, x + width, y + height))
        original = Image.new('RGBA', tuple(frame['original']))
        original.paste(rgba, tuple(frame['crop']))
        require(digest(original.tobytes()) == frame['rgba_sha256'],
                f'Source frame pixels changed: {pack_name}:{number}')
        return ({**{k: frame[k] for k in ['original', 'crop', 'offset', 'page', 'rect']},
                 'atlas': page['file'], 'rgba_sha256': digest(rgba.tobytes())}, atlas_pin)

    # Same frozen material recipe as the canonical 121-owner field. The small
    # 768-square PNG is stored; the 3x3 interpolation neighborhood is runtime-only.
    with Image.open(BytesIO(inputs[RAW])) as raw:
        require(raw.size == (1254, 1254), 'Material raw size changed')
        a = np.array(raw.convert('RGB').resize((1024, 1024), Image.Resampling.LANCZOS),
                     dtype=np.float64) / 255
    calibration = json.loads(inputs[PALETTE])
    transformed = a * np.array(calibration['gain_rgb']) + np.array(calibration['bias_rgb'])
    require(bool(((transformed >= 0) & (transformed <= 1)).all()), 'Unexpected palette clipping')
    corrected = Image.fromarray(np.floor(255 * transformed + .5).astype('uint8'))
    tile = corrected.resize((768, 768), Image.Resampling.LANCZOS)
    buffer = BytesIO()
    tile.save(buffer, format='PNG')
    tile_bytes = buffer.getvalue()
    require(digest(tile_bytes) == recipe['ground']['tile_sha256'], 'Canonical tile bytes differ')
    tile_pin = pin(TILE, 'texture', tile_bytes)

    floor_stream = []
    floor_positions = {}
    for order, cell in enumerate(source['cells']):
        if cell[0] == 0:
            continue
        x, y = divmod(order, 100)
        floor_positions[order] = len(floor_stream)
        floor_stream.append({'pack': 'Map/Res/FloorBig' if cell[0] < 0 else 'Map/Res/FloorSmall',
                             'index': abs(cell[0]), 'origin': [x * 48, y * 32]})
    require(len(floor_stream) == 2553, 'Original floor stream changed')
    ground_owners = []
    ground_dependencies = {p['path']: p for p in shared + [tile_pin]}
    orders = recipe['ground']['orders']
    require(len(orders) == len(set(orders)) == 57 and orders == sorted(orders), 'Invalid 57-owner scope')
    for order in orders:
        x, y = divmod(order, 100)
        cell = source['cells'][order]
        require(cell[0] in recipe['ground']['signed_ids'], f'Non-pure floor: {order}')
        frame, atlas_pin = source_frame('Map/Res/FloorBig', -cell[0])
        require(frame['rgba_sha256'] == recipe['ground']['source_rgba_sha256'], 'Non-identical grass source')
        require(frame['crop'] == [0, 0] and frame['original'] == frame['rect'][2:] == [96, 64],
                'Ground geometry changed')
        ground_dependencies[atlas_pin['path']] = atlas_pin
        origin = [x * 48, y * 32]
        ground_owners.append({'key': f'Map/Res/FloorBig:{-cell[0]}@{x},{y}',
                              'pack': 'Map/Res/FloorBig', 'index': -cell[0], 'frame_index': -cell[0],
                              'cell': [x, y], 'source_cell': cell, 'flag': cell[1], 'layer': 0,
                              'sort_y': y, 'stable_source_order': order,
                              'floor_stream_index': floor_positions[order], 'world_origin': origin,
                              'source_frame': frame,
                              'shared_region_px': [768 + 2 * origin[0] % 768,
                                                   768 + 2 * origin[1] % 768, 192, 128]})
    ground = {'schema': 'earth-first-map-east-ground-v1', 'status': recipe['scope'],
              'source_map': shared[0], 'source_manifest': shared[1],
              'group': {'owner_count': 57, 'density': 2, 'period_world': 384,
                        'phase_world': [0, 0], 'tile': tile_pin, 'runtime_image_size': [2304, 2304],
                        'sampling': 'Shared 3x3 tile image made in memory. LINEAR, repeat disabled, clip_uv=false; world phase unchanged.',
                        'floor_stream_count': len(floor_stream), 'owners': ground_owners,
                        'source_dependencies': sorted(ground_dependencies.values(), key=lambda p: p['path'])},
              'runtime_files': sorted(ground_dependencies.values(), key=lambda p: p['path']),
              'provenance': [provenance_recipe, pin(RAW, 'provenance-only-not-runtime'),
                             pin(PALETTE, 'provenance-only-not-runtime')]}

    plant_groups = {}
    plant_runtime = {p['path']: p for p in shared}
    plant_provenance = {p['path']: p for p in [provenance_recipe]}
    seen_orders = set()
    for specification in recipe['plants']:
        template_path = specification['template_registration']
        template = json.loads(inputs[template_path])
        plant_provenance[resource(template_path)] = pin(template_path, 'provenance-only-not-runtime')
        raw_path = template['raw_texture'].removeprefix('res://')
        raw_pin = pin(raw_path, 'provenance-only-not-runtime')
        require(raw_pin['sha256'] == template['raw_sha256'], f'Plant mother changed: {raw_path}')
        plant_provenance[raw_pin['path']] = raw_pin
        dx, dy = [specification['target_root'][i] - specification['baseline_root'][i] for i in range(2)]
        owners = []
        dependencies = {p['path']: p for p in shared}
        for baseline in template['owners']:
            x, y = baseline['cell'][0] + dx, baseline['cell'][1] + dy
            require(0 <= x < 100 and 0 <= y < 100, 'Plant target outside map')
            order = x * 100 + y
            require(order not in seen_orders, 'Overlapping plant instances')
            seen_orders.add(order)
            cell = source['cells'][order]
            number = baseline['frame_index']
            require(cell[2:] == [2, number], 'Incomplete translated plant family')
            layer = 0 if cell[1] in [1, -2] else 2 if cell[1] == 2 else 1
            require(layer == baseline['layer'], 'Plant layer differs from complete-family template')
            frame, atlas_pin = source_frame(baseline['pack'], number)
            texture_path = baseline['texture'].removeprefix('res://')
            texture_pin = pin(texture_path, 'texture')
            require(texture_pin['sha256'] == baseline['texture_sha256'], f'Plant owner texture changed: {texture_path}')
            require([texture_pin['width'], texture_pin['height']] == baseline['texture_size'], 'Plant texture size changed')
            dependencies[atlas_pin['path']] = atlas_pin
            dependencies[texture_pin['path']] = texture_pin
            owners.append({'key': f'{baseline["pack"]}:{number}@{x},{y}', 'pack': baseline['pack'],
                           'index': number, 'frame_index': number, 'cell': [x, y], 'source_cell': cell,
                           'flag': cell[1], 'layer': layer, 'sort_y': y, 'stable_source_order': order,
                           'source_frame': frame, 'texture': resource(texture_path),
                           'texture_sha256': texture_pin['sha256'], 'texture_size': baseline['texture_size'],
                           'world_top_left': [baseline['world_top_left'][0] + dx * 48,
                                              baseline['world_top_left'][1] + dy * 32],
                           'scale': baseline['scale'], 'empty': baseline['empty']})
        require(len(owners) == specification['owner_count'], 'Plant instance owner count changed')
        plant_groups[specification['id']] = {'family': specification['family'], 'owner_count': len(owners),
                                           'new_shadow': False, 'target_root': specification['target_root'],
                                           'owners': owners, 'source_dependencies': sorted(dependencies.values(), key=lambda p: p['path'])}
        plant_runtime.update(dependencies)
    require(len(plant_groups) == 24 and len(seen_orders) == 81, 'Complete plant reuse scope changed')
    require(sum(p['role'] == 'texture' for p in plant_runtime.values()) == 21, 'Unexpected texture duplication')
    plants = {'schema': 'earth-first-map-plant-reuse-v1', 'status': recipe['scope'],
              'source_map': shared[0], 'source_manifest': shared[1], 'groups': plant_groups,
              'group_count': 24, 'owner_count': 81, 'new_shadow': False,
              'runtime_files': sorted(plant_runtime.values(), key=lambda p: p['path']),
              'provenance': sorted(plant_provenance.values(), key=lambda p: p['path'])}
    return {'east_ground_registration.json': payload(ground),
            'plant_reuse_registration.json': payload(plants), 'east_ground_period384.png': tile_bytes}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=PROJECT)
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    directory = args.output_dir or args.project / OUTPUT
    outputs = build(args.project)
    for name, data in outputs.items():
        path = directory / name
        if args.check:
            require(path.is_file() and path.read_bytes() == data, f'Rebuild differs: {path}')
        else:
            directory.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        print(f'{name}: sha256={digest(data)} bytes={len(data)}')
