extends "res://scripts/earth/upright_51_70_world.gd"
## Bounded artwork-only branch; source order, NPC hit path and all shadows inherit.
const WallGuard=preload("res://scripts/earth/wall_2653_2660_guard.gd")
var wall_guard=WallGuard.new()
var prefer_wall=true
var wall_active=false
var wall_draw_commands=0
var wall_fallback_frames=0
var _wall_in_draw=false
var _wall_draw_entries:Array=[]
var _wall_offset=Vector2.ZERO

func setup(actor:RefCounted,map_path:String="res://data/maps/A13.json")->bool:
 wall_guard.reset();wall_active=false
 return super.setup(actor,map_path)

func prepare_visuals()->void:
 wall_guard.reset();wall_active=false
 super.prepare_visuals()
 prepare_wall()

func prepare_wall(path:String=WallGuard.REGISTRATION)->bool:
 wall_active=false
 var ok=wall_guard.prepare(path,map,packs)
 queue_redraw()
 return ok

func ordered_objects()->Array:
 # The exact validated parent result is the stream consumed by this draw.
 # Outside drawing (including NPC hit tests), keep the unmodified parent route.
 if _wall_in_draw:return _wall_draw_entries
 return super.ordered_objects()

func _draw()->void:
 wall_draw_commands=0;wall_fallback_frames=0;wall_active=false
 _wall_in_draw=false;_wall_draw_entries=[]
 if initialized and prefer_wall:
  var actual_ordered=super.ordered_objects()
  wall_active=wall_guard.validate(map,packs,objects,actual_ordered)
  if wall_active:
   _wall_draw_entries=actual_ordered
   _wall_offset=screen_origin()
   _wall_in_draw=true
 # Parent early_source -> _source_entry -> virtual _draw_frame remains intact.
 # A rejected group simply renders every original frame through the parent.
 super._draw()
 _wall_in_draw=false;_wall_draw_entries=[]

func _draw_frame(pack_name:String,index:int,origin:Vector2,use_offset:bool,top:float)->void:
 if wall_active and _wall_in_draw:
  var item=wall_guard.draw_item(pack_name,index,origin,use_offset,top,_wall_offset)
  if not item.is_empty():
   var destination=Rect2(item.position+_wall_offset,item.size)
   if destination.intersects(get_viewport_rect()):
    # WHITE does not enter the existing special house-owner shader color route.
    draw_texture_rect(item.texture,destination,false,Color.WHITE)
    wall_draw_commands+=1
   return
 if pack_name==WallGuard.PACK and index>=2653 and index<=2660:wall_fallback_frames+=1
 super._draw_frame(pack_name,index,origin,use_offset,top)

func _exit_tree()->void:
 wall_guard.reset();wall_active=false
 super._exit_tree()
