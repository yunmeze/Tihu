extends Node2D
## Fixed raw-texel descriptor for the approved left upright tree. Geometry stays
## in the original 1162 x 1353 frame; only the final body basis scales by 2/9.
const LEGACY = preload("res://scripts/art/hero_alpha_ground_shadow.gd")
const SHADOW_SHADER = preload("res://shaders/density_alpha_ground_shadow.gdshader")
const RAW_SIZE := Vector2i(1162, 1353)
const RAW_REFERENCE := Vector2(560, 1329)
const CAST := Vector2(1.2, 0.55)
const RAW_BLUR := 3.6
const RAW_PADDING := 8.1
const BODY_SCALE := 2.0 / 9.0
const SHADOW_COLOR := Color(0.035, 0.045, 0.055, 0.25)
const MAX_RAW_EXTENT := 8192.0

var last_error := ""
var _shadow_bounds := Rect2()
var _configuration: Dictionary = {}
var _shadow_material: ShaderMaterial

func _init() -> void:
	_shadow_material = ShaderMaterial.new()
	_shadow_material.shader = SHADOW_SHADER
	material = _shadow_material
	z_index = -1
	visible = false

## Variant entry points reject malformed external inputs without typed-call
## errors or debug-only assertions. Failure always removes the previous frame.
func prepare(texture: Variant, origin: Variant) -> bool:
	clear_frame()
	last_error = ""
	if not is_instance_valid(texture) or not texture is Texture2D:
		return _fail("A loaded raw Texture2D is required.")
	if texture is AtlasTexture:
		return _fail("Nested AtlasTexture inputs are not supported.")
	if texture.get_width() != RAW_SIZE.x or texture.get_height() != RAW_SIZE.y:
		return _fail("The approved raw texture must be exactly 1162 x 1353 texels.")
	if not texture.get_rid().is_valid():
		return _fail("The raw texture must have a valid rendering resource.")
	if not origin is Vector2 or not origin.is_finite():
		return _fail("The parent-space origin must be a finite Vector2.")
	if material != _shadow_material or _shadow_material.shader != SHADOW_SHADER:
		return _fail("The immutable density shadow material is required.")
	var body_transform := Transform2D(Vector2(BODY_SCALE, 0), Vector2(0, BODY_SCALE), origin)
	var projection := LEGACY.make_ground_projection(RAW_REFERENCE, 0.0, CAST)
	if not _valid_transform(body_transform) or not _valid_transform(projection):
		return _fail("Raw body and projection transforms must be finite and invertible.")
	var inverse := projection.affine_inverse()
	if not _valid_transform(inverse) or not _valid_transform(body_transform.affine_inverse()):
		return _fail("Raw inverse transforms must be finite and invertible.")
	var bounds := LEGACY.projected_bounds(Vector2(RAW_SIZE), projection).grow(RAW_PADDING)
	if not bounds.position.is_finite() or not bounds.size.is_finite() or bounds.size.x <= 0.0 or bounds.size.y <= 0.0 or bounds.size.x > MAX_RAW_EXTENT or bounds.size.y > MAX_RAW_EXTENT:
		return _fail("Raw shadow bounds must be finite and bounded.")
	for corner in [bounds.position, Vector2(bounds.end.x, bounds.position.y), bounds.end, Vector2(bounds.position.x, bounds.end.y)]:
		if not (body_transform * corner).is_finite():
			return _fail("Transformed raw shadow bounds must be finite.")
	transform = body_transform
	_shadow_bounds = bounds
	var parameters := {
		"body_atlas": texture, "atlas_size_px": Vector2(RAW_SIZE),
		"frame_region_px": Vector4(0, 0, RAW_SIZE.x, RAW_SIZE.y),
		"inverse_x": inverse.x, "inverse_y": inverse.y, "inverse_origin": inverse.origin,
		"blur_radius_px": RAW_BLUR, "shadow_color": SHADOW_COLOR,
	}
	for key in parameters:
		_shadow_material.set_shader_parameter(key, parameters[key])
	_configuration = {
		"projection_mode": "fixed_receiver_raw_texels", "region": Rect2i(Vector2i.ZERO, RAW_SIZE),
		"ground_reference": RAW_REFERENCE, "ground_slope": 0.0, "cast_per_height": CAST,
		"body_to_parent": body_transform, "projection": projection, "bounds": bounds,
		"blur_radius_px": RAW_BLUR, "raw_padding_px": RAW_PADDING,
		"opacity": SHADOW_COLOR.a, "compositing_passes": 1,
	}
	visible = true
	queue_redraw()
	return true

func clear_frame() -> void:
	visible = false
	_shadow_bounds = Rect2()
	_configuration.clear()
	transform = Transform2D.IDENTITY
	if _shadow_material != null:
		_shadow_material.set_shader_parameter("body_atlas", null)
	queue_redraw()

func configuration() -> Dictionary:
	return _configuration.duplicate(true)

func _fail(reason: String) -> bool:
	last_error = reason
	clear_frame()
	return false

static func _valid_transform(value: Transform2D) -> bool:
	return LEGACY.finite_transform(value) and is_finite(value.determinant()) and absf(value.determinant()) >= 0.0001

func _draw() -> void:
	if not _configuration.is_empty():
		draw_rect(_shadow_bounds, Color.WHITE)
