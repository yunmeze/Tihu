extends "res://scripts/earth/viewport_ground_shadow.gd"
## New independent sixth contribution; immutable legacy five slots and idle API.
const WalkGate=preload("res://scripts/earth/s_walk_contact_v3_gate.gd")
const WALK_SHADER_PATH="res://shaders/earth_s_walk_contact_v3.gdshader"
const WALK_SHADER_SHA="c40ba78cea3342ae09029f7655cedf8fe375760d39123082dbdfa9a651dc92ab"
var walk_gate=WalkGate.new()
var walk_active=false
func clear_walk() -> void:
 walk_active=false;_material.set_shader_parameter("s_walk_active",false)
func clear_frame() -> void:
 super.clear_frame();clear_walk()
func prepare(path:Variant=WALK_SHADER_PATH) -> bool:
 clear_frame();prepared=false;walk_gate.reset();error="invalid S walk common shader"
 if not path is String or path!=WALK_SHADER_PATH or not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=WALK_SHADER_SHA:return false
 # Legacy source identity is preserved, but is not a substitute for the new shader pin.
 if not FileAccess.file_exists(SHADER_PATH) or FileAccess.get_sha256(SHADER_PATH)!=SHADER_SHA:return false
 var shader=load(path)
 if not shader is Shader:return false
 _expected_shader=shader;_material.shader=shader;material=_material
 _material.set_shader_parameter("tint",Color(.035,.045,.055,1))
 prepared=true;error="";return true
func bind_s_walk_frames(values:Variant) -> bool:
 clear_walk()
 return walk_gate.prepare(false) and walk_gate.bind_frames(values)
func set_s_walk(enabled:Variant,body:Variant,origin:Variant,source_id:Variant) -> bool:
 clear_walk()
 if not enabled is bool or not enabled:return false
 if not prepared or material!=_material or _material.shader!=_expected_shader or _expected_shader==null:clear_frame();return false
 if _material.get_shader_parameter("tint")!=Color(.035,.045,.055,1):clear_frame();return false
 if not walk_gate.matches_body(body,source_id):return false
 if not origin is Vector2 or not origin.is_finite() or absf(origin.x)>Guard.MAX_COORD or absf(origin.y)>Guard.MAX_COORD:return false
 _material.set_shader_parameter("s_walk_body",body)
 _material.set_shader_parameter("s_walk_origin",origin)
 _material.set_shader_parameter("s_walk_active",true)
 walk_active=true;visible=true;queue_redraw();return true
