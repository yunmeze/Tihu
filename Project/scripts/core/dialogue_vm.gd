extends RefCounted
## Bounded, pure dialogue kernel. No scene, file, inventory, or world access.
## A successful result owns a detached state; a failure exposes no staged output.

const FLAG_COUNT := 30
const FLAG_MIN := -32768
const FLAG_MAX := 32767
const DEFAULT_STEP_BUDGET := 2048
const MAX_STEP_BUDGET := 65536
const MAX_SOURCE_LENGTH := 262144
const MAX_LINES := 8192
const MAX_LINE_LENGTH := 4096
const MAX_PROCESSES := 256
const MAX_STATE_NODES := 16384
const MAX_STATE_DEPTH := 32
const MAX_STATE_TEXT_LENGTH := 262144


static func initial_state() -> Dictionary:
	# Starting a new game (including setting ET0 to 1) belongs to the caller.
	var et: Array = []
	var bt: Array = []
	et.resize(FLAG_COUNT)
	bt.resize(FLAG_COUNT)
	et.fill(0)
	bt.fill(-1)
	return {"et": et, "bt": bt}


static func execute(source: Variant, input_state: Variant, process: Variant = "START", step_budget: Variant = DEFAULT_STEP_BUDGET, context: Variant = {}) -> Dictionary:
	if typeof(source) != TYPE_STRING:
		return _failure("invalid_source", "Source must be a String.")
	if typeof(process) != TYPE_STRING or not _is_name(process):
		return _failure("invalid_process", "Process must be an ASCII identifier.")
	if typeof(step_budget) != TYPE_INT or step_budget < 1 or step_budget > MAX_STEP_BUDGET:
		return _failure("invalid_budget", "Step budget must be an integer from 1 to %s." % MAX_STEP_BUDGET)
	var context_error := _validate_context(context)
	if not context_error.is_empty():
		return _failure("invalid_context", context_error)
	var state_error := _validate_state(input_state)
	if not state_error.is_empty():
		return _failure("invalid_state", state_error)
	var parsed := _compile(source)
	if not parsed.ok:
		return parsed
	var sections: Dictionary = parsed.sections
	var page: String = process.to_upper()
	var result := {"ok": true, "state": input_state.duplicate(true), "page": page,
		"text": [], "buttons": [], "events": [], "closed": false, "steps": 0, "error": null,
		"silent": parsed.silent or context.get("map_load", false), "random_consumed": 0}
	# OVER is the source scripts' reserved close-button target, not a process.
	if page == "OVER":
		result.closed = true
		result.events.append({"kind": "close"})
		return result
	if not sections.has(page):
		return _failure("missing_process", "Unknown process: %s" % page, 0, page)
	var pc := 0
	var stack: Array = []
	var active := true
	while true:
		var lines: Array = sections[page]
		if pc >= lines.size():
			return result
		var node: Dictionary = lines[pc]
		if result.steps >= step_budget:
			return _failure("step_budget", "Execution step budget exhausted.", node.line, page, result.steps)
		result.steps += 1
		pc += 1
		var command: String = node.command
		if command == "IF":
			var matched := false
			if active:
				if not node.condition.field.ok:
					return _failure("unsupported_field", node.condition.field.message, node.line, page, result.steps)
				var read := _read_field(node.condition.field, result, context)
				if not read.ok:
					return _failure(read.code, read.message, node.line, page, result.steps)
				matched = _compare(read.value, node.condition.operator, node.condition.value)
			stack.append({"parent": active, "matched": matched})
			active = active and matched
			continue
		if command == "ELSE":
			active = stack[-1].parent and not stack[-1].matched
			continue
		if command == "ENDIF":
			active = stack.pop_back().parent
			continue
		if not active:
			continue
		if command == "TEXT":
			result.text.append(node.args)
			continue
		if command == "END":
			return result
		if command == "GOTO":
			var target: String = node.args.to_upper()
			if not _is_name(node.args) or target == "OVER" or not sections.has(target):
				return _failure("invalid_goto", "GOTO needs one existing process name.", node.line, page, result.steps)
			page = target
			result.page = page
			pc = 0
			stack.clear()
			active = true
			continue
		if command == "CHANGE":
			var change := _expression(node.args, true)
			if not change.ok:
				return _failure("invalid_change", change.message, node.line, page, result.steps)
			if not change.field.ok:
				return _failure("unsupported_field", change.field.message, node.line, page, result.steps)
			if change.field.kind != "flag":
				return _failure("readonly_field", "Only ET/BT fields can be changed by this kernel.", node.line, page, result.steps)
			var old_value: int = result.state[change.field.bank][change.field.index]
			var new_value: int = change.value
			if change.operator == "+":
				new_value = old_value + change.value
			elif change.operator == "-":
				new_value = old_value - change.value
			if new_value < FLAG_MIN or new_value > FLAG_MAX:
				return _failure("flag_range", "CHANGE result is outside signed 16-bit range.", node.line, page, result.steps)
			result.state[change.field.bank][change.field.index] = new_value
			continue
		if command == "BUTTON":
			var button := _button(node.args, sections)
			if not button.ok:
				return _failure("invalid_button", button.message, node.line, page, result.steps)
			result.buttons.append(button.button)
			continue
		if command in ["STOP", "UNSTOP"]:
			if not node.args.is_empty():
				return _failure("invalid_event", "%s takes no arguments." % command, node.line, page, result.steps)
			result.events.append({"kind": command.to_lower()})
			continue
		if command == "TOMAP":
			var move := _tomap(node.args)
			if not move.ok:
				return _failure("invalid_tomap", move.message, node.line, page, result.steps)
			result.events.append(move.event)
			continue
		if command in ["MOVE", "DELNPC", "SETMAPFLAG", "ADDMON"]:
			var event := _map_event(command, node.args)
			if not event.ok:
				return _failure("invalid_map_event", event.message, node.line, page, result.steps)
			result.events.append(event.event)
			continue
		return _failure("unsupported_command", "Unsupported active command: #%s" % command, node.line, page, result.steps)
	return result


