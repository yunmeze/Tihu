extends RefCounted
## A13 eight-owner gate. Preparation hashes bytes; drawing checks live identity.
## Raw and actual ordered/cache streams are independently authoritative.
const Identity=preload("res://scripts/earth/instance_identity_guard.gd")
const REGISTRATION="res://assets/earth/environment/wall_2653_2660_anchor18_17_v1/registration.json"
const REGISTRATION_SHA="8ebe783b1cf57a1c9a54d332d4f74767ee7013e4a1061fbfc317a3f21c675241"
const MAP_PATH="res://data/maps/A13.json"
const MAP_SHA="d09549838963c8157307cc5406d3118baf69259d82459bcba0a3a8be5b34aa27"
const MANIFEST_PATH="res://assets/original/manifest.json"
const MANIFEST_SHA="506fba1f0fd826589046d38e4ebd5285ee9a11e3235cd78495cdd133c2e63837"
const ATLAS_PATH="res://assets/original/Map/Res/Wall/0.png"
const ATLAS_SHA="07bfa06728270c7f901eafc930c8c19a465af39e634d7ec0aa1160d9fcfad629"
const PACK="Map/Res/Wall"
const IDENTITIES=[[2653,18,17],[2654,17,18],[2655,18,18],[2656,16,19],[2657,17,19],[2658,15,20],[2659,16,20],[2660,15,21]]
const SOURCE_PINS={"res://scripts/world_view.gd": "b404d8dd5e7e85a120fec00b7eb5f01e6bfc1fc37adf5e7878c1798432d4e285", "res://scripts/earth/sample_world.gd": "c9139f34e1d57b1d33086c11157850454325c88078608fe13f8a081f7ddc07b2", "res://scripts/earth/first_map_world.gd": "e6a8ac3604c5ea938fbf006da1a79f195e38adf65695168ea0498db44bb37a5c", "res://scripts/earth/snapshot_world.gd": "f53f2d90843ff55e9078eda8d45498ea407aeffc520a8beec8d95f1ea35c89fe", "res://scripts/earth/snapshot_sorted_world.gd": "1d89ee9e02b984739eebf1f51641f9843ef7c7d43b9f4c7434a4022128333e78", "res://scripts/earth/snapshot_prefilter_world.gd": "02dea14cf29ecf358547abac62cb11503faaa12ad76a4a5bc4b85ee4cd1e609b", "res://scripts/earth/snapshot_zhang_world.gd": "533199fca3174a0e426eebe46cb740eb8eb1ad91e12d5644f7671f77e0aa2d92", "res://scripts/earth/south_walk_snapshot_world.gd": "66a6f6d73ee3ef25c1ad1896605d6d00a8e12754923c298c64b220f30c9add61", "res://scripts/earth/south_walk_contact_world.gd": "d17f4a4768452905c21b1c6a5949ff8b8344bf27752558024697cd0847cf37fa", "res://scripts/earth/upright_51_70_world.gd": "26bfa8866f26930de5f11638689c079beabf1be0b3f25bb1897085f0b7d6de43", "res://scripts/earth/instance_identity_guard.gd": "2eabae66a29b8696d7aef50ddfe5bbd27b46ad4278624c10b4a1183a2435cb0b", "res://scripts/earth/asset_guard.gd": "c5a0718736b91ceac6aea417a464840e61b33c03b19d8dc3f61272339a7cdf4e"}
var _generation=0
var prepared=false
var error="not prepared"
var _owners:Dictionary={}
var _source_pages:Array=[]
var _source_frames:Dictionary={}
var _raw_textures:Dictionary={}

func reset()->void:
 _generation+=1
 prepared=false;_owners={};_source_pages=[];_source_frames={};_raw_textures={}
 error="not prepared"

func _texture_changed(generation:int)->void:
 if generation==_generation:
  prepared=false;error="owner texture resource changed; explicit reprepare required"

func reject(reason:String)->bool:
 error=reason
 return false

static func freeze(value:Variant)->void:
 if value is Dictionary:
  for v in value.values():freeze(v)
  value.make_read_only()
 elif value is Array:
  for v in value:freeze(v)
  value.make_read_only()

static func verified_json(path:String,digest:String)->Dictionary:
 if not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=digest:return {}
 var value=JSON.parse_string(FileAccess.get_file_as_string(path))
 return value if value is Dictionary else {}

