extends Node2D
## Preserve the complete source floor stream; only validated owners use the union.
var world
func _draw() -> void:
	world.validate_review_ground_stream()
	draw_rect(get_viewport_rect(),Color("20291f"))
	var offset=world.screen_origin()
	for f in world.floors:
		var order=roundi(f.origin.x/48)*100+roundi(f.origin.y/32)
		if world.prefer_ground and world.review_ground_owners.has(order):
			var item=world.review_ground_owners[order]
			draw_texture_rect_region(world.review_ground_texture,Rect2(item.origin+offset,Vector2(96,64)),item.region,Color.WHITE,false,false)
		else:
			var pack=world.packs[f.pack];var frame=pack.frames[str(f.index)];var r=frame.rect
			draw_texture_rect_region(world.textures[pack.pages[int(frame.page)].file],Rect2(f.origin+offset+Vector2(frame.crop[0],frame.crop[1]),Vector2(r[2],r[3])),Rect2(r[0],r[1],r[2],r[3]))