static func _compile(source: String) -> Dictionary:
	if source.length() > MAX_SOURCE_LENGTH:
		return _failure("source_limit", "Source is too large.")
	var raw_lines := source.replace("\r\n", "\n").replace("\r", "\n").split("\n")
	if raw_lines.size() > MAX_LINES:
		return _failure("source_limit", "Source has too many lines.")
	var sections := {"START": []}
	var declared := {}
	var silent := false
	var current := "START"
	var line_number := 0
	for raw: String in raw_lines:
		line_number += 1
		if raw.length() > MAX_LINE_LENGTH:
			return _failure("source_limit", "Source line is too long.", line_number, current)
		var line := _clean(raw)
		if line.is_empty() or line.begins_with("//"):
			continue
		var command := "TEXT"
		var args := line
		if line.begins_with("#"):
			var match_result := RegEx.create_from_string("^#(\\S+)(?:[ \\t]+(.*))?$").search(line)
			if match_result == null:
				return _failure("invalid_command", "Malformed command token.", line_number, current)
			command = match_result.get_string(1).to_upper()
			args = match_result.get_string(2).strip_edges()
		if command == "NOTUI":
			if not args.is_empty():
				return _failure("invalid_notui", "NOTUI metadata takes no arguments.", line_number, current)
			silent = true
			continue
		if command == "SUB":
			if not _is_name(args) or args.to_upper() == "OVER":
				return _failure("invalid_sub", "SUB needs one non-reserved process name.", line_number, current)
			current = args.to_upper()
			if declared.has(current):
				return _failure("duplicate_process", "Duplicate process: %s" % current, line_number, current)
			declared[current] = true
			if not sections.has(current):
				if sections.size() >= MAX_PROCESSES:
					return _failure("source_limit", "Source has too many processes.", line_number, current)
				sections[current] = []
			continue
		sections[current].append({"command": command, "args": args, "line": line_number})
	# Structural validation is unconditional, including inactive and unvisited code.
	# END is never ENDIF. Only a last standalone END can finish open IF frames.
	for page: String in sections:
		var stack: Array = []
		var nodes: Array = sections[page]
		for i in nodes.size():
			var node: Dictionary = nodes[i]
			match node.command:
				"IF":
					var expression := _expression(node.args, false)
					if not expression.ok:
						return _failure("invalid_if", expression.message, node.line, page)
					node.condition = expression
					stack.append({"line": node.line, "else_seen": false})
				"ELSE":
					if not node.args.is_empty() or stack.is_empty() or stack[-1].else_seen:
						return _failure("invalid_else", "ELSE must occur once in an IF and take no arguments.", node.line, page)
					stack[-1].else_seen = true
				"ENDIF":
					if not node.args.is_empty() or stack.is_empty():
						return _failure("invalid_endif", "ENDIF must match IF and take no arguments.", node.line, page)
					stack.pop_back()
				"END":
					if not node.args.is_empty():
						return _failure("invalid_end", "END takes no arguments.", node.line, page)
		if not stack.is_empty() and (nodes.is_empty() or nodes[-1].command != "END"):
			return _failure("unclosed_if", "IF needs ENDIF or a terminal standalone END.", stack[-1].line, page)
	return {"ok": true, "sections": sections, "silent": silent}


