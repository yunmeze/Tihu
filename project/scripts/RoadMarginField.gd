extends RefCounted
## World-XZ distance to the union boundary of the authored road's upper faces.
## This helper creates scalar data only. It never changes visible meshes, UVs,
## transforms, materials, colliders, or CoastalPlanting's independent lane clearance.
## Sample R as linear metres, with repeat_disable and filter_linear. world_rect is
## (minimum X, minimum Z, size X, size Z); texel-center-aware UVs are returned too.
const MAX_DISTANCE := 1.5
const RESOLUTION := 768
const CACHE_VERSION := 1 # Bump whenever extraction/rasterization semantics change.
const WELD_EPSILON := 0.00001
const TOP_NORMAL_Y := 0.5
const UNION_PROBE := WELD_EPSILON * 4.0
const PARAM_EPSILON := 0.0000001

static func is_road_source(object_name: String) -> bool:
	var key := object_name.to_lower()
	return key == "roadribbon" or key == "roadcape" or key.begins_with("roadribbon.") or key.begins_with("roadcape.")

static func build(imported_world: Node3D, asset_hash: String = "") -> Dictionary:
	var cache_file := cache_path(imported_world, asset_hash)
	if not cache_file.is_empty() and FileAccess.file_exists(cache_file):
		var cached := ResourceLoader.load(cache_file, "ImageTexture", ResourceLoader.CACHE_MODE_IGNORE) as ImageTexture
		if cached != null and int(cached.get_meta("cache_version", -1)) == CACHE_VERSION and cached.has_meta("world_rect") and cached.has_meta("counts") and cached.get_width() == RESOLUTION and cached.get_height() == RESOLUTION:
			return _result(cached, true)
	var boundary := extract_boundary(imported_world)
	var segments: Array[Vector4] = boundary.segments
	if segments.is_empty():
		return {}
	var bounds := Rect2(Vector2(segments[0].x, segments[0].y), Vector2.ZERO)
	for segment in segments:
		bounds = bounds.expand(Vector2(segment.x, segment.y)).expand(Vector2(segment.z, segment.w))
	# Leave two or more fully saturated texels at every side, including bilinear
	# footprints. Clamped texture sampling beyond the rect must also return max.
	bounds = bounds.grow(MAX_DISTANCE + 0.15)
	var pixel_size := bounds.size / float(RESOLUTION - 1)
	var distances := PackedFloat32Array()
	distances.resize(RESOLUTION * RESOLUTION)
	distances.fill(MAX_DISTANCE)
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
	texture.resource_name = "AuthoredRoadMarginDistanceMetres"
	texture.set_meta("world_rect", Vector4(bounds.position.x, bounds.position.y, bounds.size.x, bounds.size.y))
	texture.set_meta("counts", boundary.counts)
	texture.set_meta("source_segment_counts", boundary.source_segment_counts)
	texture.set_meta("cache_version", CACHE_VERSION)
	texture.set_meta("asset_hash", asset_hash)
	if not cache_file.is_empty():
		var error := ResourceSaver.save(texture, cache_file)
		if error != OK:
			push_warning("Road margin cache save failed: %s" % error_string(error))
	return _result(texture, false)

static func _result(texture: ImageTexture, cached: bool) -> Dictionary:
	var counts: Dictionary = texture.get_meta("counts")
	return {"texture": texture, "world_rect": texture.get_meta("world_rect"), "segments": counts.segments, "source_segment_counts": texture.get_meta("source_segment_counts"), "counts": counts, "max_distance": MAX_DISTANCE, "uv_scale": Vector2.ONE * float(RESOLUTION - 1) / float(RESOLUTION), "uv_offset": Vector2.ONE * 0.5 / float(RESOLUTION), "cached": cached}

static func cache_path(imported_world: Node3D, asset_hash: String) -> String:
	if asset_hash.is_empty():
		return ""
	# GLB hash invalidates authored edits. Global transforms also participate:
	# a moved/rotated imported root must not reuse an old world-space raster.
	var signature: Array = [asset_hash, CACHE_VERSION, RESOLUTION, MAX_DISTANCE, WELD_EPSILON, TOP_NORMAL_Y, UNION_PROBE]
	for node in _road_nodes(imported_world):
		signature.append([String(imported_world.get_path_to(node)), node.global_transform])
	return "user://road_margin_v%d_%s.res" % [CACHE_VERSION, var_to_bytes(signature).hex_encode().sha256_text()]

