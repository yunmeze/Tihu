extends "res://scripts/earth/first_map_world.gd"
# Independent adapter for the prevalidated, detached map snapshot.
var snapshot: Dictionary = {}
const SHADOW_METHOD_SOURCE_SHA="c9139f34e1d57b1d33086c11157850454325c88078608fe13f8a081f7ddc07b2"
var source_methods_valid:=false
var ground_source_cells:Dictionary={}
var qualification=preload("res://scripts/earth/snapshot_receiver_qualification.gd").new()
func _init() -> void:
	super() # Retain first_map_world replacement of the inherited sample floor pass.
	# Optional host can exceed the original 768x512 review canvas. Preserve the
	# pinned compositor parent and replace only its draw-coverage subclass.
	shadow_compositor.free()
	shadow_compositor=preload("res://scripts/earth/viewport_ground_shadow.gd").new()
	review_guard=preload("res://scripts/earth/snapshot_ground_guard.gd").new()
	static_props_guard=preload("res://scripts/earth/snapshot_props_guard.gd").new()
	east_ground_guard=preload("res://scripts/earth/snapshot_east_guard.gd").new()
	plant_reuse_guard=preload("res://scripts/earth/snapshot_plant_guard.gd").new()
func _ready() -> void:
	super._ready()
	if s_idle_ready and s_idle_shadow_gate.matches_body(s_idle_texture.diffuse_texture):shadow_compositor.bind_s_body(s_idle_texture.diffuse_texture)
var _refresh_atlas_scope=false
var _refresh_atlas_ok=false
func qualifies(name:String) -> bool:
	var atlas_ok=_refresh_atlas_ok if _refresh_atlas_scope else snapshot_atlas_matches(packs,atlas_qualification.original)
	return source_methods_valid and atlas_ok and qualification.allows(name,map,objects)

func read_json(path: String) -> Dictionary:
	if path=="res://__map_load_snapshot__": return snapshot
	return super.read_json(path)
func setup_snapshot(actor: RefCounted, candidate: Dictionary) -> bool:
	atlas_qualification.resources_ready=false
	snapshot=candidate.duplicate(true)
	if not setup(actor,"res://__map_load_snapshot__"): return false
	for unit in map.get("added_units",[]):
		var manifest := read_json(unit.texture_manifest)
		if not manifest.get("packs") is Dictionary: return false
		if int(unit.definition_id)!=508 or not manifest.packs.has("Mon/220") or not manifest.packs["Mon/220"].frames.has("1"):
			loading_errors.append("Unsupported display adapter or missing chicken frame1")
			return false
		for name in manifest.packs:
			packs[name]=manifest.packs[name]
			for page in packs[name].pages: _load_texture(page.file)
		# Explicit display adapter: static source N idle frame1, reference alive layer1.
		objects.append({"pack":"Mon/220","index":1,"kind":9,"layer":1,"y":float(unit.y),"origin":Vector2(unit.x*48,unit.y*32),"order":int(map.width)*int(map.height)+map.npcs.size()+objects.size()})
	initialized=loading_errors.is_empty()
	if initialized: prepare_visuals()
	return initialized
func _draw_frame(pack_name: String,index: int,origin: Vector2,use_offset: bool,top: float) -> void:
	if pack_name.begins_with("Mon/"):
		super._draw_frame(pack_name,index,origin,true,0)
	else:
		super._draw_frame(pack_name,index,origin,use_offset,top)

const AtlasQualification=preload("res://scripts/earth/snapshot_atlas_qualification.gd")
var atlas_qualification=AtlasQualification.new()
func snapshot_atlas_matches(runtime:Dictionary,original:Dictionary) -> bool:
	return atlas_qualification.matches(runtime,original,map,objects)
var visual_ledger:Dictionary={}
var hit_images:Dictionary={}
func hit_image(raw:Texture2D):
	var key=raw.get_instance_id()
	if not hit_images.has(key):hit_images[key]=raw.get_image()
	return hit_images[key]
