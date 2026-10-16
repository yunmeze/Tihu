extends SceneTree
var BASE := OS.get_environment("ARAP_WORK_ROOT")
var all_textures: Array = []
var sprites: Array[Sprite2D] = []
var labels: Array[Label] = []
func _initialize() -> void:
 Engine.physics_ticks_per_second = 50
 call_deferred("run")
func run() -> void:
 root.size = Vector2i(768, 464)
 root.content_scale_size = Vector2i(768, 464)
 root.content_scale_mode = Window.CONTENT_SCALE_MODE_DISABLED
 var bg := ColorRect.new()
 bg.color = Color(0.32,0.34,0.37)
 bg.size = Vector2(768,464)
 root.add_child(bg)
 for kind in range(3):
  var bank: Array[Texture2D] = []
  for phase in range(57,63):
   var path: String
   if kind == 0:
    path = BASE + "south-walk-mesh-correction-v1/raw/source-%d.png" % phase
   elif kind == 1:
    path = BASE + "south-walk-mesh-correction-v1/baseline/%d-s0.72.png" % phase
   else:
    path = BASE + "south-walk-arap-six-v1/output/mesh-%d.png" % phase
   bank.append(ImageTexture.create_from_image(Image.load_from_file(path)))
  all_textures.append(bank)
 for row in range(2):
  var density := float(row + 1)
  for kind in range(3):
   var label := Label.new()
   label.position = Vector2(kind*256+4, 4 if row==0 else 176)
   root.add_child(label)
   labels.append(label)
   var sprite := Sprite2D.new()
   sprite.centered = false
   sprite.position = Vector2(kind*256,28 if row==0 else 200)
   sprite.scale = Vector2.ONE * density * (1.0 if kind==0 else 0.25)
   sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST if kind==0 else CanvasItem.TEXTURE_FILTER_LINEAR
   root.add_child(sprite)
   sprites.append(sprite)
 var events: Array = []
 var start := Time.get_ticks_usec()
 for tick in range(210):
  if tick % 7 == 0:
   var phase_index: int = int(tick / 7) % 6
   for index in range(sprites.size()):
    var kind := index % 3
    sprites[index].texture = all_textures[kind][phase_index]
    labels[index].text = ["SOURCE", "COMMON BASE", "ARAP"][kind] + " %d | %dx" % [57+phase_index,1+index/3]
   events.append({"physics_tick":tick,"phase":57+phase_index,"wall_elapsed_us":Time.get_ticks_usec()-start})
  await physics_frame
 var file := FileAccess.open(BASE+"south-walk-arap-six-v1/NATIVE_PREVIEW_TIMING.json",FileAccess.WRITE)
 file.store_string(JSON.stringify({"actual_window_size":str(root.size),"actual_viewport_rect":str(root.get_visible_rect()),"content_scale_mode":root.content_scale_mode,"sprite_target_sizes":["128x128 logical pixels at1x","256x256 logical pixels at2x"],"physics_hz":50,"ticks_per_phase":7,"loop_ticks":42,"loops":5,"events":events,"scope":"standalone preview only; not main game runtime or renderer-wall-time guarantee"},"  "))
 await RenderingServer.frame_post_draw
 root.get_texture().get_image().save_png(BASE+"south-walk-arap-six-v1/NATIVE_PREVIEW_1X_2X.png")
 print("SIX_PHASE_NATIVE_PREVIEW_COMPLETE")
 if "--hold" in OS.get_cmdline_user_args():
  print("HOLD_OBSERVATION_ONLY: additional 15 loops; recorded five-loop evidence unchanged")
  for hold_tick in range(630):
   if hold_tick % 7 == 0:
    var phase_index: int = int(hold_tick / 7) % 6
    for index in range(sprites.size()):
     var kind := index % 3
     sprites[index].texture = all_textures[kind][phase_index]
     labels[index].text = ["SOURCE", "COMMON BASE", "ARAP"][kind] + " %d | %dx HOLD" % [57+phase_index,1+index/3]
   await physics_frame
 quit()