static func _road_nodes(imported_world: Node3D) -> Array[MeshInstance3D]:
	var nodes: Array[MeshInstance3D] = []
	if imported_world is MeshInstance3D and is_road_source(String(imported_world.name)):
		nodes.append(imported_world as MeshInstance3D)
	for node: Node in imported_world.find_children("*", "MeshInstance3D", true, false):
		if is_road_source(String(node.name)):
			nodes.append(node as MeshInstance3D)
	nodes.sort_custom(func(a: MeshInstance3D, b: MeshInstance3D) -> bool: return String(a.get_path()) < String(b.get_path()))
	return nodes

static func extract_boundary(imported_world: Node3D) -> Dictionary:
	var positions: Array[Vector3] = []
	var buckets: Dictionary = {}
	var edges: Dictionary = {}
	var face_keys: Dictionary = {}
	var triangles: Array[Dictionary] = []
	var counts := {"source_meshes": 0, "source_triangles": 0, "top_triangles": 0, "rejected_triangles": 0, "duplicate_triangles": 0, "welded_vertices": 0, "internal_edges": 0, "candidate_edges": 0, "union_rejected_spans": 0, "segments": 0}
	for node in _road_nodes(imported_world):
		var mesh := node.mesh
		if mesh == null or absf(node.global_transform.basis.determinant()) < 0.000000001:
			continue
		counts.source_meshes += 1
		var normal_basis := node.global_transform.basis.inverse().transposed()
		for surface in range(mesh.get_surface_count()):
			if mesh.surface_get_primitive_type(surface) != Mesh.PRIMITIVE_TRIANGLES:
				continue
			var arrays := mesh.surface_get_arrays(surface)
			var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX] if arrays[Mesh.ARRAY_INDEX] != null else PackedInt32Array()
			var vertex_count := indices.size() if not indices.is_empty() else vertices.size()
			for index in range(0, vertex_count - 2, 3):
				counts.source_triangles += 1
				var local: Array[Vector3] = []
				for corner in range(3):
					var vertex_index := indices[index + corner] if not indices.is_empty() else index + corner
					local.append(vertices[vertex_index])
				# Godot's front-face winding is clockwise. Transform the geometric
				# local normal with inverse-transpose, including mirrored roots.
				var normal := normal_basis * (local[2] - local[0]).cross(local[1] - local[0])
				if normal.length_squared() < 0.000000000001 or normal.normalized().y < TOP_NORMAL_Y:
					counts.rejected_triangles += 1
					continue
				var ids: Array[int] = []
				for point in local:
					ids.append(_weld_vertex(node.global_transform * point, positions, buckets))
				if ids[0] == ids[1] or ids[1] == ids[2] or ids[2] == ids[0]:
					counts.rejected_triangles += 1
					continue
				var sorted_ids := ids.duplicate()
				sorted_ids.sort()
				var face_key := Vector3i(sorted_ids[0], sorted_ids[1], sorted_ids[2])
				if face_keys.has(face_key):
					counts.duplicate_triangles += 1
					continue
				face_keys[face_key] = true
				var points := PackedVector2Array()
				for id in ids:
					points.append(Vector2(positions[id].x, positions[id].z))
				var bounds := Rect2(points[0], Vector2.ZERO).expand(points[1]).expand(points[2])
				triangles.append({"points": points, "bounds": bounds})
				counts.top_triangles += 1
				for side in range(3):
					var a := ids[side]
					var b := ids[(side + 1) % 3]
					var edge_key := Vector2i(mini(a, b), maxi(a, b))
					if edges.has(edge_key):
						edges[edge_key].count += 1
					else:
						edges[edge_key] = {"count": 1, "source": String(node.name)}
	var segments: Array[Vector4] = []
	var source_segment_counts: Dictionary = {}
	for key: Vector2i in edges:
		if int(edges[key].count) != 1:
			counts.internal_edges += 1
			continue
		var first := positions[key.x]
		var second := positions[key.y]
		var a := Vector2(first.x, first.z)
		var b := Vector2(second.x, second.z)
		if a.distance_squared_to(b) <= WELD_EPSILON * WELD_EPSILON:
			continue
		counts.candidate_edges += 1
		# A different road mesh may cover part of this edge, even if its
		# triangulation/height differs. Split at all projected intersections,
		# then keep only intervals separating inside-union from outside-union.
		# This avoids transverse worn stripes at overlapping/adjoining joins.
		var spans := _union_boundary_spans(a, b, triangles)
		counts.union_rejected_spans += spans.rejected
		for segment: Vector4 in spans.segments:
			segments.append(segment)
			var source: String = edges[key].source
			source_segment_counts[source] = int(source_segment_counts.get(source, 0)) + 1
	counts.welded_vertices = positions.size()
	counts.segments = segments.size()
	return {"segments": segments, "source_segment_counts": source_segment_counts, "counts": counts}

