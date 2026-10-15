shader_type canvas_item;
render_mode unshaded, blend_mix;

// Research only. Each body Sprite2D uses the SAME full raw_frozen.png.
// centered=false, no region/atlas/flip, identical global transform and white
// modulate/self_modulate. CanvasItem texture_filter must be LINEAR for both
// whole and split comparisons. Do not bind the pre-cut owner textures here.
uniform float raw_canvas_width = 1254.0;
uniform float raw_x_begin = 0.0;
uniform float raw_x_end = 1254.0;

void fragment() {
    // Fetch the intact texture BEFORE ownership rejection. UV is full-canvas.
    vec4 intact_sample = texture(TEXTURE, UV);
    float raw_x = UV.x * raw_canvas_width;
    // Shared boundary value belongs only to its RIGHT interval.
    if (raw_x < raw_x_begin || raw_x >= raw_x_end) {
        discard;
    }
    COLOR = intact_sample;
}
