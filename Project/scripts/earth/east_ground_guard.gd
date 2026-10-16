extends RefCounted
## Exactly 57 east-corridor owners. This group never depends on the 121-owner art.
const REGISTRATION="res://assets/earth/first_map_review/east_ground_registration.json"
const REGISTRATION_SHA256="b737e81e6896b1cccc5de4f8d1c628ed41b51a2efcf5ada0f1d215cf78cd350d"
const Identity=preload("res://scripts/earth/instance_identity_guard.gd")
const Guard=preload("res://scripts/earth/asset_guard.gd")
var failure:=""

# Virtual read seam: tests can remove dependencies without touching source art.
func file_available(path:String) -> bool:
	return FileAccess.file_exists(path)

func reject(reason:String) -> Dictionary:
	failure=reason
	return {}

func checked_bytes(path:String,expected:String) -> PackedByteArray:
	if not file_available(path):return PackedByteArray()
	var bytes=FileAccess.get_file_as_bytes(path)
	return bytes if digest(bytes)==expected else PackedByteArray()

func digest(bytes:PackedByteArray) -> String:
	var hash=HashingContext.new()
	hash.start(HashingContext.HASH_SHA256);hash.update(bytes)
	return hash.finish().hex_encode()

func exact(a:Variant,b:Variant) -> bool:
	if a is Dictionary and b is Dictionary:
		if a.size()!=b.size():return false
		for key in b:
			if not a.has(key) or not exact(a[key],b[key]):return false
		return true
	if a is Array and b is Array:
		if a.size()!=b.size():return false
		for i in a.size():
			if not exact(a[i],b[i]):return false
		return true
	if (a is int or a is float) and (b is int or b is float):
		return is_finite(float(a)) and is_finite(float(b)) and a==b
	return typeof(a)==typeof(b) and a==b

func registration(path:String) -> Dictionary:
	failure=""
	if path!=REGISTRATION:return reject("东廊地面注册路径无效")
	var bytes=checked_bytes(path,REGISTRATION_SHA256)
	if bytes.is_empty():return reject("东廊地面注册缺失或校验不符")
	var reg=JSON.parse_string(bytes.get_string_from_utf8())
	if not reg is Dictionary or reg.get("schema")!="earth-first-map-east-ground-v1":return reject("东廊地面注册结构无效")
	if not reg.get("group") is Dictionary or reg.group.get("owner_count")!=57 or not reg.group.get("owners") is Array or reg.group.owners.size()!=57:return reject("东廊地面范围无效")
	return reg

func identity_failure(contract:Dictionary,source:Dictionary,packs:Dictionary,floors:Array) -> String:
	if not Identity.map_identity(source) or not source.get("cells") is Array or source.cells.size()!=10000:return "东廊源地图结构变化"
	if floors.size()!=int(contract.floor_stream_count):return "东廊源地面序列长度变化"
	var selected={};var previous=-1
	for owner in contract.owners:
		if not owner is Dictionary or not Guard.integer(owner.get("stable_source_order"),0,9999):return "东廊所有者结构无效"
		var order=int(owner.stable_source_order)
		if order<=previous or selected.has(order):return "东廊所有者重复或顺序变化"
		previous=order;selected[order]=0
		if not Identity.source_cell(source.cells[order],owner.source_cell):return "东廊源地图单元变化"
		if order!=int(owner.cell[0])*100+int(owner.cell[1]) or not int(owner.source_cell[0]) in [-591,-406,-399]:return "东廊源地块身份变化"
		var slot=int(owner.floor_stream_index)
		if slot<0 or slot>=floors.size():return "东廊源地面位置无效"
		var floor_entry=floors[slot]
		if not floor_entry is Dictionary or floor_entry.size()!=3:return "东廊源地面结构变化"
		if not Identity.text(floor_entry.get("pack"),owner.pack) or not Identity.number(floor_entry.get("index"),int(owner.index)):return "东廊源地面身份变化"
		var origin=floor_entry.get("origin")
		if not origin is Vector2 or not is_finite(origin.x) or not is_finite(origin.y) or origin!=Vector2(owner.world_origin[0],owner.world_origin[1]):return "东廊源地面坐标变化"
		var pack=packs.get(owner.pack)
		if not pack is Dictionary or not pack.get("frames") is Dictionary or not pack.get("pages") is Array:return "东廊源图集结构变化"
		var frame=pack.frames.get(str(int(owner.index)))
		if not frame is Dictionary:return "东廊源帧缺失"
		var frozen:Dictionary=owner.source_frame
		for key in ["original","crop","offset","rect","page"]:
			if not exact(frame.get(key),frozen[key]):return "东廊源帧元数据变化"
		var page=int(frozen.page)
		if page<0 or page>=pack.pages.size() or not pack.pages[page] is Dictionary or not Identity.text(pack.pages[page].get("file"),frozen.atlas):return "东廊源图集页变化"
		if not exact(owner.shared_region_px,[768+posmod(2*int(owner.world_origin[0]),768),768+posmod(2*int(owner.world_origin[1]),768),192,128]):return "东廊共享相位变化"
	return ""

