extends RefCounted
## Fixed record-0 world footprint; never use the moving hero's envelope.
const Guard=preload("res://scripts/earth/asset_guard.gd")
const PATH="res://assets/earth/shadows/fangzhang_flat_v1/manifest.json"
const SHA="bc7fe4bba3c63b50b9a9a192912abe03fe700c35a79786bd2c1feb0bf6ce712b"
var ready=false
var configuration:Dictionary={}
func prepare(path:Variant=PATH) -> bool:
 ready=false;configuration={}
 if not path is String or not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=SHA:return false
 var parser=JSON.new()
 if parser.parse(FileAccess.get_file_as_string(path))!=OK or not parser.data is Dictionary:return false
 var r:Dictionary=parser.data
 for input in r.runtime_input_sha256:
  var p="res://"+input
  if not FileAccess.file_exists(p) or FileAccess.get_sha256(p)!=r.runtime_input_sha256[input]:return false
 if not FileAccess.file_exists(r.allowed.texture) or not FileAccess.file_exists(r.envelope.texture):return false
 var a=Guard.texture(r.allowed.texture,r.allowed.texture_size,r.allowed.sha256)
 var e=Guard.texture(r.envelope.texture,r.envelope.texture_size,r.envelope.sha256)
 if a==null or e==null:return false
 var ai=a.get_image();var ei=e.get_image()
 if ai==null or ei==null:return false
 if ai.is_compressed() and ai.decompress()!=OK:return false
 if ei.is_compressed() and ei.decompress()!=OK:return false
 ai.convert(Image.FORMAT_L8);ei.convert(Image.FORMAT_L8)
 if ai.get_size()!=Vector2i(1536,1024) or ei.get_size()!=ai.get_size():return false
 var ad=ai.get_data();var ed=ei.get_data();var count=0
 for i in ed.size():
  if ed[i]!=0 and ed[i]!=255:return false
  if ad[i]!=0 and ad[i]!=255:return false
  if ed[i]>0:
   count+=1
   if ad[i]!=255:return false
 if count==0:return false
 configuration=r;ready=true;return true
