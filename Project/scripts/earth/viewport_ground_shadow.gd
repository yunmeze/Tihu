extends "res://scripts/earth/max_ground_shadow.gd"
## Optional host coverage only. Inherit constructor, material, shader, descriptor
## identity checks, tint/opacity, max-alpha composition and receiver qualification.
## Coordinates remain logical CanvasItem coordinates, never physical raster pixels.
func _draw() -> void:
	if prepared:draw_rect(get_viewport_rect(),Color.WHITE)
