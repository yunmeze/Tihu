extends RefCounted
const PATH="res://assets/earth/shadows/upright_51_70_v1/runtime_registration.json"
const SHA="53551e62e36b70d7e83bf90f0f88cfd70533f466144b157b769d0bd3b03314de"
var contract:Dictionary={}
var error="not prepared"
func prepare()->bool:
 contract={};error="tree registration closure"
 if not FileAccess.file_exists(PATH) or FileAccess.get_sha256(PATH)!=SHA:return false
 var data=JSON.parse_string(FileAccess.get_file_as_string(PATH))
 if not data is Dictionary or data.get("caster")!="upright_tree_51_70":return false
 for path in data.pins:
  if not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=data.pins[path]:error="tree pin "+path;return false
 contract=data;error="";return true
