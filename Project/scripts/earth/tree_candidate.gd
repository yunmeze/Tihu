extends RefCounted
## One original Plant group; same-canvas textures preserve the validated sampling phase.
const Identity=preload("res://scripts/earth/instance_identity_guard.gd")
const Guard=preload("res://scripts/earth/asset_guard.gd")
const PATH="res://assets/earth/environment/first_tree_v1/registration.json"
const SHA="a83f1f401b10394e13e7822f6eb04078cace3db3dc0bdca10e275b38d0bb9b27"
const SOURCE="res://data/maps/A13.json"
const SOURCE_SHA="d09549838963c8157307cc5406d3118baf69259d82459bcba0a3a8be5b34aa27"
const IDENTITIES=[[292,57,34],[293,55,37],[294,56,37],[295,58,37],[296,59,37],[297,60,37],[298,61,37]]
static func prepare(path:Variant,map:Variant) -> Dictionary:
	if not path is String or not map is Dictionary:return {}
	if not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=SHA:return {}
	if not FileAccess.file_exists(SOURCE) or FileAccess.get_sha256(SOURCE)!=SOURCE_SHA:return {}
	var p=JSON.new()
	if p.parse(FileAccess.get_file_as_string(SOURCE))!=OK or not p.data is Dictionary:return {}
	var original:Dictionary=p.data
	if not Identity.map_identity(map) or not map.get("cells") is Array or map.cells.size()!=10000:return {}
	if p.parse(FileAccess.get_file_as_string(path))!=OK or not p.data is Dictionary:return {}
	var r:Dictionary=p.data
	if not r.get("owners") is Array or r.owners.size()!=7:return {}
	var staged={}
	for i in IDENTITIES.size():
		var expected=IDENTITIES[i];var order=expected[1]*100+expected[2];var item=r.owners[i]
		if not item is Dictionary or item.get("frame_index")!=expected[0] or not item.get("cell") is Array or item.cell.size()!=2 or item.cell[0]!=expected[1] or item.cell[1]!=expected[2] or item.get("stable_source_order")!=order:return {}
		if item.get("source_cell")!=original.cells[order] or not Identity.source_cell(map.cells[order],original.cells[order]):return {}
		if item.get("pack")!="Map/Res/Plant" or item.get("layer")!=1 or item.get("sort_y")!=expected[2] or item.get("scale")!=.25:return {}
		if not item.get("empty") is bool or item.empty!=(expected[0]==298):return {}
		var tex:Texture2D
		if not item.empty:
			if not FileAccess.file_exists(item.texture):return {}
			tex=Guard.texture(item.get("texture"),item.get("texture_size"),item.get("texture_sha256"))
			if tex==null:return {}
		staged[order]={"index":expected[0],"empty":item.empty,"texture":tex,"origin":Vector2(2630.25,784),"size":Vector2(313.5,313.5)}
	return staged
