extends RefCounted
## Scalar distance to real authored shore intersections. No visible geometry is made.
## Built from transformed opaque triangles at mean sea level, then sampled in world XZ.
const SEA_LEVEL := -0.72
const MAX_DISTANCE := 2.8
const RESOLUTION := 384
const CACHE_VERSION := 2

static func surface_can_form_shore(object_name: String, material_name: String) -> bool:
	var key := object_name.to_lower()
	var pigment := material_name.to_lower()
	if key.begins_with("distant"):
		return false
	return key.begins_with("cliff") or key.begins_with("rockshore") or key.begins_with("rockstack") or pigment.begins_with("rock") or pigment.begins_with("stone") or pigment.begins_with("earth")

static func build(imported_world: Node3D, asset_hash: String = "") -> Dictionary:
	var cache_file := "user://shore_field_v%d_%s.res" % [CACHE_VERSION, asset_hash]
	if not asset_hash.is_empty() and FileAccess.file_exists(cache_file):
		var cached = load(cache_file) as ImageTexture
		if cached != null and cached.has_meta("world_rect"):
			return {"texture": cached, "world_rect": cached.get_meta("world_rect"), "segments": cached.get_meta("segments", 0), "source_segment_counts": cached.get_meta("source_segment_counts", {}), "cached": true}
	var segments: Array[Vector4] = []
	var source_segment_counts: Dictionary = {}
	for node: Node in imported_world.find_children("*", "MeshInstance3D", true, false):
		var mesh: Mesh = node.mesh
		if mesh == null:
			continue
		for surface in range(mesh.get_surface_count()):
			# Inspect the authored source material, not the runtime toon override.
			# Multimaterial slopes can have grass names but stone below water.
			var source := mesh.surface_get_material(surface)
			if not surface_can_form_shore(String(node.name), source.resource_name if source != null else ""):
				continue
			if mesh.surface_get_primitive_type(surface) != Mesh.PRIMITIVE_TRIANGLES:
				continue
			var arrays := mesh.surface_get_arrays(surface)
			var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
			var count := indices.size() if not indices.is_empty() else vertices.size()
			for index in range(0, count - 2, 3):
				var triangle: Array[Vector3] = []
				for corner in range(3):
					var vertex_index := indices[index + corner] if not indices.is_empty() else index + corner
					triangle.append(node.global_transform * vertices[vertex_index])
				var crossings: Array[Vector2] = []
				for edge in range(3):
					var a := triangle[edge]
					var b := triangle[(edge + 1) % 3]
					if (a.y < SEA_LEVEL) != (b.y < SEA_LEVEL):
						var hit := a.lerp(b, (SEA_LEVEL - a.y) / (b.y - a.y))
						crossings.append(Vector2(hit.x, hit.z))
				if crossings.size() == 2 and crossings[0].distance_squared_to(crossings[1]) > 0.00000001:
					segments.append(Vector4(crossings[0].x, crossings[0].y, crossings[1].x, crossings[1].y))
					source_segment_counts[String(node.name)] = int(source_segment_counts.get(String(node.name), 0)) + 1
	if segments.is_empty():
		return {}
	var bounds := Rect2(Vector2(segments[0].x, segments[0].y), Vector2.ZERO)
	for segment in segments:
		bounds = bounds.expand(Vector2(segment.x, segment.y)).expand(Vector2(segment.z, segment.w))
	bounds = bounds.grow(MAX_DISTANCE + 0.1)
	var pixel_size := bounds.size / float(RESOLUTION - 1)
	var distances := PackedFloat32Array()
	distances.resize(RESOLUTION * RESOLUTION)
	distances.fill(MAX_DISTANCE)
	# Rasterize only each segment's bounded influence rectangle, not every segment
	# for every pixel. Pixel values are metres, not albedo and not sRGB data.
	for segment in segments:
		var a := Vector2(segment.x, segment.y)
		var b := Vector2(segment.z, segment.w)
		var delta := b - a
		var length_squared := delta.length_squared()
		var start := ((a.min(b) - Vector2.ONE * MAX_DISTANCE - bounds.position) / pixel_size).floor()
		var finish := ((a.max(b) + Vector2.ONE * MAX_DISTANCE - bounds.position) / pixel_size).ceil()
		for y in range(maxi(0, int(start.y)), mini(RESOLUTION - 1, int(finish.y)) + 1):
			for x in range(maxi(0, int(start.x)), mini(RESOLUTION - 1, int(finish.x)) + 1):
				var point := bounds.position + Vector2(x, y) * pixel_size
				var t := clampf((point - a).dot(delta) / length_squared, 0.0, 1.0)
				var distance := point.distance_to(a + delta * t)
				var offset := y * RESOLUTION + x
				if distance < distances[offset]:
					distances[offset] = distance
	var image := Image.create_from_data(RESOLUTION, RESOLUTION, false, Image.FORMAT_RF, distances.to_byte_array())
	var texture := ImageTexture.create_from_image(image)
	texture.resource_name = "AuthoredShoreDistanceMetres"
	var world_rect := Vector4(bounds.position.x, bounds.position.y, bounds.size.x, bounds.size.y)
	texture.set_meta("world_rect", world_rect)
	texture.set_meta("segments", segments.size())
	texture.set_meta("source_segment_counts", source_segment_counts)
	if not asset_hash.is_empty():
		ResourceSaver.save(texture, cache_file)
	return {"texture": texture, "world_rect": world_rect, "segments": segments.size(), "source_segment_counts": source_segment_counts, "cached": false}
