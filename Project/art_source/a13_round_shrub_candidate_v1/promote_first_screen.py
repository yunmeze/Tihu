"""Promote exact approved raw-resolution shrub pieces to normal runtime paths."""
from pathlib import Path
import copy,hashlib,json,shutil
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent
O=P/'assets/scifi/environment/a13_round_shrub_v1';O.mkdir(parents=True,exist_ok=True)
T=D/'technical_v1';S=P/'art_source/a13_round_shrub_source/source-group-contract.json'
SH=P/'assets/scifi/environment/a13_round_shrub_shadow_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
res=lambda p:'res://'+str(p.relative_to(P))
source=json.loads(S.read_text());tech=json.loads((T/'registration.json').read_text());reuse=json.loads((T/'first-screen-reuse-index.json').read_text())
mp=json.loads((P/'data/maps/A13.json').read_text());manifest=json.loads((P/'assets/original/manifest.json').read_text());pack=manifest['packs']['Map/Res/Plant'];mh=mp['height'];shadow=json.loads((SH/'shadow.json').read_text());selected=json.loads((SH/'selection.json').read_text())
assert selected['selected_variant']=='limited_lower_foliage_band_B'
assert sha(D/'raw.png')==tech['whole_shrub_registration']['sha256']==sha(SH/'whole_shrub.png')
assert sha(SH/'contact-band.json')==selected['selected_contract_sha256']
centers=[[51,44],[57,38],[58,51],[64,45]]
texture_specs={}
for owner in tech['owners']:
 frame=owner['frame_id'];inp=T/f'owner-{frame}.png';out=O/inp.name
 assert sha(inp)==owner['texture_sha256']
 shutil.copyfile(inp,out)
 assert sha(out)==sha(inp)
 im=np.array(Image.open(out).convert('RGBA'))
 assert list(Image.open(out).size)==[1363,1154]
 texture_specs[frame]={'texture':res(out),'texture_sha256':sha(out),'texture_size':[1363,1154],'region':[0,0,1363,1154], 'stored_rgba_pixels':int(np.any(im!=0,2).sum()),'alpha_positive_pixels':int((im[:,:,3]>0).sum()),'stored_support_bbox_xyxy':owner['stored_support_bbox_xyxy']}
# Every source_cell comes from the actual TARGET map, including differing floor IDs.
all_owners=[];instances=[]
for center in centers:
 g=next(g for g in source['groups'] if g['center_owner_cell']==center)
 rg=next(g for g in reuse['groups'] if g['center_owner_cell']==center)
 sg=next(g for g in shadow['instances'] if g['center_owner_cell']==center)
 assert rg['candidate_raw_world_origin']==sg['whole_raw_world_origin']
 owners=[]
 for original in g['owners_in_draw_order']:
  item=copy.deepcopy(original);x,y=item['cell'];cell_index=x*mh+y;actual=mp['cells'][cell_index]
  assert actual==original['source_cell'] and actual[2]==2 and actual[3]==item['frame_id']
  frame=pack['frames'][str(item['frame_id'])];layer=0 if actual[1]in[1,-2]else(2 if actual[1]==2 else 1)
  item.update({'pack':'Map/Res/Plant','frame_index':item['frame_id'],'source_cell':copy.deepcopy(actual),'source_cell_index':cell_index,'source_map_byte_offset':mp['cellByteOffsets'][cell_index], 'flag':actual[1],'layer':layer,'sort_y':y,'stable_source_order':cell_index,'sort_tuple':[layer,y,cell_index],'source_rgba_sha256':frame['rgba_sha256'],'offset_ignored':frame['offset'], 'world_top_left':rg['candidate_raw_world_origin'],'scale':rg['scale'],'instance_center_owner_cell':center,'actual_woody_root':None})
  item.update(texture_specs[item['frame_id']]);owners.append(item);all_owners.append(item)
 keys=[o['key']for o in owners]
 assert keys==sg['requires_suppressed_source_keys']
 instances.append({'center_owner_cell':center,'family_anchor_cell':[center[0],center[1]-3],'family_anchor_meaning':'top143 source owner, not a physical root','world_top_left':rg['candidate_raw_world_origin'],'scale':rg['scale'],'actual_woody_root':None,'visible_leaf_proxy_raw':[778,1103],'visible_leaf_proxy_world':sg['leaf_proxy_world'],'nominal_first_screen_visibility':rg['nominal_first_screen_visibility'],'owners':owners,'suppress_source_keys':keys,'shadow_contract':res(SH/'contact-band.json'),'shadow_selection':res(SH/'selection.json'),'shadow_variant':'limited_lower_foliage_band_B','shadow_passes':1,'atomic_unit':'complete4-owner body and one selectedB cast','status':'parent-approved bounded first-screen HD working composition; normal-entry guard/rollback validation remains runtime-owned'})
