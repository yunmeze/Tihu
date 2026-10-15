class_name HeroAlphaGroundShadow
extends Node2D
## One flat-ground shadow, derived from an immutable body-only alpha atlas.
## Put this CanvasItem after the floor pass and before the object/body pass.
## No asset paths, actor-origin assumptions, frame fitting or body drawing here.

const SHADOW_SHADER = preload("res://shaders/hero_alpha_ground_shadow.gdshader")
const MAX_OPACITY := 0.42
const MAX_BLUR_RADIUS_PX := 3.0
const MIN_DETERMINANT := 0.025
const MAX_FRAME_SIZE_PX := 2048
const MAX_CONTACT_SLOPE := 2.0
const MAX_SHADOW_EXTENT_PX := 8192.0

var last_error := ""
var _shadow_bounds := Rect2()
var _projection := Transform2D.IDENTITY
var _shadow_material: ShaderMaterial
var _configuration: Dictionary = {}

func _init() -> void:
	_shadow_material = ShaderMaterial.new()
	_shadow_material.shader = SHADOW_SHADER
	material = _shadow_material
	visible = false
	texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR

## All points and cast_per_height are in frame-local image pixels (y down).
## body_to_parent must be exactly the transform used for the replacement body.
## A and B are two planted-sole proxies, not the actor draw origin or joint data.
## Invalid input clears this shadow. The caller must switch body+shadow atomically.
func configure_frame(body_atlas: Texture2D, region: Rect2i,
		body_to_parent: Transform2D, sole_a: Vector2, sole_b: Vector2,
		cast_per_height: Vector2, opacity: float = 0.30,
		blur_px: float = 0.9, tint: Color = Color(0.035, 0.045, 0.055)) -> bool:
	clear_frame()
	last_error = validate_inputs(body_atlas, region, body_to_parent, sole_a,
		sole_b, cast_per_height, opacity, blur_px, tint)
	if not last_error.is_empty():
		return false
	_projection = make_projection(sole_a, sole_b, cast_per_height)
	var inverse := _projection.affine_inverse()
	var padding := clampf(blur_px, 0.0, MAX_BLUR_RADIUS_PX) + 1.0
	_shadow_bounds = projected_bounds(Vector2(region.size), _projection).grow(padding)
	transform = body_to_parent
	_shadow_material.set_shader_parameter("body_atlas", body_atlas)
	_shadow_material.set_shader_parameter("atlas_size_px", body_atlas.get_size())
	_shadow_material.set_shader_parameter("frame_region_px", Vector4(region.position.x, region.position.y, region.size.x, region.size.y))
	_shadow_material.set_shader_parameter("inverse_x", inverse.x)
	_shadow_material.set_shader_parameter("inverse_y", inverse.y)
	_shadow_material.set_shader_parameter("inverse_origin", inverse.origin)
	_shadow_material.set_shader_parameter("blur_radius_px", clampf(blur_px, 0.0, MAX_BLUR_RADIUS_PX))
	_shadow_material.set_shader_parameter("shadow_color", Color(clampf(tint.r, 0.0, 1.0), clampf(tint.g, 0.0, 1.0), clampf(tint.b, 0.0, 1.0), clampf(opacity, 0.0, MAX_OPACITY)))
	_configuration = {
		"region": region, "sole_a": sole_a, "sole_b": sole_b,
		"cast_per_height": cast_per_height, "projection": _projection,
		"bounds": _shadow_bounds, "opacity": clampf(opacity, 0.0, MAX_OPACITY),
		"blur_radius_px": clampf(blur_px, 0.0, MAX_BLUR_RADIUS_PX),
		"body_to_parent": body_to_parent, "compositing_passes": 1,
	}
	visible = true
	queue_redraw()
	return true

func clear_frame() -> void:
	visible = false
	_shadow_bounds = Rect2()
	_configuration.clear()
	queue_redraw()

## Move the already-configured body and shadow together as the camera/actor moves.
func set_body_transform(body_to_parent: Transform2D) -> bool:
	if not finite_transform(body_to_parent) or absf(body_to_parent.determinant()) < MIN_DETERMINANT:
		last_error = "Body transform must be finite and invertible."
		clear_frame()
		return false
	transform = body_to_parent
	if not _configuration.is_empty():
		_configuration["body_to_parent"] = body_to_parent
	return not _configuration.is_empty()

func configuration() -> Dictionary:
	return _configuration.duplicate(true)

func _draw() -> void:
	if not _configuration.is_empty():
		draw_rect(_shadow_bounds, Color.WHITE)

