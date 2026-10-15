extends "res://scripts/world_view.gd"
const SAMPLE_RECT=Rect2(2496,960,768,512)
var follow_actor:=false
var flat_map_bound:=false
func setup(actor:RefCounted,map_path:String="res://data/maps/A13.json") -> bool:
	candidate_texture=null;candidate_ready=false;walk_texture=null;walk_ready=false;e_idle_texture=null;e_idle_ready=false;s_idle_texture=null;s_idle_ready=false;idle_shadow_bound=false;walk_shadow_bound=false
	fangzhang_texture=null;lingyunzi_texture=null;tree_owners={};shrub_owners={};hall_owners={};ground_owners={};upright_groups=[{},{}];translated_shrub_groups=[{},{}];grass_groups=[{},{}]
	hero_shadow.clear_frame();fangzhang_shadow.clear_frame();fangzhang_shadow_gate.ready=false
	lingyunzi_shadow.clear_frame();first_tree_shadow.clear_frame();shadow_compositor.clear_frame();receiver_v2.reset();left_upright_shadow.clear_frame();left_upright_gate.reset();s_idle_shadow_gate.reset()
	flat_map_bound=false
	var ok=super.setup(actor,map_path)
	flat_map_bound=ok and map_path=="res://data/maps/A13.json" and FileAccess.get_sha256(map_path)=="d09549838963c8157307cc5406d3118baf69259d82459bcba0a3a8be5b34aa27"
	return ok
func screen_origin() -> Vector2:
	return get_viewport_rect().size*.5-movement.position*Vector2(48,32) if follow_actor else -SAMPLE_RECT.position

const Guard=preload("res://scripts/earth/asset_guard.gd")
var prefer_candidate:=true
var candidate_ready:=false
var idle_shadow_bound:=false
var walk_shadow_bound:=false
var candidate_texture:CanvasTexture
var candidate_error:="not prepared"

static func exact_numbers(value:Variant,expected:Array) -> bool:
	if not value is Array or value.size()!=expected.size():return false
	for i in expected.size():
		if not Guard.number(value[i],-16384,16384) or value[i]!=expected[i]:return false
	return true

func prepare_actor_group(path:String,first:int,count:int,phase_ticks:int) -> CanvasTexture:
	if not FileAccess.file_exists(path):return null
	var parser=JSON.new()
	if parser.parse(FileAccess.get_file_as_string(path))!=OK or not parser.data is Dictionary:return null
	var reg:Dictionary=parser.data
	var ids=[]
	for i in count:ids.append(first+i)
	if not Guard.integer(reg.get("texture_density"),4,4) or not Guard.integer(reg.get("frame_ticks"),phase_ticks,phase_ticks):return null
	if not exact_numbers(reg.get("texture_size"),[count*512,512]) or not exact_numbers(reg.get("logical_frame_size"),[128,128]) or not exact_numbers(reg.get("logical_draw_offset"),[-16,-64]) or not exact_numbers(reg.get("source_ids"),ids):return null
	if not reg.get("records") is Array or reg.records.size()!=count:return null
	for i in count:
		var record=reg.records[i]
		if not record is Dictionary or not Guard.integer(record.get("source_id"),first+i,first+i) or not exact_numbers(record.get("region_px"),[i*512,0,512,512]):return null
	var tex=Guard.texture(reg.get("texture"),reg.get("texture_size"),reg.get("texture_sha256"))
	if tex==null:return null
	var prepared=CanvasTexture.new();prepared.diffuse_texture=tex;prepared.texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR
	return prepared
func prepare_idle(path:String="res://assets/earth/hero/se_idle_v1/manifest.json") -> bool:
	candidate_texture=prepare_actor_group(path,13,4,12)
	candidate_ready=candidate_texture!=null
	idle_shadow_bound=candidate_ready and path=="res://assets/earth/hero/se_idle_v1/manifest.json" and FileAccess.get_sha256(path)=="3672409856c27b1e81d543b8a0a29063e16170b2cafbaf55f5d6351fb1e9b5a3"
	candidate_error="" if candidate_ready else "missing or invalid four-frame candidate"
	return candidate_ready
