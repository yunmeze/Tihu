"""Bake scalar vertex AO on an export-only evaluated snapshot of authored meshes.

Usage:
  blender --background /absolute/source.blend --python export_baked_ao.py -- \
      --output /absolute/candidate.glb [--samples 32] [--radius 0.15]

No primitives, subdivision, UV generation, or source saves. Must run in a
separate background Blender process. The source .blend remains authoritative.
Every exported mesh gets BakedAO (white if not selected for baking), so existing
materials can opt into COLOR.r without a missing-color ambiguity.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys
import time
import bpy


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def mesh_signature(mesh):
    h = hashlib.sha256()
    for v in mesh.vertices:
        h.update(struct.pack('<3f', *v.co))
    for p in mesh.polygons:
        h.update(struct.pack('<II', len(p.vertices), p.material_index))
        h.update(struct.pack('<' + 'I' * len(p.vertices), *p.vertices))
    return {'vertices': len(mesh.vertices), 'polygons': len(mesh.polygons),
            'geometry_sha256': h.hexdigest()}


def object_signature(obj):
    return {'name': obj.name, 'matrix_world': [v for row in obj.matrix_world for v in row],
            'materials': [m.name if m else None for m in obj.data.materials]}


def load_glb(path):
    raw = Path(path).read_bytes()
    magic, version, length = struct.unpack_from('<4sII', raw)
    assert magic == b'glTF' and version == 2 and length == len(raw)
    offset = 12
    document = None
    binary = b''
    while offset < len(raw):
        size, kind = struct.unpack_from('<II', raw, offset)
        chunk = raw[offset + 8:offset + 8 + size]
        if kind == 0x4E4F534A:
            document = json.loads(chunk)
        elif kind == 0x004E4942:
            binary = chunk
        offset += 8 + size
    return document, binary


def accessor_bytes(document, binary, index):
    a = document['accessors'][index]
    assert 'sparse' not in a
    view = document['bufferViews'][a['bufferView']]
    components = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}[a['type']]
    width = {5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4}[a['componentType']] * components
    stride = view.get('byteStride', width)
    start = view.get('byteOffset', 0) + a.get('byteOffset', 0)
    payload = b''.join(binary[start + i * stride:start + i * stride + width] for i in range(a['count']))
    return {'count': a['count'], 'type': a['type'], 'componentType': a['componentType'],
            'normalized': a.get('normalized', False), 'sha256': hashlib.sha256(payload).hexdigest()}


def glb_signature(path):
    doc, data = load_glb(path)
    meshes = []
    color_primitives = 0
    for mesh in doc.get('meshes', []):
        prims = []
        for p in mesh['primitives']:
            attrs = {k: accessor_bytes(doc, data, v) for k, v in p['attributes'].items() if not k.startswith('COLOR_')}
            color_primitives += 'COLOR_0' in p['attributes']
            prims.append({'attributes': attrs,
                          'indices': accessor_bytes(doc, data, p['indices']),
                          'material': p.get('material'), 'mode': p.get('mode', 4)})
        meshes.append({'name': mesh.get('name'), 'primitives': prims})
    return {'nodes': doc.get('nodes'), 'meshes': meshes, 'materials': doc.get('materials'),
            'scene': doc.get('scene'), 'scenes': doc.get('scenes')}, color_primitives


def restore_materials(obj, original):
    # Preserve slot positions: clearing slots resets face material indices.
    if not original:
        obj.data.materials.clear()
        return
    assert len(obj.data.materials) == len(original)
    for index, material in enumerate(original):
        obj.data.materials[index] = material


def choose_groups(objects):
    names = {o.name for o in objects}
    rider = sorted(n for n in names if n.startswith(('Pelican', 'Wing', 'Crest', 'Cheek')))
    static = [n for n in ('BicycleFrame', 'ForkL', 'ForkR', 'Seat', 'FrameSeatTube',
                          'HandleStem', 'Handlebar', 'GripL', 'GripR', 'Bell', 'CrankAxle') if n in names]
    wheels = [[prefix + end for prefix in ('Tire', 'Rim', 'Spokes', 'Hub') if prefix + end in names]
              for end in ('Front', 'Rear')]
    return [('rider', rider), ('static_bicycle', static), ('front_wheel', wheels[0]), ('rear_wheel', wheels[1])]


def main():
    if not bpy.app.background:
        raise RuntimeError('Run only in a separate background Blender process; the interactive authoring session must stay editable.')
    args_list = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    parser.add_argument('--samples', type=int, default=32)
    parser.add_argument('--ao-samples', type=int, default=16)
    parser.add_argument('--radius', type=float, default=0.15)
    parser.add_argument('--threads', type=int, default=4)
    args = parser.parse_args(args_list)
    source = Path(bpy.data.filepath).resolve()
    if not source.is_file() or source.suffix.lower() != '.blend':
        raise RuntimeError('Open the saved authored .blend file before starting this export utility.')
    output = Path(args.output).expanduser().resolve()
    if output.suffix.lower() != '.glb' or output == source:
        raise RuntimeError('Output must be a separate .glb file.')
    if args.samples < 1 or args.ao_samples < 1 or args.radius <= 0:
        raise ValueError('Samples and radius must be positive.')
    output.parent.mkdir(parents=True, exist_ok=True)
    baseline = output.with_name(output.stem + '.baseline.glb')
    report_path = output.with_suffix('.validation.json')
    source_hash = sha(source)
    source_mtime = source.stat().st_mtime_ns
    source_filepath = bpy.data.filepath
    source_objects = sorted((o for o in bpy.context.scene.objects if o.type == 'MESH'), key=lambda x: x.name)
    source_state = {o.name: object_signature(o) for o in source_objects}
    cages = {o.name: {'geometry': mesh_signature(o.data),
                     'modifiers': [(m.name, m.type) for m in o.modifiers]} for o in source_objects}
    deps = bpy.context.evaluated_depsgraph_get()
    evaluated = {o.name: mesh_signature(o.evaluated_get(deps).data) for o in source_objects}
    visibility = {o.name: (o.hide_render, o.hide_get()) for o in source_objects}
    # Freeze existing evaluated geometry only in this process; never save .blend.
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    for o in source_objects:
        o.hide_set(False)
        o.select_set(True)
    bpy.context.view_layer.objects.active = source_objects[0]
    bpy.ops.object.convert(target='MESH')
    objects = sorted((o for o in bpy.context.scene.objects if o.type == 'MESH'), key=lambda x: x.name)
    assert {o.name for o in objects} == set(source_state), 'Object names changed during evaluation.'
    for o in objects:
        assert object_signature(o) == source_state[o.name], 'Object/material/transform changed: ' + o.name
        assert mesh_signature(o.data) == evaluated[o.name], 'Evaluated topology changed: ' + o.name
    export_args = dict(export_format='GLB', export_apply=False, export_yup=True,
                       export_cameras=False, export_lights=False, export_animations=False,
                       export_all_vertex_colors=False)
    bpy.ops.export_scene.gltf(filepath=str(baseline), export_vertex_color='NONE', **export_args)
    frozen = {o.name: mesh_signature(o.data) for o in objects}
    originals = {o.name: list(o.data.materials) for o in objects}
    for o in objects:
        old = o.data.color_attributes.get('BakedAO')
        if old:
            o.data.color_attributes.remove(old)
        attr = o.data.color_attributes.new(name='BakedAO', type='FLOAT_COLOR', domain='POINT')
        for item in attr.data:
            item.color = (1.0, 1.0, 1.0, 1.0)
        o.data.color_attributes.active_color = attr
        o.data.color_attributes.render_color_index = o.data.color_attributes.find(attr.name)
        o.select_set(False)
    temporary = bpy.data.materials.new('__AO_EXPORT_ONLY__')
    temporary.use_nodes = True
    nodes = temporary.node_tree.nodes
    nodes.clear()
    ao = nodes.new('ShaderNodeAmbientOcclusion')
    ao.inputs['Distance'].default_value = args.radius
    ao.samples = args.ao_samples
    emit = nodes.new('ShaderNodeEmission')
    surface = nodes.new('ShaderNodeOutputMaterial')
    temporary.node_tree.links.new(ao.outputs['AO'], emit.inputs['Color'])
    temporary.node_tree.links.new(emit.outputs[0], surface.inputs['Surface'])
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = args.samples
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = args.threads
    groups = choose_groups(objects)
    stats = []
    start = time.monotonic()
    try:
        for group_name, members in groups:
            if not members:
                continue
            visible = set(members)
            for o in objects:
                o.hide_render = o.name not in visible
            for name in members:
                o = bpy.data.objects[name]
                # Retain original slot count and polygon indices even during baking.
                for index in range(len(o.data.materials)):
                    o.data.materials[index] = temporary
                if not o.data.materials:
                    o.data.materials.append(temporary)
                bpy.context.view_layer.objects.active = o
                o.select_set(True)
                t = time.monotonic()
                bpy.ops.object.bake(type='EMIT', target='VERTEX_COLORS', use_selected_to_active=False)
                vals = [v.color[0] for v in o.data.color_attributes['BakedAO'].data]
                item = {'name': name, 'group': group_name, 'seconds': time.monotonic() - t,
                        'samples': len(vals), 'min': min(vals), 'max': max(vals), 'mean': sum(vals) / len(vals)}
                stats.append(item)
                print('AO_BAKED', json.dumps(item), flush=True)
                o.select_set(False)
                restore_materials(o, originals[name])
    finally:
        for o in objects:
            restore_materials(o, originals[o.name])
            o.hide_render, hidden = visibility[o.name]
            o.hide_set(hidden)
    for o in objects:
        assert object_signature(o) == source_state[o.name], 'Object/material/transform changed: ' + o.name
        assert mesh_signature(o.data) == frozen[o.name], 'AO pass altered topology: ' + o.name
    bpy.ops.export_scene.gltf(filepath=str(output), export_vertex_color='ACTIVE', **export_args)
    baseline_signature, baseline_colors = glb_signature(baseline)
    candidate_signature, candidate_colors = glb_signature(output)
    assert baseline_signature == candidate_signature, 'Final GLB non-color geometry, nodes, or materials differ from baseline.'
    primitive_count = sum(len(m['primitives']) for m in candidate_signature['meshes'])
    assert candidate_colors == primitive_count, 'Some exported primitives lack COLOR_0.'
    assert bpy.data.filepath == source_filepath, 'Blender source filename changed.'
    assert sha(source) == source_hash and source.stat().st_mtime_ns == source_mtime, 'Source file changed on disk.'
    report = {'passed': True, 'source': str(source), 'source_sha256_before': source_hash,
              'source_sha256_after': sha(source), 'source_file_unchanged': True,
              'source_filename_unchanged': True, 'source_cages': cages,
              'evaluated_topology_identical': True, 'glb_non_color_data_identical': True,
              'object_material_names_and_transforms_unchanged': True,
              'mesh_count': len(objects), 'exported_primitives': primitive_count,
              'color_0_primitives': candidate_colors, 'baseline_color_primitives': baseline_colors,
              'baked_objects': len(stats), 'white_only_objects': len(objects) - len(stats),
              'settings': vars(args), 'groups': dict(groups), 'bake_stats': stats,
              'elapsed_baking_seconds': time.monotonic() - start,
              'output': str(output), 'baseline': str(baseline)}
    report_path.write_text(json.dumps(report, indent=2))
    print('AO_VALIDATED', json.dumps({k: report[k] for k in ('passed','mesh_count','exported_primitives','color_0_primitives','baked_objects','source_file_unchanged','glb_non_color_data_identical')}), flush=True)
    print('AO_REPORT', str(report_path), flush=True)


if __name__ == '__main__':
    main()
