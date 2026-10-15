# Four-map load-script evaluator — 2026-10-15

## Scope

This extends the pure `scripts/core/dialogue_vm.gd` checkpoint to evaluate the actual extracted `loadScript` text of A13, A00, A01, and A02. It does not modify the runtime, apply map edits, spawn monsters, run the original executable, or claim an integrated map-entry/quest restoration. The earlier kernel checkpoint's unsupported-load statements describe its earlier version; the supported subset below supersedes them.

Verification on Godot 4.6.3: **614 existing regression checks, 0 failures; 6667 new checks, 0 failures; 890 actual four-map load-script executions**. The old suite retains its 614 checks; assertions for newly supported map events and missing-context errors are updated to the extended contract. Tests remain ignored local files under `Project/tests/`. Run both with `bash Project/tests/run_dialogue_vm.sh`.

## Compatible API extension

```gdscript
var state: Dictionary = DialogueVM.initial_state()
state.et[0] = 1
state.level = 1
state.clear_count = 0
state.game_mode = 0
# This is an explicit test draw, not a production random-number generator.
var candidate: Dictionary = DialogueVM.execute(
    actual_map.loadScript, state, "START", 2048,
    {"map_load": true, "rnd_values": [4]}
)
```

The existing first four arguments and dialogue result fields remain compatible. The optional fifth `context` is a Dictionary with only:

- `map_load`: bool, default false. True supplies the map-entry implicit NOTUI behavior documented by the original authoring help.
- `rnd_values`: Array of **already resolved integer RND results, 0 through 100**. No floats, strings, booleans, nulls, or automatic numeric conversion. At most 65536 samples. Omit it when no active condition reads RND. Missing samples or an exhausted sequence fail the whole transaction.

New output fields:

- `silent`: bool, true for valid global NOTUI metadata or `context.map_load == true`.
- `random_consumed`: number of RND samples actually read by active conditions during a successful transaction. Inactive nested branches do not read samples. GOTO shares the transaction's cursor. Every failed result returns 0 and clears silent/other staged outputs, even if evaluation already read samples.

Input context and state are never mutated. A caller must reserve samples without committing its external cursor, then advance by `random_consumed` only when it commits **all** candidate state and events. On failure retain the same state/cursor; do not reroll or replace a draw simply to avoid an unsupported spawn. This kernel owns no PRNG, seed, global randomness, HP, or unrelated gameplay data.

## Explicit read-only scalar state

Script field names map to these state keys:

| Script field | Required state key on active read | Valid gameplay-state range |
| --- | --- | --- |
| LEVEL, case-insensitive | level | integer 1..130 |
| 通关次数 | clear_count | integer 0..32767 |
| 游戏模式 | game_mode | integer 0..2: 普通/专家/地狱 |

`initial_state()` still only creates ET/BT banks. It does not invent a level, clear count, or mode. Missing scalar keys fail only when an active condition needs them; present but invalid reserved scalar values fail state validation. These fields and RND are read-only: CHANGE still only mutates ET/BT. Other names, including HP, remain unsupported. The ranges validate normal gameplay state; they are not claims that native field queries clamp corrupt values to these ranges.

Evidence: reference `src/progression.js:3,17` and original level-cap comparison at VA `0x61f7c7` (130); level query signed WORD at `0x6072aa`, offset `0x1ff0`; clear-count query signed WORD at `0x60748d`, offset `0x1ff8`, with ending increment at `0x62e418`; mode query at `0x606e80..0x606f35` maps the three original mode strings. Reference `src/ending.js:2,16`, `src/character.js:26`, and `src/npc-fields.js:7,30` corroborate the bounded gameplay representation.

## New candidate events

- `#MOVE x y` → `{kind: "move", x, y}` for local-map relocation. No implicit TOMAP is invented.
- `#DELNPC x y` → `{kind: "delnpc", x, y}`. The adapter must account for both NPC rows and matching monster units/spawns. A02's original `(35,35)` target is the 甲虫王 spawn, despite its empty NPC array.
- `#SETMAPFLAG x y [flag]` → `{kind: "setmapflag", x, y, flag}`. Omitted flag defaults to 0 per the reference. Only 0, 1, 2 are valid.
- `#ADDMON x y name` → `{kind: "addmon", x, y, name}`. The nonempty name is retained; this kernel does not know a monster registry. A runtime **must** resolve a registered monster and preflight its resources/capacity before applying the event. Receiving a 彩蛋鸡 event does not mean a chicken was spawned.

Coordinates are strict decimal integers 0..32767, checked before integer conversion. Actual map bounds, passability, resources, actor ownership, and spawn capacity are adapter concerns. Invalid active commands roll back every candidate output; inactive nonstructural commands remain skipped. Structural syntax and global metadata are still validated regardless of reachability.

### Map flags and visible pillars: application boundary

Original help `Help/Mod_4_6.htm:1274` defines flag 0 as clear, 1 as an invisible blocker, and 2 as a visible pillar. Reference `src/npc-world.js:17–35` validates map bounds/flag values before application:

- Flag 0 clears collision. If the cell's object kind is 8, clear its kind and object index too. Do not remove other object kinds.
- Flag 1/2 only changes a cell whose existing collision flag is 0. Both store collision -1; flag 2 additionally installs kind 8/index 1.
- Reference application first applies staged player effects, then flags, then remaining world effects. Its pure evaluator only records flag instructions. The new kernel likewise does not edit a map or its visuals.

