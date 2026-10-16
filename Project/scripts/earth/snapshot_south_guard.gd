extends RefCounted
## Geometry-only snapshot adapter. Original review preparation remains strict.
const Bank=preload("res://scripts/earth/plant_texture_weak_bank.gd")
const AssetGuard=preload("res://scripts/earth/asset_guard.gd")
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
var _permits:Dictionary={}
var _permit_generation:int=0
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
func _source_owners_valid(group:Dictionary,source:Dictionary,objects:Array)->bool:
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
 if id is String:revoke_group(id)
 if not id is String or not Base.PATHS.has(id) or path!=Base.PATHS[id]:return {}
 if not load_source() or not compatible(source):return {}
 var scope=Base._scope(id)
 var registration=Base._verified_json(path,Base.SHAS[id])
 if scope.is_empty() or registration.is_empty():return {}
 # Stage against the actual snapshot cells, never substitute original JSON for it.
 var staged=_stage_shared(id,registration,scope,source)
 if staged.is_empty():return {}
 var group=staged.group
 if group.size()!=Base.COUNTS[id] or not _source_owners_valid(group,source,objects):return {}
 var canonical_items=group.duplicate()
 canonical_items.make_read_only()
 var token={"active":true,"generation":_permit_generation}
 var permit={"generation":_permit_generation,"token":token,"items":canonical_items,"bindings":staged.bindings}
 permit.make_read_only();_permits[id]=permit
 return group

func revoke_group(id:String)->void:
 _permit_generation+=1
 if _permits.has(id):
  _permits[id].token.active=false
  _permits.erase(id)
func reset_all()->void:
 for id in _permits.keys():revoke_group(id)
func item_valid(item:Variant)->bool:
 if not item is Dictionary or not item.get("group_id") is String:return false
 var id:String=item.group_id
 if not _permits.has(id):return false
 var permit=_permits[id]
 if not permit.token.active or permit.token.generation!=permit.generation:return false
 var value=item.get("stable_source_order")
 if not AssetGuard.integer(value,0,9999):revoke_group(id);return false
 var order=int(value)
 if not permit.items.has(order) or not is_same(permit.items[order],item):revoke_group(id);return false
 var binding=permit.bindings.get(order,{})
 if not Bank.binding_valid(binding) or not is_same(item.texture,binding.texture) or item.empty!=binding.empty_alpha:
  revoke_group(id);return false
 return true
func permit_group_valid(group:Dictionary,expected_id:String="")->bool:
 if group.is_empty():return reject("empty lease group")
 var first=group.values()[0]
 if not first is Dictionary or not first.get("group_id") is String:return reject("group id type")
 var id:String=first.group_id
 if not expected_id.is_empty() and id!=expected_id:return reject("outer group id changed")
 if not _permits.has(id):return reject("group permit absent")
 var permit=_permits[id]
 if group.size()!=permit.items.size():return reject("changed lease owner set")
 for order in permit.items:
  if not group.has(order):return reject("changed lease owner keys")
 for order in group:
  var item=group[order]
  if not order is int or not item is Dictionary or item.get("group_id")!=id:return reject("mixed group id/type")
  if not AssetGuard.integer(item.get("stable_source_order"),0,9999) or order!=int(item.stable_source_order):return reject("outer order changed")
  if not permit.items.has(order) or not is_same(permit.items[order],item):return reject("foreign/replaced group item")
  if not item_valid(item):return reject("shared texture lease revoked/changed")
 return true
func owners_valid(group:Dictionary,source:Dictionary,objects:Array,expected_id:String="")->bool:
 return permit_group_valid(group,expected_id) and _source_owners_valid(group,source,objects)
func _freeze_item(value:Variant)->void:
 if value is Dictionary:
  for child in value.values():_freeze_item(child)
  value.make_read_only()
 elif value is Array:
  for child in value:_freeze_item(child)
  value.make_read_only()
func _binding_texture(path:String,digest:String,size:Array,empty:bool)->Dictionary:
 if not AssetGuard.asset_path(path) or not AssetGuard.sha256(digest) or not AssetGuard.vector(size,2,1,16384):return {}
 if not AssetGuard.integer(size[0],1,16384) or not AssetGuard.integer(size[1],1,16384):return {}
 var binding=Bank.acquire_binding(path,digest,Vector2i(int(size[0]),int(size[1])))
 if binding.is_empty() or not Bank.binding_valid(binding) or binding.empty_alpha!=empty:return {}
 return binding

func _stage_shared(id: String, registration: Dictionary, scope: Dictionary, original: Dictionary) -> Dictionary:
 if not Identity.text(registration.get("instance"), id) or not Identity.text(registration.get("source_map_sha256"), Base.SOURCE_SHA):
  return {}
 if not Identity.text(registration.get("shadow"), "DISABLED for this candidate; no gate, receiver, mask, compositor slot or cast inherited"):
  return {}
 if not registration.get("owners") is Array or registration.owners.size() != Base.COUNTS[id]:
  return {}
 var expected_keys: Array = []
 for expected in scope.expected_owners:
  expected_keys.append(expected.key)
 if not Base._exact_equal(registration.get("suppress_source_keys"), expected_keys):
  return {}
 var staged: Dictionary = {}
 var bindings: Dictionary = {}
 for i in Base.COUNTS[id]:
  var expected: Dictionary = scope.expected_owners[i]
  var record: Variant = registration.owners[i]
  if not record is Dictionary:
   return {}
  # Match every trusted field, including texture identity, full canvas,
  # translation, flag, empty304, scale and all source suppression identities.
  for field in expected:
   if not record.has(field) or not Base._exact_equal(record[field], expected[field]):
    return {}
  var order := int(expected.stable_source_order)
  var cell: Array = expected.cell
  if order != int(cell[0]) * 100 + int(cell[1]) or staged.has(order):
   return {}
  if not Identity.source_cell(original.cells[order], expected.source_cell):
   return {}
  if not Identity.number(expected.flag, int(expected.source_cell[1])) or not Identity.number(expected.source_cell[2], 2) or not Identity.number(expected.source_cell[3], int(expected.frame_index)):
   return {}
  if not Identity.number(expected.layer, 1) or not Identity.number(expected.sort_y, int(cell[1])):
   return {}
  var binding := _binding_texture(expected.texture, expected.texture_sha256, expected.texture_size, expected.empty)
  if binding.is_empty():
   return {}
  # Start with the trusted identity, not unverified incoming fields. Keep
  # texture_path because the renderer's texture key contains a Texture2D.
  var item: Dictionary = expected.duplicate(true)
  item["texture_path"] = expected.texture
  item["texture"] = binding.texture
  item["index"] = int(expected.frame_index)
  item["origin"] = Vector2(expected.world_top_left[0], expected.world_top_left[1])
  item["size"] = Vector2(expected.texture_size[0], expected.texture_size[1]) * float(expected.scale)
  item["group_id"] = id
  _freeze_item(item)
  staged[order] = item
  bindings[order] = binding
 # Nothing is published until every owner and dependency passes. Callers must
 # replace that group's previous dictionary with this result, even when empty.
 bindings.make_read_only()
 return {"group":staged,"bindings":bindings}

