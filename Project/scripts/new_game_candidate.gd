extends "res://scripts/opening_candidate.gd"
## Natural-button bounded opening. Authority owns exactly one inventory.
const ResourceCheck=preload("res://scripts/world_resource_preflight.gd")
const Profile=preload("res://scripts/core/default_warrior.gd")
const LoadBridge=preload("res://scripts/core/map_load_bridge.gd")
const LoadedWorld=preload("res://scripts/map_load_world.gd")
const MAPS={"A13":"res://data/maps/A13.json","A00":"res://data/maps/A00.json"}
const POLICY={"max_weight":25,"equipment_slots":["helmet","necklace","armor","boots","braceletLeft","braceletRight","ringLeft","ringRight","shield","weapon"],"weight_locations":["bag","equipment"]}
var authority:Dictionary={}
var rng_state:Dictionary={}
var rng_provider
var consumed_total:int:
	get:return int(rng_state.get("cursor",0))
var cloth:Dictionary={}
var monster_registry:Dictionary={}
var opening_data:Dictionary={}
var opening_page:=-1
var preparing:=false
var pending_creation:Dictionary={}
var creation_count:=0
var map_load_count:=0
var dialog_background=TextureRect.new()
var overlay=Panel.new()
var opening_text=Label.new()
var page_title=Label.new()
var previous_button=Button.new()
var next_button=Button.new()
var start_button=Button.new()
var resource_preflight_override:Callable=Callable()
func _ready() -> void:
	build_candidate_ui()
	world.hide()
	var layer=CanvasLayer.new()
	layer.layer=2
	add_child(layer)
	layer.add_child(overlay)
	overlay.position=Vector2(132,100)
	overlay.size=Vector2(760,560)
	overlay.mouse_filter=Control.MOUSE_FILTER_STOP
	var font=paragraph.get_theme_font("font")
	for label in [page_title,opening_text]:
		label.add_theme_font_override("font",font)
		label.mouse_filter=Control.MOUSE_FILTER_IGNORE
		overlay.add_child(label)
	page_title.position=Vector2(35,24)
	page_title.add_theme_font_size_override("font_size",26)
	opening_text.position=Vector2(40,90)
	opening_text.size=Vector2(680,350)
	opening_text.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	opening_text.add_theme_font_size_override("font_size",23)
	for button in [previous_button,next_button,start_button]:
		button.add_theme_font_override("font",font)
		button.add_theme_font_size_override("font_size",21)
		button.size=Vector2(200,48)
		overlay.add_child(button)
	previous_button.position=Vector2(40,480)
	next_button.position=Vector2(520,480)
	start_button.position=Vector2(280,465)
	previous_button.text="上一页"
	previous_button.pressed.connect(advance_opening.bind(-1))
	next_button.pressed.connect(advance_opening.bind(1))
	start_button.text="踏入江湖 · 创建角色"
	start_button.pressed.connect(start_new_game)
	previous_button.hide()
	next_button.hide()
	page_title.text="普通战士 · 新游戏候选"
	opening_text.text="按原数据创建新角色，阅读五页前世今生，再进入原双NPC剧情。\n\n随机抽样采用明确标记的兼容算法，尚未复原原VB随机序列。\n\n当前范围到海曦村首房，无保存、战斗或怪物AI。"
	_update_status()
func resources(definition:Dictionary) -> bool:
	if resource_preflight_override.is_valid():return resource_preflight_override.call(definition)
	var file=definition.get("texture_manifest","")
	if not file is String:return false
	return ResourceCheck.manifest(file).ok

func start_new_game() -> bool:
	if preparing or not authority.is_empty():return false
	preparing=true
	var inputs=prepare_inputs()
	if not inputs.ok:
		preparing=false
		return reject(inputs.error)
	if not ResourceLoader.exists("res://scripts/core/compat_rng.gd"):
		preparing=false
		return reject("兼容随机模块尚未就绪")
	rng_provider=load("res://scripts/core/compat_rng.gd")
	if pending_creation.is_empty():
		var entropy=Crypto.new().generate_random_bytes(16)
		var stream="new."+entropy.hex_encode()
		var random_created=rng_provider.create(stream,entropy.decode_s64(0))
		if not random_created.ok:
			preparing=false
			return reject(str(random_created))
		var created=Profile.create(stream,cloth,POLICY)
		if not created.ok:
			preparing=false
			return reject(str(created))
		pending_creation={"state":created.state,"rng":random_created.state}
	var staged=prepare_map(pending_creation.state,"A13",[61,39],false,pending_creation.rng)
	if not staged.ok:
		preparing=false
		return reject(staged.error)
	publish(staged)
	pending_creation={}
	creation_count+=1
	opening_page=0
	start_button.hide()
	show_opening()
	_update_status()
	preparing=false
	return true