func prepare(path:String,runtime_map:Variant,runtime_packs:Variant)->bool:
 reset()
 if path!=REGISTRATION:return reject("registration path outside bounded candidate")
 for source in SOURCE_PINS:
  if FileAccess.get_sha256(source)!=SOURCE_PINS[source]:return reject("parent method source drift: "+source)
 var original=verified_json(MAP_PATH,MAP_SHA)
 var manifest=verified_json(MANIFEST_PATH,MANIFEST_SHA)
 var registration=verified_json(path,REGISTRATION_SHA)
 if original.is_empty() or manifest.is_empty() or registration.is_empty():return reject("pinned source or registration bytes differ")
 if FileAccess.get_sha256(ATLAS_PATH)!=ATLAS_SHA:return reject("source wall atlas differs")
 if not registration.get("owners") is Array or registration.owners.size()!=8:return reject("owner registration count")
 var source_pack:Dictionary=manifest.packs[PACK]
 _source_pages=source_pack.pages.duplicate(true)
 var staged:Dictionary={};var raw_staged:Dictionary={}
 for i in IDENTITIES.size():
  var id:Array=IDENTITIES[i];var order:int=id[1]*100+id[2]
  var r:Dictionary=registration.owners[i]
  var frame:Dictionary=source_pack.frames[str(id[0])]
  var anchor=Vector2(id[1]*48,id[2]*32)
  var top=32.0-float(frame.original[1])
  var position=anchor+Vector2(frame.crop[0],frame.crop[1]+top)
  var size=Vector2(frame.rect[2],frame.rect[3])
  if r.frame_index!=id[0] or r.stable_source_order!=order or r.cell!=[id[1],id[2]] or r.source_cell!=original.cells[order]:return reject("registration identity")
  if r.pack!=PACK or r.runtime_kind!=3 or r.layer!=1 or r.sort_y!=id[2] or r.scale!=0.5 or r.empty:return reject("registration route")
  if Vector2(r.world_top_left[0],r.world_top_left[1])!=position or Vector2(r.world_anchor[0],r.world_anchor[1])!=anchor:return reject("registration crop/top/origin")
  if Vector2(r.texture_size[0],r.texture_size[1])!=size*2:return reject("registration density")
  if r.texture!="res://assets/earth/environment/wall_2653_2660_anchor18_17_v1/owner-%d.png"%int(id[0]):return reject("owner texture path")
  if FileAccess.get_sha256(r.texture)!=r.texture_sha256:return reject("owner PNG bytes differ")
  # Direct PNG decode deliberately bypasses ResourceLoader/import fix_alpha_border.
  var decoded=Image.new()
  if decoded.load_png_from_buffer(FileAccess.get_file_as_bytes(r.texture))!=OK:return reject("owner PNG decode")
  decoded.convert(Image.FORMAT_RGBA8)
  if decoded.has_mipmaps():decoded.clear_mipmaps()
  if decoded.get_size()!=Vector2i(r.texture_size[0],r.texture_size[1]):return reject("decoded owner dimensions")
  var digest=HashingContext.new();digest.start(HashingContext.HASH_SHA256);digest.update(decoded.get_data())
  if digest.finish().hex_encode()!=r.texture_RGBA_sha256:return reject("decoded owner RGBA differs")
  var raw=ImageTexture.create_from_image(decoded)
  if raw==null:return reject("owner ImageTexture allocation")
  var texture=CanvasTexture.new();texture.diffuse_texture=raw
  texture.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST
  texture.texture_repeat=CanvasItem.TEXTURE_REPEAT_DISABLED
  raw.changed.connect(_texture_changed.bind(_generation))
  texture.changed.connect(_texture_changed.bind(_generation))
  staged[order]={"index":int(id[0]),"cell":Vector2i(id[1],id[2]),"source_cell":original.cells[order].duplicate(),"origin":anchor,"top":top,"position":position,"size":size,"texture":texture,"raw":raw}
  raw_staged[order]=raw
  _source_frames[str(id[0])]=frame.duplicate(true)
 freeze(staged);freeze(_source_frames);freeze(_source_pages)
 _owners=staged;_raw_textures=raw_staged
 prepared=true
 if not live_source_valid(runtime_map,runtime_packs):reset();return reject("runtime source identity differs")
 error="prepared; draw stream validation still required"
 return true

