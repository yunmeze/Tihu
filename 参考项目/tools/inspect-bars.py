from pathlib import Path
import json,sys
root=Path.cwd();sys.path.insert(0,str(root/'.tools/python'))
from PIL import Image,ImageDraw
A=root/'public/assets';out=Image.new('RGBA',(1000,520),'#352c23');d=ImageDraw.Draw(out)
for pid,indices,row in [('Data4',[6,7,8,9,51,52,53,54,55,60],0),('Item1',list(range(12)),2)]:
 p=json.loads((A/'sprites'/pid/'index.json').read_text(encoding='utf8'));pages=[Image.open(A/t['file']) for t in p['pages']]
 for j,i in enumerate(indices):
  f=p['frames'][i];sx,sy,w,h=f['rect'];im=pages[f['page']].crop((sx,sy,sx+w,sy+h));x=(j%5)*200;y=(row+j//5)*120;scale=min(160/w,85/h,3);im=im.resize((max(1,round(w*scale)),max(1,round(h*scale))),Image.Resampling.NEAREST);out.alpha_composite(im,(x+10,y+10));d.text((x+8,y+97),f'{pid} #{i}',fill='white')
out.save(root/'reports/bars-icons.png')
