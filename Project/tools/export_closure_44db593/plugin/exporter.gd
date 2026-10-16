@tool
extends EditorExportPlugin
func _get_name():return "ExactRawAllowlistPrototype"
func _export_begin(_features,_debug,_path,_flags):
 var m=JSON.parse_string(FileAccess.get_file_as_string("res://addons/raw_allowlist/allowlist.json"))
 if not m is Dictionary or m.get("schema")!="earth-export-raw-allowlist-v1":
  push_error("Invalid allowlist");return
 var verified=[]
 for f in m.files:
  if not f.path.begins_with("res://") or ".." in f.path or not FileAccess.file_exists(f.path) or FileAccess.get_sha256(f.path)!=f.sha256:
   push_error("Allowlist verification failed: "+f.path);return
  var bytes=FileAccess.get_file_as_bytes(f.path)
  if bytes.size()!=f.bytes:push_error("Allowlist size mismatch");return
  verified.append([f.path,bytes])
 for record in verified:add_file(record[0],record[1],false)
 print("RAW_ALLOWLIST_EXPORT_ADDED ",verified.size())
