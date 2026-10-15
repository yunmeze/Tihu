from pathlib import Path
import json,hashlib
from PIL import Image
O=Path(__file__).resolve().parent;P=O.parents[1];I=P/'art_source/earth_vegetation_input_plan_v1';T=P/'art_source/earth_first_tree_boundary_repair_v2/raw.png'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((I/'ARCHIVE_SHA256.json').read_text())
for f in old['files']:assert sha(I/f['path'])==f['sha256']
b=[220,550,380,710];Image.open(T).crop(b).save(O/'tree_v2_foliage_light_reference.png')
refs=[I/'round_shrub_57_38_source_native.png',I/'concept_shrub_material.png',O/'tree_v2_foliage_light_reference.png'];g=next(g for g in json.loads((I/'source_contract.json').read_text())['groups']if g['id']=='round_shrub_57_38')
plan={'status':'generation input plan only; no shrub generation authorized or executed','input_images':[{'number':i+1,'path':str(p.relative_to(P)),'sha256':sha(p),'size':list(Image.open(p).size)}for i,p in enumerate(refs)],'tree_reference_crop':{'raw_path':str(T.relative_to(P)),'raw_sha256':sha(T),'crop_xyxy_exclusive':b,'role':'secondary interior leaf material/light only; never tree shape/trunk/roots'},'source_group':g,'physical_root':None,'visible_lower_green_leaf_band_local_xyxy':[40,94,95,100],'band_limit':'Approximate foliage support band, not physical root or surveyed plane','no_new_ground_shadow':True,'minimum_true_density':2,'source_native_is_not_hd':True,'authorities':[{'path':str(p.relative_to(P)),'sha256':sha(p)}for p in[P/'docs/EARTH_ART_BIBLE_V1.md',P/'art_source/earth_base_style_concept_v1/concept.png']],'frozen_40_verified':True}
(O/'INPUT_PLAN.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
files=['README.md','prompt_pending.txt','prepare_plan.py','INPUT_PLAN.json','tree_v2_foliage_light_reference.png'];(O/'ARCHIVE_SHA256.json').write_text(json.dumps({'files':[{'path':n,'sha256':sha(O/n),'bytes':(O/n).stat().st_size}for n in files]},indent=2)+'\n');print('PLAN_READY_NO_GENERATION',sha(O/'ARCHIVE_SHA256.json'))