static func _expression(args: String, change: bool) -> Dictionary:
	var pattern := "^([^\\s=+\\-]+)\\s*([=+\\-])\\s*(-?[0-9]+)$" if change else "^([^\\s<>=!]+)\\s*(>=|<=|<>|!=|==|=|>|<)\\s*(-?[0-9]+)$"
	var found := RegEx.create_from_string(pattern).search(args)
	if found == null:
		return {"ok": false, "message": "Expected a field, supported operator, and decimal integer."}
	var number := _integer(found.get_string(3), -2147483648, 2147483647)
	if not number.ok:
		return {"ok": false, "message": "Numeric literal is not a signed 32-bit integer."}
	var field := _field(found.get_string(1))
	# A malformed ET/BT index is invalid data even in an inactive IF.
	if field.has("invalid"):
		return {"ok": false, "message": field.message}
	return {"ok": true, "field": field, "operator": found.get_string(2), "value": number.value}


static func _field(name: String) -> Dictionary:
	var key := name.to_lower()
	if key == "rnd":
		return {"ok": true, "kind": "random"}
	var scalars := {"level": "level", "通关次数": "clear_count", "游戏模式": "game_mode"}
	if scalars.has(key):
		return {"ok": true, "kind": "scalar", "key": scalars[key]}
	if not key.begins_with("et") and not key.begins_with("bt"):
		return {"ok": false, "message": "Unsupported field: %s" % name}
	var suffix := key.substr(2)
	var index := {"ok": true, "value": 0} if suffix.is_empty() else _integer(suffix, 0, FLAG_COUNT - 1, false)
	if not index.ok:
		return {"ok": false, "invalid": true, "message": "ET/BT index must be decimal 0 through 29."}
	return {"ok": true, "kind": "flag", "bank": key.substr(0, 2), "index": index.value}


static func _read_field(field: Dictionary, result: Dictionary, context: Dictionary) -> Dictionary:
	if field.kind == "flag":
		return {"ok": true, "value": result.state[field.bank][field.index]}
	if field.kind == "scalar":
		if not result.state.has(field.key):
			return {"ok": false, "code": "missing_state_field", "message": "Active condition requires explicit state field: %s" % field.key}
		return {"ok": true, "value": result.state[field.key]}
	if not context.has("rnd_values"):
		return {"ok": false, "code": "missing_context", "message": "RND requires context.rnd_values; no global random source is used."}
	if result.random_consumed >= context.rnd_values.size():
		return {"ok": false, "code": "random_exhausted", "message": "RND sample sequence exhausted."}
	var sample: int = context.rnd_values[result.random_consumed]
	result.random_consumed += 1
	# Inject resolved native integer draws. The native query rounds Rnd * 100;
	# the web reference instead uses floor(sample * 100) + 1. Do not conflate them.
	return {"ok": true, "value": sample}


