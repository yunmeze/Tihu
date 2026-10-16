"""Fail-closed frozen legacy adapter + explicit future runtime_files contract.
No production writes. No research archive crawling. Python stdlib only.
"""
import argparse, hashlib, json, pathlib, re, subprocess
P = pathlib.Path(__file__).resolve().parent
PREFIXES = {'res://art_source/', 'res://assets/', 'res://art_source/hero_e_walk_source_r8/'}
FUTURE = 'earth-runtime-files-v1'

def sha(b):
    return hashlib.sha256(b).hexdigest()

def expansion_dependencies(d):
    """Audited v1 loader accesses; provenance is deliberately not traversed."""
    schema = d['schema']
    expected = {}
    def put(rec):
        path = rec['path']
        if path in expected and expected[path] != rec:
            raise ValueError('Conflicting expansion dependency records')
        expected[path] = rec
    for key in ('source_map', 'source_manifest'):
        put(d[key])
    if schema == 'earth-first-map-east-ground-v1':
        group = d['group']
        if group['owner_count'] != 57 or len(group['owners']) != 57:
            raise ValueError('East owner scope changed')
        put(group['tile'])
        dependencies = group['source_dependencies']
        actual = {d['source_map']['path'], d['source_manifest']['path'], group['tile']['path']}
        actual.update(o['source_frame']['atlas'] for o in group['owners'])
        if {r['path'] for r in dependencies} != actual or len(dependencies) != len(actual):
            raise ValueError('East source_dependencies differs from actual loader accesses')
        for rec in dependencies: put(rec)
    elif schema == 'earth-first-map-plant-reuse-v1':
        if d['group_count'] != 24 or len(d['groups']) != 24 or d['owner_count'] != 81 or sum(len(g['owners']) for g in d['groups'].values()) != 81:
            raise ValueError('Plant scope changed')
        for group in d['groups'].values():
            actual = {d['source_map']['path'], d['source_manifest']['path']}
            actual.update(o['source_frame']['atlas'] for o in group['owners'])
            actual.update(o['texture'] for o in group['owners'])
            deps = group['source_dependencies']
            if {r['path'] for r in deps} != actual or len(deps) != len(actual):
                raise ValueError('Plant source_dependencies differs from actual loader accesses')
            for rec in deps: put(rec)
            for owner in group['owners']:
                pin = expected[owner['texture']]
                if pin['sha256'] != owner['texture_sha256'] or [pin['width'], pin['height']] != owner['texture_size'] or pin['role'] != 'texture':
                    raise ValueError('Plant owner texture binding mismatch')
    else:
        raise ValueError('Unknown expansion schema')
    declared = {r['path']: r for r in d['runtime_files']}
    if len(declared) != len(d['runtime_files']) or declared != expected:
        raise ValueError('Expansion runtime_files differs from actual loader dependencies')
    return expected

