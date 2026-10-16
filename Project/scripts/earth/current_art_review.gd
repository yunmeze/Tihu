extends Node
## F6-only art inspection. Fixed source A13; no story, rewards, NPC services or saves.
const RELEASE="tree-stage-shared-south-v3-candidate"
const LOGICAL=Vector2i(1024,768)
const RASTER=Vector2i(2048,1536)
const WORLD_PATH="res://scripts/earth/upright_51_70_world.gd"
const MOVEMENT_PATH="res://scripts/core/movement.gd"
const SOURCE_MAP="res://data/maps/A13.json"
# Reviewed source-code closure, not a relaxed replacement for inherited asset gates.
const CODE_PINS={
	"res://data/maps/A13.json": "d09549838963c8157307cc5406d3118baf69259d82459bcba0a3a8be5b34aa27",
	"res://ground_candidate/ground.gdshader": "6ff20204aa62a11570d68ccc0189794382c2f28b8be79be902bbed52eae76d79",
	"res://scripts/art/density_alpha_ground_shadow.gd": "cfc61e6c2b647bee68b063c1eecd884e1ac0ffa545fc1a59b3c3af4397adaf47",
	"res://scripts/art/hero_alpha_ground_shadow.gd": "3eeebe50bfdd235fee24b30bfbdaaad5517a5254bd7e318b73abc80adb5ccdd2",
	"res://scripts/core/dialogue_vm.gd": "460b7dcb9363f99222a8840a173aa1051ac01c15f1c5827d988a3bee80ef53e8",
	"res://scripts/core/map_load_bridge.gd": "769e7342fea2acbd70a2cb625cda4d7ae99143924beaad50da14b08f9fff366f",
	"res://scripts/core/movement.gd": "6f48e3d5e7b655d19bd25f65ae735f1ab998f68cae8a17bc12306e0d66f2db99",
	"res://scripts/core/npc_source_identity.gd": "267193e102332827cd8ff18cf32aec585be9410622e3ca41c641598defd2a8e0",
	"res://scripts/earth/a13_visual_flag_identity.gd": "443ed22ee642a6f271df2cbf52155516cb609e17c1485fe652af0422d6a976be",
	"res://scripts/earth/asset_guard.gd": "c5a0718736b91ceac6aea417a464840e61b33c03b19d8dc3f61272339a7cdf4e",
	"res://scripts/earth/east_ground_guard.gd": "40c8cfda3af714c309d440f282cc70de54163d773c70d7252e61e2544ecefb4c",
	"res://scripts/earth/fangzhang_candidate.gd": "8f3b21d4f24c73299b8685715f58b8a4f15cbb9b454e84a34c69d9a12831e6a8",
	"res://scripts/earth/fangzhang_shadow_gate.gd": "d77a3598a8980871f117c61fcb7a83b602772395ecd603f223e4e2ba64518ab0",
	"res://scripts/earth/first_map_floor_pass.gd": "2fcaca8dd3534676121e09b04e8797695946143790cf473228e677caa32018fe",
	"res://scripts/earth/first_map_guard.gd": "1857a591d213ca2a574fb1de5a048bbcb266540cb246c4f3c46e9031840c2b66",
	"res://scripts/earth/first_map_world.gd": "e6a8ac3604c5ea938fbf006da1a79f195e38adf65695168ea0498db44bb37a5c",
	"res://scripts/earth/flat_shadow_gate.gd": "bb31c6ab95c0950fecd196731f8c87d1e03e2c771b5427bc5d4ae8abf18d32c7",
	"res://scripts/earth/grass_candidate.gd": "a91c5afa94ee4c02d8ce4fb07df508eaa0a9dd50728ed29df0ca473f61fe8c59",
	"res://scripts/earth/ground_candidate.gd": "b31fecb614594f21acd0b34fb0e5857f35e2c6e7fc1f5c8b03393bae10c6f6c8",
	"res://scripts/earth/ground_candidate_guard.gd": "d48b9e7ebe6c1c2a4a8c4112458d128aba485132a8029151a8a571f13af0dce7",
	"res://scripts/earth/ground_manifest_weak_cache.gd": "085d70bab1da34f4770b719b2991ee0f641c4ef9eee2e75c852ea0854be50cc2",
	"res://scripts/earth/ground_texture_weak_bank.gd": "84ca0a7c172033cdda00548d1e6fddb54a6d9de048486e0481dbf1de95f0b618",
	"res://scripts/earth/hall_candidate.gd": "87351ee17139a51f5434143544291700ea8d0a401df1b8438973c92bb248a1ae",
	"res://scripts/earth/house_owner_guard.gd": "b88505e2dffd4f666e4ac8a9e5a5e78d94b52e3856e6d831776e443f8a14a649",
	"res://scripts/earth/house_owner_mask.gdshader": "d37db049c1a79d64fa2235ac7d7e83d8b33503c635d06d78aaed709385461dca",
	"res://scripts/earth/instance_identity_guard.gd": "2eabae66a29b8696d7aef50ddfe5bbd27b46ad4278624c10b4a1183a2435cb0b",
	"res://scripts/earth/left_upright_shadow_gate.gd": "1af8a6d02d6b0f6ec68abd12b708cde4ac1e8b984bdc3d1568e54b64995c0928",
	"res://scripts/earth/lingyunzi_candidate.gd": "5c110878726bb354e20574d8a8ef092c227f2742209c9ae3cc8b4e7787509d53",
	"res://scripts/earth/max_ground_shadow.gd": "eb066c816e807bd542cf5338eab161aff9bf4ca34771764ac2a938f5edc3a5bb",
	"res://scripts/earth/plant_reuse_guard.gd": "30866034c7135d73e410874f065947976a1acd28567638d0621b45056d128f98",
	"res://scripts/earth/plant_texture_weak_bank.gd": "ddda8c839b2083178df6690eb14bed11a2f3e0be84eacdfa0552f33c71fcf4ad",
	"res://scripts/earth/raw_ground_shadow.gd": "8af76868855ce04544a6251f3f2e850550f0ae423b39e5c54c8ed98e29c5bed6",
	"res://scripts/earth/receiver_v2_gate.gd": "835353138b091230f14336d56d24bf2d477845e84e084685d6506174fabea999",
	"res://scripts/earth/s_idle_shadow_gate.gd": "265e5e5ebb41de6609575c66378d90253734d332b0a6496074633014983dc411",
	"res://scripts/earth/s_walk_contact_v3_compositor.gd": "5361a2300051cafacc12900db7e630dbf18c4e49fe794238b84c2ae02b0bc638",
	"res://scripts/earth/s_walk_contact_v3_gate.gd": "cd83aed2cbdcc3b52e2ce2c5f48a229a64796bfa555d81821b51f3c9adc110d0",
	"res://scripts/earth/s_walk_contact_v3_qualification.gd": "80dd2a7047eb1104ed8e11e46ebe57854b787ea67208d886e60d73eafcb271d2",
	"res://scripts/earth/sample_floor_pass.gd": "7fd59781dca6e3f8cb7ae7fe5c493464668350ae3086af0deb10199f0361defb",
	"res://scripts/earth/sample_world.gd": "c9139f34e1d57b1d33086c11157850454325c88078608fe13f8a081f7ddc07b2",
	"res://scripts/earth/shrub_candidate.gd": "f910e088c4d700575ffa722a85226364e4b1344cf408e1d9b87b091776fc5c41",
	"res://scripts/earth/snapshot_atlas_qualification.gd": "0e431c7b5c5e225c07846e325bfc66a65fcf76caf330a04974b80b30d1c0a2a7",
	"res://scripts/earth/snapshot_east_guard.gd": "fec5275e8c6c4944713655ba2f1a433dc91233f1f8f7002ff88dcb0b33c1ca16",
	"res://scripts/earth/snapshot_exact_cache.gd": "b7b2df18106536bfa30872dad72ff51457ea6b51a2d14598bef3f0d1a3772386",
	"res://scripts/earth/snapshot_ground_guard.gd": "e560487604de3f4520d5f591c526a944c036283893211177e5f404ff14dee46b",
	"res://scripts/earth/snapshot_plant_guard.gd": "d877839d396e980d03c7b84c0796f74b3ff2488773a125e1566f07a99565b1f3",
	"res://scripts/earth/snapshot_plant_shared_guard.gd": "a867e2349e2462c5f18849a4280be48de99fbaf821ab0d88885aebd621e8ec8e",
	"res://scripts/earth/snapshot_prefilter_world.gd": "02dea14cf29ecf358547abac62cb11503faaa12ad76a4a5bc4b85ee4cd1e609b",
	"res://scripts/earth/snapshot_props_guard.gd": "ed1e65fa004de533627e74f06784415b19e31d7198964661cd4803b495ddc415",
	"res://scripts/earth/snapshot_receiver_qualification.gd": "0dbdf5393bd9fa3344aa4dcba870b2277ef280757f7912faaf9e787c47d79fa7",
	"res://scripts/earth/snapshot_sorted_world.gd": "1d89ee9e02b984739eebf1f51641f9843ef7c7d43b9f4c7434a4022128333e78",
	"res://scripts/earth/snapshot_source_identity.gd": "19d2ff5c00392fafb2fc7e6466472d78c8e3a0b57f273508375879b212d2e011",
	"res://scripts/earth/snapshot_south_guard.gd": "6a2028999bbe4a7fec61150120ca1488f0a99caf9be96fc5ab21abbfadd29e1e",
	"res://scripts/earth/snapshot_world.gd": "f53f2d90843ff55e9078eda8d45498ea407aeffc520a8beec8d95f1ea35c89fe",
	"res://scripts/earth/snapshot_zhang_world.gd": "533199fca3174a0e426eebe46cb740eb8eb1ad91e12d5644f7671f77e0aa2d92",
	"res://scripts/earth/south_vegetation_candidate.gd": "4dd2ae3074977b62d837b8d1ca5137fc1f7a7bad5d92f21f12786d67ad8dc314",
	"res://scripts/earth/south_walk_candidate_guard.gd": "968b699c5765279ed734876c4bb148ff1041603a4c2f3fb9c4a7529fd6f0cfeb",
	"res://scripts/earth/south_walk_contact_world.gd": "d17f4a4768452905c21b1c6a5949ff8b8344bf27752558024697cd0847cf37fa",
	"res://scripts/earth/south_walk_snapshot_world.gd": "66a6f6d73ee3ef25c1ad1896605d6d00a8e12754923c298c64b220f30c9add61",
	"res://scripts/earth/static_props_guard.gd": "e6346c7829629a394075e272704bc16d26418993fad26659cc5b6ebcc9a0034a",
	"res://scripts/earth/translated_shrub_candidate.gd": "0323bbc53c55462a1b7b22b251f965cf1ebcd3499881c35601a3d0352d63cbe3",
	"res://scripts/earth/tree_candidate.gd": "b95f1180cc294698f2d23131b2b764a1b59b98759a07dc123e7407c82fcedb15",
	"res://scripts/earth/upright_51_70_compositor.gd": "bbb377e3c0b2b5770d7305ba48c69ed1e2013e025eb27435f434338af6d43844",
	"res://scripts/earth/upright_51_70_gate.gd": "933224c2d2432b6be5cf208d87f4032ac166d891a0da7b2b92cd8f781d40f629",
	"res://scripts/earth/upright_51_70_qualification.gd": "578ae908b04d3379225b7d2d88502824b8b72bf5ff24cc1d5c89dab8aaa98871",
	"res://scripts/earth/upright_51_70_world.gd": "26bfa8866f26930de5f11638689c079beabf1be0b3f25bb1897085f0b7d6de43",
	"res://scripts/earth/upright_candidate.gd": "83d79c0484b186bdf1c160be4da5c18a8395f9cf6d6f2110b7f3d42ba39413a0",
	"res://scripts/earth/upright_ground_lifecycle.gd": "d3e0b16238d746a950242aa9fa5309fab4866da6eebdfaa844887814f34c8cda",
	"res://scripts/earth/upright_raw_weak_bank.gd": "eb0ed4cdd8609eac3b14088615033ea80a5a3789fc2cf5ca50f8deb239ad1876",
	"res://scripts/earth/viewport_ground_shadow.gd": "80a5b391336090ef55338a5561fbad213e67adb3915c7eea9285cf401991882f",
	"res://scripts/earth/xuyun_guard.gd": "bca49885359f4a90520b8249aba49b1f527ee4b1198ff312c3251bc4ebe34efd",
	"res://scripts/earth/zhang_fourphase_guard.gd": "836404d9001f77826648a9356b12a7ea8faf1620a5de01ee238d24e583101c0c",
	"res://scripts/world_resource_preflight.gd": "38ea536fd5309ee13f5755d31fcf9a5332b84f981eb5a2c30fb325a2ea3c07c7",
	"res://scripts/world_view.gd": "b404d8dd5e7e85a120fec00b7eb5f01e6bfc1fc37adf5e7878c1798432d4e285",
	"res://shaders/density_alpha_ground_shadow.gdshader": "b4d976938acbb3b57df13bf85ade4ebf3173c0634b5e7ee4338e8b038bf51f3b",
	"res://shaders/earth_max_ground_shadow.gdshader": "232997a561d4451f4ecfc2da7cd4a0e821a751722392806c1d41fe2777ead22b",
	"res://shaders/earth_s_walk_contact_v3.gdshader": "c40ba78cea3342ae09029f7655cedf8fe375760d39123082dbdfa9a651dc92ab",
	"res://shaders/earth_upright_51_70.gdshader": "3fbd82add41474f094defcdc45a4ffb431a27a66938441aebff9c6e3b53598b5",
	"res://shaders/hero_alpha_ground_shadow.gdshader": "d8f4894fd16458a3a7aabb5db5af4a95f39320f5e2549c33467f79f5a5089c24"
}
const CAMERA_POINTS=[Vector2(2496,960),Vector2(2112,1664),Vector2(2450,1465),Vector2(738,400)]
const CAMERA_LABELS=["出生区","南侧","南右","小屋"]
const FLOOR_COUNTS={"C":24,"grass":907,"current":39,"source":1583}
var raster:SubViewport
var display:TextureRect
var actor:RefCounted
var world
var status:Label
var detail:Label
var ready_ok=false
var source_ok=false
var source_error=""
var gate_failures:Array[String]=[]
var last_request:Dictionary={}
var tick=0
var visual_pending=false
var source_snapshot_bytes=PackedByteArray()
var compare_ground=false

