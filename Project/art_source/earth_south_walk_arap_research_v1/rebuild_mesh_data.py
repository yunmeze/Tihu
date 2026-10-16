"""Lightweight archived-NPZ -> Godot input. Does not solve ARAP or run Godot."""
from pathlib import Path
from PIL import Image
import argparse,json,hashlib,shutil,subprocess,sys
p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);p.add_argument('--output-work',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parent;out=a.output_work.resolve();assert not out.exists(),'Use a new output directory'
sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
for n,h in json.loads((root/'SHA256.json').read_text()).items():assert sha(root/n)==h,n
for v in json.loads((root/'DEPENDENCIES.json').read_text())['dependencies']:assert sha(a.project/v['path'])==v['sha256'],v['path']
shutil.copytree(root,out);b=out/'south-walk-mesh-correction-v1';(b/'raw').mkdir(exist_ok=True);(b/'baseline').mkdir(exist_ok=True)
im=Image.open(a.project/'art_source/earth_s_whole_six_fitted_redraw_research_v1/RAW.png').convert('RGBA');assert im.size==(1024,1536)
for i,phase in enumerate([57,60,58,61,62,59]):
 q=im.crop((i%2*512,i//2*512,i%2*512+512,i//2*512+512));q.save(b/f'raw/{phase}.png');shutil.copy2(a.project/f'art_source/hero_s_walk_source_r8/source-{phase}.png',b/f'raw/source-{phase}.png');s=.72;tx=(162-s*233)-s*35*(i%2);ty=62-s*41;q.transform((512,512),Image.Transform.AFFINE,(1/s,0,-tx/s,0,1/s,-ty/s),Image.Resampling.BICUBIC).save(b/f'baseline/{phase}-s0.72.png')
subprocess.run([sys.executable,str(out/'south-walk-arap-six-v1/pack_mesh.py')],check=True)
print('PASS inputs and NPZ JSON rebuild; no solver or Godot execution. Output:',out)
