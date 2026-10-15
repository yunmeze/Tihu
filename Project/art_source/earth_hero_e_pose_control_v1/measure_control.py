from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[1];D=R/'diagnostics/earth_hero_e_pose_control_v1';D.mkdir(parents=True,exist_ok=True);im=Image.open(P/'raw-v1.png').convert('RGBA');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
raw=np.array([[[485,44],[315,789],[701,804],[330,487]],[[486,51],[370,813],[662,780],[543,491]]],float)
source=np.array([[[40,16],[29,78],[60,81],[33,57]],[[39,16],[31,83],[48,77],[43,56]]],float)
a=raw[:,1:3,1]-raw[:,0:1,1];b=source[:,1:3,1]-source[:,0:1,1];s=float((a*b).sum()/(a*a).sum());out=Image.new('RGBA',(1024,512));rows=[];re=Image.new('RGBA',im.size)
for i,n in enumerate([45,49]):
 rect=[i*887,0,(i+1)*887,887];tile=im.crop(rect);re.paste(tile,(i*887,0));t=source[i,0]-s*raw[i,0];k=4*s;frame=tile.transform((512,512),Image.Transform.AFFINE,(1/k,0,-t[0]/s,0,1/k,-t[1]/s),resample=Image.Resampling.BICUBIC);out.paste(frame,(512*i,0));m=s*raw[i]+t
 rows.append({'source_id':n,'raw_rect':rect,'point_order':['crown','left_screen_boot','right_screen_boot','near_hand'],'raw_points':raw[i].tolist(),'source_points':source[i].tolist(),'translation':t.tolist(),'mapped_points':m.tolist(),'boot_delta':(m[2]-m[1]).tolist(),'target_boot_delta':(source[i,2]-source[i,1]).tolist(),'hand_dx_from_crown':float(m[3,0]-m[0,0]),'target_hand_dx':float(source[i,3,0]-source[i,0,0])})
assert re.tobytes()==im.tobytes();out.save(P/'two-poses-HD4-DIAGNOSTIC-ONLY.png')
(P/'MEASUREMENTS.json').write_text(json.dumps({'status':'partial_control_improvement_not_passed_not_animation','common_scale':s,'fit':'all four crown-to-boot vertical spans, one scale; per-pose crown rigid translation','exact_raw_reassembly':True,'raw_sha256':sha(P/'raw-v1.png'),'uncertainty':{'raw_points_px':8,'source_boot_logic_px':2,'source_hand_logic_px':3},'records':rows},indent=2)+'\n')
for factor in [1,2]:
 z=128*factor;board=Image.new('RGBA',(2*z,2*z),(64,68,72,255))
 for i,n in enumerate([45,49]):
  sourceim=Image.open(P.parent/'earth_hero_e_input_plan_v1'/f'source-{n}.png').convert('RGBA').resize((z,z),Image.Resampling.NEAREST);new=out.crop((i*512,0,(i+1)*512,512)).resize((z,z),Image.Resampling.LANCZOS);board.alpha_composite(sourceim,(i*z,0));board.alpha_composite(new,(i*z,z))
 board.save(D/f'source-control-true-{factor}x.png')
bg=Image.new('RGBA',(1024,768))
for row,col in enumerate([(64,68,72,255),(18,20,23,255),(220,222,224,255)]):
 tile=out.resize((512,256),Image.Resampling.LANCZOS);panel=Image.new('RGBA',(1024,256),col);panel.alpha_composite(tile,(0,0));bg.paste(panel,(0,row*256))
bg.save(D/'three-background-true2x.png')
print('scale',s);print(rows)
