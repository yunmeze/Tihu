extends RefCounted
## Typed comparisons for the exact, source-bound Earth instance scopes.
const Guard=preload("res://scripts/earth/asset_guard.gd")
static func text(value:Variant,expected:String) -> bool:return value is String and value==expected
static func number(value:Variant,expected:int) -> bool:return Guard.integer(value,expected,expected)
static func map_identity(map:Variant) -> bool:
	if not map is Dictionary:return false
	return text(map.get("id"),"A13") and number(map.get("width"),100) and number(map.get("height"),100)
static func source_cell(value:Variant,expected:Array) -> bool:
	if not value is Array or value.size()!=4:return false
	for i in 4:
		if not number(value[i],int(expected[i])):return false
	return true
static func npc_record(value:Variant,expected:Dictionary) -> bool:
	if not value is Dictionary or value.size()!=expected.size():return false
	for key in ["x","y","appearance","direction"]:
		if not number(value.get(key),int(expected[key])):return false
	for key in ["name","script"]:
		if not text(value.get(key),expected[key]):return false
	return true
static func entry(value:Variant,kind:int,pack:String,index:int,layer:int,y:int,order:int,origin:Vector2) -> bool:
	if not value is Dictionary:return false
	if not number(value.get("kind"),kind) or not text(value.get("pack"),pack) or not number(value.get("index"),index) or not number(value.get("layer"),layer) or not number(value.get("y"),y) or not number(value.get("order"),order):return false
	var p=value.get("origin")
	return p is Vector2 and is_finite(p.x) and is_finite(p.y) and p==origin
