from pathlib import Path
from PIL import Image
import json,hashlib,argparse
P=Path(__file__).resolve().parent;a=argparse.ArgumentParser();a.add_argument('--project',type=Path,default=P.parents[1]);a.add_argument('--out',type=Path,required=True);args=a.parse_args();args.out.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for n,h in json.loads((P/'SHA256.json').read_text()).items():assert sha(P/n)==h,n
m=json.loads((P/'ARCHIVE.json').read_text());c=json.loads((P/'IDENTITY_CROP_MANIFEST.json').read_text());q=json.loads((P/'REQUEST_FROZEN.json').read_text())
for d in m['dependencies']:assert sha(args.project/d['path'])==d['sha256']
assert q['prompt']==(P/'PROMPT.txt').read_text() and q['transparent_background'] is True
for ref,name in zip(m['actual_refs'],c['reference_order']):assert sha(args.project/ref['project_path'] if 'project_path' in ref else P/ref['package_path'])==c['sha256'][name]
sheet=Image.open(args.project/'assets/earth/hero/s_idle_v1/body.png').convert('RGBA').crop((0,0,512,512));board=Image.open(P/'REF02_IDENTITY_CONSTRUCTION_V2.png').convert('RGBA')
for row in c['crops']:
 crop=sheet.crop(row['source_xyxy']);crop.save(args.out/row['file']);assert sha(args.out/row['file'])==c['sha256'][row['file']];crop=crop.resize((crop.width*2,crop.height*2),Image.Resampling.NEAREST);x,y=row['board_origin'];background=Image.new('RGBA',crop.size,(84,89,95,255));background.alpha_composite(crop);assert background.tobytes()==board.crop((x,y,x+crop.width,y+crop.height)).tobytes()
raw=Image.open(P/'RAW.png').convert('RGBA');assert raw.size==(1254,1254);assert all(raw.getpixel((x,1253))==(0,0,0,1) for x in range(237,241));im=raw.resize((512,512),Image.Resampling.LANCZOS);im.save(args.out/'display512.png');assert sha(args.out/'display512.png')==m['mapped_png_sha256'];assert hashlib.sha256(im.tobytes()).hexdigest()==m['mapped_rgba_sha256'];print('PASS actualref bytes, exact crop/board content lineage, fixedPNG/RGBA')
