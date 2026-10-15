from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[1];D=R/'diagnostics/earth_hero_e_walk_v1';D.mkdir(exist_ok=True,parents=True);im=Image.open(P/'raw-v1.png').convert('RGBA');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
raw=np.array([[[250,12],[115,544],[440,527]],[[212,12],[103,511],[279,564]],[[205,10],[235,568],[251,519]],[[253,15],[121,552],[438,486]],[[217,15],[142,509],[286,548]],[[212,14],[173,533],[283,548]]],float)
source=np.array([[[40,16],[29,78],[60,81]],[[39,16],[31,77],[48,87]],[[40,15],[42,87],[51,78]],[[40,16],[29,84],[60,74]],[[39,16],[31,83],[48,77]],[[40,15],[41,80],[51,86]]],float)
# Diagnostic registration only. One common vertical crown-to-visible-boot scale; x spread independent check, never fitted away.
a=raw[:,1:,1]-raw[:,0:1,1];b=source[:,1:,1]-source[:,0:1,1];s=float((a*b).sum()/(a*a).sum());xx=[0,490,950,1310];yy=[0,600,1201];out=Image.new('RGBA',(3072,512));re=Image.new('RGBA',im.size);records=[]
for i in range(6):
 rect=[xx[i%3],yy[i//3],xx[i%3+1],yy[i//3+1]];tile=im.crop(rect);re.paste(tile,(rect[0],rect[1]));t=source[i,0]-s*raw[i,0];k=4*s;frame=tile.transform((512,512),Image.Transform.AFFINE,(1/k,0,-t[0]/s,0,1/k,-t[1]/s),resample=Image.Resampling.BICUBIC);out.paste(frame,(512*i,0));alpha=np.array(tile.getchannel('A'));ys,xs=np.where(alpha>=128);mapped=s*raw[i]+t;delta=mapped[2]-mapped[1];target=source[i,2]-source[i,1]
 records.append({'source_id':45+i,'raw_rect':rect,'raw_manual_points_crown_leftboot_rightboot':raw[i].tolist(),'source_points':source[i].tolist(),'translation_logical':t.tolist(),'mapped_points':mapped.tolist(),'residuals':(mapped-source[i]).tolist(),'new_right_minus_left_boot':delta.tolist(),'source_right_minus_left_boot':target.tolist(),'wrong_boot_vertical_order':bool(delta[1]*target[1]<0),'raw_density_body_height_over_source_73':float((ys.max()-ys.min()+1)/73),'texture_region':[512*i,0,512,512]})
assert re.tobytes()==im.tobytes();out.save(P/'body-density4-DIAGNOSTIC-REJECTED.png');reg={'status':'rejected_pose_not_for_runtime','common_uniform_scale_raw_to_logical':s,'method':'one scale fitted only to all crown-to-boot vertical spans; per-cell crown-alignment translation; bad x spread/order left visible; not a production fit','raw_sha256':sha(P/'raw-v1.png'),'exact_raw_reassembly':True,'raw_cut_note':'unequal gutter cuts x0/490/950/1310 prevent first-column forward toe clipping; cuts do not scale figures','root':[16,64],'hd4_root':[64,256],'logical_frame':[128,128],'hd4_frame':[512,512],'raw_point_uncertainty_px':8,'source_boot_uncertainty_px':2,'records':records};(P/'registration-v1.json').write_text(json.dumps(reg,indent=2)+'\n')
for factor in [1,2]:
 z=128*factor;board=Image.new('RGBA',(z*3,z*4),(64,68,72,255))
 for i in range(6):
  src=Image.open(P.parent/'earth_hero_e_input_plan_v1'/f'source-{45+i}.png').convert('RGBA').resize((z,z),Image.Resampling.NEAREST);new=out.crop((512*i,0,512*(i+1),512)).resize((z,z),Image.Resampling.LANCZOS)
  for row,tile in [(i//3*2,src),(i//3*2+1,new)]:board.alpha_composite(tile,(i%3*z,row*z));ImageDraw.Draw(board).text((i%3*z+4,row*z+4),f'{45+i} '+('source' if row%2==0 else 'REJECTED'),fill='white')
 board.save(D/f'source-candidate-true-{factor}x.png')
print('scale',s);print([(r['source_id'],r['new_right_minus_left_boot'],r['source_right_minus_left_boot'],r['wrong_boot_vertical_order']) for r in records])
