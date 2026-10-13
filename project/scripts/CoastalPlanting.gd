extends RefCounted
## Art-directed coastal planting, using only the mesh resources authored in Blender.
## This module never constructs, edits, or replaces visible mesh geometry.
## Call apply(imported_world, ride_root) BEFORE ToonPalette.apply(imported_world).
## Per-card materials/UV atlas selection are owned by ToonPalette.

const SEED := 7132026
const GRID_SIZE := 0.65
const MAX_MESH_INSTANCES := 740
const MAX_ADDED_TRIANGLES := 200000
const MAX_SOLID_TRIANGLES := 180000
const ROOT_NAME := "CoastalPlanting"
const ROAD_MARGIN := 0.10
const CARD_ROOT_FRACTION := 0.0 # Atlas crop maps the painted root to the card bottom.

var report: Dictionary = {}
# Runtime can promote approved layers for a normal no-argument launch.
var canopy_enabled := false
var ledge_enabled := false
var placements: Array[Dictionary] = []
var _rng := RandomNumberGenerator.new()
var _sources: Dictionary = {}
var _prototypes: Dictionary = {}
var _ground_faces := PackedVector3Array()
var _ground_grid: Dictionary = {}
var _road_faces := PackedVector3Array()
var _road_grid: Dictionary = {}
var _wall_faces := PackedVector3Array()
var _wall_source_names: Array[String] = []
var _root: Node3D
var _mesh_count := 0
var _triangle_count := 0
var _prototype_triangle_counts: Dictionary = {}
var _card_ready := false
var _atlas_tiles: Dictionary = {}
var _serial := 0
var _skip_this_placement := false
var _resized_source_nodes: Array[String] = []
var _hidden_source_nodes: Array[String] = []

func apply(imported_world: Node3D, _ride_root: Node3D) -> Dictionary:
	# Safe to call again during look development: do not double the planting.
	var previous := imported_world.get_node_or_null(ROOT_NAME)
	if previous != null:
		return previous.get_meta("planting_report", {})
	_rng.seed = SEED
	_sources.clear()
	_prototypes.clear()
	_ground_faces.clear()
	_ground_grid.clear()
	_road_faces.clear()
	_road_grid.clear()
	_wall_faces.clear()
	_wall_source_names.clear()
	placements.clear()
	_mesh_count = 0
	_triangle_count = 0
	_serial = 0
	_skip_this_placement = false
	_resized_source_nodes.clear()
	_hidden_source_nodes.clear()
	_collect_sources(imported_world)
	# The source artist can publish the card library independently while the main
	# landscape GLB is being exported. This is still authored mesh data.
	if not _sources.has("foliagecardtemplate") and ResourceLoader.exists("res://assets/foliage_card.glb"):
		var card_scene := load("res://assets/foliage_card.glb") as PackedScene
		if card_scene != null:
			var library := card_scene.instantiate() as Node3D
			library.name = "AuthoredFoliageLibrary"
			library.visible = false
			imported_world.add_child(library)
			_collect_sources(library)
	_prepare_prototypes()
	_collect_surfaces()
	if _use_ledges():
		_collect_wall_surfaces()
	_root = Node3D.new()
	_root.name = ROOT_NAME
	imported_world.add_child(_root)
	_card_ready = _prototypes.has("card")
	_load_atlas_metadata()
	# Broad connected masses have unequal centers, lobes, sizes, and negative space.
	# The seaward row is intentionally lower than the camera-side bank.
	var banks: Array[Dictionary] = [
		_bank("near_west", Vector2(-6.0, 1.48), Vector2(1.14, 0.68), 16, 0.92),
		_bank("near_west_lobe", Vector2(-5.10, 2.20), Vector2(0.90, 0.82), 14, 1.00),
		_bank("near_flowers", Vector2(-3.95, 1.82), Vector2(1.00, 0.54), 19, 0.90),
		_bank("near_middle", Vector2(-2.70, 2.52), Vector2(0.95, 0.66), 19, 0.80),
		_bank("near_low", Vector2(-0.65, 2.28), Vector2(1.18, 0.68), 32, 0.88),
		_bank("near_front", Vector2(1.25, 2.78), Vector2(1.24, 0.85), 28, 0.90),
		_bank("near_east", Vector2(4.30, 2.53), Vector2(1.25, 0.60), 13, 0.70),
		_bank("near_far_west", Vector2(-8.30, 0.93), Vector2(1.12, 0.56), 10, 0.60),
		_bank("sea_west", Vector2(-7.20, -1.91), Vector2(1.20, 0.42), 13, 0.65),
		_bank("sea_middle", Vector2(-4.80, -1.86), Vector2(1.00, 0.39), 13, 0.70),
		_bank("sea_hero_left", Vector2(-2.80, -1.54), Vector2(0.82, 0.38), 12, 0.54),
		_bank("sea_rock", Vector2(2.43, -1.80), Vector2(1.12, 0.46), 12, 0.64),
		_bank("cape_lighthouse", Vector2(-4.83, -9.15), Vector2(0.90, 0.48), 11, 0.66),
		_bank("cape_tree", Vector2(-5.05, -10.54), Vector2(0.88, 0.55), 9, 0.65),
		_bank("cape_front", Vector2(-1.75, -8.96), Vector2(1.04, 0.43), 13, 0.62),
		_bank("cape_tip", Vector2(0.20, -8.64), Vector2(0.88, 0.55), 10, 0.55),
		_bank("cape_curve", Vector2(2.18, -7.50), Vector2(0.78, 0.68), 9, 0.53),
		_bank("cape_middle", Vector2(3.70, -6.00), Vector2(0.71, 0.82), 9, 0.50),
		_bank("cape_near", Vector2(5.70, -4.72), Vector2(0.86, 0.58), 8, 0.45),
	]
	for bank in banks:
		_plant_bank(bank)
	_plant_road_edge()
	_plant_ledge_drapes()
	_recompose_original_accents()
	if _use_canopy():
		_compose_canopy_preview()
	if _use_ledges():
		_plant_cliff_attachments()
	var stone_attachments := 0
	for placement: Dictionary in placements:
		if placement.get("anchor_mode", "terrain") == "authored_stone":
			stone_attachments += 1
	report = {
		"stone_attachments": stone_attachments,
		"seed": SEED,
		"mesh_instances": _mesh_count,
		"added_triangles": _triangle_count,
		"placements": placements.size(),
		"atlas_cards": _card_ready,
		"terrain_triangles": _ground_faces.size() / 3,
		"road_triangles": _road_faces.size() / 3,
		"budget_mesh_instances": MAX_MESH_INSTANCES,
		"budget_triangles": MAX_ADDED_TRIANGLES,
		"resized_source_nodes": _resized_source_nodes.duplicate(),
		"hidden_source_nodes": _hidden_source_nodes.duplicate(),
	}
	_root.set_meta("planting_report", report)
	_root.set_meta("planting_seed", SEED)
	print("Coastal planting: ", report)
	return report

