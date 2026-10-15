from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt
O=Path(__file__).parent;A=O.parent;V=A/'earth_bamboo_b_candidate_v2';L=A/'earth_bamboo_b_local_layers_plan_v1';raw=Image.open(V/'raw.png').convert('RGBA');m=json.loads((V/'measurements.json').read_text());d=m['density'];t=m['raw_from_source_translation'];C=[240,0,1000,760]
raw.crop(C).save(O/'input_crop.png');src=Image.open(A/'earth_bamboo_b_input_plan_v1/reference/source-body-index52-excluded.png').convert('RGBA');src.transform((760,760),Image.Transform.AFFINE,(1/d,0,(C[0]-t[0])/d,0,1/d,(C[1]-t[1])/d),Image.Resampling.NEAREST).save(O/'source_geometry_crop.png')
editable=np.array(Image.open(L/'A_upper_crown-editable-proposal.png'))>0
connections=[{'id':'left_branch_join','raw_xy':[390,440],'radius':14},{'id':'central_culm_join','raw_xy':[638,439],'radius':16},{'id':'right_branch_join','raw_xy':[749,440],'radius':14},{'id':'left_outer_boundary','raw_xy':[315,348],'radius':12},{'id':'right_outer_boundary','raw_xy':[931,345],'radius':12}]
conn=Image.new('L',raw.size);dr=ImageDraw.Draw(conn)
for p in connections:
 x,y=p['raw_xy'];r=p['radius'];dr.ellipse((x-r,y-r,x+r,y+r),fill=255)
editable &= np.array(conn)==0
# Exact final edit domain, feather wholly inward. Outside is immutable RGBA.
w=np.minimum(distance_transform_edt(editable)/12,1);mask=np.rint(w*255).astype('uint8');Image.fromarray(mask).save(O/'final_composite_weight.png');Image.fromarray(mask).crop(C).save(O/'edit_mask_crop.png');conn.save(O/'connection_guards.png')
contract={'status':'fixed before one image_gen call','base_raw_sha256':hashlib.sha256((V/'raw.png').read_bytes()).hexdigest(),'crop_xyxy':C,'crop_size':[760,760],'density':d,'translation':t,'connections':connections,'mask_sha256':hashlib.sha256((O/'final_composite_weight.png').read_bytes()).hexdigest(),'feather_native_px':12,'feather_rule':'only inward within approved A editable minus guard/hold and added connection disks','mapping_rule':'square model image maps uniformly to exact760x760 crop; scale760/output_width; no image-content fitting or independent x/y scaling. Non-square output fails without compositing.','composition':'premultiplied RGBA blend using frozen weight; every weight0 pixel restored bit-exact fromv2. No source silhouette multiplication.','not_approved':'B/C edits, owner partition, production, shadow'}
(O/'contract_before_generation.json').write_text(json.dumps(contract,indent=2)+'\n');fs=[V/'raw.png',L/'A_upper_crown-editable-proposal.png',L/'fixed_guard_proposal.png',L/'no_cut_hold_proposal.png',A/'earth_bamboo_b_input_plan_v1/reference/source-body-index52-excluded.png',O/'input_crop.png',O/'source_geometry_crop.png',O/'edit_mask_crop.png',O/'final_composite_weight.png',O/'connection_guards.png'];(O/'INPUT_SHA256.json').write_text(json.dumps([{'path':str(f.resolve()),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}for f in fs],indent=2)+'\n')
