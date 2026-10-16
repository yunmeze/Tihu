extends "res://scripts/earth/snapshot_receiver_qualification.gd"
## Separate sidecar/source closure. Existing receiver contract and pins unchanged.
const WALK_CONTRACT="res://assets/earth/shadows/s_walk_contact_v3/receiver_contract.json"
const WALK_CONTRACT_SHA="058a74cb3801322e1d64a1244024a058dd53404b56314c742741e9db2f21a0ac"
const WALK_REGISTRATION="res://assets/earth/shadows/s_walk_contact_v3/runtime_registration.json"
const WALK_REGISTRATION_SHA="166f2e68752bcb4aa4ecda5f93356277abc51058bec596b280465b06e5c1020f"
func prepare() -> bool:
 static_cache.clear();static_verdicts={};resource_ok={};contracts={};source={}
 if not runtime_declaration_valid():return false
 var value=JSON.parse_string(FileAccess.get_file_as_string(WALK_CONTRACT))
 var source_value=JSON.parse_string(FileAccess.get_file_as_string("res://data/maps/A13.json"))
 if not value is Dictionary or not source_value is Dictionary:return false
 contracts=value;source=source_value;revalidate_resources()
 return resource_ok.get("hero_s_walk_contact_v3",false)
func revalidate_resources() -> void:
 resource_ok={}
 if not runtime_declaration_valid():return
 for name in contracts:
  resource_ok[name]=true
  for path in contracts[name].pins:
   if not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=contracts[name].pins[path]:resource_ok[name]=false;break
func runtime_declaration_valid() -> bool:
 if not FileAccess.file_exists(WALK_REGISTRATION) or FileAccess.get_sha256(WALK_REGISTRATION)!=WALK_REGISTRATION_SHA:return false
 if not FileAccess.file_exists(WALK_CONTRACT) or FileAccess.get_sha256(WALK_CONTRACT)!=WALK_CONTRACT_SHA:return false
 var declaration=JSON.parse_string(FileAccess.get_file_as_string(WALK_REGISTRATION))
 var receiver=JSON.parse_string(FileAccess.get_file_as_string(WALK_CONTRACT))
 if not declaration is Dictionary or declaration.get("schema")!="earth-s-walk-contact-v3-runtime-files" or not declaration.get("runtime_files") is Array:return false
 if not receiver is Dictionary or receiver.keys()!=["hero_s_walk_contact_v3"]:return false
 var declared={}
 for item in declaration.runtime_files:
  if not item is Dictionary or not item.get("path") is String or declared.has(item.path):return false
  if not FileAccess.file_exists(item.path) or FileAccess.get_sha256(item.path)!=item.get("sha256") or FileAccess.get_file_as_bytes(item.path).size()!=item.get("bytes"):return false
  declared[item.path]=item
 if not declared.has(WALK_CONTRACT) or declared[WALK_CONTRACT].get("sha256")!=WALK_CONTRACT_SHA:return false
 var caster=receiver.hero_s_walk_contact_v3
 if not caster is Dictionary or not caster.get("pins") is Dictionary:return false
 for path in caster.pins:
  if not declared.has(path) or declared[path].get("sha256")!=caster.pins[path]:return false
 return true