var walk_texture:CanvasTexture
var walk_ready:=false
func prepare_walk(path:String="res://assets/earth/hero/se_walk_v1/manifest.json") -> bool:
	walk_texture=prepare_actor_group(path,51,6,7);walk_ready=walk_texture!=null
	walk_shadow_bound=walk_ready and path=="res://assets/earth/hero/se_walk_v1/manifest.json" and FileAccess.get_sha256(path)=="127727940bd2651460bbe90396f80e7c75d89a7d8675f5d3467e5a5f46e229d7"
	return walk_ready
var e_idle_texture:CanvasTexture
var e_idle_ready:=false
func prepare_e_idle(path:Variant="res://assets/earth/hero/e_idle_v1/manifest.json") -> bool:
	e_idle_texture=null;e_idle_ready=false
	if not path is String or not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!="8c24bc9430c293a30b1ed0f699a6e3be1390c297e434259dd6b60c4fe39b2025":return false
	if not FileAccess.file_exists("res://assets/earth/hero/e_idle_v1/body.png"):return false
	e_idle_texture=prepare_actor_group(path,9,4,12);e_idle_ready=e_idle_texture!=null
	return e_idle_ready
var s_idle_texture:CanvasTexture
var s_idle_ready:=false
func prepare_s_idle(path:Variant="res://assets/earth/hero/s_idle_v1/manifest.json") -> bool:
	s_idle_texture=null;s_idle_ready=false
	if not path is String or not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!="cfd74e66ddb74fb4ce8fc46be747f6df9b8037713044b76a287baef343654b80":return false
	if not FileAccess.file_exists("res://assets/earth/hero/s_idle_v1/body.png"):return false
	s_idle_texture=prepare_actor_group(path,17,4,12);s_idle_ready=s_idle_texture!=null
	if s_idle_ready and s_idle_shadow_gate.matches_body(s_idle_texture.diffuse_texture):shadow_compositor.bind_s_body(s_idle_texture.diffuse_texture)
	return s_idle_ready
func uses_candidate(index:int) -> bool:
	if not prefer_candidate:return false
	return (s_idle_ready and movement.action=="idle" and index>=17 and index<=20) or (e_idle_ready and movement.action=="idle" and index>=9 and index<=12) or (candidate_ready and movement.action=="idle" and index>=13 and index<=16) or (walk_ready and movement.action=="walk" and index>=51 and index<=56)
func _draw_hero(origin:Vector2,index:int) -> void:
	if uses_candidate(index):
		var walking=movement.action=="walk"
		var eastern=not walking and index>=9 and index<=12
		var southern=not walking and index>=17 and index<=20
		var atlas=s_idle_texture if southern else (e_idle_texture if eastern else (walk_texture if walking else candidate_texture))
		var first=17 if southern else (9 if eastern else (51 if walking else 13))
		draw_texture_rect_region(atlas,Rect2(origin-Vector2(16,64),Vector2(128,128)),Rect2((index-first)*512,0,512,512))
	else:super._draw_hero(origin,index)

const Ground=preload("res://scripts/earth/ground_candidate.gd")
var prefer_ground:=true
var ground_owners:Dictionary={}
func prepare_ground(path:String="res://assets/earth/environment/ground_plate_v4/registration.json") -> bool:
	# One publication point; invalid preparation restores all 64 source owners.
	ground_owners=Ground.read_prepare(path,map)
	queue_redraw()
	return ground_owners.size()==64
func _draw_frame(pack_name:String,index:int,origin:Vector2,use_offset:bool,top:float) -> void:
	if prefer_hall and hall_owners.size()==30 and pack_name==Hall.PACK:
		var cell=(origin-screen_origin())/Vector2(48,32)
		var order=roundi(cell.x)*100+roundi(cell.y)
		if hall_owners.has(order):
			var item=hall_owners[order]
			if not item.empty:draw_texture_rect(item.texture,Rect2(item.world_top_left+screen_origin(),item.texture.get_size()*item.scale),false)
			return
	if prefer_ground and ground_owners.size()==64 and pack_name==Ground.PACK:
		var cell=(origin-screen_origin())/Vector2(48,32)
		var order=roundi(cell.x)*100+roundi(cell.y)
		if ground_owners.has(order):
			var item=ground_owners[order]
			draw_texture_rect(item.texture,Rect2(item.world_top_left+screen_origin(),Vector2(96,64)),false)
			return
	super._draw_frame(pack_name,index,origin,use_offset,top)

