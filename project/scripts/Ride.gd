extends Node3D
## Fresh coastal daydream runtime. All visible 3D meshes are Blender-authored.
## Runtime creates only environment, camera, UI, and non-rendering animation pivots.

signal state_changed
const ASSET_PATH := "res://assets/coastal_ride.glb"
const Palette := preload("res://scripts/ToonPalette.gd")
const HUD := preload("res://scripts/RideHUD.gd")
const MIN_SPEED := 4.0
const MAX_SPEED := 22.0
const START_SPEED := 12.0
const START_CAMERA := 2
# A composed coastal slice: camera stays on its finished presentation side.
const MIN_AZIMUTH := -0.49
const MAX_AZIMUTH := 1.08
const MIN_ELEVATION := 0.085
const MAX_ELEVATION := 0.255
const MIN_ZOOM := 0.95
const MAX_ZOOM := 1.10
const CAMERA_NAMES := ["POSTCARD", "FOLLOW", "PORTRAIT"]

@export var wheel_radius := 0.46
@export var crank_center := Vector3(0.03, 0.65, 0.0)
@export var crank_radius := 0.17
@export var hip_center := Vector3(-0.23, 1.12, 0.0)
@export var leg_lateral := 0.25
@export var upper_leg_length := 0.32
@export var lower_leg_length := 0.35
@export var authored_leg_length := 0.32

var speed_kmh := START_SPEED
var distance_m := 0.0
var ride_time := 0.0
var paused := false
var camera_mode := START_CAMERA
var beauty_preview := true
var look_profile := 1 # 0: diagnostic rollback, 1: accepted warm look, 2: graphic test
var accepted_style := true
var orbit_yaw := 0.0
var orbit_pitch := 0.0
var zoom := 1.0
var dragging := false
var asset_loaded := false
var asset_message := "The hand-crafted scene is being prepared."
var camera: Camera3D
var world: Node3D
var imported_world: Node3D
var hud: Control
var water_material: ShaderMaterial
var palette: RefCounted
var planting: RefCounted
var planting_report: Dictionary = {}
var nodes_by_name: Dictionary = {}
var base_transforms: Dictionary = {}
var wheel_pivots: Array[Node3D] = []
var rider_parts: Array[Node3D] = []
var eyes: Array[Node3D] = []
var leg_rigs: Array[Dictionary] = []
var crank_pivot: Node3D
var motion_accents: Array[Node3D] = []
var camera_initialized := false
var smoothed_camera_target := Vector3.ZERO
var pending_capture := false

func _ready() -> void:
	# Explicit low-cost preview for software renderers; the art layout is identical.
	if OS.get_cmdline_user_args().has("--software-preview"):
		get_viewport().msaa_3d = Viewport.MSAA_DISABLED
		get_viewport().screen_space_aa = Viewport.SCREEN_SPACE_AA_FXAA
		RenderingServer.directional_shadow_atlas_set_size(2048, true)
		RenderingServer.directional_soft_shadow_filter_set_quality(RenderingServer.SHADOW_QUALITY_SOFT_LOW)
	if OS.get_cmdline_user_args().has("--compact-preview"):
		get_window().size = Vector2i(960, 600)
	paused = OS.get_cmdline_user_args().has("--paused")
	accepted_style = not OS.get_cmdline_user_args().has("--baseline-look")
	beauty_preview = accepted_style or OS.get_cmdline_user_args().has("--beauty-preview")
	look_profile = 2 if OS.get_cmdline_user_args().has("--look-cel") else (1 if accepted_style or OS.get_cmdline_user_args().has("--look-warm") else 0)
	for argument: String in OS.get_cmdline_user_args():
		if argument.begins_with("--camera="):
			camera_mode = clampi(argument.trim_prefix("--camera=").to_int() - 1, 0, 2)
	_build_environment()
	world = Node3D.new()
	world.name = "AuthoredWorld"
	add_child(world)
	camera = Camera3D.new()
	camera.name = "Camera"
	camera.near = 0.08
	camera.far = 250.0
	camera.current = true
	add_child(camera)
	_load_art()
	var layer := CanvasLayer.new()
	layer.name = "Interface"
	add_child(layer)
	hud = HUD.new()
	hud.name = "HUD"
	layer.add_child(hud)
	hud.set_ride(self)
	_update_camera(0.0, true)

