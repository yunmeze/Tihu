extends "res://scripts/earth/snapshot_prefilter_world.gd"
# Body-only leaf. No clock, collision, NPC service, sorting, or shadow changes.
const ZhangGuard=preload("res://scripts/earth/zhang_fourphase_guard.gd")
var zhang_guard=ZhangGuard.new()
var zhang_active=false
var prefer_zhang=true
func prepare_visuals()->void:
 super.prepare_visuals()
 zhang_guard.atlas_validator=snapshot_atlas_matches
 prepare_zhang()
func prepare_zhang(deny:PackedStringArray=[]) -> bool:
 zhang_guard.reload(deny)
 refresh_zhang()
 return zhang_active
func refresh_zhang()->void:
 zhang_active=initialized and zhang_guard.valid(map,packs,objects)
func refresh()->void:
 refresh_zhang()
 super.refresh()
func refresh_draw_qualifications()->void:
 refresh_zhang()
 super.refresh_draw_qualifications()
func uses_zhang(entry:Dictionary)->bool:
 return prefer_npcs and prefer_zhang and zhang_active and zhang_guard.owns(entry)
func _draw_frame(pack_name:String,index:int,origin:Vector2,use_offset:bool,top:float)->void:
 if prefer_npcs and prefer_zhang and zhang_active and use_offset and pack_name=="Npc" and index in [201,202,203,204] and origin==Vector2(1680,1088)+screen_origin():
  var body=zhang_guard.descriptor(index)
  draw_texture_rect_region(body.texture,Rect2(body.origin+screen_origin(),body.size),body.region)
  return
 super._draw_frame(pack_name,index,origin,use_offset,top)

func hit_test_npc(point:Vector2) -> int:
 refresh_zhang()
 refresh_xuyun()
 refresh_house()
 var entries=ordered_objects();entries.reverse()
 for entry in entries:
  if entry.kind==-1:continue
  var origin:Vector2=entry.origin+screen_origin()
  if uses_zhang(entry):
   var body=zhang_guard.descriptor(201+int(tick/17)%4)
   if alpha_hit(body.texture,point,Rect2(body.origin+screen_origin(),body.size),body.region):return body.npc_index
   continue
  if uses_xuyun(entry):
   var body=xuyun_guard.descriptor()
   if alpha_hit(body.texture,point,Rect2(body.origin+screen_origin(),body.size),body.region):return body.npc_index
   continue
  if uses_lingyunzi(entry) or uses_fangzhang(entry):
   var ling=uses_lingyunzi(entry)
   var tex=lingyunzi_texture if ling else fangzhang_texture
   var region=Rect2((int(tick/17)%4)*512,0,512,640) if ling else Rect2()
   if alpha_hit(tex,point,Rect2(origin+Vector2(-32,-104),Vector2(128,160)),region):return int(entry.order)-int(map.width)*int(map.height)
   continue
  if prefer_house and house_active:
   var house_id=house_guard.owner_id(entry)
   if house_id>0:
    if house_guard.owner_at(point-screen_origin())==house_id and alpha_hit(house_guard.texture,point,Rect2(Vector2(866,443)+screen_origin(),Vector2(512,512))):return -1
    continue
  var item=candidate_item(entry)
  if not item.is_empty():
   if not item.get("empty",false) and alpha_hit(item.texture,point,Rect2(item.origin+screen_origin(),item.size),item.get("region",Rect2())):return -1
   continue
  var index:int=entry.index
  if entry.kind==7:index+=int(tick/17)%4
  elif entry.kind==5:index+=int(tick/8)%5
  elif entry.kind==8:
   var phase=int(tick/8)%10;index=55+(phase if phase<5 else 9-phase)
  var pack:Dictionary=packs[entry.pack]
  var frame:Dictionary=pack.frames.get(str(index),{})
  if frame.is_empty():continue
  var top=0.0 if entry.kind==7 or entry.pack.begins_with("Mon/") else (-52.0 if entry.kind==8 else 32.0-float(frame.original[1]))
  origin+=Vector2(frame.crop[0],frame.crop[1]+top)
  if entry.kind==7 or entry.pack.begins_with("Mon/"):origin+=Vector2(frame.offset[0],frame.offset[1])
  var local=point-origin
  if local.x<0 or local.y<0 or local.x>=frame.rect[2] or local.y>=frame.rect[3]:continue
  var img=hit_image(textures[pack.pages[int(frame.page)].file])
  var color=img.get_pixel(int(frame.rect[0]+local.x),int(frame.rect[1]+local.y))
  if color.a<0.1:continue
  if entry.kind==7 and color.r8==16 and color.g8==8 and color.b8==8:continue
  return int(entry.order)-int(map.width)*int(map.height) if entry.kind==7 else -1
 return -1
