from pathlib import Path
import numpy as np,json,hashlib
from PIL import Image,ImageDraw
O=Path(__file__).parent;P=O.parents[1];V=P/'art_source/earth_ground_cross_seam_revision_plan_v3';d=json.loads((V/'PLAN.json').read_text());sz=(1536,1152);mask=np.array(Image.open(V/'PROPOSED_fixed_replace_mask.png'))>0;poly=d['source_center_polyline_localraw'];yy,xx=np.mgrid[:1152,:1536];x=xx+.5;y=yy+.5
# Fixed center geometry, physical full curb width18->8 only on upper vertical join; no art RGB processing.
dist=np.full((1152,1536),np.inf)
for a,b in zip(poly,poly[1:]):
 ax,ay=a;dx,dy=b[0]-ax,b[1]-ay;t=np.clip(((x-ax)*dx+(y-ay)*dy)/(dx*dx+dy*dy),0,1);dist=np.minimum(dist,np.hypot(x-ax-t*dx,y-ay-t*dy))
width=np.where(y<100,18-10*np.clip((y-72)/28,0,1),8)
curb=mask&(dist<=width/2)
roadpoly=Image.new('1',sz);ImageDraw.Draw(roadpoly).polygon([(0,0),(1238,0)]+poly+[(0,1152)],fill=1)
road=mask&~curb&np.array(roadpoly);grass=mask&~curb&~road
labels=np.zeros(mask.shape,np.uint8);labels[grass]=1;labels[curb]=2;labels[road]=3
assert np.all((grass.astype(int)+curb.astype(int)+road.astype(int))==mask)
Image.fromarray(labels).save(O/'DOMAIN_INDEX_TECHNICAL.png')
for name,a in [('grass',grass),('curb',curb),('paving',road)]:Image.fromarray(a.astype('uint8')*255).save(O/('DOMAIN_'+name+'_BINARY.png'))
# Cross-material boundaries never blurred. Proposed 8raw internal grass-only donor transition zone, not applied.
from scipy.ndimage import distance_transform_edt
inside=distance_transform_edt(mask);samegrass_seam=grass&(inside<=8)&(dist>=width/2+4)
Image.fromarray(samegrass_seam.astype('uint8')*255).save(O/'PROPOSED_same_grass_transition_zone_NOT_APPLIED.png')
# Potential old-curb remnants within future paving; conservative geometry-only repair guard.
cd=np.full(mask.shape,np.inf)
for a,b in zip(d['candidate_cover_polyline_localraw'],d['candidate_cover_polyline_localraw'][1:]):
 ax,ay=a;dx,dy=b[0]-ax,b[1]-ay;t=np.clip(((x-ax)*dx+(y-ay)*dy)/(dx*dx+dy*dy),0,1);cd=np.minimum(cd,np.hypot(x-ax-t*dx,y-ay-t*dy))
paving_repair=road&(cd<=12)
Image.fromarray(paving_repair.astype('uint8')*255).save(O/'PROPOSED_paving_remnant_repair_mask.png')
pp=np.argwhere(paving_repair);pbox=[int(pp[:,1].min()),int(pp[:,0].min()),int(pp[:,1].max()+1),int(pp[:,0].max()+1)]
# Photographic/art-material inputs are native untouched crops, no generated RGB assembly.
plate=Image.open(P/'assets/earth/environment/ground_plate_v4/plate.png');ctx=Image.open(V/'INPUT_ONLY_existing_art_context.png')
crops=[('approved_v4_grass_sample_native2x.png',[1152,128,1408,384]),('approved_v4_slab_sample_native2x.png',[608,704,736,832])]
for name,b in crops:plate.crop(b).save(O/name)
# Actual material candidate region has exact1536x1024 native crop mapping; technical context only.
ctx.crop((0,64,1536,1088)).save(O/'INPUT_ONLY_material_canvas_context_native2x.png')
Image.fromarray(labels).crop((0,64,1536,1088)).save(O/'INPUT_domain_crop_TECHNICAL.png')
for name,a in [('grass',grass),('curb',curb),('paving',road)]:Image.fromarray(a.astype('uint8')*255).crop((0,64,1536,1088)).save(O/('INPUT_'+name+'_domain_crop.png'))
# Donor feasibility, not an artistic sampling instruction or a ready-to-use provenance map.
pts=np.argwhere(grass);valid=np.all(pts[:,1]+80<1536);b=[int(pts[:,1].min()),int(pts[:,0].min()),int(pts[:,1].max()+1),int(pts[:,0].max()+1)]
r={'status':'PLAN/MASK ONLY; no new image generation or artistic RGB assembly','geometry_authority':'v3 approved source center path and physical curb width; source design, not generated silhouette','domain_counts':{k:int(a.sum())for k,a in [('grass',grass),('curb',curb),('paving',road)]},'mutual_exclusion_and_union_equal_approved_mask':True,'labels':{'0':'immutable existing RGBA','1':'grass','2':'curb','3':'paving'},'source_geometry':poly,'physical_width_raw':'18->8 on y72..100 upper vertical only,8 thereafter','source_geometry_uncertainty_raw':6,'material_canvas':{'native_size':[1536,1024],'world_xyxy':[2400,1328,3168,1840],'crop_from_v3':[0,64,1536,1088],'mapping_to_v3':'local=(u,v+64)','density':2},'grass_donor_feasibility':{'required_domain_bbox_local':b,'approved_v4_top_grass_rectangle_raw':[0,0,1536,512],'approved_grass_rectangle_height_insufficient':b[3]-b[1]>512,'existing_context_translation_option':[80,0],'all_donor_coordinates_within_context':bool(valid),'disposition':'Not recommended: context includes old/south material reset; translating texture does not match retained contact pixels; would duplicate visible grass marks. No donor copy applied.'},'paving_repair_proposal':{'pixels':int(paving_repair.sum()),'bbox_local':pbox,'default':'Retain same-coordinate paving outside this tiny guard. Guard is geometry estimate, require visual remnant verification before finalizing.'},'reference_crops':[{'file':n,'source':'assets/earth/environment/ground_plate_v4/plate.png','raw_xyxy':b,'density':2,'operation':'unchanged integer crop'}for n,b in crops],'proposed_same_grass_transition_zone_pixels':int(samegrass_seam.sum()),'transition_status':'Not applied. Proposed at most8raw inside fixed mask, grass-only and>=4raw from curb; never blends grass across curb geometry. Actual conditional-material boundary must pass before any transition approval.','inputs':[]}
for p in [P/'assets/earth/environment/ground_plate_v4/plate.png',P/'art_source/earth_south_ground_candidate_v1/raw.png',P/'art_source/earth_ground_cross_seam_candidate_v1/raw.png',V/'PLAN.json',V/'PROPOSED_fixed_replace_mask.png',V/'INPUT_ONLY_existing_art_context.png']:
 r['inputs'].append({'path':str(p.relative_to(P)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(O/'MATERIAL_PLAN.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r['domain_counts']));print('bbox',r['grass_donor_feasibility'])
