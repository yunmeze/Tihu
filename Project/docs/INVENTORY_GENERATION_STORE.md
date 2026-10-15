# Explicit inventory generation store

This separate checkpoint adds `scripts/core/inventory_store.gd`. It persists only the validated inventory envelope from `inventory_codec.gd`. It is not wired into the preview, VM, player initialization, combat, autosaving, or a complete character-save format. Merely loading the script creates no directories or files. There is no old-format migration or search for historical saves in another environment.

## Why immutable generations

Godot 4.6.3's Windows overwrite-rename path removes an existing destination before moving the source. The store therefore **never overwrites a committed destination** and never updates a mutable “latest” pointer. Each successful save appends a new generation; every previous generation remains byte-for-byte untouched. A valid older generation acts as the recovery copy. A corrupt new generation cannot be rotated over a good older copy.

The caller supplies an existing dedicated directory and an explicit inventory namespace, catalogue, and policy. Only absolute paths or explicit `user://` paths are accepted; `res://`, relative, absent, and linked store roots are rejected. The store creates only its own temporary writer-lock directory. It does not create the requested root or remove unrelated files. The caller owns the directory and must keep its path/ancestors stable. The final root component is checked for links; ancestor-component symlinks are not rejected or resolved into an ownership guarantee.

This protocol coordinates **cooperating writers that follow this lock protocol**. It does not claim safety against hostile processes, administrators, concurrent outside edits, mount changes, or external writers that ignore the lock. Godot has no portable rename-no-replace operation, so the lock and final absence check are essential to avoiding its overwrite behavior.

## Format and head token

A committed filename is exactly `inventory-` + 16 zero-padded decimal digits + `.dat`, such as `inventory-0000000000000001.dat`. Generations are positive integers bounded by `2^53 - 1`; noncanonical, zero, out-of-range, differently cased, or suffixed names are not interpreted as saves. Unknown names are left untouched but count toward the directory scan limit.

Each file contains:

```text
LEGEND-INVENTORY-GENERATION/1
codec-format:legend.inventory
codec-version:1
generation:1
payload-bytes:<canonical positive decimal byte length>
payload-sha256:<64 lowercase SHA-256 hex characters>

<unchanged legend.inventory v1 codec JSON bytes>
```

The fixed, ordered ASCII preheader ends in one blank line and is at most 256 bytes. Its generation is canonical unpadded decimal and must equal the filename. Length is a canonical positive integer bounded by `2^53 - 1`; the SHA-256 covers exactly the payload bytes. This is corruption detection, not authentication of local writers. There is no legacy two-line-header compatibility path: this store protocol was not published before the fixed preheader was added.

At most 256 bytes are read first, before applying current-version payload limits. Store schema, codec schema, filename binding, and the complete header are independently checked. An explicit unknown store version is recognized from the short first line even if the whole file exceeds current limits. Only after this gate may a current-version body be allocated, probed, checked for exact length/digest, decoded, and validated against the explicit namespace and external catalogue/policy. Unknown raw proficiency remains null. Bounded overweight remains loadable, allowing the core's later recovery actions.

Generation is a persistence sequence separate from inventory revision. A recovered snapshot can therefore be saved without inventing a gameplay mutation or reusing a damaged generation's number.

A head token has exactly:

```json
{"max_generation": 2, "valid_generation": 1, "digest": "64 lowercase SHA-256 hex characters"}
```

`max_generation` covers the highest canonical filename observed, including rejected/corrupt candidates. `valid_generation` and `digest` identify the actually selected valid record. The hash covers the complete record, not just JSON. Empty stores use `EMPTY_HEAD = {max_generation: 0, valid_generation: 0, digest: ""}`. Both sequence values are native bounded integers. A stale token cannot silently save over a later observation.

## Small API

Instantiate the module with `preload("res://scripts/core/inventory_store.gd").new()`.

