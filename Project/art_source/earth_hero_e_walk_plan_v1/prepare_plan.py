from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil
P=Path(__file__).resolve().parent;A=P.parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
src=A/'earth_hero_e_input_plan_v1/source-walk-complete-pose-main-8x.png';shutil.copyfile(src,P/'source45-50-complete-pose-main-8x.png')
im=Image.open(A/'earth_hero_e_idle_v1/raw-v1.png').convert('RGBA')
parts={'E_head_side_identity':(217,41,322,140),'E_chest_side_black_layer':(268,153,330,272),'E_red_shoulder':(199,146,262,236),'E_waist_side_plate':(240,280,330,351),'E_black_thigh_fabric':(252,402,309,461),'E_glove':(193,351,265,419),'E_knee':(188,509,243,572),'E_boot':(189,637,310,703)}
b=Image.new('RGBA',(800,430));d=ImageDraw.Draw(b)
for i,(name,r) in enumerate(parts.items()):
 x=i%4*200+10;y=i//4*215+30;d.text((x,y-20),name,fill='white');b.alpha_composite(im.crop(r),(x,y))
b.save(P/'current-E-idle9-disconnected-parts.png')
# Small SE material patches only, not its head, full torso or leg silhouettes.
s=Image.open(A/'earth_hero_se_idle_v1/raw-v1.png').convert('RGBA');patches={'SE_red_paint':(150,193,190,225),'SE_silver_plate':(246,210,285,242),'SE_black_thigh_fabric':(224,410,262,449)}
b=Image.new('RGBA',(420,120));d=ImageDraw.Draw(b)
for i,(name,r) in enumerate(patches.items()):d.text((i*140+6,5),name,fill='white');b.alpha_composite(s.crop(r),(i*140+15,35))
b.save(P/'approved-SE-material-swatches-only.png')
analysis=json.loads((A/'earth_hero_e_input_plan_v1/SOURCE_PHASE_ANALYSIS.json').read_text())['walk']
(P/'SOURCE_PHASE_ANALYSIS.json').write_text(json.dumps({'frames':analysis,'source_reading_boundary':'surface proxies only; screen-low foot is not proved support/contact; anatomical left/right not proved','crown_uncertainty_px':1,'boot_uncertainty_px':2,'clothing_hand_uncertainty_px':3},indent=2)+'\n')
inputs=['source45-50-complete-pose-main-8x.png','current-E-idle9-disconnected-parts.png','approved-SE-material-swatches-only.png']
j={'status':'prepared_not_generated_waiting_idle_runtime_review_and_parent_authorization','inputs':[{'path':f,'sha256':sha(P/f)} for f in inputs],'E_raw':{'path':'art_source/earth_hero_e_idle_v1/raw-v1.png','sha256':sha(A/'earth_hero_e_idle_v1/raw-v1.png'),'crop_rects':parts},'SE_raw':{'path':'art_source/earth_hero_se_idle_v1/raw-v1.png','sha256':sha(A/'earth_hero_se_idle_v1/raw-v1.png'),'crop_rects':patches},'source_common_crop':[12,8,76,96],'source_grid':[3,2],'source_scale':8,'logical_root':[16,64],'crop_root':[4,56],'ticks':7,'runtime_changed':False}
(P/'INPUT_PROVENANCE.json').write_text(json.dumps(j,indent=2)+'\n')
manifest={'status':'archive_allowlist_only_no_git','files':[{'path':f.name,'sha256':sha(f)} for f in sorted(P.iterdir()) if f.is_file() and f.name!='GIT_SAVE_MANIFEST.json'],'exclude':['diagnostics/**']};(P/'GIT_SAVE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
