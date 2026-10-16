extends "res://scripts/earth/plant_reuse_guard.gd"
const SnapshotIdentity=preload("res://scripts/earth/snapshot_source_identity.gd")
var atlas_validator:Callable=Callable()
func source_matches(source:Dictionary,original:Dictionary) -> bool:
	# Parent still verifies SHA, every selected cell/owner, and complete stream where applicable.
	return SnapshotIdentity.compatible(source,original)
func atlas_matches(runtime:Dictionary,original:Dictionary) -> bool:
	return atlas_validator.is_valid() and atlas_validator.call(runtime,original)