static func _validate_context(context: Variant) -> String:
	if typeof(context) != TYPE_DICTIONARY:
		return "Context must be a Dictionary."
	for key: Variant in context:
		if typeof(key) not in [TYPE_STRING, TYPE_STRING_NAME] or key not in ["rnd_values", "map_load"]:
			return "Unknown context key; supported keys are rnd_values and map_load."
	if context.has("map_load") and typeof(context.map_load) != TYPE_BOOL:
		return "Context map_load must be a bool."
	if context.has("rnd_values"):
		if typeof(context.rnd_values) != TYPE_ARRAY or context.rnd_values.size() > MAX_STEP_BUDGET:
			return "Context rnd_values must be an Array of at most 65536 samples."
		for sample: Variant in context.rnd_values:
			if typeof(sample) != TYPE_INT or sample < 0 or sample > 100:
				return "RND samples must be resolved integers from 0 through 100; no floating-point conversion or random generation is performed."
	return ""


static func _map_event(command: String, args: String) -> Dictionary:
	var pattern := "^([0-9]+)\\s+([0-9]+)$"
	if command == "SETMAPFLAG":
		pattern = "^([0-9]+)\\s+([0-9]+)(?:\\s+([0-9]+))?$"
	elif command == "ADDMON":
		pattern = "^([0-9]+)\\s+([0-9]+)\\s+(.+)$"
	var found := RegEx.create_from_string(pattern).search(args)
	if found == null:
		return {"ok": false, "message": "Malformed %s arguments." % command}
	var x := _integer(found.get_string(1), 0, FLAG_MAX, false)
	var y := _integer(found.get_string(2), 0, FLAG_MAX, false)
	if not x.ok or not y.ok:
		return {"ok": false, "message": "Map-event coordinates must be decimal integers from 0 through 32767."}
	var event := {"kind": command.to_lower(), "x": x.value, "y": y.value}
	if command == "SETMAPFLAG":
		var token := found.get_string(3)
		var flag := {"ok": true, "value": 0} if token.is_empty() else _integer(token, 0, 2, false)
		if not flag.ok:
			return {"ok": false, "message": "SETMAPFLAG flag must be 0 (clear), 1 (block), or 2 (visible pillar)."}
		event.flag = flag.value
	elif command == "ADDMON":
		var name := found.get_string(3).strip_edges()
		if name.is_empty() or name.length() > 128:
			return {"ok": false, "message": "ADDMON needs a monster name of 1 through 128 characters."}
		event.name = name
	return {"ok": true, "event": event}


static func _button(args: String, sections: Dictionary) -> Dictionary:
	var found := RegEx.create_from_string("^(.+?)\\s+(-?[0-9]+)\\s+(-?[0-9]+)\\s+(\\S+)\\s+(\\S+)$").search(args)
	if found == null:
		return {"ok": false, "message": "BUTTON needs label, x, y, color, and target."}
	var x := _integer(found.get_string(2), FLAG_MIN, FLAG_MAX)
	var y := _integer(found.get_string(3), FLAG_MIN, FLAG_MAX)
	var target := found.get_string(5).to_upper()
	if not x.ok or not y.ok or not _is_name(target) or (target != "OVER" and not sections.has(target)):
		return {"ok": false, "message": "BUTTON has invalid coordinates or an unknown target."}
	var label := found.get_string(1).strip_edges()
	if label.is_empty():
		return {"ok": false, "message": "BUTTON label must not be empty."}
	return {"ok": true, "button": {"label": label, "x": x.value, "y": y.value, "color": found.get_string(4), "target": target}}


static func _tomap(args: String) -> Dictionary:
	var found := RegEx.create_from_string("^(\\S+)\\s+([0-9]+)\\s+([0-9]+)$").search(args)
	if found == null or not _is_name(found.get_string(1)):
		return {"ok": false, "message": "TOMAP needs a map identifier and two nonnegative integers."}
	var x := _integer(found.get_string(2), 0, FLAG_MAX, false)
	var y := _integer(found.get_string(3), 0, FLAG_MAX, false)
	if not x.ok or not y.ok:
		return {"ok": false, "message": "TOMAP coordinates must be from 0 through 32767."}
	return {"ok": true, "event": {"kind": "tomap", "map": found.get_string(1).to_upper(), "x": x.value, "y": y.value}}


