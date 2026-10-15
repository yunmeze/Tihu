from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
O=Path(__file__).parent;P=O.parents[1];D=P/'diagnostics/earth-npc-lingyunzi-v2';D.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
im=Image.open(O/'raw-v2.png').convert('RGBA');assert im.size==(2172,724)
# Visible surface points in phase0 only, raw source113+registered(41,53).
# Crown ignored. Manual uncertainty +/-2 source and +/-8 generated pixels.
names=['visible_face_center','overlapping_hands_center','left_boot_lower_edge','right_boot_lower_edge']
src=np.array([[55.5,75.],[55.5,92.],[48.5,124.],[63.,124.]])
gen=np.array([[292.,150.],[292.,355.],[211.,684.],[382.,684.]])
s=float(((gen-gen.mean(0))*(src-src.mean(0))).sum()/((gen-gen.mean(0))**2).sum());tr=src.mean(0)-s*gen.mean(0)
phases=[im.crop((j*543,0,(j+1)*543,724))for j in range(4)];bboxes=[]
for phase in phases:bboxes.append(phase.getchannel('A').point(lambda x:255 if x>=128 else 0).getbbox())
for density in [1,2,4]:
    strip=Image.new('RGBA',(512*density,160*density))
    for j,phase in enumerate(phases):
        r=phase.transform((128*density,160*density),Image.Transform.AFFINE,(1/(s*density),0,-tr[0]/s,0,1/(s*density),-tr[1]/s),resample=Image.Resampling.BICUBIC);strip.paste(r,(j*128*density,0))
    strip.save(D/f'candidate-common-register-{density}x.png')
    source=Image.open(P/'art_source/earth_npc_input_plan_v1/lingyunzi/source-four-registered-native.png').resize((512*density,160*density),Image.Resampling.NEAREST)
    board=Image.new('RGBA',(512*density,320*density),(95,102,108,255));board.alpha_composite(source,(0,0));board.alpha_composite(strip,(0,160*density));board.convert('RGB').save(D/f'source-candidate-four-phase-{density}x.png')
# Readable tighter display preserves common logical crop across every phase and both rows.
board=Image.open(D/'source-candidate-four-phase-2x.png');# no production copy
A=np.asarray(im.getchannel('A'))
r={'status':'hold_for_four_phase_review_no_runtime','raw_sha256':sha(O/'raw-v2.png'),'raw_size':list(im.size),'raw_cell_size':[543,724],'source_ids':[113,114,115,116],'generation_calls':1,'prompt_sha256':sha(O/'prompt.txt'),'request_sha256':sha(O/'tool-request.json'),'raw_alpha0_pixels':int((A==0).sum()),'raw_alpha1_to7_pixels':int(((A>0)&(A<8)).sum()),'raw_phase_alpha128_bbox':bboxes,'uniform_registration':{'scale_raw_to_logical':s,'translation_to_logical_canvas':tr.tolist(),'raw_pixels_per_logical':1/s,'rotation':0,'per_phase_fit':False,'double_apply_source_offsets':False,'density4_production_texture_created':False},'phase_measurements':{'candidate_scalp_top_delta_logical':[s*(b[1]-bboxes[0][1])for b in bboxes],'candidate_visible_bottom_delta_logical':[s*(b[3]-bboxes[0][3])for b in bboxes],'source_old_crown_top_delta':[0,2,2,1],'source_alpha_bottom_delta_including_checker':[0,1,1,0],'warning':'Different identity head top is not directly homologous to old crown. Relative temporal motion is evidence; refine using face/hands/boots. Source alpha bottom is not exact sole.'},'landmarks_phase0':[{'name':n,'source_registered':a.tolist(),'generated_raw':b.tolist(),'residual_logical_px':float(np.linalg.norm(s*b+tr-a))}for n,a,b in zip(names,src,gen)],'manual_uncertainty':{'source_px':2,'generated_px':8,'note':'surface feature centers and boot extrema only, no skeletal claim'},'scope':'One authorized whole-sheet v2 edit; no further generation, no runtime, no per-phase morph, no production promotion','source_input_hashes':{str(f.relative_to(P)):sha(f)for f in [P/'art_source/earth_npc_input_plan_v1/lingyunzi/source-four-pose-4x.png',P/'art_source/earth_npc_lingyunzi_candidate_v1/raw-v1.png']}}
(O/'review.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r,ensure_ascii=False,indent=2))
