shader_type canvas_item;
render_mode unshaded, blend_disabled;
// Reconstructed from preserved design after host loss. Not engine revalidated.
// Fixed1536x1024 original water ->384x256 D4 cache, exact4x4 box footprint.
uniform sampler2D raw_water : source_color, filter_nearest, repeat_disable;
void fragment() {
    ivec2 first = ivec2(floor(FRAGCOORD.xy)) * 4;
    vec3 total = vec3(0.0);
    for (int dy = 0; dy < 4; dy++) {
        for (int dx = 0; dx < 4; dx++) {
            total += texelFetch(raw_water, first + ivec2(dx, dy), 0).rgb;
        }
    }
    COLOR = vec4(total / 16.0, 1.0);
}
