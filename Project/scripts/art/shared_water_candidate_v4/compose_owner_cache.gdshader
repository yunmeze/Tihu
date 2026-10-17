shader_type canvas_item;
render_mode unshaded, blend_disabled;

// Recovered source, not yet compiled or proven identical to lost v4 bytes.
// All water routes consume the same D4 canonical texture, world period and LOD.
uniform sampler2D canonical_water : source_color, filter_linear, repeat_enable;
uniform sampler2D raw_bank : source_color, filter_nearest, repeat_disable;
uniform vec2 world_phase = vec2(0.0);
uniform float diagnostic_water_weight = 1.0;
uniform bool floor_only = false;
// L8 data samplers deliberately have no source_color transform or mip filtering.
uniform sampler2D core_mask : filter_nearest, repeat_disable;
uniform sampler2D support_mask : filter_nearest, repeat_disable;
uniform int spatial_mode = 0;
uniform bool output_weight_only = false;

const float DENSITY = 4.0;
const float GUTTER = 2.0;
const vec2 WATER_PERIOD = vec2(96.0, 64.0);
const vec2 BANK_LOGICAL_SIZE = vec2(192.0);

bool mask_in_bounds(ivec2 p) {
    return p.x >= 0 && p.y >= 0 && p.x < 192 && p.y < 192;
}

bool original_support(vec2 q) {
    ivec2 p = ivec2(floor(q));
    if (!mask_in_bounds(p)) {
        return false;
    }
    return texelFetch(support_mask, p, 0).r == 1.0;
}

bool original_core(vec2 q) {
    ivec2 p = ivec2(floor(q));
    if (!mask_in_bounds(p)) {
        return false;
    }
    return texelFetch(support_mask, p, 0).r == 1.0
        && texelFetch(core_mask, p, 0).r == 1.0;
}

float spatial_water_weight(vec2 q) {
    if (!original_core(q)) {
        return 0.0;
    }
    if (spatial_mode == 11) {
        // Exclude only supported noncore centers in the 3x3 D4 neighborhood.
        // Outside original support is not a protected/unresolved bank label.
        for (int dy = -1; dy <= 1; dy++) {
            for (int dx = -1; dx <= 1; dx++) {
                vec2 neighbor = q + vec2(float(dx), float(dy)) / DENSITY;
                if (original_support(neighbor) && !original_core(neighbor)) {
                    return 0.0;
                }
            }
        }
    }
    return 1.0;
}

// A D4 bank texel spans 1254/(192*4) source texels (<2), so at most
// three source texels per axis contribute. Clamp only the bank extension.
vec3 bank_area_sample(vec2 q) {
    vec2 source_size = vec2(textureSize(raw_bank, 0));
    vec2 footprint = source_size / (BANK_LOGICAL_SIZE * DENSITY);
    vec2 low = (q - vec2(0.5 / DENSITY)) * source_size / BANK_LOGICAL_SIZE;
    vec2 high = low + footprint;
    ivec2 first = ivec2(floor(low));
    ivec2 maximum = textureSize(raw_bank, 0) - ivec2(1);
    vec3 total = vec3(0.0);
    for (int y = 0; y < 3; y++) {
        for (int x = 0; x < 3; x++) {
            ivec2 p = first + ivec2(x, y);
            vec2 overlap = max(vec2(0.0), min(high, vec2(p + ivec2(1))) - max(low, vec2(p)));
            total += texelFetch(raw_bank, clamp(p, ivec2(0), maximum), 0).rgb * overlap.x * overlap.y;
        }
    }
    return total / (footprint.x * footprint.y);
}

void fragment() {
    // FRAGCOORD is already at j+0.5. Do not add another half texel.
    vec2 q = (FRAGCOORD.xy - vec2(GUTTER)) / DENSITY;
    float weight = 1.0;
    if (!floor_only) {
        weight = diagnostic_water_weight;
        if (spatial_mode == 10 || spatial_mode == 11) {
            weight = spatial_water_weight(q);
        }
    }
    vec3 result = vec3(weight);
    if (!output_weight_only) {
        // Unwrapped UV: repeat is sampler state, never a discontinuous fract().
        vec3 water = textureLod(canonical_water, (world_phase + q) / WATER_PERIOD, 0.0).rgb;
        result = water;
        if (!floor_only) {
            vec3 bank = bank_area_sample(q);
            result = mix(bank, water, weight);
        }
    }
    // Full rectangular cache is storage only; consumer draws original owners.
    COLOR = vec4(result, 1.0);
}
