extends RefCounted
## Frozen optional first-map static-prop integration. No ordinary scene depends on this.
const REGISTRATION="res://assets/earth/first_map_review/static_props_registration.json"
const REGISTRATION_SHA256="5794b3a0ec72736b70465e009a5e55f3de41b9939fa576fbc6568ab6274311a6"
const Identity=preload("res://scripts/earth/instance_identity_guard.gd")
var failure:=""

# Kept as a narrow virtual read seam so external tests can simulate a missing
# dependency without renaming or modifying the user's immutable source files.
func file_available(path:String) -> bool:
	return FileAccess.file_exists(path)

func reject(reason:String) -> Dictionary:
	failure=reason
	return {}

func registration(path:String) -> Dictionary:
	failure=""
	if path!=REGISTRATION or not file_available(path) or FileAccess.get_sha256(path)!=REGISTRATION_SHA256:
		return reject("静态物件注册缺失或校验不符")
	var parsed=JSON.parse_string(FileAccess.get_file_as_string(path))
	if not parsed is Dictionary or parsed.get("schema")!="earth-first-map-static-props-v1":return reject("静态物件注册结构无效")
	if not parsed.get("groups") is Dictionary or not parsed.groups.has("pool") or not parsed.groups.has("clump"):return reject("静态物件分组缺失")
	return parsed

func identity_failure(group:Dictionary,source:Variant,objects:Variant,packs:Variant,snapshot:Dictionary={}) -> String:
	if not Identity.map_identity(source) or not source.get("cells") is Array or source.cells.size()!=10000:return "源地图结构变化"
	if not objects is Array or not packs is Dictionary:return "源物件或图集结构变化"
	var owners=group.get("owners")
	if not owners is Array or owners.size()!=group.get("owner_count"):return "静态物件所有者数量变化"
	for owner in owners:
		if not owner is Dictionary:return "所有者结构无效"
		var order=owner.get("stable_source_order")
		if not (order is int or order is float) or not is_finite(float(order)) or float(order)!=floorf(float(order)) or order<0 or order>=source.cells.size():return "所有者顺序无效"
		if not owner.get("source_cell") is Array or owner.source_cell.size()!=4 or not owner.get("cell") is Array or owner.cell.size()!=2 or not owner.get("source_frame") is Dictionary:return "所有者源结构无效"
		for field in ["index","layer","sort_y"]:
			var value=owner.get(field)
			if not (value is int or value is float) or not is_finite(float(value)) or float(value)!=floorf(float(value)):return "所有者数值无效"
		if not owner.get("pack") is String:return "所有者图集无效"
		for value in owner.cell+owner.source_cell:
			if not (value is int or value is float) or not is_finite(float(value)) or float(value)!=floorf(float(value)):return "所有者源数值无效"
		for field in ["original","crop","offset","rect"]:
			if not owner.source_frame.get(field) is Array:return "所有者源帧结构无效"
		if not owner.source_frame.has("page") or not owner.source_frame.get("atlas") is String:return "所有者源图集页无效"
		if not Identity.source_cell(source.cells[int(order)],owner.source_cell):return "源地图单元变化：%s"%owner.index
		var found:=0
		if snapshot.is_empty():
			for entry in objects:
				if not entry is Dictionary:return "源物件序列结构变化"
				if entry.get("order")==order:
					if not Identity.entry(entry,int(owner.source_cell[2]),owner.pack,int(owner.index),int(owner.layer),int(owner.sort_y),int(order),Vector2(owner.cell[0]*48,owner.cell[1]*32)):return "源物件身份变化：%s"%owner.index
					found+=1
		else:
			var entries:Array=snapshot.by_order.get(int(order),[])
			for indexed in entries:
				if snapshot.first_invalid>=0 and snapshot.first_invalid<indexed.position:return "源物件序列结构变化"
				var entry=indexed.entry
				if not Identity.entry(entry,int(owner.source_cell[2]),owner.pack,int(owner.index),int(owner.layer),int(owner.sort_y),int(order),Vector2(owner.cell[0]*48,owner.cell[1]*32)):return "源物件身份变化：%s"%owner.index
				found+=1
			if not snapshot.is_empty() and snapshot.first_invalid>=0:return "源物件序列结构变化"
		if found!=1:return "源物件缺失或重复：%s"%owner.index
		var pack=packs.get(owner.pack)
		if not pack is Dictionary or not pack.get("frames") is Dictionary or not pack.get("pages") is Array:return "源图集结构变化"
		var frame=pack.frames.get(str(int(owner.index)))
		if not frame is Dictionary:return "源帧缺失：%s"%owner.index
		var page=frame.get("page")
		if not (page is int or page is float) or not is_finite(float(page)) or float(page)!=floorf(float(page)) or page<0 or page>=pack.pages.size():return "源图集页索引无效"
		var sf:Dictionary=owner.source_frame
		if frame.get("original")!=sf.original or frame.get("crop")!=sf.crop or frame.get("offset")!=sf.offset or frame.get("rect")!=sf.rect or page!=sf.page:return "源帧元数据变化：%s"%owner.index
		var atlas_page=pack.pages[int(page)]
		if not atlas_page is Dictionary or atlas_page.get("file")!=sf.atlas:return "源图集页变化"
	return ""

