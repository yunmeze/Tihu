shader_type spatial;
render_mode unshaded, fog_disabled;

// Distant authored land is a low-contrast painted silhouette. Keeping local
// lighting subdued avoids a dark underwater rim against the pale sea horizon.
uniform vec4 base_color : source_color = vec4(0.38, 0.58, 0.64, 1.0);
uniform vec4 haze_color : source_color = vec4(0.66, 0.81, 0.84, 1.0);
uniform float atmospheric_depth = 0.3;
varying vec3 world_normal;
void vertex() {
	world_normal = normalize(MODEL_NORMAL_MATRIX * NORMAL);
}
void fragment() {
	float haze = clamp(0.24 + atmospheric_depth * 0.70, 0.30, 0.76);
	vec3 color = mix(base_color.rgb, haze_color.rgb, haze);
	float form = dot(normalize(world_normal), normalize(vec3(-0.3, 0.85, 0.25)));
	ALBEDO = color + form * 0.022;
}