func prepare_visuals() -> void:
	atlas_qualification.prepare()
	xuyun_guard.atlas_validator=snapshot_atlas_matches
	prepare_xuyun()
	review_guard.atlas_validator=snapshot_atlas_matches
	static_props_guard.atlas_validator=snapshot_atlas_matches
	east_ground_guard.atlas_validator=snapshot_atlas_matches
	plant_reuse_guard.atlas_validator=snapshot_atlas_matches
	# Deliberately retain false: virtual snapshot is NOT an unchanged source file receiver proof.
	assert(not flat_map_bound)
	follow_actor=true
	source_methods_valid=FileAccess.get_sha256("res://scripts/earth/sample_world.gd")==SHADOW_METHOD_SOURCE_SHA
	qualification.prepare()
	prepare_idle();prepare_walk();prepare_e_idle();prepare_s_idle();prepare_e_walk()
	prepare_ground();prepare_east_ground();prepare_plant_reuse()
	prepare_static_props("pool");prepare_static_props("clump");prepare_hall();prepare_fangzhang();prepare_lingyunzi();prepare_tree();prepare_shrub()
	for i in 2:
		prepare_upright_group(i);prepare_translated_shrub(i);prepare_grass_group(i)
	for id in SouthCandidate.IDS:prepare_south_group(id)
	visual_ledger={"map":map.id,"ground":review_ground_owners.size(),"east_ground":east_ground_count(),"plant_instances":plant_reuse_groups.size(),"plant_owners":plant_reuse_owners.size(),"hall":hall_owners.size(),"fangzhang":fangzhang_texture!=null,"lingyunzi":lingyunzi_texture!=null,"e_walk":e_walk_frames.size(),"pool":static_props_count("pool"),"clump":static_props_count("clump"),"receiver":"per-caster closure AND original runtime gate","flat_map_bound":flat_map_bound}
	atlas_qualification.prepare_snapshot(packs,atlas_qualification.original,map,objects)
	qualification.prepare_snapshot(map,objects)

func candidate_item(entry:Dictionary) -> Dictionary:
	# Match the inherited draw precedence so generated plant alpha occludes NPC input.
	if prefer_plant_reuse and plant_reuse_owners.has(entry.order):
		var owner:Dictionary=plant_reuse_owners[entry.order]
		if owner.pack==entry.pack and owner.index==entry.index:return owner
	for id in ["pool","clump"]:
		if static_props_count(id)>0 and static_props_groups[id].owners.has(entry.order):
			var group:Dictionary=static_props_groups[id];var owner:Dictionary=group.owners[entry.order]
			if owner.pack==entry.pack and owner.index==entry.index:
				return {"texture":group.texture,"origin":owner.origin,"size":owner.size,"region":owner.region}
	for method in [south_item,upright_item,grass_item,translated_shrub_item]:
		var item:Dictionary=method.call(entry)
		if not item.is_empty():return item
	if uses_shrub(entry):return shrub_owners[entry.order]
	if uses_tree(entry):return tree_owners[entry.order]
	if prefer_hall and hall_owners.has(entry.order):
		var h:Dictionary=hall_owners[entry.order]
		if h.empty:return h
		return {"texture":h.texture,"origin":h.world_top_left,"size":h.texture.get_size()*h.scale}
	return {}

func alpha_hit(texture:Texture2D,point:Vector2,rect:Rect2,region:Rect2=Rect2()) -> bool:
	if not rect.has_point(point):return false
	var raw=texture.diffuse_texture if texture is CanvasTexture else texture
	var img=hit_image(raw)
	if region.size==Vector2.ZERO:region=Rect2(Vector2.ZERO,raw.get_size())
	var uv=region.position+(point-rect.position)/rect.size*region.size
	var pixel=uv-Vector2(0.5,0.5)
	var x=int(floor(pixel.x));var y=int(floor(pixel.y))
	var fx=pixel.x-x;var fy=pixel.y-y
	var a=img.get_pixel(clampi(x,0,img.get_width()-1),clampi(y,0,img.get_height()-1)).a
	var b=img.get_pixel(clampi(x+1,0,img.get_width()-1),clampi(y,0,img.get_height()-1)).a
	var c=img.get_pixel(clampi(x,0,img.get_width()-1),clampi(y+1,0,img.get_height()-1)).a
	var d=img.get_pixel(clampi(x+1,0,img.get_width()-1),clampi(y+1,0,img.get_height()-1)).a
	return lerpf(lerpf(a,b,fx),lerpf(c,d,fx),fy)>=0.1

