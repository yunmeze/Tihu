from pathlib import Path
from PIL import Image
import argparse,json,hashlib
p=argparse.ArgumentParser();p.add_argument('project');p.add_argument('output');a=p.parse_args();root=Path(__file__).parent;project=Path(a.project);out=Path(a.output);out.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();c=json.loads((root/'ARCHIVE.json').read_text())
for n,h in json.loads((root/'SHA256.json').read_text()).items():assert sha(root/n)==h,n
for d in c['tracked_dependencies']:assert sha(project/d['path'])==d['sha256']
for r in c['actual_refs_order']:assert sha(root/r['path'])==r['sha256']
im=Image.open(root/'RAW.png').convert('RGBA');images={}
if c['mode']=='H':
 h=im.resize((512,512),Image.Resampling.LANCZOS);s=c['scale'];tx,ty=c['translation_HD'];hreg=h.transform((512,512),Image.Transform.AFFINE,(1/s,0,-tx/s,0,1/s,-ty/s),Image.Resampling.BICUBIC);images={'H-fullcanvas512.png':h,'H-registered512.png':hreg}
 base=project/'art_source/earth_s_core_c_registration_research_v1';cm=json.loads((base/'ARCHIVE.json').read_text());core=Image.open(base/'RAW.png').convert('RGBA').resize((512,512),Image.Resampling.LANCZOS);s=cm['locked_scale'];tx,ty=cm['locked_translation'];core=core.transform((512,512),Image.Transform.AFFINE,(1/s,0,-tx/s,0,1/s,-ty/s),Image.Resampling.BICUBIC)
 for phase,offset in c['head_offsets_HD'].items():
  shifted=Image.new('RGBA',(512,512));shifted.paste(hreg,offset);images['HC-'+phase+'.png']=Image.alpha_composite(core,shifted)
elif c['mode'] in ['P1','P2']:
 assert im.size==(1536,1024)
 for i in range(6):x=i%3*512;y=i//3*512;images[f'P-{57+i}-fixed-slot.png']=im.crop((x,y,x+512,y+512))
else:
 for d in [1,2]:images[f'fixed-fullcanvas-{d}x.png']=im.resize((384*d,384*d),Image.Resampling.BICUBIC)
for n,pic in images.items():pic.save(out/n);assert sha(out/n)==c['outputs'][n],n
print('PASS exact mapping/registered research outputs; acceptance limits unchanged')
