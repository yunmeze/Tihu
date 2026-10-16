extends Node2D
## Preserve the complete source floor stream; only validated owners use the union.
var world
var candidate_enabled=false
var candidate={}
var candidate_guard=preload("res://scripts/earth/ground_candidate_guard.gd").new()
var last_counts={}
func prepare_candidate()->bool:
 candidate={};material=null;candidate=candidate_guard.prepare(world);queue_redraw();return not candidate.is_empty()
func set_candidate_enabled(value:bool)->void:
 candidate_enabled=value;material=candidate.get("material") if value and not candidate.is_empty() else null;queue_redraw()
func _draw() -> void:
 if candidate_enabled and not candidate.is_empty():
  if world.floors!=candidate.floors or world.map.cells!=candidate.cells:candidate={};material=null
  else:
   _draw_candidate();return
 material=null
 world.validate_review_ground_stream()
 draw_rect(get_viewport_rect(),Color("20291f"))
 var offset=world.screen_origin()
 var visible_rect=get_viewport_rect().grow(1.0)
 for f in world.floors:
  var order=roundi(f.origin.x/48)*100+roundi(f.origin.y/32)
  if world.prefer_ground and world.review_ground_owners.has(order):
   var item=world.review_ground_owners[order]
   var destination=Rect2(item.origin+offset,Vector2(96,64))
   if destination.intersects(visible_rect):
    draw_texture_rect_region(world.review_ground_texture,destination,item.region,Color.WHITE,false,false)
  elif world.east_ground_count()>0 and world.east_ground_group.owners.has(order):
   var item=world.east_ground_group.owners[order]
   var destination=Rect2(item.origin+offset,Vector2(96,64))
   if destination.intersects(visible_rect):
    draw_texture_rect_region(world.east_ground_group.texture,destination,item.region,Color.WHITE,false,false)
  else:
   var pack=world.packs[f.pack];var frame=pack.frames[str(f.index)];var r=frame.rect
   var destination=Rect2(f.origin+offset+Vector2(frame.crop[0],frame.crop[1]),Vector2(r[2],r[3]))
   if destination.intersects(visible_rect):
    draw_texture_rect_region(world.textures[pack.pages[int(frame.page)].file],destination,Rect2(r[0],r[1],r[2],r[3]))

func _draw_candidate()->void:
 material=candidate.material
 var offset=world.screen_origin();candidate.material.set_shader_parameter("camera_origin",-offset)
 draw_rect(get_viewport_rect(),Color("20291f"));var visible=get_viewport_rect().grow(1.0)
 var counts={"C":0,"grass":0,"current":0,"source":0,"overlay":0}
 for entry in candidate.streams:
  var row=entry.row;var f=world.floors[int(row.floor_stream_index)];var kind=entry.kind
  var dest=Rect2(f.origin+offset,Vector2(96,64))
  if kind=="source":
   var pack=world.packs[f.pack];var frame=pack.frames[str(f.index)];var r=frame.rect
   dest=Rect2(f.origin+offset+Vector2(frame.crop[0],frame.crop[1]),Vector2(r[2],r[3]))
   if dest.intersects(visible):draw_texture_rect_region(world.textures[pack.pages[int(frame.page)].file],dest,Rect2(r[0],r[1],r[2],r[3]));counts.source+=1
  elif dest.intersects(visible):
   counts[kind]+=1
   if kind=="C":
    draw_rect(dest,Color(16.0/255.0,0,0,1))
    if candidate.overlays.has(row.key):draw_texture_rect(candidate.textures[candidate.overlays[row.key]],dest,false);counts.overlay+=1
   elif kind=="grass":draw_texture_rect_region(candidate.grass,dest,Rect2(posmod(int(f.origin.x)*2,768)+768,posmod(int(f.origin.y)*2,768)+768,192,128),Color.WHITE,false,false)
   else:
    var r=row.region;draw_texture_rect_region(candidate.union if row.current_union else candidate.grass,dest,Rect2(r[0],r[1],r[2],r[3]),Color.WHITE,false,false)
 last_counts=counts