func _build_environment() -> void:
	var sky_material := ShaderMaterial.new()
	sky_material.shader = load("res://shaders/pastel_sky.gdshader")
	sky_material.set_shader_parameter("cloud_panorama", load("res://assets/textures/coastal_cumulus_panorama.png"))
	sky_material.set_shader_parameter("cloud_strength", 0.78 if accepted_style or OS.get_cmdline_user_args().has("--atmosphere-preview") else 0.60)
	sky_material.set_shader_parameter("cloud_azimuth_turns", 0.15)
	var sky := Sky.new()
	sky.sky_material = sky_material
	sky.radiance_size = Sky.RADIANCE_SIZE_128
	var environment := Environment.new()
	environment.background_mode = Environment.BG_SKY
	environment.sky = sky
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color("c4d2e7")
	environment.ambient_light_energy = 0.65
	if look_profile > 0:
		environment.ambient_light_color = Color("b9c6e8")
		environment.ambient_light_energy = 0.38
	environment.ambient_light_sky_contribution = 0.0
	environment.reflected_light_source = Environment.REFLECTION_SOURCE_DISABLED
	environment.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	environment.tonemap_exposure = 1.0
	# Opt-in native A/B until the restrained Compatibility AO pass is reviewed.
	environment.ssao_enabled = OS.get_cmdline_user_args().has("--ao-preview")
	environment.ssao_radius = 0.18
	environment.ssao_intensity = 0.55
	environment.fog_enabled = true
	environment.fog_light_color = Color("a4ced6")
	environment.fog_light_energy = 0.65
	environment.fog_density = 0.0035
	environment.fog_sky_affect = 0.0
	var atmosphere := WorldEnvironment.new()
	atmosphere.name = "CoastalAtmosphere"
	atmosphere.environment = environment
	add_child(atmosphere)
	var sun := DirectionalLight3D.new()
	sun.name = "IllustratedSun"
	sun.rotation_degrees = Vector3(-43.0, -20.0, 0.0)
	sun.light_color = Color("fff1d8")
	sun.light_energy = 0.09
	if look_profile > 0:
		sun.light_color = Color("fff1d7")
		sun.light_energy = 0.22
	sun.light_angular_distance = 1.6
	sun.shadow_enabled = true
	sun.shadow_bias = 0.16
	sun.shadow_normal_bias = 1.2
	sun.directional_shadow_max_distance = 28.0
	add_child(sun)
	var bounce := DirectionalLight3D.new()
	bounce.name = "SeaBounce"
	bounce.rotation_degrees = Vector3(-22.0, 148.0, 0.0)
	bounce.light_color = Color("acd9e7")
	# Native colored ambient provides the broad fill.
	# Keep an extra directional fill disabled to avoid additive washout.
	bounce.light_energy = 0.0
	bounce.sky_mode = DirectionalLight3D.SKY_MODE_LIGHT_ONLY
	add_child(bounce)

