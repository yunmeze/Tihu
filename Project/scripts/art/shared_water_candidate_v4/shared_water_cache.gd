extends Node
## Independently recovered probe source. Not verified byte-identical to lost v4.
## Missing masks and an unpinned module must fail closed. No production integration.
signal completed(request_id: int, ok: bool, reason: String)

const MODULE_ROOT := "res://scripts/art/shared_water_candidate_v4"
const PINS_SHA := "PLACEHOLDER"
const DENSITY := 4
const GUTTER := 2
const PERIOD := Vector2i(96, 64)
const PHASES := [Vector2i(0, 32), Vector2i(48, 0)]
const TIMEOUT_MSEC := 10000
const SPATIAL_MODES := {"binary_negative_control": 10, "core_inset": 11}
const MASK_SIZE := Vector2i(192, 192)
const PINS_SCHEMA := "shared-water-real-mask-probe-pins-v4"
const MASK_SCHEMA := "shared-water-real-mask-contract-v4"
const READY_STATUS := "MASK_READY_FOR_ISOLATED_PROBE"
var _serial: int = 0
var _post_draw: int = 0
var _job: Dictionary = {}
var _active: Dictionary = {}
var _retired: Array[Dictionary] = []
var last_error: String = ""
# Mandatory external correctness gate. Never publish an unvalidated generation.
var diagnostic_validator: Callable

func _ready() -> void:
	RenderingServer.frame_post_draw.connect(_after_draw)

func request_prepare(workspace_root: String, diagnostic_mask: int, module_root: String = MODULE_ROOT) -> int:
	# Legacy numeric entry point remains limited to the two constant controls.
	return _request_prepare(workspace_root, diagnostic_mask, "", false, module_root)

func request_prepare_spatial(workspace_root: String, mode: String, module_root: String = MODULE_ROOT) -> int:
	# Color and weight-only entries are always prepared in one atomic bundle.
	var selector: int = int(SPATIAL_MODES.get(mode, -1))
	return _request_prepare(workspace_root, selector, mode, true, module_root)

func _request_prepare(workspace_root: String, selector: int, spatial_mode: String, spatial_request: bool, module_root: String) -> int:
	cancel_pending("Superseded by a new request")
	_serial += 1
	var ticket: int = _serial
	last_error = ""
	if not is_inside_tree():
		_reject_later(ticket, "Cache service must be attached to the scene tree")
		return ticket
	if spatial_request and not SPATIAL_MODES.has(spatial_mode):
		_reject_later(ticket, "Unknown real-mask probe mode")
		return ticket
	if not spatial_request and selector not in [0, 1]:
		_reject_later(ticket, "Only diagnostic constant masks 0 and 1 are authorized")
		return ticket
	if RenderingServer.get_current_rendering_method() != "gl_compatibility" or get_viewport().use_hdr_2d:
		_reject_later(ticket, "Fixture requires GL Compatibility and SDR 2D")
		return ticket
	var loaded: Dictionary = _load_verified_inputs(workspace_root, module_root)
	if loaded.is_empty():
		_reject_later(ticket, last_error)
		return ticket
	var staging: Node = Node.new()
	staging.name = "StagedCache_%d" % ticket
	add_child(staging)
	_job = {"ticket": ticket, "root": staging, "inputs": loaded,
		"mask": selector, "entries": {}, "weight_entries": {}, "viewports": [],
		"spatial_mode": spatial_mode, "module_root": module_root,
		"step": "canonical", "started": _now_msec(), "armed_after": _post_draw,
		"key": PINS_SHA + ":D4:g2:area:SDR:LOD0:m%d" % selector}
	if spatial_request:
		_job.key = PINS_SHA + ":D4:g2:area:SDR:LOD0:spatial:" + spatial_mode
	var parameters: Dictionary = {"raw_water": loaded.water}
	_job.canonical = _make_pass(Vector2i(384, 256), loaded.canonical_shader, parameters)
	return ticket

func cancel_pending(reason: String = "Cancelled") -> void:
	if _job.is_empty():
		return
	var ticket: int = _job.ticket
	var cancelled: Dictionary = _job
	_job = {}
	_destroy_bundle(cancelled)
	# Do not resume listeners in the middle of an enclosing prepare or clear.
	_send_result.call_deferred(ticket, false, reason)

