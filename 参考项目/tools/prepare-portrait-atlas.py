"""Repack unchanged native HUD/font pixels; preserve source files and provenance."""
from pathlib import Path
import json,sys,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'.tools/python'))
from PIL import Image
root=Path(__file__).resolve().parent.parent/'public/assets'
index=json.loads((root/'ui/native/index.json').read_text(encoding='utf8'))
font=json.loads((root/'fonts/index.json').read_text(encoding='utf8'))
skill=json.loads((root/'sprites/Data5/index.json').read_text(encoding='utf8'))
keys=['dialog','button','button-active','tasks-0','system-0','insight-0','collection-0','progress-track','experience','target-track','target-hp']
files={index['assets'][k]['file']for k in keys}|{p['file']for p in font['pages']}|{p['file']for p in skill['pages']}
files.add('ui/resource-orbs-v1.png')
images=[(f,Image.open(root/f).convert('RGBA'))for f in sorted(files)]
images.sort(key=lambda v:(-v[1].height,-v[1].width,v[0]));width=4096;x=8;y=2;row=0;rects={}
for file,im in images:
 if x+im.width+2>width:x=2;y+=row+4;row=0
 rects[file]=dict(x=x,y=y,width=im.width,height=im.height,sha256=hashlib.sha256((root/file).read_bytes()).hexdigest())
 x+=im.width+4;row=max(row,im.height)
height=2**(y+row+2-1).bit_length();assert height<=4096
atlas=Image.new('RGBA',(width,height));atlas.paste((255,255,255,255),(0,0,6,6))
for file,im in images:
 r=rects[file];atlas.paste(im,(r['x'],r['y']))
out='ui/portrait-atlas.png';atlas.save(root/out)
data=dict(file=out,width=width,height=height,white=[1,1,2,2],regions=rects,sourcePixelsUnchanged=True)
(root/'ui/portrait-atlas.json').write_text(json.dumps(data,separators=(',',':')),encoding='utf8')
print(json.dumps(dict(file=out,width=width,height=height,images=len(images),bytes=(root/out).stat().st_size)))