static func _integer(token: String, minimum: int, maximum: int, signed: bool = true) -> Dictionary:
	# Validate and range-check the string BEFORE to_int: Godot may overflow on
	# enormous decimal strings. Leading zeros are legal and normalized here.
	var pattern := "^-?[0-9]+$" if signed else "^[0-9]+$"
	if RegEx.create_from_string(pattern).search(token) == null:
		return {"ok": false}
	var negative := token.begins_with("-")
	var digits := token.substr(1) if negative else token
	var first := 0
	while first < digits.length() - 1 and digits.unicode_at(first) == 48:
		first += 1
	digits = digits.substr(first)
	var limit := str(-minimum if negative else maximum)
	if (negative and minimum >= 0) or digits.length() > limit.length() or (digits.length() == limit.length() and digits > limit):
		return {"ok": false}
	var value := digits.to_int()
	if negative:
		value = -value
	if value < minimum or value > maximum:
		return {"ok": false}
	return {"ok": true, "value": value}


static func _validate_state(state: Variant) -> String:
	if typeof(state) != TYPE_DICTIONARY:
		return "State must be a Dictionary."
	if not _json_data(state, 0, [0, 0]):
		return "State must be bounded, acyclic JSON-style data with String/StringName keys."
	for bank: String in ["et", "bt"]:
		if not state.has(bank) or typeof(state[bank]) != TYPE_ARRAY or state[bank].size() != FLAG_COUNT:
			return "State needs et and bt Arrays of exactly 30 integers."
		for value: Variant in state[bank]:
			if typeof(value) != TYPE_INT or value < FLAG_MIN or value > FLAG_MAX:
				return "ET/BT values must be signed 16-bit integers (not strings, floats, or booleans)."
	for key: String in ["level", "clear_count", "game_mode"]:
		if state.has(key):
			var minimum := 1 if key == "level" else 0
			var maximum: int = {"level": 130, "clear_count": 32767, "game_mode": 2}[key]
			if typeof(state[key]) != TYPE_INT or state[key] < minimum or state[key] > maximum:
				return "%s must be an explicit integer from %s through %s." % [key, minimum, maximum]
	return ""


static func _json_data(value: Variant, depth: int, count: Array) -> bool:
	count[0] += 1
	if count[0] > MAX_STATE_NODES or depth > MAX_STATE_DEPTH:
		return false
	match typeof(value):
		TYPE_NIL, TYPE_BOOL, TYPE_INT:
			return true
		TYPE_FLOAT:
			return is_finite(value)
		TYPE_STRING:
			count[1] += value.length()
			return count[1] <= MAX_STATE_TEXT_LENGTH
		TYPE_ARRAY:
			for child: Variant in value:
				if not _json_data(child, depth + 1, count):
					return false
			return true
		TYPE_DICTIONARY:
			for key: Variant in value:
				if typeof(key) not in [TYPE_STRING, TYPE_STRING_NAME]:
					return false
				count[1] += String(key).length()
				if count[1] > MAX_STATE_TEXT_LENGTH or not _json_data(value[key], depth + 1, count):
					return false
			return true
	return false


static func _compare(left: int, operator: String, right: int) -> bool:
	match operator:
		"=", "==": return left == right
		"!=", "<>": return left != right
		">": return left > right
		"<": return left < right
		">=": return left >= right
		"<=": return left <= right
	return false


static func _is_name(value: String) -> bool:
	return value.length() <= 64 and RegEx.create_from_string("^[A-Za-z_][A-Za-z0-9_]*$").search(value) != null


static func _clean(value: String) -> String:
	# Original dialogue embeds private-use spacing glyphs; keep readable wording.
	var cleaned := ""
	for character in value:
		var code: int = character.unicode_at(0)
		if code < 0xe000 or code > 0xf8ff:
			cleaned += character
	return cleaned.strip_edges()


static func _failure(code: String, message: String, line: int = 0, page: String = "", steps: int = 0) -> Dictionary:
	return {"ok": false, "state": null, "page": page, "text": [], "buttons": [], "events": [],
		"closed": false, "silent": false, "random_consumed": 0, "steps": steps,
		"error": {"code": code, "message": message, "line": line, "process": page}}