func _use_canopy() -> bool:
	var args := OS.get_cmdline_user_args()
	return not args.has("--no-canopy") and (canopy_enabled or args.has("--canopy-preview"))

func _use_ledges() -> bool:
	var args := OS.get_cmdline_user_args()
	return not args.has("--no-ledge") and (ledge_enabled or args.has("--ledge-preview"))

func _bank(label: String, center: Vector2, radius: Vector2, count: int, height: float) -> Dictionary:
	return {"label": label, "center": center, "radius": radius, "count": count, "height": height}

func _collect_sources(node: Node) -> void:
	if node is MeshInstance3D and node.mesh != null:
		_sources[_key(node.name)] = node
	for child in node.get_children():
		_collect_sources(child)

func _key(value: String) -> String:
	return value.to_lower().replace("_", "").replace("-", "").replace(" ", "").replace(".", "")

func _prepare_prototypes() -> void:
	_add_prototype("fan", ["LeafFanA.005"])
	_add_prototype("shrub", ["LeafShrubRound"])
	_add_prototype("fern", ["FernStemA", "FernLeafletA.001"])
	_add_prototype("flower", ["FlowerCream", "FlowerCenter", "FlowerStem"])
	_add_prototype("pebble", ["RockShoreA"])
	_add_prototype("card", ["FoliageCardTemplate"])
	if _prototypes.has("card"):
		# The authored library card is not itself a landscape object.
		var source: MeshInstance3D = _prototypes["card"][0]
		source.visible = false

func _add_prototype(label: String, names: Array) -> void:
	var pieces: Array[MeshInstance3D] = []
	var triangle_count := 0
	for source_name: String in names:
		var source := _sources.get(_key(source_name)) as MeshInstance3D
		if source == null:
			return
		pieces.append(source)
		triangle_count += source.mesh.get_faces().size() / 3
	_prototypes[label] = pieces
	_prototype_triangle_counts[label] = triangle_count

func _collect_surfaces() -> void:
	for source_key: String in _sources:
		var source: MeshInstance3D = _sources[source_key]
		var is_road := source_key.begins_with("road") or source_key in ["headlandpath", "capepath"]
		var is_rock := source_key.begins_with("rockshore")
		var is_ground := source_key in ["grassshelf", "grasscape", "cliffheadland"] or is_rock
		if not is_road and not is_ground:
			continue
		for surface in source.mesh.get_surface_count():
			if source_key == "cliffheadland":
				var material := source.get_active_material(surface)
				if material == null or not "grass" in material.resource_name.to_lower():
					continue
			var arrays: Array = source.mesh.surface_get_arrays(surface)
			var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
			var count := indices.size() if not indices.is_empty() else vertices.size()
			for index in range(0, count, 3):
				var a := source.global_transform * vertices[indices[index] if not indices.is_empty() else index]
				var b := source.global_transform * vertices[indices[index + 1] if not indices.is_empty() else index + 1]
				var c := source.global_transform * vertices[indices[index + 2] if not indices.is_empty() else index + 2]
				var normal := (b - a).cross(c - a).normalized()
				if absf(normal.y) < (0.60 if is_rock else (0.34 if is_ground else 0.05)):
					continue
				if is_road:
					_index_triangle(a, b, c, _road_faces, _road_grid)
				else:
					_index_triangle(a, b, c, _ground_faces, _ground_grid)

