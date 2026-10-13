shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_never, fog_disabled;

// Shades only the artist's original subdivided Ocean. Depth-based foam follows
// the actual opaque coastline/rocks, rather than painting unrelated white rings.
uniform sampler2D scene_depth : hint_depth_texture, repeat_disable, filter_nearest;
uniform vec4 deep_water : source_color = vec4(0.075, 0.43, 0.64, 1.0);
uniform vec4 shallow_water : source_color = vec4(0.20, 0.74, 0.72, 1.0);
uniform vec4 crest_water : source_color = vec4(0.36, 0.85, 0.80, 1.0);
uniform vec4 sea_glint : source_color = vec4(0.94, 0.97, 0.83, 1.0);
uniform vec4 horizon_water : source_color = vec4(0.78, 0.89, 0.90, 1.0);
uniform sampler2D reflected_sky : source_color, repeat_enable, filter_linear_mipmap;
uniform float sky_reflection_strength = 0.0;
uniform float sky_azimuth_turns = 0.15;
uniform float sky_altitude_scale = 2.0;
uniform float ride_clock = 0.0;
uniform float glint_strength : hint_range(0.0, 0.6) = 0.18;
uniform float foam_strength : hint_range(0.0, 0.6) = 0.28;
uniform float wave_amplitude : hint_range(0.0, 0.3) = 0.055;
uniform float foam_width : hint_range(0.05, 2.0) = 0.085;
uniform float depth_range : hint_range(0.5, 20.0) = 1.0;
varying vec3 world_pos;
varying float crest;

float water_noise(vec2 p) {
	return sin(p.x * 1.7 + sin(p.y * 0.8)) * sin(p.y * 1.3 - p.x * 0.45);
}
void vertex() {
	vec3 p = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	float phase_a = p.x * 0.55 + p.z * 0.32 + ride_clock * 0.72;
	float phase_b = p.x * 0.94 - p.z * 0.46 - ride_clock * 0.65;
	float wave = sin(phase_a) + 0.38 * sin(phase_b);
	VERTEX.y += wave * wave_amplitude;
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	crest = wave;
}
void fragment() {
	float depth_raw = textureLod(scene_depth, SCREEN_UV, 0.0).r;
	// Compatibility uses OpenGL NDC [-1,1]; Forward+/Mobile use [0,1] for Z.
	#if CURRENT_RENDERER == RENDERER_COMPATIBILITY
		vec3 ndc = vec3(SCREEN_UV, depth_raw) * 2.0 - 1.0;
	#else
		vec3 ndc = vec3(SCREEN_UV * 2.0 - 1.0, depth_raw);
	#endif
	vec4 behind = INV_PROJECTION_MATRIX * vec4(ndc, 1.0);
	behind.xyz /= behind.w;
	// Vertical water depth stays consistent as the camera orbits.
	vec3 behind_world = (INV_VIEW_MATRIX * vec4(behind.xyz, 1.0)).xyz;
	float water_depth = max(0.0, world_pos.y - behind_world.y);
	// Reconstructed wall depth is not a shallow seabed: exclude steep faces
	// so finite submerged cliff/stack silhouettes cannot become cyan cuffs.
	vec3 floor_dx = dFdx(behind_world);
	vec3 floor_dy = dFdy(behind_world);
	vec3 floor_cross = cross(floor_dx, floor_dy);
	float floor_up = abs(floor_cross.y) / max(length(floor_cross), 0.00001);
	float seabed = smoothstep(0.45, 0.85, floor_up);
	float shallow = (1.0 - smoothstep(0.0, depth_range, water_depth)) * seabed;
	float large_waves = sin(world_pos.z * 0.49 + world_pos.x * 0.13 + sin(world_pos.x * 0.20) * 1.8 + ride_clock * 0.72);
	float surface_paint = water_noise(world_pos.xz * 0.17 + vec2(ride_clock * 0.018, 0.0));
	float wave_band = smoothstep(-0.28, 0.16, large_waves) * 0.10;
	float wave_ridge = smoothstep(0.70, 0.89, large_waves) * 0.035;
	float coastal_tint = 0.26 + shallow * 0.16 + wave_band + surface_paint * 0.055;
	vec3 water = mix(deep_water.rgb, shallow_water.rgb, clamp(coastal_tint, 0.0, 1.0));
	water = mix(water, crest_water.rgb, wave_ridge + max(crest, 0.0) * 0.032);
	float horizon_blend = smoothstep(28.0, 100.0, length(world_pos.xz - CAMERA_POSITION_WORLD.xz));
	water = mix(water, horizon_water.rgb, horizon_blend);
	if (sky_reflection_strength > 0.0) {
		float phase_a = world_pos.x * 0.55 + world_pos.z * 0.32 + ride_clock * 0.72;
		float phase_b = world_pos.x * 0.94 - world_pos.z * 0.46 - ride_clock * 0.65;
		vec2 slope = wave_amplitude * vec2(0.55 * cos(phase_a) + 0.3572 * cos(phase_b), 0.32 * cos(phase_a) - 0.1748 * cos(phase_b));
		vec3 surface_normal = normalize(vec3(-slope.x, 1.0, -slope.y));
		vec3 to_eye = normalize(CAMERA_POSITION_WORLD - world_pos);
		vec3 reflected = reflect(-to_eye, surface_normal);
		reflected.y *= sky_altitude_scale;
		reflected = normalize(reflected);
		vec2 reflected_uv = vec2(atan(reflected.x, reflected.z) / (2.0 * PI) + 0.5 + sky_azimuth_turns, acos(clamp(reflected.y, -1.0, 1.0)) / PI);
		vec3 sky = textureLod(reflected_sky, reflected_uv, 1.0).rgb;
		float fresnel = pow(1.0 - clamp(dot(to_eye, surface_normal), 0.0, 1.0), 3.0);
		water = mix(water, sky, sky_reflection_strength * (0.30 + 0.70 * fresnel) * (1.0 - horizon_blend));
	}
	// Broken calligraphic glints, grouped into long wave lines, soften with distance.
	float small_ripple = sin(world_pos.z * 1.7 + sin(world_pos.x * 0.58 + ride_clock * 0.28) * 1.3 + ride_clock * 0.84);
	float glint_breaks = smoothstep(0.60, 0.90, sin(world_pos.x * 0.79 + world_pos.z * 0.29));
	float ripple_aa = max(fwidth(small_ripple), 0.008);
	float glint = smoothstep(0.988 - ripple_aa, 0.988 + ripple_aa, small_ripple) * glint_breaks * glint_strength * (1.0 - horizon_blend * 0.72);
	// Two narrow moving bands at true shoreline contact, with small breaks.
	float contact = 1.0 - smoothstep(foam_width * 0.12, foam_width, water_depth);
	float foam_pulse = sin(water_depth * 16.0 - ride_clock * 1.6 + surface_paint * 2.0);
	float foam_breaks = smoothstep(0.05, 0.52, sin(world_pos.x * 2.1 + world_pos.z * 0.8 + sin(world_pos.z * 1.5)) + surface_paint * 0.6);
	float foam = contact * smoothstep(-0.55, 0.12, foam_pulse) * (foam_strength + surface_paint * 0.08) * foam_breaks * (1.0 - horizon_blend * 0.92);
	ALBEDO = mix(water, sea_glint.rgb, max(glint, foam));
	// An opaque-looking transparent-pass surface permits access to scene depth.
	// It intentionally does not refract, sort with itself, or require SSR/Vulkan.
	ALPHA = 1.0;
}