func _load_art() -> void:
	var asset_path := ASSET_PATH
	if not ResourceLoader.exists(asset_path):
		return
	var packed := load(asset_path) as PackedScene
	if packed == null:
		asset_message = "The authored scene could not be loaded."
		push_error(asset_message)
		return
	imported_world = packed.instantiate() as Node3D
	if imported_world == null:
		return
	world.add_child(imported_world)
	_index(imported_world)
	palette = Palette.new()
	palette.vertex_ao_strength = 0.0 if OS.get_cmdline_user_args().has("--no-vertex-ao") else 0.22
	palette.rim_preview_strength = 0.35 if OS.get_cmdline_user_args().has("--rim-preview") else 0.0
	palette.outline_wings = not accepted_style and not OS.get_cmdline_user_args().has("--no-wing-outline")
	palette.color_preview = accepted_style or OS.get_cmdline_user_args().has("--coast-color-preview")
	palette.look_profile = look_profile
	palette.feather_flow_preview = accepted_style or OS.get_cmdline_user_args().has("--feather-preview")
	palette.rock_plane_preview = accepted_style or OS.get_cmdline_user_args().has("--rock-plane-preview")
	if not OS.get_cmdline_user_args().has("--no-planting") and (accepted_style or OS.get_cmdline_user_args().has("--planting-preview")) and _prepare_foliage_atlas():
		planting = load("res://scripts/CoastalPlanting.gd").new()
		planting.canopy_enabled = accepted_style and not OS.get_cmdline_user_args().has("--no-canopy")
		planting.ledge_enabled = accepted_style and not OS.get_cmdline_user_args().has("--no-ledge")
		planting_report = planting.apply(imported_world, self)
		_index(imported_world)
	palette.apply(imported_world)
	if planting != null and not OS.get_cmdline_user_args().has("--no-batch") and (accepted_style or OS.get_cmdline_user_args().has("--batch-foliage")):
		planting_report["batching"] = planting.batch_cards(imported_world)
	_bind_water()
	_bind_motion()
	asset_loaded = true
	asset_message = "Hand-shaped coast · real-time toon lighting"
	print("Authored scene: ", nodes_by_name.size(), " nodes, ", palette.surface_count, " toon surfaces.")


func _prepare_foliage_atlas() -> bool:
	const METADATA := "res://assets/textures/coastal_foliage_atlas_0724.json"
	if not FileAccess.file_exists(METADATA):
		push_warning("Painted foliage metadata is absent; planting preview skipped.")
		return false
	var mapping := _validate_atlas_mapping(JSON.parse_string(FileAccess.get_file_as_string(METADATA)))
	if mapping.is_empty():
		push_warning("Painted foliage metadata is invalid; planting preview skipped.")
		return false
	palette.atlas_texture = load(mapping.asset) as Texture2D
	palette.atlas_regions = mapping.regions
	palette.atlas_roots = mapping.roots
	return palette.atlas_texture != null

func _validate_atlas_mapping(data: Variant) -> Dictionary:
	if not data is Dictionary or not data.get("tiles") is Array or data.tiles.size() != 16:
		return {}
	if not data.get("asset") is String or not data.asset.begins_with("res://assets/textures/") or not ResourceLoader.exists(data.asset):
		return {}
	var regions: Array[Rect2] = []
	var roots: Array[Vector2] = []
	regions.resize(16)
	roots.resize(16)
	var seen: Dictionary = {}
	for tile: Variant in data.tiles:
		if not tile is Dictionary or not typeof(tile.get("index")) in [TYPE_INT, TYPE_FLOAT]:
			return {}
		var index := int(tile.index)
		if float(index) != float(tile.index) or index < 0 or index > 15 or seen.has(index):
			return {}
		var rect: Variant = tile.get("atlas_region_xywh")
		var root_uv: Variant = tile.get("root_in_crop_uv")
		if not rect is Array or rect.size() != 4 or not root_uv is Array or root_uv.size() != 2:
			return {}
		for value: Variant in rect + root_uv:
			if not typeof(value) in [TYPE_INT, TYPE_FLOAT] or not is_finite(float(value)):
				return {}
		var region := Rect2(float(rect[0]), float(rect[1]), float(rect[2]), float(rect[3]))
		var root_uv_value := Vector2(float(root_uv[0]), float(root_uv[1]))
		if region.position.x < 0.0 or region.position.y < 0.0 or region.size.x <= 0.0 or region.size.y <= 0.0 or region.end.x > 1.000001 or region.end.y > 1.000001:
			return {}
		if root_uv_value.x < 0.0 or root_uv_value.x > 1.0 or root_uv_value.y < 0.0 or root_uv_value.y > 1.0:
			return {}
		regions[index] = region
		roots[index] = root_uv_value
		seen[index] = true
	return {"asset": data.asset, "regions": regions, "roots": roots}

