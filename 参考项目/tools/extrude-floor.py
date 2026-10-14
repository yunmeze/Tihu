"""Prevent texture-atlas edge bleed without changing any tile's source pixels."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'.tools/python'))
from PIL import Image
A=ROOT/'public/assets';count=0
for name in ['FloorBig','FloorSmall']:
 p=A/'sprites/Map/Res'/name/'index.json';o=json.loads(p.read_text(encoding='utf8'));pages=[Image.open(A/page['file']).convert('RGBA') for page in o['pages']]
 for f in o['frames']:
  im=pages[f['page']];x,y,w,h=f['rect'];tile=im.crop((x,y,x+w,y+h))
  im.paste(tile.crop((0,0,1,h)),(x-1,y));im.paste(tile.crop((w-1,0,w,h)),(x+w,y));im.paste(tile.crop((0,0,w,1)),(x,y-1));im.paste(tile.crop((0,h-1,w,h)),(x,y+h))
  for dx,dy,sx,sy in [(-1,-1,0,0),(w,-1,w-1,0),(-1,h,0,h-1),(w,h,w-1,h-1)]:im.putpixel((x+dx,y+dy),tile.getpixel((sx,sy)))
  assert im.crop((x,y,x+w,y+h)).tobytes()==tile.tobytes()
  assert im.crop((x-1,y,x,y+h)).tobytes()==tile.crop((0,0,1,h)).tobytes()
  count+=1
 for page,im in zip(o['pages'],pages):im.save(A/page['file'],compress_level=6)
 o['extrudedGutter']=1;p.write_text(json.dumps(o,ensure_ascii=False,separators=(',',':')),encoding='utf8')
print(json.dumps({'tilesWithExtrudedEdges':count,'sourcePixelsChanged':0}))
