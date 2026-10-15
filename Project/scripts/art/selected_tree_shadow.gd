extends "res://scripts/art/hero_alpha_ground_shadow.gd"
## One whole-tree ground pass. Resource failure leaves the owner in source mode.
const MANIFEST="res://assets/scifi/environment/a13_first_tree_shadow_v1/shadow.json"
var whole_texture:Texture2D
var registration:Dictionary={}
var prepared:=false
func prepare(path:String=MANIFEST) -> bool:
 prepared=false;whole_texture=null;registration={};visible=false
 if not FileAccess.file_exists(path):return false
 var parser=JSON.new()
 if parser.parse(FileAccess.get_file_as_string(path))!=OK or not parser.data is Dictionary:return false
 var config:Dictionary=parser.data
 if not config.get("schema") is String or config.schema!="a13-first-tree-single-alpha-cast-v1":return false
 if not config.get("texture") is String or not ResourceLoader.exists(config.texture,"Texture2D"):return false
 if not config.get("whole_tree_registration") is Dictionary:return false
 var reg:Dictionary=config.whole_tree_registration
 if not number(reg.get("scale")) or float(reg.scale)<=0.0:return false
 if not reg.get("world_top_left") is Array or reg.world_top_left.size()!=2:return false
 for v in reg.world_top_left:
  if not number(v):return false
 # This is the accepted first-tree contract, not a generic arbitrary JSON renderer.
 if not vector_equal(config.get("texture_size"),[1254,1254]) or not vector_equal(config.get("region"),[0,0,1254,1254]):return false
 if not vector_equal(config.get("ground_reference"),[498.0,1224.0]) or not number(config.get("ground_slope")) or float(config.ground_slope)!=0.0:return false
 if not vector_equal(config.get("cast_per_height"),[148.0/279,-111.0/279]):return false
 if not number(config.get("opacity")) or not is_equal_approx(float(config.opacity),0.30):return false
 if not number(config.get("blur_radius_px")) or not is_equal_approx(float(config.blur_radius_px),3.0):return false
 var loaded=load(config.texture)
 if not loaded is Texture2D or loaded.get_size()!=Vector2(1254,1254):return false
 whole_texture=loaded;registration=reg.duplicate(true);prepared=true
 return true
func configure_at(offset:Vector2) -> bool:
 if not prepared or whole_texture==null:visible=false;return false
 var scale_value=float(registration.scale)
 var origin=Vector2(registration.world_top_left[0],registration.world_top_left[1])+offset
 return configure_ground_frame(whole_texture,Rect2i(0,0,1254,1254),Transform2D(Vector2(scale_value,0),Vector2(0,scale_value),origin),Vector2(498,1224),0.0,Vector2(148.0/279,-111.0/279),0.30,3.0)
func number(v:Variant) -> bool:
 return (v is int or v is float) and is_finite(float(v))
func vector_equal(v:Variant,expected:Array) -> bool:
 if not v is Array or v.size()!=expected.size():return false
 for i in expected.size():
  if not number(v[i]) or not is_equal_approx(float(v[i]),float(expected[i])):return false
 return true