func clear() -> void:
	cancel_pending("Cache cleared")
	_destroy_bundle(_active)
	_active = {}
	for bundle in _retired:
		_destroy_bundle(bundle)
	_retired.clear()

func snapshot() -> Dictionary:
	# Borrowed handles. Keep this service alive and refresh after completion.
	return _active.duplicate(false)

func phase_key(origin: Vector2i) -> String:
	return "%d,%d" % [posmod(origin.x, PERIOD.x), posmod(origin.y, PERIOD.y)]

func owner_region(local_rect: Rect2) -> Rect2:
	return Rect2(Vector2(GUTTER, GUTTER) + local_rect.position * DENSITY,
		local_rect.size * DENSITY)

func _load_verified_inputs(root_path: String, module_root: String = MODULE_ROOT) -> Dictionary:
	if PINS_SHA == "PLACEHOLDER":
		last_error = "Unpinned recovery module; mask rebuild and pin verification required"
		return {}
	var pin_bytes: PackedByteArray = _verified_bytes(module_root.path_join("INPUT_PINS.json"), PINS_SHA)
	if pin_bytes.is_empty():
		return {}
	var parsed_pins: Variant = JSON.parse_string(pin_bytes.get_string_from_utf8())
	if not parsed_pins is Dictionary or parsed_pins.get("schema") != PINS_SCHEMA:
		last_error = "Invalid pin document"
		return {}
	var pins: Dictionary = parsed_pins
	if not pins.get("external_sha256") is Dictionary or not pins.get("module_sha256") is Dictionary:
		last_error = "Pin document is missing hash dictionaries"
		return {}
	for required in ["FIXTURE_OWNERS.json", "MASK_CONTRACT.json", "canonical_water.gdshader",
		"compose_owner_cache.gdshader", "data/core.png", "data/state.png", "data/support.png"]:
		if not pins.module_sha256.has(required):
			last_error = "Missing required module pin: " + str(required)
			return {}
	if not pins.get("water_raw") is String or not pins.get("bank_raw") is String:
		last_error = "Pin document is missing raw image paths"
		return {}
	if not pins.external_sha256.has(pins.water_raw) or not pins.external_sha256.has(pins.bank_raw):
		last_error = "Raw image paths are not pinned"
		return {}
	var retained: Dictionary = {}
	for relative in pins.external_sha256:
		var data: PackedByteArray = _verified_bytes(root_path.path_join(relative), pins.external_sha256[relative])
		if data.is_empty():
			return {}
		if relative in [pins.water_raw, pins.bank_raw]:
			retained[relative] = data
	var module_bytes: Dictionary = {}
	for relative in pins.module_sha256:
		var data: PackedByteArray = _verified_bytes(module_root.path_join(relative), pins.module_sha256[relative])
		if data.is_empty():
			return {}
		module_bytes[relative] = data
	var mask_inputs: Dictionary = _decode_verified_masks(module_bytes)
	if mask_inputs.is_empty():
		return {}
	var parsed_owners: Variant = JSON.parse_string(module_bytes["FIXTURE_OWNERS.json"].get_string_from_utf8())
	if not parsed_owners is Dictionary or parsed_owners.get("schema") != "shared-water-fixture-owners-v1":
		last_error = "Invalid original owner contract"
		return {}
	var owners: Dictionary = parsed_owners
	if not owners.get("family") is Dictionary or owners.get("density") != DENSITY or owners.get("gutter_pixels") != GUTTER:
		last_error = "Original owner contract policy changed"
		return {}
	if owners.family.get("id") != "shore-1668-1676" or owners.family.get("owner_count") != 27:
		last_error = "Original owner family changed"
		return {}
	if not owners.family.get("template") is Array or not owners.family.get("instances") is Array:
		last_error = "Original owner windows are missing"
		return {}
	if owners.family.template.size() != 9 or owners.family.instances.size() != 3:
		last_error = "Original owner windows or instances changed"
		return {}
	var water: Image = Image.new()
	var bank: Image = Image.new()
	if water.load_png_from_buffer(retained[pins.water_raw]) != OK or bank.load_png_from_buffer(retained[pins.bank_raw]) != OK:
		last_error = "Pinned PNG decode failed"
		return {}
	if water.get_size() != Vector2i(1536, 1024) or bank.get_size() != Vector2i(1254, 1254):
		last_error = "Pinned PNG dimensions changed"
		return {}
	if water.detect_alpha() != Image.ALPHA_NONE or bank.detect_alpha() != Image.ALPHA_NONE:
		last_error = "Input is not fully opaque"
		return {}
	var canonical: Shader = Shader.new()
	canonical.code = module_bytes["canonical_water.gdshader"].get_string_from_utf8()
	var compose: Shader = Shader.new()
	compose.code = module_bytes["compose_owner_cache.gdshader"].get_string_from_utf8()
	if not _uniforms_present(canonical, ["raw_water"]) or not _uniforms_present(compose,
		["canonical_water", "raw_bank", "world_phase", "diagnostic_water_weight", "floor_only",
		"core_mask", "support_mask", "spatial_mode", "output_weight_only"]):
		last_error = "Shader uniform interface failed validation"
		return {}
	# Exact verified PNG decode/upload only: no CPU transforms or composition.
	return {"water": ImageTexture.create_from_image(water), "bank": ImageTexture.create_from_image(bank),
		"canonical_shader": canonical, "compose_shader": compose, "contract": owners,
		"mask_contract": mask_inputs.contract, "source_mask_images": mask_inputs.images,
		"core_mask": mask_inputs.textures.core, "state_mask": mask_inputs.textures.state,
		"support_mask": mask_inputs.textures.support, "pins": pins, "module_root": module_root}