func _index_triangle(a: Vector3, b: Vector3, c: Vector3, faces: PackedVector3Array, grid: Dictionary) -> void:
	var first := faces.size()
	faces.append(a)
	faces.append(b)
	faces.append(c)
	var low := Vector2(minf(a.x, minf(b.x, c.x)), minf(a.z, minf(b.z, c.z)))
	var high := Vector2(maxf(a.x, maxf(b.x, c.x)), maxf(a.z, maxf(b.z, c.z)))
	var minimum := _cell(low)
	var maximum := _cell(high)
	for x in range(minimum.x, maximum.x + 1):
		for z in range(minimum.y, maximum.y + 1):
			var key := Vector2i(x, z)
			if not grid.has(key):
				grid[key] = []
			grid[key].append(first)

func _cell(point: Vector2) -> Vector2i:
	return Vector2i(floori(point.x / GRID_SIZE), floori(point.y / GRID_SIZE))

func _barycentric(point: Vector2, a: Vector3, b: Vector3, c: Vector3) -> Vector3:
	var u := Vector2(b.x - a.x, b.z - a.z)
	var v := Vector2(c.x - a.x, c.z - a.z)
	var q := point - Vector2(a.x, a.z)
	var determinant := u.cross(v)
	if absf(determinant) < 0.00000001:
		return Vector3(-1.0, -1.0, -1.0)
	var wb := q.cross(v) / determinant
	var wc := u.cross(q) / determinant
	return Vector3(1.0 - wb - wc, wb, wc)

func sample_ground(point: Vector2) -> Dictionary:
	var best_height := -INF
	var best_normal := Vector3.UP
	for first: int in _ground_grid.get(_cell(point), []):
		var a := _ground_faces[first]
		var b := _ground_faces[first + 1]
		var c := _ground_faces[first + 2]
		var bary := _barycentric(point, a, b, c)
		if minf(bary.x, minf(bary.y, bary.z)) < -0.00001:
			continue
		var height := a.y * bary.x + b.y * bary.y + c.y * bary.z
		if height > best_height:
			best_height = height
			best_normal = (b - a).cross(c - a).normalized()
			if best_normal.y < 0.0:
				best_normal = -best_normal
	if best_height == -INF or best_height < -0.40:
		return {}
	return {"position": Vector3(point.x, best_height, point.y), "normal": best_normal}

func is_road(point: Vector2, margin := ROAD_MARGIN) -> bool:
	var minimum := _cell(point - Vector2.ONE * margin)
	var maximum := _cell(point + Vector2.ONE * margin)
	for x in range(minimum.x, maximum.x + 1):
		for z in range(minimum.y, maximum.y + 1):
			for first: int in _road_grid.get(Vector2i(x, z), []):
				var a := _road_faces[first]
				var b := _road_faces[first + 1]
				var c := _road_faces[first + 2]
				var bary := _barycentric(point, a, b, c)
				if minf(bary.x, minf(bary.y, bary.z)) >= -0.00001:
					return true
				if margin > 0.0:
					var av := Vector2(a.x, a.z)
					var bv := Vector2(b.x, b.z)
					var cv := Vector2(c.x, c.z)
					if _segment_distance(point, av, bv) < margin or _segment_distance(point, bv, cv) < margin or _segment_distance(point, cv, av) < margin:
						return true
	return false

func _segment_distance(point: Vector2, a: Vector2, b: Vector2) -> float:
	var delta := b - a
	return point.distance_to(a + delta * clampf((point - a).dot(delta) / maxf(delta.length_squared(), 0.000001), 0.0, 1.0))

func _plant_bank(bank: Dictionary) -> void:
	var center: Vector2 = bank.center
	var radius: Vector2 = bank.radius
	var count: int = bank.count
	var height: float = bank.height
	var cape := center.y < -5.0
	for i in count:
		# Offset lobes and a spiral with randomized angles give cohesive islands,
		# rather than a uniform scatter or a rectangular carpet of clones.
		var angle := float(i) * 2.399963 + _rng.randf_range(-0.40, 0.40)
		var distance := sqrt((float(i) + _rng.randf()) / float(count))
		var ragged := 0.78 + 0.19 * sin(angle * 3.0 + center.x) + _rng.randf_range(-0.07, 0.14)
		var point := center + Vector2(cos(angle), sin(angle)) * radius * distance * ragged
		var size := _rng.randf_range(0.31, 0.55) * height
		if i % 7 == 0 and height > 0.57:
			_try_place("shrub", point, Vector3(size * 1.72, size * 0.80, size * 1.65), bank.label, 0.17 * height)
		else:
			_try_place("fan", point, Vector3(size * 1.05, size * 0.90, size * 1.05), bank.label, 0.09 * height)
		if _card_ready:
			var tile_choices := [0, 1, 2, 3, 4, 5, 5, 5, 6, 7, 13, 14]
			var tile: int = tile_choices[(i + _rng.randi_range(0, 11)) % 12]
			var card_height := _rng.randf_range(0.26, 0.49) * height
			_card_clump(point, card_height, tile, bank.label, 2 if height > 0.72 or i % 3 == 0 else 1)
		if i % 8 == 3 and height > 0.55:
			var fern_size := _rng.randf_range(0.30, 0.46) * height
			_try_place("fern", point + Vector2(0.11, 0.10), Vector3.ONE * fern_size, bank.label, 0.10 * height)
		if i % 9 == 2:
			if _card_ready:
				_card_clump(point + Vector2(-0.10, 0.06), _rng.randf_range(0.28, 0.46) * height, 9 if i % 3 == 0 else (10 if i % 2 == 0 else 8), bank.label, 1)
			elif not cape and i < 15:
				_try_place("flower", point + Vector2(-0.06, 0.06), Vector3.ONE * _rng.randf_range(0.26, 0.42) * height, bank.label, 0.075 * height)
		if i % 10 == 1:
			_try_place("pebble", point + Vector2(0.14, -0.16), Vector3.ONE * _rng.randf_range(0.025, 0.060), bank.label, 0.035)

