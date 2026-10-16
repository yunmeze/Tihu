extends "res://scripts/earth/sample_preview.gd"
## Open this scene explicitly with F6. Main scene and sample remain unchanged.
var research_status=Label.new()
func _init() -> void:
	# Base construction owns unparented drawing Nodes until its _ready.
	for property in world.get_property_list():
		if property.usage & PROPERTY_USAGE_SCRIPT_VARIABLE:
			var value=world.get(property.name)
			if value is Node and value.get_parent()==null:value.free()
	world.free()
	world=preload("res://scripts/earth/first_map_world.gd").new()
func _ready() -> void:
	super._ready()
	get_window().title="第一地图局部美术研究稿 · 未完成整图美术验收 / Windows 未测"
	var font=SystemFont.new()
	font.font_names=PackedStringArray(["Noto Sans CJK SC","Noto Sans CJK","Microsoft YaHei","SimHei","PingFang SC","sans-serif"])
	for label in [hud,research_status]:
		label.add_theme_font_override("font",font)
		label.add_theme_font_size_override("font_size",14)
		label.add_theme_color_override("font_shadow_color",Color.BLACK)
		label.add_theme_constant_override("shadow_outline_size",5)
		label.mouse_filter=Control.MOUSE_FILTER_IGNORE
	hud.position=Vector2(8,74)
	hud.get_parent().add_child(research_status)
	research_status.position=Vector2(8,8)
	research_status.modulate=Color("ffd287")
	if ready_ok:
		world.prepare_e_walk();world.prepare_static_props("pool");world.prepare_static_props("clump")
	update_hud()
func _input(event:InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and ready_ok:
		match event.keycode:
			KEY_Q:world.prefer_review_pool=not world.prefer_review_pool
			KEY_W:world.prefer_review_clump=not world.prefer_review_clump
			KEY_L:
				world.review_camera_top_left=Vector2(2816,1576);world.review_camera_label="水池与细草丛";world.follow_actor=false
			KEY_HOME:
				world.review_camera_top_left=world.SAMPLE_RECT.position;world.review_camera_label="出生点";world.follow_actor=false
		world.refresh();update_hud()
	super._input(event)

func update_hud() -> void:
	research_status.visible=true
	research_status.text="第一地图局部美术研究稿 · 未完成整图美术验收 / Windows 未测\n范围：出生点及南侧道路 121 / 2553 地块，非全图替换"
	hud.visible=show_hud
	if not ready_ok:
		research_status.text+="\n原版资源加载失败；预览不可用"
		hud.text=""
		return
	research_status.text+="\n"+world.actor_mode()+" · 地面："+("121 地块草地研究稿" if world.prefer_ground and world.review_ground_owners.size()==121 else "原版地形")
	research_status.text+="\n水池：%d/7 研究稿 · 细草丛：%d/3 研究稿（其余整组原版）"%[world.static_props_count("pool"),world.static_props_count("clump")]
	hud.text="点击寻路 | Shift 跑步 | 空格停止 | F 跟随 | G 网格 | H 说明\nB 角色原版/研究稿 | P 地面原版/研究稿 | T 建筑 | S 阴影\nN NPC | V 树木 | J 灌木 | K 草丛（场景物件沿用既有样稿）\nQ 水池原版/研究稿 | W 细草丛原版/研究稿 | L 定位静态物件 | Home 回出生点相机\n相机：%s · 角色：%s"%["跟随" if world.follow_actor else world.review_camera_label,actor.position]
	if world.e_walk_frames.size()!=6:
		research_status.text+="\nE 步行研究稿不可用，整组使用原版"
		hud.text+="\nE 步行原因："+world.e_walk_error
	if world.review_ground_owners.size()!=121:
		research_status.text+="\n草地研究稿不可用，121 个地块全部使用原版"
		hud.text+="\n草地原因："+world.review_ground_error

	for id in ["pool","clump"]:
		if not world.static_props_groups.has(id):
			research_status.text+="\n"+("水池" if id=="pool" else "细草丛")+"整组原版回退："+str(world.static_props_errors.get(id,"尚未加载"))

	hud.position.y=8+research_status.get_line_count()*research_status.get_theme_font("font").get_height(14)+8
