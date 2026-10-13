extends RefCounted
## Converts authored material colors into intentional, differentiated toon families.
## No mesh or texture geometry is generated here.

const TOON := preload("res://shaders/coastal_toon.gdshader")
const FOLIAGE_ATLAS := preload("res://shaders/foliage_atlas.gdshader")
const PAINTED := preload("res://shaders/coastal_painted_toon.gdshader")
const DISTANT := preload("res://shaders/distant_land.gdshader")
const ENVIRONMENT_FAMILIES := ["foliage", "rock", "road", "wood", "cloud", "architecture"]
const OUTLINE := preload("res://shaders/colored_outline.gdshader")
var materials: Dictionary = {}
var surface_count := 0
var vertex_ao_strength := 0.0
var rim_preview_strength := 0.0
var outline_wings := true
var color_preview := false
var look_profile := 0
var feather_flow_preview := false
var rock_plane_preview := false
var wind_materials: Array[ShaderMaterial] = []
var atlas_texture: Texture2D
var atlas_regions: Array[Rect2] = []
var atlas_roots: Array[Vector2] = []

func apply(root: Node3D) -> void:
	var pending: Array[Node] = [root]
	while not pending.is_empty():
		var node: Node = pending.pop_back()
		for child in node.get_children():
			pending.append(child)
		if not node is MeshInstance3D or node.mesh == null:
			continue
		if node.has_meta("foliage_atlas_tile") and atlas_texture != null:
			_apply_atlas_card(node)
			continue
		var object_name := String(node.name).to_lower()
		if "ocean" in object_name or "water" in object_name or "foam" in object_name:
			continue
		for surface in range(node.mesh.get_surface_count()):
			var source: Material = node.get_active_material(surface)
			var source_name := source.resource_name.to_lower() if source != null else ""
			var family := _family(object_name, source_name)
			var outline := _outlined_shape(object_name)
			var depth := clampf((-node.global_position.z - 20.0) / 75.0, 0.0, 0.58)
			var source_id := source.get_instance_id() if source != null else 0
			var wind := object_name.begins_with("leaf") or object_name.begins_with("fern") or object_name.begins_with("flower") or object_name.begins_with("grasstuft")
			var feather_uv := feather_flow_preview and object_name in ["pelicanhead", "pelicanbody"]
			var key := "%d_%s_%s_%.2f_%d_%s" % [source_id, family, outline, depth, node.get_instance_id() if wind else 0, feather_uv]
			if not materials.has(key):
				materials[key] = _make(source, family, outline, depth)
				if feather_uv:
					materials[key].set_shader_parameter("feather_albedo", load("res://assets/textures/pelican_feather_flow_0832.png"))
					materials[key].set_shader_parameter("feather_strength", 0.72)
				if wind and materials[key].shader == PAINTED:
					materials[key].set_shader_parameter("wind_strength", 0.045)
					materials[key].set_shader_parameter("wind_origin_y", node.global_position.y)
					wind_materials.append(materials[key])
			node.set_surface_override_material(surface, materials[key])
			surface_count += 1

func set_time(time: float) -> void:
	for material in wind_materials:
		material.set_shader_parameter("ride_clock", time)

func _outlined_shape(object_name: String) -> bool:
	# Detail feather tufts and the warm bill lip must not acquire sticker-like
	# individual hull strokes merely because they share a principal-name prefix.
	return object_name in ["pelicanhead", "pelicanbody", "pelicanbill", "pelicanpouch"] or (outline_wings and object_name in ["wingl", "wingr"])

