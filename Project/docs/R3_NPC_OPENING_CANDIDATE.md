# R3 bounded NPC opening candidate

## Entry and verified scope

Run `res://scenes/opening_candidate.tscn` explicitly. Default `game.tscn` stays R1.
This is a diagnostic starting fixture: A13 (61,39), ET0=1, STOP=true. It is **not a complete new-game loader**.

The two original scripts are read unchanged from A13 NPC records 0/1. Actual mouse interaction verified:
- STOP refuses ground movement but accepts NPC dialogue.
- Early Lingyun A1 shows 慈悲, closes, keeps ET1.
- Abbot A1→A5 changes ET1→2; original text and button labels shown.
- Lingyun B1→B6 changes ET2→3, UNSTOP and original TOMAP to A00 (138,12).
- Dialogue closes on transfer; actual subsequent mouse movement is enabled.

`diagnostics/r3/01..15*.png` and `native.log` record this newly executed chain. All displayed pages were visually inspected. The longest B3 fits in three lines.

## Atomic boundary

The pure VM produces a detached state and events. The bridge validates all event kinds before any commit, builds a separate target WorldView and Movement, loads every target atlas, and validates target map ID and original walkable coordinate. Only then does it exchange state, STOP and world. Missing resource, invalid coordinate, unknown event, or stale button revision preserves old flags, actor/world, dialogue and revision. No target map path comes from saved or user input.

`tests/test_opening_candidate.gd` executes the real two-script chain plus these failure cases and confirms the nine original A00 barrier flags remain blocked. Existing movement, R1 scene, and R2 portal tests were rerun successfully. `test.log` has `R3_OPENING_CANDIDATE_ATOMIC_CHAIN_PASS`.

## Explicit exclusions

Neither A13 nor A00 loadScript is executed in this fixture. The VM rejects their unsupported fields/events (including rnd, 通关次数, and SETMAPFLAG); the bridge does not claim them as successful executions. The banner repeats this scope before and after transfer. Hidden-NPC policies, random chicken/spawn, inventory, saving, combat, full new-game initialization and automatic house portals in this entry are not implemented. R2 remains the separate house-portal diagnostic.

Only A13 two-NPC interaction is enabled, within five cells. Click hit-testing uses current frame alpha and reverse original draw order; original NPC checker pixels do not own interaction. This is a bounded modern adapter, not proof of original EXE mouse semantics. Hero occlusion of click targets is not yet handled.

## UI and platform

Original dialog texture is copied byte-for-byte from `参考项目/public/assets/ui/native/dialog.png` (523×216). Position and text/button controls are an adaptation; source button coordinates currently map to a 16px grid, not claimed as proven native coordinate units. Source U+E810 indentation renders as spaces. System Noto Sans CJK SC is used without packaging the reference font; Windows font availability and rendering are untested.

No original EXE was run. Initial import without isolated XDG logged editor-settings errors; it is retained as `import-first-no-xdg.log`. Subsequent isolated-XDG import, headless tests and actual native runtime have zero ERROR/SCRIPT ERROR. Vsync warning is cloud display-driver only.