func _ready()->void:
	get_window().title="当前美术检视 · A13 固定参考图 · 不执行剧情 / 奖励 / 存档"
	get_window().content_scale_size=LOGICAL
	get_window().content_scale_aspect=Window.CONTENT_SCALE_ASPECT_KEEP
	raster=SubViewport.new()
	raster.size=RASTER;raster.size_2d_override=LOGICAL;raster.size_2d_override_stretch=true
	raster.render_target_update_mode=SubViewport.UPDATE_ALWAYS
	add_child(raster)
	display=TextureRect.new()
	display.texture=raster.get_texture();display.expand_mode=TextureRect.EXPAND_IGNORE_SIZE
	display.texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR;display.mouse_filter=Control.MOUSE_FILTER_IGNORE
	add_child(display)
	build_ui()
	get_viewport().size_changed.connect(fit_display);fit_display()
	for path in CODE_PINS:
		if not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=CODE_PINS[path]:
			source_error="发布源文件不符："+path.get_file();update_hud();return
	if Engine.physics_ticks_per_second!=50:
		source_error="需要项目原有 50Hz 物理时序";update_hud();return
	var original=JSON.parse_string(FileAccess.get_file_as_string(SOURCE_MAP))
	if not original is Dictionary or original.get("id")!="A13":
		source_error="A13 固定参考图不可用";update_hud();return
	source_snapshot_bytes=var_to_bytes(original)
	actor=load(MOVEMENT_PATH).new();actor.position=Vector2(61,39);actor.direction=4
	world=load(WORLD_PATH).new();world.prefer_s_walk_shadow=true;world.prefer_tree_pilot=true
	if not world.setup_snapshot(actor,original):
		source_error="地图资源加载失败："+str(world.loading_errors)
		world.free();world=null;update_hud();return
	# The source snapshot is intentionally unexecuted. No map-load scripts run.
	if var_to_bytes(world.map)!=source_snapshot_bytes:
		source_error="固定参考图被改动";world.free();world=null;update_hud();return
	source_ok=true;raster.add_child(world)
	world.follow_actor=false;world.review_camera_top_left=CAMERA_POINTS[0];world.review_camera_label=CAMERA_LABELS[0]
	visual_pending=true;flush_visual_refresh()
	print("CURRENT_ART_REVIEW_READY ",ready_ok," release=",RELEASE," fixed_snapshot=",CODE_PINS[SOURCE_MAP]," gates=",gate_failures)