func _index(node: Node) -> void:
	if node is Node3D:
		nodes_by_name[_key(node.name)] = node
		base_transforms[node] = node.transform
	for child in node.get_children():
		_index(child)

func _key(value: String) -> String:
	return value.to_lower().replace("_", "").replace("-", "").replace(" ", "").replace(".", "")

func part(part_name: String) -> Node3D:
	return nodes_by_name.get(_key(part_name)) as Node3D

func _bind_water() -> void:
	water_material = ShaderMaterial.new()
	water_material.resource_name = "PaintedDepthAndContactWater"
	water_material.shader = load("res://shaders/coastal_water.gdshader")
	water_material.set_shader_parameter("reflected_sky", load("res://assets/textures/coastal_cumulus_panorama.png"))
	water_material.set_shader_parameter("sky_reflection_strength", 0.18)
	water_material.set_shader_parameter("depth_range", 1.0)
	water_material.set_shader_parameter("foam_width", 0.085)
	if accepted_style or OS.get_cmdline_user_args().has("--atmosphere-preview"):
		water_material.set_shader_parameter("deep_water", Color(0.05, 0.34, 0.59))
		water_material.set_shader_parameter("glint_strength", 0.38)
		water_material.set_shader_parameter("foam_strength", 0.42)
	for key: String in nodes_by_name:
		var node: Node3D = nodes_by_name[key]
		if node is MeshInstance3D and ("ocean" in key or key.begins_with("water")) and not "foam" in key:
			node.material_override = water_material
			node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF

func _bind_motion() -> void:
	for end in ["Front", "Rear"]:
		var wheel := _bind_wheel(end)
		if wheel != null:
			wheel_pivots.append(wheel)
	var crank := part("Crank")
	if crank != null:
		crank_pivot = _pivot_at_bounds(crank, "CrankSpin")
	else:
		var arms: Array[Node3D] = []
		for side in ["L", "R"]:
			var arm := part("CrankArm" + side)
			if arm != null:
				arms.append(arm)
		if not arms.is_empty():
			crank_pivot = Node3D.new()
			crank_pivot.name = "CrankSpin"
			imported_world.add_child(crank_pivot)
			crank_pivot.global_position = crank_center
			for arm in arms:
				arm.reparent(crank_pivot, true)
			base_transforms[crank_pivot] = crank_pivot.transform
	# Optional authored drivetrain detail rotates with the exact crank assembly.
	var chainring := part("CrankChainring")
	if chainring != null and crank_pivot != null and not crank_pivot.is_ancestor_of(chainring):
		chainring.reparent(crank_pivot, true)
	for key: String in nodes_by_name:
		var node: Node3D = nodes_by_name[key]
		if key.begins_with("pelican") or key.begins_with("wing") or key.begins_with("eye") or key.begins_with("cheek") or key.begins_with("tuft") or key.begins_with("crest") or key.begins_with("scarf") or "nostril" in key:
			rider_parts.append(node)
		if key.begins_with("eye"):
			eyes.append(node)
		if key.begins_with("rideaccent"):
			motion_accents.append(node)
	for side in ["L", "R"]:
		var foot := part("Foot" + side)
		if foot == null:
			continue
		var rig: Dictionary = {
			"side": side,
			"foot_half_height": world_bounds(foot).size.y * 0.5,
			"pedal_half_height": 0.025,
			"foot": _pivot_at_bounds(foot, "FootPose" + side)
		}
		for segment in ["UpperLeg", "LowerLeg", "Pedal"]:
			var source := part(segment + side)
			if source != null:
				if segment == "Pedal":
					rig["pedal_half_height"] = world_bounds(source).size.y * 0.5
				rig[segment] = _pivot_at_bounds(source, segment + "Pose" + side)
		rig["contact_lift"] = rig["foot_half_height"] + rig["pedal_half_height"] - 0.005
		leg_rigs.append(rig)
	_animate()

