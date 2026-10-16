extends RefCounted
## Controlled immutable load proof. External ImageTexture.update is outside contract.
const PATH="res://assets/earth/environment/upright_tree_v1/raw.png"
const PNG_SHA="ada0e0fd8952fe1dcc6b60dafb9d64be96476ed7736a881f1e5e401436b3db0f"
const RGBA_SHA="1d03e3c7605db988407421f40d09de825febaffa2487a2e09484ebdd106de967"
static var _holder:WeakRef
static func digest(bytes:PackedByteArray)->String:
 var ctx=HashingContext.new();ctx.start(HashingContext.HASH_SHA256);ctx.update(bytes);return ctx.finish().hex_encode()
static func acquire()->Texture2D:
 if not FileAccess.file_exists(PATH):return null
 var bytes=FileAccess.get_file_as_bytes(PATH)
 if digest(bytes)!=PNG_SHA:return null
 if _holder!=null:
  var found=_holder.get_ref()
  if found is ImageTexture and found.get_size()==Vector2(1162,1353):return found
 var image=Image.new()
 if image.load_png_from_buffer(bytes)!=OK:return null
 image.convert(Image.FORMAT_RGBA8)
 if image.get_size()!=Vector2i(1162,1353) or digest(image.get_data())!=RGBA_SHA:return null
 var texture=ImageTexture.create_from_image(image)
 _holder=weakref(texture)
 return texture
static func live_count()->int:
 return 1 if _holder!=null and _holder.get_ref()!=null else 0
