"""Palette, authoring-view and glTF export utility. No mesh generation or shape edits."""
import bpy
import sys
from pathlib import Path
from mathutils import Vector
if Path(bpy.data.filepath).name != 'pelican_coast.blend':
 raise RuntimeError('Open source/pelican_coast.blend before exporting.')
root=Path(bpy.data.filepath).resolve().parent.parent
export_target=root/'assets/coastal_ride.glb'
if '--' in sys.argv:
 args=sys.argv[sys.argv.index('--')+1:]
 if '--output' in args: export_target=Path(args[args.index('--output')+1]).resolve()
def color(h):
 v=[int(h[i:i+2],16)/255 for i in (0,2,4)]
 return [x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in v]+[1]
colors={'FeatherIvory':'fff1d8','BillPeach':'ffa55f','BillMark':'a56b4f','BillLipWarm':'c88958','PouchGold':'f8c568','EyeInk':'21353d','IrisAmber':'d99b48','CatchlightCream':'fff7df','CheekCoral':'f59b85','MintPaint':'7dbba1','CreamRubber':'ebd6ad','WarmRim':'d6a869','SatinMetal':'aabcc0','CableRubber':'415959','SaddleLeather':'aa764f','LeafSage':'427e66','LeafLight':'aec57b','GrassGreen':'83a572','SandCream':'dec69e','RockPeach':'c6a48e','RockCool':'92a6a4','RockLedge':'cdb69f','RockStratum':'b39b89','DistantTeal':'91b2b4','OceanCyan':'55bcc3','TowerCream':'f8ecd0','RoofCoral':'d97c65','GlassNavy':'415b6b','PetalGold':'f9d879','PetalCream':'fff1cf','TrunkWood':'a27e61'}
for n,c in colors.items():
 m=bpy.data.materials.get(n) or bpy.data.materials.new(n);m.diffuse_color=color(c);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=color(c);p.inputs['Roughness'].default_value=.65
for o in bpy.data.objects:
 if o.type!='MESH':continue
 n=o.name.lower();mat='FeatherIvory'
 for token,m in [('eyeiris','IrisAmber'),('eyecatchlight','CatchlightCream'),('eyelid','FeatherIvory'),('eye','EyeInk'),('cheek','CheekCoral'),('nostril','BillMark'),('billlip','BillLipWarm'),('bill','BillPeach'),('pouch','PouchGold'),('foot','BillPeach'),('leg','BillPeach'),('lighthouseframes','TowerCream'),('lighthousewindow','TowerCream'),('frame','MintPaint'),('fork','MintPaint'),('tire','CreamRubber'),('rim','WarmRim'),('spoke','WarmRim'),('hub','WarmRim'),('bell','WarmRim'),('handle','SatinMetal'),('crank','SatinMetal'),('chain','SatinMetal'),('cable','CableRubber'),('brake','SatinMetal'),('grip','MintPaint'),('seat','SaddleLeather'),('pedal','SaddleLeather'),('road','SandCream'),('path','SandCream'),('sand','SandCream'),('grass','GrassGreen'),('coastshelf','GrassGreen'),('islanddistant','DistantTeal'),('island','GrassGreen'),('cliff','RockPeach'),('rockcool','RockCool'),('rock','RockPeach'),('ocean','OceanCyan'),('roof','RoofCoral'),('lighthouse','TowerCream'),('glass','GlassNavy'),('trunk','TrunkWood'),('fern','LeafSage'),('leaf','LeafSage'),('flowerstem','LeafSage'),('flowercream','PetalCream'),('flower','PetalGold')]:
  if token in n:mat=m;break
 if len(o.data.materials)==0:o.data.materials.append(bpy.data.materials[mat])
 else:o.data.materials[0]=bpy.data.materials[mat]