func _bind_wheel(end: String) -> Node3D:
	var authored_group := part(end + "Wheel")
	if authored_group != null:
		return _pivot_at_bounds(authored_group, end + "WheelSpin")
	var pieces: Array[Node3D] = []
	for prefix in ["Tire", "Rim", "Spokes", "Hub"]:
		var source := part(prefix + end)
		if source != null:
			pieces.append(source)
	if pieces.is_empty():
		return null
	var pivot := Node3D.new()
	pivot.name = end + "WheelSpin"
	imported_world.add_child(pivot)
	pivot.global_position = world_bounds(pieces[0]).get_center()
	for piece in pieces:
		piece.reparent(pivot, true)
	base_transforms[pivot] = pivot.transform
	return pivot

func _pivot_at_bounds(node: Node3D, pivot_name: String) -> Node3D:
	var pivot := Node3D.new()
	pivot.name = pivot_name
	var bounds := world_bounds(node)
	node.get_parent().add_child(pivot)
	pivot.global_position = bounds.get_center() if bounds.size.length_squared() > 0.0001 else node.global_position
	node.reparent(pivot, true)
	base_transforms[pivot] = pivot.transform
	return pivot

func world_bounds(node: Node3D) -> AABB:
	var bounds := AABB()
	var first := true
	var pending: Array[Node] = [node]
	while not pending.is_empty():
		var current: Node = pending.pop_back()
		if current is MeshInstance3D:
			var box: AABB = current.global_transform * current.get_aabb()
			bounds = box if first else bounds.merge(box)
			first = false
		for child in current.get_children():
			pending.append(child)
	return bounds

func _process(delta: float) -> void:
	if not paused:
		ride_time += delta
		distance_m += delta * speed_kmh / 3.6
		_animate()
	_update_camera(delta)
	if hud != null:
		hud.queue_redraw()

func _animate() -> void:
	if palette != null:
		palette.set_time(ride_time)
	if water_material != null:
		water_material.set_shader_parameter("ride_clock", ride_time)
	var wheel_phase := distance_m / wheel_radius
	var phase := wheel_phase * 0.46
	var bob := sin(phase * 2.0) * 0.014
	for wheel in wheel_pivots:
		wheel.transform = base_transforms[wheel]
		wheel.rotate_object_local(Vector3.FORWARD, wheel_phase)
	if crank_pivot != null:
		crank_pivot.transform = base_transforms[crank_pivot]
		crank_pivot.rotate_object_local(Vector3.FORWARD, phase)
	for node in rider_parts:
		node.transform = base_transforms[node]
		if not _has_rider_parent(node):
			node.position.y += bob
	for eye in eyes:
		var blink_phase := fmod(ride_time, 6.4)
		var blink := 1.0 - 0.86 * maxf(0.0, 1.0 - absf(blink_phase - 5.6) / 0.085)
		var ancestor := eye.get_parent()
		var inherited_blink := false
		while ancestor != null and ancestor != imported_world:
			if ancestor in eyes:
				inherited_blink = true
				break
			ancestor = ancestor.get_parent()
		if not inherited_blink:
			eye.scale.y *= blink
	_pose_legs(phase, bob)
	for node in motion_accents:
		node.transform = base_transforms[node]
		node.position.x = fposmod(node.position.x - distance_m + 16.0, 32.0) - 16.0

func _has_rider_parent(node: Node3D) -> bool:
	var ancestor := node.get_parent()
	while ancestor != null and ancestor != imported_world:
		if ancestor in rider_parts:
			return true
		ancestor = ancestor.get_parent()
	return false

