extends Node2D
## Five explicitly gated density-shadow descriptors; one common-light blend.
const Density=preload("res://scripts/art/density_alpha_ground_shadow.gd")
const Raw=preload("res://scripts/earth/raw_ground_shadow.gd")
const Guard=preload("res://scripts/earth/asset_guard.gd")
const SHADER_PATH="res://shaders/earth_max_ground_shadow.gdshader"
const SHADER_SHA="273309ffbc426414782d21f8229fd02ee90152c0865b0fb144ef9e125daad103"
var prepared=false
var _expected_shader:Shader
var active_slots:Array=[false,false,false,false,false]
var error="not prepared"
var _material=ShaderMaterial.new()
func _init():material=_material;z_index=-1;visible=false
func clear_frame():
 visible=false;active_slots=[false,false,false,false,false]
 for i in 5:_material.set_shader_parameter("active%d"%i,false)
 queue_redraw()
func prepare(path:Variant=SHADER_PATH) -> bool:
 clear_frame();prepared=false;error="invalid common shader"
 if not path is String or path!=SHADER_PATH or not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=SHADER_SHA:return false
 var shader=load(path)
 if not shader is Shader:return false
 _expected_shader=shader;_material.shader=shader;material=_material;_material.set_shader_parameter("tint",Color(.035,.045,.055,1));prepared=true;error="";return true
func configure(nodes:Variant) -> bool:
 clear_frame()
 if not prepared or material!=_material or _material.shader!=_expected_shader or _expected_shader==null:return false
 var tint=_material.get_shader_parameter("tint")
 if not tint is Color or tint!=Color(.035,.045,.055,1):error="invalid common tint";return false
 if not nodes is Array or nodes.size()!=5:return false
 var staged=[]
 for slot_index in 5:
  var node=nodes[slot_index]
  if not is_instance_valid(node) or not node is Node2D or node.get_script()!=(Raw if slot_index==4 else Density):staged.append({});continue
  var c=node.configuration()
  if c.is_empty():staged.append({});continue
  var old=node.material
  if not old is ShaderMaterial or old.shader!=Density.SHADOW_SHADER:staged.append({});continue
  var color=old.get_shader_parameter("shadow_color")
  # All slots share one physical light; incompatible common tint fails all.
  if not color is Color or color!=Color(.035,.045,.055,.25):error="incompatible common tint/opacity";return false
  var texture=old.get_shader_parameter("body_atlas")
  var transform_value=c.get("body_to_parent");var bounds=c.get("bounds")
  if not texture is Texture2D or not transform_value is Transform2D or not bounds is Rect2:staged.append({});continue
  if not Density.LEGACY.finite_transform(transform_value) or not is_finite(transform_value.determinant()) or absf(transform_value.determinant())<.0001 or not bounds.position.is_finite() or not bounds.size.is_finite() or bounds.size.x<=0 or bounds.size.y<=0:staged.append({});continue
  var values={};var valid=true
  for pair in [["atlas","body_atlas"],["size","atlas_size_px"],["region","frame_region_px"],["px","inverse_x"],["py","inverse_y"],["po","inverse_origin"],["blur","blur_radius_px"]]:values[pair[0]]=old.get_shader_parameter(pair[1])
  for key in ["size","px","py","po"]:
   if not values[key] is Vector2 or not values[key].is_finite():valid=false
  if not values.region is Vector4 or not values.region.is_finite() or not Guard.number(values.blur,0,12):valid=false
  if not valid:staged.append({});continue
  if values.size!=texture.get_size() or values.region.z<=0 or values.region.w<=0 or values.region.x<0 or values.region.y<0 or values.region.x+values.region.z>values.size.x or values.region.y+values.region.w>values.size.y:staged.append({});continue
  var inverse=transform_value.affine_inverse()
  if not Density.LEGACY.finite_transform(inverse):staged.append({});continue
  values.bx=inverse.x;values.by=inverse.y;values.bo=inverse.origin
  values.bounds=Vector4(bounds.position.x,bounds.position.y,bounds.size.x,bounds.size.y);values.opacity=color.a
  staged.append(values)
 for i in 5:
  if staged[i].is_empty():continue
  for key in staged[i]:_material.set_shader_parameter(key+str(i),staged[i][key])
  _material.set_shader_parameter("active%d"%i,true);active_slots[i]=true
 visible=true;error="";queue_redraw();return true
func _draw():
 if prepared:draw_rect(Rect2(0,0,768,512),Color.WHITE)
