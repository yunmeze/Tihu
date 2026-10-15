from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;A=P.parent;D=P.parents[1]/'diagnostics/earth_hero_e_49_arm_edit_v1';D.mkdir(parents=True,exist_ok=True)
base=Image.open(A/'earth_hero_e_49_control_v2/raw.png').convert('RGBA');new=Image.open(P/'raw.png').convert('RGBA');old=json.loads((A/'earth_hero_e_49_control_v2/MEASUREMENTS.json').read_text());s=old['common_uniform_scale'];t=old['translation'];k=4*s
out=new.transform((512,512),Image.Transform.AFFINE,(1/k,0,-t[0]/s,0,1/k,-t[1]/s),resample=Image.Resampling.BICUBIC);out.save(P/'fixed-registration-HD4-CONTROL-ONLY.png')
a=np.asarray(base);b=np.asarray(new);outside=np.ones(a.shape[:2],bool);outside[365:580,330:485]=False
# Compare visible premultiplied RGB+alpha, ignoring hidden RGB in fully transparent pixels.
def premul(x):return np.concatenate((x[:,:,:3].astype(float)*x[:,:,3:4]/255,x[:,:,3:4].astype(float)),axis=2)
diff=np.max(np.abs(premul(a)-premul(b)),axis=2);visible=(a[:,:,3]>8)|(b[:,:,3]>8)
def bbox(x):
 yy,xx=np.where(x[:,:,3]>=128);return [int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
rawpoints={'crown':[404,168],'left_toe_surface':[288,997],'right_toe_surface':[515,945],'near_hand_group':[511,629]}
m={n:[p[0]*s+t[0],p[1]*s+t[1]] for n,p in rawpoints.items()}
j={'status':'failed_local_preservation','raw_sha256':hashlib.sha256((P/'raw.png').read_bytes()).hexdigest(),'base_sha256':old['raw_sha256'],'base_size':base.size,'output_size':new.size,'registration':'EXACT prior scale and translation reused, no refit','scale':s,'translation':t,'base_alpha128_bbox':bbox(a),'new_alpha128_bbox':bbox(b),'raw_manual_surface_points':rawpoints,'mapped_surface_points':m,'raw_point_uncertainty_px':8,'protected_region':'everything outside [330,365,485,580]; torso within also protected semantically','protected_visible_union_pixels':int((outside&visible).sum()),'protected_visible_pixels_premultiplied_delta_gt8':int((outside&visible&(diff>8)).sum()),'protected_visible_changed_fraction':float((outside&visible&(diff>8)).sum()/(outside&visible).sum()),'limits':['changed-pixel statistic alone cannot separate global resynthesis from geometry; silhouette/bbox and same-registration image corroborate clear enlargement','source sleeve regions are approximate, no exact elbow inferred','do not rescale candidate to match base or composite old legs']}
(P/'MEASUREMENTS.json').write_text(json.dumps(j,indent=2)+'\n')
src=Image.open(A/'earth_hero_e_input_plan_v1/source-49.png').convert('RGBA');prior=Image.open(A/'earth_hero_e_49_control_v2/single49-HD4-CONTROL-ONLY.png').convert('RGBA')
for f in [1,2]:
 z=128*f;board=Image.new('RGBA',(z*3,z),(64,68,72,255))
 for i,(label,tile) in enumerate([('source49',src.resize((z,z),Image.Resampling.NEAREST)),('prior FIXED',prior.resize((z,z),Image.Resampling.LANCZOS)),('edit SAME transform',out.resize((z,z),Image.Resampling.LANCZOS))]):
  board.alpha_composite(tile,(z*i,0));ImageDraw.Draw(board).text((z*i+3,3),label,fill='white')
 board.save(D/f'source-base-edit-fixed-true-{f}x.png')
heat=np.zeros_like(a);heat[:,:,3]=255;heat[:,:,:3]=24;heat[diff>8]=[230,90,55,255];heat[~outside]=[60,90,120,255];Image.fromarray(heat).save(D/'protected-pixel-change-map.png')
board=Image.new('RGBA',(2508,1254),(64,68,72,255));board.alpha_composite(base,(0,0));board.alpha_composite(new,(1254,0));ImageDraw.Draw(board).text((10,10),'BASE - unchanged raw scale',fill='white');ImageDraw.Draw(board).text((1264,10),'EDIT - same1254 canvas, NO refit',fill='white');board.save(D/'base-edit-raw-same-canvas.png')
print(json.dumps(j,indent=2))
