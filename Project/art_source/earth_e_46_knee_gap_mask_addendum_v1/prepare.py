from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[1];S=R/'art_source/earth_e_46_knee_join_v1';D=R/'diagnostics/earth_e_46_knee_gap_mask_addendum_v1';D.mkdir(exist_ok=True,parents=True)
a=np.array(Image.open(S/'rigid46-BEFORE-JOIN.png').convert('RGBA'));old=Image.open(S/'46-HD4-RIGID-JOIN-RESEARCH.png').convert('RGBA');patch=Image.open(S/'patch-mapped-HD4-crop.png').convert('RGBA');lay=Image.new('RGBA',(512,512));lay.paste(patch,(128,244));p=np.array(lay);prev=np.array(Image.open(S/'actual-gap-only-replacement-mask.png'))>0
poly=[(146,266),(175,266),(175,271),(146,271)];gate=Image.new('L',(512,512));ImageDraw.Draw(gate).rectangle((146,266,175,271),fill=255);add=(np.array(gate)>0)&(a[:,:,3]<128)&~prev;add[267,175]=False # exterior coordinate has no patch cloth, excluded explicitly

Image.fromarray((add*255).astype('uint8')).save(P/'ADDITIONAL-GAP-ONLY-PROPOSED-mask.png');coords=[[int(x),int(y)] for y,x in zip(*np.where(add))];rows={str(y):[x for x,yy in coords if yy==y] for y in sorted({y for x,y in coords})};sel=p.copy();sel[~add,3]=0;u=Image.fromarray(sel);u.alpha_composite(old);out=np.array(u);oa=np.array(old);out[~add]=oa[~add];proposal=Image.fromarray(out)
for nm,c in [('gray',(128,128,128,255)),('light',(235,235,235,255)),('dark',(20,22,26,255))]:
 b=Image.new('RGBA',(1200,420),c)
 for i,im in enumerate([old,lay,proposal]):b.alpha_composite(im.crop((140,260,180,288)).resize((400,280),Image.Resampling.NEAREST),(i*400,0))
 b.save(D/f'failed-samepatch-proposed-{nm}.png')
ov=Image.new('RGBA',(512,512),(128,128,128,255));ov.alpha_composite(old);z=np.array(ov);z[add,:3]=[255,0,220];Image.fromarray(z).crop((140,260,180,288)).resize((800,560),Image.Resampling.NEAREST).save(D/'exact-added-pixels-pink.png');j={'status':'proposal only; frozen failed image untouched','mask_coordinate_system':'HD4 512; logical divide by4','manual_gap_polygon':poly,'add_pixel_count':len(coords),'coords_HD4':coords,'row_x_coords':rows,'original_alpha_ge128_intersection':int((add&(a[:,:,3]>=128)).sum()),'existing_patch_mask_intersection':int((add&prev).sum()),'same_mapped_patch_alpha_range': [int(p[:,:,3][add].min()),int(p[:,:,3][add].max())],'source_raw_sha256':hashlib.sha256((S/'raw.png').read_bytes()).hexdigest(),'mapped_patch_sha256':hashlib.sha256((S/'patch-mapped-HD4-crop.png').read_bytes()).hexdigest(),'no_new_generation':True,'mapping_unchanged':60/1298};(P/'PROPOSAL.json').write_text(json.dumps(j,indent=2)+'\n');print({k:v for k,v in j.items() if k not in ['coords_HD4','row_x_coords']})
