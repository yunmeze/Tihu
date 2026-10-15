"""Reproducible NE source-only preparation; does not generate or alter art."""
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib,json
R=Path(__file__).resolve().parents[2]
p=R/'art_source/hero_ne_source_r10';p.mkdir(exist_ok=True)
d=R/'diagnostics/hero/northeast-source-r10';d.mkdir(parents=True,exist_ok=True)
m=json.loads((R/'data/hero/movement.json').read_text());H=lambda b:hashlib.sha256(b).hexdigest()
at={n:Image.open(R/l['atlas'].removeprefix('res://')).convert('RGBA') for n,l in m['layers'].items()}
for action,ids,ticks,cols in [('idle',list(range(5,9)),12,4),('walk',list(range(39,45)),7,3)]:
 records=[];images=[];rows=(len(ids)+cols-1)//cols
 full=Image.new('RGBA',(128*cols,128*rows));crop=Image.new('RGBA',(64*cols,88*rows))
 grid=Image.new('RGB',(512*cols,560*rows),(78,78,78));dr=ImageDraw.Draw(grid)
 for j,fid in enumerate(ids):
  im=Image.new('RGBA',(128,128));rec={'source_id':fid,'layers':{}}
  for n in ['body','head']:
   f=m['layers'][n]['frames'][str(fid)];x,y,w,h=f['rect'];tile=at[n].crop((x,y,x+w,y+h));assert H(tile.tobytes())==f['rgba_sha256'];ox,oy=f['offset'];im.alpha_composite(tile,(16+ox,64+oy));rec['layers'][n]={k:f[k] for k in ['original','offset','rgba_sha256','sourceOffset','sourceBytes']}
  im.save(p/f'source-{fid}.png');rec['composite_rgba_sha256']=H(im.tobytes());records.append(rec);images.append(im)
  x=j%cols;y=j//cols;full.paste(im,(128*x,128*y));crop.paste(im.crop((12,8,76,96)),(64*x,88*y));tile=im.resize((512,512),Image.Resampling.NEAREST);grid.paste(tile,(512*x,560*y+32),tile);dr.text((512*x+8,560*y+8),str(fid),fill='white')
 full.save(p/f'{action}-full-native.png');crop.resize((cols*512,rows*704),Image.Resampling.NEAREST).save(p/f'{action}-source-main-8x.png');grid.save(d/f'{action}-all-source.jpg')
 pairs=[{'ids':[ids[a],ids[b]],'changed_pixels':sum(x!=y for x,y in zip(images[a].getdata(),images[b].getdata()))} for a in range(len(ids)) for b in range(a+1,len(ids))]
 info={'status':'prepared_source_only_not_generated','direction':'NE','action':action,'source_ids':ids,'canvas':[128,128],'root':[16,64],'common_crop':[12,8,76,96],'crop_root':[4,56],'frame_ticks':ticks,'timing_scope':'Current/reference clip, not movement speed or EXE lifecycle proof.','transparency':'Original RGBA, including checker and all nonblack colors, retained.','source_manifest_sha256':H((R/'data/hero/movement.json').read_bytes()),'records':records,'pairwise':pairs}
 (p/f'{action}-provenance.json').write_text(json.dumps(info,indent=2)+'\n')
print(p)
