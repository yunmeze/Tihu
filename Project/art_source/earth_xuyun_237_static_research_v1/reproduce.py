from pathlib import Path
from PIL import Image
import argparse,json,hashlib
a=argparse.ArgumentParser();a.add_argument('--output',required=True);args=a.parse_args()
H=Path(__file__).resolve().parent;P=H.parents[1];O=Path(args.output).resolve();assert O!=P and P not in O.parents;O.mkdir(parents=True,exist_ok=False)
read=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n,h in read(H/'SHA256.json').items():assert sha(H/n)==h,n
d=read(H/'ARCHIVE.json')
for r in d['dependencies']:assert sha(P/r['path'])==r['sha256']
source=read(H/'attempt1/contract-before-generation.json')['record'];m=read(P/'data/maps/A13.json');assert m['npcs'][source['record']]==source['npc']
pack=read(P/'assets/original/manifest.json')['packs']['Npc'];eq=read(H/'four-id-equivalence.json');pixels=[]
for rec in source['frames']:
 f=pack['frames'][str(rec['id'])];assert f==rec['metadata'];x,y,w,h=f['rect'];im=Image.open(P/pack['pages'][int(f['page'])]['file'][6:]).convert('RGBA').crop((x,y,x+w,y+h));r=next(e for e in eq if e['id']==rec['id'])
 assert hashlib.sha256(im.tobytes()).hexdigest()==r['rgba_sha256']==f['rgba_sha256']
 assert f['offset']==r['offset']==[-1,-23] and f['crop']==r['crop']==[0,0] and list(im.size)==r['size']==f['original']==r['original']==[48,53]
 im.save(O/('source-'+str(rec['id'])+'.png'));assert sha(O/('source-'+str(rec['id'])+'.png'))==r['png_sha256'];pixels.append(im.tobytes())
assert len(set(pixels))==1
im=Image.open(O/'source-237.png').convert('RGBA');pad=Image.new('RGBA',(640,640));pad.alpha_composite(im.resize((384,424),Image.Resampling.NEAREST),(120,104));pad.save(O/'primary-source237-padded.png');assert sha(O/'primary-source237-padded.png')==sha(H/'references/primary-source237-padded.png')
Image.open(P/'assets/earth/npc/lingyunzi_v2/body.png').crop((180,304,265,390)).save(O/'material-only-fabric.png');assert sha(O/'material-only-fabric.png')==sha(H/'references/material-only-fabric.png')
for stage in ['attempt1','attempt2']:
 c=read(H/stage/'contract-before-generation.json');record=d['attempts'][stage]
 assert sha(H/stage/'prompt_actual.txt')==record['prompt_sha256'];assert sha(H/stage/'generated-raw.png')==record['raw_sha256']
 for path in c['actual_refs_order']:
  r=d['reference_resolution'][path];assert sha(H/r['package_path'])==c['sha256'][path]==r['sha256']
 raw=Image.open(H/stage/'generated-raw.png').convert('RGBA');assert raw.width==raw.height
 small=raw.convert('RGBa').resize((320,320),Image.Resampling.LANCZOS).convert('RGBA');body=Image.new('RGBA',(512,640));body.alpha_composite(small,(64,272));f=O/(stage+'-candidate237-density4.png');body.save(f);assert sha(f)==record['candidate_density4_sha256'];assert Image.open(f).convert('RGBA').tobytes()==body.tobytes()
print('PASS exact source4-ID equivalence/input bytes and both fixed fullcanvas candidate mappings; research only')
