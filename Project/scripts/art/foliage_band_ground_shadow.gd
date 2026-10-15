class_name FoliageBandGroundShadow
extends "res://scripts/art/hero_alpha_ground_shadow.gd"
## One deliberately limited2D contact cast from the lower visible foliage band.
## The whole input/body alpha is immutable. Only shadow sampling is attenuated.
const BAND_SHADER = preload("res://shaders/foliage_band_ground_shadow.gdshader")
const MAX_BAND_FADE_PX := 512.0
func _init() -> void:
	super()
	_shadow_material.shader = BAND_SHADER

## All coordinates are frame-local/raw texels, including band/fade and blur.
## Use a raw-space parent for the exact small whole-image body transform.
func configure_foliage_band_frame(body_atlas: Texture2D, region: Rect2i,
		body_to_parent: Transform2D, ground_reference: Vector2,
		ground_slope: float, cast_per_height: Vector2,
		band_start_y: float, band_fade_px: float,
		opacity: float = 0.30, blur_px: float = 3.0,
		tint: Color = Color(0.035, 0.045, 0.055)) -> bool:
	clear_frame()
	if not is_finite(band_start_y) or not is_finite(band_fade_px) or band_start_y < 0.0 or band_start_y >= region.size.y or band_fade_px < 1.0 or band_fade_px > MAX_BAND_FADE_PX or band_start_y + band_fade_px > region.size.y:
		last_error = "Finite lower-foliage band and1..512-texel fade must fit inside the frame."
		return false
	if not super.configure_ground_frame(body_atlas, region, body_to_parent,
			ground_reference, ground_slope, cast_per_height, opacity, blur_px, tint):
		return false
	_shadow_material.set_shader_parameter("alpha_band_start_y", band_start_y)
	_shadow_material.set_shader_parameter("alpha_band_fade_px", band_fade_px)
	_configuration["alpha_source_mode"] = "limited_lower_foliage_band"
	_configuration["alpha_band_start_y"] = band_start_y
	_configuration["alpha_band_fade_px"] = band_fade_px
	return true

## CPU mirror of shadow-only alpha attenuation. No body pixels are rewritten.
static func band_weight(raw_y: float, start_y: float, fade_px: float) -> float:
	if not is_finite(raw_y) or not is_finite(start_y) or not is_finite(fade_px) or fade_px <= 0.0:
		return 0.0
	var t := clampf((raw_y - start_y) / fade_px, 0.0, 1.0)
	return t * t * (3.0 - 2.0 * t)
