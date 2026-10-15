from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,shutil
P=Path(__file__).resolve().parent; A=P.parent
raw=A/'earth_hero_se_canonical_v1/raw-v2.png'; im=Image.open(raw).convert('RGBA')
rects={'head_identity':(440,95,640,310),'chest_black_underlayer':(415,315,645,590),'shoulder':(300,290,435,465),'low_waist':(412,590,650,708),'fingerless_hand':(270,715,393,851),'dark_shin_boot':(533,973,747,1235)}
b=Image.new('RGBA',(900,650),(0,0,0,0));d=ImageDraw.Draw(b)
for i,(name,r) in enumerate(rects.items()):
 x=(i%3)*300;y=(i//3)*325;d.text((x+8,y+5),name,fill='white');b.alpha_composite(im.crop(r),(x+20,y+32))
b.save(P/'canonical-v2-disconnected-parts.png');src=A/'earth_hero_input_plan_v1/source13-16-pose-main-6x.png';shutil.copyfile(src,P/'source13-16-pose-main-6x.png')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(P/'INPUTS.json').write_text(json.dumps({'canonical_raw':str(raw.relative_to(A.parent)),'canonical_sha256':sha(raw),'crop_rectangles':rects,'method':'unaltered RGBA technical crops, disconnected; no full person identity input','source':str(src.relative_to(A.parent)),'source_sha256':sha(src),'inputs':[{'path':p.name,'sha256':sha(p)} for p in [P/'source13-16-pose-main-6x.png',P/'canonical-v2-disconnected-parts.png']]},indent=2)+'\n')
