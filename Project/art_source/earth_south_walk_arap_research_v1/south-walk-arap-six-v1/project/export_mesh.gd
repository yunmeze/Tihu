extends SceneTree
func _initialize() -> void:
 call_deferred("run")
func run() -> void:
 var file := FileAccess.open("res://mesh.json", FileAccess.READ)
 var frames: Array = JSON.parse_string(file.get_as_text())
 for frame in frames:
  var viewport := SubViewport.new()
  viewport.size = Vector2i(512,512)
  viewport.transparent_bg = true
  viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
  root.add_child(viewport)
  var polygon := Polygon2D.new()
  var points := PackedVector2Array()
  var uvs := PackedVector2Array()
  for p in frame.vertices:
   points.append(Vector2(p[0],p[1]))
  for p in frame.uv:
   uvs.append(Vector2(p[0],p[1]))
  polygon.polygon = points
  polygon.uv = uvs
  var triangles: Array[PackedInt32Array] = []
  for t in frame.triangles:
   triangles.append(PackedInt32Array(t))
  polygon.polygons = triangles
  polygon.texture = ImageTexture.create_from_image(Image.load_from_file(frame.texture))
  polygon.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
  viewport.add_child(polygon)
  await process_frame
  await RenderingServer.frame_post_draw
  await process_frame
  await RenderingServer.frame_post_draw
  var result := viewport.get_texture().get_image()
  var err := result.save_png(frame.output)
  print("MESH_EXPORT ", frame.phase, " ", frame.output, " err=",err," size=",result.get_size())
  viewport.queue_free()
  await process_frame
 print("MESH_PILOT_COMPLETE")
 quit()
