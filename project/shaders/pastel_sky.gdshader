shader_type sky;

uniform vec4 horizon_color : source_color = vec4(0.78, 0.90, 0.92, 1.0);
uniform vec4 zenith_color : source_color = vec4(0.38, 0.67, 0.88, 1.0);
uniform vec4 warm_haze : source_color = vec4(1.0, 0.84, 0.63, 1.0);
uniform sampler2D cloud_panorama : source_color, repeat_enable, filter_linear_mipmap;
uniform float cloud_strength = 0.0;
uniform float cloud_altitude_scale = 2.0;
uniform float cloud_azimuth_turns = 0.25;
uniform sampler2D sky_sector : source_color, repeat_disable, filter_linear_mipmap;
uniform float sky_sector_strength = 0.0;
uniform float sky_sector_center = -2.12;
uniform float sky_sector_span = 1.40;
uniform float sky_sector_height = 0.70;
void sky() {
	float altitude = smoothstep(-0.06, 0.28, EYEDIR.y);
	vec3 sky_color = mix(horizon_color.rgb, zenith_color.rgb, altitude);
	vec3 sun_direction = normalize(vec3(-0.58, 0.35, -0.73));
	float warm_scatter = pow(max(dot(EYEDIR, sun_direction), 0.0), 8.0) * 0.20;
	sky_color = mix(sky_color, warm_haze.rgb, warm_scatter);
	float horizon_mist = exp(-abs(EYEDIR.y + 0.015) * 24.0) * 0.13;
	sky_color = mix(sky_color, horizon_color.rgb, horizon_mist);
	if (cloud_strength > 0.0) {
		vec3 panorama_direction = normalize(vec3(EYEDIR.x, EYEDIR.y * cloud_altitude_scale, EYEDIR.z));
		vec2 panorama_uv = vec2(atan(panorama_direction.x, panorama_direction.z) / (2.0 * PI) + 0.5 + cloud_azimuth_turns, acos(clamp(panorama_direction.y, -1.0, 1.0)) / PI);
		// Explicit LOD avoids a false coarse-mip line at atan's angular discontinuity.
		vec3 painted_sky = textureLod(cloud_panorama, panorama_uv, 0.0).rgb;
		float clear_horizon = smoothstep(0.015, 0.050, EYEDIR.y);
		sky_color = mix(sky_color, painted_sky, cloud_strength * clear_horizon);
	}
	if (sky_sector_strength > 0.0) {
		float angle = atan(EYEDIR.x, EYEDIR.z);
		float delta = atan(sin(angle - sky_sector_center), cos(angle - sky_sector_center));
		vec2 sector_uv = vec2(0.5 - delta / sky_sector_span, 0.66 - asin(clamp(EYEDIR.y, -1.0, 1.0)) / sky_sector_height);
		float side_fade = smoothstep(0.0, 0.10, sector_uv.x) * (1.0 - smoothstep(0.90, 1.0, sector_uv.x));
		float top_fade = smoothstep(-0.04, 0.10, sector_uv.y);
		float horizon_fade = smoothstep(0.015, 0.065, EYEDIR.y);
		vec3 sector = textureLod(sky_sector, clamp(sector_uv, vec2(0.0), vec2(1.0)), 0.0).rgb;
		float luminance = dot(sector, vec3(0.2126, 0.7152, 0.0722));
		sector = mix(vec3(luminance), sector, 0.76);
		sector = mix(sector, horizon_color.rgb, 0.05);
		sky_color = mix(sky_color, sector, sky_sector_strength * side_fade * top_fade * horizon_fade);
	}
	COLOR = sky_color;
}
