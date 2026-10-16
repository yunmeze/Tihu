extends RefCounted
signal bank_revoked
const MANIFEST="res://assets/earth/hero/s_walk_arap_v1/manifest.json"
const MANIFEST_SHA="04d1d075c5cdb38819b2e7b1180f2aa8ff3848ba983aa60d2c02951fcf3ab2c0"
const Movement=preload("res://scripts/core/movement.gd")
var _frames:Array=[]
var _identities:Dictionary={}
var generation:int=0
var bank_state:Dictionary={"generation":0,"active":false}
var source_actor:Dictionary={}
var failure="unprepared"
func reset()->void:
 bank_state.active=false;bank_revoked.emit();generation+=1;bank_state={"generation":generation,"active":false}
 _frames=[];_identities={};source_actor={};failure="unprepared"
func reject(reason:String)->bool:
 reset();failure=reason;return false
func prepare(path:Variant=MANIFEST)->bool:
 reset()
 if not path is String or path!=MANIFEST:return reject("registration identity")
 if not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=MANIFEST_SHA:return reject("registration SHA")
 var doc=JSON.parse_string(FileAccess.get_file_as_string(path))
 if not doc is Dictionary:return reject("registration structure")
 for source in doc.source_pins:
  if not FileAccess.file_exists(source) or FileAccess.get_sha256(source)!=doc.source_pins[source]:return reject("source identity "+source)
 var staged:Array=[];var bindings:Dictionary={}
 for record in doc.records:
  var p:String=record.path
  if not FileAccess.file_exists(p) or FileAccess.get_sha256(p)!=record.sha256:return reject("body SHA "+str(record.source_id))
  var image=Image.load_from_file(p)
  if image==null or image.is_empty() or image.get_size()!=Vector2i(512,512):return reject("body dimensions "+str(record.source_id))
  image.convert(Image.FORMAT_RGBA8)
  var hash=HashingContext.new();hash.start(HashingContext.HASH_SHA256);hash.update(image.get_data())
  if hash.finish().hex_encode()!=record.rgba_sha256:return reject("decoded RGBA "+str(record.source_id))
  var raw=ImageTexture.create_from_image(image)
  var canvas=CanvasTexture.new();canvas.diffuse_texture=raw;canvas.texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR
  staged.append(canvas)
  bindings[int(record.source_id)]={"texture":raw,"path":p,"sha256":record.sha256,"source_id":int(record.source_id),"generation":generation,"bank_state":bank_state,"rid":raw.get_rid()}
 if staged.size()!=6:return reject("incomplete group")
 var actor_data=JSON.parse_string(FileAccess.get_file_as_string("res://data/hero/movement.json"))
 if not actor_data is Dictionary:return reject("source actor")
 # Exact manifest SHA fixes schema, IDs, order, timing, direction and offset.
 source_actor=actor_data;_frames=staged;_identities=bindings;bank_state.active=true;failure="";return true
func bank_complete()->bool:
 if not bank_state.active or bank_state.generation!=generation or _frames.size()!=6 or _identities.size()!=6:return false
 for i in 6:
  if not _frames[i] is CanvasTexture or not _identities.has(57+i):return false
  var raw=_identities[57+i].get("texture")
  if not raw is Texture2D or _frames[i].diffuse_texture!=raw or raw.get_size()!=Vector2(512,512) or raw.get_rid()!=_identities[57+i].rid or _identities[57+i].generation!=generation:return false
 return true
func selected(actor:RefCounted,hero:Dictionary,index:int)->bool:
 return bank_complete() and actor!=null and actor.get_script()==Movement and hero==source_actor and actor.action=="walk" and actor.direction==4 and index>=57 and index<=62 and index==actor.source_frame()
func body_identity(index:int)->Dictionary:
 return _identities.get(index,{}).duplicate()

func canvas(index:int)->CanvasTexture:
 return _frames[index-57] if index>=57 and index<=62 and bank_complete() else null
