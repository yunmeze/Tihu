from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'.tools/python'))
from PIL import Image,ImageChops
A=ROOT/'public/assets';count=0
for p in (A/'sprites').rglob('index.json'):
    o=json.loads(p.read_text(encoding='utf8'))
    if not o['nativeAnimation'] and not (o['id'].startswith('Map/Res/') and 'Floor' not in o['id']):continue
    for page in o['pages']:
        file=A/page['file'];im=Image.open(file).convert('RGBA');r,g,b,alpha=im.split();mask=ImageChops.lighter(ImageChops.lighter(r,g),b).point(lambda x:255 if x else 0);im.putalpha(ImageChops.multiply(alpha,mask));im.save(file,compress_level=6);count+=1
    o['colorKey']='RGB(0,0,0)';p.write_text(json.dumps(o,ensure_ascii=False,separators=(',',':')),encoding='utf8')
print(json.dumps({'normalizedAtlasPages':count,'nativeColorKey':'RGB(0,0,0)'}))
