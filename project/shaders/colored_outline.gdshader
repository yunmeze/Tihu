shader_type spatial;
render_mode unshaded, cull_front, shadows_disabled;

// Inverted hull uses the exact imported mesh as a second pass, not new geometry.
// Clip-space expansion keeps selective hero outlines approximately pixel-sized.
uniform vec4 outline_color : source_color = vec4(0.35, 0.31, 0.34, 1.0);
uniform float outline_pixels : hint_range(0.0, 3.0) = 0.9;
void vertex() {
	vec4 clip = PROJECTION_MATRIX * MODELVIEW_MATRIX * vec4(VERTEX, 1.0);
	vec3 view_normal = normalize(MODELVIEW_NORMAL_MATRIX * NORMAL);
	vec2 projected_normal = (PROJECTION_MATRIX * vec4(view_normal, 0.0)).xy;
	float normal_length = max(length(projected_normal), 0.001);
	clip.xy += projected_normal / normal_length * outline_pixels * 2.0 / VIEWPORT_SIZE * clip.w;
	POSITION = clip;
}
void fragment() {
	ALBEDO = outline_color.rgb;
}
