extends Control
## Optional art review only; never selects or replaces gameplay assets.
const IDS := [45, 46, 47, 48, 49, 50]
const SOURCE_DIR := "res://art_source/hero_e_walk_source_r8/"
const RESEARCH_PATHS := [
	"res://art_source/earth_e45_vertical_leg_research_v1/45-HD4-CLOTH-CLEANED-RESEARCH.png",
	"res://art_source/earth_e_walk_layered_research_v1/46-HD4-RESEARCH.png",
	"res://art_source/earth_e_walk_layered_research_v1/47-HD4-RESEARCH.png",
	"res://art_source/earth_e48_vertical_leg_research_v1/48-HD4-BOUNDED-DONOR-DIAGNOSTIC.png",
	"res://art_source/earth_e_walk_layered_research_v1/49-HD4-RESEARCH.png",
	"res://art_source/earth_e_walk_layered_research_v1/50-HD4-RESEARCH.png",
]
const FRAME_TICKS := 7
const SLOW_FACTOR := 4
const DISPLAY_SCALE := 3.0
const LOGICAL_ROOT := Vector2(16, 64)
const PANEL_SIZE := Vector2(384, 384)
const PANEL_ORIGINS := [Vector2(64, 178), Vector2(560, 178)]
var source_frames: Array[Texture2D] = []
var research_frames: Array[Texture2D] = []
var ready_ok := false
var paused := false
var slow := false
var frame_index := 0
var elapsed_ticks := 0
var failure := ""
var frame_label := Label.new()
var pause_button := Button.new()
var slow_button := Button.new()
var step_button := Button.new()

func _ready() -> void:
	get_window().title = "E 步行美术研究预览 · 未完成实机验收"
	get_window().content_scale_size = Vector2i(1024, 768)
	get_window().content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	get_window().content_scale_aspect = Window.CONTENT_SCALE_ASPECT_KEEP
	get_window().size = Vector2i(1024, 768)
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	var font := SystemFont.new()
	font.font_names = PackedStringArray(["Noto Sans CJK SC", "Noto Sans CJK", "Microsoft YaHei", "SimHei", "PingFang SC", "sans-serif"])
	theme = Theme.new()
	theme.default_font = font
	theme.default_font_size = 18
	_label("E 方向步行 · 45–50 原图 / 最新研究稿", Vector2(32, 24), 28)
	var status := _label("研究预览，未完成实机验收", Vector2(32, 68), 22)
	status.modulate = Color("ffd287")
	_label("原始完整画布（含头部）", Vector2(64, 136), 20)
	_label("最新研究稿（含 45 / 48 新版本）", Vector2(560, 136), 20)
	frame_label.position = Vector2(32, 590)
	add_child(frame_label)
	pause_button.position = Vector2(32, 634)
	pause_button.custom_minimum_size = Vector2(180, 40)
	pause_button.pressed.connect(toggle_pause)
	add_child(pause_button)
	slow_button.position = Vector2(228, 634)
	slow_button.custom_minimum_size = Vector2(240, 40)
	slow_button.pressed.connect(toggle_slow)
	add_child(slow_button)
	step_button.position = Vector2(484, 634)
	step_button.custom_minimum_size = Vector2(180, 40)
	step_button.text = "下一帧（→）"
	step_button.pressed.connect(step_frame)
	add_child(step_button)
	_label("固定根点 (16,64) · 同一逻辑尺寸 ×3 · 十字为根点，不是脚底接触点", Vector2(32, 694), 17)
	_label("研究稿 HD4 以 1/4 映射逻辑画布；无逐帧裁剪、居中、拟合或根点修正。", Vector2(32, 722), 17)
	ready_ok = load_frames()
	if not ready_ok:
		var error_label := _label("无法预览 / REVIEW UNAVAILABLE\n" + failure, Vector2(64, 280), 18)
		error_label.size = Vector2(880, 200)
		error_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		error_label.modulate = Color("ffb0a3")
	_update_controls()
	queue_redraw()

func _label(text: String, at: Vector2, font_size: int) -> Label:
	var label := Label.new()
	label.text = text
	label.position = at
	label.add_theme_font_size_override("font_size", font_size)
	add_child(label)
	return label

func load_frames() -> bool:
	ready_ok = false
	failure = ""
	# Commit both complete sets together. A failed frame never mixes versions or
	# silently falls back to an old candidate / gameplay atlas.
	source_frames.clear()
	research_frames.clear()
	var sources: Array[Texture2D] = []
	var candidates: Array[Texture2D] = []
	for index in IDS.size():
		var paths := [SOURCE_DIR + "source-%d.png" % IDS[index], RESEARCH_PATHS[index]]
		for side in 2:
			var path: String = paths[side]
			if not FileAccess.file_exists(path):
				failure = "缺少文件 / Missing: " + path
				return false
			var image := Image.load_from_file(path)
			var expected := Vector2i(128, 128) if side == 0 else Vector2i(512, 512)
			if image == null or image.is_empty() or image.get_size() != expected:
				failure = "图像无效或尺寸错误 / Invalid image or dimensions: " + path
				return false
			var texture := ImageTexture.create_from_image(image)
			if side == 0:
				sources.append(texture)
			else:
				candidates.append(texture)
	source_frames = sources
	research_frames = candidates
	ready_ok = true
	return true

func _physics_process(_delta: float) -> void:
	if not ready_ok or paused:
		return
	elapsed_ticks += 1
	if elapsed_ticks >= FRAME_TICKS * (SLOW_FACTOR if slow else 1):
		elapsed_ticks = 0
		frame_index = (frame_index + 1) % IDS.size()
		_update_controls()
		queue_redraw()

func toggle_pause() -> void:
	if not ready_ok:
		return
	paused = not paused
	_update_controls()

func toggle_slow() -> void:
	if not ready_ok:
		return
	slow = not slow
	elapsed_ticks = 0
	_update_controls()

func step_frame() -> void:
	if not ready_ok:
		return
	paused = true
	elapsed_ticks = 0
	frame_index = (frame_index + 1) % IDS.size()
	_update_controls()
	queue_redraw()

func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_SPACE: toggle_pause()
			KEY_S: toggle_slow()
			KEY_RIGHT: step_frame()

func _update_controls() -> void:
	for button in [pause_button, slow_button, step_button]:
		button.disabled = not ready_ok
		button.focus_mode = Control.FOCUS_NONE
	pause_button.text = "继续（空格）" if paused else "暂停（空格）"
	slow_button.text = "慢速 ×0.25（S）" if slow else "正常速度（S）"
	frame_label.text = "相位 %d / 6 · 源帧 %d · %d tick/帧 · %s" % [frame_index + 1, IDS[frame_index], FRAME_TICKS * (SLOW_FACTOR if slow else 1), "暂停" if paused else "播放"] if ready_ok else "整组六帧不可用；未显示部分序列，也未回退旧版。"

func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, Vector2(1024, 768)), Color("171e29"))
	for side in 2:
		var origin: Vector2 = PANEL_ORIGINS[side]
		draw_rect(Rect2(origin, PANEL_SIZE), Color("303b4b"))
		if not ready_ok:
			continue
		var texture: Texture2D = source_frames[frame_index] if side == 0 else research_frames[frame_index]
		draw_texture_rect(texture, Rect2(origin, PANEL_SIZE), false)
		var root := origin + LOGICAL_ROOT * DISPLAY_SCALE
		draw_line(root - Vector2(7, 0), root + Vector2(7, 0), Color("67d9cb"), 1.0)
		draw_line(root - Vector2(0, 7), root + Vector2(0, 7), Color("67d9cb"), 1.0)
