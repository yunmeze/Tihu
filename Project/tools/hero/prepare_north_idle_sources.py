"""Prepare original N1-4 plus disconnected newly selected rear material fragments."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
R=Path(__file__).resolve().parents[2];p=R/'art_source/hero_n_idle_source_r9';p.mkdir(exist_ok=True);m=json.loads((R/'data/hero/movement.json').read_text());H=lambda b:hashlib.sha256(b).hexdigest();strip=Image.new('RGBA',(512,128));main=Image.new('RGBA',(256,88));records=[];imgs=[]
for i in range(4):
 fid=i+1;im=Image.new('RGBA',(128,128));rec={'source_id':fid,'layers':{}}
 for n in ['body','head']:
  l=m['layers'][n];f=l['frames'][str(fid)];a=Image.open(R/l['atlas'].removeprefix('res://')).convert('RGBA');x,y,w,h=f['rect'];tile=a.crop((x,y,x+w,y+h));assert H(tile.tobytes())==f['rgba_sha256'];ox,oy=f['offset'];im.alpha_composite(tile,(16+ox,64+oy));rec['layers'][n]={k:f[k] for k in ['original','offset','rgba_sha256','sourceOffset','sourceBytes']}
 im.save(p/f'source-{fid}.png');rec['composite_rgba_sha256']=H(im.tobytes());records.append(rec);imgs.append(im);strip.paste(im,(i*128,0));main.paste(im.crop((12,8,76,96)),(i*64,0))
strip.save(p/'original-four-native-strip.png');main.resize((1536,528),Image.Resampling.NEAREST).save(p/'original-four-common-crop-6x.png');pairs=[{'source_ids':[a+1,b+1],'changed_pixels':sum(x!=y for x,y in zip(imgs[a].getdata(),imgs[b].getdata()))} for a in range(4) for b in range(a+1,4)]
info={'status':'source_prepared_pending_review_no_generation','source_ids':[1,2,3,4],'direction':'N','canvas':[128,128],'root':[16,64],'crop':[12,8,76,96],'crop_root':[4,56],'source_manifest_sha256':H((R/'data/hero/movement.json').read_bytes()),'records':records,'pairwise':pairs,'frame_ticks':12,'timing_scope':'Current/reference clip only, no new EXE lifecycle proof.','transparency':'All original nonblack RGBA/checker retained, no same-color removal.'};(p/'source-provenance.json').write_text(json.dumps(info,indent=2)+'\n')
rawp=R/'art_source/hero_n_back_identity_rebuild_v1/raw-v1.png';raw=Image.open(rawp).convert('RGBA');rects={'rear_hair_only':[410,150,565,320],'scapular_plate_material':[370,375,463,529],'black_spine_material':[469,440,500,552],'wine_shoulder_shell':[275,368,350,460],'low_rear_waist_module':[420,632,526,672],'rear_fingerless_glove':[220,696,286,765],'rear_shin_material':[375,1048,423,1163],'heel_shell_material':[365,1205,444,1275]};board=Image.new('RGBA',(1000,460));dr=ImageDraw.Draw(board)
for i,(name,box) in enumerate(rects.items()):
 x=(i%4)*250;y=(i//4)*230;dr.text((x+8,y+8),name,fill='white');board.alpha_composite(raw.crop(box),(x+25,y+40))
board.save(p/'rear-identity-disconnected-fragments.png');(p/'identity-input-contract.json').write_text(json.dumps({'status':'prepared_only_no_N_animation_generation','identity_raw':str(rawp.relative_to(R)),'identity_sha256':H(rawp.read_bytes()),'crop_rectangles':rects,'pose_authority':'original-four-common-crop-6x.png only, all four actual N source poses; rear design fragments only material, no full generated back body.','design_boundary':'Selected back working identity, not recovered old concept; low waist silver band and wraparound rear red knee design residuals retained. No face/backpack/weapon/cloak/core.'},indent=2)+'\n')
print(p,pairs)
