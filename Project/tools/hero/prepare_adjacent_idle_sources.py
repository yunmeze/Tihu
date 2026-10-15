"""Read original movement atlases; prepare complete adjacent idle pose references.
No generated characters or runtime assets are changed. Exact nonblack RGBA retained.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/'art_source';M=ROOT/'data/hero/movement.json';m=json.loads(M.read_text());H=lambda b:hashlib.sha256(b).hexdigest()
for direction,ids in [('E',range(9,13)),('S',range(17,21))]:
 p=ART/f'hero_{direction.lower()}_idle_source_r7';p.mkdir(exist_ok=True);strip=Image.new('RGBA',(512,128));main=Image.new('RGBA',(256,88));records=[]
 for i,fid in enumerate(ids):
  composite=Image.new('RGBA',(128,128));record={'source_id':fid,'layers':{}}
  for layer in ['body','head']:
   d=m['layers'][layer];f=d['frames'][str(fid)];at=Image.open(ROOT/d['atlas'].removeprefix('res://')).convert('RGBA');x,y,w,h=f['rect'];im=at.crop((x,y,x+w,y+h));assert H(im.tobytes())==f['rgba_sha256'];ox,oy=f['offset'];composite.alpha_composite(im,(16+ox,64+oy));record['layers'][layer]={k:f[k] for k in ['original','offset','rgba_sha256','sourceOffset','sourceBytes']}
  composite.save(p/f'source-{fid}.png');record['composite_rgba_sha256']=H(composite.tobytes());record['composite_file_sha256']=H((p/f'source-{fid}.png').read_bytes());records.append(record);strip.paste(composite,(i*128,0));main.paste(composite.crop((12,8,76,96)),(i*64,0))
 strip.save(p/'original-four-native-strip.png');main.resize((1536,528),Image.Resampling.NEAREST).save(p/'original-four-common-crop-6x.png');pairs=[]
 for a in range(4):
  for b in range(a+1,4):
   ia=Image.open(p/f'source-{list(ids)[a]}.png');ib=Image.open(p/f'source-{list(ids)[b]}.png');pairs.append({'source_ids':[list(ids)[a],list(ids)[b]],'identical_rgba':ia.tobytes()==ib.tobytes(),'changed_pixel_count':sum(aa!=bb for aa,bb in zip(ia.getdata(),ib.getdata()))})
 info={'status':'original_source_only_no_generation','direction':direction,'source_ids':list(ids),'canvas':[128,128],'native_draw_origin':[16,64],'reference_common_crop':[12,8,76,96],'cropped_native_origin':[4,56],'magnification':6,'frame_ticks':12,'timing_scope':'reference/current clip cadence, not independently proven original EXE transition lifecycle','original_manifest_sha256':H(M.read_bytes()),'records':records,'pairwise_composite_comparison':pairs,'transparency':'exactblack already transparent in audited original atlas; no additional color removal, checker and darkbody/head retained'}
 (p/'source-provenance.json').write_text(json.dumps(info,indent=2)+'\n')
print('Prepared E9-12 and S17-20 exact source composites.')
