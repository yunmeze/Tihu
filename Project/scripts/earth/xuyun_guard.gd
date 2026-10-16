extends RefCounted
const REGISTRATION="res://assets/earth/xuyun_static_v1/registration.json"
const BODY="res://assets/earth/xuyun_static_v1/body.png"
const REGISTRATION_SHA="bee860c2b673fcd17c3337ae8c35a574020d13fe38a2d727ca00fc7d2d5774cd"
const Identity=preload("res://scripts/earth/instance_identity_guard.gd")
var reg:Dictionary={}
var texture:Texture2D
var image:Image
var dependencies:PackedStringArray=[]
var blocked:PackedStringArray=[]
var error="not loaded"
var slot=-1
var atlas_validator:Callable
var original_packs:Dictionary={}
func reject(why:String) -> bool:
 error=why;slot=-1;return false
func reload(deny:PackedStringArray=[]) -> bool:
 reg={};texture=null;image=null;dependencies.clear();blocked=deny
 if not FileAccess.file_exists(REGISTRATION) or FileAccess.get_sha256(REGISTRATION)!=REGISTRATION_SHA:return reject("registration")
 var parsed=JSON.parse_string(FileAccess.get_file_as_string(REGISTRATION))
 if not parsed is Dictionary:return reject("registration type")
 reg=parsed
 var pins={"res://data/maps/A13.json":reg.source_map_sha,"res://assets/original/manifest.json":reg.source_manifest_sha,BODY:reg.body_sha}
 pins.merge(reg.atlas_pins)
 for path in pins:
  dependencies.append(path)
  if path in blocked or not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=pins[path]:return reject("dependency "+path)
 original_packs=JSON.parse_string(FileAccess.get_file_as_string("res://assets/original/manifest.json")).get("packs",{})
 dependencies.append(REGISTRATION)
 var loaded=ResourceLoader.load(BODY) if ResourceLoader.exists(BODY) else null
 if not loaded is Texture2D:return reject("body resource")
 image=loaded.get_image()
 if image==null or image.get_size()!=Vector2i(512,640):return reject("body size")
 texture=loaded
 error="loaded";return true
func valid(map:Dictionary,packs:Dictionary,objects:Array) -> bool:
 slot=-1
 if texture==null or reg.is_empty():return reject("not prepared")
 for path in dependencies:
  if path in blocked or not FileAccess.file_exists(path):return reject("missing "+path)
 if atlas_validator.is_valid():
  if not atlas_validator.call(packs,original_packs):return reject("snapshot atlas closure")
 elif packs!=original_packs:return reject("source atlas closure")
 if not Identity.map_identity(map) or not map.get("npcs") is Array:return reject("map")
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
  if e.get("kind")==7 and e.get("origin")==Vector2(1392,1344):
   count+=1
   if not Identity.entry(e,7,"Npc",237,1,42,expected_order,Vector2(1392,1344)):return reject("NPC draw identity")
 if count!=1:return reject("NPC draw missing/duplicate")
 slot=current_slot;error="ready";return true
func hit(world_point:Vector2) -> bool:
 if slot<0 or image==null:return false
 var p=(world_point-Vector2(1360,1240))*4
 if p.x<0 or p.y<0 or p.x>=512 or p.y>=640:return false
 return image.get_pixel(int(p.x),int(p.y)).a>=0.1

func descriptor() -> Dictionary:
 if slot<0 or texture==null:return {}
 return {"texture":texture,"origin":Vector2(1360,1240),"size":Vector2(128,160),"region":Rect2(0,0,512,640),"npc_index":slot,"order":10000+slot}
func owns(entry:Dictionary) -> bool:
 return slot>=0 and Identity.entry(entry,7,"Npc",237,1,42,10000+slot,Vector2(1392,1344))
