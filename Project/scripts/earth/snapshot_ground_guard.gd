extends "res://scripts/earth/first_map_guard.gd"
const SnapshotIdentity=preload("res://scripts/earth/snapshot_source_identity.gd")
func source_matches(source:Dictionary,original:Dictionary) -> bool:
	# Existing full floor stream +121 exact owner flags/atlas remain checked by parent.
	return SnapshotIdentity.compatible(source,original)

var atlas_validator:Callable=Callable()
func atlas_matches(runtime:Dictionary,original:Dictionary) -> bool:
	return atlas_validator.is_valid() and atlas_validator.call(runtime,original)
