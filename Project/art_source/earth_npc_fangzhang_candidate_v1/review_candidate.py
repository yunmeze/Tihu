from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
O=Path(__file__).parent;P=O.parents[1];D=P/'diagnostics/earth-npc-fangzhang-v1';D.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Manually read visible surface/extremum proxies, NOT exact anatomical joints.
# Head-top construction changed; only scale check, not facial anatomy proof.
names=['head_top_proxy','screen_left_boot_lower_edge','screen_right_boot_lower_edge']
src=np.array([[55.,64.],[43.5,119.],[59.5,129.]])
gen=np.array([[574.,60.],[380.,1188.],[819.,1484.]])
sc=float(((gen-gen.mean(0))*(src-src.mean(0))).sum()/((gen-gen.mean(0))**2).sum());tr=src.mean(0)-sc*gen.mean(0)
im=Image.open(O/'raw-v1.png').convert('RGBA');a=np.asarray(im.getchannel('A'));res={}
for den in [1,4]:
    # One fixed scalar + translation. No body/background edits or retouch. Diagnostic only.
    coeff=(1/(sc*den),0,-tr[0]/sc,0,1/(sc*den),-tr[1]/sc)
    reg=im.transform((128*den,160*den),Image.Transform.AFFINE,coeff,resample=Image.Resampling.BICUBIC)
    reg.save(D/f'candidate-fixed-register-{den}x.png')
s=Image.open(P/'art_source/earth_npc_input_plan_v1/fangzhang/source-four-registered-native.png').crop((0,0,128,160));g=Image.open(D/'candidate-fixed-register-1x.png')
board=Image.new('RGBA',(256,160),(92,100,106,255));board.alpha_composite(s,(0,0));board.alpha_composite(g,(128,0));board.convert('RGB').save(D/'source-candidate-native-1x.png');board.resize((1024,640),Image.Resampling.NEAREST).convert('RGB').save(D/'source-candidate-native-4x.png')
r={'status':'one_raw_candidate_only_hold_for_parent_pose_review_no_runtime','raw':{'size':list(im.size),'sha256':sha(O/'raw-v1.png'),'alpha0_pixels':int((a==0).sum()),'alpha1_to7_pixels':int(((a>0)&(a<8)).sum()),'alpha128_bbox':im.getchannel('A').point(lambda x:255 if x>=128 else 0).getbbox()},'transform':{'uniform_scale_generated_to_logical':sc,'translation_to_registered_canvas':tr.tolist(),'rotation':0,'per_limb_adjustments':False,'raw_pixels_per_logical_unit':1/sc,'diagnostic_only':True},'landmarks':[{'name':n,'source_registered':s.tolist(),'raw_generated':g.tolist(),'residual_logical_px':float(np.linalg.norm(sc*g+tr-s))}for n,s,g in zip(names,src,gen)],'uncertainty':{'source_px':3,'raw_px':15,'note':'visible extrema only, source baked shadow confounds boot endpoints; head clothing removed. No solved anatomical floor.'},'generation':{'built_in_imagegen_calls':1,'transparent_background_requested':True,'inputs':['source261-pose-8x.png','../earth_npc_input_plan_v1/concept-fangzhang-disconnected-local-4x.png'],'prompt_sha256':sha(O/'prompt.txt'),'request_sha256':sha(O/'tool-request.json')},'scope':'native references and input plan remain frozen; no second generation, no runtime, no shadow integration'}
(O/'review.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r,ensure_ascii=False,indent=2))