func _decode_verified_masks(module_bytes: Dictionary) -> Dictionary:
	var parsed: Variant = JSON.parse_string(module_bytes["MASK_CONTRACT.json"].get_string_from_utf8())
	if not parsed is Dictionary:
		last_error = "Invalid real-mask contract"
		return {}
	var contract: Dictionary = parsed
	if contract.get("schema") != MASK_SCHEMA or contract.get("family") != "shore-1668-1676":
		last_error = "Wrong real-mask contract schema or family"
		return {}
	# Recovered text is not recovered mask evidence. No diagnostic bypass exists.
	if contract.get("status") != READY_STATUS or contract.get("integration") != false:
		last_error = "MASK_REBUILD_REQUIRED: isolated mask readiness is not verified"
		return {}
	var logical_size: Variant = contract.get("logical_size")
	if not logical_size is Array or logical_size.size() != 2:
		last_error = "Real-mask coordinates or modes changed"
		return {}
	if logical_size[0] != 192 or logical_size[1] != 192 or contract.get("modes") != ["binary_negative_control", "core_inset"]:
		last_error = "Real-mask coordinates or modes changed"
		return {}
	if contract.get("density") != DENSITY or contract.get("gutter_pixels") != GUTTER:
		last_error = "Real-mask cache sampling policy changed"
		return {}
	var expected_counts: Dictionary = {"core": 9402, "support": 32256, "protected": 3133, "unresolved": 19721, "outside": 4608}
	if not contract.get("counts") is Dictionary or not contract.get("files") is Dictionary:
		last_error = "Real-mask count or file contract changed"
		return {}
	if contract.counts.size() != expected_counts.size():
		last_error = "Real-mask count or file contract changed"
		return {}
	for count_name in expected_counts:
		if contract.counts.get(count_name) != expected_counts[count_name]:
			last_error = "Real-mask count or file contract changed"
			return {}
	var images: Dictionary = {}
	var bytes_by_name: Dictionary = {}
	for mask_name in ["core", "state", "support"]:
		var relative: String = "data/" + str(mask_name) + ".png"
		if contract.files.get(mask_name) != relative or not module_bytes.has(relative):
			last_error = "Real-mask path is not the verified contract path: " + str(mask_name)
			return {}
		var mask_image: Image = Image.new()
		var checked_bytes: PackedByteArray = module_bytes[relative]
		if mask_image.load_png_from_buffer(checked_bytes) != OK:
			last_error = "Pinned mask PNG decode failed: " + str(mask_name)
			return {}
		if mask_image.get_size() != MASK_SIZE or mask_image.get_format() != Image.FORMAT_L8 or mask_image.has_mipmaps():
			last_error = "Masks must be unchanged 192x192 L8 data without mipmaps: " + str(mask_name)
			return {}
		images[mask_name] = mask_image
		bytes_by_name[mask_name] = mask_image.get_data()
	var core_bytes: PackedByteArray = bytes_by_name.core
	var state_bytes: PackedByteArray = bytes_by_name.state
	var support_bytes: PackedByteArray = bytes_by_name.support
	if core_bytes.size() != 36864 or state_bytes.size() != 36864 or support_bytes.size() != 36864:
		last_error = "Unexpected mask byte count"
		return {}
	var counts: Dictionary = {"core": 0, "support": 0, "protected": 0, "unresolved": 0, "outside": 0}
	for i in range(36864):
		var core_value: int = core_bytes[i]
		var state_value: int = state_bytes[i]
		var support_value: int = support_bytes[i]
		if core_value not in [0, 255] or support_value not in [0, 255] or state_value not in [0, 127, 255]:
			last_error = "Mask contains a non-contract data value"
			return {}
		var is_core: bool = state_value == 255 and support_value == 255
		if (core_value == 255) != is_core:
			last_error = "Binary mask is not exactly supported state255"
			return {}
		if support_value == 0:
			if state_value != 127 or core_value != 0:
				last_error = "Outside-support sentinel or binary value changed"
				return {}
			counts.outside += 1
		else:
			counts.support += 1
			if state_value == 255:
				counts.core += 1
			elif state_value == 0:
				counts.protected += 1
			else:
				counts.unresolved += 1
	if counts != expected_counts:
		last_error = "Decoded real-mask counts differ from the pinned contract"
		return {}
	var textures: Dictionary = {"core": ImageTexture.create_from_image(images.core),
		"state": ImageTexture.create_from_image(images.state), "support": ImageTexture.create_from_image(images.support)}
	return {"contract": contract, "images": images, "textures": textures}