## g(x) = m*x+b is the contact line. h=g(x)-y is height above it.
## Project p to (x,g(x)) + h*cast. Both contact anchors remain fixed.
## Unlike flattening about one global y, a high-screen planted foot has h=0.
static func make_projection(sole_a: Vector2, sole_b: Vector2, cast: Vector2) -> Transform2D:
	var slope := (sole_b.y - sole_a.y) / (sole_b.x - sole_a.x)
	var intercept := sole_a.y - slope * sole_a.x
	return Transform2D(
		Vector2(1.0 + cast.x * slope, slope * (1.0 + cast.y)),
		Vector2(-cast.x, -cast.y),
		Vector2(cast.x * intercept, (1.0 + cast.y) * intercept))

static func projected_bounds(frame_size: Vector2, projection: Transform2D) -> Rect2:
	var result := Rect2(projection * Vector2.ZERO, Vector2.ZERO)
	for corner in [Vector2(frame_size.x, 0.0), frame_size, Vector2(0.0, frame_size.y)]:
		result = result.expand(projection * corner)
	return result

static func finite_transform(value: Transform2D) -> bool:
	return value.x.is_finite() and value.y.is_finite() and value.origin.is_finite()

static func validate_inputs(body_atlas: Texture2D, region: Rect2i,
		body_to_parent: Transform2D, sole_a: Vector2, sole_b: Vector2,
		cast: Vector2, opacity: float, blur_px: float, tint: Color) -> String:
	if body_atlas == null or body_atlas.get_width() <= 0 or body_atlas.get_height() <= 0:
		return "A loaded, body-only alpha Texture2D is required."
	if body_atlas is AtlasTexture:
		return "Pass the underlying atlas Texture2D plus an explicit region, not a nested AtlasTexture."
	if region.size.x <= 0 or region.size.y <= 0 or region.size.x > MAX_FRAME_SIZE_PX or region.size.y > MAX_FRAME_SIZE_PX:
		return "Frame dimensions must be within 1..2048 pixels."
	if region.position.x < 0 or region.position.y < 0 or region.end.x > body_atlas.get_width() or region.end.y > body_atlas.get_height():
		return "Frame region must be entirely inside the explicit atlas."
	if not finite_transform(body_to_parent) or absf(body_to_parent.determinant()) < MIN_DETERMINANT:
		return "Body transform must be finite and invertible."
	if not sole_a.is_finite() or not sole_b.is_finite() or not cast.is_finite():
		return "Sole anchors and cast direction must be finite."
	if absf(sole_b.x - sole_a.x) < 1.0:
		return "Two soles must have at least one pixel of horizontal separation."
	if absf((sole_b.y - sole_a.y) / (sole_b.x - sole_a.x)) > MAX_CONTACT_SLOPE:
		return "Contact-line slope is outside the bounded flat-ground range."
	var frame_bounds := Rect2(Vector2.ZERO, Vector2(region.size)).grow(1.0)
	if not frame_bounds.has_point(sole_a) or not frame_bounds.has_point(sole_b):
		return "Sole proxies must lie within the frame, allowing one edge pixel."
	if cast.length() > 2.0 or absf(make_projection(sole_a, sole_b, cast).determinant()) < MIN_DETERMINANT:
		return "Cast projection is singular, too compressed, or outside the bounded flat-ground range."
	var size := projected_bounds(Vector2(region.size), make_projection(sole_a, sole_b, cast)).size
	if size.x > MAX_SHADOW_EXTENT_PX or size.y > MAX_SHADOW_EXTENT_PX:
		return "Projected frame exceeds the bounded shadow extent."
	if not is_finite(opacity) or not is_finite(blur_px) or not is_finite(tint.r) or not is_finite(tint.g) or not is_finite(tint.b):
		return "Opacity, blur and tint must be finite."
	return ""

## CPU mirror of the shader's atlas guard, used by headless contract tests.
## Empty means transparent; otherwise uv is safely between region texel centers.
static func guarded_sample_uv(frame_pixel: Vector2, region: Rect2i, atlas_size: Vector2) -> Dictionary:
	if not atlas_size.is_finite() or atlas_size.x <= 0.0 or atlas_size.y <= 0.0 or region.size.x <= 0 or region.size.y <= 0 or region.position.x < 0 or region.position.y < 0 or region.end.x > atlas_size.x or region.end.y > atlas_size.y:
		return {}
	if not frame_pixel.is_finite() or frame_pixel.x < 0.0 or frame_pixel.y < 0.0 or frame_pixel.x >= region.size.x or frame_pixel.y >= region.size.y:
		return {}
	var center := frame_pixel.clamp(Vector2(0.5, 0.5), Vector2(region.size) - Vector2(0.5, 0.5))
	return {"uv": (Vector2(region.position) + center) / atlas_size}
