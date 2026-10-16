from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,argparse
a=argparse.ArgumentParser();a.add_argument('--output',required=True);args=a.parse_args()
H=Path(__file__).resolve().parent;P=H.parents[1];O=Path(args.output).resolve()
assert P!=O and P not in O.parents;O.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n,h in json.loads((H/'SHA256.json').read_bytes()).items():assert sha(H/n)==h,n
d=json.loads((H/'ARCHIVE.json').read_bytes());c=json.loads((H/'contract-before-generation.json').read_bytes())
for path in c['refs_order']:
 r=d['reference_resolution'][path];assert sha(H/r['package_path'] if 'package_path' in r else P/r['project_path'])==c['sha256'][path]
assert sha(H/'prompt_actual.txt')==d['prompt_sha256'];assert sha(H/'edit-envelope.png')==c['mask_sha256']
im=Image.open(P/d['dependencies'][0]['path']).convert('RGBA');poly=[(x*1254/832,y*1254/832) for x,y in d['editable_envelope_polygon_logical']];ImageDraw.Draw(im).line(poly+[poly[0]],fill=(255,60,150,255),width=4);im.save(O/'edit-region-guide.png')
assert sha(O/'edit-region-guide.png')==sha(H/'edit-region-guide.png')
assert im.tobytes()==Image.open(H/'edit-region-guide.png').convert('RGBA').tobytes()
print('PASS exact actual references/raw/prompt and submitted guide; no composition exists')
