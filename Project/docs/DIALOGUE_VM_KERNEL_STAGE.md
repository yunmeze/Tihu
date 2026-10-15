# Dialogue VM kernel checkpoint — 2026-10-15

## Scope and status

`Project/scripts/core/dialogue_vm.gd` is a **pure, bounded transaction evaluator**, implemented afresh for the recovered Godot project. It is a preparatory R2 checkpoint, not a restored game story, map loader, or playable quest. It has no scene tree, file, GUI, world, inventory, combat, random-number, or save access. This stage does not modify the runtime or GUI.

Fresh Godot 4.6.3 headless tests exercise the extracted original A13 方丈 / 凌云子 scripts, including their actual text, buttons, conditional starts, and first ET0 progression from 1 to 2 to 3. Old VM test reports are not evidence for this implementation. Original executables were not run.

## Critical integration boundary: prepare first, commit together

**A successful evaluation returns candidate state, dialogue, and events. It does not authorize a partial runtime commit.** A consuming adapter must:

1. Evaluate against the current authoritative state without mutating that state.
2. Validate every candidate event. For `tomap`, verify the map is registered, the coordinate is inside that actual map, and the necessary map/assets/entry semantics can be prepared. Syntactically valid map names and coordinates in this kernel do not prove these facts.
3. Prepare the complete transition without externally observable changes. If a required map-load script is unsupported, stop and report that blocker; do not silently skip it.
4. Commit candidate state and all world changes together, or leave both unchanged. In particular, do not commit ET0=3 or UNSTOP before knowing the A00 transition can succeed.
5. Present the candidate dialogue only as appropriate to the completed transaction.

`STOP`, `UNSTOP`, and `TOMAP` are ordered **candidate events**, not already-applied side effects. A runtime adapter must separately establish its atomicity and error behavior. This kernel alone does not establish runtime atomicity or UI correctness.

## Public API

```gdscript
const DialogueVM = preload("res://scripts/core/dialogue_vm.gd")

var state: Dictionary = DialogueVM.initial_state()
state.et[0] = 1 # Explicit caller decision for a new-game opening, not a VM default.
var candidate: Dictionary = DialogueVM.execute(npc_script, state, "START")
# On failure, state remains untouched. On success, candidate.state is detached.
# Validate/prepare candidate.events before any runtime state/world commit.
```

`execute(source, input_state, process = "START", step_budget = 2048)` accepts Variants at the boundary so malformed caller values produce structured errors rather than implicit type conversions. `source` and `process` must be Strings; the budget must be an integer from 1 through 65536. Script, process, and field keywords are case-insensitive. Process and map identifiers use ASCII `[A-Za-z_][A-Za-z0-9_]*`, at most 64 characters.

`initial_state()` returns two independent, fixed-size Arrays:

- `et`: 30 integer values, initialized to 0
- `bt`: 30 integer values, initialized to -1

No opening quest value is inferred. Both banks are mandatory on execution and every element must be an actual integer from -32768 through 32767. Strings, floating-point numbers (including 1.0), booleans, nulls, packed arrays, and truncated banks are rejected. A future save adapter must explicitly validate/normalize its transport representation; this evaluator never silently converts saved values.

Additional state fields are preserved via deep copy. State must be bounded, acyclic JSON-style data: null, booleans, integers, finite floats, Strings, Arrays, and Dictionaries. Dictionary keys may be String or StringName, since GDScript dot assignment creates StringName keys. Objects, Resources, other engine types, cycles, nonfinite floats, and excessive depth/data size are rejected before copying.

A successful result contains:

```text
ok: true
state: detached Dictionary, including staged ET/BT changes
page: final uppercase process name (after any GOTO)
text: ordered Array[String]
buttons: Array[{label, x, y, color, target}]
events: ordered Array[Dictionary]
closed: bool
steps: executed/scanned instruction count
error: null
```

A failed result contains `ok: false`, `state: null`, empty `text`, `buttons`, and `events`, `closed: false`, and `error: {code, message, line, process}`. Line numbers are one-based source lines; preflight errors without a line use 0. `page` and `steps` provide diagnostic location/budget information. No staged state, text, choice, close action, or world event escapes a failure. The caller's input is never modified, even on success.

The adapter follows a returned button by evaluating the same NPC script with `button.target` against its current authoritative state. The kernel is stateless and does not itself verify that a UI click came from a currently displayed choice. The reserved target `OVER` returns `closed: true` and `[{kind: "close"}]`, retaining detached unchanged state. `OVER` is not a legal `SUB` name or `GOTO` destination.

## Supported language

