shader_type canvas_item;
render_mode unshaded, blend_mix;

// Body-only RGBA, supplied explicitly by the caller. RGB is never examined.
uniform sampler2D body_atlas : filter_linear, repeat_disable;
uniform vec2 atlas_size_px = vec2(1.0);
uniform vec4 frame_region_px = vec4(0.0, 0.0, 1.0, 1.0);
uniform vec2 inverse_x = vec2(1.0, 0.0);
uniform vec2 inverse_y = vec2(0.0, 1.0);
uniform vec2 inverse_origin = vec2(0.0);
uniform float blur_radius_px : hint_range(0.0, 3.0) = 0.9;
uniform vec4 shadow_color : source_color = vec4(0.035, 0.045, 0.055, 0.30);

varying vec2 shadow_position_px;

void vertex() {
	shadow_position_px = VERTEX;
}

float projected_alpha(vec2 ground_position) {
	vec2 p = inverse_x * ground_position.x + inverse_y * ground_position.y + inverse_origin;
	// Reject before clamping. Clamp each in-frame bilinear footprint to texel
	// centers so neither atlas neighbors nor their mipmaps can enter this frame.
	if (any(lessThan(p, vec2(0.0))) || any(greaterThanEqual(p, frame_region_px.zw))) {
		return 0.0;
	}
	vec2 pixel_center = clamp(p, vec2(0.5), frame_region_px.zw - vec2(0.5));
	vec2 uv = (frame_region_px.xy + pixel_center) / atlas_size_px;
	return textureLod(body_atlas, uv, 0.0).a;
}

void fragment() {
	// A single normalized 3x3 kernel, in projected/frame pixels. This is one
	// shadow compositing pass, not overlapping cast/contact shadow layers.
	float alpha = 0.0;
	for (int y = -1; y <= 1; y++) {
		for (int x = -1; x <= 1; x++) {
			float weight = (x == 0 ? 2.0 : 1.0) * (y == 0 ? 2.0 : 1.0);
			alpha += weight * projected_alpha(shadow_position_px + vec2(float(x), float(y)) * blur_radius_px);
		}
	}
	// Cap final opacity even if a caller bypasses the helper's validation.
	COLOR = vec4(shadow_color.rgb, clamp(alpha / 16.0, 0.0, 1.0) * clamp(shadow_color.a, 0.0, 0.42));
}
