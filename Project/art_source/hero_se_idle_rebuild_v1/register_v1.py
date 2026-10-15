from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent
names=['crown_surface','neck_surface','sternum_armor_proxy','pelvis_clothing_proxy','screen_left_boot_tip','screen_right_boot_tip']
source=np.array([[[40,15],[42,27],[43,38],[43,54],[36,86],[52,81]],[[40,15],[42,27],[43,38],[43,54],[36,86],[52,81]],[[40,15],[42,28],[43,38],[43,54],[36,86],[52,81]],[[40,15],[43,27],[44,38],[44,54],[37,86],[53,81]]],float)
candidate=np.array([[[320,40],[315,155],[334,232],[320,382],[267,683],[414,613]],[[311,40],[309,155],[328,232],[313,382],[260,683],[407,613]],[[307,44],[310,162],[328,232],[310,382],[257,683],[403,613]],[[299,38],[303,155],[321,232],[307,382],[251,683],[398,613]]],float)
w=np.array([1,.6,.5,.5,1,1]);cm=(candidate*w[None,:,None]).sum(1)/w.sum();sm=(source*w[None,:,None]).sum(1)/w.sum();a=candidate-cm[:,None,:];b=source-sm[:,None,:];scale=float((a*b*w[None,:,None]).sum()/(a*a*w[None,:,None]).sum());translations=sm-scale*cm
raw=Image.open(P/'raw-v1.png').convert('RGBA');atlas=Image.new('RGBA',(512,128));rebuild=Image.new('RGBA',raw.size);records=[]
for i in range(4):
 cell=raw.crop((543*i,0,543*(i+1),724));rebuild.paste(cell,(543*i,0));tx,ty=translations[i]
 registered=cell.transform((128,128),Image.Transform.AFFINE,(1/scale,0,-tx/scale,0,1/scale,-ty/scale),resample=Image.Resampling.BICUBIC);atlas.paste(registered,(128*i,0));registered.save(P/f'v1-registered-{13+i}.png')
 pts=scale*candidate[i]+translations[i];records.append({'source_id':13+i,'translation':translations[i].tolist(),'source_points':dict(zip(names,source[i].tolist())),'candidate_raw_points':dict(zip(names,candidate[i].tolist())),'mapped_points':dict(zip(names,pts.tolist())),'residuals':dict(zip(names,(pts-source[i]).tolist())),'weighted_rms':float(np.sqrt((((pts-source[i])**2).sum(1)*w).sum()/w.sum()))})
assert rebuild.tobytes()==raw.tobytes()
atlas.save(P/'v1-registered-atlas-128.png');gray=Image.new('RGBA',(512,256),(100,100,100,255));gray.alpha_composite(Image.open(P/'source-13-16-native-strip.png'),(0,0));gray.alpha_composite(atlas,(0,128));gray.resize((1536,768),Image.Resampling.NEAREST).convert('RGB').save(P/'v1-source-registered-3x-gray.jpg',quality=95)
sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
m={'status':'candidate_pending_native_validation','source_ids':[13,14,15,16],'atlas':'v1-registered-atlas-128.png','atlas_sha256':sha(P/'v1-registered-atlas-128.png'),'raw_sha256':sha(P/'raw-v1.png'),'frame_size':[128,128],'grid':[4,1],'native_draw_origin_in_cell':[16,64],'frame_ticks':12,'common_uniform_scale':scale,'no_per_frame_scale':True,'registration_method':'weighted common uniform scale and per-frame rigid translation; no rotation or deformation','weights':dict(zip(names,w.tolist())),'measurement_uncertainty':{'source_crown_and_boot_tips_px':1,'source_neck_sternum_pelvis_surface_proxy_px':3,'candidate_manual_raw_px':6},'exact_raw_rectangle_rebuild':True,'shadow':'none in generated asset; needs separate single-shadow review','records':records,'limitations':['manual surface/clothing points are not physical joints','source checker retained only in comparison','root position is shared native drawing origin, not inferred ground contact','material and pose remain reconstruction candidates pending native review']}
(P/'v1-registration.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'scale':scale,'rms':[r['weighted_rms'] for r in records],'atlas_sha256':m['atlas_sha256']},indent=2))
