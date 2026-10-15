# Pure compatibility RND provider

`Project/scripts/core/compat_rng.gd` supplies the existing dialogue VM with resolved integer RND queries. It is an explicitly chosen compatibility generator for the playable reconstruction. It does not reconstruct the VB PRNG, reproduce a historical save's random stream, or certify the original executable's sampling probabilities or tie behavior. There are no file operations, clock-based seed selection, global RNG calls, default seed, or runtime/UI hooks in this module.

## Source and conversion boundary

The read-only native evidence in `MAP_LOAD_VM_STAGE.md` shows the original RND query calling random import ordinal 593 at VA 6082e6, multiplying by the float constant 100.0, and calling `__vbaFpI2` at VA 6082f2. There is no `+1`. Original EXE SHA-256 is `21dc753d3aa828fb29dc171e595857be234833edc43a1d80833540ae7e355b84`; the executable was not run. The authoring help's 1..100 and reference `floor(random()*100)+1` disagree with this static sequence.

Microsoft documents Rnd as a Single-precision result in [0, 1). The compatibility provider uses a declared 32-bit grid in that interval, not a claim of the same Single-precision sampling lattice or VB seed evolution. [Microsoft VBA Rnd function](https://learn.microsoft.com/en-us/office/vba/language/reference/user-interface-help/rnd-function).

Microsoft documents exact-half CInt/CLng conversion as nearest-even. This informs the declared compatibility rule; it is not direct verification of this executable's helper, x87 control mode, or intermediate precision. [Microsoft VBA type conversion functions](https://learn.microsoft.com/en-us/office/vba/language/concepts/getting-started/type-conversion-functions).

Each isolated engine `randi()` yields an unsigned 32-bit raw integer. The provider interprets it on the exact grid `raw / 2^32`, scales by 100, then rounds to the nearest integer with exact halves going to the even integer. Integer quotient/remainder arithmetic implements the entire operation; neither Godot `round()` nor floating-point conversion is used. The numerator is at most 429496729500 and fits signed 64-bit. Output is 0..100. Exact examples: raw 536870912 maps 12.5→12; 1610612736 maps 37.5→38; 2684354560 maps 62.5→62; 3758096384 maps 87.5→88. Raw 0 maps 0 and raw 4294967295 maps 100. This mapping has roughly half-width endpoint buckets. It is not a measured native distribution, and it does not imply a 5% probability for the strict source condition RND<5.

Godot currently uses PCG32 internally but explicitly treats the algorithm as an implementation detail. Its documentation supports isolated seeded generators, integer draws, and state snapshots, and requires seed to be set before restoring state. [Godot 4.6 RandomNumberGenerator](https://docs.godotengine.org/en/4.6/classes/class_randomnumbergenerator.html). The provider therefore records an exact engine fingerprint and refuses a snapshot made by a different build instead of silently reseeding or promising cross-version sequences.

## State and authority

The caller explicitly supplies a native signed 64-bit seed and a unique `stream_id` of 1..64 ASCII letters, digits, dot, underscore, or hyphen. The token identifies the owning session/stream; it does not secretly salt the seed. Two stream IDs with the same seed yield the same samples, but their transactions cannot be interchanged. Reusing both a stream ID and all state values deliberately produces an indistinguishable stream; uniqueness is the caller's responsibility.

A successful snapshot is recursively read-only and has exactly:

```text
provider: "legend.compat-rng"
version: 1
engine: "<major>.<minor>.<patch>:<status>:<build>:<full source hash>"
stream_id: <explicit caller token>
seed_words: [low_uint32, high_uint32]
state_words: [low_uint32, high_uint32]
cursor: <native integer 0..9007199254740991>
```

Seed and PRNG state are stored as two native unsigned 32-bit-valued integers, preserving every bit of the signed 64-bit engine representation, including the sign bit. No 64-bit state passes through a float or JSON number. All API numeric inputs require native integers; integral floats, NaN, Infinity, booleans and numeric strings are rejected. A future persistence adapter must explicitly preserve/reconstruct these exact integers and retain provider/version/engine; this module does not add a JSON decoder or extend the inventory-only save format.

`validate` is bounded structural admission of a caller-owned snapshot, not authentication or proof of the entire stream history. Supply only snapshots issued by `create`/`commit` or faithfully restored copies of those snapshots. Arbitrary invented engine state values are outside the restoration contract. Replaying from the original seed for an arbitrarily large cursor is deliberately not performed. Transaction validation does prove that a supplied candidate follows its admitted current base.

New streams are supported on the currently running compatible Godot API, including a different 4.6.x patch: `create` records that running engine's fingerprint. The engine restriction applies to **old snapshots**, not new game creation. An engine mismatch is an explicit error requiring a future migration/compatibility decision, never implicit reseeding. Linux 4.6.3 was tested; Windows execution and cross-build/cross-platform replay equivalence have not been verified.

The runtime owns one authoritative RNG snapshot, separate from `state.inventory`. VM `rnd_values` and bridge actor `random_cursor` are temporary query/candidate projections, not independently mutable authorities. Construct the bridge cursor from the RNG snapshot and check that its returned cursor agrees with the committed RNG candidate before publishing the whole game/world transaction. The current bridge's smaller cursor bound may reject before this provider's larger exact-integer limit.

## API and transaction sequence

All methods return `{ok:false,error,detail}` on rejection without exposing partial state/draws or modifying inputs. Successful returned `state` and `transaction` objects, including all nested arrays, are detached and recursively read-only. Caller-owned typed arrays are normalized when snapshots are returned.

- `create(stream_id, seed)` → `{ok:true,state}`. Seed selection happens explicitly outside the pure module. No seed is inferred from time, a previous save, or global RNG.
- `validate(state)` → `{ok:true,state}`. Validates exact fields/provider/build/token/word pairs/cursor, and returns a detached snapshot. It neither draws nor advances.
- `reserve(state, count)` → `{ok:true,transaction}`. Count is 0..64 and `cursor+count` must remain bounded before generation/allocation. The transaction contains exact `kind`, `version`, `base`, `count`, `raw_values`, `rnd_values`, and post-draw `checkpoints`. It restores an isolated generator, produces the candidate, and does not change live state. Repeating the same reservation returns identical data.
- `commit(current, transaction, consumed)` → `{ok:true,state}`. Requires the complete live base to match, including stream ID, seed, engine and cursor. It validates bounded transaction structure and regenerates **all** reserved raw/resolved values and checkpoints, including unused suffixes, to reject tampering. It returns only the successfully consumed prefix's state and advances cursor by `consumed`. Consumption must be a native integer from 0 through count. Zero consumption is a no-op, not a hidden reservation consumption.
- `rollback(current, transaction)` → `{ok:true,state}`. Requires a valid structural reservation and matching live base, then returns an unchanged detached snapshot. It does not draw or replay. Candidate values are discarded, so rollback does not need to certify their content. It cannot undo a committed stream: an old base is stale after positive consumption.
- `resolve_u32(raw)` → `{ok:true,value}`. Exposes the deterministic conversion for boundary verification; it is not another random source.
- `engine_fingerprint()` → exact build identifier.

The adapter reserves enough draws for its bounded VM operation and passes only `transaction.rnd_values` as `context.rnd_values`. VM failure, sample exhaustion, missing assets, invalid destination, or world-preflight failure must discard/rollback the reservation. Retrying on the same base sees the same values. A successful VM result's `random_consumed` selects the prefix, but **the provider cannot authenticate that this count came from a successful VM**: the adapter must enforce that precondition and keep the candidate unpublished until every world/state check succeeds. Missing/insufficient draws are an error, not permission to reroll.

For compound operations, carry detached staged RNG state forward between their successful candidate steps and publish only the final state with the world/game changes. Never publish RNG alone before world preflight. Positive commit invalidates the previous base; a zero-consumption candidate or rollback intentionally leaves the original reservation reusable. This is a pure value protocol with no global transaction registry or hidden consumed-token cache.

## Verification

The ignored harness `Project/tests/test_compat_rng.gd` passed 13,353 assertions on Linux Godot 4.6.3. It checks:

- Exact rational nearest-even oracle at 10,001 grid positions, all 100 rounding thresholds and adjacent raw integers, four representable half-ties, and both endpoints.
- Signed64 seed boundaries, all-bit state checkpoints against an independently instantiated engine RNG, binary primitive roundtrip, batch/single-step equality, and same-base retry identity.
- Consumed prefixes 0/1/7/32/63/64, full unused-suffix forgery rejection, stale/changed/cross-stream bases, zero reservations, exhaustion, and cursor/count limits before draws.
- Recursive read-only output, normalized typed word arrays, input byte equivalence after failed transactions, bounded malformed/cyclic/oversized data, discriminator/type matrices, finite-value rejection, and build mismatch with current-build new creation still available.
- The process-global RNG sequence remains unchanged by all provider APIs. Real VM success advances only its consumed prefix; late invalid TOMAP and exhausted RND clear the VM transaction and permit identical retry draws.

No full-player save, native random migration, arbitrary distribution claim, or additional gameplay mechanic is introduced.
