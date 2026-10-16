"""Reproduce immutable research mappings and approved integer registrations."""
from pathlib import Path
import argparse, hashlib, json
from PIL import Image

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 root=Path(__file__).resolve().parent;c=json.loads((root/'ARCHIVE.json').read_text());a.out.mkdir(parents=True,exist_ok=True)
 for name,h in json.loads((root/'SHA256.json').read_text()).items(): assert sha(root/name)==h,name
 for dep in c['tracked_dependencies']:
  f=a.project_root/dep['path'];assert f.stat().st_size==dep['bytes'] and sha(f)==dep['sha256'],str(f)
 manifest=json.loads((a.project_root/'assets/original/manifest.json').read_text())['packs']['Npc'];e=json.loads((root/'source-evidence.json').read_text());registered={}
 for q in c['phases']:
  n=q['id'];folder=root/q['directory'];contract=json.loads((folder/'contract-before-generation.json').read_text());assert sha(folder/'prompt_actual.txt')==contract['prompt_sha256']
  for ref in q['actual_refs']: assert sha(root/ref['path'])==ref['sha256']
  source=next(v for v in e['record']['frames'] if v['id']==n);m=manifest['frames'][str(n)];assert m==source['metadata']
  page=Image.open(a.project_root/manifest['pages'][m['page']]['file'].removeprefix('res://')).convert('RGBA');x,y,w,h=m['rect'];im=page.crop((x,y,x+w,y+h));assert hashlib.sha256(im.tobytes()).hexdigest()==m['rgba_sha256']
  full=Image.new('RGBA',(96,96));full.alpha_composite(im,(12+m['offset'][0]+m['crop'][0],56+m['offset'][1]+m['crop'][1]));full=full.resize((384,384),Image.Resampling.NEAREST)
  ref=Image.open(root/q['actual_refs'][0]['path']).convert('RGBA');assert ref.size==full.size and ref.tobytes()==full.tobytes(),f'source {n}'
  raw=folder/'generated-raw.png';assert sha(raw)==q['raw_sha256'];im=Image.open(raw).convert('RGBA');assert im.size==(1254,1254)
  im=im.convert('RGBa').resize((384,384),Image.Resampling.LANCZOS).convert('RGBA');dest=a.out/f'{n}-original-mapping.png';im.save(dest);assert sha(dest)==q['mapped_sha256']
  dx,dy=q['density4_translation'];out=Image.new('RGBA',im.size);out.paste(im,(dx,dy));assert sum(v>0 for v in im.getchannel('A').getdata())==sum(v>0 for v in out.getchannel('A').getdata()),'nonzero alpha clipped'
  dest=a.out/f'{n}-registered-research.png';out.save(dest);assert sha(dest)==q['rigid_sha256'];registered[n]=out
  if n>201:
   identity=Image.open(root/q['actual_refs'][1]['path']).convert('RGBA');assert identity.tobytes()==registered[201].tobytes()
 print('PASS: four original mappings, four rigid research frames, all exact PNG SHA; actual refs and tracked source geometry verified. No runtime acceptance implied.')
if __name__=='__main__':main()
