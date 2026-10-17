# A00 v2 small additive installer

This is a newly written tool, **not** an exact recovery of the old freeze04/04 installer.
It only supports this handoff's independently copied and already imported source Project.
It does not support PCK deployments, importing resources, running Godot, tests installation,
`--with-tests`, resource copying, settings edits, replacement, or Git operations.
Python 3 on POSIX with `O_NOFOLLOW`, `O_DIRECTORY`, and `dir_fd` support is required.

## Command

Run the dry run first, with the actual repository root, the unpacked candidate directory,
and the separate imported Project directory. The target must already have
`.godot/imported` and the pinned, unchanged `project.godot`.

```sh
python3 -B tools/install_a00.py \
  --repo /absolute/path/to/tihu-legend-recovered \
  --candidate /absolute/path/to/a00-runtime-rebuilt-v2 \
  --target /absolute/path/to/independent-imported/Project \
  --manifest-sha 44978022b97618b998e630cbd3baaf91063349c12b7a10839978658845e76094 \
  --dry-run
```

After a successful dry run, omit only `--dry-run` to install six new runtime files.
A repeat install refuses because the runtime leaves already exist. There is no overwrite
or force switch. A dry run and an install repeat the entire preflight independently.
No test or evidence files are installed.

## Safety contract

- Walk `lstat` over every component of each original CLI root before resolving it,
  including components that appear before `..`. Symlink root chains are refused.
- Resolve repository/candidate/target canonical paths; refuse protected repository or
  candidate overlap. All subsequent directory walks and file access are descriptor-based,
  with no-follow flags; candidate and target leaf/parent symlinks are refused.
- Check baseline `Project/project.godot` against fixed SHA256
  `3f6b02dbff6fd73dac52288b74290408dc22b8151922e21f5019bea65cc099b4`, and
  target `project.godot` byte-for-byte against that baseline.
- Check caller-provided candidate MANIFEST SHA256, every declared file's size/SHA256,
  the exact set of six runtime payload paths, EXECUTION_ROOT, the leaves DAG, leaf count,
  and controller's execution SHA pin. For the real candidate this covers 436 leaves.
  Runtime leaves come from the verified candidate; all old leaves are verified in target.
- Require all six destination files to be absent. The complete preflight is read-only.
  Malformed, mismatched, incomplete, symlinked, and conflicting input is refused.
- Create each payload with `O_EXCL|O_NOFOLLOW`, after the whole preflight passes.
  On write failure, unlink only files created by that call and still matching the original
  device/inode. Existing files, including a concurrently created conflict, are not removed.
  Newly created empty parent directories can remain after an installation write failure.
- Guards use explicit checks and exceptions, not `assert`; Python `-O` retains them.

The target and source should be quiescent while running. Descriptor-based access and
exclusive creation defend path substitution and leaf conflicts; the tool is not a locking
protocol for arbitrary concurrent directory moves or edits to already-verified old leaves.
It never changes an entry scene, setting, existing file, or resource import cache.

This tool validates bytes and installation safety only. It does not establish Godot parse,
behavior, rendering, or native GUI success. The separate safety tests use tiny synthetic
projects, not the protected real repository.
