from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
from scipy.ndimage import affine_transform
from scipy.optimize import differential_evolution
P=Path(__file__).resolve().parent;D=P.parents[1]/'diagnostics/earth_hero_e_49_arm_edit_v1'
base=Image.open(P.parent/'earth_hero_e_49_control_v2/raw.png').convert('RGBA');new=Image.open(P/'raw.png').convert('RGBA')
a=np.array(base.getchannel('A').resize((314,314),Image.Resampling.BOX))>128
b=np.array(new.getchannel('A').resize((314,314),Image.Resampling.BOX))/255.
ratio=314/1254
def matrix(p):
 s,theta,tx,ty=p;th=np.deg2rad(theta);R=np.array([[np.cos(th),-np.sin(th)],[np.sin(th),np.cos(th)]])
 # yx coordinate convention. New -> base: base=sR new + t.
 M=R.T/s;t=np.array([ty,tx])*ratio
 return M,-M@t
def warped(p):
 M,o=matrix(p);return affine_transform(b,M,o,output_shape=a.shape,order=1)>0.5
def obj(p):
 c=warped(p);return 1-(a&c).sum()/max(1,(a|c).sum())
res=differential_evolution(obj,[(.65,1.05),(-8,8),(-100,150),(-100,150)],seed=49,popsize=12,maxiter=120,tol=1e-6)
s,angle,tx,ty=map(float,res.x);M,o=matrix(res.x);o=o/ratio
# Pillow inverse matrix uses xy, scipy formula above uses yx.
c=new.transform(base.size,Image.Transform.AFFINE,(M[1,1],M[1,0],o[1],M[0,1],M[0,0],o[0]),resample=Image.Resampling.BICUBIC)
aa=np.array(base.getchannel('A'))>128;cc=np.array(c.getchannel('A'))>128
regions={'full':[0,0,1254,1254],'head':[310,140,480,285],'legs_and_boots':[150,580,600,900],'upper_body_including_edited_arm':[280,275,520,580]}
stats={}
for name,(x0,y0,x1,y1) in regions.items():
 x=aa[y0:y1,x0:x1];y=cc[y0:y1,x0:x1];stats[name]={'silhouette_iou':float((x&y).sum()/max(1,(x|y).sum())),'xor_pixels':int((x^y).sum())}
j={'purpose':'EXPLANATION ONLY; does not replace fixed registration or failure','fit':'one whole-image alpha-silhouette similarity transform, all foreground equally weighted, no limb/point fits','map':'base_yx = scale * R(theta) * output_yx + [ty,tx]','new_to_base_scale':s,'rotation_degrees_yx_convention':angle,'translation_xy_raw':[tx,ty],'implied_linear_enlargement':1/s,'silhouette_regions_after_same_global_transform':stats,'limitations':['fit includes changed arm and may compromise other areas','alpha silhouette cannot prove internal armor/pants texture or joint invariance','optimized transform is diagnostic only; not candidate registration or edited artwork']}
(P/'GLOBAL_DRIFT_EXPLANATION.json').write_text(json.dumps(j,indent=2)+'\n')
board=Image.new('RGBA',(1254*3,1254),(64,68,72,255));board.alpha_composite(base,(0,0));board.alpha_composite(c,(1254,0))
over=np.zeros((1254,1254,4),np.uint8);over[:]=[64,68,72,255];over[aa&cc]=[170,170,170,255];over[aa&~cc]=[40,210,240,255];over[cc&~aa]=[250,90,160,255];board.paste(Image.fromarray(over),(2508,0))
dr=ImageDraw.Draw(board)
for i,txt in enumerate(['BASE','GLOBAL similarity only: NOT accepted registration','Overlay: cyan base-only / pink new-only']):dr.text((i*1254+10,10),txt,fill='white')
board.resize((1881,627),Image.Resampling.LANCZOS).save(D/'explanatory-global-similarity-overlay.png')
print(json.dumps(j,indent=2))
