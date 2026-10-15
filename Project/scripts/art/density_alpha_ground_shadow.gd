class_name DensityAlphaGroundShadow
extends Node2D
## Explicit texture-density adapter for one immutable-alpha flat-ground cast.
## All caller geometry is LOGICAL pixels; raw density is applied exactly once.
## Existing HeroAlphaGroundShadow APIs, shader and constants are unchanged.

const LEGACY = preload("res://scripts/art/hero_alpha_ground_shadow.gd")
const SHADOW_SHADER = preload("res://shaders/density_alpha_ground_shadow.gdshader")
const MAX_TEXTURE_DENSITY := 4.0
const MAX_RAW_FRAME_SIZE_PX := 2048
const MAX_RAW_SHADOW_EXTENT_PX := 8192.0
const MAX_LOGICAL_BLUR_RADIUS_PX := 3.0
const MAX_OPACITY := 0.42
const MIN_LOGICAL_DETERMINANT := 0.025

var last_error := ""
var _shadow_bounds := Rect2()
var _shadow_material: ShaderMaterial
var _configuration: Dictionary = {}

func _init() -> void:
	_shadow_material = ShaderMaterial.new()
	_shadow_material.shader = SHADOW_SHADER
	material = _shadow_material
	visible = false
	texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR

## logical_region is in the density-one atlas coordinate system, including its
## position. raw_region=logical_region*density; the supplied texture is raw-sized.
## logical_body_to_parent transforms LOGICAL frame pixels, not raw texels.
## Reference and blur are logical; cast and slope are dimensionless and unchanged.
func configure_density_ground_frame(body_atlas: Texture2D, logical_region: Rect2i,
		texture_density: float, logical_body_to_parent: Transform2D,
		logical_ground_reference: Vector2, ground_slope: float,
		cast_per_height: Vector2, opacity: float = 0.30,
		logical_blur_px: float = 0.9,
		tint: Color = Color(0.035, 0.045, 0.055)) -> bool:
	clear_frame()
	last_error = validate_density_inputs(body_atlas, logical_region, texture_density,
		logical_body_to_parent, logical_ground_reference, ground_slope,
		cast_per_height, opacity, logical_blur_px, tint)
	if not last_error.is_empty():
		return false
	var d := int(texture_density)
	var raw_region := Rect2i(logical_region.position * d, logical_region.size * d)
	var raw_reference := logical_ground_reference * texture_density
	var raw_projection := LEGACY.make_ground_projection(raw_reference, ground_slope, cast_per_height)
	var inverse := raw_projection.affine_inverse()
	var logical_blur := clampf(logical_blur_px, 0.0, MAX_LOGICAL_BLUR_RADIUS_PX)
	var raw_blur := logical_blur * texture_density
	var raw_padding := (logical_blur + 1.0) * texture_density
	_shadow_bounds = LEGACY.projected_bounds(Vector2(raw_region.size), raw_projection).grow(raw_padding)
	var raw_transform := raw_body_transform(logical_body_to_parent, texture_density)
	transform = raw_transform
	_shadow_material.set_shader_parameter("body_atlas", body_atlas)
	_shadow_material.set_shader_parameter("atlas_size_px", body_atlas.get_size())
	_shadow_material.set_shader_parameter("frame_region_px", Vector4(raw_region.position.x, raw_region.position.y, raw_region.size.x, raw_region.size.y))
	_shadow_material.set_shader_parameter("inverse_x", inverse.x)
	_shadow_material.set_shader_parameter("inverse_y", inverse.y)
	_shadow_material.set_shader_parameter("inverse_origin", inverse.origin)
	_shadow_material.set_shader_parameter("blur_radius_px", raw_blur)
	_shadow_material.set_shader_parameter("shadow_color", Color(clampf(tint.r, 0.0, 1.0), clampf(tint.g, 0.0, 1.0), clampf(tint.b, 0.0, 1.0), clampf(opacity, 0.0, MAX_OPACITY)))
	_configuration = {
		"projection_mode": "fixed_receiver_texture_density",
		"texture_density": texture_density,
		"logical_region": logical_region, "region": raw_region,
		"logical_ground_reference": logical_ground_reference, "ground_reference": raw_reference,
		"ground_slope": ground_slope, "cast_per_height": cast_per_height,
		"logical_body_to_parent": logical_body_to_parent, "body_to_parent": raw_transform,
		"logical_projection": LEGACY.make_ground_projection(logical_ground_reference, ground_slope, cast_per_height),
		"projection": raw_projection, "bounds": _shadow_bounds,
		"logical_bounds": Rect2(_shadow_bounds.position / texture_density, _shadow_bounds.size / texture_density),
		"requested_logical_blur_radius_px": logical_blur_px,
		"logical_blur_radius_px": logical_blur, "blur_radius_px": raw_blur,
		"logical_padding_px": logical_blur + 1.0, "raw_padding_px": raw_padding,
		"opacity": clampf(opacity, 0.0, MAX_OPACITY), "compositing_passes": 1,
	}
	visible = true
	queue_redraw()
	return true

