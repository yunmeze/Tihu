extends RefCounted
## Bounded A13 record 0; candidate failure leaves the original NPC render intact.
const Guard=preload("res://scripts/earth/asset_guard.gd")
const PATH="res://assets/earth/npc/fangzhang_v1/manifest.json"
const SHA="0239fc9ac1f662d7756710f4f824e9d7a25a474caa0206996b6c9b2e269f9d59"
const SOURCE="res://data/maps/A13.json"
const SOURCE_SHA="d09549838963c8157307cc5406d3118baf69259d82459bcba0a3a8be5b34aa27"
static func prepare(path:String,map:Dictionary) -> CanvasTexture:
	if not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=SHA:return null
	if FileAccess.get_sha256(SOURCE)!=SOURCE_SHA:return null
	var p=JSON.new()
	if p.parse(FileAccess.get_file_as_string(SOURCE))!=OK or not p.data is Dictionary:return null
	var original:Dictionary=p.data
	if map.get("id")!="A13" or map.get("width")!=100 or map.get("height")!=100:return null
	if not map.get("npcs") is Array or map.npcs.is_empty() or map.npcs[0]!=original.npcs[0]:return null
	if p.parse(FileAccess.get_file_as_string(path))!=OK or not p.data is Dictionary:return null
	var r:Dictionary=p.data
	var raw=Guard.texture(r.get("texture"),r.get("texture_size"),r.get("texture_sha256"))
	if raw==null:return null
	var tex=CanvasTexture.new();tex.diffuse_texture=raw;tex.texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR
	return tex
static func matches(entry:Dictionary) -> bool:
	return entry.get("kind")==7 and entry.get("pack")=="Npc" and entry.get("index")==261 and entry.get("layer")==1 and entry.get("y")==37 and entry.get("order")==10000 and entry.get("origin")==Vector2(3072,1184)
