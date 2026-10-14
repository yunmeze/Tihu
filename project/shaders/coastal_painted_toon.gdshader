shader_type spatial;
render_mode diffuse_lambert, specular_disabled, fog_disabled;

// Environment-only surface treatment on the same bounded native-light core.
// World-space low-frequency pigment fields vary hue and value without UV seams.
// Distant authored land loses saturation toward the coastal atmosphere.
uniform float paint_strength = 0.10;
uniform float paint_scale = 1.0;
uniform float atmospheric_depth = 0.0;
uniform vec4 haze_color : source_color = vec4(0.57, 0.76, 0.82, 1.0);
uniform sampler2D painted_albedo : source_color, repeat_enable, filter_linear_mipmap_anisotropic;
uniform vec4 painted_mean : source_color = vec4(0.5, 0.5, 0.5, 1.0);
uniform float texture_strength : hint_range(0.0, 1.0) = 0.0;
uniform float texture_scale = 0.4;
// Separate low-frequency authored stone planes; zero preserves accepted pigment.
uniform sampler2D stone_planes : source_color, repeat_enable, filter_linear_mipmap_anisotropic;
uniform vec4 stone_planes_mean : source_color = vec4(0.820675, 0.600267, 0.462129, 1.0);
uniform float stone_planes_strength : hint_range(0.0, 1.0) = 0.0;
uniform float stone_planes_scale = 0.30;
uniform sampler2D road_margin_distance : repeat_disable, filter_linear;
uniform vec4 road_margin_rect = vec4(0.0, 0.0, 1.0, 1.0);
uniform vec2 road_margin_uv_scale = vec2(1.0);
uniform vec2 road_margin_uv_offset = vec2(0.0);
uniform sampler2D road_gravel : source_color, repeat_enable, filter_linear_mipmap_anisotropic;
uniform vec4 road_gravel_mean : source_color = vec4(0.9264, 0.7980, 0.5954, 1.0);
uniform float road_wear_strength : hint_range(0.0, 1.0) = 0.0;
uniform float road_dust_strength : hint_range(0.0, 1.0) = 0.0;
uniform vec4 road_dust_color : source_color = vec4(0.7608, 0.7176, 0.5490, 1.0);
varying vec3 world_position;
varying vec3 world_normal;
uniform float ride_clock = 0.0;
uniform float wind_strength = 0.0;
uniform float wind_origin_y = 0.0;
uniform vec4 base_color : source_color = vec4(0.97, 0.94, 0.87, 1.0);
uniform float terminator = 0.14;
uniform float band_softness = 0.11;
uniform float material_roughness = 0.88;
uniform float vertex_ao_strength : hint_range(0.0, 0.4) = 0.0;
uniform float shadow_fill = 0.0;
uniform float direct_gain = 1.0;
uniform bool graphic_bands = false;
uniform vec3 ambient_tint = vec3(1.0);
uniform vec3 direct_tint = vec3(1.0);
uniform float highlight_strength = 0.008;
uniform float highlight_size = 0.12;
float hash31(vec3 p) {
	p = fract(p * 0.1031);
	p += dot(p, p.yzx + 33.33);
	return fract((p.x + p.y) * p.z);
}
float paint_noise(vec3 p) {
	vec3 i = floor(p);
	vec3 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(mix(hash31(i), hash31(i + vec3(1,0,0)), f.x),
		mix(hash31(i + vec3(0,1,0)), hash31(i + vec3(1,1,0)), f.x), f.y),
		mix(mix(hash31(i + vec3(0,0,1)), hash31(i + vec3(1,0,1)), f.x),
		mix(hash31(i + vec3(0,1,1)), hash31(i + vec3(1,1,1)), f.x), f.y), f.z);
}
void vertex() {
	vec3 rest_world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	float height_weight = clamp(rest_world.y - wind_origin_y, 0.0, 1.0);
	height_weight *= height_weight;
	float gust = sin(ride_clock * 1.15 + rest_world.x * 0.50 + rest_world.z * 0.32);
	float flutter = sin(ride_clock * 2.1 + rest_world.z * 0.8) * 0.18;
	VERTEX.x += (gust + flutter) * wind_strength * height_weight;
	VERTEX.z += sin(ride_clock * 0.82 + rest_world.x * 0.38) * wind_strength * height_weight * 0.35;
	world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	world_normal = normalize(MODEL_NORMAL_MATRIX * NORMAL);
}
void fragment() {
	float pigment = 0.0;
	if (paint_strength > 0.0) {
		pigment = paint_noise(world_position * paint_scale) * 0.72 + paint_noise(world_position * paint_scale * 2.3 + vec3(17.0)) * 0.28 - 0.5;
	}
	vec3 painted = base_color.rgb * (1.0 + pigment * paint_strength);
	painted += vec3(0.16, 0.10, -0.10) * pigment * paint_strength;
	if (texture_strength > 0.0) {
		vec3 weights = pow(abs(normalize(world_normal)), vec3(4.0));
		weights /= max(weights.x + weights.y + weights.z, 0.0001);
		vec3 p = world_position * texture_scale;
		vec3 texel = texture(painted_albedo, p.yz).rgb * weights.x
			+ texture(painted_albedo, p.xz).rgb * weights.y
			+ texture(painted_albedo, p.xy).rgb * weights.z;
		// Normalize around the measured texture mean so authored material colors
		// remain authoritative; the image contributes brush detail and minerals.
		vec3 pigment_ratio = clamp(texel / max(painted_mean.rgb, vec3(0.05)), vec3(0.65), vec3(1.35));
		painted *= mix(vec3(1.0), pigment_ratio, texture_strength);
	}
	if (stone_planes_strength > 0.0) {
		vec3 weights = pow(abs(normalize(world_normal)), vec3(5.0));
		weights /= max(weights.x + weights.y + weights.z, 0.0001);
		vec3 p = world_position * stone_planes_scale;
		vec3 planes = texture(stone_planes, p.yz + vec2(0.13, 0.37)).rgb * weights.x
			+ texture(stone_planes, p.xz + vec2(0.42, 0.18)).rgb * weights.y
			+ texture(stone_planes, p.xy + vec2(0.26, 0.43)).rgb * weights.z;
		// Source-color mean cancels the warmer image bias; no additive emission.
		vec3 planes_ratio = clamp(planes / max(stone_planes_mean.rgb, vec3(0.05)), vec3(0.55), vec3(1.45));
		painted *= mix(vec3(1.0), planes_ratio, stone_planes_strength);
	}
	if (road_wear_strength > 0.0 || road_dust_strength > 0.0) {
		vec2 road_uv = ((world_position.xz - road_margin_rect.xy) / road_margin_rect.zw) * road_margin_uv_scale + road_margin_uv_offset;
		float margin_distance = texture(road_margin_distance, road_uv).r;
		float edge = 1.0 - smoothstep(0.06, 0.40, margin_distance);
		float patches = smoothstep(0.18, 0.68, paint_noise(world_position * vec3(0.63, 0.0, 0.74)));
		if (road_wear_strength > 0.0) {
			vec3 gravel = texture(road_gravel, world_position.xz * 0.68).rgb;
			vec3 ratio = clamp(vec3(1.0) + (gravel / max(road_gravel_mean.rgb, vec3(0.05)) - vec3(1.0)) * 2.8, vec3(0.42), vec3(1.6));
			painted *= mix(vec3(1.0), ratio * vec3(0.98, 0.96, 0.93), edge * patches * road_wear_strength);
		}
		if (road_dust_strength > 0.0) {
			float dust = (1.0 - smoothstep(0.025, 0.18, margin_distance)) * patches;
			painted = mix(painted, road_dust_color.rgb, dust * road_dust_strength);
		}
	}
	float distance_haze = smoothstep(18.0, 85.0, distance(world_position, CAMERA_POSITION_WORLD)) * 0.42;
	float haze = max(atmospheric_depth, distance_haze);
	ALBEDO = mix(painted * ambient_tint, haze_color.rgb, haze);
	EMISSION = base_color.rgb * shadow_fill + haze_color.rgb * haze * 0.18;
	// COLOR.r stores scalar AO only in the optional evaluated export candidate.
	float painted_ao = mix(1.0, clamp(COLOR.r, 0.0, 1.0), vertex_ao_strength);
	ALBEDO *= painted_ao;
	EMISSION *= painted_ao;
	ROUGHNESS = material_roughness;
	METALLIC = 0.0;
	SPECULAR = 0.0;
}
void light() {
	float ndotl = dot(NORMAL, LIGHT);
	float lit_band = smoothstep(terminator - band_softness, terminator + band_softness, ndotl);
	float top_band = smoothstep(0.68 - band_softness, 0.68 + band_softness, ndotl);
	float ramp = smoothstep(-0.32, 0.16, ndotl) * 0.10 + lit_band * 0.62 + top_band * 0.18;
	if (graphic_bands) {
		ramp = lit_band * 0.62 + top_band * 0.26;
	}
	DIFFUSE_LIGHT += ramp * direct_gain * direct_tint * ATTENUATION * LIGHT_COLOR / PI;
	vec3 half_vector = normalize(LIGHT + VIEW);
	float highlight = smoothstep(1.0 - highlight_size, 1.0 - highlight_size * 0.68, dot(NORMAL, half_vector));
	SPECULAR_LIGHT += highlight * highlight_strength * lit_band * ATTENUATION * LIGHT_COLOR / PI;
}
