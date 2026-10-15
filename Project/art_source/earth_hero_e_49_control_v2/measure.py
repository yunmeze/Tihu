from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[1];D=R/'diagnostics/earth_hero_e_49_control_v2';D.mkdir(exist_ok=True,parents=True);im=Image.open(P/'raw.png').convert('RGBA')
raw=np.array([[393,158],[306,802],[479,759],[389,548]],float);src=np.array([[39,16],[31,83],[48,77],[43,56]],float);a=raw[1:3,1]-raw[0,1];b=src[1:3,1]-src[0,1];s=float((a*b).sum()/(a*a).sum());t=src[0]-s*raw[0];k=4*s
out=im.transform((512,512),Image.Transform.AFFINE,(1/k,0,-t[0]/s,0,1/k,-t[1]/s),resample=Image.Resampling.BICUBIC);out.save(P/'single49-HD4-CONTROL-ONLY.png')
regions={'left_ankle_surface':[269,738,292,768],'right_ankle_surface':[391,714,427,741],'left_toe_surface':[294,792,318,813],'right_toe_surface':[464,747,494,771],'left_heel_contour':[228,725,257,755],'right_heel_contour':[375,749,405,773]}
mapped={name:[r[0]*s+t[0],r[1]*s+t[1],r[2]*s+t[0],r[3]*s+t[1]] for name,r in regions.items()}
j={'status':'single49_control_pending_parent_review_not_animation','raw_sha256':hashlib.sha256((P/'raw.png').read_bytes()).hexdigest(),'common_uniform_scale':s,'translation':t.tolist(),'fit':'crown-to-two toe-region centers vertical spans, single scale, crown translation; no body/local warp or independent fit','point_order':['crown_surface','left_toe_region_center','right_toe_region_center','near_hand_group'],'raw_points':raw.tolist(),'source_points':src.tolist(),'mapped_points':(raw*s+t).tolist(),'boot_delta':((raw[2]-raw[1])*s).tolist(),'hand_dx_from_crown':float((raw[3,0]-raw[0,0])*s),'raw_surface_regions':regions,'mapped_surface_regions':mapped,'source_surface_regions':{'left_ankle':[24,74,28,78],'right_ankle':[38,73,42,77],'left_toe':[29,81,33,85],'right_toe':[46,75,50,79],'left_heel':None,'right_heel':None},'limits':['source heel not reliably separable into independent region; null, not fabricated','all regions are manually read clothing/boot surfaces, not joints or contact','source toes +/-2, ankles +/-3, raw regions approximate +/-8px','scale uses toe y so y residual is not independent validation','single pose cannot establish shared six-frame scale, timing or cycle']}
(P/'MEASUREMENTS.json').write_text(json.dumps(j,indent=2)+'\n')
srcim=Image.open(P.parent/'earth_hero_e_input_plan_v1/source-49.png').convert('RGBA');idle=Image.open(P.parent/'earth_hero_e_idle_v1/body-density4.png').crop((0,0,512,512)).convert('RGBA')
for factor in [1,2]:
 z=128*factor;b=Image.new('RGBA',(z*3,z),(64,68,72,255))
 for i,tile in enumerate([srcim.resize((z,z),Image.Resampling.NEAREST),out.resize((z,z),Image.Resampling.LANCZOS),idle.resize((z,z),Image.Resampling.LANCZOS)]):b.alpha_composite(tile,(i*z,0))
 b.save(D/f'source-single49-idle-true-{factor}x.png')
b=Image.new('RGBA',(256*3,256))
for i,c in enumerate([(64,68,72,255),(18,20,23,255),(220,222,224,255)]):
 panel=Image.new('RGBA',(256,256),c);panel.alpha_composite(out.resize((256,256),Image.Resampling.LANCZOS));b.paste(panel,(256*i,0))
b.save(D/'three-background-true2x.png')
print(json.dumps({'scale':s,'toe_delta':j['boot_delta'],'hand_dx':j['hand_dx_from_crown'],'regions':mapped}))