func build_ui()->void:
	var layer=CanvasLayer.new();add_child(layer)
	var panel=PanelContainer.new();panel.position=Vector2(8,8);layer.add_child(panel)
	var margin=MarginContainer.new();panel.add_child(margin)
	for side in ["left","top","right","bottom"]:margin.add_theme_constant_override("margin_"+side,6)
	var rows=VBoxContainer.new();margin.add_child(rows);rows.add_theme_constant_override("separation",3)
	var font=SystemFont.new()
	font.font_names=PackedStringArray(["Noto Sans CJK SC","Noto Sans CJK","Microsoft YaHei","SimHei","PingFang SC","sans-serif"])
	rows.add_theme_font_override("font",font);rows.add_theme_font_size_override("font_size",14)
	var title=Label.new();title.text="美术检视 · A13 固定参考图 · 不执行剧情 / 奖励 / 存档";rows.add_child(title)
	var buttons=HBoxContainer.new();rows.add_child(buttons)
	for i in CAMERA_POINTS.size():
		var button=Button.new();button.text=CAMERA_LABELS[i];button.focus_mode=Control.FOCUS_NONE
		button.add_theme_font_override("font",font);button.add_theme_font_size_override("font_size",14)
		button.pressed.connect(set_review_camera.bind(i));buttons.add_child(button)
	var follow=Button.new();follow.text="跟随主角";follow.focus_mode=Control.FOCUS_NONE
	follow.add_theme_font_override("font",font);follow.add_theme_font_size_override("font_size",14)
	follow.pressed.connect(follow_actor);buttons.add_child(follow)
	status=Label.new();rows.add_child(status)
	detail=Label.new();rows.add_child(detail)
	for label in [title,status,detail]:
		label.add_theme_font_override("font",font);label.add_theme_font_size_override("font_size",14)
	# This panel consumes pointer events. World clicks only use _unhandled_input.
	panel.mouse_filter=Control.MOUSE_FILTER_STOP

