extends RefCounted
## Exactly the 64 original FloorBig owners filling the approved sample rectangle.
const Guard=preload("res://scripts/earth/asset_guard.gd")
const PACK="Map/Res/FloorBig"
static func scope(source:Dictionary) -> Dictionary:
	if source.get("id")!="A13" or source.get("height")!=100 or source.get("width")!=100:return {}
	if not source.get("cells") is Array or source.cells.size()!=10000:return {}
	var expected={}
	for x in range(52,68,2):
		for y in range(30,46,2):
			var order=x*100+y
			var c=source.cells[order]
			if not c is Array or c.size()!=4 or not Guard.integer(c[0],-32768,-1):return {}
			var frame=-int(c[0])
			expected[order]={"key":"%s:%d@%d,%d"%[PACK,frame,x,y],"pack":PACK,"frame_index":frame,"cell":[x,y],"layer":0,"sort_y":y}
	return expected
static func same_numbers(value:Variant,expected:Array) -> bool:
	if not value is Array or value.size()!=expected.size():return false
	for i in expected.size():
		if not Guard.number(value[i],-Guard.MAX_COORD,Guard.MAX_COORD) or value[i]!=expected[i]:return false
	return true
static func prepare(reg:Variant,source:Dictionary) -> Dictionary:
	if not reg is Dictionary or not reg.get("owners") is Array:return {}
	var expected=scope(source)
	if expected.size()!=64 or reg.owners.size()!=64:return {}
	for owner in reg.owners:
		if not owner is Dictionary or not Guard.integer(owner.get("stable_source_order"),0,9999):return {}
		var order=int(owner.stable_source_order)
		if not expected.has(order):return {}
		var cell=expected[order].cell
		if not same_numbers(owner.get("world_top_left"),[cell[0]*48,cell[1]*32]) or not same_numbers(owner.get("texture_size"),[192,128]) or not Guard.number(owner.get("scale"),.5,.5):return {}
	return Guard.prepare_owners(reg.owners,source,expected)
static func read_prepare(path:String,source:Dictionary) -> Dictionary:
	if not FileAccess.file_exists(path):return {}
	var parser=JSON.new()
	if parser.parse(FileAccess.get_file_as_string(path))!=OK:return {}
	return prepare(parser.data,source)
