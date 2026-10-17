# Pure-data API

Load src/a01_animation_core.gd explicitly; no class_name registration or scene is needed. All public parameters are Variant to prevent implicit typed-parameter coercion before validation. Accepted numeric values must have typeof(value)==TYPE_INT. Floats (including 1.0), bools, NaN, INF, nulls and numeric strings are not accepted as integers. The core does not parse JSON or cast numbers. A JSON adapter must validate its own lexical/numeric input instead of truncating JSON floats.

Every call returns either {ok:true,status:"ok",snapshot:Dictionary,events:Array} or {ok:false,status:"invalid_input"|"unsupported",code:String}. Successful snapshots are independent copies. No input dictionary is mutated. Failure returns no partial state or events. Unknown state codes are explicitly unsupported, never treated as idle. Error status/code form a documented API boundary; no engine exception is intended for malformed inputs.

## Snapshot

Exactly these eight keys, all integer values:

- appearance: 5 or 7; other appearances unsupported
- direction: 0=N,1=NE,2=E,3=SE,4=S,5=SW,6=W,7=NW
- state and previous_state: supported source enum 0,1,33,81,129,145
- stored_frame: native resource index1..216, not a zero-based clip index
- clock: -1..2147483647; stepping active clock at the upper limit is unsupported
- phase: 0..5 for idle/walk/attack, 0..1 for hurt, 0..8 for death/inactive
- pause_b4: 0..32767, a supported nonnegative subset of the original signed WORD

This is a bounded animation-slice snapshot, not proof every accepted combination can arise in full original AI. previous_state is only written by walk/attack dispatch here, as established by the contract. Stored frame is intentionally not forced to agree with current state/phase. Idle phase5 is allowed because walk arrival can leave it behind. Negative original clocks below-1, negative b4 values, unsupported states, other appearances and out-of-range phases are outside this implementation.

## Methods

make_idle(appearance,direction,clock=0)

Creates state1,phase1,frame4*direction+1,previous_state0,pause_b40. Clock0 and previous_state0 are API initialization defaults, not a newly claimed original initialization/timing proof. The caller may explicitly choose clock-1..INT32_MAX.

checked_snapshot(snapshot)

Validates and copies an explicit snapshot. Use it to represent a proven external hurt/death entry without inventing an entry routine. In particular, hurt state129,clock0,phase0 emits at clocks5 and10 only if subsequent calls reach dispatch.

enter(snapshot,entry,direction)

entry is an integer enum: 1=PURSUIT_WALK,2=WANDER_WALK,3=ATTACK. Only source idle context state1 is supported. This operation represents the already-selected source entry site; it does not run AI or add another tick. Do not automatically call step before enter as though that simulated all original idle/AI ordering.

- Pursuit sets state33/direction. When previous_state!=33, reset clock=-1,phase=0. When previous_state==33, preserve both. Always hold stored_frame.
- Wander sets state33,clock=-1,phase=1 and immediately writes idle-tail frame4*d+1. Its next uninterrupted clock0 walk gate emits phase2.
- Attack sets state81,clock=-1,phase=0 and holds stored_frame.

step(snapshot,hp,q,movement_outcome=0)

hp is signed32-bit integer. It is an observed value, not damage calculation. q is the effective post-status-prelude integer0/1; status counters, side effects and q derivation are outside this core. q affects walk/attack frame period4+q and walk movement period1+q.

movement_outcome: integer enum0=UNCHANGED or1=ARRIVED_IDLE, an externally established result of the movement call. Applied only when a walk movement gate is actually reached; ignored on other paths. No pathfinding, coordinate changes, occupancy changes or world callback occurs. A movement result can set state1 before the same call still executes walk-frame logic.

Ordering:

1. State0 returns unchanged without incrementing clock or consuming b4.
2. Active clock increments once. Other original prelude early returns are outside this slice; caller must know it reached the supported path.
3. Ordinary non-revival hp<=0 and state!=145 enters death with clock0/phase0.
4. Positive b4 with hp>0 decrements b4 and skips this dispatch, including when decremented to0. Clock remains incremented; phase/frame/previous_state hold. hp<=0 clears positive b4 and continues.
5. Dispatch original state-specific gates. This models eligible update calls, never seconds or an assumed original Hz.

## Frame rules

- Idle: at clock%12==0 increment phase; phase>=5 becomes1. Write4*d+phase on every reached ordinary tail.
- Walk: at clock%(4+q)==0 reset old phase>=5 to0, increment, write33+6*d+new_phase. Emitted cycle is1..5, never a six-frame loop.
- Attack: at clock%(4+q)==0 write81+6*d+old_phase then increment. Old phase4 emits main_strike_dispatch_due; this is an opportunity event, not damage. Old phase5 completes into idle,clock=-1,phase0 and keeps its final frame.
- Hurt: at clock%5==0 write129+2*d+old_phase then increment. Second sample completes into idle,clock=-1,phase0, retaining its last frame.
- Death: at clock%4==0 write145+9*d+old_phase then increment. At9 clamp phase8 and emit clear_occupancy then publish_corpse. State remains145, frame153+9*d remains visible.

Repeated death updates continue clock advancement and, on subsequent4tick gates, emit the terminal frame and terminal events again. The source path does not establish a one-shot latch. A future consumer may need idempotent world handling, but this core neither adds a latch nor deletes a corpse.

## Events

- frame_written: native_frame, dispatch_state, emitted_phase, clock. A write is emitted even if the numeric frame is unchanged. dispatch_state records the branch that wrote it and can differ from final snapshot.state.
- movement_due: clock. Observational request only; the supplied outcome is applied by the core.
- main_strike_dispatch_due: clock. No hit, damage, target or special attack effect is produced.
- attack_completed / hurt_completed: animation completion only. Cooldown restoration/aggro bookkeeping and optional combat side effects are external.
- death_entered: ordinary animation transition occurred.
- dispatch_paused: clock, remaining_b4.
- clear_occupancy: slot_count2. No entity/cell IDs are guessed and no memory/grid is written.
- publish_corpse: appearance, direction, native_frame153+9*d. No lifetime or cleanup policy is assigned.

## Explicit unsupported boundaries

Source clock signed32-bit overflow is not emulated. A north-facing idle phase0 off its phase gate computes native record0; that record has special registration rather than normal frame1 registration. step returns unsupported/idle_record_zero_boundary instead of changing the frame or silently shifting indices. Other directions retain the exact proven idle formula even at transient phases. Unsupported errors are atomic relative to the supplied snapshot; callers must retain/diagnose the original snapshot rather than treat an error as an elapsed source tick.

The supplemental b4 evidence proves this narrow gate and ordering, not every status-system interaction. The current implementation does not infer revival, appearance888, source tick rate, complete combat, all hurt entry sites or corpse cleanup.
