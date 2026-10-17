extends "res://scripts/a00_trial_runtime/controller.gd"
## Optional review leaf: preserves exact LoadedWorld factory and every transaction gate.
const ArtProxy = preload("res://scripts/art/a00_village_preview_proxy_v10.gd")
const Registry = preload("res://scripts/art/hd_frame_registry_v10.gd")
const SOURCE_MAP := "res://data/maps/A00.json"
const SOURCE_SHA := "0f921a2714cab0a29383a8a25631b515b2de98fa38c02ed4701f0a19d3355868"
const UI_TEXTURE := "res://assets/earth/overall_v1/dialog_panel.png"
# Set from the actual generated file during assembly; verify before replacing UI.
const UI_SHA := "5ee66ecdcda39b3c9df27a4716a518c2ae9b9ede1cf6924f935e8bbb9866b4b2"

func prepare_map(candidate_authority: Dictionary, map_id: String, cell: Array, next_stop: bool, base_rng: Dictionary) -> Dictionary:
	var staged: Dictionary = super.prepare_map(candidate_authority,map_id,cell,next_stop,base_rng)
	_prepare_detached_art(staged)
	return staged

func prepare_trial_world(context: Dictionary) -> Dictionary:
	var staged: Dictionary = super.prepare_trial_world(context)
	_prepare_detached_art(staged)
	return staged

func _prepare_detached_art(staged: Dictionary) -> void:
	if not staged.get("ok",false) or not staged.has("world"): return
	var candidate = staged.world
	if str(candidate.map.get("id","")) != "A00": return
	var manifest_path := _manifest_for(candidate.map)
	if manifest_path.is_empty(): return
	var proxy = ArtProxy.new()
	# Original LoadedWorld is untouched unless complete art preparation succeeds.
	if not proxy.bind_detached(candidate,manifest_path):
		proxy.free()
		return
	candidate.add_child(proxy)
	proxy.activate_parent_suppression()

func prepare_inputs() -> Dictionary:
	var prepared: Dictionary = super.prepare_inputs()
	if prepared.get("ok",false): _apply_ui_art()
	return prepared

func build_candidate_ui() -> void:
	super.build_candidate_ui()
	_apply_ui_art()

func _apply_ui_art() -> void:
	if not FileAccess.file_exists(UI_TEXTURE) or FileAccess.get_sha256(UI_TEXTURE) != UI_SHA: return
	if not ResourceLoader.exists(UI_TEXTURE): return
	var texture = load(UI_TEXTURE)
	if not texture is Texture2D: return
	dialog_background.texture = texture
	dialog_background.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	dialog_background.stretch_mode = TextureRect.STRETCH_SCALE
	dialog_background.size = Vector2(523,216)
	dialog_background.mouse_filter = Control.MOUSE_FILTER_IGNORE
	dialog_background.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR

# Exact source state selection only; no arbitrary missing-owner tolerance.
func _manifest_for(current: Dictionary) -> String:
	if not FileAccess.file_exists(SOURCE_MAP) or FileAccess.get_sha256(SOURCE_MAP) != SOURCE_SHA: return ""
	var source = JSON.parse_string(FileAccess.get_file_as_string(SOURCE_MAP))
	if not source is Dictionary or not source.get("npcs") is Array: return ""
	if not Registry._same_art_npcs(source,current): return ""
	return Registry.FULL_MANIFEST if source.npcs == current.get("npcs") else Registry.DEFAULT_MANIFEST
