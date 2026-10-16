extends RefCounted
## Geometry-only snapshot adapter. Original review preparation remains strict.
const Base=preload("res://scripts/earth/south_vegetation_candidate.gd")
const SnapshotIdentity=preload("res://scripts/earth/snapshot_source_identity.gd")
const Identity=preload("res://scripts/earth/instance_identity_guard.gd")
const NpcIdentity=preload("res://scripts/core/npc_source_identity.gd")
const Bridge=preload("res://scripts/core/map_load_bridge.gd")
const BASE_SHA="4dd2ae3074977b62d837b8d1ca5137fc1f7a7bad5d92f21f12786d67ad8dc314"
const CHICKEN_PATH="res://data/monsters/a13-chicken.json"
const CHICKEN_SHA="4046ae10127843058cf369b4d4d19532d8c483f8ac331f3953d4338d6913d363"
var original:Dictionary={}
var flag_identity=preload("res://scripts/earth/a13_visual_flag_identity.gd").new()
var failure=""
func load_source()->bool:
 if FileAccess.get_sha256("res://scripts/earth/south_vegetation_candidate.gd")!=BASE_SHA:return false
 if FileAccess.get_sha256(Base.SOURCE)!=Base.SOURCE_SHA or FileAccess.get_sha256(CHICKEN_PATH)!=CHICKEN_SHA:return false
 original=JSON.parse_string(FileAccess.get_file_as_string(Base.SOURCE))
 return not original.is_empty() and flag_identity.prepare(original)
func reject(reason:String)->bool:
 failure=reason;return false
func compatible(source:Dictionary)->bool:
 failure=""
 if original.is_empty():return reject("source not prepared")
 if not SnapshotIdentity.compatible(source,original) or not flag_identity.matches_source(source,original):return reject("snapshot geometry identity")
 # No flags/cell values or unknown metadata are loosened by this adapter.
 for key in source:
  if key!="added_units" and not original.has(key):return reject("unknown extra map key")
 for key in original:
  if key in ["npcs","cells"]:continue
  if not source.has(key) or not Base._exact_equal(source[key],original[key]):return reject("changed source field "+key)
 if not source.get("npcs") is Array:return reject("NPC bank type")
 var mapping=[];var next=0
 for npc in source.npcs:
  if not NpcIdentity.record_valid(npc):return reject("NPC record shape")
  while next<original.npcs.size() and original.npcs[next]!=npc:next+=1
  if next>=original.npcs.size():return reject("NPC not source deletion subsequence")
  mapping.append(next);next+=1
 var stamp={"map_id":original.id,"source_fingerprint":JSON.stringify(original).sha256_text(),"records_fingerprint":JSON.stringify(original.npcs).sha256_text()}
 var sidecar={"map_id":original.id,"source_fingerprint":stamp.source_fingerprint,"source_records":original.npcs,"runtime_to_source":mapping}
 if not NpcIdentity.validate(sidecar,source,stamp):return reject("NPC source identity")
 var units=source.get("added_units",[])
 if not units is Array or units.size()>Bridge.MAX_ADDED_UNITS:return reject("added unit bank")
 var expected={"x":49,"y":53,"name":"彩蛋鸡","definition_id":508,"texture_manifest":"res://assets/original/monsters/a13-chicken/manifest.json","runtime_behavior":"entity_record_only"}
 for unit in units:
  if not Base._exact_equal(unit,expected):return reject("unknown added unit")
 return true
func owners_valid(group:Dictionary,source:Dictionary,objects:Array)->bool:
 var seen={}
 for entry in objects:
  if not entry is Dictionary:return reject("object type")
  var order=entry.get("order")
  if not order is int or not group.has(order):continue
  if seen.has(order):return reject("duplicate live owner")
  var item=group[order]
  if not Identity.source_cell(source.cells[order],item.source_cell):return reject("changed owner cell")
  if not Identity.entry(entry,2,"Map/Res/Plant",item.index,1,order%100,order,Vector2(int(order/100),order%100)*Vector2(48,32)):return reject("changed live owner")
  seen[order]=true
 return seen.size()==group.size() or reject("missing live owner")
func prepare(id:Variant,path:Variant,source:Dictionary,objects:Array)->Dictionary:
 if not id is String or not Base.PATHS.has(id) or path!=Base.PATHS[id]:return {}
 if not load_source() or not compatible(source):return {}
 var scope=Base._scope(id)
 var registration=Base._verified_json(path,Base.SHAS[id])
 if scope.is_empty() or registration.is_empty():return {}
 # Stage against the actual snapshot cells, never substitute original JSON for it.
 var group=Base._stage(id,registration,scope,source)
 if group.size()!=Base.COUNTS[id] or not owners_valid(group,source,objects):return {}
 return group