- `load_inventory(directory, namespace, catalogue, policy)` scans and reads without mutation. Success returns `inventory`, `total_weight`, `overweight`, `generation`, `path`, `source` (`latest` or `fallback`), `head`, `rejected` diagnostics, and `generation_count`.
- `save_inventory(directory, namespace, inventory, catalogue, policy, expected_head)` requires an explicit current head, or `EMPTY_HEAD` for a genuinely empty store. Success returns `committed: true`, the new generation/path/head, normalized inventory/weight information, `warnings`, and `lock_pending`.

Failures return `ok: false`, a stable `error`, and `detail`; save results additionally distinguish ordinary non-commit from uncertain publication. A pre-validation error creates nothing. A store with recognized files but no valid generation refuses automatic reinitialization. Explicit recovery/cleanup remains a future operation, not an implicit overwrite path.

## Bounded read and recovery

Directory entries are read incrementally with hidden entries included; there is no unbounded `get_files()` allocation. Admission limits are:

- 512 total directory entries, including unknown files and an existing lock.
- 128 recognized generation paths, with no automatic garbage collection.
- `Codec.MAX_BYTES + 256` bytes per file and `Codec.MAX_BYTES` payload bytes. Only the bounded 256-byte header probe may precede these checks; a larger body is never allocated.
- 16 MiB of total file bytes read in one scan.

Exceeding a scan/generation/read budget is an explicit failure, never permission to select from a partial scan. Candidate files are processed newest-first. Symlinks and directories in generation positions are rejected. Exact read length and unchanged observed length are checked.

A **complete, known-compatible preheader** permits ordinary body corruption, truncation, invalid UTF-8, checksum/length mismatch, or invalid v1 state to fall back to a valid older generation within the budget. The result names the actual source and includes rejected newer paths/reasons. Loading never rewrites, repairs, deletes, renames, or claims a lock.

Missing, truncated, malformed, or unreadable preheaders cannot establish compatibility. They return `compatibility_unknown`, not a normal successful fallback. This also covers symlink/directory candidates and bodies too large to safely cross-check. An older valid generation may be named only as recovery diagnostic metadata. Exceeding codec instance/depth/node limits or the total-read budget fails explicitly with no partial inventory, rather than letting an incomplete inspection bypass a version barrier.

A newer candidate with an unsupported store/codec version or format is a **downgrade barrier**: return `unsupported_newer_version`, with no adoptable `inventory`. If an older valid record exists, only its path/generation/digest are exposed as `recoverable` diagnostic metadata. Filename/header or namespace disagreement similarly returns `incompatible_generation`. These conditions prohibit continued writing; they are not normal silent rollbacks.

The body is independently schema-probed **before checksum or length failures can trigger fallback**. A parseable body declaring a future/unknown codec schema is a barrier even when its header declares v1 and its length/hash are stale. The probe ignores current v1 numeric/instance/field admission so future schema plus fractional metadata, fractional counters, additional fields, or excess instances cannot masquerade as ordinary v1 corruption. If structural inspection itself exhausts its bounded budget, loading/writing fails closed. After known-v1 schema identification, codec admission still runs without materializing instance payloads before its build pass.

## Write protocol and ordinary failures

1. Validate/encode the candidate in memory before any filesystem mutation. Reject namespace mismatch or malformed head.
2. Acquire exclusive write ownership by atomically creating `.inventory-write-lock` under the caller's directory. Only a successful mkdir grants ownership. A pre-existing lock, file, or link is never entered for writing, deleted, or automatically reclaimed.
3. Under the lock, rescan with the same bounds and compare the whole head token. Reject stale heads, incompatible versions, exhausted generations, and stores with no valid recognized record.
4. Select `max_generation + 1`, never an old or corrupt number. The final target must not exist.
5. Write `pending.tmp` inside this invocation's newly created lock directory. Check store_buffer/error status, flush, close, reopen, enforce read limits, decode/validate, and require exact record-byte equality.
6. Close all handles. Recheck final-target absence, then rename the owned temporary file to the fresh committed filename. Source and destination are within the same directory tree and volume. No committed file is removed first.
7. Successful rename is the commit point. Clean only the owned leftover temporary path and the owned empty lock directory, never recursively and never by scanning for somebody else's temporary files.