func _family(object_name: String, source_name: String) -> String:
	var label := object_name + " " + source_name
	if "distant" in label:
		return "distant"
	if "eyelid" in object_name:
		return "feather"
	if "catchlight" in label:
		return "catchlight"
	if "iris" in label:
		return "iris"
	if "eye" in label or "pupil" in label:
		return "eye"
	if "bill" in label or "beak" in label or "foot" in label or "leg" in label:
		return "bill"
	if "pouch" in label:
		return "pouch"
	if "lighthouse" in label or "roof" in label or "tower" in label or "glass" in label:
		return "architecture"
	if "metal" in label or "handlebar" in label or "handlestem" in label or "crank" in label or "bell" in label:
		return "metal"
	if "tire" in label or "rubber" in label or "grip" in label:
		return "rubber"
	if "frame" in label or "mint" in label or "paint" in label or "fork" in label or "rim" in label or "spoke" in label or "hub" in label or "wheel" in label:
		return "paint"
	if object_name.begins_with("road") or "path" in label or "sand" in source_name or source_name.begins_with("road"):
		return "road"
	if "rock" in source_name or "stone" in source_name or "cliff" in source_name:
		return "rock"
	if "flower" in label or "fern" in label or "grass" in label or "leaf" in label or "foliage" in label or "crown" in label or "terrain" in label or "headland" in label or "island" in label:
		return "foliage"
	if "rock" in label or "stone" in label or "cliff" in label:
		return "rock"
	if "wood" in label or "trunk" in label or "seat" in label or "rail" in label or "post" in label:
		return "wood"
	if "cloud" in label:
		return "cloud"
	return "feather"