func fit_display()->void:
	var available=get_viewport().get_visible_rect().size
	var factor=minf(available.x/LOGICAL.x,available.y/LOGICAL.y)
	display.size=Vector2(LOGICAL)*factor;display.position=(available-display.size)*0.5

func map_display_point(point:Vector2)->Dictionary:
	if not source_ok or not Rect2(display.position,display.size).has_point(point):return {"ok":false}
	var physical=(point-display.position)/display.size*Vector2(RASTER)
	var logical=raster.get_stretch_transform().affine_inverse()*physical
	return {"ok":true,"logical":logical,"cell":world.to_cell(logical)}

func set_review_camera(index:int)->void:
	if not source_ok or index<0 or index>=CAMERA_POINTS.size():return
	world.review_camera_top_left=CAMERA_POINTS[index];world.review_camera_label=CAMERA_LABELS[index];world.follow_actor=false
	visual_pending=true;flush_visual_refresh()

func follow_actor()->void:
	if not source_ok:return
	world.follow_actor=true;visual_pending=true;flush_visual_refresh()

func toggle_ground()->void:
	if not source_ok or world.floor_pass.candidate.is_empty():return
	compare_ground=not compare_ground
	world.floor_pass.set_candidate_enabled(not compare_ground)
	visual_pending=true;flush_visual_refresh()

