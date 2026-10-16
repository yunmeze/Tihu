extends RefCounted
## Controlled immutable ImageTexture bank. Weak entries do not retain unused maps.
const MANIFEST="res://assets/earth/first_map_review/plant_shared_bank_v1.json"
const MANIFEST_SHA="0e4c6a9663bb4ff092088216103fdb3e3897e04a9a880566b5d0bfb214eeab8e"
static var _weak:Dictionary={}
static var hits=0
static var misses=0
static func rgba_hash(data:PackedByteArray)->String:
 var ctx=HashingContext.new();ctx.start(HashingContext.HASH_SHA256);ctx.update(data);return ctx.finish().hex_encode()
static func acquire(path:String,digest:String,size:Vector2i)->Texture2D:
 if not path.begins_with("res://assets/") or path.simplify_path()!=path or ".." in path:return null
 # Every request checks current bytes before consulting cache, including hits.
 if not FileAccess.file_exists(path):return null
 var raw=FileAccess.get_file_as_bytes(path)
 if rgba_hash(raw)!=digest:return null
 if FileAccess.get_sha256(MANIFEST)!=MANIFEST_SHA:return null
 var spec=JSON.parse_string(FileAccess.get_file_as_string(MANIFEST))
 if not spec is Dictionary or spec.get("schema")!="verified-plant-texture-bank-v1" or not spec.get("entries") is Array or spec.entries.size()!=21:return null
 var entry={}
 for row in spec.entries:
  if row.path==path:
   if not entry.is_empty():return null
   entry=row
 if entry.is_empty() or entry.sha256!=digest or (not entry.size is Array or entry.size.size()!=2 or entry.size[0]!=size.x or entry.size[1]!=size.y) or entry.contract!="rgba8/no_mipmaps/linear/clamp/v1":return null
 var key=path+"|"+digest+"|"+str(size)+"|"+entry.rgba_sha256+"|"+entry.contract
 if _weak.has(key):
  var found=_weak[key].get_ref()
  if found!=null and found is ImageTexture and found.get_size()==Vector2(size):hits+=1;return found
  _weak.erase(key)
 var im=Image.new()
 if im.load_png_from_buffer(raw)!=OK or im.get_size()!=size:return null
 im.convert(Image.FORMAT_RGBA8)
 if rgba_hash(im.get_data())!=entry.rgba_sha256:return null
 var result=ImageTexture.create_from_image(im)
 _weak[key]=weakref(result);misses+=1;return result
static func live_count()->int:
 var count=0
 for key in _weak.keys():
  if _weak[key].get_ref()==null:_weak.erase(key)
  else:count+=1
 return count