func _make(source: Material, family: String, outline: bool, depth: float) -> ShaderMaterial:
	var result := ShaderMaterial.new()
	result.shader = PAINTED if family in ENVIRONMENT_FAMILIES else TOON
	result.resource_name = "Toon_" + family + "_" + (source.resource_name if source != null else "Ivory")
	var base := Color("fff2d9")
	if source is BaseMaterial3D:
		base = source.albedo_color
	result.set_shader_parameter("base_color", base)
	if family == "distant":
		result.shader = DISTANT
		result.set_shader_parameter("base_color", base)
		result.set_shader_parameter("atmospheric_depth", depth)
		return result
	result.set_shader_parameter("vertex_ao_strength", minf(vertex_ao_strength, 0.12) if family in ["metal", "paint", "rubber", "wood"] else vertex_ao_strength)
	if family in ENVIRONMENT_FAMILIES:
		result.set_shader_parameter("atmospheric_depth", depth)
	var p: Dictionary = {"terminator": 0.14, "band_softness": 0.11, "highlight_strength": 0.008, "highlight_size": 0.12}
	if family == "feather" and base.get_luminance() > 0.75:
		p.merge({"shadow_emission": Color(0.08, 0.07, 0.30), "direct_tint": Vector3(0.99, 1.0, 0.60), "band_softness": 0.07, "rim_strength": rim_preview_strength}, true)
	match family:
		"bill":
			p.merge({"highlight_strength": 0.040, "highlight_size": 0.16, "material_roughness": 0.48}, true)
		"pouch":
			p.merge({"shadow_fill": 0.42, "fill_tint": Vector3(1.20, 0.50, 0.0), "direct_gain": 0.68, "direct_tint": Vector3(0.72, 1.0, 1.0), "highlight_strength": 0.012, "material_roughness": 0.85}, true)
		"iris":
			p.merge({"shadow_fill": 0.12, "highlight_strength": 0.28, "highlight_size": 0.045, "material_roughness": 0.30}, true)
		"catchlight":
			p.merge({"shadow_fill": 0.55, "direct_gain": 0.0, "highlight_strength": 0.0}, true)
		"eye":
			p.merge({"highlight_strength": 5.0, "highlight_size": 0.045, "material_roughness": 0.16}, true)
		"metal":
			p.merge({"highlight_strength": 0.9, "highlight_size": 0.06, "material_roughness": 0.28}, true)
		"paint":
			p.merge({"highlight_strength": 0.085, "highlight_size": 0.11, "material_roughness": 0.50}, true)
		"rubber":
			p.merge({"highlight_strength": 0.008, "material_roughness": 0.96}, true)
		"foliage":
			p.merge({"terminator": 0.19, "band_softness": 0.075, "highlight_strength": 0.0, "material_roughness": 1.0, "paint_strength": 0.12, "paint_scale": 1.15}, true)
		"rock":
			p.merge({"band_softness": 0.065, "highlight_strength": 0.0, "paint_strength": 0.11, "paint_scale": 1.4}, true)
		"road":
			p.merge({"highlight_strength": 0.0, "paint_strength": 0.05, "paint_scale": 0.80}, true)
		"wood":
			p.merge({"highlight_strength": 0.025, "paint_strength": 0.10, "paint_scale": 2.4}, true)
		"cloud":
			p.merge({"band_softness": 0.13, "highlight_strength": 0.0, "paint_strength": 0.0}, true)
		"architecture":
			p.merge({"highlight_strength": 0.015, "paint_strength": 0.045, "paint_scale": 1.4}, true)
	if color_preview:
		match family:
			"foliage":
				var name_hint := source.resource_name.to_lower() if source != null else ""
				if "leaf" in name_hint or "grass" in name_hint or "green" in name_hint:
					p.merge({"ambient_tint": Vector3(0.82, 1.02, 1.08), "direct_tint": Vector3(1.85, 1.24, 0.33)}, true)
			"rock":
				p.merge({"ambient_tint": Vector3(0.82, 0.92, 1.12), "direct_tint": Vector3(1.85, 1.23, 0.45)}, true)
			"road":
				p.merge({"ambient_tint": Vector3(0.96, 0.97, 0.99), "direct_tint": Vector3(0.98, 0.99, 0.92)}, true)
			"architecture":
				p.merge({"ambient_tint": Vector3(0.96, 0.97, 1.00), "direct_tint": Vector3(1.05, 1.02, 0.91)}, true)
	if look_profile > 0:
		# Isolated native look development. Total scene exposure remains one.
		p.merge({"band_softness": 0.065, "highlight_strength": 0.006}, true)
		match family:
			"feather":
				p.merge({"shadow_emission": Color(0.15, 0.11, 0.25), "direct_gain": 1.0, "direct_tint": Vector3(1.0, 1.0, 0.80), "rim_strength": 0.10}, true)
			"pouch":
				p.merge({"shadow_fill": 0.48, "fill_tint": Vector3(1.35, 0.55, 0.0), "direct_gain": 0.65, "direct_tint": Vector3(0.90, 1.0, 0.85), "highlight_strength": 0.035}, true)
			"bill":
				p.merge({"highlight_strength": 0.14, "highlight_size": 0.10, "direct_gain": 0.80}, true)
			"iris":
				p.merge({"shadow_fill": 0.15, "highlight_strength": 0.3}, true)
			"catchlight":
				p.merge({"shadow_fill": 0.55, "direct_gain": 0.0, "highlight_strength": 0.0}, true)
			"eye":
				p.merge({"highlight_strength": 3.0, "highlight_size": 0.035}, true)
			"metal":
				p.merge({"highlight_strength": 1.0, "highlight_size": 0.055}, true)
			"paint":
				p.merge({"highlight_strength": 0.28, "highlight_size": 0.085, "direct_gain": 0.90}, true)
			"rubber":
				p.merge({"highlight_strength": 0.005}, true)
			"foliage":
				p.merge({"ambient_tint": Vector3(0.92, 1.02, 1.10), "direct_tint": Vector3(1.45, 1.22, 0.55), "highlight_strength": 0.0}, true)
			"rock":
				p.merge({"ambient_tint": Vector3(0.90, 1.0, 1.10), "direct_tint": Vector3(1.08, 1.08, 0.90), "highlight_strength": 0.0}, true)
			"road":
				p.merge({"ambient_tint": Vector3(0.95, 1.0, 1.05), "direct_tint": Vector3(1.0, 1.04, 0.95), "highlight_strength": 0.0}, true)
			"architecture":
				p.merge({"ambient_tint": Vector3(0.96, 0.97, 1.06), "direct_tint": Vector3(1.0, 1.02, 0.87), "direct_gain": 0.85}, true)
		if look_profile == 2:
			p.merge({"graphic_bands": true, "band_softness": 0.022, "terminator": 0.12}, true)
	if rock_plane_preview and family == "rock":
		# Broader warm top planes and cool shade, isolated from hero exposure.
		p.merge({"graphic_bands": true, "band_softness": 0.065, "terminator": 0.16, "ambient_tint": Vector3(0.92, 0.98, 1.08), "direct_tint": Vector3(1.65, 1.22, 0.66), "direct_gain": 0.80}, true)
	for key: String in p:
		result.set_shader_parameter(key, p[key])
	var texture_path := ""
	var texture_mean := Color.WHITE
	var texture_strength := 0.0
	var texture_scale := 0.4
	if family == "rock":
		texture_path = "res://assets/textures/coastal_stone_painted.png"
		texture_mean = Color(201.298 / 255.0, 173.631 / 255.0, 148.146 / 255.0)
		texture_strength = 0.28
		texture_scale = 0.36
	elif family == "road":
		texture_path = "res://assets/textures/coastal_sand_painted.png"
		texture_mean = Color(229.264 / 255.0, 191.892 / 255.0, 144.099 / 255.0)
		texture_strength = 0.65
	elif family == "foliage" and source != null and "grass" in source.resource_name.to_lower():
		texture_path = "res://assets/textures/coastal_grass_painted.png"
		texture_mean = Color(139.030 / 255.0, 164.796 / 255.0, 98.143 / 255.0)
		texture_strength = 0.28
		texture_scale = 0.30
	if not texture_path.is_empty():
		result.set_shader_parameter("painted_albedo", load(texture_path))
		result.set_shader_parameter("painted_mean", texture_mean)
		result.set_shader_parameter("texture_strength", texture_strength)
		result.set_shader_parameter("texture_scale", texture_scale)
		result.set_shader_parameter("paint_strength", 0.0)
	if outline:
		var line := ShaderMaterial.new()
		line.shader = OUTLINE
		line.resource_name = "SelectiveColoredSilhouette"
		line.set_shader_parameter("outline_pixels", 0.8 if family == "feather" else 0.7)
		line.set_shader_parameter("outline_color", Color("797486") if family == "feather" else Color("a26c67"))
		result.next_pass = line
	return result