func _pose_legs(phase: float, bob: float) -> void:
	for rig in leg_rigs:
		var is_left: bool = rig["side"] == "L"
		var cycle := phase + (0.0 if is_left else PI)
		var lateral := leg_lateral if is_left else -leg_lateral
		var pedal := crank_center + Vector3(sin(cycle) * crank_radius, cos(cycle) * crank_radius, lateral)
		var foot: Node3D = rig["foot"]
		foot.global_position = pedal + Vector3(0.0, rig["contact_lift"], 0.0)
		foot.global_basis = Basis.IDENTITY
		if rig.has("Pedal"):
			var pedal_pivot: Node3D = rig["Pedal"]
			pedal_pivot.global_position = pedal
			pedal_pivot.global_basis = Basis.IDENTITY
		var hip := hip_center + Vector3(0.0, bob, lateral)
		var ankle := foot.global_position + Vector3(0.0, rig["foot_half_height"] * 0.75, 0.0)
		var knee := solve_knee(hip, ankle)
		if rig.has("UpperLeg"):
			_pose_segment(rig["UpperLeg"], hip, knee)
		if rig.has("LowerLeg"):
			_pose_segment(rig["LowerLeg"], knee, ankle)

func solve_knee(hip: Vector3, ankle: Vector3) -> Vector3:
	var delta := ankle - hip
	var length := maxf(delta.length(), 0.0001)
	var direction := delta / length
	var reachable := clampf(length, absf(upper_leg_length - lower_leg_length) + 0.001, upper_leg_length + lower_leg_length - 0.001)
	var along := (upper_leg_length * upper_leg_length - lower_leg_length * lower_leg_length + reachable * reachable) / (2.0 * reachable)
	var bend := sqrt(maxf(0.0, upper_leg_length * upper_leg_length - along * along))
	return hip + direction * along + Vector3(-direction.y, direction.x, 0.0).normalized() * bend

func _pose_segment(pivot: Node3D, start: Vector3, end: Vector3) -> void:
	var delta := end - start
	var basis := Basis(Quaternion(Vector3.UP, delta.normalized()))
	basis = basis * Basis.from_scale(Vector3(1.0, (delta.length() + 0.035) / authored_leg_length, 1.0))
	pivot.global_transform = Transform3D(basis, (start + end) * 0.5)

func _camera_offset() -> Vector3:
	match camera_mode:
		1: return Vector3(-3.8, 1.1, 7.5)
		2: return Vector3(7.0, 0.85, 4.65) if beauty_preview else Vector3(7.7, 1.3, 5.2)
		_: return Vector3(5.3, 1.9, 6.7)

func _camera_target() -> Vector3:
	if camera_mode == 1:
		return Vector3(-0.4, 1.55, -0.4)
	if camera_mode == 2 and beauty_preview:
		return Vector3(0.50, 1.50, -0.60)
	return Vector3(0.05, 1.7, 0.0) if camera_mode == 2 else Vector3(-0.15, 1.55, 0.0)

func _camera_angles() -> Vector2:
	var base := _camera_offset()
	return Vector2(atan2(base.x, base.z), atan2(base.y, Vector2(base.x, base.z).length()))

func _azimuth_limits() -> Vector2:
	if camera_mode == 1:
		return Vector2(MIN_AZIMUTH, 0.45)
	if camera_mode == 2:
		return Vector2(-0.10, MAX_AZIMUTH)
	return Vector2(MIN_AZIMUTH, MAX_AZIMUTH)

func _clamp_presentation_camera() -> void:
	var base := _camera_angles()
	var azimuth_limits := _azimuth_limits()
	orbit_yaw = clampf(base.x + orbit_yaw, azimuth_limits.x, azimuth_limits.y) - base.x
	orbit_pitch = clampf(base.y + orbit_pitch, MIN_ELEVATION, MAX_ELEVATION) - base.y
	zoom = clampf(zoom, MIN_ZOOM, MAX_ZOOM)

