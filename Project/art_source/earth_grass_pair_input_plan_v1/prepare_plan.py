from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[2]; D=Path(__file__).resolve().parent; S=P/'art_source/earth_vegetation_input_plan_v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
contract=json.loads((S/'source_contract.json').read_text()); groups={g['id']:g for g in contract['groups']}
# Source-only discrete palette classification, never a generated-art matte operation.
board=Image.new('RGBA',(144,48)); original=Image.new('RGBA',(144,48)); records=[]
for name,xy in [('grass239_54_30',(8,10)),('grass241_54_31',(80,10))]:
 g=groups[name]; a=np.array(Image.open(S/(name+'_source_native.png')).convert('RGBA')); shadow=np.all(a==[8,0,0,255],axis=2); body=a.copy();body[shadow]=0
 ys,xs=np.where(body[:,:,3]>0); bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
 im=Image.fromarray(body);board.alpha_composite(im,xy);original.alpha_composite(Image.fromarray(a),xy)
 records.append({'id':name,'source_native':str((S/(name+'_source_native.png')).relative_to(P)),'source_sha256':sha(S/(name+'_source_native.png')),'logical_canvas':g['logical_size'],'sheet_xy':xy,'visible_non_checker_bbox_xyxy':bbox,'visible_non_checker_pixels':int((body[:,:,3]>0).sum()),'excluded_exact_checker_pixels':int(shadow.sum()),'minimum_density2_body_dimensions':[(bbox[2]-bbox[0])*2,(bbox[3]-bbox[1])*2],'recommended_density8_body_dimensions':[(bbox[2]-bbox[0])*8,(bbox[3]-bbox[1])*8],'support_reads':g['anchor']['historical_reads'],'owners':g['owners_in_draw_order']})
# Correct stale historical contributor instance labels in NEW report only.
for r in records:
 for b in r['support_reads']:
  b['contributors']=[v.replace('@54,26','@54,31').replace('@55,26','@55,31') for v in b['contributors']]
board.save(D/'pair_geometry_native.png');original.save(D/'pair_original_native.png')
refs=[]
for source,box,name in [('earth_base_style_concept_v1/concept.png',(230,520,400,650),'concept_short_grass_material.png'),('earth_ground_plate_clean_regen_v4/raw.png',(650,200,906,456),'approved_ground_material.png')]:
 p=P/'art_source'/source;Image.open(p).crop(box).save(D/name);refs.append({'input':name,'source':str(p.relative_to(P)),'source_sha256':sha(p),'crop_xyxy':box,'use':'material/light only; no source geometry or terrain patch transfer'})
report={'status':'INPUT PLAN ONLY; no generation or registrations','scope':['239–240@(54,30)','241–242@(54,31)'],'geometry_sheet_size':[144,48],'classification':'Only exact opaque (8,0,0) checker palette removed in source interpretation sheet. Visible visual checker confirmed on native nearest enlargement. Other dark/neutral foliage retained. No hidden leaf reconstruction; dark non-checker pixels are not asserted to be botanically identified. This is NOT an RGB cleanup rule for generated assets.','records':records,'material_inputs':refs,'fixed_ratio':'Both source canvases at identical scale; A64x27, B58x26. A support centers local(21,24),(40,24); B(21,22),(34,22). Keep two entire clumps, not four owner plants.','density':'Minimum actual body density2 each axis after registration; aim8. At8 sheet1152x384, A512x216 logical canvas, B464x208. Tool output dimensions not guaranteed. No upscaled old pixels counted as new density.','registration_boundary':'Future uniform scale+translation per whole group, never per owner or anisotropic warp; use support bands not invented physical roots. Preserve flags0 and two identities/order; fullcanvas disjoint owner assignment and exact RGBA recomposition if approved. No new cast shadows.','inputs_for_one_generation':['pair_geometry_native.png','concept_short_grass_material.png','approved_ground_material.png']}
(D/'INPUT_PLAN.json').write_text(json.dumps(report,indent=2)+'\n')
# Strict complete-source aliases, no registrations created.
c=groups['round_shrub_57_38'];proof=[]
for name in ['round_shrub_51_44','round_shrub_64_45']:
 g=groups[name];delta=[g['world_bounds_xyxy'][i]-c['world_bounds_xyxy'][i] for i in range(2)];dc=[g['root_or_center_owner_cell'][i]-c['root_or_center_owner_cell'][i] for i in range(2)];checks=[]
 for a,b in zip(c['owners_in_draw_order'],g['owners_in_draw_order']):
  fields=['frame_index','source_cell','flag','layer','original_canvas','crop','ignored_frame_offset','atlas_page','atlas_rect','frame_rgba_sha256']
  checks.append({'center':a['key'],'target':b['key'],'equal_fields':{k:a[k]==b[k] for k in fields},'center_source_cell':a['source_cell'],'target_source_cell':b['source_cell'],'world_rect_delta':[b['world_rect'][i]-a['world_rect'][i] for i in range(4)],'cell_delta':[b['cell'][i]-a['cell'][i] for i in range(2)],'sort_y_delta':b['sort_y']-a['sort_y'],'stable_source_order_delta':b['stable_source_order']-a['stable_source_order']})
 native=np.array_equal(np.array(Image.open(S/(name+'_source_native.png'))),np.array(Image.open(S/'round_shrub_57_38_source_native.png')))
 strict=native and all(all(x['equal_fields'].values()) and x['world_rect_delta']==delta+[0,0] and x['cell_delta']==dc and x['sort_y_delta']==dc[1] and x['stable_source_order_delta']==100*dc[0]+dc[1] for x in checks)
 proof.append({'target':name,'world_delta':delta,'cell_delta':dc,'native_rgba_equal':native,'strict_source_translation':strict,'owners':checks,'native_sha256':sha(S/(name+'_source_native.png'))})
(D/'SHRUB_REUSE_PROOF.json').write_text(json.dumps({'center':'round_shrub_57_38','center_native_sha256':sha(S/'round_shrub_57_38_source_native.png'),'scope':'Source identity proof only. Different surroundings require independent original routes and layering diagnostics before any reuse promotion. No registration or runtime change.','targets':proof},indent=2)+'\n')
diag=P/'diagnostics/art_source/earth_grass_pair_input_plan_v1';diag.mkdir(parents=True,exist_ok=True)
bg=Image.new('RGBA',(144,96),(110,110,110,255));bg.alpha_composite(original,(0,0));bg.alpha_composite(board,(0,48));bg.save(diag/'source_original_and_body_1x.png');bg.resize((1152,768),Image.Resampling.NEAREST).save(diag/'source_original_and_body_8x.png')
print(json.dumps({'grass':[{k:r[k] for k in ['id','visible_non_checker_bbox_xyxy','excluded_exact_checker_pixels','minimum_density2_body_dimensions']} for r in records],'shrub':[{k:t[k] for k in ['target','world_delta','strict_source_translation']} for t in proof]},indent=2))
