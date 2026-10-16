extends RefCounted
## Immutable verified ground textures; weak cache retains no inactive world.
static var _weak:Dictionary={}
static var hits=0
static var misses=0
static func digest(bytes:PackedByteArray)->String:
 var h=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(bytes);return h.finish().hex_encode()
static func acquire(path:String,sha:String,size:Vector2i,construction:String)->ImageTexture:
 if not path.begins_with("res://") or path.simplify_path()!=path or ".." in path or sha.length()!=64:return null
 if not FileAccess.file_exists(path):return null
 var raw=FileAccess.get_file_as_bytes(path)
 if digest(raw)!=sha:return null
 var format=Image.FORMAT_RF if construction=="rf32-961x705-v1" else Image.FORMAT_RGBA8
 if construction not in ["png-rgba8-v1","png-rgba8-tile3x3-v1","rf32-961x705-v1"]:return null
 var key=path+"|"+sha+"|"+str(size)+"|"+str(format)+"|"+construction+"|no-mipmap/linear/clamp/v1"
 if _weak.has(key):
  var current=_weak[key].get_ref()
  if current!=null and current is ImageTexture and current.get_size()==Vector2(size) and current.get_format()==format:hits+=1;return current
  _weak.erase(key)
 var image:Image
 if construction=="rf32-961x705-v1":
  if size!=Vector2i(961,705) or raw.size()!=961*705*4:return null
  for i in range(961*705):
   var value=raw.decode_float(i*4)
   if not is_finite(value) or value<0 or value>1:return null
  image=Image.create_from_data(961,705,false,Image.FORMAT_RF,raw)
 else:
  image=Image.new()
  if image.load_png_from_buffer(raw)!=OK:return null
  image.convert(Image.FORMAT_RGBA8)
  if construction=="png-rgba8-tile3x3-v1":
   if image.get_size()!=Vector2i(768,768) or size!=Vector2i(2304,2304):return null
   var tiled=Image.create(2304,2304,false,Image.FORMAT_RGBA8)
   for y in 3:
    for x in 3:tiled.blit_rect(image,Rect2i(0,0,768,768),Vector2i(x*768,y*768))
   image=tiled
 if image.get_size()!=size:return null
 var texture=ImageTexture.create_from_image(image)
 _weak[key]=weakref(texture);misses+=1;return texture
static func live_count()->int:
 var result=0
 for key in _weak.keys():
  if _weak[key].get_ref()==null:_weak.erase(key)
  else:result+=1
 return result
