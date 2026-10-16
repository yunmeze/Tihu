from pathlib import Path
from PIL import Image
import json,hashlib,argparse
p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=Path(__file__).resolve().parent;c=json.loads((r/'ARCHIVE.json').read_text());sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
for n,v in c['inputs'].items():assert sha(r/n)==v['sha256'],n
for d in c['tracked_dependencies']:assert sha(a.project/d['path'])==d['sha256'],d['path']
raw=Image.open(r/'RAW.png').convert('RGBA');assert raw.size==(1536,1024)
audit=json.loads((r/'AUDIT.json').read_text());ap=json.loads((r/'limited-assembly/APPLIED_DIAGNOSTIC.json').read_text());s=ap['scale'];assets={};outputs={}
for row in audit['slots']:
 n=row['asset']
 if n not in ap['translations_HD']:continue
 i=row['slot'];im=raw.crop((i%3*512,i//3*512,i%3*512+512,i//3*512+512));tx,ty=ap['translations_HD'][n];assets[n]=im.transform((512,512),Image.Transform.AFFINE,(1/s,0,-tx/s,0,1/s,-ty/s),Image.Resampling.BICUBIC);outputs[n+'_REGISTERED_DIAGNOSTIC_512.png']=assets[n]
for label,package in [('C','earth_s_core_c_registration_research_v1'),('H','earth_s_head_hc_registration_research_v1')]:
 d=a.project/'art_source'/package;m=json.loads((d/'ARCHIVE.json').read_text());im=Image.open(d/'RAW.png').convert('RGBA').resize((512,512),Image.Resampling.LANCZOS);s=m['locked_scale'] if label=='C' else m['scale'];tx,ty=m['locked_translation'] if label=='C' else m['translation_HD'];assets[label]=im.transform((512,512),Image.Transform.AFFINE,(1/s,0,-tx/s,0,1/s,-ty/s),Image.Resampling.BICUBIC)
for phase in [59,62]:
 im=Image.new('RGBA',(512,512))
 for n in ['L'+str(phase),'R'+str(phase),'HIP','C','H']:im=Image.alpha_composite(im,assets[n])
 outputs[f'ASSEMBLY_{phase}_512.png']=im
a.output.mkdir(parents=True,exist_ok=True)
for n,im in outputs.items():im.save(a.output/n);assert sha(a.output/n)==c['outputs'][n],n
print('PASS exact seven research outputs; original and assembly failures retained')
