shader_type spatial;
render_mode cull_disabled, diffuse_lambert, specular_disabled, fog_disabled;

// Original painted foliage on the authored bowed-card mesh. Alpha scissor keeps
// genuine depth/cast-shadow silhouettes; no camera-facing billboard is created.
uniform sampler2D foliage_atlas : source_color, repeat_disable, filter_linear_mipmap_anisotropic;
uniform vec4 atlas_region = vec4(0.0, 0.0, 0.25, 0.25);
uniform vec4 foliage_tint : source_color = vec4(1.0);
uniform float ride_clock = 0.0;
uniform float wind_strength = 0.028;
uniform float card_height = 1.0;
uniform float card_width = 1.0;
uniform vec2 root_in_crop_uv = vec2(0.5, 1.0);
uniform float alpha_cutoff = 0.45;
// Compatibility converts fragment EMISSION from sRGB after this stage.
// A 0.42 encoded fill remains modest in linear light; native proof required.
uniform float painted_fill = 0.42;
uniform vec4 haze_color : source_color = vec4(0.57, 0.76, 0.82, 1.0);
varying vec3 world_position;
varying float leaf_height;
void vertex() {
	VERTEX.x -= (root_in_crop_uv.x - 0.5) * card_width;
	VERTEX.y -= (1.0 - root_in_crop_uv.y) * card_height;
	vec3 rest_world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	leaf_height = clamp(VERTEX.y / max(card_height, 0.01), 0.0, 1.0);
	float anchor = leaf_height * leaf_height;
	VERTEX.x += sin(ride_clock * 1.15 + rest_world.x * 0.5 + rest_world.z * 0.32) * wind_strength * anchor;
	VERTEX.z += sin(ride_clock * 0.82 + rest_world.x * 0.38) * wind_strength * 0.35 * anchor;
	world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}
void fragment() {
	vec2 sample_uv = atlas_region.xy + clamp(UV, vec2(0.001), vec2(0.999)) * atlas_region.zw;
	vec4 painted = texture(foliage_atlas, sample_uv);
	ALPHA = painted.a;
	ALPHA_SCISSOR_THRESHOLD = alpha_cutoff;
	vec3 color = painted.rgb * foliage_tint.rgb;
	// A low, cool root zone anchors the cutout without adding noisy texture.
	color *= mix(vec3(0.90, 0.95, 0.94), vec3(1.0), smoothstep(0.05, 0.55, leaf_height));
	float haze = smoothstep(18.0, 85.0, distance(world_position, CAMERA_POSITION_WORLD)) * 0.42;
	ALBEDO = mix(color, haze_color.rgb, haze);
	EMISSION = color * painted_fill * (1.0 - haze) + haze_color.rgb * haze * 0.18;
	if (!FRONT_FACING) { NORMAL = -NORMAL; }
	ROUGHNESS = 1.0;
	SPECULAR = 0.0;
}
void light() {
	// Wrapped two-sided plant illumination prevents perpendicular card planes
	// becoming black while retaining coherent native shadow attenuation.
	float ndotl = dot(NORMAL, LIGHT);
	float band = smoothstep(-0.08, 0.20, ndotl);
	float top = smoothstep(0.57, 0.71, ndotl);
	float ramp = 0.12 + band * 0.52 + top * 0.20;
	DIFFUSE_LIGHT += ramp * vec3(1.20, 1.13, 0.75) * ATTENUATION * LIGHT_COLOR / PI;
}
