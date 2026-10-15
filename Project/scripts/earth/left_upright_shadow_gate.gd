extends RefCounted
## One source-bound left upright; complete conservative patch, no clipping.
const Guard=preload("res://scripts/earth/asset_guard.gd")
const Identity=preload("res://scripts/earth/instance_identity_guard.gd")
const Upright=preload("res://scripts/earth/upright_candidate.gd")
const PATH="res://assets/earth/shadows/left_upright_v1/manifest.json"
const SHA="ee32ba2d5bf2c421f22a0b6eebe286c57746b0cc9c4e9947219a96fd4dbc4701"
var ready=false
var configuration={}
var expected={}
var texture:Texture2D
func reset():ready=false;configuration={};expected={};texture=null
func prepare(map:Variant,path:Variant=PATH) -> bool:
 reset()
 if not Identity.map_identity(map) or not map.get("cells") is Array or map.cells.size()!=10000:return false
 if not path is String or path!=PATH or not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=SHA:return false
 var parser=JSON.new()
 if parser.parse(FileAccess.get_file_as_string(path))!=OK or not parser.data is Dictionary:return false
 var r=parser.data
 if not r.get("input_sha256") is Dictionary:return false
 for file in r.input_sha256:
  if not file is String or not file.begins_with("res://") or not Guard.sha256(r.input_sha256[file]) or not FileAccess.file_exists(file) or FileAccess.get_sha256(file)!=r.input_sha256[file]:return false
 var images={}
 for key in ["allowed","forbidden","nominal-envelope","root-error-envelope"]:
  var record=r.receiver.files[key]
  if not FileAccess.file_exists(record.path):return false
  var tex=Guard.texture(record.path,record.texture_size,record.sha256)
  if tex==null:return false
  var image=tex.get_image()
  if image==null or (image.is_compressed() and image.decompress()!=OK):return false
  image.convert(Image.FORMAT_L8)
  if image.get_size()!=Vector2i(1210,380):return false
  images[key]=image.get_data()
 var a=images.allowed;var f=images.forbidden
 for i in a.size():
  if a[i] not in [0,255] or f[i] not in [0,255] or int(a[i])+int(f[i])!=255:return false
 for key in ["nominal-envelope","root-error-envelope"]:
  var count=0
  for i in a.size():
   if images[key][i] not in [0,255]:return false
   if images[key][i]>0:
    if a[i]!=255:return false
    count+=1
  if count==0:return false
 var staged=Upright.prepare(0,Upright.PATHS[0],map)
 if staged.size()!=6 or not FileAccess.file_exists(r.body_texture.path):return false
 var tex=Guard.texture(r.body_texture.path,r.body_texture.texture_size,r.body_texture.sha256)
 if tex==null:return false
 configuration=r;expected=staged;texture=tex;ready=true;return true
func matches(map:Variant,objects:Variant,owners:Variant) -> bool:
 if not ready or not Identity.map_identity(map) or not map.get("cells") is Array or map.cells.size()!=10000 or not objects is Array or not owners is Dictionary or owners!=expected:return false
 for owner in configuration.identity.owners:
  if not Identity.source_cell(map.cells[owner.stable_source_order],owner.source_cell):return false
 var found={}
 for entry in objects:
  if not entry is Dictionary or not Guard.integer(entry.get("order"),0,9999):continue
  var order=int(entry.order)
  if not expected.has(order):continue
  var item=expected[order]
  if found.has(order) or not Identity.entry(entry,2,"Map/Res/Plant",item.index,1,order%100,order,Vector2(order/100,order%100)*Vector2(48,32)):return false
  found[order]=true
 return found.size()==6
