from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;D=P.parents[1]/'diagnostics/earth_hero_e_walk_v3';D.mkdir(parents=True,exist_ok=True)
im=Image.open(P/'raw.png').convert('RGBA')
# Surface-region representative locations only, not bone joints.
raw=np.array([[[270,40],[161,452],[406,453],[189,273]],[[266,40],[185,431],[291,474],[303,241]],[[268,40],[260,477],[300,429],[313,222]],[[282,27],[163,452],[397,405],[358,205]],[[268,28],[192,448],[283,451],[315,203]],[[268,27],[239,442],[314,452],[182,247]]],float)
src=np.array([[[40,16],[29,78],[60,81],[33,57]],[[39,16],[31,77],[48,87],[37,56]],[[40,15],[42,87],[51,78],[44,56]],[[40,16],[29,84],[60,74],[49,56]],[[39,16],[31,83],[48,77],[43,56]],[[40,15],[41,80],[51,86],[36,57]]],float)
a=raw[:,1:3,1]-raw[:,0:1,1];b=src[:,1:3,1]-src[:,0:1,1];s=float((a*b).sum()/(a*a).sum())
out=Image.new('RGBA',(3072,512));re=Image.new('RGBA',im.size);records=[]
for i in range(6):
 x=i%3*512;y=i//3*512;tile=im.crop((x,y,x+512,y+512));re.paste(tile,(x,y))
 t=src[i,0]-s*raw[i,0];k=4*s
 frame=tile.transform((512,512),Image.Transform.AFFINE,(1/k,0,-t[0]/s,0,1/k,-t[1]/s),resample=Image.Resampling.BICUBIC);out.paste(frame,(512*i,0))
 m=s*raw[i]+t;delta=m[2]-m[1];target=src[i,2]-src[i,1];alpha=np.array(tile.getchannel('A'));ys,xs=np.where(alpha>=128)
 records.append({'source_id':45+i,'raw_rect':[x,y,x+512,y+512],'raw_points_crown_lefttoe_righttoe_nearhand':raw[i].tolist(),'source_points':src[i].tolist(),'translation_logical':t.tolist(),'mapped_points':m.tolist(),'right_minus_left_toe':delta.tolist(),'source_right_minus_left_toe':target.tolist(),'near_hand_residual':(m[3]-src[i,3]).tolist(),'raw_body_height':int(ys.max()-ys.min()+1),'raw_effective_density':float((ys.max()-ys.min()+1)/73)})
assert re.tobytes()==im.tobytes()
out.save(P/'body-density4-STATIC-ONLY.png')
data={'status':'STATIC_REJECTED_NOT_RUNTIME','raw_sha256':hashlib.sha256((P/'raw.png').read_bytes()).hexdigest(),'common_scale_raw_to_logical':s,'registration':'One shared least-squares vertical crown-to-toe span scale, all six phases; per-frame crown translation only. No x fit, no per-frame scale or warp. Diagnostic, not production.','logical_root':[16,64],'hd4_root':[64,256],'exact_raw_reassembly':True,'uncertainty':'raw surface regions +/-8 px; source crown +/-1, toe +/-2, hand +/-3. Residuals are surface locations, NOT precise bone offsets. Source contact/hidden elbows remain unknown.','records':records}
(P/'MEASUREMENTS.json').write_text(json.dumps(data,indent=2)+'\n')
def srcim(i,z):return Image.open(P.parent/'earth_hero_e_input_plan_v1'/f'source-{i}.png').convert('RGBA').resize((z,z),Image.Resampling.NEAREST)
def newim(i,z):return out.crop((512*(i-45),0,512*(i-44),512)).resize((z,z),Image.Resampling.LANCZOS)
for factor in [1,2]:
 z=128*factor;board=Image.new('RGBA',(3*z,4*z),(64,68,72,255))
 for i in range(6):
  for r,tile in [(i//3*2,srcim(45+i,z)),(i//3*2+1,newim(45+i,z))]:
   xy=(i%3*z,r*z);board.alpha_composite(tile,xy);ImageDraw.Draw(board).text((xy[0]+4,xy[1]+4),f'{45+i} '+('source' if r%2==0 else 'v3 STATIC'),fill='white')
 board.save(D/f'source-candidate-true-{factor}x.png')
z=256;idle=Image.open(P.parent/'earth_hero_e_idle_v1/body-density4.png').convert('RGBA').crop((0,0,512,512)).resize((z,z),Image.Resampling.LANCZOS)
board=Image.new('RGBA',(5*z,2*z),(64,68,72,255))
for row in range(2):
 for col,i in enumerate([49,50,45,46,9]):
  tile=(idle if row else srcim(9,z)) if i==9 else (newim(i,z) if row else srcim(i,z))
  board.alpha_composite(tile,(col*z,row*z));ImageDraw.Draw(board).text((col*z+4,row*z+4),str(i)+(' candidate / idle' if row else ' source'),fill='white')
board.save(D/'cycle50-45-idle-true-2x.png')
board=Image.new('RGBA',(6*z,3*z))
for row,c in enumerate([(32,34,38,255),(128,128,128,255),(232,232,232,255)]):
 for i in range(6):
  tile=Image.new('RGBA',(z,z),c);tile.alpha_composite(newim(45+i,z));board.paste(tile,(i*z,row*z))
board.save(D/'three-background-true-2x.png')
print(json.dumps({'scale':s,'raw_sha256':data['raw_sha256'],'phases':[{k:r[k] for k in ['source_id','right_minus_left_toe','source_right_minus_left_toe','near_hand_residual','raw_effective_density']} for r in records]},indent=2))
