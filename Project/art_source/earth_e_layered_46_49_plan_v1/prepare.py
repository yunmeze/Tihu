from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil
P=Path(__file__).resolve().parent;A=P.parent;D=P.parents[1]/'diagnostics/earth_e_layered_46_49_plan_v1';D.mkdir(parents=True,exist_ok=True)
S=P.parents[1]/'diagnostics/earth_e_source_shadow_index_audit_v1'
board=Image.new('RGBA',(1536,768),(35,39,44,255))
for i,n in enumerate([46,49]):
 im=Image.open(S/f'{n}-index18-excluded-NOT-SEMANTICALLY-CERTIFIED.png').convert('RGBA');board.alpha_composite(im.resize((768,768),Image.Resampling.NEAREST),(768*i,0))
board.save(P/'source46-left49-right-full128-6x.png')
shutil.copy2(A/'earth_hero_e_walk_plan_v3/approved-E-design-only.png',P/'approved-E-idle-design-only.png')
idle=Image.open(A/'earth_hero_e_idle_v1/body-density4.png').convert('RGBA').crop((0,0,512,512));idle.save(P/'approved-E-idle9-HD4-full128.png')
# Inspection crop sheet only: no component masks or pose composite made.
boxes={'head_identity':[32,14,48,29],'torso_waist_identity':[31,25,49,49],'sleeve_forearm_glove_identity':[30,29,41,56],'trouser_boot_material_identity':[29,47,50,88]}
sheet=Image.new('RGBA',(1100,600),(45,49,53,255));d=ImageDraw.Draw(sheet)
for i,(name,r) in enumerate(boxes.items()):
 crop=idle.crop(tuple(v*4 for v in r));sheet.alpha_composite(crop,(20+i*270,40));d.text((20+i*270,15),name,fill='white');d.text((20+i*270,230),'STUDY CROP, NOT READY PART',fill='white')
sheet.save(D/'identity-study-crops.png')
j={'status':'plan_only_new_part_generation_pending','base_identity_source':str(A/'earth_hero_e_idle_v1/body-density4.png'),'identity_crops_logical':boxes,'five_art_items':['shared_head_torso_waist','near_arm46_whole_sleeve_guard_hand','near_arm49_whole_sleeve_guard_hand','lower_pair46_pelvis_to_both_boots','lower_pair49_pelvis_to_both_boots'],'display_inputs':[{'path':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(P.glob('*.png'))],'rig_scope':'future separate diagnostic only, no runtime changes','input_transform':'source full128 nearest6; idle HD4 full128; identity fragment image is design only'}
(P/'INPUT_PROVENANCE.json').write_text(json.dumps(j,indent=2)+'\n')