const InstanceIdentity=preload("res://scripts/earth/instance_identity_guard.gd")
const ShrubCandidate=preload("res://scripts/earth/shrub_candidate.gd")
var prefer_shrub:=true
var shrub_owners:Dictionary={}
func prepare_shrub(path:Variant=ShrubCandidate.PATH) -> bool:
	shrub_owners=ShrubCandidate.prepare(path,map);queue_redraw();return shrub_owners.size()==4
func uses_shrub(entry:Variant) -> bool:
	if not entry is Dictionary:return false
	if not prefer_shrub or shrub_owners.size()!=4:return false
	var order=entry.get("order")
	if not Guard.integer(order,0,9999):return false
	order=int(order)
	if not shrub_owners.has(order):return false
	return InstanceIdentity.entry(entry,2,"Map/Res/Plant",shrub_owners[order].index,1,order%100,order,Vector2(order/100,order%100)*Vector2(48,32))

const TranslatedShrub=preload("res://scripts/earth/translated_shrub_candidate.gd")
var translated_shrub_groups:Array=[{},{}]
func prepare_translated_shrub(instance:Variant,path:Variant=null) -> bool:
	if not Guard.integer(instance,0,1):return false
	var n=int(instance)
	if path==null:path=TranslatedShrub.PATHS[n]
	translated_shrub_groups[n]=TranslatedShrub.prepare(n,path,map);queue_redraw();return translated_shrub_groups[n].size()==4
func translated_shrub_item(entry:Variant) -> Dictionary:
	if not entry is Dictionary or not prefer_shrub:return {}
	var order=entry.get("order")
	if not Guard.integer(order,0,9999):return {}
	order=int(order)
	for group in translated_shrub_groups:
		if group.size()!=4 or not group.has(order):continue
		var item=group[order]
		if InstanceIdentity.entry(entry,2,"Map/Res/Plant",item.index,1,order%100,order,Vector2(order/100,order%100)*Vector2(48,32)):return item
	return {}

const GrassCandidate=preload("res://scripts/earth/grass_candidate.gd")
var prefer_grass:=true
var grass_groups:Array=[{},{}]
func prepare_grass_group(instance:Variant,path:Variant=null) -> bool:
	if not Guard.integer(instance,0,1):return false
	var n=int(instance)
	if path==null:path=GrassCandidate.PATHS[n]
	grass_groups[n]=GrassCandidate.prepare(n,path,map);queue_redraw();return grass_groups[n].size()==2
func grass_item(entry:Variant) -> Dictionary:
	if not entry is Dictionary or not prefer_grass:return {}
	var order=entry.get("order")
	if not Guard.integer(order,0,9999):return {}
	order=int(order)
	for group in grass_groups:
		if group.size()!=2 or not group.has(order):continue
		var item=group[order]
		if InstanceIdentity.entry(entry,2,"Map/Res/Plant",item.index,1,order%100,order,Vector2(order/100,order%100)*Vector2(48,32)):return item
	return {}

const TreeCandidate=preload("res://scripts/earth/tree_candidate.gd")
var prefer_tree:=true
var tree_owners:Dictionary={}
func prepare_tree(path:Variant=TreeCandidate.PATH) -> bool:
	tree_owners=TreeCandidate.prepare(path,map);queue_redraw();return tree_owners.size()==7
func uses_tree(entry:Variant) -> bool:
	if not entry is Dictionary:return false
	if not prefer_tree or tree_owners.size()!=7:return false
	var order=entry.get("order")
	if not Guard.integer(order,0,9999):return false
	order=int(order)
	if not tree_owners.has(order):return false
	return InstanceIdentity.entry(entry,2,"Map/Res/Plant",tree_owners[order].index,1,order%100,order,Vector2(order/100,order%100)*Vector2(48,32))