func prepare(id:String,source:Dictionary,objects:Array,packs:Dictionary,path:String=REGISTRATION) -> Dictionary:
	var reg=registration(path)
	if reg.is_empty():return {}
	if id not in ["pool","clump"]:return reject("静态物件分组无效")
	var group:Dictionary=reg.groups[id]
	var identity_error=identity_failure(group,source,objects,packs)
	if not identity_error.is_empty():return reject(identity_error)
	for pin in group.source_dependencies:
		if not file_available(pin.path) or FileAccess.get_sha256(pin.path)!=pin.sha256:return reject("静态物件依赖缺失或校验不符："+str(pin.path).get_file())
	# Exact map and complete manifest bind cells, flags and source frame metadata.
	var map_disk=JSON.parse_string(FileAccess.get_file_as_string(reg.source_map.path))
	var manifest_disk=JSON.parse_string(FileAccess.get_file_as_string(reg.source_manifest.path))
	if not map_disk is Dictionary or not source_matches(source,map_disk,group) or not manifest_disk is Dictionary or not manifest_disk.get("packs") is Dictionary or not atlas_matches(packs,manifest_disk.packs):return reject("运行时地图或图集身份变化")
	var image=Image.load_from_file(group.master.path)
	if image==null or image.is_empty() or image.get_size()!=Vector2i(group.master.width,group.master.height):return reject("静态物件完整母图解码失败")
	var texture=CanvasTexture.new()
	texture.diffuse_texture=ImageTexture.create_from_image(image)
	texture.texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR
	texture.texture_repeat=CanvasItem.TEXTURE_REPEAT_DISABLED
	var owners:Dictionary={}
	for record in group.owners:
		var r:Array=record.support_px_half_open
		var source_rect=Rect2(r[0],r[1],r[2]-r[0],r[3]-r[1])
		var world_origin=Vector2(group.world_origin[0],group.world_origin[1])
		owners[int(record.stable_source_order)]={"index":int(record.index),"pack":record.pack,"region":source_rect,"origin":world_origin+source_rect.position/float(group.density),"size":source_rect.size/float(group.density)}
	failure=""
	# Sole publication: return the complete group, never a partial owner dictionary.
	return {"texture":texture,"owners":owners,"contract":group,"registration":path}

func live_valid(group:Dictionary,source:Dictionary,objects:Array,packs:Dictionary,snapshot:Dictionary={}) -> bool:
	failure=""
	if group.is_empty():return false
	if not snapshot_file_available(group.registration,snapshot):failure="运行时静态物件注册缺失";return false
	for pin in group.contract.source_dependencies:
		if not snapshot_file_available(pin.path,snapshot):failure="运行时静态物件依赖缺失："+str(pin.path).get_file();return false
	failure=identity_failure(group.contract,source,objects,packs,snapshot)
	return failure.is_empty()

# Snapshot is local to ONE synchronous refresh; never stored or reused next tick.
func refresh_snapshot(groups:Array,objects:Array) -> Dictionary:
	var snapshot={"by_order":{},"first_invalid":-1,"available":{}}
	for group in groups:
		if not group is Dictionary or not group.get("contract") is Dictionary or not group.contract.get("owners") is Array:continue
		for owner in group.contract.owners:
			if not owner is Dictionary:continue
			var order=owner.get("stable_source_order")
			if (order is int or order is float) and is_finite(float(order)) and float(order)==floorf(float(order)):
				snapshot.by_order[int(order)]=[]
	if snapshot.by_order.is_empty():return snapshot
	var position=-1
	for entry in objects:
		position+=1
		if not entry is Dictionary:
			if snapshot.first_invalid<0:snapshot.first_invalid=position
			continue
		var order=entry.get("order")
		if order is float:
			if not is_finite(order) or order!=floorf(order):continue
			order=int(order)
		elif not order is int:continue
		if snapshot.by_order.has(order):
			snapshot.by_order[order].append({"entry":entry,"position":position})
	return snapshot

func snapshot_file_available(path:String,snapshot:Dictionary) -> bool:
	if snapshot.is_empty():return file_available(path)
	if not snapshot.available.has(path):snapshot.available[path]=file_available(path)
	return snapshot.available[path]

func source_matches(source:Dictionary,source_disk:Dictionary,_group:Dictionary) -> bool:
	return source==source_disk

func atlas_matches(runtime:Dictionary,original:Dictionary) -> bool:
	return runtime==original
