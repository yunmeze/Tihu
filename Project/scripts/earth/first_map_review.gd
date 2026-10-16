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
		world.prepare_east_ground();world.prepare_plant_reuse()
	update_hud()
func _input(event:InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and ready_ok:
		match event.keycode:
			KEY_E:world.prefer_east_ground=not world.prefer_east_ground
			KEY_R:world.prefer_plant_reuse=not world.prefer_plant_reuse
			KEY_1:
				world.review_camera_top_left=Vector2(3168,1024);world.review_camera_label="东侧走廊";world.follow_actor=false
			KEY_2:
				world.review_camera_top_left=Vector2(1920,1024);world.review_camera_label="西侧植物";world.follow_actor=false
			KEY_3:
				world.review_camera_top_left=Vector2(2112,1856);world.review_camera_label="南侧植物";world.follow_actor=false
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
	research_status.text="第一地图局部美术研究稿 · 未完成整图美术验收 / Windows 未测\n范围：地面 178 / 2553（既有 121 + 东廊新增 57），非全图替换"
	hud.visible=show_hud
	if not ready_ok:
		research_status.text+="\n原版资源加载失败；预览不可用"
		hud.text=""
		return
	research_status.text+="\n"+world.actor_mode()+" · 地面："+("研究稿 %d / 178 地块"%[(121 if world.prefer_ground and world.review_ground_owners.size()==121 else 0)+world.east_ground_count()])
	research_status.text+="\n水池：%d/7 研究稿 · 细草丛：%d/3 研究稿（其余整组原版）"%[world.static_props_count("pool"),world.static_props_count("clump")]
	research_status.text+="\n新增植物：%d/24 完整组 · %d/81 owner（既有样区另计；缺组原版）"%[world.plant_reuse_groups.size() if world.prefer_plant_reuse else 0,world.plant_reuse_owners.size()]
	hud.text="点击寻路 | Shift 跑步 | 空格停止 | F 跟随 | G 网格 | H 说明\nB 角色原版/研究稿 | P 地面原版/研究稿 | T 建筑 | S 阴影\nN NPC | V 树木 | J 灌木 | K 草丛（场景物件沿用既有样稿）\nQ 水池原版/研究稿 | W 细草丛原版/研究稿 | L 定位静态物件 | Home 回出生点相机\nE 东廊 57 对比 | R 新增植物对比 | 1 东廊 / 2 西侧 / 3 南侧相机\n快捷键只移动相机，角色不传送；东廊外围 23 源边界保留，重复纹理待美术验收\n相机：%s · 角色：%s"%["跟随" if world.follow_actor else world.review_camera_label,actor.position]
	if world.e_walk_frames.size()!=6:
		research_status.text+="\nE 步行研究稿不可用，整组使用原版"
		hud.text+="\nE 步行原因："+world.e_walk_error
	if world.review_ground_owners.size()!=121:
		research_status.text+="\n草地研究稿不可用，121 个地块全部使用原版"
		hud.text+="\n草地原因："+world.review_ground_error

	if world.east_ground_group.is_empty():
		research_status.text+="\n东廊 57 整组原版回退"
		hud.text+="\n东廊 57 整组原版回退："+world.east_ground_error
	if world.plant_reuse_groups.size()!=24:
		hud.text+="\n新增植物缺失组完整原版回退："+str(world.plant_reuse_errors)
	for id in ["pool","clump"]:
		if not world.static_props_groups.has(id):
			research_status.text+="\n"+("水池" if id=="pool" else "细草丛")+"整组原版回退："+str(world.static_props_errors.get(id,"尚未加载"))

	hud.position.y=8+research_status.get_line_count()*research_status.get_theme_font("font").get_height(14)+8
