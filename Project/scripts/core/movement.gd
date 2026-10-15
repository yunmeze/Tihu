extends RefCounted
# R1 reference-adapted movement, not a claim of original EXE timing parity.
const WALK_SPEED := 1.5625
const RUN_SPEED := 3.125
const DIRS := [Vector2i(0,-1), Vector2i(1,-1), Vector2i(1,0), Vector2i(1,1), Vector2i(0,1), Vector2i(-1,1), Vector2i(-1,0), Vector2i(-1,-1)]
var grid := AStarGrid2D.new()
var position := Vector2(61,39)
var path: Array[Vector2i] = []
var direction := 4
var action := "idle"
var animation_tick := 0
var width := 0
var height := 0

func configure(w: int, h: int, flags: Array, occupied: Array = []) -> void:
	width = w
	height = h
	grid.region = Rect2i(0,0,w,h)
	grid.cell_size = Vector2.ONE
	grid.diagonal_mode = AStarGrid2D.DIAGONAL_MODE_ONLY_IF_NO_OBSTACLES
	grid.default_compute_heuristic = AStarGrid2D.HEURISTIC_CHEBYSHEV
	grid.default_estimate_heuristic = AStarGrid2D.HEURISTIC_CHEBYSHEV
	grid.update()
	for x in w:
		for y in h:
			grid.set_point_solid(Vector2i(x,y), int(flags[x*h+y]) in [-1,-2,-3])
	for cell in occupied:
		if cell is Vector2i and grid.is_in_boundsv(cell): grid.set_point_solid(cell)

func can_enter(cell: Vector2i) -> bool:
	return grid.is_in_boundsv(cell) and not grid.is_point_solid(cell)

func request(target: Vector2i) -> bool:
	var start := Vector2i(roundi(position.x),roundi(position.y))
	if not can_enter(start) or not can_enter(target): return false
	var route: Array[Vector2i] = grid.get_id_path(start,target)
	if route.is_empty(): return false
	path.clear()
	for i in range(1,route.size()): path.append(route[i])
	if path.is_empty() and position.distance_to(Vector2(start)) > 0.000001: path.append(start)
	return true

func stop() -> void:
	path.clear()
	_set_action("idle")

func step(delta: float, run: bool = false) -> void:
	_set_action("idle" if path.is_empty() else ("run" if run else "walk"))
	animation_tick += 1
	var budget := delta * (RUN_SPEED if run else WALK_SPEED)
	while not path.is_empty() and budget > 0.000001:
		var goal := Vector2(path[0])
		var difference := goal-position
		var distance: float = maxf(absf(difference.x),absf(difference.y))
		if distance < 0.000001:
			position = goal
			path.pop_front()
			continue
		var facing := Vector2i(signi(roundi(difference.x*100000)),signi(roundi(difference.y*100000)))
		var found := DIRS.find(facing)
		if found >= 0: direction = found
		var amount := minf(distance,budget)
		position += difference / distance * amount
		budget -= amount
		if amount >= distance-0.000001:
			position = goal
			path.pop_front()
	if path.is_empty(): _set_action("idle")

func _set_action(value: String) -> void:
	if action != value:
		action = value
		animation_tick = 0

func source_frame() -> int:
	if action == "walk": return 33+direction*6+(animation_tick/7)%6
	if action == "run": return 81+direction*6+(animation_tick/5)%6
	return 1+direction*4+(animation_tick/12)%4
