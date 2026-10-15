extends "res://scripts/world_view.gd"
var pass_kind:=0
var temple_enabled:=false
var temple_owners:Dictionary={}
func prepare_temple() -> bool:
	var path="res://assets/scifi/environment/a13_temple_v2/registration.json"
	var reg=read_json(path)
	if reg.is_empty() or not reg.get("owners") is Array:return false
	var staged={}
	for owner in reg.owners:
		var order=int(owner.stable_source_order)
		var cell:Vector2i=Vector2i(owner.cell[0],owner.cell[1])
		var original:Array=map.cells[cell.x*int(map.height)+cell.y]
		if original!=owner.source_cell or order!=cell.x*int(map.height)+cell.y:return false
		if staged.has(order):return false
		if owner.texture!=null:
			_load_texture(owner.texture)
			if not textures.has(owner.texture):return false
			if textures[owner.texture].get_size()!=Vector2(owner.raw_rect[2],owner.raw_rect[3]):return false
		staged[order]=owner
	if staged.size()!=30:return false
	temple_owners=staged
	return true
func draw_temple(owner:Dictionary,offset:Vector2) -> void:
	if owner.texture==null:return
	var tex:Texture2D=textures[owner.texture]
	draw_texture_rect(tex,Rect2(Vector2(owner.world_top_left[0],owner.world_top_left[1])+offset,tex.get_size()*float(owner.scale)),false)
func _draw() -> void:
	if not initialized:return
	var offset=screen_origin()
	if pass_kind==0:
		draw_rect(get_viewport_rect(),Color("20291f"))
		for f in floors:_draw_frame(f.pack,f.index,f.origin+offset,false,0)
		return
	var after:=false
	for entry in ordered_objects():
		if entry.kind==-1:
			after=true
			continue
		if (pass_kind==1 and after) or (pass_kind==2 and not after):continue
		if temple_enabled and entry.kind==4 and temple_owners.has(entry.order):
			draw_temple(temple_owners[entry.order],offset)
			continue
		var index:int=entry.index
		if entry.kind==7:index+=(tick/17)%4
		elif entry.kind==5:index+=(tick/8)%5
		elif entry.kind==8:
			var phase:int=(tick/8)%10
			index=55+(phase if phase<5 else 9-phase)
		var frame:Dictionary=packs[entry.pack].frames.get(str(index),{})
		if frame.is_empty():continue
		var top:=0.0 if entry.kind==7 else (-52.0 if entry.kind==8 else 32.0-float(frame.original[1]))
		_draw_frame(entry.pack,index,entry.origin+offset,entry.kind==7,top)
