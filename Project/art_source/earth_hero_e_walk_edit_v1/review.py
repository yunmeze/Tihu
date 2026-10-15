from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;A=P.parent;D=P.parents[1]/'diagnostics/earth_hero_e_walk_edit_v1';D.mkdir(parents=True,exist_ok=True)
base=Image.open(A/'earth_hero_e_walk_v2/raw-v2.png').convert('RGBA');im=Image.open(P/'raw.png').convert('RGBA');old=json.loads((A/'earth_hero_e_walk_v2/registration-v2.json').read_text());plan=json.loads((A/'earth_hero_e_walk_edit_plan_v1/INPUT_PROVENANCE.json').read_text());s=old['common_uniform_scale_raw_to_logical'];out=Image.new('RGBA',(3072,512));rows=[]
raw=np.array([[[232,41],[133,448],[339,450],[202,281]],[[263,41],[184,416],[310,466],[191,274]],[[272,41],[260,465],[305,430],[260,285]],[[230,41],[142,448],[340,437],[237,280]],[[263,44],[218,435],[310,451],[234,291]],[[272,38],[232,441],[311,456],[211,286]]],float)
hands=[[33,57],[37,56],[44,56],[49,56],[43,56],[36,57]]
for i,r in enumerate(old['records']):
 n=45+i;rect=r['raw_rect'];b=base.crop(rect);new=im.crop(rect);t=np.array(r['translation_logical']);k=4*s
 frame=new.transform((512,512),Image.Transform.AFFINE,(1/k,0,-t[0]/s,0,1/k,-t[1]/s),resample=Image.Resampling.BICUBIC);out.paste(frame,(512*i,0))
 a=np.array(b);c=np.array(new);mask=np.ones((512,512),bool)
 for q in plan['base_cell_local_context_envelopes'][str(n)].values():mask[q[1]:q[3],q[0]:q[2]]=False
 def pm(z):return np.concatenate((z[:,:,:3].astype(float)*z[:,:,3:4]/255,z[:,:,3:4].astype(float)),axis=2)
 diff=np.max(abs(pm(a)-pm(c)),axis=2);vis=(a[:,:,3]>8)|(c[:,:,3]>8)
 m=raw[i]*s+t
 # alpha additions outside base support; includes genuine intended arm/leg changes, not all called halos
 rows.append({'source_id':n,'raw_surface_points_crown_lefttoe_righttoe_hand':raw[i].tolist(),'mapped_points_original_registration':m.tolist(),'toe_right_minus_left':(m[2]-m[1]).tolist(),'source_toe_difference':r['source_right_minus_left_boot'],'hand_residual_to_source':(m[3]-hands[i]).tolist(),'protected_visible_changed_fraction_gt8':float((mask&vis&(diff>8)).sum()/max(1,(mask&vis).sum())),'added_alpha_pixels_where_base_alpha_le2':int(((a[:,:,3]<=2)&(c[:,:,3]>8)).sum())})
out.save(P/'original-v2-registration-HD4-STATIC-ONLY.png')
reg={'status':'rejected_local_correction','raw_sha256':hashlib.sha256((P/'raw.png').read_bytes()).hexdigest(),'base_and_output_sizes':[base.size,im.size],'registration':'EXACT v2 scale and all6 translations, no refit, no rotation','scale':s,'uncertainty':'source toe +/-2,hand +/-3; raw surface selection +/-8. Not bones/contact.','records':rows}
(P/'MEASUREMENTS.json').write_text(json.dumps(reg,indent=2)+'\n')
oldhd=Image.open(A/'earth_hero_e_walk_v2/body-density4-DIAGNOSTIC-REJECTED.png').convert('RGBA')
def tile(n,kind,z):
 if kind=='source':return Image.open(A/'earth_hero_e_input_plan_v1'/f'source-{n}.png').convert('RGBA').resize((z,z),Image.Resampling.NEAREST)
 sheet=oldhd if kind=='v2 BASE' else out
 return sheet.crop(((n-45)*512,0,(n-44)*512,512)).resize((z,z),Image.Resampling.LANCZOS)
for f in [1,2]:
 z=128*f;board=Image.new('RGBA',(3*z,6*z),(64,68,72,255));d=ImageDraw.Draw(board)
 for i in range(6):
  for j,kind in enumerate(['source','v2 BASE','EDIT fixed']):
   x=i%3*z;y=(i//3*3+j)*z;board.alpha_composite(tile(45+i,kind,z),(x,y));d.text((x+3,y+3),f'{45+i} {kind}',fill='white')
 board.save(D/f'source-base-edit-true-{f}x.png')
z=256;board=Image.new('RGBA',(4*z,3*z),(64,68,72,255));d=ImageDraw.Draw(board)
for row,kind in enumerate(['source','v2 BASE','EDIT fixed']):
 for col,n in enumerate([49,50,45,46]):
  board.alpha_composite(tile(n,kind,z),(col*z,row*z));d.text((col*z+3,row*z+3),f'{n} {kind}',fill='white')
board.save(D/'cycle50-45-true-2x.png')
board=Image.new('RGBA',(1536,768))
for row,color in enumerate([(20,22,26,255),(128,128,128,255),(235,235,235,255)]):
 for i in range(6):
  b=Image.new('RGBA',(256,256),color);b.alpha_composite(tile(45+i,'EDIT fixed',256));board.paste(b,(i*256,row*256))
board.save(D/'three-background-true-2x.png')
print(json.dumps(reg,indent=2))
