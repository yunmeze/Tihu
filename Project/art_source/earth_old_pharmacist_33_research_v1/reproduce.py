from pathlib import Path
from PIL import Image
import json,hashlib,argparse
a=argparse.ArgumentParser();a.add_argument('--output',required=True);args=a.parse_args()
H=Path(__file__).resolve().parent;P=H.parents[1];O=Path(args.output).resolve()
assert O!=P and P not in O.parents;O.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
for n,h in read(H/'SHA256.json').items():assert sha(H/n)==h,n
d=read(H/'ARCHIVE.json');c=read(H/'contract-before-generation.json')
for r in d['dependencies']:assert sha(P/r['path'])==r['sha256']
assert sha(H/'prompt_actual.txt')==d['prompt_sha256'];assert sha(H/'generated-raw.png')==d['raw_sha256']
for p in c['actual_refs_order']:assert sha(H/Path(p).name)==c['sha256'][p]
m=read(P/'data/maps/A13.json');source=c['source_record'];assert m['npcs'][source['record']]==source['npc']
pack=read(P/'assets/original/manifest.json')['packs']['Npc']
for r in source['frames']:assert pack['frames'][str(r['id'])]==r['metadata']
f=pack['frames']['33'];x,y,w,h=f['rect'];im=Image.open(P/pack['pages'][int(f['page'])]['file'][6:]).convert('RGBA').crop((x,y,x+w,y+h));assert hashlib.sha256(im.tobytes()).hexdigest()==f['rgba_sha256']
pad=Image.new('RGBA',(768,768));pad.alpha_composite(im.resize((448,528),Image.Resampling.NEAREST),(136,96));pad.save(O/'primary-source33-padded.png');assert sha(O/'primary-source33-padded.png')==sha(H/'primary-source33-padded.png')
for src,rect,name in [('fangzhang_v1',(113,303,179,366),'material-fang-sleeve.png'),('lingyunzi_v2',(180,304,265,390),'material-ling-fabric.png')]:
 im=Image.open(P/f'assets/earth/npc/{src}/body.png').crop(rect);im.save(O/name);assert sha(O/name)==sha(H/name)
raw=Image.open(H/'generated-raw.png').convert('RGBA');assert raw.width==raw.height
small=raw.convert('RGBa').resize((384,384),Image.Resampling.LANCZOS).convert('RGBA');body=Image.new('RGBA',(512,640));body.alpha_composite(small,(64,200));body.save(O/'candidate33-density4.png')
assert sha(O/'candidate33-density4.png')==d['expected_candidate_sha256']
assert Image.open(O/'candidate33-density4.png').convert('RGBA').tobytes()==body.tobytes()
print('PASS exact source geometry,4actual refs/prompt/raw and fixed single33 candidate; no registration correction/four-phase output')