func hit_test_npc(point:Vector2) -> int:
	refresh_xuyun()
	var entries=ordered_objects();entries.reverse()
	for entry in entries:
		if entry.kind==-1:continue
		var origin:Vector2=entry.origin+screen_origin()
		if uses_xuyun(entry):
			var body=xuyun_guard.descriptor()
			if alpha_hit(body.texture,point,Rect2(body.origin+screen_origin(),body.size),body.region):return body.npc_index
			continue
		if uses_lingyunzi(entry) or uses_fangzhang(entry):
			var ling=uses_lingyunzi(entry)
			var tex=lingyunzi_texture if ling else fangzhang_texture
			var region=Rect2((int(tick/17)%4)*512,0,512,640) if ling else Rect2()
			if alpha_hit(tex,point,Rect2(origin+Vector2(-32,-104),Vector2(128,160)),region):return int(entry.order)-int(map.width)*int(map.height)
			continue
		var item=candidate_item(entry)
		if not item.is_empty():
			if not item.get("empty",false) and alpha_hit(item.texture,point,Rect2(item.origin+screen_origin(),item.size),item.get("region",Rect2())):return -1
			continue
		var index:int=entry.index
		if entry.kind==7:index+=int(tick/17)%4
		elif entry.kind==5:index+=int(tick/8)%5
		elif entry.kind==8:
			var phase=int(tick/8)%10;index=55+(phase if phase<5 else 9-phase)
		var pack:Dictionary=packs[entry.pack]
		var frame:Dictionary=pack.frames.get(str(index),{})
		if frame.is_empty():continue
		var top=0.0 if entry.kind==7 or entry.pack.begins_with("Mon/") else (-52.0 if entry.kind==8 else 32.0-float(frame.original[1]))
		origin+=Vector2(frame.crop[0],frame.crop[1]+top)
		if entry.kind==7 or entry.pack.begins_with("Mon/"):origin+=Vector2(frame.offset[0],frame.offset[1])
		var local=point-origin
		if local.x<0 or local.y<0 or local.x>=frame.rect[2] or local.y>=frame.rect[3]:continue
		var img=hit_image(textures[pack.pages[int(frame.page)].file])
		var color=img.get_pixel(int(frame.rect[0]+local.x),int(frame.rect[1]+local.y))
		if color.a<0.1:continue
		if entry.kind==7 and color.r8==16 and color.g8==8 and color.b8==8:continue
		return int(entry.order)-int(map.width)*int(map.height) if entry.kind==7 else -1
	return -1

func refresh() -> void:
	# Atomic R6 staging has no viewport. Publish calls refresh synchronously after
	# add_child; prepare complete plant draw/hit descriptors without screen work.
	if not is_inside_tree():
		plant_reuse_owners.clear()
		if prefer_plant_reuse:
			for group in plant_reuse_groups.values():plant_reuse_owners.merge(group.owners)
		return
	_refresh_atlas_ok=snapshot_atlas_matches(packs,atlas_qualification.original)
	_refresh_atlas_scope=true
	qualification.begin_refresh_scope(map,objects)
	if atlas_qualification.resources_ready and not _refresh_atlas_ok:
		review_ground_owners.clear();review_ground_texture=null;validated_floor_stream.clear();ground_source_cells.clear()
		static_props_groups.clear()
		east_ground_group.clear();plant_reuse_groups.clear();plant_reuse_owners.clear()
		east_ground_error="Snapshot atlas closure invalid"
		plant_reuse_errors["snapshot"]="Snapshot atlas closure invalid"
		review_ground_error="Snapshot atlas closure invalid"
	if not review_ground_owners.is_empty():
		for order in ground_source_cells:
			if map.cells[order]!=ground_source_cells[order]:
				review_ground_owners.clear();review_ground_texture=null;validated_floor_stream.clear()
				review_ground_error="Snapshot ground owner cell changed; complete121 group withdrawn"
				break
	super.refresh()
	var frame=movement.source_frame()
	var body=s_idle_texture.diffuse_texture if s_idle_texture!=null else null
	var valid=prefer_shadow and qualifies("hero_s") and movement.action=="idle" and frame>=17 and frame<=20 and uses_candidate(frame) and s_idle_shadow_gate.matches_body(body) and s_idle_shadow_gate.allows(movement.position)
	shadow_compositor.set_s_contact(valid,body,movement.position*Vector2(48,32)+screen_origin()-Vector2(16,64),frame-17)
	qualification.end_refresh_scope()
	_refresh_atlas_scope=false;_refresh_atlas_ok=false