func prepare_map(candidate_authority:Dictionary,map_id:String,cell:Array,next_stop:bool,base_rng:Dictionary) -> Dictionary:
	var views=Profile.project(candidate_authority,cloth,POLICY)
	if not views.ok:return {"ok":false,"error":str(views)}
	if not MAPS.has(map_id):return {"ok":false,"error":"Unsupported map"}
	var source_result=ResourceCheck.read(MAPS[map_id])
	if not source_result.ok:return source_result
	var source=source_result.value
	if not source.get("id") is String or source.id!=map_id:return {"ok":false,"error":"Map identity mismatch"}
	var reserved=rng_provider.reserve(base_rng,1)
	if not reserved.ok:return {"ok":false,"error":str(reserved)}
	var loaded=LoadBridge.prepare(source,views.vm_projection,{"cell":cell,"stopped":next_stop,"random_cursor":int(base_rng.cursor)},{"map_load":true,"rnd_values":reserved.transaction.rnd_values},monster_registry,resources)
	if not loaded.ok:return {"ok":false,"error":str(loaded.error)}
	if loaded.map.get("id")!=map_id:return {"ok":false,"error":"Prepared map identity mismatch"}
	var candidate=candidate_authority.duplicate(true)
	candidate.et=loaded.story.et.duplicate()
	candidate.bt=loaded.story.bt.duplicate()
	var final_view=Profile.project(candidate,cloth,POLICY)
	if not final_view.ok:return {"ok":false,"error":str(final_view)}
	var resource_check=ResourceCheck.check(loaded.map)
	if not resource_check.ok:return resource_check
	var next_actor=Movement.new()
	var next_world=LoadedWorld.new()
	if not next_world.setup_snapshot(next_actor,loaded.map):
		var error=str(next_world.loading_errors)
		next_world.free()
		return {"ok":false,"error":error}
	var position_cell=Vector2i(loaded.actor.cell[0],loaded.actor.cell[1])
	if not next_actor.can_enter(position_cell):
		next_world.free()
		return {"ok":false,"error":"Final actor cell blocked"}
	next_actor.position=Vector2(position_cell)
	next_actor.direction=4
	var used:int=loaded.actor.random_cursor-int(base_rng.cursor)
	var random_committed=rng_provider.commit(base_rng,reserved.transaction,used)
	if not random_committed.ok or random_committed.state.cursor!=loaded.actor.random_cursor:
		next_world.free()
		return {"ok":false,"error":str(random_committed)}
	return {"ok":true,"authority":candidate,"story":final_view.vm_projection,"world":next_world,"movement":next_actor,"stopped":loaded.actor.stopped,"rng":random_committed.state,"consumed":int(base_rng.cursor)+used}
func publish(staged:Dictionary) -> void:
	var old_world=world
	world=staged.world
	movement=staged.movement
	ready_ok=true
	authority=staged.authority
	story=staged.story
	stopped=staged.stopped
	rng_state=staged.rng
	remove_child(old_world)
	add_child(world)
	move_child(world,0)
	old_world.queue_free()
	images.clear()
	revision+=1
	map_load_count+=1
	world.refresh()
	print("NATURAL_MAP_COMMIT ",JSON.stringify({"map":world.map.id,"et0":authority.et[0],"bt0":authority.bt[0],"stop":stopped,"rng_consumed":consumed_total,"added_units":world.map.added_units.size(),"inventory_instances":authority.inventory.instances.size()}))
func advance_opening(delta:int) -> bool:
	if opening_page<0 or preparing:return false
	if delta<0:opening_page=maxi(0,opening_page-1)
	elif opening_page<opening_data.pages.size()-1:opening_page+=1
	else:
		opening_page=-1
		overlay.hide()
		_update_status()
		return true
	show_opening()
	return true
func show_opening() -> void:
	var page=opening_data.pages[opening_page]
	page_title.text="前世今生 · %d / %d"%[opening_page+1,opening_data.pages.size()]
	opening_text.text=page.text
	opening_text.add_theme_color_override("font_color",Color.WHITE if page.color=="白" else Color.YELLOW)
	previous_button.visible=opening_page>0
	next_button.text="下一页" if opening_page<4 else "进入梦境"
	next_button.show()
	overlay.show()
func _physics_process(delta:float) -> void:
	if authority.is_empty() or opening_page>=0:return
	super._physics_process(delta)
func _unhandled_input(event:InputEvent) -> void:
	if authority.is_empty() or opening_page>=0:return
	super._unhandled_input(event)
func _update_status() -> void:
	if authority.is_empty():
		status.text="新游戏候选 | 普通战士 | 兼容RNG明确标记 | 未开始"
		return
	status.text="新游戏候选 | ET%d STOP=%s | %s (%.2f,%.2f) | HP%d MP%d | 兼容RNG consumed=%d\n原五页与双NPC/load链；唯一布衣实例；无战斗/保存/怪物AI。\n%s"%[authority.et[0],stopped,world.map.id,movement.position.x,movement.position.y,authority.character.hp,authority.character.mp,consumed_total,notice]
