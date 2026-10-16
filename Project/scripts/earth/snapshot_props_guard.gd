extends "res://scripts/earth/static_props_guard.gd"
const SnapshotIdentity=preload("res://scripts/earth/snapshot_source_identity.gd")
func source_matches(source:Dictionary,original:Dictionary,_group:Dictionary) -> bool:
	# Parent identity_failure retains group cell quadruples and unique actual-owner closure.
	return SnapshotIdentity.compatible(source,original)

var atlas_validator:Callable=Callable()
func atlas_matches(runtime:Dictionary,original:Dictionary) -> bool:
	return atlas_validator.is_valid() and atlas_validator.call(runtime,original)
