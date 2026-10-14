from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'.tools/python'))
from PIL import Image,ImageDraw
A=ROOT/'public/assets';m=json.loads((A/'maps/A00.json').read_text(encoding='utf8'));p=json.loads((A/'sprites/Map/Res/Building/index.json').read_text(encoding='utf8'));samples=[]
for x in range(73,86):
 for y in range(47,63):
  c=m['cells'][x*m['height']+y]
  if c[2]==4 and c[3]>0:samples.append((x,y,c[1],c[3]))
cols=8;out=Image.new('RGBA',(cols*100,((len(samples)+cols-1)//cols)*320),'#8e805e');d=ImageDraw.Draw(out)
for i,(x,y,flag,n) in enumerate(samples):
 f=p['frames'][n];sx,sy,w,h=f['rect'];im=Image.open(A/p['pages'][f['page']]['file']).crop((sx,sy,sx+w,sy+h));xx,yy=(i%cols)*100,(i//cols)*320;out.alpha_composite(im,(xx+20+f['crop'][0],yy+300-f['original'][1]+f['crop'][1]));d.text((xx+2,yy+2),f'{x},{y} flag {flag}\n#{n}',fill='white')
out.save(ROOT/'reports/building-layers.png');print(len(samples))
