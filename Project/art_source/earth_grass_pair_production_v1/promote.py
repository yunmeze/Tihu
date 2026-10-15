from pathlib import Path
import json,hashlib,copy,shutil
P=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent;S=P/'art_source/earth_grass_pair_registration_v1';O=P/'assets/earth/environment/grass_pair_v1';O.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n');rows=[];copied={}
def cp(src,dst):
 dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert sha(dst)==sha(src)
 else:shutil.copyfile(src,dst)
 assert sha(dst)==sha(src);copied[str(dst.relative_to(P.parent))]={'path':str(dst.relative_to(P.parent)),'source':str(src.relative_to(P.parent)),'sha256':sha(dst),'bytes':dst.stat().st_size}
for name,expected in [('A','34103290a132f5e46ed131ce27ee1c66c79559bd0090c4c85b3a2fcad1594ac9'),('B','8d6e7928ae110ab1e994234ffd03d5c5f3a0ab947cc542571c17a83d313266b5')]:
 src=S/f'registration_{name}.json';assert sha(src)==expected;r=json.loads(src.read_text());old=copy.deepcopy(r)
 for key,dest in [('raw_texture',O/f'whole_{name}.png'),('original_sheet_texture',O/'raw.png')]:cp(P/r[key][6:],dest);r[key]='res://'+str(dest.relative_to(P))
 for o in r['owners']:
  dest=O/'owners'/Path(o['texture']).name;cp(P/o['texture'][6:],dest);o['texture']='res://'+str(dest.relative_to(P));assert sha(dest)==o['texture_sha256']
 r['status']='parent-approved ordinary bounded candidate; exact current instance only; original native routes/GPU reviewed'
 f=O/f'registration_{name}.json';assert not f.exists();write(f,r)
 check=copy.deepcopy(r)
 for key in ['status','raw_texture','original_sheet_texture']:check[key]=old[key]
 for a,b in zip(check['owners'],old['owners']):a['texture']=b['texture']
 assert check==old;rows.append({'path':str(f.relative_to(P.parent)),'sha256':sha(f),'bytes':f.stat().st_size,'source_registration_sha256':expected})
write(D/'PROMOTION_REPORT.json',{'registrations':rows,'same_sha_copies':list(copied.values()),'unchanged_identity_geometry_fields_verified':True,'scope':'only239–240@54,30 and241–242@54,31; independent2ownerfallback','density':21,'shadow':'none; original checker replaced with full original owner group','runner_evidence':'Both GPU whole/full true2x0differentpixels; original A*54,29→30→31→32 two rounds640ticks; failure/recovery passed; parent reviewed both depth boards','secondary_visual_review':'Viewed A/B depth boards; source/new rows compare each group independently. Other unselected source clump visible in each individual test is not claimed remade in that test.','freeze':'all new generation paused pending joint checker review and new shadow plan','stage54_manifest_sha256':sha(P/'art_source/earth_vegetation_stage_archive_v2/MINIMAL_SHA256.json')})
files=rows+list(copied.values())+[{'path':str(p.relative_to(P.parent)),'sha256':sha(p),'bytes':p.stat().st_size} for p in [D/'promote.py',D/'PROMOTION_REPORT.json']];write(D/'MINIMAL_SHA256.json',{'file_count':len(files),'total_bytes':sum(f['bytes'] for f in files),'files':files,'exclude':'diagnostics/logs; prior frozen files unchanged'});print(json.dumps(rows,indent=2));print(len(files),sum(f['bytes'] for f in files),sha(D/'MINIMAL_SHA256.json'))