func _apply_atlas_card(node: MeshInstance3D) -> void:
	var tile := clampi(int(node.get_meta("foliage_atlas_tile", 0)), 0, 15)
	var tint: Color = node.get_meta("foliage_tint", Color.WHITE)
	var key := "atlas_%d_%s" % [tile, tint.to_html()]
	if not materials.has(key):
		var material := ShaderMaterial.new()
		material.shader = FOLIAGE_ATLAS
		material.resource_name = "PaintedFoliageTile_%d" % tile
		material.set_shader_parameter("foliage_atlas", atlas_texture)
		material.set_shader_parameter("foliage_tint", tint)
		var region := Rect2(float(tile % 4) / 4.0, floorf(float(tile) / 4.0) / 4.0, 0.25, 0.25)
		if tile < atlas_regions.size():
			region = atlas_regions[tile]
		material.set_shader_parameter("atlas_region", Vector4(region.position.x, region.position.y, region.size.x, region.size.y))
		material.set_shader_parameter("card_height", maxf(node.mesh.get_aabb().size.y, 0.01))
		material.set_shader_parameter("card_width", maxf(node.mesh.get_aabb().size.x, 0.01))
		if tile < atlas_roots.size():
			material.set_shader_parameter("root_in_crop_uv", atlas_roots[tile])
		materials[key] = material
		wind_materials.append(material)
	node.material_override = materials[key]
	surface_count += node.mesh.get_surface_count()
