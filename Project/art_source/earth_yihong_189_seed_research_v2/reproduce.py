from pathlib import Path
import argparse,json,hashlib
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parent;c=json.loads((root/'ARCHIVE.json').read_text())
for n,v in c['inputs'].items():
 q=root/n;assert q.stat().st_size==v['bytes'] and hashlib.sha256(q.read_bytes()).hexdigest()==v['sha256'],n
im=Image.open(root/c['raw']).convert('RGBA');a.output.mkdir(parents=True,exist_ok=True)
if c['mapping']=='npc':
 outputs={'candidate189-density4.png':im.convert('RGBa').resize((384,384),Image.Resampling.LANCZOS).convert('RGBA')}
else:
 assert im.size==(1024,1536);outputs={f'source-phase-{phase}-fixed-slot.png':im.crop((i%2*512,i//2*512,i%2*512+512,i//2*512+512)) for i,phase in enumerate([57,60,58,61,62,59])}
for n,img in outputs.items():
 q=a.output/n;img.save(q);v=c['outputs'][n];assert hashlib.sha256(q.read_bytes()).hexdigest()==v['sha256'],n;assert hashlib.sha256(img.tobytes()).hexdigest()==v['rgba_sha256'],n
print('PASS: selected source inputs and exact PNG/RGBA reproduction; no registration applied')
