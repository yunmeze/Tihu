from pathlib import Path
import json,hashlib,shutil,copy
P=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent;S=P/'art_source/earth_upright_tree_registration_v1';O=P/'assets/earth/environment/upright_tree_v1';O.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
report=[];copied={}
def cp(src,dst):
 dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert sha(dst)==sha(src)
 else:shutil.copyfile(src,dst)
 assert sha(dst)==sha(src);copied[str(dst.relative_to(P.parent))]={'path':str(dst.relative_to(P.parent)),'source':str(src.relative_to(P.parent)),'sha256':sha(dst),'bytes':dst.stat().st_size}
for name,expected in [('left_50_41','0a2a6846f51b3dc31b5c9795c91c0aafd0a77f581b5297e411452376c663b0c2'),('bottom_61_51','e9257db54ef10dde4d783e5eec1b99466e52497a5e81b1e342898e406d1bcf70')]:
 src=S/f'registration_{name}.json';assert sha(src)==expected;r=json.loads(src.read_text());old=copy.deepcopy(r)
 cp(P/r['raw_texture'][6:],O/'raw.png');r['raw_texture']='res://'+str((O/'raw.png').relative_to(P))
 cp(P/r['partition']['owner_labels'][6:],O/'owner-labels.png');r['partition']['owner_labels']='res://'+str((O/'owner-labels.png').relative_to(P))
 for o in r['owners']:
  source=P/o['texture'][6:];dest=O/'owners'/source.name;cp(source,dest);o['texture']='res://'+str(dest.relative_to(P))
 r['status']='parent-approved ordinary bounded candidate; independent native GPU/routes reviewed; only specified two instances'
 f=O/f'registration_{name}.json';write(f,r)
 # Every non-path/status field is identical to the source registration.
 check=copy.deepcopy(r);check['status']=old['status'];check['raw_texture']=old['raw_texture'];check['partition']['owner_labels']=old['partition']['owner_labels']
 for a,b in zip(check['owners'],old['owners']):a['texture']=b['texture']
 assert check==old
 report.append({'instance':name,'registration':'res://'+str(f.relative_to(P)),'sha256':sha(f),'source_registration_sha256':expected})
files=sorted(list(O.glob('*.json'))+list(O.glob('*.png'))+list((O/'owners').glob('*.png')));write(D/'PRODUCTION_SHA256.json',{'file_count':len(files),'total_bytes':sum(p.stat().st_size for p in files),'files':[{'path':str(p.relative_to(P.parent)),'sha256':sha(p),'bytes':p.stat().st_size} for p in files]});write(D/'PROMOTION_REPORT.json',{'scope':'only50,41 and61,51; no same-ID mapwide replacement','registrations':report,'same_sha_copies':list(copied.values()),'unchanged_fields_verified':True,'shared_scale':2/9,'world_delta':[528,320],'owner304':'explicit empty identity suppresses original shadow; no new shadow','gpu_evidence_reported_by_runner':{'left_different_pixels':38,'bottom_different_pixels':39,'max_channel_difference':2,'original_route_ticks':1184,'additional_front_ticks':672},'visual_review':'Viewed both depth-detail boards and clear-front-detail. Rear foliage/trunk-front relation preserved. Other source tree at61,56 and source grass over boots at64,56 remain; not claimed unobstructed.','frozen_stage54_manifest_sha256':sha(P/'art_source/earth_vegetation_stage_archive_v2/MINIMAL_SHA256.json')});print(json.dumps(report,indent=2));print('production manifest',sha(D/'PRODUCTION_SHA256.json'))
