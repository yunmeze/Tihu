"""Build a source-referenced fixed foliage-edge shadow contract, no body edits."""
from pathlib import Path
import hashlib,json,shutil
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent
O=P/'assets/scifi/environment/a13_round_shrub_shadow_v1';O.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
raw=D/'raw.png';assert sha(raw)=='b093644c662a8d42f8beee8160b4fe2b4c200257bfb7d3ac5589683069f8b469'
a=np.array(Image.open(raw).convert('RGBA'));source_path=P/'art_source/a13_round_shrub_source/source-group-contract.json';source=json.loads(source_path.read_text());body_path=D/'technical_v1/registration.json';body=json.loads(body_path.read_text());idx_path=D/'technical_v1/first-screen-reuse-index.json';index=json.loads(idx_path.read_text());s=body['whole_shrub_registration']['scale'];t=np.array(body['whole_shrub_registration']['translation_to_source_composite']);measure=[]
for threshold in [32,64,96,128,192]:
 y,x=np.where(a[:,:,3]>=threshold);last=int(y.max());xs=x[y==last];edge=[float(xs.mean()+.5),last+1];measure.append({'alpha_threshold':threshold,'last_row_index':last,'x_range_inclusive':[int(xs.min()),int(xs.max())],'mean_lower_texel_edge':edge,'source_local_edge':(np.array(edge)*s+t).tolist()})
ref=np.array(measure[2]['mean_lower_texel_edge']);assert np.array_equal(ref,[778,1103])
cast=np.array([148/279,-111/279]);y,x=np.where(a[:,:,3]>=96);p=np.c_[x+.5,y+.5];height=ref[1]-p[:,1];projected=np.c_[p[:,0],np.full(len(p),ref[1])]+height[:,None]*cast;projected=projected*s+t
instances=[]
for g in index['groups']:
 if g['nominal_first_screen_visibility']=='outside':continue
 instances.append({'center_owner_cell':g['center_owner_cell'],'whole_raw_world_origin':g['candidate_raw_world_origin'],'scale':s,'actual_woody_root':None,'leaf_proxy_world':(np.array(g['candidate_raw_world_origin'])+ref*s).tolist(),'nominal_first_screen_visibility':g['nominal_first_screen_visibility'],'source_owners':g['source_keys_and_sort'],'requires_suppressed_source_keys':[o['key']for o in g['source_keys_and_sort']],'activation':'pilot57,38 first; other first-screen groups only after separate body/depth approval','casts_per_instance':1})