func live_source_valid(runtime_map:Variant,runtime_packs:Variant)->bool:
 if not prepared or _owners.size()!=8:return reject("eight-owner group not prepared")
 if not Identity.map_identity(runtime_map) or not runtime_map.get("cells") is Array or runtime_map.cells.size()!=10000:return reject("live A13 map identity")
 if not runtime_packs is Dictionary or not runtime_packs.get(PACK) is Dictionary:return reject("live wall pack")
 var pack:Dictionary=runtime_packs[PACK]
 if not pack.get("frames") is Dictionary or pack.get("pages")!=_source_pages:return reject("live wall page identity")
 for order in _owners:
  var owner:Dictionary=_owners[order]
  if not Identity.source_cell(runtime_map.cells[order],owner.source_cell):return reject("live source cell changed")
  var frame=pack.frames.get(str(owner.index))
  # Type-preserving structural serialization prevents true==1 from passing.
  if not frame is Dictionary or var_to_bytes(frame)!=var_to_bytes(_source_frames[str(owner.index)]):return reject("live frame geometry/metadata changed")
  var texture=owner.texture
  var raw=owner.raw
  if not texture is CanvasTexture or not raw is ImageTexture or raw!=_raw_textures[order] or texture.diffuse_texture!=raw:return reject("live owner texture binding changed")
  if texture.texture_filter!=CanvasItem.TEXTURE_FILTER_NEAREST or texture.texture_repeat!=CanvasItem.TEXTURE_REPEAT_DISABLED:return reject("owner sampling changed")
  if raw.get_size()!=owner.size*2 or raw.get_format()!=Image.FORMAT_RGBA8:return reject("owner density/format changed")
 return true

func entry_valid(entry:Variant,order:int)->bool:
 if not _owners.has(order):return false
 var owner:Dictionary=_owners[order]
 return Identity.entry(entry,3,PACK,owner.index,1,owner.cell.y,order,owner.origin)

func route_order(entry:Variant)->int:
 if not entry is Dictionary or entry.get("pack")!=PACK:return -1
 for order in _owners:
  var owner:Dictionary=_owners[order]
  # Parent typed-int conversion and kind5 animation can change the base index.
  # Any Wall entry at an owned origin must be the precise intended owner.
  var origin=entry.get("origin")
  if (origin is Vector2 or origin is Vector2i) and Vector2(origin)==owner.origin:return order
 return -1

func stream_valid(stream:Variant,ordered:bool)->bool:
 if not stream is Array:return reject("draw stream is not an array")
 var found:Dictionary={};var sequence:Array=[]
 for entry in stream:
  if not entry is Dictionary:return reject("draw stream entry is not a dictionary")
  # A same-route alias is relevant even with a different order/layer/y/kind.
  # Checking only claimed order misses raw aliases hidden behind a stale cache.
  var route=route_order(entry)
  var claimed=entry.get("order")
  var claimed_owner=-1
  if claimed is int or claimed is float:
   for order in _owners:
    if Identity.number(claimed,order):claimed_owner=order;break
  if route<0 and claimed_owner<0:continue
  if route<0 or claimed_owner!=route or not entry_valid(entry,route):return reject("owner identity or same-route alias changed")
  if found.has(route):return reject("duplicate owner route")
  found[route]=true;sequence.append(int(entry.index))
 if found.size()!=8:return reject("missing owner in draw stream")
 if ordered and sequence!=[2653,2654,2655,2656,2657,2658,2659,2660]:return reject("owner draw order changed")
 return true

func validate(runtime_map:Variant,runtime_packs:Variant,raw_objects:Variant,actual_ordered:Variant)->bool:
 if not live_source_valid(runtime_map,runtime_packs):return false
 if not stream_valid(raw_objects,false):return false
 if not stream_valid(actual_ordered,true):return false
 error="eight-owner draw group admitted"
 return true

func draw_item(pack_name:String,index:int,draw_origin:Vector2,use_offset:bool,top:float,screen_offset:Vector2=Vector2.ZERO)->Dictionary:
 if not prepared or pack_name!=PACK or use_offset or not is_finite(top):return {}
 for owner in _owners.values():
  if owner.index==index and owner.origin+screen_offset==draw_origin and owner.top==top:return owner
 return {}

func owner_count()->int:return _owners.size()
