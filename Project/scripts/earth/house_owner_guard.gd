extends RefCounted
const Identity=preload("res://scripts/earth/instance_identity_guard.gd")
const REGISTRATION_SHA="cdbbaded84adf25c9d2f694f9b76e1353a98d1ad96ec6fd3a3d3cec7c814c6f9"
var local_scope_enabled=true
var building_header:Dictionary={}
var atlas_validator:Callable
var original_packs:Dictionary={}
var owner_orders:Dictionary={}
var validations=0
var profile_us:Dictionary={}
var profile_calls:Dictionary={}
var body_used_rect=Rect2()
func profile_add(key:String,start:int)->void:
 profile_us[key]=int(profile_us.get(key,0))+Time.get_ticks_usec()-start
 profile_calls[key]=int(profile_calls.get(key,0))+1
var reg:Dictionary={}
var texture:Texture2D
var image:Image
var blocked:PackedStringArray=[]
var error="not prepared"
var mask_pixels:Image
var owner_mask:Texture2D
var counts:Dictionary={}
const MASK_SHA="8d18e597c554c880396a33d76b5112c38cf0bb738dbea5471e37830a00ef1163"
const COUNTS_SHA="8cffca6bf7832b8fcd6b484d4e1af3fb70018cece7dee1e6d7491d8ee2519c50"
func reject(why:String)->bool:error=why;return false
func reload(deny:PackedStringArray=[])->bool:
 texture=null;owner_mask=null;counts={};reg={};owner_orders={};blocked=deny
 if not FileAccess.file_exists("res://assets/earth/house_280_289_v1/registration.json") or FileAccess.get_sha256("res://assets/earth/house_280_289_v1/registration.json")!=REGISTRATION_SHA:return reject("registration")
 reg=JSON.parse_string(FileAccess.get_file_as_string("res://assets/earth/house_280_289_v1/registration.json"))
 for pair in [["res://assets/earth/house_280_289_v1/body.png",reg.body_sha],["res://data/maps/A13.json",reg.source_map_sha],["res://assets/original/manifest.json",reg.source_manifest_sha]]:
  if pair[0] in blocked or not FileAccess.file_exists(pair[0]) or FileAccess.get_sha256(pair[0])!=pair[1]:return reject("dependency "+pair[0])
 for path in reg.atlas_pins:
  if path in blocked or not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=reg.atlas_pins[path]:return reject("atlas bytes")
 for dep in [["res://assets/earth/house_280_289_v1/ownership-id-data.png",MASK_SHA],["res://assets/earth/house_280_289_v1/owner_bounds.json",COUNTS_SHA]]:
  if dep[0] in blocked or not FileAccess.file_exists(dep[0]) or FileAccess.get_sha256(dep[0])!=dep[1]:return reject("owner mask dependency "+dep[0])
 counts=JSON.parse_string(FileAccess.get_file_as_string("res://assets/earth/house_280_289_v1/owner_bounds.json"))
 var mask_image=Image.load_from_file("res://assets/earth/house_280_289_v1/ownership-id-data.png")
 if mask_image==null or mask_image.get_size()!=Vector2i(1024,1024):return reject("owner mask image")
 mask_image.convert(Image.FORMAT_R8);mask_pixels=mask_image;owner_mask=ImageTexture.create_from_image(mask_image)
 image=Image.load_from_file("res://assets/earth/house_280_289_v1/body.png")
 if image==null or image.get_size()!=Vector2i(1024,1024):return reject("body size")
 var color_texture=CanvasTexture.new();color_texture.diffuse_texture=ImageTexture.create_from_image(image);color_texture.texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR
 texture=color_texture
 body_used_rect=Rect2(image.get_used_rect())
 original_packs=JSON.parse_string(FileAccess.get_file_as_string("res://assets/original/manifest.json")).get("packs",{})
 building_header=original_packs["Map/Res/Building"].duplicate(true)
 building_header.erase("frames");building_header.erase("pages");building_header.make_read_only()
 for i in reg.owners.size():owner_orders[int(reg.owners[i].stable_source_order)]={"owner_id":i+1}
 error="loaded";return true