func _plant_road_edge() -> void:
	# Unequal patches grow out from the road into the banks. Several longitudinal
	# gaps are left completely open; no regular row of isolated potted clumps.
	var patch_centers := [-9.65, -7.9, -5.25, -3.85, -1.85, 0.65, 2.90, 5.25, 7.7, 9.6]
	for patch in patch_centers.size():
		for side: float in [-1.0, 1.0]:
			if (patch == 3 and side < 0.0) or (patch == 7 and side > 0.0):
				continue
			var center_x: float = patch_centers[patch] + _rng.randf_range(-0.22, 0.22)
			var half_length := _rng.randf_range(0.38, 0.78)
			var width := _rng.randf_range(0.34, 0.72)
			var count := _rng.randi_range(7, 12)

			for sample in count:
				var angle := float(sample) * 2.399963 + _rng.randf_range(-0.22, 0.22)
				var d := sqrt((float(sample) + 0.5) / float(count))
				var x := center_x + cos(angle) * half_length * d
				var center_z := _road_center_hint(x)
				var boundary_z := center_z
				for step in range(1, 24):
					var test_z := center_z + side * float(step) * 0.09
					if not is_road(Vector2(x, test_z), 0.02):
						boundary_z = test_z
						break
				var outward := 0.10 + width * (0.50 + sin(angle) * d * 0.50)
				var point := Vector2(x, boundary_z + side * outward)
				var size := _rng.randf_range(0.14, 0.28) * (0.83 + outward * 0.35)
				# Consume the same random choices even for reclaimed peripheral cards,
				# so enabling the ledge layer cannot rearrange later verge/canopy art.
				_skip_this_placement = _use_ledges() and absf(center_x) > 7.0 and sample >= 3
				if _card_ready:
					var tiles := [1, 1, 0, 5, 13]
					_card_clump(point, size, tiles[(sample + patch) % tiles.size()], "ragged_verge", 1)
				else:
					_try_place("fan", point, Vector3(size * 0.94, size * 0.70, size * 0.94), "ragged_verge", 0.05)
				_skip_this_placement = false
				if sample == 0 and patch % 3 == 0:
					_try_place("pebble", point + Vector2(0.08, -side * 0.08), Vector3.ONE * _rng.randf_range(0.02, 0.045), "ragged_verge", 0.025)

func _road_center_hint(x: float) -> float:
	var points := [Vector2(-14.0, 0.0), Vector2(-9.0, -0.5), Vector2(-4.0, -0.5), Vector2(0.0, 0.0), Vector2(4.0, 1.3), Vector2(9.0, 0.3), Vector2(14.0, -1.4)]
	for i in range(points.size() - 1):
		if x >= points[i].x and x <= points[i + 1].x:
			return lerpf(points[i].y, points[i + 1].y, inverse_lerp(points[i].x, points[i + 1].x, x))
	return 0.0

func _collect_wall_surfaces() -> void:
	# A separate exact triangle set for attachment to vertical authored stone.
	# The ground sampler deliberately excludes these steep faces.
	for source_key: String in _sources:
		if source_key not in ["cliffheadland", "cliffcape"] and not source_key.begins_with("rockshore"):
			continue
		var source: MeshInstance3D = _sources[source_key]
		var faces := source.mesh.get_faces()
		for index in range(0, faces.size(), 3):
			var a := source.global_transform * faces[index]
			var b := source.global_transform * faces[index + 1]
			var c := source.global_transform * faces[index + 2]
			var normal := (b - a).cross(c - a).normalized()
			if absf(normal.y) > 0.91:
				continue
			_wall_faces.append(a)
			_wall_faces.append(b)
			_wall_faces.append(c)
			_wall_source_names.append(String(source.name))

func sample_wall(origin: Vector3, direction: Vector3, maximum_distance := 2.0) -> Dictionary:
	var nearest := maximum_distance
	var result: Dictionary = {}
	for index in range(0, _wall_faces.size(), 3):
		var a := _wall_faces[index]
		var b := _wall_faces[index + 1]
		var c := _wall_faces[index + 2]
		var intersection: Variant = Geometry3D.ray_intersects_triangle(origin, direction, a, b, c)
		if not intersection is Vector3:
			continue
		var point: Vector3 = intersection
		var distance := origin.distance_to(point)
		if distance > nearest:
			continue
		nearest = distance
		var normal := (b - a).cross(c - a).normalized()
		if normal.dot(direction) > 0.0:
			normal = -normal
		result = {"position": point, "normal": normal, "source": _wall_source_names[index / 3]}
	return result

