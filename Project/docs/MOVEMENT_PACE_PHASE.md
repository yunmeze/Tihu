# Walk/run phase continuity

This is a reference-adapter consistency correction, not independently established original EXE timing. Original EXE was not executed. Reference `参考项目/src/animation.js` sets hero walk6 phases/.84s and run6/.6s at50Hz (7/5ticks per phase). Its `setAction` resets action clocks. The preservation rule is specifically `参考项目/src/hero-movement.js:setMovementAction`, lines30–33, which carries normalized elapsed phase only when the old action is moving.

Production `scripts/core/movement.gd` now carries one moving cycle as210 units. A walk update adds5, a run update adds7; each phase spans35 units. Walk↔run changes keep units modulo210, without multiplying/dividing the stored units or rounding fractional tick values. Idle entry/exit still resets0. The public `animation_tick` remains readable/writable in current-action tick units; whole and fractional external assignments remain supported. Tick increments operate on internal units directly. At current bounded clocks, integer units are exact in binary64, so repeated switches cannot drift below a frame boundary. No epsilon is used. Arbitrary external fractional clock writes are represented as floating units, as supplied, not claimed arbitrary-precision rationals.

Before update, E walk21→run gives run15/frame96; reverse gives walk21/frame48. An actual step then adds exactly one tick of the new action, as before. Initial movement still draws after incrementing its reset clock to1. Natural arrival still resets idle clock0 on that same update. Explicit stop, waypoint facing, A* path, position budget, speed and visuals are unchanged. Pure turning and same-speed retargeting keep their existing clocks.

## Compatibility and verification
Production search found only art_preview's explicit stop+clock0 write outside movement; inventory/save schemas do not persist this animation clock. Existing diagnostics assigning action then integer animation_tick remain supported. Public action direct assignment is not a transition API: callers invoking an action change with continuity must use `_set_action` or normal `step`/`stop`.

`tests/test_movement_phase.gd`:288983 checks, including42 starting ticks×1000 no-update roundtrips with every intermediate frame checked,100000 alternating pace updates against exact integer-unit oracle, fractional public assignments, source integer-frame equivalence across8directions/3actions/200ticks, same-pace retargeting, stop/start and natural arrival. R1 movement and R6 natural opening transaction tests also pass. Diagnostic East sequence tool487 checks remain passing; full new six-frame clip remains unavailable because four frames are missing.

## Hash binding scope
Only receiver_v2 manifest directly bound movement.gd. Its movement input SHA is faithfully updated, then its pinned gate SHA and left_upright manifest receiver-chain SHA and gate SHA. World, compositor, shader, body, mask, other gates and other manifests are unchanged. No sampling or permission is expanded. Source resource package receipts that record old releases remain historical rather than rewriting their evidence.

Logs and explicit stage hashes: `/workspace/shared/movement-phase-stage/`. No new GUI evidence is claimed for this headless timing correction.
