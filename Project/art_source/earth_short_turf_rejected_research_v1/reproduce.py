from pathlib import Path
from PIL import Image
import json,hashlib,argparse
a=argparse.ArgumentParser();a.add_argument('--output',required=True);args=a.parse_args()
H=Path(__file__).resolve().parent;P=H.parents[1];O=Path(args.output).resolve()
assert O!=P and P not in O.parents;O.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n,h in json.loads((H/'SHA256.json').read_bytes()).items():assert sha(H/n)==h,n
d=json.loads((H/'ARCHIVE.json').read_bytes());r=json.loads((H/'REQUEST_FROZEN.json').read_bytes())
assert not r['transparent_background'];assert sha(H/'PROMPT.txt')==r['prompt_sha256']
for v in r['references']:
 x=d['reference_resolution'][v['path']];assert sha(P/x['project_path'])==v['sha256']==x['sha256']
raw=Image.open(H/'RAW.png').convert('RGBA');assert raw.size==(1254,1254) and raw.getchannel('A').getextrema()==(255,255)
tile=raw.resize((768,768),Image.Resampling.LANCZOS);one=tile.resize((384,384),Image.Resampling.BOX)
for name,im in [('tile-native2x.png',tile),('tile-logical1x.png',one)]:
 im.save(O/name);assert sha(O/name)==d['expected_outputs'][name];assert Image.open(O/name).convert('RGBA').tobytes()==im.tobytes()
print('PASS exact frozen request/input bytes and raw-to768/384 mapping; rejected material, no core composition')
