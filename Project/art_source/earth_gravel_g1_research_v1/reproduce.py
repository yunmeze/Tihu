"""Archive replay of full-canvas mappings only; no diagnostic composition."""
from pathlib import Path
import argparse,json,hashlib
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('output');a=p.parse_args();s=Path(a.input);o=Path(a.output);o.mkdir(parents=True,exist_ok=True)
c=json.loads(Path(__file__).with_name('RECIPE.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(s/c['raw'])==c['raw_sha256']
im=Image.open(s/c['raw']);mode=c['mode'];im=im.convert('RGBA' if mode in ['premult','rgba'] else 'RGB');base=im
for i,row in enumerate(c['outputs']):
 if mode=='premult':out=base.convert('RGBa').resize(row['size'],Image.Resampling.LANCZOS).convert('RGBA')
 elif mode=='rgb_direct':out=base.resize(row['size'],Image.Resampling.LANCZOS)
 else:out=(base if i==0 else previous).resize(row['size'],Image.Resampling.LANCZOS if i==0 else Image.Resampling.BOX)
 out.save(o/row['name']);assert sha(o/row['name'])==row['sha256'];previous=out
print('PASS exact full-canvas mapping SHA; no acceptance implied')