- `#SUB name`: named process. A script without SUB has implicit START. Preamble lines and the first explicit `#SUB Start` merge into the same START process, matching the reference parser. Repeated explicit process declarations, including case-only duplicates, fail rather than silently merge.
- `#IF field operator integer`, `#ELSE`, `#ENDIF`: nested branches. Operators: `=`, `==`, `!=`, `<>`, `<`, `>`, `<=`, `>=`. Conditions read the staged state, so earlier CHANGE operations are visible.
- `ET0` through `ET29`, `BT0` through `BT29`; bare `ET` / `BT` alias element 0. Decimal leading zeros are accepted and safely normalized. Negative, fractional, malformed, or out-of-range indices fail.
- `#CHANGE field = integer`, `+ integer`, or `- integer`: staged assignment/addition/subtraction. Literal bounds are signed 32-bit; the resulting flag must remain signed 16-bit. Numeric syntax and bounds are checked as strings **before** `to_int()`, including extremely long indices and literals.
- `#GOTO process`: transfer to another process in the same script, preserve staged outputs/state, and reset that process's conditional stack. No dynamic expression evaluation, functions, external scripts, or command execution.
- `#BUTTON label x y color target`: a nonempty label (spaces supported), signed 16-bit UI coordinates, a nonempty opaque color token, and one existing process or OVER. Targets are normalized to uppercase. Inline command targets are outside this subset.
- Non-command lines: dialogue text. CRLF, LF, and CR are normalized; blank lines and lines beginning `//` are ignored. Original private-use spacing glyphs U+E000–U+F8FF are removed, matching the reference's readable-text treatment.
- `#STOP`, `#UNSTOP`: zero-argument events `{kind: "stop"}` / `{kind: "unstop"}`.
- `#TOMAP map x y`: `{kind: "tomap", map: "A00", x: 138, y: 12}` for the opening transition. Coordinates must be nonnegative decimal integers up to 32767. The adapter, not this pure kernel, validates map existence, dimensions, assets, and entry behavior.

### END is not ENDIF

A zero-argument `#END` terminates execution only when active. An early END in an inactive branch is ignored without closing its IF or truncating subsequent lines. The structural parser always validates IF/ELSE/ENDIF pairing, duplicate ELSE, SUB declarations, and END arity, even in inactive or unvisited code and after an earlier active END.

For bounded source compatibility, a process whose **last nonblank/noncomment instruction is standalone `#END`** may finish with open IF frames. This exception applies at the process boundary only. An earlier END never substitutes for ENDIF; open IF frames followed by more instructions and no terminal END are rejected. Extra ENDIF remains an error. Malformed IF expressions and malformed ET/BT indices in IF are rejected even inside inactive code.

## Explicit unsupported boundary

Unknown commands and unsupported fields fail when active. Unsupported commands/fields in inactive branches are not executed. All structural validation still applies. `GAMEOVER`, inventory/item checks and grants, monetary fields, random values, character stats, combat, spawn/NPC mutation, map flags, services, and all commands not listed above are unimplemented. There is no default value for unsupported `rnd`, `level`, `通关次数`, etc.

Consequences verified with actual source:

- A13 loadScript fails at its active `rnd` condition; it is **not** a supported map-entry transaction.
- A00 loadScript also fails. At ET0=1 it stages ET0=3 then fails at unsupported `通关次数`, discarding that change. Other states can first encounter unsupported SETMAPFLAG.
- A00 海曦村长 text-only A1–A4 can be evaluated, but A5 fails at the unsupported money change; no reward or quest advancement is committed.
- 方丈's later ToGM process fails at unsupported GAMEOVER and discards the preceding candidate UNSTOP. This checkpoint does not implement the ending.

## Fresh verification

Local tests live under ignored `Project/tests/`, consistent with the production-only repository policy. They are new tests for this implementation and read `Project/data/maps/A13.json` and `A00.json` directly, rather than retyping source scripts as substitutes. The test runner uses isolated writable HOME/XDG directories under ignored `Project/.tmp/`; it does not open the editor or GUI.

```sh
bash Project/tests/run_dialogue_vm.sh
```

On 2026-10-15, the fresh run and independent review rerun both passed: **614 checks, 0 failures, 23 original A13 process executions** on Godot 4.6.3. The runner performs a GDScript parse check, runs the headless suite, rejects script/engine errors, and requires a zero-failure summary. Coverage includes all first-two-NPC processes (including explicit failure of ToGM), every actual opening button transition and label, exact source dialogue text, ET1→2→3, all 60 flag slots, condition operators, nested and inactive branches, terminal END compatibility, case-insensitive targets, detached nested metadata, staged visibility, missing targets, invalid state/type/range/arity, huge indices/numbers, output rollback after late failure, and bounded loops.

Resource limits: source 262144 characters; at most 8192 lines, 4096 characters per line, 256 processes; state depth 32, 16384 nodes, and 262144 total key/String characters; execution defaults to 2048 instructions, with caller budgets capped at 65536. Inactive instructions count toward the execution budget; blank/comment/SUB lines do not. Separate button selections are separate bounded transactions.

## Evidence and provenance

- `Project/data/maps/A13.json`, extracted from original `原版游戏/Data/Map/A13.lpMap`, source SHA-256 `e1cc7189fc96e04312b935422ec511a078b1fbe6259b97b9e3c279732becb3e3` (90394 bytes).
- `Project/data/maps/A00.json`, extracted from original `原版游戏/Data/Map/A00.lpMap`, source SHA-256 `906f33edb6d0c7181629ba37296829a6b8adaf9cde2637ffc4c2530e2c5c352f` (188772 bytes).
- `参考项目/src/npc-dialogue.js`: implementation reference for process selection, text cleanup, staged evaluation, commands, and script flow. Its permissive structural behavior is not copied wholesale.
- `参考项目/src/npc-fields.js`: implementation reference for ET/BT aliases, 30-slot banks, ET/BT defaults, and signed 16-bit changes. This is not a claim of newly proven executable parity.

Neither the original game nor the reference project is changed by this stage. Linux headless verification does not establish Windows behavior, an integrated natural-play quest, or recovery of a historical save.
