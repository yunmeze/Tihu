from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,math,hashlib
P=Path(__file__).resolve().parent;R=P.parents[1];D=R/'diagnostics/earth_e_49_rigid_shoulder_v1';D.mkdir(parents=True,exist_ok=True);prev=R/'art_source/earth_e_49_cloth_patch_v1';PD=R/'diagnostics/earth_e_49_cloth_patch_v1'
proof=json.loads((prev/'COMPOSITE_PROOF.json').read_text());cs=proof['assembly']['core_scale'];ct=np.array(proof['assembly']['core_translation']);s=.079
sheet=Image.open(R/'art_source/earth_e_layered_parts_v1/raw.png').convert('RGBA');arm=sheet.crop((1024,0,1536,512));bg=Image.open(R/'art_source/earth_e_parts_density_review_v1/background-only-proposed-keep-mask.png').crop((1024,0,1536,512));a=np.array(arm);a[np.array(bg)==0,3]=0;arm=Image.fromarray(a)
ca=np.array([190.,250.]);anchor=ca*cs+ct;pa=np.array([226.5,137.5]);ph=np.array([321.5,434.]);target=np.array([43.,56.]);v=(ph-pa)*s;dest=target-anchor;theta=math.atan2(dest[1],dest[0])-math.atan2(v[1],v[0]);Q=np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta),math.cos(theta)]]);t=anchor-Q@pa*s
inv=Q.T/(4*s);off=-Q.T@t/s;coeff=(inv[0,0],inv[0,1],off[0],inv[1,0],inv[1,1],off[1]);A=arm.transform((512,512),Image.Transform.AFFINE,coeff,resample=Image.Resampling.BICUBIC);A.save(P/'arm49-rigid-HD4.png')
L=Image.open(PD/'layer49-lower.png').convert('RGBA');B=Image.open(PD/'layer49-core-back.png').convert('RGBA');F=Image.open(PD/'layer49-core-front.png').convert('RGBA');out=Image.new('RGBA',(512,512))
for x in [L,B,A,F]:out.alpha_composite(x)
out.save(P/'assembled49-rigid-HD4-RESEARCH.png');old=Image.open(prev/'assembled49-HD4-RESEARCH.png').convert('RGBA');src=Image.open(R/'diagnostics/earth_e_source_shadow_index_audit_v1/49-index18-excluded-NOT-SEMANTICALLY-CERTIFIED.png').convert('RGBA').resize((512,512),Image.Resampling.NEAREST)
for name,c in [('gray',(128,128,128,255)),('dark',(20,22,26,255)),('light',(235,235,235,255))]:
 b=Image.new('RGBA',(1536,512),c)
 for i,x in enumerate([src,old,out]):b.alpha_composite(x,(i*512,0))
 b.save(D/f'source-zero-rigid-{name}.png')
 b=Image.new('RGBA',(1000,650),c)
 for i,x in enumerate([old,out]):b.alpha_composite(x.crop((105,100,205,230)).resize((500,650)),(i*500,0))
 b.save(D/f'joints-zero-rigid-{name}.png')
core=sheet.crop((0,0,512,512));b=Image.new('RGBA',(1024,512),(90,90,90,255));b.alpha_composite(core);b.alpha_composite(arm,(512,0));dr=ImageDraw.Draw(b);dr.rectangle((175,235,205,265),outline='cyan',width=2);dr.ellipse((185,245,195,255),outline='cyan',width=2);dr.rectangle((723,120,754,155),outline='magenta',width=2);dr.rectangle((812,414,855,454),outline='yellow',width=2);b.save(D/'actual-cap-arm-anchors.png')
hand=Q@ph*s+t
j={'status':'fixed-density rigid assembly research not source passed','core_actual_cap_anchor_raw':ca.tolist(),'core_cap_anchor_uncertainty_raw':[175,235,205,265],'anchor_logical':anchor.tolist(),'arm_attachment_raw':pa.tolist(),'arm_hand_proxy_raw':ph.tolist(),'fixed_arm_scale':s,'screen_rotation_deg':math.degrees(theta),'rotation_convention':'x right y down; negative counterclockwise on screen','translation_logical':t.tolist(),'hand_logical':hand.tolist(),'source_hand_region':[40,53,46,59],'source_hand_center':target.tolist(),'arm_proxy_span_logical':float(np.linalg.norm(v)),'cap_to_target_span_logical':float(np.linalg.norm(dest)),'hand_center_residual':(hand-target).tolist(),'no_scale_fit':True,'unchanged_layers':['lower','core-back','core-front'],'source_uncertainty':'cap authoring anchor and hand surface region; not anatomical shoulder/elbow','inputs':[{'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [prev/'assembled49-HD4-RESEARCH.png',R/'art_source/earth_e_layered_parts_v1/raw.png',PD/'layer49-lower.png',PD/'layer49-core-back.png',PD/'layer49-core-front.png']]};(P/'TRANSFORM.json').write_text(json.dumps(j,indent=2)+'\n');print(json.dumps(j))
# Actual patch contribution transmittance after foreground layers, not silhouette guess.
pm=Image.open(prev/'actual-inner-feather-mask.png').convert('L');ls=.1028549998260168;lt=np.array([-1.4220149316246022,-.25108997251065546]);coeff2=(1/(4*ls),0,-lt[0]/ls,0,1/(4*ls),-lt[1]/ls);pm=pm.transform((512,512),Image.Transform.AFFINE,coeff2,resample=Image.Resampling.BILINEAR);pw=np.array(pm)/255.;la=np.array(L)[:,:,3]/255.;base=pw*la
oldA=Image.open(PD/'layer49-near-arm.png').convert('RGBA')
coverage={}
for label,aa in [('zero',oldA),('rigid',A)]:
 trans=np.ones((512,512))
 for tile in [B,aa,F]:trans*=1-np.array(tile)[:,:,3]/255.
 vis=base*trans;coverage[label]={'patch_visible_alpha_weight_sum_HD4_pixels':float(vis.sum()),'patch_visible_gt_half_HD4_pixels':int((vis>.5).sum())}
 highlight=out.copy();arr=np.array(highlight);sel=vis>.1;arr[sel,:3]=[255,0,220];Image.fromarray(arr).save(D/f'patch-contribution-visible-{label}.png')
j['patch_visibility']=coverage;j['unchanged_legs_pixels_y_ge248']=int(np.any(np.array(out)[248:]!=np.array(old)[248:],axis=2).sum());j['patch_visibility_caveat']='Transmittance estimates patch-source contribution, not a measure of visual quality or missing anatomy.';(P/'TRANSFORM.json').write_text(json.dumps(j,indent=2)+'\n');print(coverage,j['unchanged_legs_pixels_y_ge248'])
