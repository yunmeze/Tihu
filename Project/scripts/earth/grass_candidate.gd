extends RefCounted
## Two explicit grass groups, each two-owner group publishes independently.
const Identity=preload("res://scripts/earth/instance_identity_guard.gd")
const Guard=preload("res://scripts/earth/asset_guard.gd")
const SOURCE="res://data/maps/A13.json"
const SOURCE_SHA="d09549838963c8157307cc5406d3118baf69259d82459bcba0a3a8be5b34aa27"
const PATHS=["res://assets/earth/environment/grass_pair_v1/registration_A.json","res://assets/earth/environment/grass_pair_v1/registration_B.json"]
const SHAS=["c53d03de5aa0917772c999a91931746283b01972071b0b736f03480bc8f5408c","9e4b1b58b57d32e410b775dbfaf9c53ff436b0b13d6fb3265791ec022da3e395"]
const CELLS=[[[54,30],[55,30]],[[54,31],[55,31]]]
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
 if not r.get("owners") is Array or r.owners.size()!=2:return {}
 var staged={};var origin=Vector2(2606.8333333333335,959.5714285714286) if n==0 else Vector2(2555.5,985.4285714285714)
 for i in 2:
  var c=CELLS[n][i];var order=c[0]*100+c[1];var item=r.owners[i]
  if not item is Dictionary or not Identity.number(item.get("frame_index"),239+n*2+i) or not Identity.number(item.get("stable_source_order"),order):return {}
  if not item.get("cell") is Array or item.cell.size()!=2 or not Identity.number(item.cell[0],c[0]) or not Identity.number(item.cell[1],c[1]):return {}
  if not Identity.source_cell(item.get("source_cell"),original.cells[order]) or not Identity.source_cell(map.cells[order],original.cells[order]):return {}
  if not Identity.text(item.get("pack"),"Map/Res/Plant") or not Identity.number(item.get("layer"),1) or not Identity.number(item.get("sort_y"),c[1]) or not Guard.number(item.get("scale"),1.0/21.0-1e-15,1.0/21.0+1e-15):return {}
  if not item.get("empty") is bool or item.empty:return {}
  var tex:Texture2D
  if not item.empty:
   if not item.get("texture") is String or not FileAccess.file_exists(item.texture):return {}
   tex=Guard.texture(item.texture,item.get("texture_size"),item.get("texture_sha256"))
   if tex==null:return {}
  staged[order]={"index":239+n*2+i,"empty":item.empty,"texture":tex,"origin":origin,"size":Vector2(2172,724)/21.0}
 return staged
