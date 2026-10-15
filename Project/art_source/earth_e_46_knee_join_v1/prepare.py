from pathlib import Path
from PIL import Image
import numpy as np,json,math,hashlib
P=Path(__file__).resolve().parent;R=P.parents[1];PL=R/'art_source/earth_e_46_leg_rigid_plan_v1';D=R/'diagnostics/earth_e_46_knee_join_v1';D.mkdir(exist_ok=True,parents=True);j=json.loads((PL/'PLAN.json').read_text());raw=Image.open(R/'art_source/earth_e_46_49_static_research_v1/46-lower-cleaned.png').convert('RGBA');a=np.array(raw);s=j['density'];t=j['existing_lower_translation'];layers={}
for nm in ['rear','main','fixed']:
 fn=f'{nm}_shin_boot-SEGMENT-PROPOSED-mask.png' if nm!='fixed' else 'fixed-upper-and-rest-PROTECT-mask.png';m=np.array(Image.open(PL/fn))>0;b=a.copy();b[~m,3]=0
 if nm=='fixed':Q=np.eye(2);tt=np.array(t)
 else:
  angle=math.radians(j['moves'][nm]['rotation_deg']);Q=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]]);tt=np.array(j['moves'][nm]['raw_to_logical_translation'])
 inv=Q.T/(4*s);off=-Q.T@tt/s;im=Image.fromarray(b).transform((512,512),Image.Transform.AFFINE,(inv[0,0],inv[0,1],off[0],inv[1,0],inv[1,1],off[1]),resample=Image.Resampling.BICUBIC);im.save(P/f'layer-{nm}-HD4.png');layers[nm]=im
lo=Image.new('RGBA',(512,512))
for nm in ['rear','main','fixed']:lo.alpha_composite(layers[nm])
lo.save(P/'rigid-lower-BEFORE-JOIN.png');full=lo.copy()
for f in [R/'diagnostics/earth_e_49_cloth_patch_v1/layer49-core-back.png',R/'art_source/earth_e_46_cloth_patch_v1/arm46-rigid-HD4.png',R/'diagnostics/earth_e_49_cloth_patch_v1/layer49-core-front.png']:full.alpha_composite(Image.open(f).convert('RGBA'))
full.save(P/'rigid46-BEFORE-JOIN.png');b=Image.new('RGBA',(512,512),(128,128,128,255));b.alpha_composite(full);b.crop((112,232,192,302)).resize((800,700),Image.Resampling.NEAREST).save(D/'actual-knee-gap-before-10x.png');full.crop((128,244,188,300)).save(P/'input-context.png');print('prepared')