func update_left_upright_shadow() -> void:
	left_upright_shadow.clear_frame()
	if not prefer_shadow or not prefer_tree or not qualifies("left_upright") or not left_upright_gate.matches(map,objects,upright_groups[0]):return
	left_upright_shadow.prepare(left_upright_gate.texture,Vector2(2311.5555555555557,1030.6666666666667)+screen_origin())
func update_shadow() -> void:
	var frame=movement.source_frame()
	var supported=(movement.action=="idle" and frame>=13 and frame<=16) or (movement.action=="walk" and frame>=51 and frame<=56)
	var bound=supported and (walk_shadow_bound if movement.action=="walk" else idle_shadow_bound)
	if not prefer_shadow or not qualifies("hero_se") or not bound or not uses_candidate(frame) or not flat_gate.allows(movement.position):
		hero_shadow.clear_frame();return
	var walking=movement.action=="walk";var tex=walk_texture if walking else candidate_texture;var first=51 if walking else 13
	hero_shadow.configure_density_ground_frame(tex.diffuse_texture,Rect2i((frame-first)*128,0,128,128),4,Transform2D(0,movement.position*Vector2(48,32)+screen_origin()-Vector2(16,64)),Vector2(40,85.2463),-.342818,Vector2(1.2,.55),.25,.8)
func update_fangzhang_shadow() -> void:
	fangzhang_shadow.clear_frame()
	if not prefer_shadow or not qualifies("fangzhang") or not fangzhang_shadow_gate.ready or not prefer_npcs or fangzhang_texture==null:return
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
	if not prefer_shadow or not prefer_hall or not receiver_v2.hall_matches(map,objects,hall_owners):return
	if qualifies("lingyunzi") and receiver_v2.slots.lingyunzi and lingyunzi_texture!=null and lingyunzi_texture.diffuse_texture==receiver_v2.textures.get("lingyunzi"):
		var active=false
		for entry in objects:
			if uses_lingyunzi(entry):active=true;break
		if active:
			var c=receiver_v2.configuration.casters.lingyunzi;var s=c.shadow
			lingyunzi_shadow.configure_density_ground_frame(receiver_v2.textures.lingyunzi,Rect2i((int(tick/17)%4)*128,0,128,160),4,Transform2D(0,Vector2(c.world_body_origin[0],c.world_body_origin[1])+screen_origin()),Vector2(s.reference_logical[0],s.reference_logical[1]),s.slope,Vector2(1.2,.55),.25,.8)
	if qualifies("first_tree") and receiver_v2.slots.first_tree and tree_owners==receiver_v2.tree_prepared and tree_owners.size()==7:
		var found={}
		var duplicate=false
		for entry in objects:
			if uses_tree(entry):
				if found.has(entry.order):duplicate=true
				found[entry.order]=true
		if found.size()==7 and not duplicate:
			var c=receiver_v2.configuration.casters.first_tree;var s=c.shadow
			first_tree_shadow.configure_density_ground_frame(receiver_v2.textures.first_tree,Rect2i(0,0,314,314),4,Transform2D(0,Vector2(c.world_body_origin[0],c.world_body_origin[1])+screen_origin()),Vector2(s.reference_logical[0],s.reference_logical[1]),s.slope,Vector2(1.2,.55),.25,.8)

func prepare_ground(path:String=ReviewGuard.REGISTRATION) -> bool:
	var prepared_ok=super.prepare_ground(path)
	ground_source_cells.clear()
	if prepared_ok:
		for order in review_ground_owners:ground_source_cells[order]=map.cells[order].duplicate()
	return prepared_ok
