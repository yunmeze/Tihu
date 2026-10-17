extends RefCounted
## New standalone implementation from pinned source; not a recovered tested binary.
## Pure data only. No Node, IO, resource loader, wall clock, map, AI or damage system.
## Public inputs stay Variant until strict type/range validation has succeeded.

enum State { INACTIVE = 0, IDLE = 1, WALK = 33, ATTACK = 81, HURT = 129, DEATH = 145 }
enum Entry { PURSUIT_WALK = 1, WANDER_WALK = 2, ATTACK = 3 }
enum MovementOutcome { UNCHANGED = 0, ARRIVED_IDLE = 1 }

const I32_MAX: int = 2147483647
const I32_MIN: int = -2147483648
const STATES: Array = [0, 1, 33, 81, 129, 145]
const SNAPSHOT_KEYS: Array = [
	"appearance", "direction", "state", "previous_state", "stored_frame",
	"clock", "phase", "pause_b4",
]


static func make_idle(appearance: Variant, direction: Variant, clock: Variant = 0) -> Dictionary:
	# clock=0, previous_state=0, pause_b4=0 are explicit API defaults.
	# Source anchors prove idle state/phase/frame, not an elapsed-seconds claim.
	var result: Dictionary = checked_snapshot({
		"appearance": appearance, "direction": direction, "state": State.IDLE,
		"previous_state": State.INACTIVE, "stored_frame": 1,
		"clock": clock, "phase": 1, "pause_b4": 0,
	})
	if result.ok:
		result.snapshot.stored_frame = 4 * direction + 1
	return result


static func checked_snapshot(value: Variant) -> Dictionary:
	var failure: Dictionary = _validate(value)
	if not failure.is_empty():
		return failure
	return _success(value.duplicate(true), [])


static func enter(value: Variant, kind: Variant, direction: Variant) -> Dictionary:
	var failure: Dictionary = _validate(value)
	if not failure.is_empty():
		return failure
	if not _integer(kind, 1, 3):
		return _error("unsupported" if typeof(kind) == TYPE_INT else "invalid_input", "unsupported_entry")
	if not _integer(direction, 0, 7):
		return _error("invalid_input", "direction_requires_integer_0_to_7")
	if value.state != State.IDLE:
		return _error("unsupported", "entry_requires_source_idle_context")
	var snapshot: Dictionary = value.duplicate(true)
	var events: Array = []
	snapshot.direction = direction
	match kind:
		Entry.PURSUIT_WALK:
			snapshot.state = State.WALK
			if snapshot.previous_state != State.WALK:
				snapshot.clock = -1
				snapshot.phase = 0
			# 0x5ca00b: no frame or previous_state write at this entry.
		Entry.WANDER_WALK:
			snapshot.state = State.WALK
			snapshot.clock = -1
			snapshot.phase = 1
			_write_frame(snapshot, events, 4 * direction + 1, State.IDLE, 1)
		Entry.ATTACK:
			snapshot.state = State.ATTACK
			snapshot.clock = -1
			snapshot.phase = 0
	return _success(snapshot, events)


