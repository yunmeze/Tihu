"""Copy original HUD pixels to independently loadable, traceable textures."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'.tools/python'))
from PIL import Image
A=ROOT/'public/assets';dest=A/'ui/native';dest.mkdir(parents=True,exist_ok=True);assets={}
def export(name,pack,index):
    o=json.loads((A/'sprites'/pack/'index.json').read_text(encoding='utf8'));f=o['frames'][index];p=o['pages'][f['page']];x,y,w,h=f['rect'];src=Image.open(A/p['file']).crop((x,y,x+w,y+h));out=Image.new('RGBA',tuple(f['original']));out.paste(src,tuple(f['crop']));out.save(dest/(name+'.png'))
    assets[name]={'file':'ui/native/'+name+'.png','width':out.width,'height':out.height,'source':o['source'],'sourceSha256':o['sha256'],'frame':index,'sourceOffset':f['sourceOffset'],'sourceBytes':f['sourceBytes'],'generated':False}
for name,pack,index in [('dialog','Data1',9),('header','Data1',3),('separator','Data1',26),('logo','Data1',7),('status','Data4',1),('hp','Data4',2),('mp','Data4',3),('portrait-female','Data4',4),('portrait-male','Data4',5),('button','Data2',7),('button-active','Data2',8),('progress-track','Data4',53),('experience','Data4',60),('target-track','Data4',8),('target-hp','Data4',9)]:export(name,pack,index)
for i in range(1,79):export('skill-'+str(i),'Data5',i)
for i,name in enumerate(['character','bag','skills','tasks','insight','collection','system']):
    for state in (0,1):
        file=A/'ui'/f'Button_{i}_{state}.png';im=Image.open(file);key=f'{name}-{state}';source=f'Data/Button/Button_{i}_{state}.gif';assets[key]={'file':str(file.relative_to(A)).replace('\\','/'),'width':im.width,'height':im.height,'source':source,'sourceSha256':hashlib.sha256((ROOT/'reference/LP传奇单机版-重生v1.2.2E'/source).read_bytes()).hexdigest(),'generated':False}
if (A/'ui/portrait-panel-v1.meta.json').exists():assets['portrait-panel']=json.loads((A/'ui/portrait-panel-v1.meta.json').read_text(encoding='utf8'))
if (A/'ui/resource-orbs-v1.meta.json').exists():
    orbs=json.loads((A/'ui/resource-orbs-v1.meta.json').read_text(encoding='utf8'));orbs['width'],orbs['height']=Image.open(A/orbs['file']).size;assets['resource-orbs']=orbs
(A/'ui/native/index.json').write_text(json.dumps({'version':1,'assets':assets,'design':{'width':750,'height':1624},'adaptation':'native sprite reuse and nine-slice; labels rendered separately'},ensure_ascii=False,separators=(',',':')),encoding='utf8')
print(json.dumps({'nativeHudAssets':len(assets),'output':str(dest)},ensure_ascii=False))
