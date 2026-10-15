extends RefCounted
## Two additional exact shrub instances, each four-owner group publishes independently.
const Identity=preload("res://scripts/earth/instance_identity_guard.gd")
const Guard=preload("res://scripts/earth/asset_guard.gd")
const SOURCE="res://data/maps/A13.json"
const SOURCE_SHA="d09549838963c8157307cc5406d3118baf69259d82459bcba0a3a8be5b34aa27"
const PATHS=["res://assets/earth/environment/round_shrub_v1/registration_51_44.json","res://assets/earth/environment/round_shrub_v1/registration_64_45.json"]
const SHAS=["acff0018134654b8c26a652edd4661d338f0c631d2daebb4d0773da3aed3103d","c7f6ebbe6e9239413722cceaed8e994caa854f191721e23651154176c65515a2"]
const CELLS=[[[51,41],[50,44],[51,44],[52,44]],[[64,42],[63,45],[64,45],[65,45]]]
static func prepare(instance:Variant,path:Variant,map:Variant) -> Dictionary:
 if not Guard.integer(instance,0,1) or not path is String or not map is Dictionary:return {}
 var n=int(instance)
 if not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=SHAS[n]:return {}
 if not FileAccess.file_exists(SOURCE) or FileAccess.get_sha256(SOURCE)!=SOURCE_SHA:return {}
 var p=JSON.new()
 if p.parse(FileAccess.get_file_as_string(SOURCE))!=OK or not p.data is Dictionary:return {}
 var original:Dictionary=p.data
 if not Identity.map_identity(map) or not map.get("cells") is Array or map.cells.size()!=10000:return {}
 if p.parse(FileAccess.get_file_as_string(path))!=OK or not p.data is Dictionary:return {}
 var r:Dictionary=p.data
 if not r.get("owners") is Array or r.owners.size()!=4:return {}
 var staged={};var origin=Vector2(3031,1365)
 if n==0:origin=Vector2(2407,1333)
 for i in 4:
  var c=CELLS[n][i];var order=c[0]*100+c[1];var item=r.owners[i]
  if not item is Dictionary or not Identity.number(item.get("frame_index"),143+i) or not Identity.number(item.get("stable_source_order"),order):return {}
  if not item.get("cell") is Array or item.cell.size()!=2 or not Identity.number(item.cell[0],c[0]) or not Identity.number(item.cell[1],c[1]):return {}
  if not Identity.source_cell(item.get("source_cell"),original.cells[order]) or not Identity.source_cell(map.cells[order],original.cells[order]):return {}
  if not Identity.text(item.get("pack"),"Map/Res/Plant") or not Identity.number(item.get("layer"),1) or not Identity.number(item.get("sort_y"),c[1]) or not Guard.number(item.get("scale"),1.0/11.0-1e-15,1.0/11.0+1e-15):return {}
  if not item.get("empty") is bool or item.empty:return {}
  var tex:Texture2D
  if not item.empty:
   if not item.get("texture") is String or not FileAccess.file_exists(item.texture):return {}
   tex=Guard.texture(item.texture,item.get("texture_size"),item.get("texture_sha256"))
   if tex==null:return {}
  staged[order]={"index":143+i,"empty":item.empty,"texture":tex,"origin":origin,"size":Vector2(1363,1154)/11.0}
 return staged
