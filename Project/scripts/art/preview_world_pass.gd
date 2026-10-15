extends "res://scripts/world_view.gd"
var pass_kind:=0
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
