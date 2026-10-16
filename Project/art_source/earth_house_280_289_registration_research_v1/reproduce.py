from pathlib import Path
import argparse,json,hashlib
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('output');a=p.parse_args();root=Path(__file__).parent;o=Path(a.output);o.mkdir(parents=True,exist_ok=True);c=json.loads((root/'ARCHIVE.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n,h in json.loads((root/'SHA256.json').read_text()).items():assert sha(root/n)==h,n
assert sha(root/'RAW.png')==c['raw_sha256'] and sha(root/'PROMPT.txt')==c['prompt_sha256']
for r in c['actual_refs']:assert sha(root/r['path'])==r['sha256']
im=Image.open(root/'RAW.png').convert('RGBA');assert im.width==im.height
s=c['locked_scale'];tx,ty=c['locked_translation']
if c['mode']=='core':
 mapped=im.resize((512,512),Image.Resampling.LANCZOS)
 registered=mapped.transform((512,512),Image.Transform.AFFINE,(1/s,0,-tx/s,0,1/s,-ty/s),Image.Resampling.BICUBIC)
else:
 mapped=im.convert('RGBa').resize((1024,1024),Image.Resampling.LANCZOS).convert('RGBA');d=im.width/512
 registered=im.convert('RGBa').transform((1024,1024),Image.Transform.AFFINE,(d/(2*s),0,-d*tx/s,0,d/(2*s),-d*ty/s),Image.Resampling.BICUBIC).convert('RGBA')
for im,name,key in [(mapped,'original-full-window.png','mapped_sha256'),(registered,'registered-research.png','registered_sha256')]:
 im.save(o/name);assert sha(o/name)==c[key],name
print('PASS original mapping and locked registration exact PNG SHA; original failure remains.')
