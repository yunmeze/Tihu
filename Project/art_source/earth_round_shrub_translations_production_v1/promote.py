from pathlib import Path
import json,hashlib,copy
P=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent;O=P/'assets/earth/environment/round_shrub_v1';S=P/'art_source/earth_round_shrub_translations_v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n');center=json.loads((O/'registration.json').read_text());rows=[];dependencies={}
for name,expected in [('51_44','96c9ab688413d284bac1727657a1e2d3546484d85c45616bc53e75c38de187ea'),('64_45','c40590051edf6a176032581dd10a6d7b46bc00c1b78796c9250c1757c3267b30')]:
 src=S/f'registration_{name}.json';assert sha(src)==expected;r=json.loads(src.read_text());old=copy.deepcopy(r);r['raw_texture']=center['raw_texture'];r['partition']['owner_labels']=center['partition']['owner_labels']
 for o,c in zip(r['owners'],center['owners']):
  assert o['texture_sha256']==c['texture_sha256'];o['texture']=c['texture'];p=P/o['texture'][6:];assert sha(p)==o['texture_sha256'];dependencies[o['texture']]=sha(p)
 for field,h in [(r['raw_texture'],r['raw_sha256']),(r['partition']['owner_labels'],r['partition']['owner_labels_sha256'])]:assert sha(P/field[6:])==h;dependencies[field]=h
 r['status']='parent-approved ordinary bounded candidate; independent original routes and GPU reviewed; only this exact instance'
 f=O/f'registration_{name}.json';assert not f.exists();write(f,r)
 chk=copy.deepcopy(r);chk['status']=old['status'];chk['raw_texture']=old['raw_texture'];chk['partition']['owner_labels']=old['partition']['owner_labels']
 for a,b in zip(chk['owners'],old['owners']):a['texture']=b['texture']
 assert chk==old;rows.append({'path':str(f.relative_to(P.parent)),'sha256':sha(f),'bytes':f.stat().st_size,'source_registration_sha256':expected})
write(D/'PROMOTION_REPORT.json',{'registrations':rows,'shared_existing_dependencies':dependencies,'all_identity_geometry_fields_unchanged':True,'new_png_count':0,'scope':'only51,44 and64,45; independent4ownerfallback; no all-map reuse; no new shadow','runner_evidence':'1184ticks9points; left4/right3 differing pixels max1; parent reviewed both depth boards'});write(D/'MINIMAL_SHA256.json',{'file_count':4,'files':rows+[{'path':str(p.relative_to(P.parent)),'sha256':sha(p),'bytes':p.stat().st_size} for p in [D/'promote.py',D/'PROMOTION_REPORT.json']],'shared_existing_dependencies':dependencies,'exclude':'previous archives/diagnostics/logs; no duplicate PNG'});print(json.dumps(rows,indent=2));print('manifest',sha(D/'MINIMAL_SHA256.json'))