static func _weld_vertex(point: Vector3, positions: Array[Vector3], buckets: Dictionary) -> int:
	var cell := Vector3i((point / WELD_EPSILON).floor())
	# Search adjacent cells too: rounding alone fails for seam duplicates on
	# opposite sides of a quantization boundary.
	for z in range(-1, 2):
		for y in range(-1, 2):
			for x in range(-1, 2):
				var nearby := cell + Vector3i(x, y, z)
				for id: int in buckets.get(nearby, []):
					if positions[id].distance_squared_to(point) <= WELD_EPSILON * WELD_EPSILON:
						return id
	var result := positions.size()
	positions.append(point)
	if not buckets.has(cell):
		buckets[cell] = []
	buckets[cell].append(result)
	return result

static func _union_boundary_spans(a: Vector2, b: Vector2, triangles: Array[Dictionary]) -> Dictionary:
	var delta := b - a
	var length_squared := delta.length_squared()
	var cuts: Array[float] = [0.0, 1.0]
	var edge_bounds := Rect2(a.min(b), a.max(b) - a.min(b)).grow(WELD_EPSILON)
	for triangle in triangles:
		if not edge_bounds.intersects(triangle.bounds, true):
			continue
		var points: PackedVector2Array = triangle.points
		for side in range(3):
			var c := points[side]
			var d := points[(side + 1) % 3]
			var other_delta := d - c
			var denominator := delta.cross(other_delta)
			if absf(denominator) > 0.00000001:
				var t := (c - a).cross(other_delta) / denominator
				var u := (c - a).cross(delta) / denominator
				if t > PARAM_EPSILON and t < 1.0 - PARAM_EPSILON and u >= -PARAM_EPSILON and u <= 1.0 + PARAM_EPSILON:
					cuts.append(t)
			elif absf((c - a).cross(delta)) <= WELD_EPSILON * sqrt(length_squared):
				# Collinear seams also need split points at the other endpoints.
				for point: Vector2 in [c, d]:
					var t := (point - a).dot(delta) / length_squared
					if t > PARAM_EPSILON and t < 1.0 - PARAM_EPSILON:
						cuts.append(t)
	cuts.sort()
	var segments: Array[Vector4] = []
	var rejected := 0
	var perpendicular := Vector2(-delta.y, delta.x).normalized() * UNION_PROBE
	var start := cuts[0]
	var open_start := -1.0
	var open_finish := -1.0
	for index in range(1, cuts.size()):
		var finish := cuts[index]
		if finish - start <= PARAM_EPSILON:
			continue
		var midpoint := a + delta * ((start + finish) * 0.5)
		var keep := _inside_union(midpoint + perpendicular, triangles) != _inside_union(midpoint - perpendicular, triangles)
		if keep:
			if open_start < 0.0:
				open_start = start
			open_finish = finish
		else:
			rejected += 1
			if open_start >= 0.0:
				segments.append(_span(a, delta, open_start, open_finish))
				open_start = -1.0
		start = finish
	if open_start >= 0.0:
		segments.append(_span(a, delta, open_start, open_finish))
	return {"segments": segments, "rejected": rejected}

static func _span(a: Vector2, delta: Vector2, start: float, finish: float) -> Vector4:
	var first := a + delta * start
	var second := a + delta * finish
	return Vector4(first.x, first.y, second.x, second.y)

static func _inside_union(point: Vector2, triangles: Array[Dictionary]) -> bool:
	for triangle in triangles:
		var bounds: Rect2 = triangle.bounds
		if not bounds.grow(WELD_EPSILON * 0.1).has_point(point):
			continue
		var vertices: PackedVector2Array = triangle.points
		var a := (vertices[1] - vertices[0]).cross(point - vertices[0])
		var b := (vertices[2] - vertices[1]).cross(point - vertices[1])
		var c := (vertices[0] - vertices[2]).cross(point - vertices[2])
		if (a >= 0.0 and b >= 0.0 and c >= 0.0) or (a <= 0.0 and b <= 0.0 and c <= 0.0):
			return true
	return false

static func distance_to_boundary(point: Vector2, segments: Array[Vector4]) -> float:
	var nearest := MAX_DISTANCE
	for segment in segments:
		var a := Vector2(segment.x, segment.y)
		var delta := Vector2(segment.z, segment.w) - a
		var t := clampf((point - a).dot(delta) / delta.length_squared(), 0.0, 1.0)
		nearest = minf(nearest, point.distance_to(a + delta * t))
	return nearest
