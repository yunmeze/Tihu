extends RefCounted
## Preparation only: no mutations, no publication, no copies of unvalidated fields.
## Bounded logical coordinates/scales avoid float64 -> float32 overflow/underflow.
const MAX_COORD=1048576.0
const MIN_SCALE=1.0/65536.0

static func number(value:Variant,low:float,high:float) -> bool:
	return (value is int or value is float) and is_finite(float(value)) and value>=low and value<=high

static func integer(value:Variant,low:int,high:int) -> bool:
	return number(value,low,high) and value==floor(value)

static func vector(value:Variant,count:int,low:float,high:float) -> bool:
	if not value is Array or value.size()!=count:return false
	for part in value:
		if not number(part,low,high):return false
	return true

static func asset_path(path:Variant) -> bool:
	if not path is String or not path.begins_with("res://assets/") or path.length()>1024:return false
	if path.contains("\\") or path.contains("%"):return false
	for i in path.length():
		var code=path.unicode_at(i)
		if code<32 or (code>=127 and code<=159):return false
	var relative=path.substr(6)
	for segment in relative.split("/",true):
		if segment in ["",".",".."] or segment.contains(":"):return false
	return path.simplify_path()==path and path.ends_with(".png")

static func sha256(value:Variant) -> bool:
	if not value is String or value.length()!=64:return false
	for c in value:
		if not c in "0123456789abcdef":return false
	return true

static func texture(path:Variant,size:Variant,digest:Variant) -> Texture2D:
	if not asset_path(path) or not vector(size,2,1,16384) or not sha256(digest):return null
	if not integer(size[0],1,16384) or not integer(size[1],1,16384):return null
	# Source project bytes can be checked here. Packed builds must also verify
	# their import/build manifest; absence of loose PNG is not a hash assertion.
	if FileAccess.file_exists(path) and FileAccess.get_sha256(path)!=digest:return null
	if not ResourceLoader.exists(path,"Texture2D"):return null
	var tex=load(path)
	return tex if tex is Texture2D and tex.get_size()==Vector2(size[0],size[1]) else null

static func prepare_owners(records:Variant,source_map:Dictionary,expected:Dictionary) -> Dictionary:
	if not records is Array or records.size()!=expected.size() or records.is_empty():return {}
	if not source_map.get("id") is String or source_map.id!="A13" or not integer(source_map.get("width"),1,4096) or not integer(source_map.get("height"),1,4096):return {}
	var width=int(source_map.width);var height=int(source_map.height)
	if not source_map.get("cells") is Array or source_map.cells.size()!=width*height:return {}
	var staged={}
	for record in records:
		if not record is Dictionary:return {}
		var order=record.get("stable_source_order")
		if not integer(order,0,width*height-1):return {}
		order=int(order)
		if not expected.has(order) or staged.has(order):return {}
		var identity=expected[order]
		if not identity is Dictionary:return {}
		# The caller supplies a frozen, source-verified scope, never values derived
		# from the incoming registration. Match every identity field before load.
		for field in ["key","pack"]:
			if not record.get(field) is String or not identity.get(field) is String or record[field]!=identity[field]:return {}
		for field in ["frame_index","layer","sort_y"]:
			if not integer(record.get(field),0,65535) or not integer(identity.get(field),0,65535) or record[field]!=identity[field]:return {}
		var cell=record.get("cell")
		var expected_cell=identity.get("cell")
		if not vector(cell,2,0,4095) or not vector(expected_cell,2,0,4095):return {}
		for axis in 2:
			if not integer(cell[axis],0,4095) or not integer(expected_cell[axis],0,4095) or int(cell[axis])!=int(expected_cell[axis]):return {}
		if cell[0]>=width or cell[1]>=height or int(cell[0])*height+int(cell[1])!=order:return {}
		var source=source_map.cells[order]
		if not source is Array or source.size()!=4 or not record.get("source_cell") is Array or record.source_cell.size()!=4:return {}
		for index in 4:
			if not integer(source[index],-32768,65535) or not integer(record.source_cell[index],-32768,65535) or int(source[index])!=int(record.source_cell[index]):return {}
		if not vector(record.get("world_top_left"),2,-MAX_COORD,MAX_COORD) or not number(record.get("scale"),MIN_SCALE,4):return {}
		var tex=texture(record.get("texture"),record.get("texture_size"),record.get("texture_sha256"))
		if tex==null:return {}
		staged[order]={"texture":tex,"world_top_left":Vector2(record.world_top_left[0],record.world_top_left[1]),"scale":float(record.scale)}
	return staged