assert len(all_owners)==16 and len({x['key']for x in all_owners})==16
assert len({x['texture']for x in all_owners})==4
raw=np.array(Image.open(SH/'whole_shrub.png').convert('RGBA'));joined=sum((np.array(Image.open(P/q['texture'][6:]).convert('RGBA')).astype(np.uint16)for q in texture_specs.values()));assert np.array_equal(raw,joined)
far=[g for g in source['groups'] if g['center_owner_cell']not in centers]
config={
 'schema':'a13-round-shrub-selected-hd-v1','status':'parent-approved bounded first-screen HD working composition; promoted normal resources; normal-entry runtime validation separate',
 'map':'A13','source_map_sha256':sha(P/'data/maps/A13.json'),'source_manifest_sha256':sha(P/'assets/original/manifest.json'),
 'raw_sha256':sha(SH/'whole_shrub.png'),'whole_alpha_texture':res(SH/'whole_shrub.png'),'whole_alpha_texture_size':[1363,1154],
 'shared_texture_count':4,'owners':all_owners,'suppress_source_keys':[o['key']for o in all_owners],'instances':instances,
 'selected_shadow_contract':res(SH/'contact-band.json'),'selected_shadow_contract_sha256':sha(SH/'contact-band.json'),'shadow_selection':res(SH/'selection.json'),'shadow_selection_sha256':sha(SH/'selection.json'),
 'sampling':{'body_filter':'nearest','mipmaps':False,'common_canvas_size':[1363,1154],'common_canvas_required':True,'render_density':'Render original-resolution owner textures through the sharedHD canvas; do not pre-bake logical-sized sprites.','one_transform_per_instance':True},
 'validation':{'cpu_whole_four_RGBA_byte_exact':True,'raw_rgba_bytes':int(raw.size),'raw_nonzero_alpha_pixels':int((raw[:,:,3]>0).sum()),'raw_stored_rgba_pixels':int(np.any(raw!=0,2).sum()),'source_owner_cells_verified_directly':16,'source_owner_keys_unique':16,'whole_four_gpu_max_rgb_difference':1,'whole_four_gpu_different_pixels':3,'gpu_residual_accepted_by_parent':True,'research_native_cases':25,'research_direct2x_cases':25},
 'acceptance':{'approved_at_utc':'2026-10-15T07:22:45Z','native_raster':[2048,1536],'scope':'parent-viewed complete first-screen working composition; four exact shrub groups only','pilot_front_back_depth':'reviewed','selected_shadow':'B lower-foliage band; same field direction, explicit contact-shadow art adaptation','normal_path_loading_guard_and_failure_closure':'runtime owner must validate after this promotion; this metadata is not a claim that normal entry already passed'},
 'guard_contract':{'unit':'complete4-owner instance plus oneB cast','fields':['cell','source_cell','layer','sort_y','stable_source_order','texture','texture_sha256','texture_size','region','world_top_left','scale'],'check_actual_png_sha256_in_source_project':True,'source_cell_rule':'Compare the complete actual target map cell, including its floor ID. Values are not copied from the pilot.','invalid':'Disable that instance cast and restore all4 exact original keys; shared resource failure affects every dependent instance.','no_matching_by_frame_id_alone':True,'no_partial_owner_activation':True,'exported_build_note':'Raw file SHA proof is source-project verification. Exported imported resources require an explicitly supported validation path, not a claimed raw filesystem hash.'},
 'scope':{'only_centers':centers,'excluded_far_centers':[g['center_owner_cell']for g in far],'excluded_far_source_keys':[o['key']for g in far for o in g['owners_in_draw_order']],'automatic_same_family_replacement':False},
 'runtime_resource_closure':{'body_textures':[q['texture']for q in texture_specs.values()],'whole_alpha_texture':res(SH/'whole_shrub.png'),'selected_shadow_contract':res(SH/'contact-band.json'),'selected_shadow_base_contract':res(SH/'shadow.json'),'shadow_selection':res(SH/'selection.json'),'shadow_helper':'res://scripts/art/foliage_band_ground_shadow.gd','shadow_shader':'res://shaders/foliage_band_ground_shadow.gdshader','base_helper':'res://scripts/art/hero_alpha_ground_shadow.gd','base_shader':'res://shaders/hero_alpha_ground_shadow.gdshader','ignored_diagnostics_dependency':False,'art_source_runtime_dependency':False},
 'provenance':{'source_contract_path':str(S.relative_to(P)),'source_contract_sha256':sha(S),'technical_registration_path':str((T/'registration.json').relative_to(P)),'technical_registration_sha256':sha(T/'registration.json'),'reuse_index_sha256':sha(T/'first-screen-reuse-index.json'),'raw_provenance_path':str((D/'raw.png').relative_to(P)),'meaning':'Read-only generation/registration provenance; not runtime-loaded dependencies.'},
 'limits':['Actual woody root is not visible and remains null; family-anchor143 is only a map-owner anchor.','Four owner textures share one full raw canvas. Do not tighten crops or change sampling without new parity review.','OneB cast per active whole shrub, never four cutout casts or source checker plus new cast.','No far-map rollout; the remaining four source groups stay original.','Body white points and low-alpha green fringes remain immutable reviewed residuals.','Contact-band light is a2D design adaptation, not full original-shadow recovery or physical height inference.']}
(O/'registration.json').write_text(json.dumps(config,indent=2)+'\n')
# File closure is explicit and resolvable without diagnostics/art_source inputs.
def visit(value):
 if isinstance(value,list):
  for x in value:yield from visit(x)
 elif isinstance(value,dict):
  for x in value.values():yield from visit(x)
 elif isinstance(value,str)and value.startswith('res://'):yield value
for path in visit(config['runtime_resource_closure']):
 assert not path.startswith('res://art_source/') and '/diagnostics/'not in path
 assert (P/path[6:]).is_file(),path
print('ROUND_SHRUB_PROMOTION_PASS owners=16 instances=4 shared_textures=4 raw_RGBA_exact=true exact_target_cells=true normal_closure=true far4_disabled=true')
