extends RefCounted
## Canonical JSON content only. Live floor/map identity is never cached.
const PATH="res://ground_candidate/manifest.json"
const VERSION="ground-manifest-2553-json-recursive-readonly-v1"
const KEYS=["floors","objects","windows","tile","union","inputs","reuse_count","current178","hut10","note"]
class Holder extends RefCounted:
 var data:Dictionary
static var _weak:Dictionary={}
static var parses=0
static var hits=0
static func acquire(path:String,sha:String)->RefCounted:
 if path!=PATH or sha.length()!=64 or not FileAccess.file_exists(path):return null
 var bytes=FileAccess.get_file_as_bytes(path)
 var ctx=HashingContext.new();ctx.start(HashingContext.HASH_SHA256);ctx.update(bytes)
 if ctx.finish().hex_encode()!=sha:return null
 var key=path+"|"+sha+"|"+VERSION
 if _weak.has(key):
  var existing=_weak[key].get_ref()
  if existing!=null:hits+=1;return existing
  _weak.erase(key)
 var value=JSON.parse_string(bytes.get_string_from_utf8());parses+=1
 if not value is Dictionary or value.size()!=KEYS.size():return null
 for field in KEYS:
  if not value.has(field):return null
 for field in ["floors","objects","windows","inputs","current178","hut10"]:
  if not value[field] is Array:return null
 if value.floors.size()!=2553 or value.objects.size()!=1156 or value.windows.size()!=3 or value.inputs.size()!=13 or value.current178.size()!=178 or value.hut10.size()!=10:return null
 if not value.tile is String or not value.union is String or not value.note is String or value.reuse_count!=907:return null
 if not freeze_json(value,0):return null
 var holder=Holder.new();holder.data=value;_weak[key]=weakref(holder);return holder
static func freeze_json(value,depth:int)->bool:
 if depth>32:return false
 if value is Dictionary:
  for key in value:
   if not key is String or not freeze_json(value[key],depth+1):return false
  value.make_read_only();return true
 if value is Array:
  for item in value:
   if not freeze_json(item,depth+1):return false
  value.make_read_only();return true
 return value==null or value is String or value is bool or value is int or (value is float and is_finite(value))
static func live_count()->int:
 var count=0
 for key in _weak.keys():
  if _weak[key].get_ref()==null:_weak.erase(key)
  else:count+=1
 return count