func _verified_bytes(path: String, expected_sha: String) -> PackedByteArray:
	if expected_sha.length() != 64 or not expected_sha.is_valid_hex_number(false):
		last_error = "Missing or invalid SHA256 pin: " + path
		return PackedByteArray()
	if not FileAccess.file_exists(path):
		last_error = "Missing pinned input: " + path
		return PackedByteArray()
	var data: PackedByteArray = FileAccess.get_file_as_bytes(path)
	var hasher: HashingContext = HashingContext.new()
	hasher.start(HashingContext.HASH_SHA256)
	hasher.update(data)
	if hasher.finish().hex_encode() != expected_sha:
		last_error = "SHA256 mismatch: " + path
		return PackedByteArray()
	# Consume this checked buffer. Never reopen the file for decoding.
	return data

func _uniforms_present(shader: Shader, names: Array) -> bool:
	var found: Array[String] = []
	for entry in shader.get_shader_uniform_list():
		found.append(str(entry.name))
	for expected in names:
		if expected not in found:
			return false
	return true

func _make_pass(dimensions: Vector2i, shader: Shader, parameters: Dictionary) -> Dictionary:
	var viewport: SubViewport = SubViewport.new()
	viewport.size = dimensions
	viewport.disable_3d = true
	viewport.world_2d = World2D.new()
	viewport.transparent_bg = true
	viewport.use_hdr_2d = false
	viewport.msaa_2d = Viewport.MSAA_DISABLED
	viewport.render_target_clear_mode = SubViewport.CLEAR_MODE_ALWAYS
	viewport.render_target_update_mode = SubViewport.UPDATE_DISABLED
	var material: ShaderMaterial = ShaderMaterial.new()
	material.shader = shader
	for key in parameters:
		material.set_shader_parameter(key, parameters[key])
	var quad: ColorRect = ColorRect.new()
	quad.size = Vector2(dimensions)
	quad.mouse_filter = Control.MOUSE_FILTER_IGNORE
	quad.material = material
	viewport.add_child(quad)
	_job.root.add_child(viewport)
	# Attach before arming. Actual RenderingServer state confirms completion.
	viewport.render_target_update_mode = SubViewport.UPDATE_ONCE
	var texture: ViewportTexture = viewport.get_texture()
	var canvas: CanvasTexture = CanvasTexture.new()
	canvas.diffuse_texture = texture
	canvas.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	canvas.texture_repeat = CanvasItem.TEXTURE_REPEAT_DISABLED
	var entry: Dictionary = {"viewport": viewport, "texture": texture, "canvas": canvas,
		"material": material, "quad": quad, "size": dimensions}
	_job.viewports.append(viewport)
	return entry

