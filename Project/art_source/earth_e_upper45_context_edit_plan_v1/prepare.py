from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,math,hashlib
P=Path(__file__).resolve().parent;R=P.parents[1];D=R/'diagnostics/earth_e_upper45_context_edit_plan_v1';D.mkdir(parents=True,exist_ok=True)
S=R/'art_source/earth_e_four_phase_rigid_study_v1';V=R/'art_source/earth_hero_e_walk_v2';raw=Image.open(V/'raw-v2.png').convert('RGBA').crop((0,0,512,512));reg=json.loads((V/'registration-v2.json').read_text());rr=reg['records'][0];s=reg['common_uniform_scale_raw_to_logical'];t=np.array(rr['translation_logical'])
# Visible old upper pants ONLY; exclude old arm/hand/belt and old shin modules.
poly=[(204,254),(243,251),(270,264),(294,303),(302,330),(307,350),(294,362),(263,366),(250,345),(222,320),(203,343),(178,353),(154,336),(171,311),(195,288)]
m=Image.new('L',(512,512));ImageDraw.Draw(m).polygon(poly,fill=255);m=np.array(m)>0;m&=np.array(Image.open(S/'45-fixed-exclusive-mask.png'))>0
a=np.array(raw);a[~m,3]=0;old=Image.fromarray(a).transform((512,512),Image.Transform.AFFINE,(1/(4*s),0,-t[0]/s,0,1/(4*s),-t[1]/s),resample=Image.Resampling.BICUBIC)
old.save(P/'old45-upper-REPLACEMENT-CONTEXT.png');Image.fromarray((m*255).astype('uint8')).save(P/'old45-upper-extraction-RAW-mask.png')
# Same arm family, independent rigid low-back candidate for context; never replace with whole46.
sheet=Image.open(R/'art_source/earth_e_layered_parts_v1/raw.png').convert('RGBA');arm=sheet.crop((512,0,1024,512));aa=np.array(arm);keep=np.array(Image.open(R/'art_source/earth_e_parts_density_review_v1/background-only-proposed-keep-mask.png').crop((512,0,1024,512)));aa[keep==0,3]=0
pa=np.array([230.5,132.5]);ph=np.array([271,436.5]);anchor=np.array([31.3023255814,34.8449612403]);target=np.array([33.,57.]);v=(ph-pa)*.079;des=target-anchor;th=math.atan2(des[1],des[0])-math.atan2(v[1],v[0]);Q=np.array([[math.cos(th),-math.sin(th)],[math.sin(th),math.cos(th)]]);at=anchor-Q@pa*.079;inv=Q.T/(4*.079);off=-Q.T@at/.079
A=Image.fromarray(aa).transform((512,512),Image.Transform.AFFINE,(inv[0,0],inv[0,1],off[0],inv[1,0],inv[1,1],off[1]),resample=Image.Resampling.BICUBIC);A.save(P/'arm45-context-rigid.png')
protect=Image.new('RGBA',(512,512));layers=[]
for side in ['left','right']:layers.append(Image.open(S/f'45-{side}-rigid-HD4.png').convert('RGBA'))
for nm in ['back']:
 z=Image.new('RGBA',(512,512));z.alpha_composite(Image.open(R/f'diagnostics/earth_e_49_cloth_patch_v1/layer49-core-{nm}.png'),(4,0));layers.append(z)
