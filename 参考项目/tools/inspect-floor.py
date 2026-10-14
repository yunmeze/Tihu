from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'.tools/python'))
from PIL import Image,ImageDraw
A=ROOT/'public/assets';o=json.loads((A/'sprites/Map/Res/FloorBig/index.json').read_text(encoding='utf8'));m=json.loads((A/'maps/A02.json').read_text(encoding='utf8'));ids=[]
for x in range(80,90):
 for y in range(46,57):
  n=m['cells'][x*m['height']+y][0]
  if n<0 and abs(n) not in ids:ids.append(abs(n))
out=Image.new('RGB',(600,((len(ids)+3)//4)*160),'#222222');d=ImageDraw.Draw(out)
for i,n in enumerate(ids):
 f=o['frames'][n];p=o['pages'][f['page']];x,y,w,h=f['rect'];im=Image.open(A/p['file']).crop((x,y,x+w,y+h));px,py=(i%4)*150,(i//4)*160;out.paste(im.resize((144,96)),(px,py+30));d.text((px,py),f'{n}: {f["original"]}',fill='white')
out.save(ROOT/'reports/floor-inspection.png');print(ids)
