from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
O=Path(__file__).resolve().parent;P=O.parents[1];I=P/'art_source/earth_vegetation_input_plan_v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
frozen=P/'art_source/earth_vegetation_stage_archive_v1/MINIMAL_SHA256.json';prior=json.loads(frozen.read_text())
assert sha(frozen)=='dd2e94edd584e40cfb753ff4d1be27dee12928746bc497b2e73391bc69ee8841'
for f in prior['files']:assert sha(P/f['path'])==f['sha256']
source=json.loads((I/'source_contract.json').read_text());gs=[g for g in source['groups']if g['family']=='upright_tree'];assert [g['root_or_center_owner_cell']for g in gs]==[[50,41],[61,51]]
im=[Image.open(I/(g['file_prefix']+'_source_native.png')).convert('RGBA')for g in gs];assert np.array_equal(np.asarray(im[0]),np.asarray(im[1]))
checks=[]
for a,b in zip(gs[0]['owners_in_draw_order'],gs[1]['owners_in_draw_order']):
 assert a['frame_index']==b['frame_index'];assert a['source_cell']==b['source_cell'];assert a['original_canvas']==b['original_canvas'];assert a['crop']==b['crop'];assert a['atlas_rect']==b['atlas_rect'];assert a['frame_rgba_sha256']==b['frame_rgba_sha256'];assert a['flag']==b['flag']and a['layer']==b['layer']
 assert [b['cell'][k]-a['cell'][k]for k in[0,1]]==[11,10];assert [b['world_rect'][k]-a['world_rect'][k]for k in[0,1]]==[528,320];assert b['world_rect'][2:]==a['world_rect'][2:];assert b['sort_y']-a['sort_y']==10;assert b['stable_source_order']-a['stable_source_order']==1110
 checks.append({'frame':a['frame_index'],'left_key':a['key'],'bottom_key':b['key'],'same_frame_rgba_and_source_cell':True,'world_delta':[528,320],'cell_delta':[11,10],'sort_y_delta':10,'stable_source_order_delta':1110})
# Correct instance-local contributor IDs in this NEW contract only; frozen historical inputs untouched.
instances=[]
for g in gs:
 g=json.loads(json.dumps(g));x,y=g['root_or_center_owner_cell'];g['anchor']['contributors_at_read_point']=[f'Plant:299@{x},{y}'];g['anchor']['wood_foot_continuation_owner']=f'Plant:302@{x+1},{y+4}';instances.append(g)
T=P/'art_source/earth_first_tree_boundary_repair_v2/raw.png';crop=[485,1060,535,1170];Image.open(T).crop(crop).save(O/'first_tree_bark_interior_reference.png')
refs=[I/'upright_tree_61_51_source_native.png',I/'concept_tree_branch_foliage.png',P/'art_source/earth_round_shrub_input_plan_v1/tree_v2_foliage_light_reference.png',O/'first_tree_bark_interior_reference.png']
plan={'status':'one whole upright-tree generation input plan only, not authorized/executed','scope':'Only complete instances50,41 and61,51; no whole-map reuse','strict_translation_reuse':{'composite_rgba_equal':True,'native_size':[281,298],'composite_rgba_sha256':hashlib.sha256(np.asarray(im[0]).tobytes()).hexdigest(),'world_delta_from_left_to_bottom':[528,320],'per_owner':checks,'meaning':'One source family with identical pixels and relative owners. One generated master can be translated to these two placements only after each placement passes independent sorting/route review.'},'instances':instances,'input_images':[{'number':i+1,'path':str(p.relative_to(P)),'sha256':sha(p),'size':list(Image.open(p).size)}for i,p in enumerate(refs)],'new_bark_reference_crop':{'source':str(T.relative_to(P)),'sha256':sha(T),'crop_xyxy':crop,'role':'interior bark only, no trunk silhouette transfer'},'geometry':{'source_canvas':[281,298],'root_local':[125,294],'root_manual_uncertainty_logical_px':4,'root_read_region':[121,290,129,298],'wood_foot_region':[104,278,152,298],'source_root_low_trim_caution':True,'minimum_density':2,'minimum_canvas_at_density2':[562,596],'recommended_density4_layout':[1124,1192],'source_shadow304_is_not_foliage':True,'no_exact_body_shadow_segmentation_claim':True},'frozen_41_sha256':sha(frozen),'frozen_41_unchanged':True,'historical_metadata_correction':'Frozen source left-instance anchor inherited contributor string299@61,51 though its world anchor was translated correctly. This new plan corrects only the local contributor string to299@50,41; frozen originals unchanged.'}
(O/'INPUT_PLAN.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
files=['README.md','prompt_pending.txt','prepare_plan.py','INPUT_PLAN.json','first_tree_bark_interior_reference.png'];(O/'ARCHIVE_SHA256.json').write_text(json.dumps({'files':[{'path':n,'bytes':(O/n).stat().st_size,'sha256':sha(O/n)}for n in files]},indent=2)+'\n');print('STRICT_TRANSLATION_PASS',len(checks),'OWNERS_EACH');print('MANIFEST_SHA',sha(O/'ARCHIVE_SHA256.json'))
