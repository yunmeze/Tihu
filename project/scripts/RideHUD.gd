extends Control
## Lightweight native HUD; the authored scene keeps most of the screen.
const REGULAR := preload("res://assets/fonts/Sans.ttf")
const BOLD := preload("res://assets/fonts/Sans-Bold.ttf")
const SERIF := preload("res://assets/fonts/Serif.otf")
const INK := Color("234b57")
const MUTED := Color("55747a")
const CREAM := Color("fcf6e7")
const TEAL := Color("286e74")
var ride: Node3D
var hit_areas: Dictionary = {}
var hovered := ""

func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE

func set_ride(value: Node3D) -> void:
	ride = value
	queue_redraw()

func _label(value: String, position: Vector2, size_px: int, color := INK, font: Font = REGULAR) -> void:
	draw_string(font, position, value, HORIZONTAL_ALIGNMENT_LEFT, -1, size_px, color)

func _pill(rect: Rect2, fill: Color, border: Color = Color.TRANSPARENT) -> void:
	var style := StyleBoxFlat.new()
	style.bg_color = fill
	style.corner_radius_top_left = int(rect.size.y * 0.5)
	style.corner_radius_top_right = int(rect.size.y * 0.5)
	style.corner_radius_bottom_left = int(rect.size.y * 0.5)
	style.corner_radius_bottom_right = int(rect.size.y * 0.5)
	if border.a > 0.0:
		style.border_color = border
		style.set_border_width_all(1)
	draw_style_box(style, rect)

func _button(id: String, text: String, rect: Rect2, active := false) -> void:
	hit_areas[id] = rect
	var fill := TEAL if active else Color("fffaf0")
	if hovered == id and not active:
		fill = Color("e5efe4")
	_pill(rect, fill, Color("c6d4ca") if not active else Color.TRANSPARENT)
	var width := BOLD.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, 12).x
	_label(text, rect.position + Vector2((rect.size.x - width) * 0.5, rect.size.y * 0.5 + 4.0), 12, CREAM if active else INK, BOLD)

func _draw() -> void:
	if ride == null:
		return
	hit_areas.clear()
	var w := size.x
	var h := size.y
	var margin := 34.0
	_label("PELICAN PEDAL CLUB", Vector2(margin, 38), 12, INK, BOLD)
	_label("Coastal daydream", Vector2(margin - 1, 82), 34, INK, SERIF)
	_label("A little sun. A sea breeze. No hurry.", Vector2(margin, 106), 13, MUTED)
	var badge := Rect2(w - 195, 24, 162, 30)
	_pill(badge, Color(0.98, 0.97, 0.88, 0.88))
	draw_circle(badge.position + Vector2(16, 15), 3, Color("cd9851"))
	_label("HAND-CRAFTED COAST", badge.position + Vector2(26, 19), 10, INK, BOLD)
	var panel_w := minf(970.0, w - 52.0)
	var panel := Rect2((w - panel_w) * 0.5, h - 92, panel_w, 64)
	_pill(Rect2(panel.position + Vector2(0, 4), panel.size), Color(0.15, 0.24, 0.26, 0.13))
	_pill(panel, Color(0.99, 0.975, 0.92, 0.97), Color("d9dfcf"))
	_label("%02d" % int(ride.speed_kmh), panel.position + Vector2(23, 39), 27, INK, BOLD)
	_label("km/h", panel.position + Vector2(67, 39), 10, MUTED)
	_label("%.2f km" % (ride.distance_m / 1000.0), panel.position + Vector2(110, 30), 12, INK, BOLD)
	_label("OF DAYDREAMING", panel.position + Vector2(110, 46), 8, MUTED)
	var start_x := panel.position.x + 234
	var compact := w < 1100
	var button_w := 85.0 if compact else 100.0
	for i in range(3):
		_button("camera%d" % i, ["1  POSTCARD", "2  FOLLOW", "3  PORTRAIT"][i], Rect2(start_x + i * (button_w + 5), panel.position.y + 14, button_w, 36), ride.camera_mode == i)
	var right := panel.end.x - 18
	_button("reset", "RESET", Rect2(right - 65, panel.position.y + 14, 65, 36))
	_button("faster", "+", Rect2(right - 107, panel.position.y + 14, 36, 36))
	_button("slower", "−", Rect2(right - 149, panel.position.y + 14, 36, 36))
	_button("pause", "PLAY" if ride.paused else "PAUSE", Rect2(right - 228, panel.position.y + 14, 73, 36), ride.paused)
	_label("DRAG TO ORBIT   ·   SCROLL TO ZOOM", Vector2(margin, h - 114), 9, MUTED)
	var caption := "SEA BREEZE / SOFT DAYLIGHT"
	_label(caption, Vector2(w - 234, h - 114), 9, MUTED, BOLD)
	if not ride.asset_loaded:
		var box := Rect2(w * 0.5 - 235, h * 0.5 - 50, 470, 100)
		_pill(box, CREAM)
		_label("The coastal studio", box.position + Vector2(30, 38), 24, INK, SERIF)
		_label(ride.asset_message, box.position + Vector2(30, 65), 13, MUTED)

func _input(event: InputEvent) -> void:
	if event is InputEventMouseMotion:
		var next := ""
		for id: String in hit_areas:
			if hit_areas[id].has_point(event.position):
				next = id
		if next != hovered:
			hovered = next
			mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND if not hovered.is_empty() else Control.CURSOR_ARROW
			queue_redraw()
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
		for id: String in hit_areas:
			if hit_areas[id].has_point(event.position):
				activate(id)
				get_viewport().set_input_as_handled()
				return

func activate(id: String) -> void:
	match id:
		"camera0": ride.set_camera_mode(0)
		"camera1": ride.set_camera_mode(1)
		"camera2": ride.set_camera_mode(2)
		"pause": ride.toggle_pause()
		"slower": ride.adjust_speed(-2.0)
		"faster": ride.adjust_speed(2.0)
		"reset": ride.reset_ride()
	queue_redraw()
