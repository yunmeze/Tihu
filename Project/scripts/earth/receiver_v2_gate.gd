extends RefCounted
## Source-project, immutable-contract receiver. Masks never clip a rendered cast.
const Guard=preload("res://scripts/earth/asset_guard.gd")
const Identity=preload("res://scripts/earth/instance_identity_guard.gd")
const Hall=preload("res://scripts/earth/hall_candidate.gd")
const TreeCandidate=preload("res://scripts/earth/tree_candidate.gd")
const PATH="res://assets/earth/shadows/receiver_v2/manifest.json"
const SHA="94378c86a0c41b6f62aa9b9e06c46c346160c70936834b3a97ce884c7f61f330"
var ready=false
var slots={"lingyunzi":false,"first_tree":false}
var configuration={}
var textures={}
var hall_expected={}
var hall_prepared={}
var tree_prepared={}
func reset():
 ready=false;slots={"lingyunzi":false,"first_tree":false};configuration={};textures={};hall_expected={};hall_prepared={};tree_prepared={}
func file_hashes(inputs:Dictionary) -> bool:
 for path in inputs:
  if not path is String or not path.begins_with("res://") or not Guard.sha256(inputs[path]) or not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=inputs[path]:return false
 return true
func image_file(record:Dictionary) -> Image:
 if not FileAccess.file_exists(record.path):return null
 var tex=Guard.texture(record.path,record.texture_size,record.sha256)
 if tex==null:return null
 var image=tex.get_image()
 if image==null or (image.is_compressed() and image.decompress()!=OK):return null
 image.convert(Image.FORMAT_L8)
 return image
func prepare(map:Variant,path:Variant=PATH) -> bool:
 reset()
 if not Identity.map_identity(map) or not path is String or not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=SHA:return false
 var p=JSON.new()
 if p.parse(FileAccess.get_file_as_string(path))!=OK or not p.data is Dictionary:return false
 var r=p.data
 if not file_hashes(r.required_runtime_inputs) or not file_hashes({r.world_binding.path:r.world_binding.sha256}):return false
 var allowed=image_file(r.files.allowed);var forbidden=image_file(r.files.forbidden)
 if allowed==null or forbidden==null or allowed.get_size()!=Vector2i(1536,1024) or forbidden.get_size()!=allowed.get_size():return false
 var a=allowed.get_data();var f=forbidden.get_data()
 for i in a.size():
  if (a[i]!=0 and a[i]!=255) or (f[i]!=0 and f[i]!=255) or int(a[i])+int(f[i])!=255:return false
 hall_expected=Hall.scope(map);hall_prepared=Hall.read_prepare("res://assets/earth/environment/training_hall_v1/registration.json",map)
 if hall_expected.size()!=30 or hall_prepared.size()!=30:return false
 tree_prepared=TreeCandidate.prepare(TreeCandidate.PATH,map)
 for key in slots:
  var c=r.casters[key]
  if not file_hashes(c.inputs):continue
  var envelope=image_file(c.envelope)
  if envelope==null or envelope.get_size()!=allowed.get_size():continue
  var e=envelope.get_data();var valid=true;var count=0
  for i in e.size():
   if e[i]!=0 and e[i]!=255:valid=false;break
   if e[i]>0:
    count+=1
    if a[i]!=255:valid=false;break
  if not valid or count==0:continue
  var tex=Guard.texture(c.shadow_texture.path,c.shadow_texture.texture_size,c.shadow_texture.sha256)
  if not FileAccess.file_exists(c.shadow_texture.path) or tex==null:continue
  textures[key]=tex;slots[key]=true
 configuration=r;ready=true;return true
func hall_matches(map:Variant,objects:Variant,owners:Variant) -> bool:
 if not ready or not Identity.map_identity(map) or not objects is Array or not owners is Dictionary or owners!=hall_prepared or not map.get("cells") is Array or map.cells.size()!=10000:return false
 for order in hall_expected:
  if not Identity.source_cell(map.cells[order],hall_expected[order].source_cell):return false
 var found={}
 for entry in objects:
  if not entry is Dictionary or not Guard.integer(entry.get("order"),0,10010):continue
  var order=int(entry.order)
  if not hall_expected.has(order):continue
  var e=hall_expected[order]
  if found.has(order) or not Identity.entry(entry,4,"Map/Res/Building",int(e.frame_index),int(e.layer),int(e.sort_y),order,Vector2(e.cell[0]*48,e.cell[1]*32)):return false
  found[order]=true
 return found.size()==30
