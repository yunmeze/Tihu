extends RefCounted
## Bounded A13 record 0; candidate failure leaves the original NPC render intact.
const Identity=preload("res://scripts/earth/instance_identity_guard.gd")
const Guard=preload("res://scripts/earth/asset_guard.gd")
const PATH="res://assets/earth/npc/fangzhang_v1/manifest.json"
const SHA="0239fc9ac1f662d7756710f4f824e9d7a25a474caa0206996b6c9b2e269f9d59"
const SOURCE="res://data/maps/A13.json"
const SOURCE_SHA="d09549838963c8157307cc5406d3118baf69259d82459bcba0a3a8be5b34aa27"
static func prepare(path:Variant,map:Variant) -> CanvasTexture:
	if not path is String or not map is Dictionary:return null
	if not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=SHA:return null
	if not FileAccess.file_exists(SOURCE) or FileAccess.get_sha256(SOURCE)!=SOURCE_SHA:return null
	var p=JSON.new()
	if p.parse(FileAccess.get_file_as_string(SOURCE))!=OK or not p.data is Dictionary:return null
	var original:Dictionary=p.data
	if not Identity.map_identity(map):return null
	if not map.get("npcs") is Array or map.npcs.is_empty() or not Identity.npc_record(map.npcs[0],original.npcs[0]):return null
	if p.parse(FileAccess.get_file_as_string(path))!=OK or not p.data is Dictionary:return null
	var r:Dictionary=p.data
	if not FileAccess.file_exists(r.texture):return null
	var raw=Guard.texture(r.get("texture"),r.get("texture_size"),r.get("texture_sha256"))
	if raw==null:return null
	var tex=CanvasTexture.new();tex.diffuse_texture=raw;tex.texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR
	return tex
static func matches(entry:Variant) -> bool:
	return Identity.entry(entry,7,"Npc",261,1,37,10000,Vector2(3072,1184))
