extends "res://scripts/world_view.gd"
const SAMPLE_RECT=Rect2(2496,960,768,512)
var follow_actor:=false
func screen_origin() -> Vector2:
	return get_viewport_rect().size*.5-movement.position*Vector2(48,32) if follow_actor else -SAMPLE_RECT.position
