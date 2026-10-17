shader_type canvas_item;
render_mode unshaded, blend_disabled;
// Fixed GL Compatibility SDR: HSV offsets are defined in stored-sRGB values.
uniform sampler2D master_texture : filter_nearest, repeat_disable;
uniform float hue_offset;
vec3 rgb_to_hsv(vec3 c) {
	vec4 k = vec4(0.0, -1.0/3.0, 2.0/3.0, -1.0);
	vec4 p = mix(vec4(c.bg, k.wz), vec4(c.gb, k.xy), step(c.b, c.g));
	vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
	float d = q.x - min(q.w, q.y);
	float e = 1.0e-10;
	return vec3(abs(q.z + (q.w-q.y)/(6.0*d+e)), d/(q.x+e), q.x);
}
vec3 hsv_to_rgb(vec3 c) {
	vec3 p = abs(fract(c.xxx + vec3(0.0,2.0/3.0,1.0/3.0))*6.0-3.0);
	return c.z * mix(vec3(1.0), clamp(p-1.0,0.0,1.0), c.y);
}
void fragment() {
	ivec2 pixel = clamp(ivec2(UV*vec2(384.0,736.0)),ivec2(0),ivec2(383,735));
	vec4 source = texelFetch(master_texture,pixel,0);
	vec3 hsv = rgb_to_hsv(source.rgb);
	hsv.x = fract(hsv.x+hue_offset);
	COLOR = vec4(hsv_to_rgb(hsv),source.a);
}