func _plant_cliff_attachments() -> void:
	if not _card_ready or _wall_faces.is_empty():
		return
	var rng := RandomNumberGenerator.new()
	rng.seed = SEED + 204
	# Art-directed gaps between root sites preserve the main stone planes.
	var x_sites := [-5.65, -4.90, -4.00, -2.60, -1.50, -0.10, 1.35, 2.45]
	for site in x_sites.size():
		var x: float = x_sites[site]
		var lip: Dictionary = {}
		for step in 107:
			var point := Vector2(x, -11.4 + float(step) * 0.055)
			var hit := sample_ground(point)
			if not hit.is_empty() and hit.position.y > 0.28:
				lip = hit
		if lip.is_empty():
			continue
		var position: Vector3 = lip.position
		for sprig in 2:
			var origin := position + Vector3(float(sprig) * 0.16 - 0.07, -0.045, 0.65)
			var wall := sample_wall(origin, Vector3.FORWARD, 1.4)
			if wall.is_empty():
				continue
			var tile := 11 if sprig == 0 and site % 3 != 1 else 12
			var height := rng.randf_range(0.38, 0.59) if tile == 11 else rng.randf_range(0.22, 0.34)
			_attach_wall_card(wall, tile, height, true, rng.randf_range(-0.20, 0.20), "cape_hanging_ivy")
			if sprig == 0 and site % 2 == 0:
				_attach_wall_card(wall, 1, rng.randf_range(0.17, 0.24), false, rng.randf_range(-0.16, 0.16), "cape_lip_grass")
	# A few visible stone ledges receive short moss/ivy, never a random wall carpet.
	for point: Vector2 in [Vector2(2.15, -2.15), Vector2(2.70, -1.85), Vector2(3.25, -2.20), Vector2(0.95, -2.70)]:
		var top := sample_ground(point)
		if top.is_empty():
			continue
		for sprig in 2:
			var origin: Vector3 = top.position + Vector3(float(sprig) * 0.13, -0.035, 0.85)
			var wall := sample_wall(origin, Vector3.FORWARD, 1.55)
			if wall.is_empty():
				continue
			_attach_wall_card(wall, 12 if sprig == 0 else 11, rng.randf_range(0.20, 0.32), true, rng.randf_range(-0.28, 0.28), "shore_ledge_ivy")

func _attach_wall_card(hit: Dictionary, tile: int, height: float, hanging: bool, roll: float, bank: String) -> void:
	var normal: Vector3 = hit.normal
	var growth := Vector3.DOWN if hanging else Vector3.UP
	var up := growth.slide(normal).normalized()
	if up.length_squared() < 0.1:
		return
	var right := up.cross(normal).normalized()
	var orientation := Basis(right, up, normal).orthonormalized().rotated(normal, roll)
	var info: Dictionary = _atlas_tiles.get(tile, {})
	var aspect: float = info.get("pixel_aspect_width_over_height", 1.20)
	var position: Vector3 = hit.position + normal * 0.013
	_try_place("card", Vector2(position.x, position.z), Vector3(height * aspect, height, height), bank, 0.0, tile, 0.0, {"position": position, "normal": normal, "basis": orientation, "anchor_mode": "authored_stone", "surface_point": hit.position, "surface_source": hit.source, "tint": Color("e1e7ca") if hanging else Color("edf0cf")})

func _load_atlas_metadata() -> void:
	_atlas_tiles.clear()
	var path := "res://assets/textures/coastal_foliage_atlas_0724.json"
	if not FileAccess.file_exists(path):
		return
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not parsed is Dictionary:
		return
	for tile: Dictionary in parsed.get("tiles", []):
		_atlas_tiles[int(tile.index)] = tile

func _plant_ledge_drapes() -> void:
	if not _card_ready:
		return
	# Find the actual camera-facing grassy cliff lip, with gaps around the apron.
	# These low sprays connect cape top cover to its vertical stone silhouette.
	for sample in 19:
		if sample % 6 == 4:
			continue
		var x := -6.15 + float(sample) * 0.39 + _rng.randf_range(-0.10, 0.10)
		var last := Vector2(INF, INF)
		for step in 62:
			var point := Vector2(x, -10.90 + float(step) * 0.055)
			var hit := sample_ground(point)
			if not hit.is_empty() and hit.position.y > 0.28:
				last = point
		if last.x == INF:
			continue
		var height := _rng.randf_range(0.17, 0.26)
		var tile: int = 12 if sample % 4 != 0 else 11
		var info: Dictionary = _atlas_tiles.get(tile, {})
		var aspect: float = info.get("pixel_aspect_width_over_height", 1.40)
		_try_place("card", last + Vector2(0.0, -0.025), Vector3(height * aspect, height, height), "cape_ledge", 0.04, tile, _rng.randf_range(-0.32, 0.32))

func _card_clump(point: Vector2, height: float, tile: int, bank: String, layers: int) -> void:
	var yaw := _rng.randf_range(-PI, PI)
	var tile_info: Dictionary = _atlas_tiles.get(tile, {})
	var aspect: float = tile_info.get("pixel_aspect_width_over_height", 1.18)
	if tile_info.has("suggested_whole_card_height_m_range"):
		height = minf(height, float(tile_info.suggested_whole_card_height_m_range[1]))
	for layer in layers:
		var offset := Vector2(_rng.randf_range(-0.045, 0.045), _rng.randf_range(-0.045, 0.045))
		var width := height * aspect * _rng.randf_range(0.94, 1.06)
		_try_place("card", point + offset, Vector3(width, height, width), bank, width * 0.20, tile, yaw + layer * 1.70)

