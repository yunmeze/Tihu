from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
import numpy as np
P=Path(__file__).resolve().parents[2];O=Path(__file__).parent;I=P/'art_source/earth_south_ground_input_plan_v1';D=P/'diagnostics/art_source/earth-south-ground-candidate-v1';D.mkdir(exist_ok=True,parents=True)
raw=Image.open(O/'raw.png').convert('RGB');old=Image.open(I/'approved_overlap_2x.png').convert('RGB');assert raw.size==(1536,1024)
join=raw.copy();join.paste(old,(192,0));join.save(D/'REVIEW_ONLY_old7_plus_new57.png')
arr=np.asarray(raw).astype(int);oa=np.asarray(old).astype(int);ja=np.asarray(join).astype(int);diff=arr[:128,192:1536]-oa
edges=[]
for i in range(7):
 x0=192+i*192;x1=x0+192
 before=ja[127,x0:x1];after=ja[128,x0:x1];delta=np.abs(before-after)
 # compare ordinary one-row difference adjacent within each side, not a pass criterion
 oldlocal=np.abs(ja[126,x0:x1]-ja[127,x0:x1]);newlocal=np.abs(ja[128,x0:x1]-ja[129,x0:x1]);patchdiff=np.abs(diff[:,i*192:(i+1)*192])
 edges.append({'id':f'north_{i+1}','world_line':[2496+i*96,1472,2592+i*96,1472],'candidate_pixel_line':[x0,128,x1,128],'boundary_mean_abs_rgb':float(delta.mean()),'old_internal_neighbor_mean_abs_rgb':float(oldlocal.mean()),'new_internal_neighbor_mean_abs_rgb':float(newlocal.mean()),'generated_vs_frozen_overlap_mean_abs_rgb':float(patchdiff.mean()),'generated_vs_frozen_overlap_max_abs_rgb':int(patchdiff.max())})
 crop=join.crop((x0,64,x1,192));crop.save(D/f'seam_north_{i+1}_1to1.png')
delta=np.abs(ja[:128,191]-ja[:128,192]);edges.append({'id':'west','world_line':[2496,1408,2496,1472],'candidate_pixel_line':[192,0,192,128],'boundary_mean_abs_rgb':float(delta.mean()),'old_internal_neighbor_mean_abs_rgb':float(np.abs(ja[:128,192]-ja[:128,193]).mean()),'new_internal_neighbor_mean_abs_rgb':float(np.abs(ja[:128,190]-ja[:128,191]).mean())});join.crop((128,0,256,128)).save(D/'seam_west_1to1.png')
# Comparison sheets use unchanged input/source pixels aside from labeled margins, not final assets.
source=Image.open(I/'source_floor_layout_native.png').convert('RGB').resize((1536,1024),Image.Resampling.NEAREST)
board=Image.new('RGB',(1536,3*1024+3*30),(35,35,35));dr=ImageDraw.Draw(board)
for n,(label,im) in enumerate([('SOURCE GEOMETRY ONLY 2X NEAREST',source),('RAW CANDIDATE - GENERATED OVERLAP NOT FROZEN',raw),('REVIEW ONLY - ACTUAL OLD7 + NEW57 - NO BLEND',join)]):
 y=n*1054;dr.text((8,y+8),label,fill='white');board.paste(im,(0,y+30))
board.save(D/'source_raw_frozenjoin_review.png')
# Boundary/context strips offer exact 1:1 inspection of road/grass registration and join.
join.crop((0,96,1536,160)).save(D/'north_join_full_width_1to1.png');raw.crop((0,576,256,896)).save(D/'candidate_kink_1to1.png');source.crop((0,576,256,896)).save(D/'source_kink_2x_nearest.png')
report={'raw_sha256':hashlib.sha256((O/'raw.png').read_bytes()).hexdigest(),'actual_raw_size':[1536,1024],'world_size':[768,512],'effective_density':[2,2],'raw_unmodified':True,'generation_calls':1,'runtime_or_registration_changes':False,'generated_overlap_byte_exact':bool(np.array_equal(arr[:128,192:1536],oa)),'generated_overlap_mean_abs_rgb':float(np.abs(diff).mean()),'generated_overlap_changed_pixels':int(np.any(diff!=0,axis=2).sum()),'frozen_join_old_overlap_byte_exact':bool(np.array_equal(ja[:128,192:1536],oa)),'seams':edges,'metric_limit':'Adjacent-pixel RGB discontinuity and overlap RGB error are diagnostics, not geometric acceptance thresholds. Texture naturally varies. Parent visual/source-edge review required.','source_v4_registration_sha256':hashlib.sha256((P/'assets/earth/environment/ground_plate_v4/registration.json').read_bytes()).hexdigest(),'honest_composite_path':str((D/'REVIEW_ONLY_old7_plus_new57.png').relative_to(P))}
(O/'review.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