An ordinary precommit failure leaves every previous generation unchanged and attempts to remove only this invocation's staging artifacts. Failed cleanup is explicitly reported. If rename reports failure but the intended final bytes can be reread and validated exactly, publication is reconciled as committed with a warning. If the source still exists and the final target does not, publication is a definite failure. Other ambiguous outcomes return `commit_uncertain`, `committed: null`, and retain the lock for read-only diagnosis rather than guessing or retrying.

After a successful publication, a later checkpoint or cleanup failure still returns `ok: true` and `committed: true`, with warnings. `lock_pending: true` means the generation is saved but the lock requires explicit cleanup; it is not an invitation to retry the save. Reads remain available. The test-only protected `_fault` and `_rename` override seams permit deterministic failure tests without adding a saved-input switch or a public runtime fault parameter.

A process crash can leave a lock or pending file. Readers ignore staging content and continue to inspect committed generations. Future writes return `store_locked`; the implementation does not guess whether a writer is dead. There is no automatic lock takeover, recursive deletion, or history pruning. At capacity, writing fails explicitly.

## Guarantees and platform boundary

Verified locally: ordinary failures and tested process interruptions preserve old committed records; incomplete staging never becomes an adopted snapshot; a complete newer generation can be read after publication even if lock cleanup did not happen.

This is **not a power-loss/fsync guarantee**. Godot's FileAccess.flush uses buffered I/O flushing and does not provide this protocol with parent-directory fsync. Hardware/filesystem I/O failure, hostile outside mutation, and arbitrary filesystem crash behavior remain outside the guarantee. The design avoids Windows's known destructive overwrite branch, but **actual Windows 4.6.x execution has not been tested**. Linux tests plus source review are not Windows runtime validation.

Implementation references:

- [Godot 4.6.3 Windows rename](https://github.com/godotengine/godot/blob/4.6.3-stable/drivers/windows/dir_access_windows.cpp#L254-L292)
- [Godot 4.6.3 Unix rename](https://github.com/godotengine/godot/blob/4.6.3-stable/drivers/unix/dir_access_unix.cpp#L379-L407)
- [Godot Windows flush](https://github.com/godotengine/godot/blob/4.6.3-stable/drivers/windows/file_access_windows.cpp#L352-L375)
- [Godot DirAccess API](https://docs.godotengine.org/en/4.6/classes/class_diraccess.html)

## Fresh verification

On 2026-10-15, Linux Godot 4.6.3 passed **1,683 local store assertions** without script errors or engine warnings, using only caller-created isolated `user://` directories under ignored validation storage. The ignored harness covers:

- Empty/current/stale heads, immutable history, same snapshot in later generations, Unicode, valid overweight, and codec rejection before file creation.
- All before/after lock, write, flush, reread/validation, publication, and cleanup checkpoints; corruption and valid-but-changed staged bytes; existing-target conflicts; failed/uncertain/reconciled publication; committed-with-lock-pending reporting.
- Cooperative writer contention, stale locks and foreign pending files left untouched, known-header body corruption fallback, unknown/truncated-header barriers, future-version/format barriers even with stale checksums or lengths, oversized future headers, schema-probe exhaustion, filename/namespace mismatch, no-valid-generation refusal, unknown-name exclusion, and all scan/file/generation/read budgets.

An additional **34 real-process assertions** use separate Godot processes. One process is killed after lock creation, write, flush, successful verification, just before rename, and just after rename. Each case reloads the old or newly committed generation as appropriate, retains the old file's exact bytes, and keeps writes blocked by the abandoned lock. Two real cooperating processes also contend for the lock: the owner publishes exactly one new generation, the other receives `store_locked`, and the owner releases its lock normally. These probes are under ignored `Project/tests`; no original game executable was run.
