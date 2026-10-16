extends "res://scripts/earth/s_walk_contact_v3_compositor.gd"
## One new local tree contribution; old five, idle and walk code remain inherited.
const TREE_SHADER="res://shaders/earth_upright_51_70.gdshader"
const TREE_SHADER_SHA="3fbd82add41474f094defcdc45a4ffb431a27a66938441aebff9c6e3b53598b5"
var tree_active=false
func clear_tree() -> void:
 tree_active=false;_material.set_shader_parameter("tree_pilot_active",false)
func clear_frame() -> void:
 super.clear_frame();clear_tree()
func prepare(path:Variant=TREE_SHADER) -> bool:
 clear_frame();prepared=false;walk_gate.reset();error="tree common shader closure"
 if not path is String or path!=TREE_SHADER or not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=TREE_SHADER_SHA:return false
 for pin in [[WALK_SHADER_PATH,WALK_SHADER_SHA],[SHADER_PATH,SHADER_SHA]]:
  if not FileAccess.file_exists(pin[0]) or FileAccess.get_sha256(pin[0])!=pin[1]:return false
 var shader=load(path)
 if not shader is Shader:return false
 _expected_shader=shader;_material.shader=shader;material=_material
 _material.set_shader_parameter("tint",Color(.035,.045,.055,1));prepared=true;error="";return true
func set_tree(enabled:bool,gate,camera:Vector2,world) -> bool:
 clear_tree()
 if not enabled:return false
 if not prepared or material!=_material or _material.shader!=_expected_shader or _expected_shader==null:clear_frame();return false
 if _material.get_shader_parameter("tint")!=Color(.035,.045,.055,1):clear_frame();return false
 if not camera.is_finite() or not gate.valid(world):return false
 _material.set_shader_parameter("tree_pilot_body",gate.body)
 _material.set_shader_parameter("tree_pilot_receiver",gate.receiver)
 _material.set_shader_parameter("tree_pilot_camera",camera)
 _material.set_shader_parameter("tree_pilot_active",true);tree_active=true;visible=true;queue_redraw();return true
