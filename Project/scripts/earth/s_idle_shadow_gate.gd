extends RefCounted
## Complete S-only four-phase contact envelope. Never borrows the SE footprint.
const Guard=preload("res://scripts/earth/asset_guard.gd")
const Identity=preload("res://scripts/earth/instance_identity_guard.gd")
const Flat=preload("res://scripts/earth/flat_shadow_gate.gd")
const PATH="res://assets/earth/shadows/s_idle_contact_v1/manifest.json"
const SHA="0af5254fe748796c1bcb9540d8378f71b7e19a082bac6b837fa8989f7b67eab5"
const BODY="res://assets/earth/hero/s_idle_v1/body.png"
var ready=false
var texture:Texture2D
var footprint=Flat.new()
func reset():ready=false;texture=null;footprint.ready=false;footprint.spans.clear()
func prepare(path:Variant=PATH) -> bool:
 reset()
 if not path is String or path!=PATH or not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=SHA:return false
 var p=JSON.new()
 if p.parse(FileAccess.get_file_as_string(path))!=OK or not p.data is Dictionary:return false
 var r=p.data
 if not r.get("input_sha256") is Dictionary:return false
 for key in r.input_sha256:
  if not key is String or not key.begins_with("res://") or not Guard.sha256(r.input_sha256[key]) or not FileAccess.file_exists(key) or FileAccess.get_sha256(key)!=r.input_sha256[key]:return false
 if not FileAccess.file_exists(BODY):return false
 texture=Guard.texture(BODY,[2048,512],"f0ca3b8a554c175f3d0085f4a4fa55a6d192132d6cfeb443d3242bd3ab54a12e")
 if texture==null or not footprint.prepare():reset();return false
 var e=r.get("envelope")
 if not e is Dictionary or not e.get("path") is String or not FileAccess.file_exists(e.path):reset();return false
 var et=Guard.texture(e.path,[208,96],"a731de3104eccc3e35aa50b2a2cce5ac994b781cee19ea3e027fd3b57a0a9047")
 if et==null:reset();return false
 var im=et.get_image()
 if im==null or (im.is_compressed() and im.decompress()!=OK):reset();return false
 im.convert(Image.FORMAT_L8);var data=im.get_data();var count=0;footprint.spans.clear()
 for y in 96:
  var start=-1
  for x in 209:
   var value=data[y*208+x] if x<208 else 0
   if value!=0 and value!=255:reset();return false
   if value>0:count+=1
   if value>0 and start<0:start=x
   elif value==0 and start>=0:footprint.spans.append(Vector3i(start,x,y));start=-1
 if count!=6901:reset();return false
 footprint.envelope_offset=Vector2(26.5,79);footprint.ready=true;ready=true;return true
func allows(cell:Variant) -> bool:
 return ready and cell is Vector2 and cell.is_finite() and footprint.allows(cell)
func matches_body(body:Variant) -> bool:
 return ready and is_instance_valid(body) and body is Texture2D and body==texture and body.get_size()==Vector2(2048,512)