func _update_camera(delta: float, snap := false) -> void:
	if camera == null:
		return
	_clamp_presentation_camera()
	var target := _camera_target()
	var angles := _camera_angles() + Vector2(orbit_yaw, orbit_pitch)
	var radius := _camera_offset().length() * zoom
	var horizontal := cos(angles.y) * radius
	var offset := Vector3(sin(angles.x) * horizontal, sin(angles.y) * radius, cos(angles.x) * horizontal)
	var blend := 1.0 if snap or not camera_initialized else 1.0 - exp(-delta * 5.5)
	if snap or not camera_initialized:
		smoothed_camera_target = target
		camera.position = target + offset
	else:
		# Interpolate along the presentation arc, not a chord through the hero.
		var previous_offset := camera.position - smoothed_camera_target
		var previous_azimuth := atan2(previous_offset.x, previous_offset.z)
		var previous_elevation := atan2(previous_offset.y, Vector2(previous_offset.x, previous_offset.z).length())
		# A great-circle slerp can rise above the allowed elevation between
		# two legal endpoints. Interpolate spherical angles independently.
		var smooth_azimuth := lerp_angle(previous_azimuth, angles.x, blend)
		var smooth_elevation := lerpf(previous_elevation, angles.y, blend)
		var smooth_radius := lerpf(previous_offset.length(), radius, blend)
		var smooth_horizontal := cos(smooth_elevation) * smooth_radius
		var smooth_offset := Vector3(sin(smooth_azimuth) * smooth_horizontal, sin(smooth_elevation) * smooth_radius, cos(smooth_azimuth) * smooth_horizontal)
		smoothed_camera_target = smoothed_camera_target.lerp(target, blend)
		camera.position = smoothed_camera_target + smooth_offset
	camera.look_at(smoothed_camera_target, Vector3.UP)
	var target_fov := 34.5 if camera_mode == 2 else (36.0 if camera_mode == 1 else 39.0)
	camera.fov = lerpf(camera.fov, target_fov, blend)
	camera_initialized = true

func set_camera_mode(mode: int) -> void:
	camera_mode = clampi(mode, 0, 2)
	orbit_yaw = 0.0
	orbit_pitch = 0.0
	zoom = 1.0
	state_changed.emit()

func toggle_pause() -> void:
	paused = not paused
	state_changed.emit()

func adjust_speed(amount: float) -> void:
	speed_kmh = clampf(speed_kmh + amount, MIN_SPEED, MAX_SPEED)
	state_changed.emit()

func reset_ride() -> void:
	speed_kmh = START_SPEED
	distance_m = 0.0
	ride_time = 0.0
	paused = false
	dragging = false
	set_camera_mode(START_CAMERA)
	_animate()
	_update_camera(0.0, true)
	state_changed.emit()

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_SPACE: toggle_pause()
			KEY_PLUS, KEY_EQUAL, KEY_KP_ADD, KEY_UP: adjust_speed(2.0)
			KEY_MINUS, KEY_KP_SUBTRACT, KEY_DOWN: adjust_speed(-2.0)
			KEY_1, KEY_KP_1: set_camera_mode(0)
			KEY_2, KEY_KP_2: set_camera_mode(1)
			KEY_3, KEY_KP_3: set_camera_mode(2)
			KEY_R: reset_ride()
			KEY_ESCAPE: dragging = false
			KEY_F12: capture_viewport()
	if event is InputEventMouseButton:
		if event.button_index in [MOUSE_BUTTON_LEFT, MOUSE_BUTTON_RIGHT]:
			dragging = event.pressed
		if event.pressed and event.button_index == MOUSE_BUTTON_WHEEL_UP:
			zoom = clampf(zoom - 0.04, MIN_ZOOM, MAX_ZOOM)
		if event.pressed and event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			zoom = clampf(zoom + 0.04, MIN_ZOOM, MAX_ZOOM)
	if event is InputEventMouseMotion and dragging:
		orbit_yaw -= event.relative.x * 0.0045
		orbit_pitch -= event.relative.y * 0.003
		_clamp_presentation_camera()

func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_WINDOW_FOCUS_OUT:
		dragging = false

func capture_viewport() -> void:
	if pending_capture:
		return
	pending_capture = true
	await RenderingServer.frame_post_draw
	var directory := ProjectSettings.globalize_path("res://captures")
	DirAccess.make_dir_recursive_absolute(directory)
	var path := directory.path_join("toon_coast_camera%d.png" % (camera_mode + 1))
	var error := get_viewport().get_texture().get_image().save_png(path)
	print("Native viewport capture: ", path, " status ", error)
	pending_capture = false
