from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
P=Path(__file__).resolve().parent;A=P.parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=Image.new('RGBA',(384,256));legs=Image.new('RGBA',(3*56*8,2*48*8));recs=[]
for i in range(6):
 src=A/'earth_hero_e_input_plan_v1'/f'source-{45+i}.png';im=Image.open(src).convert('RGBA');assert im.size==(128,128);b.paste(im,(i%3*128,i//3*128));crop=im.crop((16,48,72,96));legs.paste(crop.resize((448,384),Image.Resampling.NEAREST),(i%3*448,i//3*384));recs.append({'source_id':45+i,'sha256':sha(src),'rgba_sha256':hashlib.sha256(im.tobytes()).hexdigest()})
b.resize((1536,1024),Image.Resampling.NEAREST).save(P/'source45-50-full128-equal-grid-4x.png');legs.save(P/'source45-50-common-leg-crop-8x.png')
# Approved E idle9, complete forearm garment structure in a disconnected detail; no full figure/paired legs.
im=Image.open(A/'earth_hero_e_idle_v1/raw-v1.png').convert('RGBA');parts={'E_side_head':(217,41,322,140),'E_chest_side':(268,153,330,272),'E_red_shoulder':(199,146,262,236),'E_waist_side':(240,280,330,351),'E_black_long_sleeve_silver_forearm':(186,222,256,355),'E_glove_fingers_only_skin':(193,351,265,419),'E_black_thigh':(252,402,309,461),'E_knee':(188,509,243,572),'E_boot':(189,637,310,703)}
b=Image.new('RGBA',(660,600));d=ImageDraw.Draw(b)
for i,(name,r) in enumerate(parts.items()):
 x=i%3*220+8;y=i//3*200+30;d.text((x,y-20),name,fill='white');b.alpha_composite(im.crop(r),(x,y))
b.save(P/'approved-E-idle9-design-with-forearm.png')
j={'status':'preparation_only_no_generation','source_frames':recs,'main_canvas':[1536,1024],'main_grid':[3,2],'main_native_frame':[128,128],'main_uniform_display_scale':4,'main_display_frame':[512,512],'main_display_root_per_cell':[64,256],'leg_common_crop':[16,48,72,96],'leg_uniform_display_scale':8,'identity_raw_sha256':sha(A/'earth_hero_e_idle_v1/raw-v1.png'),'identity_crop_rectangles':parts,'inputs':[{'path':p.name,'sha256':sha(p)} for p in sorted(P.glob('*.png'))],'rejected_raw_used_as_input':False};(P/'INPUT_PROVENANCE.json').write_text(json.dumps(j,indent=2)+'\n')
(P/'GIT_SAVE_MANIFEST.json').write_text(json.dumps({'status':'prepared_no_generation_no_git','files':[{'path':p.name,'sha256':sha(p)} for p in sorted(P.iterdir()) if p.is_file() and p.name!='GIT_SAVE_MANIFEST.json']},indent=2)+'\n')