func _recompose_original_accents() -> void:
	# Preserve a few tall silhouettes, while the two older large foreground fronds
	# become compatible accents within the new, finer-grained banks.
	_resize_source_group(["FernStemA", "FernLeafletA.001", "FernStemA.001", "FernLeafletA.002", "FernStemA.002", "FernLeafletA.003", "FernStemA.003", "FernLeafletA.004"], 0.58)
	_resize_source_group(["LeafFanA.005"], 0.64)
	_resize_source_group(["LeafFanA.001"], 0.72)
	_resize_source_group(["LeafShrubRound", "TrunkShrubRound"], 0.55)
	_resize_source_group(["LeafShrubRound.001", "TrunkShrubRound.001"], 0.65)
	for suffix: String in ["", ".001", ".002"]:
		_resize_source_group(["FlowerCream" + suffix, "FlowerCenter" + suffix, "FlowerStem" + suffix], 0.60)

func _compose_canopy_preview() -> void:
	if not _card_ready:
		return
	var centers := [Vector3(-4.45, 2.30, -10.10), Vector3(-5.55, 2.25, -10.30), Vector3(-4.80, 2.65, -10.15), Vector3(-5.25, 1.65, -9.72)]
	var kept := ["leafshrubroundtreea", "leafshrubroundtreea001", "leafshrubroundtreea002", "leafshrubroundtreea003"]
	# Four shrunken authored 3D leaf meshes provide interior volume. All other
	# disconnected oversized crown sprays are hidden only in this explicit preview.
	for source_key: String in _sources:
		if not source_key.begins_with("leafshrubroundtreea"):
			continue
		var source: MeshInstance3D = _sources[source_key]
		var mass := kept.find(source_key)
		if mass < 0:
			source.visible = false
			_hidden_source_nodes.append(String(source.name))
		else:
			var adjusted := source.global_transform
			adjusted.basis = adjusted.basis.scaled(Vector3.ONE * 0.44)
			adjusted.origin = centers[mass] - adjusted.basis * source.mesh.get_aabb().get_center()
			source.global_transform = adjusted
			_resized_source_nodes.append(String(source.name))
	for mass in centers.size():
		var center: Vector3 = centers[mass]
		for leaf in 7:
			var angle := float(leaf) * 2.399963 + mass * 0.8
			var spread := 0.17 + sqrt(float(leaf) / 7.0) * 0.27
			var position := center + Vector3(cos(angle) * spread, -0.18 + _rng.randf_range(-0.08, 0.12), sin(angle) * spread * 0.68)
			var height := _rng.randf_range(0.35, 0.46) * (0.77 if mass == 3 else 1.0)
			var tile := 3 if leaf % 3 == 0 else (5 if leaf == 1 else 4)
			var info: Dictionary = _atlas_tiles.get(tile, {})
			var aspect: float = info.get("pixel_aspect_width_over_height", 1.18)
			var tint := Color("fff3c7") if leaf % 3 == 0 else (Color("c1d7b7") if leaf == 1 else Color("e6edc7"))
			_try_place("card", Vector2(position.x, position.z), Vector3(height * aspect, height, height), "canopy_mass", 0.0, tile, 0.66 + _rng.randf_range(-0.65, 0.65), {"position": position, "normal": Vector3.UP, "tilt": Vector2(_rng.randf_range(-0.40, 0.38), _rng.randf_range(-0.20, 0.20)), "tint": tint})

func _resize_source_group(names: Array, factor: float) -> void:
	var first := _sources.get(_key(names[0])) as MeshInstance3D
	if first == null:
		return
	var anchor := first.global_position
	var hit := sample_ground(Vector2(anchor.x, anchor.z))
	var grounded: Vector3 = hit.position if not hit.is_empty() else anchor
	for source_name: String in names:
		var source := _sources.get(_key(source_name)) as MeshInstance3D
		if source == null:
			continue
		var adjusted := source.global_transform
		adjusted.origin = grounded + (adjusted.origin - anchor) * factor
		adjusted.basis = adjusted.basis.scaled(Vector3.ONE * factor)
		source.global_transform = adjusted
		_resized_source_nodes.append(String(source.name))

func _occludes_hero(position: Vector3, height: float, radius: float) -> bool:
	# Camera endpoints include the three normal modes plus the composed portrait.
	# Spherical silhouette volumes conservatively cover wheel/frame/head shapes.
	var cameras := [Vector3(5.15, 3.45, 6.7), Vector3(-4.2, 2.65, 7.1), Vector3(7.75, 3.0, 5.2), Vector3(7.5, 2.35, 4.05)]
	var shapes := [Vector4(-0.76, 0.48, 0.0, 0.45), Vector4(0.76, 0.48, 0.0, 0.45), Vector4(0.0, 1.0, 0.0, 0.58), Vector4(0.15, 2.2, 0.0, 0.85)]
	for camera: Vector3 in cameras:
		for weight: float in [0.35, 0.75, 1.0]:
			var sample := position + Vector3.UP * height * weight
			var ray := (sample - camera).normalized()
			var plant_distance := camera.distance_to(sample)
			for sphere: Vector4 in shapes:
				var center := Vector3(sphere.x, sphere.y, sphere.z)
				var depth := (center - camera).dot(ray)
				if depth <= plant_distance + 0.18:
					continue
				var distance := (camera + ray * depth).distance_to(center)
				if distance < sphere.w + radius * 0.5:
					return true
	return false

