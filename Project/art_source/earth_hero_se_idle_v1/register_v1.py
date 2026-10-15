from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent; J=P.parents[1]; D=J/'diagnostics/hero/earth-se-idle-v1';D.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=['crown_surface','neck_surface','sternum_armor_proxy','pelvis_clothing_proxy','screen_left_boot_terminal','screen_right_boot_terminal']
s=np.array([[[40,15],[42,27],[43,38],[43,54],[36,86],[52,81]],[[40,15],[42,27],[43,38],[43,54],[36,86],[52,81]],[[40,15],[42,28],[43,38],[43,54],[36,86],[52,81]],[[40,15],[43,27],[44,38],[44,54],[37,86],[53,81]]],float)
c=np.array([[[264.60,56],[270,168],[278,237],[275,354],[211.4,692],[343.3,647]],[[264.21,56],[272,168],[282,237],[281,354],[215.64,692],[349.9,647]],[[274.01,55],[284,170],[295,240],[291,358],[226.86,697],[365.35,650]],[[282.13,57],[293,168],[307,237],[305,355],[236.61,695],[372.05,647]]],float)
w=np.array([1,.6,.4,.25,1,1]); cm=(c*w[None,:,None]).sum(1)/w.sum();sm=(s*w[None,:,None]).sum(1)/w.sum();a=c-cm[:,None,:];b=s-sm[:,None,:];k=float((a*b*w[None,:,None]).sum()/(a*a*w[None,:,None]).sum());t=sm-k*cm
im=Image.open(P/'raw-v1.png').convert('RGBA'); edges=[0,535,1069,1604,2138];rec=[];atlases={d:Image.new('RGBA',(4*128*d,128*d)) for d in [1,4]}; rebuilt=Image.new('RGBA',im.size)
for i in range(4):
 r=(edges[i],0,edges[i+1],735);cell=im.crop(r);rebuilt.paste(cell,(r[0],0));tx,ty=t[i]
 for d,atlas in atlases.items():
  out=cell.transform((128*d,128*d),Image.Transform.AFFINE,(1/(k*d),0,-tx/k,0,1/(k*d),-ty/k),resample=Image.Resampling.BICUBIC);atlas.paste(out,(128*d*i,0))
 mapped=k*c[i]+t[i]; rec.append({'source_id':13+i,'raw_rect':list(r),'translation_logical':t[i].tolist(),'region_px':[512*i,0,512,512],'source_points':dict(zip(names,s[i].tolist())),'candidate_raw_points':dict(zip(names,c[i].tolist())),'mapped_points':dict(zip(names,mapped.tolist())),'residuals':dict(zip(names,(mapped-s[i]).tolist()))})
assert rebuilt.tobytes()==im.tobytes()
for d,atlas in atlases.items():atlas.save(P/f'body-density{d}.png')
m={'status':'pose_candidate_pending_native_review','source_ids':[13,14,15,16],'atlas':'body-density4.png','atlas_sha256':sha(P/'body-density4.png'),'raw_sha256':sha(P/'raw-v1.png'),'texture_density':4,'logical_frame_size':[128,128],'texture_frame_size':[512,512],'logical_root':[16,64],'texture_root':[64,256],'frame_ticks':12,'common_uniform_scale_raw_to_logical':k,'registration':'single uniform scale plus per-frame rigid translations; no rotation, warp, independent scale or bbox normalization','weights':dict(zip(names,w.tolist())),'uncertainty':{'source_clothing_proxy_px':3,'source_boot_terminal_px':2,'candidate_manual_raw_px':8,'alpha_edge_raw_px':2},'limitations':['boot terminal is a coarse visible endpoint proxy, not proven contact or homologous joint','cloth/armor surface centers are not anatomical joints','far shoulder red patch and thigh plate coverage vary from canonical; inspect at true size','warm upper-left key; no ground shadow; old right-up shadow parameters prohibited'],'exact_raw_reassembly':True,'records':rec}
(P/'registration-v1.json').write_text(json.dumps(m,indent=2)+'\n')
for d in [1,2]:
 board=Image.new('RGBA',(512*d,280*d),(100,100,100,255));draw=ImageDraw.Draw(board);draw.text((3,3),'SOURCE 13 14 15 16',(255,255,255));draw.text((3,140*d),'EARTH CANDIDATE',(255,255,255))
 for i in range(4):
  src=Image.open(P.parent/'earth_hero_input_plan_v1'/f'source-{13+i}.png').convert('RGBA').resize((128*d,128*d),Image.Resampling.NEAREST);board.alpha_composite(src,(128*d*i,12*d))
 new=atlases[4].resize((512*d,128*d),Image.Resampling.LANCZOS);board.alpha_composite(new,(0,152*d));board.convert('RGB').save(D/f'source-candidate-true{d}x.png')
print(json.dumps({'scale':k,'sha':m['atlas_sha256'],'boot_residuals':[{n:r['residuals'][n] for n in names[-2:]}for r in rec]},indent=2))
