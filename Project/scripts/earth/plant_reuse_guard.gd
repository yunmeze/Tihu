extends RefCounted
## Complete, source-bound instances only. No new shadow owner is ever registered.
const REGISTRATION="res://assets/earth/first_map_review/plant_reuse_registration.json"
const REGISTRATION_SHA256="e8db80f83ba048ca6f7b81947a7fab9c99bc6bad48c5ac4a3e295bb540109863"
const StaticGuard=preload("res://scripts/earth/static_props_guard.gd")
var identity_guard=StaticGuard.new()
var failure:=""
var errors:Dictionary={}

func file_available(path:String) -> bool:
	return FileAccess.file_exists(path)

func reject(reason:String) -> Dictionary:
	failure=reason
	return {}

func checked_bytes(path:String,expected:String) -> PackedByteArray:
	if not file_available(path):return PackedByteArray()
	var bytes=FileAccess.get_file_as_bytes(path)
	var hash=HashingContext.new()
	hash.start(HashingContext.HASH_SHA256);hash.update(bytes)
	return bytes if hash.finish().hex_encode()==expected else PackedByteArray()

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
	failure="";errors.clear()
	if path!=REGISTRATION:return reject("植物复用注册路径无效")
	var bytes=checked_bytes(path,REGISTRATION_SHA256)
	if bytes.is_empty():return reject("植物复用注册缺失或校验不符")
	var reg=JSON.parse_string(bytes.get_string_from_utf8())
	if not reg is Dictionary or reg.get("schema")!="earth-first-map-plant-reuse-v1":return reject("植物复用注册结构无效")
	if not reg.get("groups") is Dictionary or reg.groups.size()!=24 or reg.get("owner_count")!=81 or reg.get("new_shadow")!=false:return reject("植物复用注册范围无效")
	return reg

func prepare(source:Dictionary,objects:Array,packs:Dictionary,path:String=REGISTRATION) -> Dictionary:
	var reg=registration(path)
	if reg.is_empty():return {}
	var resources={}
	# Unique dependencies are read and verified once. A failed owner texture only
	# withholds instances that actually use it; it never publishes partial owners.
	for pin in reg.runtime_files:
		var bytes=checked_bytes(pin.path,pin.sha256)
		if not bytes.is_empty():resources[pin.path]=bytes
	if not resources.has(reg.source_map.path) or not resources.has(reg.source_manifest.path):return reject("植物复用源地图或图集缺失或校验不符")
	var source_disk=JSON.parse_string(resources[reg.source_map.path].get_string_from_utf8())
	var manifest_disk=JSON.parse_string(resources[reg.source_manifest.path].get_string_from_utf8())
	if not source_disk is Dictionary or not manifest_disk is Dictionary or not manifest_disk.get("packs") is Dictionary or not source_matches(source,source_disk) or not atlas_matches(packs,manifest_disk.packs):return reject("运行时植物地图或图集身份变化")
	var contracts=[]
	for contract in reg.groups.values():contracts.append({"contract":contract})
	# Preparation also shares one fresh object scan across all 24 instances.
	var snapshot=identity_guard.refresh_snapshot(contracts,objects)
	var textures={}
	for pin in reg.runtime_files:
		if pin.role!="texture" or not resources.has(pin.path):continue
		var image=Image.new()
		if image.load_png_from_buffer(resources[pin.path])!=OK or image.get_size()!=Vector2i(pin.width,pin.height):continue
		var texture=CanvasTexture.new()
		texture.diffuse_texture=ImageTexture.create_from_image(image)
		texture.texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR
		texture.texture_repeat=CanvasItem.TEXTURE_REPEAT_DISABLED
		textures[pin.path]=texture
	var result={}
	for id in reg.groups:
		var contract:Dictionary=reg.groups[id]
		var error=identity_guard.identity_failure(contract,source,objects,packs,snapshot)
		if not error.is_empty():errors[id]=error;continue
		for pin in contract.source_dependencies:
			if not resources.has(pin.path):error="植物实例依赖缺失或校验不符："+str(pin.path).get_file();break
		if not error.is_empty():errors[id]=error;continue
		var staged={}
		for record in contract.owners:
			if not textures.has(record.texture):error="植物实例纹理解码失败";break
			staged[int(record.stable_source_order)]={"pack":record.pack,"index":int(record.index),"texture":textures[record.texture],"origin":Vector2(record.world_top_left[0],record.world_top_left[1]),"size":Vector2(record.texture_size[0],record.texture_size[1])*float(record.scale),"empty":record.empty}
		if not error.is_empty() or staged.size()!=int(contract.owner_count):errors[id]=error if not error.is_empty() else "植物实例所有者数量变化";continue
		result[id]={"family":contract.family,"owners":staged,"contract":contract,"registration":path}
	failure="" if errors.is_empty() else "%d 个完整植物实例已回退"%errors.size()
	return result

func snapshot_file_available(path:String,snapshot:Dictionary) -> bool:
	if snapshot.is_empty():return file_available(path)
	if not snapshot.has("available"):snapshot.available={}
	if not snapshot.available.has(path):snapshot.available[path]=file_available(path)
	return snapshot.available[path]

# Caller shares static_props_guard.refresh_snapshot(static_groups + plant_groups,
# objects) with both guards. The snapshot is local to one synchronous refresh.
func live_valid(group:Dictionary,source:Dictionary,objects:Array,packs:Dictionary,snapshot:Dictionary={}) -> bool:
	failure=""
	if group.is_empty():return false
	if not snapshot_file_available(group.registration,snapshot):failure="运行时植物复用注册缺失";return false
	for pin in group.contract.source_dependencies:
		if not snapshot_file_available(pin.path,snapshot):failure="运行时植物实例依赖缺失："+str(pin.path).get_file();return false
	failure=identity_guard.identity_failure(group.contract,source,objects,packs,snapshot)
	return failure.is_empty()

# Default review remains strict; snapshot adapters override only these comparisons.
func source_matches(source:Dictionary,original:Dictionary) -> bool:
	return exact(source,original)

func atlas_matches(runtime:Dictionary,original:Dictionary) -> bool:
	return exact(runtime,original)
