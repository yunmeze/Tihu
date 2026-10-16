extends RefCounted
## Independent S walk identity and full six-phase support; never an idle/SE gate.
const Guard=preload("res://scripts/earth/asset_guard.gd")
const PATH="res://assets/earth/shadows/s_walk_contact_v3/manifest.json"
const SHA="a1f0bb3e6a5f7bbe24018ce646761c8ccb1492f3b0fb9c5769da51f75198b8dd"
var ready=false
var receiver_ready=false
var configuration:Dictionary={}
var textures:Dictionary={}
var records:Dictionary={}
var bank_state:Dictionary={}
var bound_generation=-1
var rids:Dictionary={}
var spans:Array[Vector3i]=[]
var forbidden_prefix=PackedInt32Array()
func reset() -> void:
 ready=false;receiver_ready=false;configuration={};textures={};records={};bank_state={};bound_generation=-1;rids={};spans.clear();forbidden_prefix.clear()
func prepare(load_receiver:bool=true) -> bool:
 reset()
 if not FileAccess.file_exists(PATH) or FileAccess.get_sha256(PATH)!=SHA:return false
 var parsed=JSON.parse_string(FileAccess.get_file_as_string(PATH))
 if not parsed is Dictionary:return false
 for path in parsed.input_sha256:
  if not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=parsed.input_sha256[path]:return false
 configuration=parsed
 for record in parsed.frames:records[int(record.source_id)]=record
 if load_receiver:
  var allowed=Image.load_from_file(parsed.receiver.allowed)
  var forbidden=Image.load_from_file(parsed.receiver.forbidden)
  var envelope=Image.load_from_file(parsed.envelope.path)
  if allowed==null or forbidden==null or envelope==null:reset();return false
  if allowed.get_size()!=Vector2i(1536,1024) or forbidden.get_size()!=Vector2i(1536,1024) or envelope.get_size()!=Vector2i(340,93):reset();return false
  allowed.convert(Image.FORMAT_L8);forbidden.convert(Image.FORMAT_L8);envelope.convert(Image.FORMAT_L8)
  var a=allowed.get_data();var f=forbidden.get_data();var e=envelope.get_data()
  forbidden_prefix.resize(1537*1024)
  for y in 1024:
   var total=0;var row=y*1537;forbidden_prefix[row]=0
   for x in 1536:
    var v=a[y*1536+x]
    if (v!=0 and v!=255) or int(v)+int(f[y*1536+x])!=255:reset();return false
    if v==0:total+=1
    forbidden_prefix[row+x+1]=total
  var count=0
  for y in 93:
   var start=-1
   for x in 341:
    var v=e[y*340+x] if x<340 else 0
    if v!=0 and v!=255:reset();return false
    if v>0:count+=1
    if v>0 and start<0:start=x
    elif v==0 and start>=0:spans.append(Vector3i(start,x,y));start=-1
  if count!=12049:reset();return false
  receiver_ready=true
 ready=true;return true
static func image_sha(texture:Texture2D) -> String:
 var im=texture.get_image()
 if im==null or (im.is_compressed() and im.decompress()!=OK):return ""
 if im.get_size()!=Vector2i(512,512):return ""
 im.convert(Image.FORMAT_RGBA8)
 var context=HashingContext.new()
 if context.start(HashingContext.HASH_SHA256)!=OK:return ""
 context.update(im.get_data());return context.finish().hex_encode()
func bind_frames(values:Variant) -> bool:
 textures={};bank_state={};bound_generation=-1;rids={}
 if not ready or not values is Dictionary or values.size()!=6:return false
 var staged={};var staged_rids={};var lease:Dictionary={};var generation=-1
 for id in range(57,63):
  if not values.has(id) or not values[id] is Dictionary:return false
  var v=values[id];var r=records[id];var body=v.get("texture")
  if v.has("source_id") and (not v.source_id is int or v.source_id!=id):return false
  if v.get("path")!=r.path or v.get("sha256")!=r.sha256:return false
  if not v.get("generation") is int or v.generation<0 or not v.get("bank_state") is Dictionary:return false
  var state:Dictionary=v.bank_state
  if state.get("active")!=true or not state.get("generation") is int or state.generation!=v.generation:return false
  if id==57:lease=state;generation=v.generation
  elif not is_same(lease,state) or generation!=v.generation:return false
  if not body is Texture2D or body is AtlasTexture or body.get_size()!=Vector2(512,512):return false
  if not v.get("rid") is RID or v.rid!=body.get_rid() or not v.rid.is_valid():return false
  if image_sha(body)!=r.rgba_sha256:return false
  staged[id]=body;staged_rids[id]=v.rid
 textures=staged;rids=staged_rids;bank_state=lease;bound_generation=generation;return true
func matches_body(body:Variant,source_id:Variant) -> bool:
 if not ready or not source_id is int or source_id<57 or source_id>62:return false
 if not is_instance_valid(body) or not body is Texture2D or body is AtlasTexture or body!=textures.get(source_id):return false
 # Controlled-loader lifetime: pixels checked at load/bind, never GPU-read back per draw.
 # The loader revokes this shared lease on reset before allocating a new generation.
 # This is not protection from arbitrary external ImageTexture.update calls.
 if bank_state.get("active")!=true or not bank_state.get("generation") is int or bank_state.generation!=bound_generation:return false
 return body.get_size()==Vector2(512,512) and body.get_rid()==rids.get(source_id) and body.get_rid().is_valid()
func allows(cell:Variant) -> bool:
 if not ready or not receiver_ready or not cell is Vector2 or not cell.is_finite() or absf(cell.x)>4096 or absf(cell.y)>4096:return false
 var base=(cell*Vector2(48,32)+Vector2(-16,-64)+Vector2(5.5,83.5)-Vector2(2496,960))*2
 for span in spans:
  var x0=floori(base.x+span.x);var x1=ceili(base.x+span.y)
  var y0=floori(base.y+span.z);var y1=ceili(base.y+span.z+1)
  if x0<0 or x1>1536 or y0<0 or y1>1024:return false
  for y in range(y0,y1):
   var row=y*1537
   if forbidden_prefix[row+x1]!=forbidden_prefix[row+x0]:return false
 return true
