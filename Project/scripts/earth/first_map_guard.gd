extends RefCounted
## This loader is intentionally confined to the frozen research registration.
const REGISTRATION="res://assets/earth/first_map_review/registration.json"
const REGISTRATION_SHA256="666eed5d3ea4f348999de1af1dc870c6e914c7333693c28ab088fe12c45034ea"
var failure:=""
func numbers(value:Array,expected:Array) -> bool:
	if value.size()!=expected.size():return false
	for i in value.size():
		if value[i]!=expected[i]:return false
	return true
func reject(reason:String) -> Dictionary:
	failure=reason
	return {}
func registration(path:String) -> Dictionary:
	failure=""
	if path!=REGISTRATION or not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=REGISTRATION_SHA256:
		return reject("注册文件缺失或校验不符")
	var reg=JSON.parse_string(FileAccess.get_file_as_string(path))
	if not reg is Dictionary or reg.get("schema")!="earth-first-map-research-review-v1":return reject("注册结构无效")
	return reg
func checked_image(path:String,digest:String,size:Vector2i) -> Image:
	if not path.begins_with("res://art_source/") or ".." in path or not path.ends_with(".png"):
		failure="研究图像路径无效";return null
	if not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=digest:
		failure="图像缺失或校验不符："+path;return null
	var image=Image.load_from_file(path)
	if image==null or image.is_empty() or image.get_size()!=size:
		failure="图像尺寸或解码无效："+path;return null
	return image
func canvas_texture(image:Image) -> CanvasTexture:
	var texture=CanvasTexture.new()
	texture.diffuse_texture=ImageTexture.create_from_image(image)
	texture.texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR
	return texture
func prepare_e_walk(path:String=REGISTRATION) -> Array:
	var reg=registration(path)
	if reg.is_empty():return []
	var actor=reg.actor
	if not numbers(actor.frame_ids,[45,46,47,48,49,50]) or not numbers(actor.logical_size,[128,128]) or not numbers(actor.logical_root,[16,64]) or actor.frame_ticks!=7 or actor.density!=4 or actor.frames.size()!=6:
		failure="E 步行注册范围无效";return []
	var staged:Array=[]
	for i in 6:
		var frame=actor.frames[i]
		if frame.id!=45+i or not numbers(frame.size,[512,512]):failure="E 步行相位无效";return []
		var image=checked_image(frame.path,frame.sha256,Vector2i(512,512))
		if image==null:return []
		staged.append(canvas_texture(image))
	return staged
func prepare_ground(path:String,source:Dictionary,packs:Dictionary,floors:Array) -> Dictionary:
	var reg=registration(path)
	if reg.is_empty():return {}
	for pin in [reg.source_map,reg.source_manifest]:
		if not FileAccess.file_exists(pin.path) or FileAccess.get_sha256(pin.path)!=pin.sha256:return reject("原版地图或图集校验不符")
	var source_disk=JSON.parse_string(FileAccess.get_file_as_string(reg.source_map.path))
	var manifest_disk=JSON.parse_string(FileAccess.get_file_as_string(reg.source_manifest.path))
	if not source_disk is Dictionary or not manifest_disk is Dictionary or not manifest_disk.get("packs") is Dictionary:return reject("Pinned source JSON structure invalid")
	if not source_matches(source,source_disk) or not atlas_matches(packs,manifest_disk.packs):return reject("运行时地图或图集身份变化")
	var stream=reg.floor_stream.records
	if floors.size()!=2553 or stream.size()!=floors.size():return reject("完整地面序列长度变化")
	for i in floors.size():
		var expected=stream[i];var actual=floors[i]
		if actual.size()!=3 or actual.get("pack")!=expected.pack or actual.get("index")!=expected.index or actual.get("origin")!=Vector2(expected.origin[0],expected.origin[1]):return reject("完整地面序列身份或顺序变化")
	var ground=reg.ground
	if ground.owner_count!=121 or ground.owners.size()!=121 or not numbers(ground.texture_size,[1728,1920]) or ground.density!=2 or not numbers(ground.world_bounds_xyxy_half_open,[2400,960,3264,1920]):return reject("地面注册范围无效")
	var image=checked_image(ground.texture,ground.texture_sha256,Vector2i(1728,1920))
	if image==null:return {}
	var staged:Dictionary={};var previous=-1
	for owner in ground.owners:
		var order=int(owner.stable_source_order)
		if order<=previous or staged.has(order):return reject("地块重复或顺序变化")
		previous=order
		var cell=owner.cell
		if order!=int(cell[0])*100+int(cell[1]) or source.cells[order]!=owner.source_cell or source.cells[order][1]!=owner.source_flag:return reject("地块源单元变化")
		var f=floors[int(owner.floor_stream_index)]
		if f.pack!=owner.pack or f.index!=owner.frame_index or f.origin!=Vector2(owner.world_origin[0],owner.world_origin[1]):return reject("地块源身份变化")
		var frame=packs[owner.pack].frames[str(int(owner.frame_index))]
		if frame.crop!=owner.crop or frame.rect!=owner.atlas_rect or frame.original!=owner.original_size or packs[owner.pack].pages[int(frame.page)].file!=owner.atlas_page:return reject("地块图集裁切变化")
		var region=owner.shared_region_px
		if not numbers(region,[2*(owner.world_origin[0]-2400),2*(owner.world_origin[1]-960),192,128]):return reject("共享图像区域变化")
		staged[order]={"origin":f.origin,"region":Rect2(region[0],region[1],region[2],region[3])}
	return {"owners":staged,"texture":canvas_texture(image)}

func source_matches(source:Dictionary,source_disk:Dictionary) -> bool:
	return source==source_disk

func atlas_matches(runtime:Dictionary,original:Dictionary) -> bool:
	return runtime==original