# Named architectural and terrain color zones on existing authored faces.
for o in bpy.data.objects:
 if o.type != 'MESH': continue
 if o.name.startswith(('Leaf','FernLeaf')):
  light=bpy.data.materials['LeafLight']
  if light.name not in o.data.materials: o.data.materials.append(light)
  slot=o.data.materials.find(light.name)
  for face in o.data.polygons:
   face.material_index=slot if face.center.z > (.85 if o.name.startswith('LeafShrubRound') else .34) else 0
 if o.name.startswith('LeafShrubRound'):
  # Assign complete connected leaves, never cut a face-height stripe across a blade.
  neighbors={v.index:[] for v in o.data.vertices}
  for edge in o.data.edges:
   a,b=edge.vertices;neighbors[a].append(b);neighbors[b].append(a)
  remaining=set(neighbors); leaf_colors={}
  while remaining:
   root_vertex=remaining.pop();component={root_vertex};pending=[root_vertex]
   while pending:
    for index in neighbors[pending.pop()]:
     if index in remaining: remaining.remove(index);component.add(index);pending.append(index)
   height=sum(o.data.vertices[index].co.z for index in component)/len(component)
   for index in component: leaf_colors[index]=slot if height>.85 else 0
  for face in o.data.polygons: face.material_index=leaf_colors[face.vertices[0]]
 if o.name == 'CliffHeadland':
  grass=bpy.data.materials['GrassGreen']
  if grass.name not in o.data.materials: o.data.materials.append(grass)
  slot=o.data.materials.find(grass.name)
  for face in o.data.polygons:
   face.material_index=slot if face.normal.z > .72 and face.center.z > -.12 else 0
 if o.name == 'GrassCape':
  # Keep grass on the upward original lip. Both native-extruded shoulder
  # rows are steep earth/stone; rooted foliage supplies narrow spill tongues.
  earth=bpy.data.materials['RockPeach']
  if earth.name not in o.data.materials: o.data.materials.append(earth)
  earth_slot=o.data.materials.find(earth.name)
  for face in o.data.polygons:
   face.material_index=earth_slot if any(i >= 105 for i in face.vertices) else 0
 if o.name.startswith('RockStack'):
  for face in o.data.polygons: face.material_index=0
 if o.name in ('RockShoreA', 'RockShoreA.002'):
  # Warm exposed cut planes and a restrained cooler recessed side on the
  # two individually edited foreground rocks; preserves their authored mesh.
  for name in ('RockLedge', 'RockStratum'):
   if name not in o.data.materials: o.data.materials.append(bpy.data.materials[name])
  upper=o.data.materials.find('RockLedge'); side=o.data.materials.find('RockStratum')
  for face in o.data.polygons:
   face.material_index=upper if face.normal.z>.72 else side if face.normal.y>.65 and face.normal.z<.3 else 0
 if o.name == 'LighthouseTower':
  band=bpy.data.materials['RoofCoral']
  if band.name not in o.data.materials: o.data.materials.append(band)
  slot=o.data.materials.find(band.name)
  for face in o.data.polygons:
   face.material_index=slot if .90 < face.center.z < 1.28 else 0
for o in bpy.data.objects:
 for modifier in o.modifiers:
  if modifier.type == 'SKIN': modifier.use_smooth_shade = True
# Set a clear non-destructive authoring view.
bpy.context.preferences.view.smooth_view=0
bpy.context.scene.tool_settings.transform_pivot_point='MEDIAN_POINT'
bpy.context.scene.tool_settings.use_proportional_edit=False
for screen in bpy.data.screens:
 for area in screen.areas:
  for sp in area.spaces:
   if sp.type=='VIEW_3D':
    sp.shading.type='SOLID';sp.shading.color_type='MATERIAL';sp.shading.show_cavity=True
bpy.ops.wm.save_as_mainfile(filepath=str(root/'source/pelican_coast.blend'))
bpy.ops.export_scene.gltf(filepath=str(export_target),export_format='GLB',export_apply=True,export_yup=True,export_cameras=False,export_lights=False,export_animations=False)
print('Exported authored Blender meshes only')
