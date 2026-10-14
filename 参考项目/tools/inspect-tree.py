from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'.tools/python'))
from PIL import Image,ImageDraw
A=ROOT/'public/assets';p=json.loads((A/'sprites/Map/Res/Plant/index.json').read_text(encoding='utf8'));im=Image.new('RGBA',(48*6,320));d=ImageDraw.Draw(im)
for k,i in enumerate(range(16,22)):
 f=p['frames'][i];x,y,w,h=f['rect'];tile=Image.open(A/p['pages'][f['page']]['file']).crop((x,y,x+w,y+h));print(i,f['crop'],f['original'],f['rect']);im.paste(tile,(48*k+f['crop'][0],320-f['original'][1]+f['crop'][1]));
im.save(ROOT/'reports/tree-source.png')