func _unhandled_input(event:InputEvent)->void:
	if event is InputEventMouseButton and event.button_index==MOUSE_BUTTON_LEFT and event.pressed and ready_ok:
		var mapped=map_display_point(event.position)
		if mapped.ok:
			var accepted=actor.request(mapped.cell)
			last_request={"cell":mapped.cell,"accepted":accepted}
			visual_pending=true;flush_visual_refresh();get_viewport().set_input_as_handled()
	elif event is InputEventKey and event.pressed and not event.echo and source_ok:
		match event.keycode:
			KEY_F:follow_actor()
			KEY_HOME:set_review_camera(0)
			KEY_SPACE:actor.stop();visual_pending=true;flush_visual_refresh()
			KEY_F8:toggle_ground()
			_:return
		get_viewport().set_input_as_handled()

func _physics_process(delta:float)->void:
	if not ready_ok:return
	actor.step(delta,Input.is_key_pressed(KEY_SHIFT))
	tick+=1;visual_pending=true

func _process(_delta:float)->void:
	if visual_pending:flush_visual_refresh()

func flush_visual_refresh()->void:
	if not source_ok:return
	world.tick=tick;world.refresh();visual_pending=false
	gate_failures=required_gate_failures()
	ready_ok=gate_failures.is_empty()
	if not ready_ok:actor.stop()
	update_hud()