func _after_draw() -> void:
	_post_draw += 1
	for i in range(_retired.size() - 1, -1, -1):
		if _post_draw >= int(_retired[i].retire_after):
			_destroy_bundle(_retired[i])
			_retired.remove_at(i)
	if _job.is_empty() or _post_draw <= int(_job.armed_after):
		return
	for viewport in _job.viewports:
		if not is_instance_valid(viewport) or not viewport.is_inside_tree():
			_fail_job("Staging viewport lost before publication")
			return
		if RenderingServer.viewport_get_update_mode(viewport.get_viewport_rid()) != RenderingServer.VIEWPORT_UPDATE_DISABLED:
			return
	if _job.step == "canonical":
		_job.step = "composites"
		_job.armed_after = _post_draw
		var inputs: Dictionary = _job.inputs
		var common: Dictionary = {"canonical_water": _job.canonical.texture, "raw_bank": inputs.bank,
			"world_phase": Vector2.ZERO, "diagnostic_water_weight": float(_job.mask), "floor_only": true}
		if not str(_job.spatial_mode).is_empty():
			common.core_mask = inputs.core_mask
			common.support_mask = inputs.support_mask
			common.spatial_mode = int(_job.mask)
			common.output_weight_only = false
		_job.entries.floor = _make_pass(Vector2i(388, 260), inputs.compose_shader, common)
		for phase in PHASES:
			var parameters: Dictionary = common.duplicate()
			parameters.world_phase = Vector2(phase)
			parameters.floor_only = false
			_job.entries[phase_key(phase)] = _make_pass(Vector2i(772, 772), inputs.compose_shader, parameters)
		if not str(_job.spatial_mode).is_empty():
			var weight_parameters: Dictionary = common.duplicate()
			weight_parameters.output_weight_only = true
			_job.weight_entries.floor = _make_pass(Vector2i(388, 260), inputs.compose_shader, weight_parameters)
			for phase in PHASES:
				var phase_parameters: Dictionary = weight_parameters.duplicate()
				phase_parameters.world_phase = Vector2(phase)
				phase_parameters.floor_only = false
				_job.weight_entries[phase_key(phase)] = _make_pass(Vector2i(772, 772), inputs.compose_shader, phase_parameters)
		return
	if not diagnostic_validator.is_valid():
		_fail_job("No diagnostic validator; unverified GPU output cannot publish")
		return
	# A synchronous validator can cross the deadline without allowing _process.
	# The historical 71-control suite did not cover this failure mode.
	var candidate_ticket: int = _job.ticket
	if not _check_deadline(candidate_ticket):
		return
	var validated: bool = bool(diagnostic_validator.call(_job.duplicate(false)))
	if _job.is_empty() or int(_job.ticket) != candidate_ticket:
		return
	if not _check_deadline(candidate_ticket):
		return
	if not validated:
		_fail_job("Diagnostic pixel gate rejected staged cache; active cache unchanged")
		return
	var ticket: int = _job.ticket
	var old: Dictionary = _active
	if not _check_deadline(candidate_ticket):
		return
	_active = _job
	_job = {}
	if not old.is_empty():
		old.retire_after = _post_draw + 2
		_retired.append(old)
	completed.emit(ticket, true, "")

func _process(_delta: float) -> void:
	if not _job.is_empty():
		_check_deadline(int(_job.ticket))

func _now_msec() -> int:
	# Only a separate test subclass may override this with an injected offset.
	return Time.get_ticks_msec()

func _check_deadline(ticket: int) -> bool:
	# Do not let an old validator cancel or publish a successor request.
	if _job.is_empty() or int(_job.ticket) != ticket:
		return false
	if _now_msec() - int(_job.started) > TIMEOUT_MSEC:
		_fail_job("No completed GPU pass within timeout; active cache unchanged")
		return false
	return true

func _fail_job(reason: String) -> void:
	last_error = reason
	cancel_pending(reason)

func _reject_later(ticket: int, reason: String) -> void:
	last_error = reason
	_send_result.call_deferred(ticket, false, reason)

func _send_result(ticket: int, ok: bool, reason: String) -> void:
	completed.emit(ticket, ok, reason)

func _destroy_bundle(bundle: Dictionary) -> void:
	if bundle.is_empty():
		return
	for viewport in bundle.get("viewports", []):
		if is_instance_valid(viewport):
			viewport.render_target_update_mode = SubViewport.UPDATE_DISABLED
	var branch: Node = bundle.get("root")
	if is_instance_valid(branch):
		branch.queue_free()
	bundle.clear()

func _exit_tree() -> void:
	if RenderingServer.frame_post_draw.is_connected(_after_draw):
		RenderingServer.frame_post_draw.disconnect(_after_draw)
	clear()
