"""Prepare selected-only CPU replay inputs. Does not solve or invoke Godot."""
from pathlib import Path
import json,hashlib,shutil,argparse
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=Path(__file__).resolve().parent;o=a.output.resolve();assert not o.exists(),'Use a new work directory'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n,h in json.loads((r/'SHA256.json').read_text()).items():assert sha(r/n)==h,n
sources=json.loads((r/'DEPENDENCIES.json').read_text())['dependencies']
for d in sources:assert sha(a.project/d['path'])==d['sha256'],d['path']
shutil.copytree(r,o)
for d in sources:
 if d['work_path']:
  p=o/d['work_path'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(a.project/d['path'],p)
raw=Image.open(a.project/sources[-1]['path']).convert('RGBA');assert raw.size==(1024,1536);b=o/'south-walk-mesh-correction-v1/raw';b.mkdir(parents=True)
for i,phase in enumerate([57,60,58,61,62,59]):
 if phase in [58,61]:raw.crop((i%2*512,i//2*512,i%2*512+512,i//2*512+512)).save(b/f'{phase}.png')
print('PASS dependency pins and isolated58/61 data preparation;61 solve not authorized or executed')
