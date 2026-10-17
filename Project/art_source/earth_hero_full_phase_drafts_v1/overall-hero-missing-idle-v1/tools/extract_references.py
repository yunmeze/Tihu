from PIL import Image
from pathlib import Path
import json,hashlib,shutil
root=Path('/workspace/scratch/22c897619190'); p=root/'tihu-legend-recovered/Project'; out=root/'legend-recovery-resume-20261017-0632/overall-hero-missing-idle-v1'; src=p/'data/hero/movement.json'; d=json.loads(src.read_text()); sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
contract={'origin':[-16,-64],'logical_canvas':[128,128],'actor_origin_in_canvas':[16,64],'reference_density':4,'draw_order':d['draw_order'],'placement':d['placement'],'anchor':d['anchor'],'sources':{'movement':{'path':str(src),'sha256':sha(src)}},'directions':{}}
for lname in ['body','head']:
 f=p/d['layers'][lname]['atlas'][6:]; contract['sources'][lname]={'path':str(f),'sha256':sha(f),'original_pack_sha256':d['layers'][lname]['source_sha256']};shutil.copy2(f,out/'inputs'/f.name)
for direction, ids in [('N',range(1,5)),('NE',range(5,9))]:
 sheet=Image.new('RGBA',(1024,1024)); rows=[]
 for phase,n in enumerate(ids):
  canvas=Image.new('RGBA',(128,128)); row={'phase':phase,'frame_id':n,'layers':{}}
  for lname in ['body','head']:
   f=d['layers'][lname]['frames'][str(n)]; atlas=Image.open(p/d['layers'][lname]['atlas'][6:]); x,y,w,h=f['rect']; crop=atlas.crop((x,y,x+w,y+h)); assert crop.size==tuple(f['original']); off=f['offset'];canvas.alpha_composite(crop,(16+off[0],64+off[1]));row['layers'][lname]=f
  row['composite_bbox']=canvas.getbbox();row['rgba_sha256']=hashlib.sha256(canvas.tobytes()).hexdigest(); canvas.save(out/'inputs'/f'{direction}-{n:03}-original-composite.png');sheet.alpha_composite(canvas.resize((512,512),Image.Resampling.NEAREST),((phase%2)*512,(phase//2)*512));rows.append(row)
 sheet.save(out/'inputs'/f'{direction}-original-fourphase-2x2.png');contract['directions'][direction]=rows
for direction in ['s','e','se']:
 f=p/f'assets/earth/hero/{direction}_idle_v1/body.png';im=Image.open(f);im.crop((0,0,512,512)).save(out/'inputs'/f'{direction.upper()}-HD-identity-phase0.png');contract['sources'][direction+'-HD-identity']={'path':str(f),'sha256':sha(f)}
shutil.copy2(src,out/'provenance/original-movement.json');(out/'provenance/original-reference-contract.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2));print(out)