func clear_frame() -> void:
	visible = false
	_shadow_bounds = Rect2()
	_configuration.clear()
	queue_redraw()

## Supply the moving/camera-updated LOGICAL body transform; never pre-divide it.
func set_logical_body_transform(logical_body_to_parent: Transform2D) -> bool:
	if not LEGACY.finite_transform(logical_body_to_parent) or absf(logical_body_to_parent.determinant()) < MIN_LOGICAL_DETERMINANT:
		last_error = "Logical body transform must be finite and invertible."
		clear_frame()
		return false
	if _configuration.is_empty():
		return false
	transform = raw_body_transform(logical_body_to_parent, _configuration.texture_density)
	_configuration["logical_body_to_parent"] = logical_body_to_parent
	_configuration["body_to_parent"] = transform
	last_error = ""
	return true

func configuration() -> Dictionary:
	return _configuration.duplicate(true)

func _draw() -> void:
	if not _configuration.is_empty():
		draw_rect(_shadow_bounds, Color.WHITE)

static func raw_body_transform(logical_transform: Transform2D, density: float) -> Transform2D:
	# Divide the two basis vectors only. A screen/world translation is not scaled.
	return Transform2D(logical_transform.x / density, logical_transform.y / density, logical_transform.origin)

static func validate_density_inputs(body_atlas: Texture2D, logical_region: Rect2i,
		density: float, logical_transform: Transform2D, reference: Vector2,
		slope: float, cast: Vector2, opacity: float, logical_blur: float, tint: Color) -> String:
	if body_atlas == null or body_atlas.get_width() <= 0 or body_atlas.get_height() <= 0:
		return "A loaded, body-only alpha Texture2D is required."
	if body_atlas is AtlasTexture:
		return "Pass the underlying raw atlas Texture2D plus an explicit logical region."
	if not is_finite(density) or density < 1.0 or density > MAX_TEXTURE_DENSITY or density != floorf(density):
		return "Texture density must be an exact integer within 1..4."
	if logical_region.size.x <= 0 or logical_region.size.y <= 0 or float(logical_region.size.x) * density > MAX_RAW_FRAME_SIZE_PX or float(logical_region.size.y) * density > MAX_RAW_FRAME_SIZE_PX:
		return "Raw frame dimensions (logical size times density) must be within 1..2048 texels."
	# Float end arithmetic precedes integer multiplication to avoid overflow.
	if logical_region.position.x < 0 or logical_region.position.y < 0 or (float(logical_region.position.x) + logical_region.size.x) * density > body_atlas.get_width() or (float(logical_region.position.y) + logical_region.size.y) * density > body_atlas.get_height():
		return "Density-scaled frame region must be entirely inside the explicit raw atlas."
	if not LEGACY.finite_transform(logical_transform) or absf(logical_transform.determinant()) < MIN_LOGICAL_DETERMINANT:
		return "Logical body transform must be finite and invertible."
	if not reference.is_finite() or not is_finite(slope) or not cast.is_finite():
		return "Logical reference, slope and cast must be finite."
	if absf(slope) > LEGACY.MAX_CONTACT_SLOPE:
		return "Ground-line slope is outside the bounded flat-ground range."
	if not Rect2(Vector2.ZERO, Vector2(logical_region.size)).grow(1.0).has_point(reference):
		return "Ground reference must lie within the logical frame, allowing one logical edge pixel."
	var projection := LEGACY.make_ground_projection(reference, slope, cast)
	if cast.length() > 2.0 or absf(projection.determinant()) < LEGACY.MIN_DETERMINANT:
		return "Cast projection is singular, too compressed, or outside the bounded flat-ground range."
	var raw_extent := LEGACY.projected_bounds(Vector2(logical_region.size), projection).size * density
	if raw_extent.x > MAX_RAW_SHADOW_EXTENT_PX or raw_extent.y > MAX_RAW_SHADOW_EXTENT_PX:
		return "Raw projected frame exceeds the bounded shadow extent."
	if not is_finite(opacity) or not is_finite(logical_blur) or not is_finite(tint.r) or not is_finite(tint.g) or not is_finite(tint.b):
		return "Opacity, logical blur and tint must be finite."
	return ""
