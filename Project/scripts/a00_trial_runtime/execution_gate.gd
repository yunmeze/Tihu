extends RefCounted
## Additive execution DAG. Does not replace/re-pin any published renderer gate.
static func verify(path: String, expected_sha: String) -> Dictionary:
 if not FileAccess.file_exists(path) or FileAccess.get_sha256(path) != expected_sha:
  return {"ok":false,"error":"A00 execution manifest identity"}
 var manifest: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
 if not manifest is Dictionary or manifest.get("schema") != "a00-runtime-execution-leaves-v1" or not manifest.get("files") is Array:
  return {"ok":false,"error":"A00 execution manifest shape"}
 var seen: Dictionary = {}
 for record in manifest.files:
  if not record is Dictionary or not record.get("path") is String or not record.get("sha256") is String:
   return {"ok":false,"error":"A00 execution record shape"}
  var leaf: String = record.path
  if not leaf.begins_with("res://") or ".." in leaf or seen.has(leaf):
   return {"ok":false,"error":"A00 execution duplicate/unsafe path"}
  seen[leaf] = true
  if not FileAccess.file_exists(leaf) or FileAccess.get_sha256(leaf) != record.sha256:
   return {"ok":false,"error":"A00 execution pin: "+leaf}
 return {"ok":true}