const UprightCandidate=preload("res://scripts/earth/upright_candidate.gd")
var upright_groups:Array=[{},{}]
func prepare_upright_group(instance:Variant,path:Variant=null) -> bool:
	if not Guard.integer(instance,0,1):return false
	var n=int(instance)
	if path==null:path=UprightCandidate.PATHS[n]
	upright_groups[n]=UprightCandidate.prepare(n,path,map);queue_redraw();return upright_groups[n].size()==6
func upright_item(entry:Variant) -> Dictionary:
	if not entry is Dictionary or not prefer_tree:return {}
	var order=entry.get("order")
	if not Guard.integer(order,0,9999):return {}
	order=int(order)
	for group in upright_groups:
		if group.size()!=6 or not group.has(order):continue
		var item=group[order]
		if InstanceIdentity.entry(entry,2,"Map/Res/Plant",item.index,1,order%100,order,Vector2(order/100,order%100)*Vector2(48,32)):return item
	return {}

const Lingyunzi=preload("res://scripts/earth/lingyunzi_candidate.gd")
var lingyunzi_texture:CanvasTexture
func prepare_lingyunzi(path:Variant=Lingyunzi.PATH) -> bool:
	lingyunzi_texture=Lingyunzi.prepare(path,map);queue_redraw();return lingyunzi_texture!=null
func uses_lingyunzi(entry:Variant) -> bool:
	return prefer_npcs and lingyunzi_texture!=null and Lingyunzi.matches(entry)

const Fangzhang=preload("res://scripts/earth/fangzhang_candidate.gd")
var prefer_npcs:=true
# Compatibility property for the earlier single-NPC candidate; N now controls both.
var prefer_fangzhang:bool:
	get:return prefer_npcs
	set(value):prefer_npcs=value
var fangzhang_texture:CanvasTexture
func prepare_fangzhang(path:Variant=Fangzhang.PATH) -> bool:
	fangzhang_texture=Fangzhang.prepare(path,map)
	queue_redraw()
	return fangzhang_texture!=null
func uses_fangzhang(entry:Variant) -> bool:
	return prefer_fangzhang and fangzhang_texture!=null and Fangzhang.matches(entry)

const Hall=preload("res://scripts/earth/hall_candidate.gd")
var prefer_hall:=true
var hall_owners:Dictionary={}
func prepare_hall(path:String="res://assets/earth/environment/training_hall_v1/registration.json") -> bool:
	hall_owners=Hall.read_prepare(path,map)
	queue_redraw()
	return hall_owners.size()==30


# Explicit flat-ground pass: floors -> one candidate shadow -> original objects.
const DensityShadow=preload("res://scripts/art/density_alpha_ground_shadow.gd")
var floor_pass=preload("res://scripts/earth/sample_floor_pass.gd").new()
var flat_gate=preload("res://scripts/earth/flat_shadow_gate.gd").new()
var hero_shadow=DensityShadow.new()
var fangzhang_shadow=DensityShadow.new()
var fangzhang_shadow_gate=preload("res://scripts/earth/fangzhang_shadow_gate.gd").new()
var prefer_shadow:=true
var lingyunzi_shadow=DensityShadow.new()
var first_tree_shadow=DensityShadow.new()
var receiver_v2=preload("res://scripts/earth/receiver_v2_gate.gd").new()
var left_upright_shadow=preload("res://scripts/earth/raw_ground_shadow.gd").new()
var left_upright_gate=preload("res://scripts/earth/left_upright_shadow_gate.gd").new()
var s_idle_shadow_gate=preload("res://scripts/earth/s_idle_shadow_gate.gd").new()
var shadow_compositor=preload("res://scripts/earth/max_ground_shadow.gd").new()
func _ready():
	floor_pass.world=self;floor_pass.z_index=-2;floor_pass.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST;add_child(floor_pass)
	hero_shadow.z_index=-1;add_child(hero_shadow)
	fangzhang_shadow.z_index=-1;add_child(fangzhang_shadow)
	flat_gate.prepare();fangzhang_shadow_gate.prepare()
	lingyunzi_shadow.z_index=-1;add_child(lingyunzi_shadow)
	first_tree_shadow.z_index=-1;add_child(first_tree_shadow)
	add_child(left_upright_shadow);left_upright_gate.prepare(map)
	add_child(shadow_compositor);shadow_compositor.prepare();receiver_v2.prepare(map);s_idle_shadow_gate.prepare()
