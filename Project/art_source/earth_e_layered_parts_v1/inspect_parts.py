from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;D=P.parents[1]/'diagnostics/earth_e_layered_parts_v1';D.mkdir(parents=True,exist_ok=True)
im=Image.open(P/'raw.png').convert('RGBA');s=33/387
names=['core','arm46','arm49','lower46','lower49','empty'];rows=[]
for i,name in enumerate(names):
 r=[i%3*512,i//3*512,i%3*512+512,i//3*512+512];tile=im.crop(r);a=np.array(tile.getchannel('A'));yy,xx=np.where(a>=128);bb=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)] if len(xx) else None
 tile.save(D/f'raw-cell-{name}.png');rows.append({'name':name,'raw_rect':r,'alpha128_bbox':bb,'bbox_height_logical_at_core_scale':None if bb is None else (bb[3]-bb[1])*s})
# Source comparison of complete lower pairs: one core-derived scale, toe midpoint translation only for diagnostic.
# No final component production or assembled poses.
srcs={46:np.array([[31,77],[48,87]],float),49:np.array([[31,83],[48,77]],float)}
raws={46:np.array([[163,406],[430,436]],float),49:np.array([[187,391],[395,428]],float)}
board=Image.new('RGBA',(1024,768),(64,68,72,255));dr=ImageDraw.Draw(board)
for i,n in enumerate([46,49]):
 src=Image.open(P.parents[1]/'diagnostics/earth_e_source_shadow_index_audit_v1'/f'{n}-index18-excluded-NOT-SEMANTICALLY-CERTIFIED.png').convert('RGBA')
 tile=im.crop(rows[3+i]['raw_rect']);t=srcs[n].mean(axis=0)-s*raws[n].mean(axis=0);k=4*s
 mapped=tile.transform((512,512),Image.Transform.AFFINE,(1/k,0,-t[0]/s,0,1/k,-t[1]/s),resample=Image.Resampling.BICUBIC)
 board.alpha_composite(src.resize((256,256),Image.Resampling.NEAREST),(i*512,0));board.alpha_composite(mapped.resize((256,256),Image.Resampling.LANCZOS),(i*512,256));dr.text((i*512+3,3),f'{n} source',fill='white');dr.text((i*512+3,260),f'{n} lower: common CORE scale; unassembled',fill='white')
 rows[3+i]['toe_delta_at_common_core_scale']=((raws[n][1]-raws[n][0])*s).tolist();rows[3+i]['source_toe_delta']=(srcs[n][1]-srcs[n][0]).tolist()
board.save(D/'lower-pairs-common-core-scale.png')
for name,c in [('gray',(64,68,72,255)),('light',(235,235,235,255)),('dark',(20,22,26,255))]:
 b=Image.new('RGBA',im.size,c);b.alpha_composite(im);b.save(D/f'raw-on-{name}.png')
j={'status':'raw_gate_failed_before_assembly','raw_sha256':hashlib.sha256((P/'raw.png').read_bytes()).hexdigest(),'raw_size':im.size,'common_explanatory_core_scale':s,'scale_assumption':'core crown y29 to belt bottom416 maps source crown16 to authored waist49; waist is uncertain production interface, NOT a bone fit','parts':rows,'arm_uncertainty':'raw tip-to-hand approx350px =29.8 logical at core scale; source shoulder29..35 to hand56 is21..27 before hand uncertainty; size mismatch suspected, not proven precise anatomy. Full-arm lengths and independently recentered cells violate requested layout; permitted hidden overlap2-3px must be assessed before assembly.','no_masks_or_edge_changes_performed':True,'no_assembled_pose':True,'no_retry':True}
(P/'RAW_GATE.json').write_text(json.dumps(j,indent=2)+'\n');print(json.dumps(j,indent=2))