static func step(value: Variant, hp: Variant, q: Variant,
		movement_outcome: Variant = MovementOutcome.UNCHANGED) -> Dictionary:
	var failure: Dictionary = _validate(value)
	if not failure.is_empty():
		return failure
	if not _integer(hp, I32_MIN, I32_MAX):
		return _error("invalid_input", "hp_requires_signed_32_bit_integer")
	if not _integer(q, 0, 1):
		return _error("unsupported" if typeof(q) == TYPE_INT else "invalid_input", "q_requires_source_integer_0_or_1")
	if not _integer(movement_outcome, 0, 1):
		return _error("unsupported" if typeof(movement_outcome) == TYPE_INT else "invalid_input", "unsupported_movement_outcome")
	var snapshot: Dictionary = value.duplicate(true)
	var events: Array = []
	if snapshot.state == State.INACTIVE:
		return _success(snapshot, events)
	if snapshot.clock == I32_MAX:
		return _error("unsupported", "source_clock_overflow_not_modeled")
	snapshot.clock += 1
	# Ordinary non-revival HP path precedes dispatch and the b4 gate.
	if hp <= 0 and snapshot.state != State.DEATH:
		snapshot.state = State.DEATH
		snapshot.clock = 0
		snapshot.phase = 0
		events.append({"type": "death_entered"})
	# 0x5c9936..0x5c9963: even the last positive b4 tick skips dispatch.
	if snapshot.pause_b4 > 0:
		if hp > 0:
			snapshot.pause_b4 -= 1
			events.append({"type": "dispatch_paused", "clock": snapshot.clock,
				"remaining_b4": snapshot.pause_b4})
			return _success(snapshot, events)
		snapshot.pause_b4 = 0
	var dispatch_state: int = snapshot.state
	var old_phase: int = snapshot.phase
	match dispatch_state:
		State.IDLE:
			if snapshot.clock % 12 == 0:
				snapshot.phase += 1
				if snapshot.phase >= 5:
					snapshot.phase = 1
			var native_frame: int = 4 * snapshot.direction + snapshot.phase
			# Phase0 off gate while facing N selects special record0.
			# Its registration is not a normal frame; do not reinterpret it.
			if native_frame == 0:
				return _error("unsupported", "idle_record_zero_boundary")
			_write_frame(snapshot, events, native_frame, dispatch_state, snapshot.phase)
		State.WALK:
			snapshot.previous_state = State.WALK
			if snapshot.clock % (1 + q) == 0:
				events.append({"type": "movement_due", "clock": snapshot.clock})
				if movement_outcome == MovementOutcome.ARRIVED_IDLE:
					snapshot.state = State.IDLE
			if snapshot.clock % (4 + q) == 0:
				if snapshot.phase >= 5:
					snapshot.phase = 0
				snapshot.phase += 1
				_write_frame(snapshot, events, 33 + 6 * snapshot.direction + snapshot.phase,
					dispatch_state, snapshot.phase)
		State.ATTACK:
			snapshot.previous_state = State.ATTACK
			if snapshot.clock % (4 + q) == 0:
				_write_frame(snapshot, events, 81 + 6 * snapshot.direction + old_phase,
					dispatch_state, old_phase)
				snapshot.phase += 1
				if old_phase == 4:
					events.append({"type": "main_strike_dispatch_due", "clock": snapshot.clock})
				if snapshot.phase >= 6:
					_finish_to_idle(snapshot)
					events.append({"type": "attack_completed"})
		State.HURT:
			if snapshot.clock % 5 == 0:
				_write_frame(snapshot, events, 129 + 2 * snapshot.direction + old_phase,
					dispatch_state, old_phase)
				snapshot.phase += 1
				if snapshot.phase >= 2:
					_finish_to_idle(snapshot)
					events.append({"type": "hurt_completed"})
		State.DEATH:
			if snapshot.clock % 4 == 0:
				_write_frame(snapshot, events, 145 + 9 * snapshot.direction + old_phase,
					dispatch_state, old_phase)
				snapshot.phase += 1
				if snapshot.phase >= 9:
					snapshot.phase = 8
					events.append({"type": "clear_occupancy", "slot_count": 2})
					events.append({"type": "publish_corpse", "appearance": snapshot.appearance,
						"direction": snapshot.direction, "native_frame": 153 + 9 * snapshot.direction})
	return _success(snapshot, events)


static func _validate(value: Variant) -> Dictionary:
	if typeof(value) != TYPE_DICTIONARY:
		return _error("invalid_input", "snapshot_requires_dictionary")
	if value.size() != SNAPSHOT_KEYS.size():
		return _error("invalid_input", "snapshot_keys_must_match_schema")
	for key: String in SNAPSHOT_KEYS:
		if not value.has(key):
			return _error("invalid_input", "snapshot_missing_" + key)
		if typeof(value[key]) != TYPE_INT:
			return _error("invalid_input", key + "_requires_integer")
	if value.appearance not in [5, 7]:
		return _error("unsupported", "unsupported_appearance")
	if not _integer(value.direction, 0, 7):
		return _error("invalid_input", "direction_requires_integer_0_to_7")
	if value.state not in STATES:
		return _error("unsupported", "unsupported_state")
	if value.previous_state not in STATES:
		return _error("unsupported", "unsupported_previous_state")
	if not _integer(value.stored_frame, 1, 216):
		return _error("invalid_input", "stored_frame_requires_integer_1_to_216")
	if not _integer(value.clock, -1, I32_MAX):
		return _error("unsupported", "clock_outside_supported_range")
	if not _integer(value.pause_b4, 0, 32767):
		return _error("invalid_input", "pause_b4_requires_integer_0_to_32767")
	var max_phase: int = 8
	match value.state:
		State.IDLE, State.WALK, State.ATTACK:
			max_phase = 5
		State.HURT:
			max_phase = 1
	if not _integer(value.phase, 0, max_phase):
		return _error("unsupported", "phase_outside_supported_state_range")
	return {}


static func _integer(value: Variant, lower: int, upper: int) -> bool:
	return typeof(value) == TYPE_INT and value >= lower and value <= upper


static func _finish_to_idle(snapshot: Dictionary) -> void:
	snapshot.state = State.IDLE
	snapshot.clock = -1
	snapshot.phase = 0


static func _write_frame(snapshot: Dictionary, events: Array,
		native_frame: int, dispatch_state: int, emitted_phase: int) -> void:
	snapshot.stored_frame = native_frame
	events.append({"type": "frame_written", "native_frame": native_frame,
		"dispatch_state": dispatch_state, "emitted_phase": emitted_phase, "clock": snapshot.clock})


static func _success(snapshot: Dictionary, events: Array) -> Dictionary:
	return {"ok": true, "status": "ok", "snapshot": snapshot, "events": events}


static func _error(status: String, code: String) -> Dictionary:
	return {"ok": false, "status": status, "code": code}
