from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
P=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
D=P/'diagnostics/art_source/earth-concrete-material-c-v1';D.mkdir(parents=True,exist_ok=True)
M=P/'art_source/earth_ground_material_layers_plan_v1';G=P/'art_source/earth_grass_two_segment_composite_v1/03_outer_8raw.png'
def arr(p):return np.asarray(Image.open(p).convert('RGBA'))
def mask(p):return np.asarray(Image.open(p).convert('L'))>0
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
b=arr(G);c=arr(O/'raw.png');assert c.shape==(1024,1536,4)
curb=mask(M/'DOMAIN_curb_BINARY.png');guard=mask(M/'PROPOSED_paving_remnant_repair_mask.png');paving=mask(M/'DOMAIN_paving_BINARY.png');grass=mask(M/'DOMAIN_grass_BINARY.png');fixed=curb|paving|grass
assert not (curb&guard).any() and not (guard&~paving).any()
m=curb|guard;y,x=np.where(m);assert min(y)>=64 and max(y)<1088
r=b.copy();r[y,x]=c[y-64,x];r[:,:,3]=255
changed=np.any(r!=b,axis=2)
assert not changed[~m].any();assert not changed[~fixed].any();assert not changed[grass].any();assert not changed[paving&~guard].any()
Image.fromarray(r).save(O/'RESEARCH_G_frozen_plus_C.png');Image.fromarray((m*255).astype('uint8')).save(O/'ACTUAL_C_replace_mask.png')
np.savez_compressed(O/'C_RGBA_difference_int16.npz',rgba_delta=r.astype('int16')-b.astype('int16'))
regions={'upstream':(1184,64,1280,192),'old_south_interface':(784,304,976,416),'long_diagonal':(480,544,704,672),'south_kinks':(40,816,176,1040),'exit':(0,992,144,1104)}
for name,box in regions.items():
 w,h=box[2]-box[0],box[3]-box[1];board=Image.new('RGB',(w*2,h+24),(25,25,25));dr=ImageDraw.Draw(board);dr.text((2,5),'frozen G',fill='white');dr.text((w+2,5),'G + C research',fill='white');board.paste(Image.fromarray(b).crop(box),(0,24));board.paste(Image.fromarray(r).crop(box),(w,24));board.save(D/(name+'.png'))
report={'actual_raw_size':[1536,1024],'density_pixels_per_world_unit':2,'mapping':'target v3(x,y) <- raw C(x,y-64); integer 1:1, no scaling/rotation/mirror/blend','curb_pixels':int(curb.sum()),'guard_pixels':int(guard.sum()),'replacement_pixels':int(m.sum()),'changed_pixels':int(changed.sum()),'outside_C_mask_RGBA_changed':int(changed[~m].sum()),'outside_fixed_mask_RGBA_changed':int(changed[~fixed].sum()),'grass_changed':int(changed[grass].sum()),'preserved_correct_paving_changed':int(changed[paving&~guard].sum()),'alpha_all_255':bool((r[:,:,3]==255).all()),'source_SHA256':{str(p.relative_to(P)):sha(p) for p in [G,O/'raw.png',M/'DOMAIN_curb_BINARY.png',M/'PROPOSED_paving_remnant_repair_mask.png']},'result_SHA256':sha(O/'RESEARCH_G_frozen_plus_C.png'),'guard_caveat':'Existing explicitly proposed conservative 1894-pixel remnant guard, not a claim every pixel contains a visually confirmed defect; no larger bounding rectangle replaced.','status':'research only; no contact lighting, no material seam blending, no production registration'}
(O/'review.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