func refresh() -> void:
	super.refresh();floor_pass.queue_redraw();update_shadow();update_fangzhang_shadow();update_receiver_shadows();update_left_upright_shadow()
	shadow_compositor.configure([hero_shadow,fangzhang_shadow,lingyunzi_shadow,first_tree_shadow,left_upright_shadow])
	var s_frame=movement.source_frame()
	var s_body=s_idle_texture.diffuse_texture if s_idle_texture!=null else null
	var s_valid=prefer_shadow and flat_map_bound and movement.action=="idle" and s_frame>=17 and s_frame<=20 and uses_candidate(s_frame) and s_idle_shadow_gate.matches_body(s_body) and s_idle_shadow_gate.allows(movement.position)
	shadow_compositor.set_s_contact(s_valid,s_body,movement.position*Vector2(48,32)+screen_origin()-Vector2(16,64),s_frame-17)
	# Descriptor helpers retain configurations, never their old draw pass.
	for node in [hero_shadow,fangzhang_shadow,lingyunzi_shadow,first_tree_shadow,left_upright_shadow]:node.visible=false
func update_left_upright_shadow() -> void:
	left_upright_shadow.clear_frame()
	if not prefer_shadow or not prefer_tree or not flat_map_bound or not left_upright_gate.matches(map,objects,upright_groups[0]):return
	left_upright_shadow.prepare(left_upright_gate.texture,Vector2(2311.5555555555557,1030.6666666666667)+screen_origin())
func update_shadow() -> void:
	var frame=movement.source_frame()
	var supported=(movement.action=="idle" and frame>=13 and frame<=16) or (movement.action=="walk" and frame>=51 and frame<=56)
	var bound=supported and (walk_shadow_bound if movement.action=="walk" else idle_shadow_bound)
	if not prefer_shadow or not flat_map_bound or not bound or not uses_candidate(frame) or not flat_gate.allows(movement.position):
		hero_shadow.clear_frame();return
	var walking=movement.action=="walk";var tex=walk_texture if walking else candidate_texture;var first=51 if walking else 13
	hero_shadow.configure_density_ground_frame(tex.diffuse_texture,Rect2i((frame-first)*128,0,128,128),4,Transform2D(0,movement.position*Vector2(48,32)+screen_origin()-Vector2(16,64)),Vector2(40,85.2463),-.342818,Vector2(1.2,.55),.25,.8)
func update_fangzhang_shadow() -> void:
	fangzhang_shadow.clear_frame()
	if not prefer_shadow or not flat_map_bound or not fangzhang_shadow_gate.ready or not prefer_npcs or fangzhang_texture==null:return
	var active_body=false
	for entry in objects:
		if uses_fangzhang(entry):active_body=true;break
	if not active_body:return
	# Only the source-bound record0 body can prepare; its position never follows hero.
	var r=fangzhang_shadow_gate.configuration
	var s=r.shadow
	fangzhang_shadow.configure_density_ground_frame(fangzhang_texture.diffuse_texture,Rect2i(0,0,128,160),4,Transform2D(0,Vector2(3040,1080)+screen_origin()),Vector2(s.reference_logical[0],s.reference_logical[1]),s.slope,Vector2(1.2,.55),.25,.8)
