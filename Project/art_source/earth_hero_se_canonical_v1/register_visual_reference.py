"""Single canonical source-size comparison only. No animation/runtime promotion."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[1];diag=R/'diagnostics/hero/earth-identity-plan';src=Image.open(P.parent/'earth_hero_input_plan_v1/source-13.png').convert('RGBA');raw=Image.open(P/'raw-v2.png').convert('RGBA');a=np.array(raw)[:,:,3];yy,xx=np.where(a[:220]>=128);top=yy.min();cx=xx[yy<=top+3].mean()
# Surface proxies, not joints; manually inspected canonical image. Sole centroids are used
# only as coarse terminal proxies with source2px uncertainty, not physical contact anchors.
c=np.array([[cx,top],[540,315],[550,430],[550,705],[428.1,1357],[690.21875,1222]],float)
s=np.array([[40,15],[42,27],[43,38],[43,54],[36,86],[52,81]],float);w=np.array([1,.6,.4,.25,1,1]);cm=(c*w[:,None]).sum(0)/w.sum();sm=(s*w[:,None]).sum(0)/w.sum();ca=c-cm;sa=s-sm;k=float((ca*sa*w[:,None]).sum()/(ca*ca*w[:,None]).sum());t=sm-k*cm
names=['crown_surface','neck_surface','sternum_armor_surface','pelvis_clothing_surface','left_boot_coarse_terminal','right_boot_coarse_terminal'];outputs={}
for density in [1,4]:
 frame=raw.transform((128*density,128*density),Image.Transform.AFFINE,(1/(k*density),0,-t[0]/k,0,1/(k*density),-t[1]/k),resample=Image.Resampling.BICUBIC);frame.save(P/f'v2-source-size-reference-{density}x.png');outputs[str(density)]=hashlib.sha256((P/f'v2-source-size-reference-{density}x.png').read_bytes()).hexdigest()
board=Image.new('RGBA',(256,160),(80,80,80,255));board.alpha_composite(src,(0,25));board.alpha_composite(Image.open(P/'v2-source-size-reference-1x.png'),(128,25));d=ImageDraw.Draw(board);d.text((5,3),'source13',fill='white');d.text((133,3),'canonical v2',fill='white');board.convert('RGB').save(diag/'canonical-v2-source-native.png');board.resize((1024,640),Image.Resampling.NEAREST).convert('RGB').save(diag/'canonical-v2-source-4x.jpg')
report={'status':'single_canonical_design_visual_reference_only_not_runtime_frame','raw_sha256':hashlib.sha256((P/'raw-v2.png').read_bytes()).hexdigest(),'uniform_scale':k,'translation':t.tolist(),'logical_canvas':[128,128],'logical_root':[16,64],'points':{n:{'raw':c[i].tolist(),'source':s[i].tolist(),'mapped':(k*c[i]+t).tolist(),'delta':(k*c[i]+t-s[i]).tolist(),'weight':w[i]} for i,n in enumerate(names)},'uncertainty':{'source_clothing_proxy_px':3,'source_boot_coarse_terminal_px':2,'candidate_manual_surface_raw_px':12,'candidate_alpha_pixel_edge_raw_px':2},'limits':'Source boot tip and new sole centroid are not homologous anatomy; broad terminal proxy only. Fit is a view aid, not proof of pose acceptance or a physical contact measurement. No frame-wise warp or body edits. Full4 source sequence still required.','outputs_sha256':outputs}
(P/'V2_SOURCE_SIZE_REFERENCE.json').write_text(json.dumps(report,indent=2)+'\n');print(k,t,[(n,(k*c[i]+t-s[i]).tolist()) for i,n in enumerate(names)])
