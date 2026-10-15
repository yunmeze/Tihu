from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil
P=Path(__file__).resolve().parent;S=P.parent/'hero_se_walk_source_r5';I=P.parent/'earth_hero_se_idle_v1/raw-v1.png';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((S/'SE_WALK_SOURCE_ANALYSIS.json').read_text()); canvas=Image.new('RGBA',(56*3,88*2));full=Image.new('RGBA',(128*6,128));refs=[]
for i in range(6):
 f=S/f'source-{51+i}.png';im=Image.open(f).convert('RGBA');assert hashlib.sha256(im.tobytes()).hexdigest()==a['frames'][i]['rgba_sha256'];shutil.copyfile(f,P/f.name);canvas.paste(im.crop((12,8,68,96)),(i%3*56,i//3*88));full.paste(im,(i*128,0));refs.append({'source_id':51+i,'path':f.name,'sha256':sha(f),'rgba_sha256':a['frames'][i]['rgba_sha256']})
canvas.resize((1344,1408),Image.Resampling.NEAREST).save(P/'source-six-main-8x.png');full.save(P/'source-six-native.png')
im=Image.open(I).convert('RGBA');parts={'head_face':(213,53,319,171),'chest_black_abdomen':(208,174,340,317),'red_shoulder':(137,157,220,258),'low_waist':(202,303,334,367),'black_thigh_small_side_plate':(180,352,285,466),'fingerless_glove':(119,374,183,448),'graphite_knee':(151,477,240,545),'dark_boot':(255,553,375,649)}
b=Image.new('RGBA',(800,430));d=ImageDraw.Draw(b)
for i,(name,r) in enumerate(parts.items()):
 x=i%4*200+10;y=i//4*215+30;d.text((x,y-20),name,fill='white');b.alpha_composite(im.crop(r),(x,y))
b.save(P/'idle-disconnected-design-parts.png');a['current_scope']='Earth source-only preparation, no generation authorized';a['identity_strategy']='current Earth idle13 fragments only; omit canonical elongated silver thigh armor';(P/'SOURCE_PHASE_ANALYSIS.json').write_text(json.dumps(a,indent=2)+'\n')
(P/'INPUT_PROVENANCE.json').write_text(json.dumps({'main_role':'sole pose/camera authority','source_common_crop':[12,8,68,96],'source_crop_root':[4,56],'main_grid':[3,2],'magnification':8,'logical_canvas':[128,128],'logical_root':[16,64],'source_frames':refs,'identity_raw':str(I.relative_to(P.parents[1])),'identity_raw_sha256':sha(I),'identity_crops':parts,'identity_policy':'unmodified disconnected RGBA crops; no full new person, no paired full legs; current idle outfit outranks canonical thigh design','inputs':[{'path':n,'sha256':sha(P/n)} for n in ['source-six-main-8x.png','idle-disconnected-design-parts.png']]},indent=2)+'\n')