func _try_place(kind: String, point: Vector2, size: Vector3, bank: String, radius: float, tile := -1, yaw := INF, anchor_override: Dictionary = {}) -> bool:
	if not _prototypes.has(kind):
		return false
	var pieces: Array = _prototypes[kind]
	var triangle_limit := MAX_ADDED_TRIANGLES if kind == "card" else MAX_SOLID_TRIANGLES
	if _mesh_count + pieces.size() > MAX_MESH_INSTANCES or _triangle_count + int(_prototype_triangle_counts[kind]) > triangle_limit:
		return false
	if anchor_override.is_empty() and is_road(point, ROAD_MARGIN + radius):
		return false
	var hit := sample_ground(point) if anchor_override.is_empty() else anchor_override
	if hit.is_empty():
		return false
	# Check the actual presentation sightlines instead of clearing a broad world
	# rectangle, which previously left a conspicuously empty foreground bank.
	var approximate_height := size.y * (1.05 if kind in ["shrub", "fern", "card"] else 0.72)
	if _occludes_hero(hit.position, approximate_height, radius):
		if kind in ["shrub", "fern", "flower"]:
			return false
		size.y = minf(size.y, 0.13 if kind == "card" else 0.18)
	# Avoid trunks, doorway/steps, and the deliberately open lighthouse apron.
	if point.distance_to(Vector2(-3.0, -9.65)) < 0.76:
		return false
	var position: Vector3 = hit.position
	var normal: Vector3 = Vector3.UP.lerp(hit.normal, 0.20).normalized()
	var angle := _rng.randf_range(-PI, PI) if yaw == INF else yaw
	var tilt: Vector2 = anchor_override.get("tilt", Vector2.ZERO)
	var basis := Basis(Quaternion(Vector3.UP, normal)) * Basis(Vector3.UP, angle) * Basis(Vector3.RIGHT, tilt.x) * Basis(Vector3.FORWARD, tilt.y) * Basis.from_scale(size)
	if anchor_override.has("basis"):
		basis = anchor_override.basis * Basis.from_scale(size)
	var source: MeshInstance3D = pieces[0]
	var anchor := source.global_position
	# RockShoreA has an underwater authored base; its highest part becomes a small
	# grounded path stone by burying the lower 80% of the original mesh volume.
	if kind == "pebble":
		position.y -= 0.07 * size.y
	elif kind == "shrub":
		position.y -= 0.18 * size.y
	elif kind == "card":
		position.y += 0.005 - CARD_ROOT_FRACTION * size.y
	else:
		position.y -= 0.012
	var transform := Transform3D(basis, position)
	var tint_index := _rng.randi_range(0, 4)
	var tint: Color = anchor_override.get("tint", [Color("f2edc7"), Color("e3efdf"), Color("eaf0d6"), Color("fff2c3"), Color("d9e8d6")][tint_index])
	if _skip_this_placement:
		return false
	var group := Node3D.new()
	group.name = "%s_%03d" % [bank, _serial]
	_root.add_child(group)
	_serial += 1
	group.set_meta("authored_plant_kind", kind)
	group.set_meta("ground_position", hit.position)
	for piece: MeshInstance3D in pieces:
		var instance := MeshInstance3D.new()
		instance.name = ("LeafAtlas" if kind == "card" else String(piece.name).get_slice(".", 0)) + "Planted%03d" % _mesh_count
		instance.mesh = piece.mesh
		instance.skeleton = NodePath()
		instance.cast_shadow = piece.cast_shadow
		instance.layers = piece.layers
		instance.material_override = piece.material_override
		for surface in piece.mesh.get_surface_count():
			instance.set_surface_override_material(surface, piece.get_surface_override_material(surface))
		group.add_child(instance)
		var relative := piece.global_transform
		relative.origin -= anchor
		# A template library object may be stored below the landscape; subtract its
		# placement without changing the authored local vertices or UVs.
		instance.global_transform = transform * relative
		instance.set_meta("authored_source", String(piece.name))
		instance.set_meta("planting_bank", bank)
		instance.set_meta("foliage_tint", tint)
		instance.set_meta("foliage_tint_index", tint_index)
		instance.set_meta("wind_root_y", hit.position.y)
		if kind == "card":
			# The shader moves roots within the atlas crop and bends the card in wind.
			# Keep those visible vertices inside the culling volume without mesh edits.
			var tile_info: Dictionary = _atlas_tiles.get(tile, {})
			var root_uv: Array = tile_info.get("root_in_crop_uv", [0.5, 1.0])
			var bounds := piece.mesh.get_aabb()
			var root_shift := maxf(absf(float(root_uv[0]) - 0.5) * bounds.size.x, absf(1.0 - float(root_uv[1])) * bounds.size.y)
			instance.extra_cull_margin = maxf(0.35, root_shift + 0.055)
			instance.set_meta("foliage_atlas_tile", tile)
		_mesh_count += 1
	_triangle_count += int(_prototype_triangle_counts[kind])
	placements.append({"kind": kind, "point": point, "position": hit.position, "radius": radius, "bank": bank, "scale": size, "tile": tile, "anchor_mode": "terrain" if anchor_override.is_empty() else anchor_override.get("anchor_mode", "authored_canopy"), "surface_point": anchor_override.get("surface_point", hit.position), "surface_normal": hit.normal, "surface_source": anchor_override.get("surface_source", "")})
	return true