func apply_page(index:int,process:String) -> bool:
	var view=Profile.project(authority,cloth,POLICY)
	if not view.ok:return reject(str(view))
	var result=VM.execute(world.map.npcs[index].script,view.vm_projection,process)
	if not result.ok:return reject(str(result.error))
	return commit_candidate(result,index)
func commit_candidate(result:Dictionary,index:int) -> bool:
	var candidate=authority.duplicate(true)
	for field in ["level","clear_count","game_mode"]:
		if result.state.get(field)!=authority.character[field]:return reject("Read-only field changed")
	candidate.et=result.state.et.duplicate()
	candidate.bt=result.state.bt.duplicate()
	var validated=Profile.project(candidate,cloth,POLICY)
	if not validated.ok:return reject(str(validated))
	var next_stop=stopped
	var destination=null
	for event in result.events:
		match event.kind:
			"stop":next_stop=true
			"unstop":next_stop=false
			"close":pass
			"tomap":
				if destination!=null or not MAPS.has(event.map):return reject("Unsupported map event")
				destination=event
			_:return reject("Unsupported NPC event")
	if destination!=null:
		var prepared=prepare_map(candidate,destination.map,[destination.x,destination.y],next_stop,rng_state)
		if not prepared.ok:return reject(prepared.error)
		publish(prepared)
		close_dialog()
	else:
		authority=candidate
		story=validated.vm_projection
		stopped=next_stop
		revision+=1
		movement.stop()
		current_npc=index
		current_view=result.duplicate(true)
		if result.closed:close_dialog()
		else:render_dialog()
	print("NATURAL_NPC_COMMIT ",JSON.stringify({"page":result.page,"et0":authority.et[0],"map":world.map.id,"stop":stopped,"rng_consumed":consumed_total}))
	notice="原脚本事务已提交。"
	_update_status()
	return true

func prepare_inputs()->Dictionary:
	var cat=ResourceCheck.read("res://data/items/catalogue.json")
	if not cat.ok:return cat
	if not cat.value.get("records") is Array or cat.value.records.size()<=252 or not cat.value.records[252] is Dictionary:return {"ok":false,"error":"Missing cloth template"}
	var mon=ResourceCheck.read("res://data/monsters/a13-chicken.json")
	if not mon.ok:return mon
	var opening=ResourceCheck.read("res://data/story/opening.json")
	if not opening.ok:return opening
	if not opening.value.get("pages") is Array or opening.value.pages.size()!=5:return {"ok":false,"error":"Expected five original opening pages"}
	for page in opening.value.pages:
		if not page is Dictionary or not page.get("text") is String or not page.get("color") is String:return {"ok":false,"error":"Invalid opening page"}
	if not ResourceLoader.exists("res://assets/ui/original_dialog.png") or not load("res://assets/ui/original_dialog.png") is Texture2D:return {"ok":false,"error":"Missing dialog texture"}
	dialog_background.texture=load("res://assets/ui/original_dialog.png")
	cloth=cat.value.records[252]
	monster_registry={"彩蛋鸡":mon.value}
	opening_data=opening.value
	return {"ok":true}
func build_candidate_ui()->void:
	# Build the inherited dialogue controls without eagerly loading a source map.
	add_child(world)
	var canvas=CanvasLayer.new()
	add_child(canvas)
	canvas.add_child(status)
	status.position=Vector2(12,12)
	status.mouse_filter=Control.MOUSE_FILTER_IGNORE
	canvas.add_child(dialog)
	dialog.position=Vector2(250,520)
	dialog.size=Vector2(523,216)
	dialog.mouse_filter=Control.MOUSE_FILTER_STOP
	dialog_background.mouse_filter=Control.MOUSE_FILTER_IGNORE
	dialog.add_child(dialog_background)
	var font=SystemFont.new()
	font.font_names=PackedStringArray(["Noto Sans CJK SC","Noto Sans CJK","sans-serif"])
	for label in [speaker,paragraph]:
		label.add_theme_font_override("font",font)
		label.add_theme_font_size_override("font_size",17)
		label.add_theme_color_override("font_color",Color("efe0b8"))
		label.mouse_filter=Control.MOUSE_FILTER_IGNORE
		dialog.add_child(label)
	speaker.position=Vector2(20,8)
	paragraph.position=Vector2(20,35)
	paragraph.size=Vector2(480,120)
	paragraph.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	dialog.add_child(choices)
	choices.mouse_filter=Control.MOUSE_FILTER_IGNORE
	dialog.hide()
	_update_status()
