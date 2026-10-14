from pathlib import Path
import sys,json
root=Path.cwd();sys.path.insert(0,str(root/'.tools/python'))
from PIL import Image,ImageDraw
A=root/'public/assets';rows=[('Hero/1',1,4),('Hero/1',33,6),('Hero/1',81,6),('Hero/1',129,6),('Hero/1',177,6),('Hero/1',225,3),('Hero/1',249,4),('Mon/4',81,6),('Mon/4',129,10),('Mon/4',209,1)];out=Image.new('RGBA',(900,len(rows)*120),'#48483e');d=ImageDraw.Draw(out)
for row,(pid,start,count) in enumerate(rows):
 p=json.loads((A/'sprites'/pid/'index.json').read_text(encoding='utf8'));pages=[Image.open(A/t['file']) for t in p['pages']];d.text((1,row*120),f'{pid} {start}',fill='white')
 for phase in range(count):
  i=start+4*count+phase;f=p['frames'][i];sx,sy,w,h=f['rect'];im=pages[f['page']].crop((sx,sy,sx+w,sy+h));x=phase*86+10;y=row*120+86;out.alpha_composite(im,(x+f['offset'][0]+f['crop'][0],y+f['offset'][1]+f['crop'][1]));d.text((phase*86+4,row*120+102),str(i),fill='white')
out.save(root/'reports/action-sequences.png')