func update_receiver_shadows() -> void:
	lingyunzi_shadow.clear_frame();first_tree_shadow.clear_frame()
	if not prefer_shadow or not flat_map_bound or not prefer_hall or not receiver_v2.hall_matches(map,objects,hall_owners):return
	if receiver_v2.slots.lingyunzi and lingyunzi_texture!=null and lingyunzi_texture.diffuse_texture==receiver_v2.textures.get("lingyunzi"):
		var active=false
		for entry in objects:
			if uses_lingyunzi(entry):active=true;break
		if active:
			var c=receiver_v2.configuration.casters.lingyunzi;var s=c.shadow
			lingyunzi_shadow.configure_density_ground_frame(receiver_v2.textures.lingyunzi,Rect2i((int(tick/17)%4)*128,0,128,160),4,Transform2D(0,Vector2(c.world_body_origin[0],c.world_body_origin[1])+screen_origin()),Vector2(s.reference_logical[0],s.reference_logical[1]),s.slope,Vector2(1.2,.55),.25,.8)
	if receiver_v2.slots.first_tree and tree_owners==receiver_v2.tree_prepared and tree_owners.size()==7:
		var found={}
		var duplicate=false
		for entry in objects:
			if uses_tree(entry):
				if found.has(entry.order):duplicate=true
				found[entry.order]=true
		if found.size()==7 and not duplicate:
			var c=receiver_v2.configuration.casters.first_tree;var s=c.shadow
			first_tree_shadow.configure_density_ground_frame(receiver_v2.textures.first_tree,Rect2i(0,0,314,314),4,Transform2D(0,Vector2(c.world_body_origin[0],c.world_body_origin[1])+screen_origin()),Vector2(s.reference_logical[0],s.reference_logical[1]),s.slope,Vector2(1.2,.55),.25,.8)
func _draw() -> void:
	if not initialized:return
	var offset=screen_origin()
	for entry in ordered_objects():
		if entry.kind==-1:
			_draw_hero(movement.position*Vector2(48,32)+offset,movement.source_frame());continue
		var upright=upright_item(entry)
		if not upright.is_empty():
			if not upright.empty:draw_texture_rect(upright.texture,Rect2(upright.origin+offset,upright.size),false)
			continue
		var grass=grass_item(entry)
		if not grass.is_empty():
			draw_texture_rect(grass.texture,Rect2(grass.origin+offset,grass.size),false)
			continue
		var extra_shrub=translated_shrub_item(entry)
		if not extra_shrub.is_empty():
			draw_texture_rect(extra_shrub.texture,Rect2(extra_shrub.origin+offset,extra_shrub.size),false)
			continue
		if uses_shrub(entry):
			var item=shrub_owners[entry.order]
			draw_texture_rect(item.texture,Rect2(item.origin+offset,item.size),false)
			continue
		if uses_tree(entry):
			var item=tree_owners[entry.order]
			if not item.empty:draw_texture_rect(item.texture,Rect2(item.origin+offset,item.size),false)
			continue
		if uses_lingyunzi(entry):
			var phase:int=(tick/17)%4
			draw_texture_rect_region(lingyunzi_texture,Rect2(entry.origin+offset+Vector2(-32,-104),Vector2(128,160)),Rect2(phase*512,0,512,640))
			continue
		if uses_fangzhang(entry):
			draw_texture_rect(fangzhang_texture,Rect2(entry.origin+offset+Vector2(-32,-104),Vector2(128,160)),false)
			continue
		var index:int=entry.index
		if entry.kind==7:index+=(tick/17)%4
		elif entry.kind==5:index+=(tick/8)%5
		elif entry.kind==8:
			var phase:int=(tick/8)%10;index=55+(phase if phase<5 else 9-phase)
		var frame:Dictionary=packs[entry.pack].frames.get(str(index),{})
		if frame.is_empty():continue
		var top=0.0 if entry.kind==7 else (-52.0 if entry.kind==8 else 32.0-float(frame.original[1]))
		_draw_frame(entry.pack,index,entry.origin+offset,entry.kind==7,top)
	if show_grid:
		for x in range(-12,13):
			for y in range(-13,14):
				var cell=Vector2i(roundi(camera.x)+x,roundi(camera.y)+y)
				if not movement.can_enter(cell):draw_rect(Rect2(Vector2(cell)*Vector2(48,32)+offset,Vector2(48,32)),Color(1,0,0,.18))
