extends "res://scripts/earth/south_walk_contact_world.gd"
## Independent single-tree diagnostic world. Unified hero/ground world stays unchanged.
const PilotCompositor=preload("res://scripts/earth/upright_51_70_compositor.gd")
const PilotGate=preload("res://scripts/earth/upright_51_70_gate.gd")
const PilotQualification=preload("res://scripts/earth/upright_51_70_qualification.gd")
var tree_gate=PilotGate.new()
var tree_qualification=PilotQualification.new()
var prefer_tree_pilot=false
var tree_ready=false
var tree_reason="not prepared"
var _tree_needs_prepare=true
func _init()->void:
 super()
 shadow_compositor.free();shadow_compositor=PilotCompositor.new()
 tree_gate.revoked.connect(_tree_revoked)
func _tree_revoked()->void:
 tree_ready=false;shadow_compositor.clear_tree()
func prepare_visuals()->void:
 tree_gate.reset();_tree_needs_prepare=true
 super.prepare_visuals()
func prepare_tree_pilot(deny:PackedStringArray=[])->bool:
 shadow_compositor.clear_tree();tree_ready=false
 if not tree_qualification.prepare():tree_reason=tree_qualification.error;return false
 tree_ready=tree_gate.prepare(tree_qualification.contract,self,deny)
 tree_reason=tree_gate.error;_tree_needs_prepare=false;return tree_ready
func refresh()->void:
 super.refresh()
 if not is_inside_tree():return
 if _tree_needs_prepare:prepare_tree_pilot()
 var enable=prefer_tree_pilot and prefer_shadow and tree_ready
 shadow_compositor.set_tree(enable,tree_gate,screen_origin(),self)
 tree_reason=tree_gate.error
