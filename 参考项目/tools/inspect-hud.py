from pathlib import Path
import sys,json,math
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'.tools/python'))
from PIL import Image,ImageDraw,ImageFont
A=ROOT/'public/assets';font=ImageFont.truetype('C:/Windows/Fonts/simsun.ttc',18)
for name in ['Data'+str(i) for i in range(1,9)]:
    p=json.loads((A/'sprites'/name/'index.json').read_text(encoding='utf8'));pages=[Image.open(A/f['file']) for f in p['pages']]
    cellW,cellH=230,180;cols=5;out=Image.new('RGB',(cols*cellW,math.ceil(len(p['frames'])/cols)*cellH),'#32352f');d=ImageDraw.Draw(out)
    for i,f in enumerate(p['frames']):
        x,y=(i%cols)*cellW,(i//cols)*cellH;sx,sy,w,h=f['rect'];im=pages[f['page']].crop((sx,sy,sx+w,sy+h));im.thumbnail((220,145));out.paste(im,(x+5,y+30),im);d.text((x+5,y+5),f'{name}:{i}  {f["original"]}',font=font,fill='white')
    out.save(ROOT/'reports'/f'hud-{name}.jpg')
    print(name,len(p['frames']),[(i,f['original']) for i,f in enumerate(p['frames']) if f['original'][0]>500],flush=True)
files=sorted((A/'ui').glob('*.png'));out=Image.new('RGB',(900,math.ceil(len(files)/5)*95),'#32352f');d=ImageDraw.Draw(out)
for i,p in enumerate(files):
    x,y=(i%5)*180,(i//5)*95;im=Image.open(p);im.thumbnail((170,65));out.paste(im,(x+5,y+25),im);d.text((x+5,y),p.stem,font=font,fill='white')
out.save(ROOT/'reports/hud-buttons.jpg')
