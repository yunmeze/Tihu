# Inventory-only persistence: pure codec checkpoint

This stage adds `scripts/core/inventory_codec.gd`, a pure bytes-to-inventory boundary. It does not read or write paths, connect to the running preview, initialize a player, restore an old save, migrate a legacy format, or define a full character-save schema. Loading a snapshot never changes a passed inventory or writes a file.

## Fixed envelope and external authority

Version 1 has exactly three envelope keys:

```json
{"format":"legend.inventory","version":1,"inventory":{}}
```

The empty object above only illustrates the envelope; a real `inventory` must satisfy `inventory_state.gd`. No template catalogue, weight policy, currency, player attributes, skills, map, VM, combat, or filesystem path belongs in this envelope. The caller supplies the fixed external catalogue and policy at both encode and decode. A file cannot authorize its own templates, equipment slots, or weight limit. Unknown labels, versions, fields, or references fail explicitly. There is no migration fallback and no search for another environment's historical save.

`encode(inventory, catalogue, policy)` returns `ok`, `bytes` (PackedByteArray), a detached normalized `inventory`, `total_weight`, and `overweight`. It checks bounds before normalizing, validates through the inventory core, enforces the narrower v1 numeric contract below, serializes the fixed envelope, then decodes and validates the exact output bytes. A bounded recursive semantic comparison must also match the normalized source before success; no altered-value result can expose writable bytes.

`decode(bytes, catalogue, policy)` requires a PackedByteArray and returns the core's detached normalized `inventory`, `total_weight`, and `overweight`. Failures return `ok: false`, `error`, `detail`, and, for parser errors, a Unicode-character `offset`. No failed result exposes a partial inventory. `overweight: true` is a valid structural result; load does not prevent later non-increasing recovery actions under the core's established policy.

## Strict and bounded input

Technical admission limits, not original gameplay rules:

- At most 4 MiB of encoded bytes; empty input fails.
- At most 4,096 instance records, including recovery entries.
- At most 131,072 JSON values and 24 nested levels.
- Numeric tokens have at most 128 characters.
- All persisted numeric values must be exact bounded integers. Native integer-valued floats and mathematically integral decimal/exponent tokens can normalize to integers; genuinely fractional metadata is unsupported in codec v1.

Before allocating normalized state or a JSON serialization, encode measures native containers with bounded traversal, rejecting cycles, excessive nodes/depth, and a conservative JSON-size estimate. That estimate reserves 256 bytes for the envelope, 32 bytes per scalar, and up to six bytes per string character; a near-limit native input can therefore be rejected even if a compact serialization might fit. Decode checks byte length before UTF-8 conversion, then makes a syntax/limits-only pass before materializing instance-record dictionaries in a second pass. The first pass still uses bounded key sets to detect duplicate object members; it does not construct instance payloads.

UTF-8 is validated byte by byte before using Godot's string conversion. Invalid continuation bytes, overlong encodings, surrogate encodings, values above U+10FFFF, truncated sequences, a leading BOM, and raw NUL are rejected. Escaped U+0000 is also deliberately rejected because this codec does not support embedded NUL text. Ordinary Unicode and valid escaped surrogate pairs are preserved.

The JSON gate requires standard object/array separators, escaped controls, standard literals, and valid number syntax. It rejects trailing commas, trailing content, unescaped newlines/tabs in strings, malformed escapes, unpaired surrogates, and duplicate keys at every level. It does not rely on Godot's permissive whole-document JSON parser. Godot's string-token decoder is called only after the token's escapes and Unicode pairing have been checked.

## Exact integer normalization

The envelope version, inventory counters, and supported instance integer properties are interpreted from decimal token text before any binary-float conversion. Exact integral forms such as `7`, `7.0`, `70e-1`, and `0.7e1` normalize to integer 7. A tiny nonzero fractional part cannot disappear through floating rounding and become a valid serial, revision, weight, or raw proficiency. Values outside the exact `2^53 - 1` bound fail; core validation still applies field-specific nonnegative/minimum constraints afterward.

Codec v1 intentionally has a **narrower metadata contract than the inventory core**: encode and decode reject non-integer provenance numbers with `unsupported_fractional_metadata`. The core continues to allow bounded finite fractional annotations in memory; it was not changed. The codec does not route fractional tokens through Godot's general decimal-to-float conversion. Independent tests found that Godot 4.6.3 can change values by one ULP or underflow normal values in that conversion, so merely replacing it with the engine JSON/Variant parser would not preserve snapshots.

Integral provenance numbers normalize to native integers when exact and within the bound. JSON does not preserve a distinction between native integer 1 and native floating 1.0; signed zero also has canonical numeric zero meaning here. The post-decode semantic comparison allows only these documented numeric normalizations while preserving dictionary keys, array order, string values, booleans, nulls, and all other values. A mismatch returns `precision_loss`, without bytes. Unknown raw proficiency remains null. IDs and different properties/provenance on same-template instances remain separate.

Supporting arbitrary IEEE floating metadata later requires a new explicitly specified representation/version, such as a validated bit-pattern encoding. It must not be silently added to this v1 contract or implemented through a known lossy engine conversion.

## Fresh verification

On 2026-10-15, Linux Godot 4.6.3 passed 10,142 fresh local codec assertions and all 1,664 inventory-core assertions, without script errors or engine warnings. Fixtures cover:

- Exact IDs, same-template/different-raw-property records, equipment/bag locations, Unicode, valid surrogate pairs, and valid overweight round trips.
- Source/byte immutability and detached decode results.
- Truncation, corrupt syntax, trailing content, invalid UTF-8, BOM/NUL, unknown format/version, duplicate keys, and malformed Unicode escapes.
- Exact decimal/exponent integer forms, maximal integers, fractional-rounding attacks, rejection of fractional/overflow/underflow tokens, nonfinite native fields, size/instance/depth/token bounds, and cyclic native input.
- A fixed-seed 5,000-value native-float probe: every non-integer value is rejected without writable bytes, integral values preserve exact numeric meaning, and every input remains byte-identical. Explicit Unicode/ID/integer cases still round-trip successfully.

The ignored harness is `Project/tests/test_inventory_codec.gd`. Tests use synthetic templates, not invented original-game initial items or old save contents. This checkpoint is not Windows runtime validation or disk durability verification.

## Next boundary: file store remains separate

No file store is implemented in this checkpoint. The next stage must take explicit caller-owned paths, validate bounded file lengths before reads, retain valid prior data, verify staged bytes after flush/reopen, report fallback source and rejected-candidate details without silent rewrites, and test ordinary failure points. Godot 4.6.3's Windows overwrite-rename implementation first removes the destination; a cross-platform store must not assume overwriting an existing primary is atomic. A generation-based, no-overwrite protocol is being evaluated separately rather than weakening this codec's completed boundary. Power-loss/fsync guarantees are not implied by FileAccess.flush.
