from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;A=P.parent;D=P.parents[1]/'diagnostics/earth_e_partition_control_v1';D.mkdir(parents=True,exist_ok=True)
im=Image.open(P/'raw.png').convert('RGBA');raw=np.array([[[520,18],[334,788],[788,805],[361,474]],[[432,18],[330,809],[579,839],[430,460]]],float);src=np.array([[[40,16],[29,78],[60,81],[33,57]],[[39,16],[31,83],[48,77],[43,56]]],float)
a=raw[:,1:3,1]-raw[:,0:1,1];b=src[:,1:3,1]-src[:,0:1,1];s=float((a*b).sum()/(a*a).sum());out=Image.new('RGBA',(1024,512));rows=[];re=Image.new('RGBA',im.size)
for i,n in enumerate([45,49]):
 tile=im.crop((i*887,0,(i+1)*887,887));re.paste(tile,(887*i,0));t=src[i,0]-s*raw[i,0];k=s*4
 f=tile.transform((512,512),Image.Transform.AFFINE,(1/k,0,-t[0]/s,0,1/k,-t[1]/s),resample=Image.Resampling.BICUBIC);out.paste(f,(512*i,0));m=raw[i]*s+t
 rows.append({'frame':n,'raw_rect':[887*i,0,887*(i+1),887],'raw_surface_points_crown_lefttoe_righttoe_hand':raw[i].tolist(),'source_points':src[i].tolist(),'translation':t.tolist(),'mapped_points':m.tolist(),'toe_difference':(m[2]-m[1]).tolist(),'source_toe_difference':(src[i,2]-src[i,1]).tolist(),'hand_residual':(m[3]-src[i,3]).tolist()})
assert im.tobytes()==re.tobytes();out.save(P/'two-poses-HD4-RESEARCH-ONLY.png')
j={'status':'rejected_leg_hand_joint_gate','raw_sha256':hashlib.sha256((P/'raw.png').read_bytes()).hexdigest(),'raw_size':im.size,'scale':s,'fit':'one shared crown-to-two-toe vertical scale across both; crown rigid translation per frame; x never fitted, no limb warp or rotation','uncertainty':'raw surface point +/-8px, source toe +/-2, hand +/-3, crown +/-1; surface locations not hidden bones/contact; y used in scale so y residual not independent','exact_partition_reassembly':True,'records':rows}
(P/'MEASUREMENTS.json').write_text(json.dumps(j,indent=2)+'\n')
for fact in [1,2]:
 z=128*fact;board=Image.new('RGBA',(z*2,z*3),(64,68,72,255));dr=ImageDraw.Draw(board)
 for i,n in enumerate([45,49]):
  for row,(label,tile) in enumerate([('original',Image.open(A/'earth_hero_e_input_plan_v1'/f'source-{n}.png').convert('RGBA')),('texture suppressed',Image.open(P.parents[1]/'diagnostics/earth_e_pose_partition_research_v1'/f'{n}-visible-core-partition.png').convert('RGBA')),('new COMMON scale',out.crop((512*i,0,512*(i+1),512)))]):
   tile=tile.resize((z,z),Image.Resampling.NEAREST if row<2 else Image.Resampling.LANCZOS);board.alpha_composite(tile,(i*z,row*z));dr.text((i*z+3,row*z+3),f'{n} {label}',fill='white')
 board.save(D/f'source-control-true-{fact}x.png')
board=Image.new('RGBA',(512,768))
for row,col in enumerate([(20,22,26,255),(128,128,128,255),(235,235,235,255)]):
 for i in range(2):
  tile=Image.new('RGBA',(256,256),col);tile.alpha_composite(out.crop((512*i,0,512*(i+1),512)).resize((256,256),Image.Resampling.LANCZOS));board.paste(tile,(256*i,256*row))
board.save(D/'three-background-true-2x.png')
print(json.dumps(j,indent=2))