func prepare(source:Dictionary,packs:Dictionary,floors:Array,path:String=REGISTRATION) -> Dictionary:
	var reg=registration(path)
	if reg.is_empty():return {}
	var resources={}
	for pin in reg.runtime_files:
		var bytes=checked_bytes(pin.path,pin.sha256)
		if bytes.is_empty():return reject("东廊地面依赖缺失或校验不符："+str(pin.path).get_file())
		resources[pin.path]=bytes
	var source_disk=JSON.parse_string(resources[reg.source_map.path].get_string_from_utf8())
	var manifest_disk=JSON.parse_string(resources[reg.source_manifest.path].get_string_from_utf8())
	if not source_disk is Dictionary or not manifest_disk is Dictionary or not manifest_disk.get("packs") is Dictionary or not source_matches(source,source_disk) or not atlas_matches(packs,manifest_disk.packs):return reject("运行时东廊地图或图集身份变化")
	# Verify the entire original x-major draw stream, including all nonselected
	# floors. This also proves that no selected owner occurs a second time.
	var expected_stream=[]
	for order in source.cells.size():
		var number=int(source.cells[order][0])
		if number==0:continue
		expected_stream.append({"pack":"Map/Res/FloorBig" if number<0 else "Map/Res/FloorSmall","index":absi(number),"origin":Vector2(floori(float(order)/100.0)*48,(order%100)*32)})
	if not exact(floors,expected_stream):return reject("东廊完整地面序列身份或顺序变化")
	var contract:Dictionary=reg.group
	var error=identity_failure(contract,source,packs,floors)
	if not error.is_empty():return reject(error)
	var tile=Image.new()
	if tile.load_png_from_buffer(resources[contract.tile.path])!=OK or tile.get_size()!=Vector2i(768,768):return reject("东廊周期纹理解码失败")
	tile.convert(Image.FORMAT_RGBA8)
	# Verify the actual source crop once per distinct frame before publishing.
	var atlases={};var frames={}
	for owner in contract.owners:
		var sf:Dictionary=owner.source_frame
		if not atlases.has(sf.atlas):
			var atlas=Image.new()
			if atlas.load_png_from_buffer(resources[sf.atlas])!=OK:return reject("东廊源图集解码失败")
			atlas.convert(Image.FORMAT_RGBA8);atlases[sf.atlas]=atlas
		if not frames.has(owner.index):
			var r:Array=sf.rect
			if digest(atlases[sf.atlas].get_region(Rect2i(r[0],r[1],r[2],r[3])).get_data())!=sf.rgba_sha256:return reject("东廊源像素变化")
			frames[owner.index]=true
	var image=Image.create(2304,2304,false,Image.FORMAT_RGBA8)
	for y in 3:
		for x in 3:image.blit_rect(tile,Rect2i(0,0,768,768),Vector2i(x*768,y*768))
	var texture=CanvasTexture.new()
	texture.diffuse_texture=ImageTexture.create_from_image(image)
	texture.texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR
	texture.texture_repeat=CanvasItem.TEXTURE_REPEAT_DISABLED
	var owners={}
	for owner in contract.owners:
		var r:Array=owner.shared_region_px
		owners[int(owner.stable_source_order)]={"origin":Vector2(owner.world_origin[0],owner.world_origin[1]),"region":Rect2(r[0],r[1],r[2],r[3])}
	failure=""
	return {"owners":owners,"texture":texture,"contract":contract,"registration":path,"validated_floor_stream":floors.duplicate(true)}

func snapshot_file_available(path:String,snapshot:Dictionary) -> bool:
	if snapshot.is_empty():return file_available(path)
	if not snapshot.has("available"):snapshot.available={}
	if not snapshot.available.has(path):snapshot.available[path]=file_available(path)
	return snapshot.available[path]

func live_valid(group:Dictionary,source:Dictionary,packs:Dictionary,floors:Array,snapshot:Dictionary={}) -> bool:
	failure=""
	if group.is_empty():return false
	# One whole-stream comparison per refresh, never a full scan per owner.
	if floors!=group.validated_floor_stream:failure="运行时完整地面序列变化，东廊57整组已撤回";return false
	if not snapshot_file_available(group.registration,snapshot):failure="运行时东廊地面注册缺失";return false
	for pin in group.contract.source_dependencies:
		if not snapshot_file_available(pin.path,snapshot):failure="运行时东廊地面依赖缺失："+str(pin.path).get_file();return false
	failure=identity_failure(group.contract,source,packs,floors)
	return failure.is_empty()

# Default review remains strict; snapshot adapters override only these comparisons.
func source_matches(source:Dictionary,original:Dictionary) -> bool:
	return exact(source,original)

func atlas_matches(runtime:Dictionary,original:Dictionary) -> bool:
	return exact(runtime,original)