layers.append(A)
z=Image.new('RGBA',(512,512));z.alpha_composite(Image.open(R/'diagnostics/earth_e_49_cloth_patch_v1/layer49-core-front.png'),(4,0));layers.append(z)
context=old.copy()
for l in layers:protect.alpha_composite(l);context.alpha_composite(l)
context.save(P/'input-complete45-context.png');protect.save(P/'protected-core-arm-shins.png')
support=np.array(Image.open(R/'art_source/earth_e_upper45_47_v1/45-fixed-support-HD4-mask.png'))>0;oldalpha=np.array(old)[:,:,3]>0;protected=np.array(protect)[:,:,3]>0
union=(oldalpha|support)&~protected
for nm,sel in [('old-upper-remove',oldalpha&~protected),('new-upper-support',support&~protected),('fixed-union-edit',union),('protected-core-hand-shins',protected)]:Image.fromarray((sel*255).astype('uint8')).save(P/f'{nm}-HD4-mask.png')
# Native full-canvas pose authority, without a destructive reinterpretation.
src=Image.open(R/'diagnostics/earth_e_source_shadow_index_audit_v1/45-index18-excluded-NOT-SEMANTICALLY-CERTIFIED.png').convert('RGBA');src.resize((512,512),Image.Resampling.NEAREST).save(P/'input-source45-full128.png')
b=Image.new('RGBA',(1536,512),(128,128,128,255));b.alpha_composite(context,(0,0));ov=np.array(context);ov[union,:3]=[255,0,200];ov[union,3]=180;b.alpha_composite(Image.fromarray(ov),(512,0));pr=np.array(context);pr[protected,:3]=[40,210,180];pr[protected,3]=220;b.alpha_composite(Image.fromarray(pr),(1024,0));b.save(D/'context-union-protected.png')
Image.fromarray(ov).save(P/'input-union-guide.png')
j={'status':'preparation only, no generation authorized this turn','canvas':[512,512],'logical_canvas':[128,128],'root_HD4':[64,256],'old_upper_raw_polygon':poly,'old_v2_density':s,'old_v2_translation':t.tolist(),'arm_context_family':46,'arm_density':.079,'arm_rotation_deg':math.degrees(th),'arm_translation':at.tolist(),'arm_hand_proxy':(Q@ph*.079+at).tolist(),'arm_note':'new rigid context candidate only; not phase45 action approved','union_HD4_pixels':int(union.sum()),'union_protected_intersection':int((union&protected).sum()),'union_bbox':Image.fromarray((union*255).astype('uint8')).getbbox(),'preservation':'future composite starts original context; copy only frozen union, restore every outside RGBA; alpha>0 core/arm/shins removed from edit domain; no new shadow','feather':'none outward; at most 1 HD4 pixel inward if later explicitly recorded','view':'screen-right side / slight three-quarter SIDE, same commoncore camera; never front product view','edit_scope':'whole visible upper-pants replacement inside localized union, not tiny seam and not whole person'}
(P/'PLAN.json').write_text(json.dumps(j,indent=2)+'\n')
prompt="""Edit image1 locally: replace only the black upper-pants area indicated pink in image3. Keep this EXACT screen-right-facing side-view / slight three-quarter SIDE character, the same camera as the head and torso. This is clothing on the existing side-facing walking character, NEVER a front-facing pants product photograph. Image2 is original phase45 pose authority.
Rebuild the compact black waist-to-knee fabric in the short spread-step pose, joining the existing waist and two fixed shin-root interfaces. Preserve side-view thigh overlap and the distinct left-screen higher rear cuff / right-screen lower front cuff. Keep all head, chest, red shoulder, sleeves, hands, belt, shin armor and boots exactly unchanged; no scale, position or pose change. No extra side plates or new belt. Black woven fabric, restrained seams, same upper-left warm lighting. No gold trim. Maintain original transparent background and silhouette outside the specified pants region. Only pants fabric and necessary transparent exterior inside the pink region may change. Pink is a location guide, never output color. The final composite will use ONLY the frozen pants region; do not move the entire person to solve the fit."""
(P/'prompt-PENDING-APPROVAL.txt').write_text(prompt+'\n')
refs=[P/'input-complete45-context.png',P/'input-source45-full128.png',P/'input-union-guide.png']
(P/'INPUT_SHA.json').write_text(json.dumps([{'path':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in refs],indent=2)+'\n');print(j)