func valid(map:Dictionary,packs:Dictionary,objects:Array)->bool:
 var started=Time.get_ticks_usec()
 var result=valid_impl(map,packs,objects)
 profile_add("valid_total",started)
 return result
func valid_impl(map:Dictionary,packs:Dictionary,objects:Array)->bool:
 validations+=1
 var stage=Time.get_ticks_usec()
 if texture==null or reg.is_empty():return reject("not loaded")
 for p in ["res://assets/earth/house_280_289_v1/ownership-id-data.png","res://assets/earth/house_280_289_v1/owner_bounds.json","res://assets/earth/house_280_289_v1/registration.json","res://assets/earth/house_280_289_v1/body.png","res://data/maps/A13.json","res://assets/original/manifest.json"]:
  if p in blocked or not FileAccess.file_exists(p):return reject("missing "+p)
 profile_add("dependency_presence",stage)
 stage=Time.get_ticks_usec()
 if not Identity.map_identity(map) or not map.get("cells") is Array or map.cells.size()!=10000:return reject("map identity")
 if not local_scope_enabled:
  if atlas_validator.is_valid():
   if not atlas_validator.call(packs,original_packs):return reject("snapshot atlas closure")
  elif packs!=original_packs:return reject("source atlas closure")
 profile_add("map_atlas_qualification",stage)
 stage=Time.get_ticks_usec()
 var pack=packs.get("Map/Res/Building",{})
 if not pack is Dictionary:return reject("Building pack type")
 if local_scope_enabled:
  if pack.size()!=building_header.size()+2:return reject("Building header shape")
  for key in building_header:
   if not pack.has(key) or pack[key]!=building_header[key]:return reject("Building header "+key)
 if not pack.get("frames") is Dictionary:return reject("Building frame bank")
 if pack.get("pages")!=reg.pages:return reject("atlas pages")
 for id in reg.frames:
  if pack.get("frames",{}).get(id)!=reg.frames[id]:return reject("atlas frame "+id)
 for page in reg.pages:
  if not FileAccess.file_exists(page.file):return reject("atlas missing")
 profile_add("building_frames_pages",stage)
 stage=Time.get_ticks_usec()
 var by_order={}
 for e in objects:
  if not e is Dictionary:return reject("object type")
  var order=e.get("order")
  if not by_order.has(order):by_order[order]=[]
  by_order[order].append(e)
 profile_add("by_order_build",stage)
 stage=Time.get_ticks_usec()
 for o in reg.owners:
  var order=int(o.stable_source_order)
  if not Identity.source_cell(map.cells[order],o.source_cell):return reject("source cell")
  if not by_order.has(order) or by_order[order].size()!=1:return reject("owner missing/duplicate")
  if not Identity.entry(by_order[order][0],4,o.pack,int(o.index),int(o.layer),int(o.sort_y),order,Vector2(o.cell[0]*48,o.cell[1]*32)):return reject("owner identity")
 profile_add("ten_owner_checks",stage)
 error="ready";return true

func owner_id(entry:Dictionary)->int:
 var order=entry.get("order")
 if not owner_orders.has(order):return 0
 var id=int(owner_orders[order].owner_id)
 var o=reg.owners[id-1]
 return id if Identity.entry(entry,4,o.pack,int(o.index),int(o.layer),int(o.sort_y),int(o.stable_source_order),Vector2(o.cell[0]*48,o.cell[1]*32)) else 0
func owner_at(world_point:Vector2)->int:
 var p=(world_point-Vector2(866,443))*2.0
 if p.x<0 or p.y<0 or p.x>=1024 or p.y>=1024:return 0
 return int(round(mask_pixels.get_pixel(int(floor(p.x)),int(floor(p.y))).r*255.0))
