extends "res://scripts/earth/snapshot_plant_guard.gd"
## Original preparation semantics; only verified texture factory uses weak bank.
const Bank=preload("res://scripts/earth/plant_texture_weak_bank.gd")
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
		var shared=Bank.acquire(pin.path,pin.sha256,Vector2i(pin.width,pin.height))
		if shared==null:continue
		var texture=CanvasTexture.new()
		texture.diffuse_texture=shared
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

