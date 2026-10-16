"""Fail-closed, exact 356e735 domain closure. No source writes or archive crawls."""
import pathlib,json,re,hashlib,argparse
if not __debug__:raise RuntimeError('Optimized Python disables required assertions; rerun without -O')
PARSER_SCHEMA='earth-reviewed-house-local-export-policy-v1'
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

def run(project,pol):
    if pol.get('schema')!=PARSER_SCHEMA:raise ValueError('Unknown export policy')
    P=pathlib.Path(project).resolve()
    sha=lambda b:hashlib.sha256(b).hexdigest()
    roots=pol['roots']
    rows={}; todo=[];errors=[];adapters={};ignored={};changes=[]
    SKIPS={'res://__map_load_snapshot__':'virtual map handled by read_json override','res://art_source/':'prefix validation only','res://art_source/hero_e_walk_source_r8/':'dynamic E frames separately enumerated','res://assets/':'prefix validation only'}
    
    def add(path,reason,digest=None):
     if not isinstance(path,str) or not path.startswith('res://'):raise ValueError(path)
     rel=path[6:]
     if '\\' in rel or ':' in rel or any(x in ('','.','..') for x in rel.split('/')):raise ValueError(path)
     f=P/rel
     if not f.is_file() or f.is_symlink():errors.append(['missing_or_symlink',path,reason]);return
     b=f.read_bytes();h=sha(b)
     if digest and h!=digest:errors.append(['dependency_sha',path,digest,h,reason])
     if path not in rows:
      if f.suffix not in ('.gd','.tscn','.gdshader','.tres','.png','.json') and path!='res://tools/earth/build_flat_shadow_gate.py':raise ValueError('unsupported explicit type '+path)
      rows[path]={'path':path,'sha256':h,'bytes':len(b),'type':f.suffix[1:],'required_by':[]};todo.append(path)
      if f.suffix=='.png':
       assert b[:8]==b'\x89PNG\r\n\x1a\n';rows[path].update(width=int.from_bytes(b[16:20],'big'),height=int.from_bytes(b[20:24],'big'))
     rows[path]['required_by'].append(reason)
    def refs(v,reason):
     if isinstance(v,str) and v.startswith('res://'):add(v,reason)
     elif isinstance(v,list):
      for x in v:refs(x,reason)
     elif isinstance(v,dict):
      for k,x in v.items():
       if isinstance(x,str) and re.fullmatch('[0-9a-f]{64}',x) and k.startswith(('res://','assets/','data/','scripts/','shaders/')):add(k if k.startswith('res://') else 'res://'+k,reason,x)
       else:refs(x,reason)
    def records(d,p):
     allowed_roles={'texture':'png','registration':'json','source-map':'json','source-atlas':'png','source-atlas-manifest':'json','shader':'gdshader','raw-contract':None};seen=set()
     for r in d['runtime_files']:
      assert set(r)<={'path','sha256','bytes','type','role','width','height'} and r['path'] not in seen
      seen.add(r['path']);assert r['role'] in allowed_roles and r['type'] in ('png','json','gdshader','gd')
      assert allowed_roles[r['role']] in (None,r['type']);add(r['path'],p+'#runtime_files',r['sha256'])
      actual=rows.get(r['path'],{})
      for key in ['bytes','type']+(['width','height'] if r['type']=='png' else []):
       if actual.get(key)!=r[key]:errors.append(['record_'+key,r['path'],r[key],actual.get(key)])
    for p in roots+pol['dynamic_paths']:add(p,'explicit root/dynamic E45..50')
    while todo:
     p=todo.pop(0);f=P/p[6:];b=f.read_bytes()
     if f.suffix in ('.gd','.tscn','.gdshader','.tres'):
      pass # Every code byte is checked against the frozen 289-file policy below.
      for r in re.findall(r'''res://[^\s"'\)\],;]+''',b.decode()):
       if r in SKIPS:ignored[r]=SKIPS[r];continue
       add(r,p+' literal')
     elif f.suffix=='.json':
      d=json.loads(b);schema=d.get('schema');adapters[p]={'schema':schema,'sha256':sha(b)}
      if p=='res://assets/earth/snapshot_opening/receiver_contract.json':
       assert set(d)=={'hero_se','hero_s','fangzhang','lingyunzi','first_tree','left_upright'}
       for name,c in d.items():
        assert set(c)=={'receiver_xyxy','cell_orders','source_owner_keys','source_values','caster','pins'}
        for path,h in c['pins'].items():add(path,p+'#'+name+'.pins',h)
      elif p=='res://assets/earth/house_280_289_v1/registration.json':
       assert d['schema']=='house280-isolated-shared-sampling-v1' # exact pinned schema
       assert len(d['owners'])==10 and set(d['frames'])==set(str(i) for i in range(280,290))
       for path,h in {'res://data/maps/A13.json':d['source_map_sha'],'res://assets/original/manifest.json':d['source_manifest_sha'],'res://assets/earth/house_280_289_v1/body.png':d['body_sha'],**d['atlas_pins']}.items():add(path,p+' explicit house pins',h)
      elif p=='res://assets/earth/house_280_289_v1/owner_bounds.json':
       assert d['source_registration_sha']==sha((P/'assets/earth/house_280_289_v1/registration.json').read_bytes())
       add('res://assets/earth/house_280_289_v1/ownership-id-data.png',p+' explicit mask',d['mask_sha'])
      elif p=='res://assets/earth/xuyun_static_v1/registration.json':
       for path,h in {'res://data/maps/A13.json':d['source_map_sha'],'res://assets/original/manifest.json':d['source_manifest_sha'],'res://assets/earth/xuyun_static_v1/body.png':d['body_sha'],**d['atlas_pins']}.items():add(path,p+' explicit xuyun pins',h)
      elif schema in ('earth-runtime-files-v1','earth-first-map-static-props-v1','earth-first-map-east-ground-v1','earth-first-map-plant-reuse-v1'):
       if schema in ('earth-first-map-east-ground-v1','earth-first-map-plant-reuse-v1'):expansion_dependencies(d)
       if schema=='earth-first-map-static-props-v1':
        expected={r['path']:r for g in d['groups'].values() for r in [g['master']]+g['source_dependencies']}
        assert expected=={r['path']:r for r in d['runtime_files']}
       if p=='res://assets/earth/snapshot_opening/snapshot_runtime_registration.json':
        assert len(d['runtime_files'])==154
        assert d['house_live_scope']=={'schema':'house-building-ten-frame-live-v1','pack':'Map/Res/Building','frames':list(range(280,290)),'reload_source_sha_unchanged':True,'unrelated_pack_and_mon220_independent':True,'other_global_guards_unchanged':True}
       records(d,p)
      elif schema=='lp-original-textures-r1':
       for pack in d['packs'].values():
        for page in pack['pages']:add(page['file'],p+'#packs.pages',page.get('sha256'))
      elif p=='res://data/maps/A00.json':
       assert schema=='lp-original-map-r1';add(d['texture_manifest'],p+'#texture_manifest')
      elif p=='res://data/monsters/a13-chicken.json':
       assert schema=='lp-a13-monster-pilot-v1';add(d['texture_manifest'],p+'#texture_manifest')
      elif p in {'res://data/items/catalogue.json','res://data/story/opening.json'}:
       assert schema=={'res://data/items/catalogue.json':'lp-original-item-templates-v1','res://data/story/opening.json':'original-opening-pages-v1'}[p]
      elif p in {'res://art_source/earth_hero_se_idle_v1/registration-v1.json','res://art_source/earth_hero_se_walk_v1/registration-v1.json'}:
       adapters[p]['mode']='receiver hash-only leaf; no runtime parse'
      elif p in pol['legacy']:
       cfg=pol['legacy'][p];assert schema==cfg['schema']
       if sha(b)!=cfg['sha256']:changes.append(p)
       for field in cfg['runtime_fields']:refs(d[field],p+'#'+field)
      else:raise ValueError(('unknown JSON/domain',p,schema))
    files=sorted(rows.values(),key=lambda x:x['path'])
    for f in files:f['required_by']=sorted(set(f['required_by']))
    reg='res://assets/earth/snapshot_opening/snapshot_runtime_registration.json';guard=(P/'scripts/earth/snapshot_receiver_qualification.gd').read_text();pin=re.search(r'const RUNTIME_REGISTRATION_SHA="([a-f0-9]+)"',guard).group(1)
    if pin!=rows[reg]['sha256']:errors.append(['runtime_registration_guard_pin',pin,rows[reg]['sha256']])
    report={'status':'STATIC_CANDIDATE_ONLY_NOT_PACK_VALIDATED','roots':roots,'file_count':len(files),'bytes':sum(f['bytes'] for f in files),'errors':errors,'changed_historical_consumers':sorted(changes),'adapters':adapters,'non_file_literals':ignored,'files':files}
    
    expected={r['path']:r for r in pol['files']}
    if set(rows)!=set(expected):raise ValueError(('Closure set differs from frozen policy',sorted(set(rows)^set(expected))))
    for path,row in rows.items():
     for key in ['sha256','bytes','type']+(['width','height'] if row['type']=='png' else []):
      if row.get(key)!=expected[path].get(key):raise ValueError(('Frozen input differs',path,key))
    if errors:raise ValueError(errors)
    return {'schema':'earth-export-raw-allowlist-v1','status':'exact frozen 356e735 closure; runtime verification required','files':files}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('project');p.add_argument('--out',required=True);p.add_argument('--policy',default=str(pathlib.Path(__file__).resolve().parent/'policy.json'));a=p.parse_args()
    result=run(a.project,json.loads(pathlib.Path(a.policy).read_text()))
    pathlib.Path(a.out).write_text(json.dumps(result,indent=2)+'\n');print(len(result['files']),sum(r['bytes'] for r in result['files']))
