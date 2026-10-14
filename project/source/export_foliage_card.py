"""Export only the existing Blender-authored UV card; never generate geometry."""
import bpy
import hashlib
from pathlib import Path
import sys

source = Path(bpy.data.filepath)
if not source.is_file():
    raise RuntimeError('Open the saved editable source first.')
before = hashlib.sha256(source.read_bytes()).hexdigest()
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
if '--output' not in args:
    raise RuntimeError('Pass --output with a separate GLB path.')
output = Path(args[args.index('--output') + 1]).resolve()
obj = bpy.data.objects.get('FoliageCardTemplate')
if obj is None or obj.type != 'MESH' or not obj.data.uv_layers:
    raise RuntimeError('The authored FoliageCardTemplate mesh and UV map are required.')
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.ops.export_scene.gltf(filepath=str(output), export_format='GLB', use_selection=True,
                          export_apply=True, export_yup=True, export_materials='NONE', export_cameras=False,
                          export_lights=False, export_animations=False)
if hashlib.sha256(source.read_bytes()).hexdigest() != before:
    raise RuntimeError('The export unexpectedly changed the editable source file.')
print(f'Exported authored foliage card: {output}')