func batch_cards(imported_world: Node3D) -> Dictionary:
	## Call only AFTER ToonPalette.apply. No material, tint, mesh, or placement
	## changes: this replaces repeated draw submissions with authored-mesh instances.
	const BATCH_ROOT := "CoastalFoliageBatches"
	var previous := imported_world.get_node_or_null(BATCH_ROOT)
	if previous != null:
		return previous.get_meta("batch_report", {})
	var groups: Dictionary = {}
	for node in imported_world.find_children("*", "MeshInstance3D", true, false):
		var card := node as MeshInstance3D
		if card == null or not card.has_meta("foliage_atlas_tile") or not card.is_visible_in_tree():
			continue
		if card.mesh == null or card.material_override == null:
			continue
		# Includes every render-state field used by our authored card instances.
		var key := "%d:%d:%d:%d" % [card.mesh.get_instance_id(), card.material_override.get_instance_id(), card.cast_shadow, card.layers]
		if not groups.has(key):
			groups[key] = []
		groups[key].append(card)
	var batch_root := Node3D.new()
	batch_root.name = BATCH_ROOT
	imported_world.add_child(batch_root)
	var card_count := 0
	var batch_count := 0
	for key: String in groups:
		var cards: Array = groups[key]
		var first: MeshInstance3D = cards[0]
		var multimesh := MultiMesh.new()
		multimesh.transform_format = MultiMesh.TRANSFORM_3D
		multimesh.use_colors = false
		multimesh.use_custom_data = false
		multimesh.mesh = first.mesh
		multimesh.instance_count = cards.size()
		var batch := MultiMeshInstance3D.new()
		batch.name = "AuthoredLeafBatch%03d" % batch_count
		batch.multimesh = multimesh
		batch.material_override = first.material_override
		batch.cast_shadow = first.cast_shadow
		batch.layers = first.layers
		batch_root.add_child(batch)
		var paths: Array[String] = []
		var transform_buffer := PackedFloat32Array()
		transform_buffer.resize(cards.size() * 12)
		var combined := AABB()
		var first_bounds := true
		var inverse := batch.global_transform.affine_inverse()
		for i in cards.size():
			var card: MeshInstance3D = cards[i]
			var local := inverse * card.global_transform
			_store_multimesh_transform(transform_buffer, i, local)
			# Bounds cover exact per-tile root shifts and all animated wind vertices.
			# Grow in card-local space before transforming into the batch space.
			var conservative := local * card.mesh.get_aabb().grow(card.extra_cull_margin)
			combined = conservative if first_bounds else combined.merge(conservative)
			first_bounds = false
			paths.append(String(imported_world.get_path_to(card)))
			card.set_meta("batched_foliage", true)
			card.set_meta("foliage_batch", String(imported_world.get_path_to(batch)))
			card.set_meta("foliage_batch_instance", i)
			card.visible = false
			card_count += 1
		# One upload also retains a verifiable CPU buffer in the headless renderer.
		multimesh.buffer = transform_buffer
		multimesh.custom_aabb = combined.grow(0.012)
		batch.set_meta("authored_source", String(first.get_meta("authored_source", "FoliageCardTemplate")))
		batch.set_meta("source_card_paths", paths)
		batch.set_meta("foliage_atlas_tile", int(first.get_meta("foliage_atlas_tile")))
		batch.set_meta("foliage_batch", true)
		batch_count += 1
	var result := {"source_cards": card_count, "batches": batch_count, "card_draw_reduction": card_count - batch_count, "authored_mesh_reused": true}
	batch_root.set_meta("batch_report", result)
	print("Coastal foliage batches: ", result)
	return result

func _store_multimesh_transform(buffer: PackedFloat32Array, index: int, value: Transform3D) -> void:
	# Godot MultiMesh TRANSFORM_3D is three row-major vec4 rows, translation in w.
	# No colors/custom data are enabled, so each instance is exactly12 floats.
	var at := index * 12
	buffer[at] = value.basis.x.x
	buffer[at + 1] = value.basis.y.x
	buffer[at + 2] = value.basis.z.x
	buffer[at + 3] = value.origin.x
	buffer[at + 4] = value.basis.x.y
	buffer[at + 5] = value.basis.y.y
	buffer[at + 6] = value.basis.z.y
	buffer[at + 7] = value.origin.y
	buffer[at + 8] = value.basis.x.z
	buffer[at + 9] = value.basis.y.z
	buffer[at + 10] = value.basis.z.z
	buffer[at + 11] = value.origin.z
