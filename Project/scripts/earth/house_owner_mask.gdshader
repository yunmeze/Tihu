shader_type canvas_item;
uniform sampler2D owner_mask : filter_nearest, repeat_disable;
uniform vec3 screen_to_local_x;
uniform vec3 screen_to_local_y;
uniform vec2 master_local_origin;
uniform int coordinate_mode = 2;
uniform bool diagnostic = false;
varying vec4 command_color;
void vertex() { command_color = COLOR; }
void fragment() {
 // Only explicitly encoded house commands use this path. Other world draws retain default COLOR.
 if (command_color.g == 0.0 && command_color.b == 1.0 && command_color.a == 1.0 && command_color.r > 0.0 && command_color.r < 0.05) {
  int expected = int(round(command_color.r * 255.0));
  vec4 shared_color = texture(TEXTURE, UV);
  vec2 local = vec2(dot(screen_to_local_x,vec3(FRAGCOORD.xy,1.0)),dot(screen_to_local_y,vec3(FRAGCOORD.xy,1.0)));
  vec2 common_master = (local - master_local_origin) * 2.0;
  ivec2 p = ivec2(floor(coordinate_mode == 2 ? common_master : UV * vec2(1024.0)));
  int id = 0;
  if (p.x >= 0 && p.y >= 0 && p.x < 1024 && p.y < 1024) { id = int(round(texelFetch(owner_mask, p, 0).r * 255.0)); }
  COLOR = shared_color;
  float gate = coordinate_mode == 0 ? 1.0 : float(id == expected);
  COLOR.a *= gate;
  if (diagnostic) { COLOR = vec4(1.0,1.0,1.0,gate); }
 }
}
