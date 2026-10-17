#!/usr/bin/env python3
"""New A00 v2 additive installer; NOT an exact recovery of the old freeze04 tool."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys

CONFIG_SHA = '3f6b02dbff6fd73dac52288b74290408dc22b8151922e21f5019bea65cc099b4'
LEAVES = 'data/a00_trial_runtime_execution_leaves.json'
CONTROLLER = 'scripts/a00_trial_runtime/controller.gd'
RUNTIME = (CONTROLLER, 'scripts/a00_trial_runtime/a00_trial_core.gd',
           'scripts/a00_trial_runtime/dialogue_vm.gd',
           'scripts/a00_trial_runtime/execution_gate.gd',
           'scenes/earth_a00_trial_candidate.tscn', LEAVES)
DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW


class Refusal(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise Refusal(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def checked_root(raw):
    """Inspect EVERY original prefix, including prefixes before '..', first."""
    require(isinstance(raw, str) and raw and '\x00' not in raw, 'invalid root')
    original = raw if os.path.isabs(raw) else os.getcwd() + '/' + raw
    prefix = '/'
    for part in original.split('/'):
        if not part:
            continue
        prefix = os.path.join(prefix, part)  # Do not normpath or resolve here.
        info = os.lstat(prefix)
        require(not stat.S_ISLNK(info.st_mode), 'symlink root chain: ' + prefix)
        require(stat.S_ISDIR(info.st_mode), 'root chain is not a directory: ' + prefix)
    return Path(original).resolve(strict=True)


def inside(path, root):
    return path == root or root in path.parents


def relative(path, resource=False):
    require(isinstance(path, str), 'non-string path')
    if resource:
        require(path.startswith('res://'), 'non-resource closure path')
        path = path[6:]
    require(path and not path.startswith('/') and '\\' not in path and '\x00' not in path,
            'unsafe relative path: ' + repr(path))
    require(all(p not in ('', '.', '..') for p in path.split('/')), 'unsafe path components')
    return path


def open_root(path):
    fd = os.open('/', DIR_FLAGS)
    try:
        for part in path.parts[1:]:
            child = os.open(part, DIR_FLAGS, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except BaseException:
        os.close(fd)
        raise


def parent_fd(root_fd, rel, create=False):
    fd = os.dup(root_fd)
    try:
        for part in relative(rel).split('/')[:-1]:
            try:
                child = os.open(part, DIR_FLAGS, dir_fd=fd)
            except FileNotFoundError:
                if not create:
                    raise
                os.mkdir(part, 0o755, dir_fd=fd)
                child = os.open(part, DIR_FLAGS, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except BaseException:
        os.close(fd)
        raise


def read_file(root_fd, rel):
    parent = parent_fd(root_fd, rel)
    try:
        fd = os.open(rel.split('/')[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                     dir_fd=parent)
        try:
            require(stat.S_ISREG(os.fstat(fd).st_mode), 'not a regular file: ' + rel)
            with os.fdopen(fd, 'rb', closefd=False) as source:
                return source.read()
        finally:
            os.close(fd)
    finally:
        os.close(parent)


def absent(root_fd, rel):
    try:
        parent = parent_fd(root_fd, rel)
    except FileNotFoundError:
        return
    try:
        try:
            os.stat(rel.split('/')[-1], dir_fd=parent, follow_symlinks=False)
        except FileNotFoundError:
            return
        raise Refusal('runtime leaf already exists: ' + rel)
    finally:
        os.close(parent)


def json_object(data):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    obj = json.loads(data, object_pairs_hook=unique)
    require(isinstance(obj, dict), 'JSON object required')
    return obj


def records(obj, schema, resource=False):
    require(obj.get('schema') == schema, 'wrong schema: ' + schema)
    rows = obj.get('files')
    require(isinstance(rows, list) and rows, 'nonempty file list required')
    out = {}
    for row in rows:
        require(isinstance(row, dict), 'file record must be an object')
        rel = relative(row.get('path'), resource)
        require(rel not in out, 'duplicate file path: ' + rel)
        require(isinstance(row.get('sha256'), str) and
                re.fullmatch('[0-9a-f]{64}', row['sha256']), 'invalid SHA256')
        require(type(row.get('bytes')) is int and row['bytes'] >= 0, 'invalid file size')
        out[rel] = row
    return out


def verify(data, row, name):
    require(len(data) == row['bytes'] and digest(data) == row['sha256'],
            'size/SHA256 mismatch: ' + name)


def preflight(repo_fd, candidate_fd, target_fd, manifest_sha):
    require(re.fullmatch('[0-9a-f]{64}', manifest_sha) is not None, 'invalid manifest SHA')
    baseline = read_file(repo_fd, 'Project/project.godot')
    require(digest(baseline) == CONFIG_SHA, 'baseline project.godot is not the pinned config')
    require(read_file(target_fd, 'project.godot') == baseline, 'target project.godot differs')
    imported = parent_fd(target_fd, '.godot/imported/_probe_')
    os.close(imported)
    manifest_bytes = read_file(candidate_fd, 'MANIFEST.json')
    require(digest(manifest_bytes) == manifest_sha, 'candidate MANIFEST SHA256 mismatch')
    manifest = records(json_object(manifest_bytes), 'a00-runtime-rebuilt-source-manifest-v2')
    require({p[8:] for p in manifest if p.startswith('Project/')} == set(RUNTIME),
            'manifest must contain exactly the six runtime leaves under Project/')
    files = {}
    for rel, row in manifest.items():
        files[rel] = read_file(candidate_fd, rel)
        verify(files[rel], row, rel)
    require('EXECUTION_ROOT.json' in files, 'EXECUTION_ROOT missing from manifest')
    root = json_object(files['EXECUTION_ROOT.json'])
    root_rows = records(root, 'a00-runtime-execution-root-v1', True)
    leaves = json_object(files['Project/' + LEAVES])
    leaf_rows = records(leaves, 'a00-runtime-execution-leaves-v1', True)
    require(set(root_rows) == {LEAVES, CONTROLLER}, 'wrong execution root members')
    require(root.get('base_commit') == leaves.get('base_commit') and
            isinstance(root.get('base_commit'), str) and
            re.fullmatch('[0-9a-f]{40}', root['base_commit']), 'wrong execution base commit')
    require(type(root.get('leaf_count')) is int and root['leaf_count'] == len(leaf_rows),
            'execution leaf count mismatch')
    require(not (set(root_rows) & set(leaf_rows)), 'execution DAG contains root/leaf overlap')
    require(set(RUNTIME) <= set(root_rows) | set(leaf_rows), 'runtime closure is incomplete')
    payload = {rel: files['Project/' + rel] for rel in RUNTIME}
    for rel, row in list(root_rows.items()) + list(leaf_rows.items()):
        data = payload[rel] if rel in payload else read_file(target_fd, rel)
        verify(data, row, 'closure: ' + rel)
    controller = payload[CONTROLLER].decode('utf-8')
    pins = re.findall(r'^const EXECUTION_SHA\s*=\s*"([0-9a-f]{64})"\s*$', controller, re.M)
    require(pins == [digest(payload[LEAVES])], 'controller execution SHA pin mismatch')
    for rel in RUNTIME:
        absent(target_fd, rel)
    return payload, len(leaf_rows)


def install(target_fd, payload):
    """Exclusive no-follow creation; rollback only still-owned new file inodes."""
    created = []
    try:
        for rel in RUNTIME:
            parent = parent_fd(target_fd, rel, create=True)
            name = rel.split('/')[-1]
            try:
                fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                             0o644, dir_fd=parent)
            except BaseException:
                os.close(parent)
                raise
            identity = os.fstat(fd)
            created.append((parent, name, identity.st_dev, identity.st_ino))
            try:
                with os.fdopen(fd, 'wb', closefd=False) as output:
                    output.write(payload[rel])
                    output.flush()
                    os.fsync(fd)
            finally:
                os.close(fd)
    except BaseException:
        for parent, name, device, inode in reversed(created):
            try:
                current = os.stat(name, dir_fd=parent, follow_symlinks=False)
                if (current.st_dev, current.st_ino) == (device, inode):
                    os.unlink(name, dir_fd=parent)
            except FileNotFoundError:
                pass
        raise
    finally:
        for parent, _, _, _ in created:
            os.close(parent)


def run(repo, candidate, target, manifest_sha, dry_run=False):
    repo, candidate, target = [checked_root(raw) for raw in (repo, candidate, target)]
    require(not inside(candidate, repo), 'candidate must be outside the repository')
    require(not inside(target, repo) and not inside(repo, target),
            'target overlaps the protected repository')
    require(not inside(target, candidate) and not inside(candidate, target),
            'target overlaps the candidate source')
    fds = []
    try:
        for path in (repo, candidate, target):
            fds.append(open_root(path))
        payload, count = preflight(*fds, manifest_sha)
        if not dry_run:
            install(fds[2], payload)
        return {'status': 'dry-run-ok' if dry_run else 'installed', 'runtime_files': 6,
                'execution_leaves': count, 'target': str(target), 'manifest_sha256': manifest_sha,
                'new_tool_not_freeze04_recovery': True, 'engine_run': False}
    finally:
        for fd in fds:
            os.close(fd)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('repo', 'candidate', 'target', 'manifest-sha'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.repo, args.candidate, args.target, args.manifest_sha, args.dry_run),
                         sort_keys=True))
    except (Refusal, OSError, ValueError, UnicodeError) as error:
        print('REFUSED: ' + str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