def run(root, policy):
    if policy.get('schema') != 'earth-reviewed-legacy-export-policy-v1':
        raise ValueError('Unknown export policy schema')
    root = pathlib.Path(root).resolve()
    rows = {}
    reasons = {}
    todo = []
    processed = set()
    tracked = set(subprocess.check_output(['git', '-C', str(root.parent), 'ls-files', '-z', 'Project']).decode().split('\x00')) if (root.parent / '.git').exists() else set(policy['tracked'])

    def add(path, reason, digest=None):
        if not (isinstance(path, str) and path.startswith('res://')):
            raise ValueError(('invalid path', path))
        rel = path[6:]
        if not ('\\' not in rel and ':' not in rel and all((x not in ('', '.', '..') for x in rel.split('/')))):
            raise ValueError(path)
        if not 'Project/' + rel in tracked:
            raise ValueError(('untracked', path))
        f = root / rel
        if f.is_symlink() or not f.resolve().is_relative_to(root):
            raise ValueError(('External or symbolic dependency', path))
        if not f.is_file():
            raise ValueError(('missing', path))
        b = f.read_bytes()
        h = sha(b)
        if path in policy.get('asset_pins', {}) and h != policy['asset_pins'][path]:
            raise ValueError(('Frozen asset bytes changed', path))
        if digest is not None:
            if not h == digest:
                raise ValueError(('hash mismatch', path))
        if path not in rows:
            row = {'path': path, 'bytes': len(b), 'sha256': h, 'type': f.suffix[1:]}
            rows[path] = row
            todo.append(path)
            if f.suffix == '.png':
                if not b[:8] == b'\x89PNG\r\n\x1a\n':
                    raise ValueError('Dependency validation failed')
                row['width'] = int.from_bytes(b[16:20], 'big')
                row['height'] = int.from_bytes(b[20:24], 'big')
        reasons.setdefault(path, set()).add(reason)

    def refs(v, reason):
        if isinstance(v, str) and v.startswith('res://'):
            add(v, reason)
        elif isinstance(v, list):
            for x in v:
                refs(x, reason)
        elif isinstance(v, dict):
            for k, x in v.items():
                if isinstance(x, str) and re.fullmatch('[0-9a-f]{64}', x) and (k.startswith('res://') or k.startswith(('assets/', 'data/', 'scripts/', 'shaders/'))):
                    add(k if k.startswith('res://') else 'res://' + k, reason, x)
                else:
                    refs(x, reason)
    for r in policy['roots']:
        add(r, 'entry')
    for r in policy['dynamic_paths']:
        add(r, 'audited dynamic expression')
    while todo:
        path = todo.pop(0)
        if path in processed:
            continue
        processed.add(path)
        f = root / path[6:]
        if f.suffix not in ('.gd', '.tscn', '.json', '.tres', '.gdshader'):
            continue
        if f.suffix == '.json':
            d = json.loads(f.read_bytes())
            if not isinstance(d, dict):
                raise ValueError('Dependency validation failed')
            if d.get('schema') in (FUTURE, 'earth-first-map-static-props-v1', 'earth-first-map-east-ground-v1', 'earth-first-map-plant-reuse-v1'):
                if d.get('schema') != FUTURE:
                    cfg = policy['legacy'].get(path)
                    if cfg is None or cfg['schema'] != d['schema'] or cfg['sha256'] != rows[path]['sha256']:
                        raise ValueError(('Unreviewed static-props schema or bytes', path))
                    if d['schema'] in ('earth-first-map-east-ground-v1', 'earth-first-map-plant-reuse-v1'):
                        expansion_dependencies(d)
                    if d['schema'] == 'earth-first-map-static-props-v1':
                        expected = {}
                        for group in d['groups'].values():
                            for rec in [group['master']] + group['source_dependencies']:
                                if rec['path'] in expected and expected[rec['path']] != rec:
                                    raise ValueError('Conflicting static-props dependency records')
                                expected[rec['path']] = rec
                        declared = {r['path']: r for r in d['runtime_files']}
                        if len(declared) != len(d['runtime_files']) or declared != expected:
                            raise ValueError('Static-props runtime_files differs from actual loader dependencies')
                        for pin in [d['source_map'], d['source_manifest']]:
                            if pin['path'] not in declared or pin['sha256'] != declared[pin['path']]['sha256']:
                                raise ValueError('Static-props source binding missing')
                if d.get('schema') == FUTURE and not (set(d) <= {'schema', 'runtime_files', 'provenance', 'status'} and d.get('runtime_files')):
                    raise ValueError(('future fields', path))
                for rec in d['runtime_files']:
                    if not set(rec) <= {'path', 'sha256', 'bytes', 'type', 'role', 'width', 'height'}:
                        raise ValueError('Dependency validation failed')
                    if not rec.get('role') in ('texture', 'registration', 'source-map', 'source-atlas', 'source-atlas-manifest', 'shader', 'raw-contract'):
                        raise ValueError('Dependency validation failed')
                    if not rec.get('type') in ('png', 'json', 'gdshader', 'gd'):
                        raise ValueError('Dependency validation failed')
                    role_types = {'texture':'png', 'registration':'json', 'source-map':'json', 'source-atlas':'png', 'source-atlas-manifest':'json', 'shader':'gdshader'}
                    if rec['role'] in role_types and rec['type'] != role_types[rec['role']]:
                        raise ValueError('Runtime file role/type mismatch')
                    add(rec['path'], path + ' runtime_files', rec['sha256'])
                    row = rows[rec['path']]
                    if not (row['bytes'] == rec['bytes'] and row['type'] == rec['type']):
                        raise ValueError('Dependency validation failed')
                    if row['type'] == 'png':
                        if not (row['width'] == rec['width'] and row['height'] == rec['height']):
                            raise ValueError('Dependency validation failed')
                continue
            cfg = policy['legacy'].get(path)
            if not cfg is not None:
                raise ValueError(('unknown registration/schema', path, d.get('schema')))
            if not d.get('schema') == cfg['schema']:
                raise ValueError(('unknown schema', path))
            if not rows[path]['sha256'] == cfg['sha256']:
                raise ValueError(('legacy content changed: review dependency adapter', path))
            for field in cfg['runtime_fields']:
                if not field in d:
                    raise ValueError(('missing required runtime field', path, field))
                refs(d[field], path + '#' + field)
        else:
            if not policy['code_pins'].get(path) == rows[path]['sha256']:
                raise ValueError(('unreviewed code dependency graph', path))
            for r in re.findall('res://[^\\s"\\\'\\)\\],;]+', f.read_text()):
                if r in PREFIXES:
                    continue
                add(r, path + ' literal')
    for r in rows.values():
        r['required_by'] = sorted(reasons[r['path']])
    return {'schema': 'earth-export-raw-allowlist-v1', 'status': 'prototype; raw bytes plus normal imported resources still required', 'files': sorted(rows.values(), key=lambda x: x['path'])}
if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('project')
    a.add_argument('--policy', default=str(P / 'policy.json'))
    a.add_argument('--out', required=True)
    args = a.parse_args()
    result = run(args.project, json.loads(pathlib.Path(args.policy).read_text()))
    pathlib.Path(args.out).write_text(json.dumps(result, indent=2) + '\n')
    print(len(result['files']), sum((x['bytes'] for x in result['files'])))