assert len(instances)==4 and len({k for g in instances for k in g['requires_suppressed_source_keys']})==16
shutil.copyfile(raw,O/'whole_shrub.png');assert sha(O/'whole_shrub.png')==sha(raw)
contract={'schema':'a13-round-shrub-first-screen-single-alpha-cast-v1','status':'bounded candidate; native on/off/contact/depth and per-group activation pending','texture':'res://assets/scifi/environment/a13_round_shrub_shadow_v1/whole_shrub.png','texture_sha256':sha(raw),'texture_alpha_sha256':hashlib.sha256(a[:,:,3].tobytes()).hexdigest(),'texture_size':[a.shape[1],a.shape[0]],'region':[0,0,a.shape[1],a.shape[0]],'body_rgba_preservation':'PNG copied byte-for-byte from accepted raw; no resize, alpha threshold, RGB deletion or baked shadow. Shader samples full alpha including fringes.','helper':'res://scripts/art/hero_alpha_ground_shadow.gd','method':'configure_ground_frame','ground_reference':ref.tolist(),'ground_slope':0.,'actual_woody_root':None,'reference_meaning':'fixed visible lower-foliage texel-edge proxy; not woody root, foot-contact proof or3D ground calibration','cast_per_height':cast.tolist(),'cast_exact':['148/279','-111/279'],'opacity':.30,'blur_radius_px':3.,'blur_radius_logical_px':3*s,'tint':[.035,.045,.055],
'coordinate_contract':{'helper_frame_space':'raw image pixels; density1 within a dedicated raw-space parent','helper_body_to_parent':'Transform2D.IDENTITY','raw_space_parent_basis':[s,0,0,s],'raw_space_parent_origin':'per-instance whole_raw_world_origin plus logical camera offset','composed_mapping':'parent_transform * helper_transform * projected_raw_point; total raw-to-logical scale is exactly the body scale','hd_transform':'Apply the same outer2x world canvas as the body; do not multiply reference or scale again.','reason':'The whole high-resolution shrub uses scale.0944287. A raw-space parent preserves a well-conditioned identity helper transform and the exact total body mapping, without changing frozen helper limits.','blur_note':'3raw texels equals0.283286 logical pixels. This is an initial candidate softness, not the hero0.9logical setting.'},
'instances':instances,'draw_contract':{'passes_per_selected_instance':1,'after':'all floors','before':'all original/replacement objects and actors','alpha_input':'one whole texture, never one per owner slice','atomic_group':'Only activate a cast with its complete four-owner replacement, suppressing all four original checker-bearing source owners. A source body must never get this new cast.','failure':'A missing common texture/config disables all affected casts and restores all four source owners of each affected instance. Never leave partial body/source or duplicate checker.','diagnostic_off':'An explicit same-phase shadow-off comparison may retain the new body; this deliberate A/B is distinct from failure fallback.','scope':'Only four nominal first-screen groups; pilot57,38 first. No distant groups automatically enabled.'},
'evidence':{'source_contract':str(source_path.relative_to(P)),'source_contract_sha256':sha(source_path),'body_registration':str(body_path.relative_to(P)),'body_registration_sha256':sha(body_path),'reuse_index':str(idx_path.relative_to(P)),'reuse_index_sha256':sha(idx_path),'source_actual_root':None,'source_visible_leaf_edges':source['registration_cautions']['visible_lower_foliage_samples'],'source_checker_spatial_rois':source['checker_evidence']['spatial_rois'],'source_checker_limitation':source['checker_evidence']['warning'],'source_direction_limitation':source['checker_evidence']['direction'],'proxy_threshold_sensitivity_measurement_only':measure,'projected_alpha96_source_local_bbox_pixel_centers':[ *projected.min(0).tolist(),*projected.max(0).tolist()]},
'limits':['Source root is hidden. A horizontal visible-foliage envelope is only a stable2D receiver approximation.','The selected raw alpha96 lower edge varies by at most1raw texel over thresholds32..192; this is measurement robustness, not physical contact certainty.','Full-alpha cast may extend about31logical pixels right of the new foliage envelope; source exposed checker is much smaller. This is shared-field lighting, not an old shadow reconstruction.','Low-alpha fringes below the proxy are retained and project according to the same affine rule; no threshold mask removes them.','Small blur may appear too sharp under actualHD. Runtime on/off review must decide before promotion.','No platform/stair receiver, environmental occlusion mask or3D crown-depth claim.','Preserve original four-owner body depth order. First-screen64,45 also overlaps an original tree and needs its own native check.']}
(O/'shadow.json').write_text(json.dumps(contract,indent=2)+'\n')
print('SHRUB_CAST_CONTRACT_PASS raw_exact=true root=null instances=4 owners=16 proxy=778,1103 scale='+str(s))
# Conservative lower-band B is a render-time alpha weighting, not a new body.
mask=(a[:,:,3]>=96)&(np.indices(a.shape[:2])[0]>=900)
y,x=np.where(mask);p=np.c_[x+.5,y+.5];height=ref[1]-p[:,1]
projected_band=(np.c_[p[:,0],np.full(len(p),ref[1])]+height[:,None]*cast)*s+t
contact={
 'schema':'a13-round-shrub-limited-foliage-band-cast-v1',
 'status':'conservativeB candidate; nativeHD A/B pending',
 'base_contract':'res://assets/scifi/environment/a13_round_shrub_shadow_v1/shadow.json',
 'base_contract_sha256':sha(O/'shadow.json'),
 'texture':contract['texture'],'texture_sha256':contract['texture_sha256'],
 'helper':'res://scripts/art/foliage_band_ground_shadow.gd',
 'method':'configure_foliage_band_frame',
 'shader':'res://shaders/foliage_band_ground_shadow.gdshader',
 'region':contract['region'],'ground_reference':contract['ground_reference'],
 'ground_slope':0.,'actual_woody_root':None,'cast_per_height':cast.tolist(),
 'opacity':.30,'blur_radius_px':3.,'alpha_band_start_y':900.,'alpha_band_fade_px':64.,
 'band_coordinate_units':'raw texels, frame local',
 'alpha_rule':'Within the same guarded whole-raw alpha sample, multiply only the shadow by smoothstep(900,964,p.y). No body/channel rewrite and no RGB classification.',
 'logical_band_start_y_source_composite':float(900*s+t[1]),
 'logical_fade_extent_px':float(64*s),
 'design_meaning':'Limited contact-shadow design adaptation from near-ground visible foliage; no upper-crown height inference, no full original-cast recovery.',
 'alpha96_projected_bound_before_fade_source_local':[*projected_band.min(0).tolist(),*projected_band.max(0).tolist()],
 'max_positive_logical_y_gap_cast_as_height':float((ref[1]-900)*s),
 'coordinate_contract':contract['coordinate_contract'],
 'instances':instances,'draw_contract':contract['draw_contract'],
 'limits':['This chooses a lower image band as an explicit design envelope, not a proven physical receiver/height.',
           'The fade can reduce an already mostly-hidden shadow too far; judge same-positionHD A/B rather than forcing visible darkness.',
           'One pass only; do not layer this on top of full-shadowA. Select A or B.',
           'Shared raw texture, original-source atomic suppression and failure fallback remain mandatory.']}
(O/'contact-band.json').write_text(json.dumps(contact,indent=2)+'\n')
print('SHRUB_CONTACT_BAND_CONTRACT_PASS band_start=900 fade=64 raw_unchanged=true one_pass=true')