func required_gate_failures()->Array[String]:
	var failed:Array[String]=[]
	if var_to_bytes(world.map)!=source_snapshot_bytes:failed.append("固定A13身份")
	if not world.source_methods_valid or not world.sort_methods_valid or not world.draw_source_valid:failed.append("发布绘制代码")
	if not world.snapshot_atlas_matches(world.packs,world.atlas_qualification.original):failed.append("原图集身份")
	if not world.candidate_ready or not world.walk_ready or not world.e_idle_ready or not world.s_idle_ready or world.e_walk_frames.size()!=6:failed.append("既有角色相位")
	if not world.south_walk_ready or not world.south_walk_guard.bank_complete():failed.append("S步行6相")
	if not world.s_walk_shadow_ready or not world.s_walk_qualification.resource_ok.get("hero_s_walk_contact_v3",false):failed.append("S步行影接地区门")
	if world.floor_pass.candidate.get("counts",{})!=FLOOR_COUNTS:failed.append("地面C24/907/39/1583")
	if world.floor_pass.candidate_enabled==compare_ground:failed.append("地面对照状态")
	if world.review_ground_owners.size()!=121 or world.east_ground_count()!=57:failed.append("既有地面121+57")
	if world.plant_reuse_groups.size()!=24 or world.plant_reuse_owners.size()!=81:failed.append("植物24组/81owner")
	if world.hall_owners.size()!=30:failed.append("大殿30owner")
	if world.fangzhang_texture==null or world.lingyunzi_texture==null:failed.append("方丈/凌云子")
	if not world.xuyun_active:failed.append("虚云")
	if not world.house_active:failed.append("小屋")
	if not world.zhang_active or world.zhang_guard.slot<0:failed.append("张四相")
	if world.tree_owners.size()!=7 or world.shrub_owners.size()!=4:failed.append("首树/灌木")
	for i in 2:
		if world.upright_groups[i].size()!=6 or world.translated_shrub_groups[i].size()!=4 or world.grass_groups[i].size()!=2:failed.append("既有植物组"+str(i))
	for id in world.SouthCandidate.IDS:
		if world.south_groups.get(id,{}).size()!=world.SouthCandidate.COUNTS[id] or not world.south_active.get(id,false):failed.append("南植:"+id)
	if not world.south_snapshot_errors.is_empty():failed.append("南植身份")
	if world.static_props_count("pool")!=7 or world.static_props_count("clump")!=3:failed.append("水池/细草")
	for caster in ["hero_se","hero_s","fangzhang","lingyunzi","first_tree","left_upright"]:
		if not world.qualification.resource_ok.get(caster,false) or not world.qualifies(caster):failed.append("接地区:"+caster)
	# The visible tree body is independent of the new tree-shadow raw sampler.
	var tree_group:Dictionary=world.plant_reuse_groups.get("upright_tree_51_70",{})
	if tree_group.is_empty() or not world.prefer_tree_pilot or not world.tree_plant_token.get("active",false) or not world.plant_reuse_guard.live_valid(tree_group,world.map,world.objects,world.packs):failed.append("51,70树体身份")
	if world.tree_qualification.contract.is_empty() or not world.tree_qualification.error.is_empty():failed.append("51,70树影源资格")
	var tree_material=world.shadow_compositor.material
	if not tree_material is ShaderMaterial:
		failed.append("51,70树影材质")
	elif compare_ground:
		# F8 off must revoke shadow raw sampling/receiver/bindings, not the tree body.
		if world.tree_ready or world.shadow_compositor.tree_active or world.tree_gate.body!=null or world.tree_gate.receiver!=null or world.floor_pass.ground_token.get("active",false):failed.append("51,70树影未随对照撤销")
		if tree_material.get_shader_parameter("tree_pilot_active")!=false or tree_material.get_shader_parameter("tree_pilot_body")!=null or tree_material.get_shader_parameter("tree_pilot_receiver")!=null:failed.append("51,70树影旧绑定未清空")
	else:
		if not world.tree_ready or not world.tree_gate.valid(world) or not world.shadow_compositor.tree_active:failed.append("51,70树影正门")
		if tree_material.get_shader_parameter("tree_pilot_active")!=true or tree_material.get_shader_parameter("tree_pilot_body")!=world.tree_gate.body or tree_material.get_shader_parameter("tree_pilot_receiver")!=world.tree_gate.receiver:failed.append("51,70树影实际绑定")
	return failed

func update_hud()->void:
	if not source_error.is_empty():
		status.text="检视未启动："+source_error;status.modulate=Color("ffab8a")
		detail.text="未加载替代版本。F5 正常开场保持原样。";return
	if not source_ok:return
	status.modulate=Color.WHITE if ready_ok else Color("ffab8a")
	if ready_ok:
		status.text="地面："+("既有通道121+57（F8对照）" if compare_ground else "C24 / 草907 / 既有39 / 原版保留1583")+" · S步行6相 / 张4相 / 南植4组 / 51,70树"
	else:status.text="检视不完整，移动已停止："+"、".join(gate_failures)
	var mode="原版动作"
	if world.uses_s_walk(actor.source_frame()):mode="S步行6相"
	elif world.uses_e_walk(actor.source_frame()) or world.uses_candidate(actor.source_frame()):mode="已发布候选动作"
	detail.text="点击寻路 · Shift跑 · 空格停 · F跟随 · F8地面对照 | "+("跟随" if world.follow_actor else world.review_camera_label)+" · "+mode
	if not last_request.is_empty() and not last_request.accepted:detail.text+=" · 原格阻挡/不可达"
