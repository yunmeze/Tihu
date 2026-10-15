"""Revision scope masks only; never alter candidate, approved art or production."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFilter
import numpy as np
P=Path(__file__).resolve().parents[2];O=Path(__file__).parent;RAW=P/'art_source/earth_south_ground_candidate_v1/raw.png';SRC=P/'art_source/earth_south_ground_input_plan_v1/source_floor_layout_native.png';OLD=P/'art_source/earth_south_ground_input_plan_v1/approved_overlap_2x.png'
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
raw=Image.open(RAW).convert('RGB');source=Image.open(SRC).convert('RGB').resize((1536,1024),Image.Resampling.NEAREST)
# Manually read structural curb center proxies, deliberately coarse uncertainty, NOT measured navigation geometry.
srcpts=[(208,558),(160,590),(112,622),(88,638),(84,704),(80,770),(56,786)]
candpts=[(208,598),(160,632),(112,665),(102,674),(100,720),(94,774),(56,800)]
A=Image.new('L',raw.size);d=ImageDraw.Draw(A);d.polygon(srcpts+list(reversed(candpts)),fill=255);d.line(srcpts,fill=255,width=32,joint='curve');d.line(candpts,fill=255,width=32,joint='curve');d.rectangle((72,704,128,756),fill=255)
# Fixed mask includes geometry gap, both material sides, and unwanted tuft; no automatic content segmentation.
A.save(O/'A_fixed_replace_mask.png');ab=list(A.getbbox());ctx=[max(0,ab[0]-48),max(0,ab[1]-48),min(1536,ab[2]+64),min(1024,ab[3]+48)]
raw.crop(ctx).save(O/'A_candidate_context_1to1.png');source.crop(ctx).save(O/'A_source_context_2x_nearest.png');A.crop(ctx).save(O/'A_fixed_replace_mask_local.png')
# Source reading uncertainty band, +/-6raw (3logical), wider +/-8 at kink/occluded basal edge.
band=Image.new('L',raw.size);d=ImageDraw.Draw(band);d.line(srcpts,fill=255,width=13,joint='curve');d.ellipse((80,630,96,646),fill=255);band.save(O/'A_source_read_uncertainty_band.png')
# B conservative grass-only zones. Avoid ambiguous near-road grass at north4; no road/curb mask.
B=Image.new('L',raw.size);d=ImageDraw.Draw(B);d.rectangle((128,0,191,127),fill=255);d.polygon([(160,128),(224,128),(160,176)],fill=255);d.rectangle((960,128,1535,191),fill=255);B.save(O/'B_grass_only_allowed_mask.png')
# Explicit proposed mixing weight, not applied. Fixed raw-coordinate branches; only new-side generated patch + candidate raw.
weights=np.zeros((1024,1536),np.uint8);mask=np.asarray(B)>0
for y,x in zip(*np.where(mask)):
 if y<128:
  depth=191-x;inner=max(0,min(1,(64-depth)/16));lateral=1 # top edge is world canvas boundary, not a new seam.
 elif x>=960:
  depth=y-128;inner=max(0,min(1,(64-depth)/16));lateral=min(1,max(0,(x-960)/16)) # protect new artificial left patch boundary.
 else:
  depth=y-128;inner=max(0,min(1,(48-depth)/16));right=224-(4/3)*(y-128);lateral=min(1,max(0,(right-x)/16),max(0,(x-160)/16))
 weights[y,x]=round(255*inner*lateral)
Image.fromarray(weights).save(O/'B_PROPOSED_generation_weight_NOT_APPLIED.png')
# No candidate output is synthesized. Only colored scope overlays are generated.
for label,maskim in [('A',A),('B',B)]:
 overlay=raw.copy();color=Image.new('RGB',raw.size,(255,60,180) if label=='A' else (40,200,255));opacity=maskim.point(lambda v:80 if v else 0);overlay.paste(color,(0,0),opacity);dr=ImageDraw.Draw(overlay);dr.rectangle((192,0,1535,127),outline=(255,230,20),width=3);overlay.save(O/(label+'_SCOPE_OVERLAY_NOT_ART.png'))
input_context=raw.copy();input_context.paste(Image.open(OLD).convert('RGB'),(192,0))
for name,rect in [('B_west_left_context',[96,0,288,224]),('B_right_grass_context',[896,64,1536,224])]:
 raw.crop(rect).save(O/(name+'_candidate.png'));input_context.crop(rect).save(O/(name+'_INPUT_ONLY_frozen_old7.png'));B.crop(rect).save(O/(name+'_allowed_mask.png'))
# Visible coordinate control board crops for A preserve source/candidate role labels in files.
for name,im in [('source',source),('candidate',raw)]:
 b=[32,528,320,848];a=im.crop(b).resize((864,960),Image.Resampling.NEAREST);dr=ImageDraw.Draw(a)
 for x in range(32,321,16):
  xx=(x-32)*3;dr.line((xx,0,xx,960),fill=(50,100,180));dr.text((xx+1,1),str(x),fill='white')
 for y in range(528,849,16):
  yy=(y-528)*3;dr.line((0,yy,864,yy),fill=(50,100,180));dr.text((1,yy+1),str(y),fill='white')
 a.save(O/(name+'_A_coordinate_read.png'))
ma=np.asarray(A)>0;mb=np.asarray(B)>0;frozen=np.zeros_like(ma);frozen[:128,192:1536]=True
assert not np.any((ma|mb)&frozen);assert not np.any(ma&mb);assert not np.any((weights>0)&~mb)
def world(pt):return [2400+pt[0]/2,1408+pt[1]/2]
r={'status':'SCOPE PROPOSAL ONLY; no generation or candidate pixel modification','candidate_sha256':h(RAW),'source_sha256':h(SRC),'old_overlap_sha256':h(OLD),'coordinate_contract':'All mask points in full candidate1536x1024 raw pixels; world=[2400,1408]+raw/2. Half-open bbox.','A':{'source_center_proxy_points_raw':srcpts,'source_center_proxy_points_world':[world(p) for p in srcpts],'candidate_center_proxy_points_raw':candpts,'source_manual_uncertainty_raw':6,'kink_manual_uncertainty_raw':8,'interpretation_limit':'Source thin curb center proxy versus candidate wider curb center; not exact physical survey. Top diagonal continues outside A with an unresolved mismatch.','fixed_binary_replace_mask':'A_fixed_replace_mask.png','fixed_mask_bbox_raw':ab,'fixed_mask_bbox_world':[world(ab[:2]),world(ab[2:])],'context_raw':ctx,'replace_pixel_count':int(ma.sum()),'output_assembly':'Only future generated patch texels where fixed mask255; outside mask original candidate v1 exactly. No blend, warp or new resize.','blocked_constraint':'Upper diagonal source-vs-candidate offset persists at right context entry. Freezing outside A can force a new bend. Parent must approve a feasible local joint or bounded diagonal extension; A is not approved for generation yet.'},'B':{'allowed_mask':'B_grass_only_allowed_mask.png','proposed_weight':'B_PROPOSED_generation_weight_NOT_APPLIED.png','allowed_pixel_count':int(mb.sum()),'maximum_width_raw':64,'maximum_width_logical':32,'proposed_inner_transition_raw':16,'proposed_inner_transition_logical':8,'zones':[{'name':'west','polygon_raw':[[128,0],[192,0],[192,128],[128,128]],'contact':'west old/new seam, new side only'},{'name':'north_left_conservative','polygon_raw':[[160,128],[224,128],[160,176]],'contact':'north1 small grass wedge; narrowing avoids diagonal road'},{'name':'north_right','polygon_raw':[[960,128],[1536,128],[1536,192],[960,192]],'contact':'north5..7 grass'}],'excluded_contacts':'north2/3 paving, north4 curb/ambiguous roadside grass and nearby north1 road edge remain unchanged; cannot claim all8seams solved','patch_contexts_raw':[[96,0,288,224],[896,64,1536,224]],'provenance_formula':'Within allowed B: round((weight*future_patch_RGB+(255-weight)*original_candidate_v1_RGB)/255). Weight0 and outside B use original candidate bytes. No old-v4 RGB sampled into blend. Actual future patch SHA must be recorded. Formula is proposed only, never applied.','boundary_requirement':'At old/new contact generated new-side pixels must visually match frozen original7; finite blend inside new side cannot rescue bad outer boundary. Reject if still discontinuous.'},'invariants':{'A_B_disjoint':True,'frozen_old7_changed_pixels':0,'outside_new57_mask_pixels':0,'no_navigation_or_source_data_change':True,'no_final_art_processed':True}}
(O/'REVISION_SCOPE.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'A_bbox':ab,'A_context':ctx,'A_pixels':int(ma.sum()),'B_pixels':int(mb.sum()),'max_B_width':64}))