Static original evidence agrees with the clear operation's internal order: VA `0x606287` clears the flag, `0x6062c7` tests object kind 8, and `0x6062cc` / `0x6062e9` clear kind/index. A consuming adapter must preflight the whole transaction and publish state, collision, visuals, actor changes, and random cursor together. Do not commit ET progress first and later fail while rebuilding pillars or spawning a monster.

## Original four-map results and tested boundaries

All tests execute `Project/data/maps/<id>.json`'s actual `loadScript`; they do not replace it with hard-coded map results.

- **A13:** strict RND<5 proposes 彩蛋鸡 at `(49,53)`; ET0=1 proposes STOP; ET0=28 proposes MOVE `(61,39)` then STOP; 2<ET0<28 proposes DELNPC `(62,36)`; ET9=1 removes `(78,23)` and emits all eight listed aura-gate flag changes. Each of level<79, clear_count=0, and game_mode=0 independently proposes DELNPC `(61,70)`; duplicate events are intentionally preserved. The matrix spans ET0 0/1/2/3/27/28/29, ET9 0/1, level 78/79, clear count 0/1, all three modes, and RND 0/1/4/5/100: 840 transactions.
- **A00:** ET0<3 is first staged to 3. Only resulting ET0>3 opens the nine north-gate cells; ET0>5 opens six additional south-gate cells. clear_count=0 and ET7>0 each independently remove `(94,60)`. The matrix covers 42 transactions with both sides of every condition. ET0=1 becomes 3 and opens **none** of the nine cells.
- **A01:** comment, END, then NotUI. No world events; silent is true. Four BT-state cases.
- **A02:** BT0>0 proposes DELNPC `(35,35)`; then END and NotUI. BT0 -1/0/1/32767 cover both branches. Four cases.

The exact nine north-gate cells are `(37,55), (37,56), (38,56), (38,57), (39,57), (39,58), (40,58), (40,59), (41,59)`. The additional six are `(114,96), (114,97), (113,97), (113,98), (112,98), (112,99)`. All 15 original A00 cells remain flag -1/kind 8/index 1 in pure tests. Visual pillar removal belongs to the successful adapter commit at the original condition's timing.

## NOTUI is global metadata, not an action after END

Original authoring help `Help/Mod_4_6.htm:1305–1307` states that NOTUI anywhere suppresses the whole script's dialogue window, and map-load scripts implicitly include it. Reference `src/npc-dialogue.js:45` scans all source lines before execution, while its line 57 still terminates active execution at END.

The parser recognizes standalone zero-argument `#NOTUI` anywhere, including after END or in another process, removes it from executable instructions, and records silent metadata. It does **not** execute CHANGE, STOP, ADDMON, or other actions after an active END. Comments containing `#NotUI`, ordinary text mentioning it, and names such as `#NOTUIX` are not metadata. Extra arguments or mixed directives such as `#NOTUI #END` fail, including in unreachable code. NOTUI metadata does not prevent terminal-END structural compatibility.

## RND: documented discrepancy, no invented bit-exact claim

Three sources disagree:

1. Original authoring help `Help/Mod_4_6.htm:406–408` describes 1..100.
2. Reference `src/npc-fields.js:29` uses `min(100, floor(random()*100)+1)`.
3. Static original code uses a random result multiplied by 100, then the VB integer-conversion helper, with **no +1**. For a raw sample 0.04, the native conversion gives 4 and the reference formula gives 5, changing A13's strict `<5` branch.

Read-only disassembly of `原版游戏/LP传奇单机版_重生.exe`, SHA-256 `21dc753d3aa828fb29dc171e595857be234833edc43a1d80833540ae7e355b84`:

```text
VA        Raw bytes                Operation
6082e6    ff 15 ac 10 40 00         call [4010ac]       ; random import ordinal 593
6082ec    d8 0d 60 15 40 00         fmul dword [401560]
6082f2    ff 15 20 12 40 00         call [401220]       ; __vbaFpI2
6082f8    0f bf d0                  movsx edx, ax
6082fe    89 55 e8                  mov [ebp-18h], edx
608b0a    8b 45 e8                  mov eax, [ebp-18h]  ; unchanged query result
401560    00 00 c8 42              IEEE-754 float 100.0
```

This checkpoint therefore accepts explicit resolved native-query integer draws 0..100 and applies the original integer comparison. Injected 4 passes RND<5; 5 fails. It does not implement the VB PRNG, seed evolution, floating-point sampling precision, integer-helper tie behavior, or actual draw distribution. Banker’s rounding and bit-exact sampling parity are **not** certified. The original executable was inspected as bytes only, never run.

## Source provenance and remaining boundaries

Original A13/A00 source hashes are recorded in `DIALOGUE_VM_KERNEL_STAGE.md`. Additional originals:

- A01.lpMap: SHA-256 `6e38d97077f363e77079a6845460a57c791402ddc54d675c8c6cdb6a4ad9369d`, 180891 bytes.
- A02.lpMap: SHA-256 `5c09201febc7b072874c23d611e0d2080993fb340a1f3f429a8b9ead2eb35798`, 181290 bytes.

Independent source inspection decoded the four original load strings and matched the extracted Project data. Tests also cover missing/invalid context, exhausted RNG, inactive reads, late-failure rollback after draws, read-only/absent/malformed scalar state, huge numeric arguments, event arity, flag values, and global NOTUI cases. Existing unknown commands remain errors when active. Inventory/rewards, combat, map-world application, PRNG integration, and save/load integration are outside this checkpoint.
