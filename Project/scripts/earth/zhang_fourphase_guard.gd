extends RefCounted
const REGISTRATION="res://assets/earth/zhang_fourphase_v1/registration.json"
const REGISTRATION_SHA="fda24d1fc3c1b6bb7b3062f2815d97d3e4cde9fb4dea64ecbb3a1ee09524396c"
const Identity=preload("res://scripts/earth/instance_identity_guard.gd")
var reg:Dictionary={}
var textures:Dictionary={}
var images:Dictionary={}
var dependencies:PackedStringArray=[]
var blocked:PackedStringArray=[]
var error="not loaded"
var slot=-1
var atlas_validator:Callable
var original_packs:Dictionary={}
var body_pins:Dictionary={}
func reject(why:String) -> bool:
 error=why;slot=-1;return false
func reload(deny:PackedStringArray=[]) -> bool:
 reg={};textures.clear();images.clear();dependencies.clear();blocked=deny;body_pins.clear()
 if not FileAccess.file_exists(REGISTRATION) or FileAccess.get_sha256(REGISTRATION)!=REGISTRATION_SHA:return reject("registration")
 var parsed=JSON.parse_string(FileAccess.get_file_as_string(REGISTRATION))
 if not parsed is Dictionary:return reject("registration type")
 reg=parsed
 var pins={"res://data/maps/A13.json":reg.source_map_sha,"res://assets/original/manifest.json":reg.source_manifest_sha}
 pins.merge(reg.atlas_pins)
 for id in reg.bodies:
  pins[reg.bodies[id].file]=reg.bodies[id].sha256
  body_pins[reg.bodies[id].file]=reg.bodies[id].sha256
 for path in pins:
  dependencies.append(path)
  if path in blocked or not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=pins[path]:return reject("dependency "+path)
 dependencies.append(REGISTRATION)
 var source=JSON.parse_string(FileAccess.get_file_as_string("res://data/maps/A13.json"))
 if not source is Dictionary or not source.get("npcs") is Array or source.npcs.size()<=4 or not Identity.npc_record(source.npcs[4],reg.npc_identity):return reject("original record4")
 original_packs=JSON.parse_string(FileAccess.get_file_as_string("res://assets/original/manifest.json")).get("packs",{})
 var pending_images:Dictionary={}
 var pending_textures:Dictionary={}
 for id in reg.bodies:
  var image=Image.load_from_file(reg.bodies[id].file)
  if image==null or image.get_size()!=Vector2i(384,384):return reject("body size "+id)
  pending_images[int(id)]=image;pending_textures[int(id)]=ImageTexture.create_from_image(image)
 images=pending_images;textures=pending_textures
 error="loaded";return true
func valid(map:Dictionary,packs:Dictionary,objects:Array) -> bool:
 slot=-1
 if textures.size()!=4 or reg.is_empty():return reject("not prepared")
 for id in [201,202,203,204]:
  if not textures.get(id) is Texture2D or not images.get(id) is Image:return reject("incomplete body bank")
 for path in dependencies:
  if path in blocked or not FileAccess.file_exists(path):return reject("missing "+path)
 if FileAccess.get_sha256(REGISTRATION)!=REGISTRATION_SHA:return reject("live registration SHA")
 for path in body_pins:
  if FileAccess.get_sha256(path)!=body_pins[path]:return reject("live body SHA "+path)
 if atlas_validator.is_valid():
  if not atlas_validator.call(packs,original_packs):return reject("snapshot atlas closure")
 elif packs!=original_packs:return reject("source atlas closure")
 if not Identity.map_identity(map) or not map.get("npcs") is Array:return reject("map")
 if not map.get("cells") is Array or map.cells.size()<=3534 or not Identity.source_cell(map.cells[3534],reg.source_cell):return reject("source cell")
 var matches=[]
 for i in map.npcs.size():
  if Identity.npc_record(map.npcs[i],reg.npc_identity):matches.append(i)
 if matches.size()!=1:return reject("source NPC absent/changed/duplicate")
 var current_slot:int=matches[0]
 if not packs.get("Npc") is Dictionary:return reject("Npc atlas")
 var pack:Dictionary=packs.Npc
 if not pack.get("frames") is Dictionary or not pack.get("pages") is Array:return reject("atlas metadata")
 for id in reg.frames:
  if pack.frames.get(id)!=reg.frames[id]:return reject("source frame "+id)
 for page in reg.pages:
  var i=int(page)
  if i>=pack.pages.size() or pack.pages[i]!=reg.pages[page]:return reject("source page")
 var count=0
 var expected_order=int(map.width)*int(map.height)+current_slot
 for e in objects:
  if not e is Dictionary:return reject("object type")
  if e.get("kind")==7 and e.get("origin")==Vector2(1680,1088):
   count+=1
   if not Identity.entry(e,7,"Npc",201,1,34,expected_order,Vector2(1680,1088)):return reject("NPC draw identity")
 if count!=1:return reject("NPC draw missing/duplicate")
 slot=current_slot;error="ready";return true
func hit(world_point:Vector2,id:int=201) -> bool:
 if slot<0 or not images.has(id):return false
 var p=(world_point-Vector2(1668,1032))*4
 if p.x<0 or p.y<0 or p.x>=384 or p.y>=384:return false
 return images[id].get_pixel(int(p.x),int(p.y)).a>=0.1

func owns(entry:Dictionary) -> bool:
 return slot>=0 and Identity.entry(entry,7,"Npc",201,1,34,10000+slot,Vector2(1680,1088))
func descriptor(id:int) -> Dictionary:
 if slot<0 or not textures.has(id):return {}
 return {"texture":textures[id],"origin":Vector2(1668,1032),"size":Vector2(96,96),"region":Rect2(0,0,384,384),"npc_index":slot}
