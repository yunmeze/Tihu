from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[1];D=R/'diagnostics/earth_e_49_farhand_mask_plan_v1';D.mkdir(exist_ok=True,parents=True)
oldp=R/'art_source/earth_hero_e_49_control_v2/raw.png';old=Image.open(oldp).convert('RGBA');current=Image.open(R/'art_source/earth_e_49_cloth_patch_v1/old49-with-masked-cloth-patch-COMPOSITE.png').convert('RGBA');crop=[435,430,520,580]
# Conservative visibly external fingertip candidates. These do not claim the obscured body contour.
safe=[[(480,476),(485,476),(485,482),(480,488),(476,492),(474,490),(477,484)],[(473,500),(476,502),(475,509),(472,512),(470,511),(470,508)]]
# Remaining hand/glove surface proposed review envelope, excludes retained metal belt/hip plate.
full=[(468,476),(485,476),(485,483),(479,491),(475,495),(473,500),(476,503),(475,511),(467,515),(461,510),(461,501),(465,494),(469,487)]
# Cloth-facing boundary uncertainty: cutting this risks notch/hole. No fabricated anatomy.
uncertain=[(468,482),(474,484),(471,493),(469,500),(472,507),(467,514),(461,510),(461,501),(465,494)]
ms=Image.new('L',old.size);mf=Image.new('L',old.size);mu=Image.new('L',old.size)
for poly in safe:ImageDraw.Draw(ms).polygon(poly,fill=255)
ImageDraw.Draw(mf).polygon(full,fill=255);ImageDraw.Draw(mu).polygon(uncertain,fill=255)
for name,m in [('EXTERIOR-TIPS-proposed-remove-mask',ms),('WHOLE-RESIDUE-review-envelope-NOT-APPROVED',mf),('CLOTH-INTERFACE-uncertain-mask',mu)]:m.save(P/f'{name}.png')
b=Image.new('RGBA',old.size,(110,110,110,255));b.alpha_composite(old);dr=ImageDraw.Draw(b)
for poly in safe:dr.line(poly+[poly[0]],fill=(0,255,255),width=1)
dr.line(full+[full[0]],fill=(255,60,220),width=1);dr.line(uncertain+[uncertain[0]],fill=(255,220,0),width=1);b.crop(crop).resize((680,1200),Image.Resampling.NEAREST).save(D/'farhand-three-regions-8x.png')
a=np.array(current);trial=a.copy();trial[np.array(ms)>0,3]=0;trial=Image.fromarray(trial)
for name,c in [('gray',(128,128,128,255)),('light',(235,235,235,255)),('dark',(20,22,26,255))]:
 board=Image.new('RGBA',(1020,900),c)
 for i,v in enumerate([old,current,trial]):board.alpha_composite(v.crop(crop).resize((510,900),Image.Resampling.NEAREST),(i*340,0)) if False else None
 board=Image.new('RGBA',(1020,600),c)
 for i,v in enumerate([old,current,trial]):board.alpha_composite(v.crop(crop).resize((340,600),Image.Resampling.NEAREST),(i*340,0))
 board.save(D/f'original-current-TIPS-ONLY-proposal-{name}.png')
arr=np.array(old);bounds=(slice(476,515),slice(461,486));same=np.all(arr[bounds]==a[bounds]);n=int(((np.array(ms)>0)&(a[:,:,3]>0)).sum());j={'status':'mask proposal only; no current assembly changed','old_raw_sha256':hashlib.sha256(oldp.read_bytes()).hexdigest(),'evidence_crop':crop,'module_top_y':476,'visible_residue_bbox_review':[461,476,486,515],'safe_external_fingertip_polygons':safe,'whole_residue_review_polygon':full,'cloth_interface_uncertainty_polygon':uncertain,'old_raw_equals_current_composite_in_residue_region':bool(same),'candidate_tip_removal_nonzero_alpha_pixels':n,'mapping_to_logical':{'s':.1028549998260168,'t':[-1.4220149316246022,-.25108997251065546]},'no_final_mask_applied':True};(P/'PROVENANCE.json').write_text(json.dumps(j,indent=2)+'\n');print(j)
