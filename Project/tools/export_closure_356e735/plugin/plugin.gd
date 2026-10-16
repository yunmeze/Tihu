@tool
extends EditorPlugin
var exporter
func _enter_tree():
 exporter=preload("res://addons/raw_allowlist/exporter.gd").new()
 add_export_plugin(exporter)
func _exit_tree():
 remove_export_plugin(exporter)
