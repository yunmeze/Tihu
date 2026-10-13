shader_type spatial;
render_mode diffuse_lambert, specular_disabled, fog_disabled;

// Verified Compatibility baseline: authored sRGB ALBEDO, native ambient, and
// stepped direct lighting. Pouch-only fill uses a bounded native emission input;
// there is no cross-stage color subtraction or complete-color light injection.
uniform vec4 base_color : source_color = vec4(0.97, 0.94, 0.87, 1.0);
// Only the UV-authored head/body candidate enables this original flow painting.
// The measured neutral is in the same source_color space as the sampled image.
uniform sampler2D feather_albedo : source_color, repeat_enable, filter_linear_mipmap_anisotropic;
uniform vec4 feather_neutral : source_color = vec4(0.945284, 0.892300, 0.804740, 1.0);
uniform float feather_strength : hint_range(0.0, 1.0) = 0.0;
uniform float terminator = 0.14;
uniform float band_softness = 0.11;
uniform float material_roughness = 0.88;
uniform float vertex_ao_strength : hint_range(0.0, 0.4) = 0.0;
uniform float shadow_fill = 0.0;
uniform float direct_gain = 1.0;
uniform bool graphic_bands = false;
uniform vec3 direct_tint = vec3(1.0);
uniform vec4 shadow_emission : source_color = vec4(0.0, 0.0, 0.0, 1.0);
uniform vec3 fill_tint = vec3(1.0);
uniform float highlight_strength = 0.008;
uniform float highlight_size = 0.12;
uniform float rim_strength = 0.0;
uniform vec4 rim_color : source_color = vec4(1.0, 0.91, 0.71, 1.0);
void fragment() {
	vec3 feather_pigment = vec3(1.0);
	if (feather_strength > 0.0) {
		vec3 texel = texture(feather_albedo, vec2(UV.x, clamp(UV.y, 0.002, 0.998))).rgb;
		// The image contributes pigment, never a second light or a white boost.
		vec3 ratio = clamp(texel / max(feather_neutral.rgb, vec3(0.05)), vec3(0.72), vec3(1.0));
		feather_pigment = mix(vec3(1.0), ratio, feather_strength);
	}
	ALBEDO = base_color.rgb * feather_pigment;
	EMISSION = (base_color.rgb * shadow_fill * fill_tint + shadow_emission.rgb) * feather_pigment;
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
	// Only the key-facing grazing silhouette receives this optional narrow rim.
	// It is off by default until its per-family native A/B is reviewed.
	float grazing = pow(1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0), 5.0);
	float rim_mask = grazing * smoothstep(0.10, 0.60, ndotl);
	SPECULAR_LIGHT += rim_color.rgb * rim_mask * rim_strength * ATTENUATION * LIGHT_COLOR / PI;
}
