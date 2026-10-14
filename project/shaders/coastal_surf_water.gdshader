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
// Numeric, linear-distance field generated from the authored coast at sea level.
uniform sampler2D shore_distance : repeat_disable, filter_linear;
uniform vec4 shore_rect = vec4(-25.0, -25.0, 50.0, 50.0);
uniform bool shore_field_ready = false;
// Original grayscale artwork is scalar data, intentionally without source_color.
uniform sampler2D foam_pattern : repeat_enable, filter_linear_mipmap;
uniform vec3 sun_direction = vec3(-0.25, 0.68, 0.69);
uniform float surf_strength = 0.84;
varying vec3 world_pos;
varying float crest;

float water_noise(vec2 p) {
	return sin(p.x * 1.7 + sin(p.y * 0.8)) * sin(p.y * 1.3 - p.x * 0.45);
}
float hash_water(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
}
float soft_noise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash_water(i), hash_water(i + vec2(1.0, 0.0)), f.x), mix(hash_water(i + vec2(0.0, 1.0)), hash_water(i + vec2(1.0, 1.0)), f.x), f.y);
}
void vertex() {
	vec3 p = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	float phase_a = p.x * 0.55 + p.z * 0.32 + ride_clock * 0.72;
	float phase_b = p.x * 0.94 - p.z * 0.46 - ride_clock * 0.65;
	float wave = sin(phase_a) + 0.38 * sin(phase_b);
	// Keep the far horizon level even when the local water moves.
	float displacement_fade = 1.0 - smoothstep(20.0, 65.0, length(p.xz));
	VERTEX.y += wave * wave_amplitude * displacement_fade;
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
	vec2 flow = vec2(dot(world_pos.xz, vec2(0.94, 0.34)), dot(world_pos.xz, vec2(-0.34, 0.94)));
	float water_patch = soft_noise(flow * vec2(0.18, 0.30) + vec2(ride_clock * 0.024, 0.0));
	float surface_paint = water_noise(world_pos.xz * 0.17 + vec2(ride_clock * 0.018, 0.0));
	float broad_phase = flow.y * 1.68 + water_patch * 2.4 + sin(flow.x * 0.32) * 0.65 + ride_clock * 0.62;
	float large_waves = sin(broad_phase) + 0.24 * sin(broad_phase * 2.0 - 0.9);
	float cross_swells = sin(flow.y * 2.42 - flow.x * 0.31 + water_patch * 6.1 - ride_clock * 0.48);
	float near_detail = 1.0 - smoothstep(14.0, 36.0, length(world_pos.xz - CAMERA_POSITION_WORLD.xz));
	float distant_envelope = mix(1.0, 0.66 + water_patch * 0.66, 1.0 - near_detail);
	float wave_band = smoothstep(-0.45, 0.50, large_waves) * mix(0.01, 0.34, near_detail) * distant_envelope;
	float wave_ridge = smoothstep(0.26, 0.93, large_waves) * smoothstep(-0.62, 0.64, cross_swells) * 0.21 * near_detail;
	float coastal_tint = 0.13 + shallow * 0.16 + wave_band + surface_paint * 0.025 + (water_patch - 0.5) * 0.11 * near_detail;
	vec3 water = mix(deep_water.rgb, shallow_water.rgb, clamp(coastal_tint, 0.0, 1.0));
	float trough = (1.0 - smoothstep(-0.90, -0.24, large_waves)) * near_detail;
	water *= 1.0 - trough * 0.13;
	water = mix(water, crest_water.rgb, wave_ridge + max(crest, 0.0) * 0.025 * near_detail);
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
	// Fine crests follow the same warped current rather than independent dashes.
	float small_ripple = sin(broad_phase * 2.7 + flow.x * 0.19 + sin(flow.x * 1.5) * 0.65);
	float glint_breaks = smoothstep(0.30, 0.64, water_patch) * smoothstep(-0.4, 0.8, cross_swells);
	glint_breaks *= smoothstep(0.40, 0.72, soft_noise(flow * vec2(0.82, 0.55) + vec2(ride_clock * 0.03, 0.0)));
	float ripple_aa = max(fwidth(small_ripple), 0.012);
	float glint = smoothstep(0.985 - ripple_aa, 0.985 + ripple_aa, small_ripple) * glint_breaks * glint_strength * mix(0.12, 1.0, near_detail);
	vec3 to_eye = normalize(CAMERA_POSITION_WORLD - world_pos);
	vec3 normal_wave = normalize(vec3(-cos(broad_phase) * 0.11, 1.0, -cos(broad_phase + 0.6) * 0.15));
	vec3 half_sun = normalize(to_eye + normalize(sun_direction));
	float sun_region = pow(max(dot(normal_wave, half_sun), 0.0), 22.0);
	float reflection_glint = sun_region * smoothstep(0.85 - ripple_aa, 0.99 + ripple_aa, small_ripple) * (0.12 + 0.23 * water_patch) * near_detail;
	// Two narrow moving bands at true shoreline contact, with small breaks.
	float contact = 1.0 - smoothstep(foam_width * 0.12, foam_width, water_depth);
	float foam_pulse = sin(water_depth * 16.0 - ride_clock * 1.6 + surface_paint * 2.0);
	float foam_breaks = smoothstep(0.05, 0.52, sin(world_pos.x * 2.1 + world_pos.z * 0.8 + sin(world_pos.z * 1.5)) + surface_paint * 0.6);
	float foam = contact * smoothstep(-0.55, 0.12, foam_pulse) * (foam_strength + surface_paint * 0.08) * foam_breaks * (1.0 - horizon_blend * 0.92);
	// Natural spill comes from world-space distance to actual shore segments,
	// independently of the camera/depth-buffer silhouette. It cannot create a
	// projected cyan cuff from the bottom edge of a finite submerged wall.
	float surf = 0.0;
	if (shore_field_ready) {
		vec2 shore_uv = (world_pos.xz - shore_rect.xy) / shore_rect.zw;
		float shore_valid = step(0.0, shore_uv.x) * step(shore_uv.x, 1.0) * step(0.0, shore_uv.y) * step(shore_uv.y, 1.0);
		float shore_metres = texture(shore_distance, shore_uv).r;
		vec2 foam_uv = flow * vec2(0.19, 0.28) + vec2(ride_clock * 0.012, -ride_clock * 0.020);
		float lace = texture(foam_pattern, foam_uv).r;
		float fine_lace = texture(foam_pattern, foam_uv * 2.17 + vec2(0.31, 0.63) - vec2(0.0, ride_clock * 0.006)).r;
		float broken = smoothstep(0.18, 0.65, water_patch + surface_paint * 0.12);
		float shore_wash = 1.0 - smoothstep(0.12 + water_patch * 0.10, 0.52 + water_patch * 0.43, shore_metres);
		float outward = 0.38 + 0.35 * sin(ride_clock * 0.52 + water_patch * 2.3);
		float rolling_edge = 1.0 - smoothstep(0.10, 0.31, abs(shore_metres - outward - water_patch * 0.24));
		float scattered = (1.0 - smoothstep(0.45, 1.55, shore_metres)) * smoothstep(0.67, 0.88, lace) * smoothstep(0.27, 0.63, fine_lace);
		surf = max(shore_wash * smoothstep(0.12, 0.66, lace) * 0.85, rolling_edge * smoothstep(0.22, 0.74, lace) * broken);
		surf = max(surf, scattered * 0.58) * surf_strength * shore_valid * (1.0 - horizon_blend);
		water = mix(water, shallow_water.rgb, shore_wash * broken * 0.10 * shore_valid);
	}
	ALBEDO = mix(water, sea_glint.rgb, clamp(max(max(glint, reflection_glint), max(foam, surf)), 0.0, 0.92));
	// An opaque-looking transparent-pass surface permits access to scene depth.
	// It intentionally does not refract, sort with itself, or require SSR/Vulkan.
	ALPHA = 1.0;
}
