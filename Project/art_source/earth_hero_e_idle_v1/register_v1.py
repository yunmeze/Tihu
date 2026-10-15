from PIL import Image,ImageDraw
from pathlib import Path
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[1];D=R/'diagnostics/earth_hero_e_idle_v1';D.mkdir(parents=True,exist_ok=True)
im=Image.open(P/'raw-v1.png').convert('RGBA');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Manually inspected visible surface proxies; no inferred skeleton or physical contacts.
raw=[[[270,44],[282,684],[326,613]],[[278,44],[287,684],[334,612]],[[281,43],[289,684],[336,612]],[[286,44],[292,685],[340,613]]]
target=np.array([[40,15],[41,86],[48,77]],float)
# Least squares common isotropic scale, separate rigid translation per cell.
X=[];Y=[]
for a in raw:
 a=np.array(a,float);X.append(a-a.mean(0));Y.append(target-target.mean(0))
s=sum((x*y).sum() for x,y in zip(X,Y))/sum((x*x).sum() for x in X)
result=Image.new('RGBA',(2048,512));rows=[];parts=[]
for i,points in enumerate(raw):
 rect=[round(i*im.width/4),0,round((i+1)*im.width/4),im.height];part=im.crop(rect);parts.append(part);a=np.array(points,float);t=target.mean(0)-s*a.mean(0);k=s*4
 # One resampling directly from untouched raw into HD4. Inverse affine is common isotropic scale plus translation only.
 frame=part.transform((512,512),Image.Transform.AFFINE,(1/k,0,-t[0]/s,0,1/k,-t[1]/s),resample=Image.Resampling.BICUBIC);result.paste(frame,(i*512,0))
 alpha=np.asarray(part.getchannel('A'));ys,xs=np.where(alpha>=128);bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
 rows.append({'source_id':9+i,'raw_rect':rect,'raw_anchor_names':['crown','near_boot_terminal','far_boot_terminal'],'raw_anchor_points':points,'source_points':target.tolist(),'translation_logical':t.tolist(),'mapped_points':(s*a+t).tolist(),'residuals':(s*a+t-target).tolist(),'alpha128_body_bbox':bbox,'raw_body_height':bbox[3]-bbox[1],'raw_density_vs_source_72':(bbox[3]-bbox[1])/72,'alpha_1_to_15_count':int(((alpha>0)&(alpha<16)).sum()),'texture_region':[i*512,0,512,512]})
result.save(P/'body-density4.png');result.resize((512,128),Image.Resampling.LANCZOS).save(P/'body-density1.png')
# Exact original raw reassembly check, no deletion of low-alpha pixels.
re=Image.new('RGBA',im.size)
for i,p in enumerate(parts):re.paste(p,(round(i*im.width/4),0))
assert re.tobytes()==im.tobytes()
reg={'status':'candidate_pending_parent_review_not_runtime','raw_sha256':sha(P/'raw-v1.png'),'atlas_sha256':sha(P/'body-density4.png'),'logical_frame_size':[128,128],'logical_root':[16,64],'texture_frame_size':[512,512],'texture_root':[64,256],'texture_density':4,'frame_ticks':12,'common_uniform_scale_raw_to_logical':s,'method':'global least squares crown and two visible boot terminals; one common isotropic scale + each cell rigid translation; raw directly resampled to HD4','no_rotation_warp_independent_scale_or_bbox_normalization':True,'exact_raw_reassembly':True,'uncertainty':{'raw_manual_anchor_px':8,'source_crown_px':1,'source_boot_px':2},'limits':['visible surface anchors are not anatomical joints or ground contacts','source small breathing changes still require visual assessment','low-alpha raw speckles retained unchanged','HD4 canvas alone does not prove density; raw body measurements supplied'],'records':rows}
(P/'registration-v1.json').write_text(json.dumps(reg,indent=2)+'\n')
# Real 1x/2x raster panels, not enlarged 1x copies.
for factor in [1,2]:
 w=128*factor;h=128*factor;board=Image.new('RGBA',(4*w,3*h),(64,68,72,255))
 for i in range(4):
  src=Image.open(P.parent/'earth_hero_e_input_plan_v1'/f'source-{9+i}.png').convert('RGBA').resize((w,h),Image.Resampling.NEAREST);e=result.crop((i*512,0,(i+1)*512,512)).resize((w,h),Image.Resampling.LANCZOS);se=Image.open(P.parent/'earth_hero_se_idle_v1/body-density4.png').convert('RGBA').crop((i*512,0,(i+1)*512,512)).resize((w,h),Image.Resampling.LANCZOS)
  for row,tile in enumerate([src,e,se]):board.alpha_composite(tile,(i*w,row*h))
 ImageDraw.Draw(board).text((3,3),'Original E / Candidate E / Approved SE',fill='white');board.save(D/f'original-E-SE-review-true-{factor}x.png')
(P/'candidate-interface.json').write_text(json.dumps({'direction':'E','action':'idle','source_ids':[9,10,11,12],'atlas':'body-density4.png','density':4,'frame_size':[128,128],'root':[16,64],'ticks':12,'runtime_installed':False},indent=2)+'\n')
print('common scale',s,'raw density minimum',min(r['raw_density_vs_source_72'] for r in rows))
# Actual compositing on three standard backgrounds; do not diagnose halos on transparent viewer alone.
tile=result.resize((1024,256),Image.Resampling.LANCZOS);b=Image.new('RGBA',(1024,768))
for row,color in enumerate([(64,68,72,255),(18,20,23,255),(220,222,224,255)]):
 bg=Image.new('RGBA',(1024,256),color);bg.alpha_composite(tile);ImageDraw.Draw(bg).text((5,5),['gray true2x','dark true2x','light true2x'][row],fill='white' if row<2 else 'black');b.paste(bg,(0,row*256))
b.save(D/'three-background-alpha-true2x.png')
