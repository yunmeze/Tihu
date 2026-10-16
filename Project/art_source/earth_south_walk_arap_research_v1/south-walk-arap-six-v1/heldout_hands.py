from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,os
from scipy.ndimage import label
O=Path(__file__).parent;R=O.parent;ch=json.load(open(Path(os.environ['ARAP_SOURCE_PROJECT'])/'art_source/hero_s_walk_source_r8/SOURCE_VISIBLE_CHAIN_ANALYSIS.json'));sf={f['source_id']:f for f in ch['frames']};result=[];board=Image.new('RGB',(6*256,256),(80,85,90));draw=ImageDraw.Draw(board)
for p in range(57,63):
 col=1 if p in [59,60,61] else 0;im=Image.open(R/f'south-walk-mesh-correction-v1/raw/{p}.png').convert('RGBA');a=np.array(im);r,g,b=a[:,:,0].astype(int),a[:,:,1].astype(int),a[:,:,2].astype(int);mask=(a[:,:,3]>=128)&(r>80)&(r-g>15)&(g-b>8);items={};vis=Image.new('RGBA',im.size,(80,85,90,255));vis.alpha_composite(im);d=ImageDraw.Draw(vis)
 for side,(x0,x1) in zip(['L','R'],[(140+35*col,180+36*col),(298+35*col,336+36*col)]):
  sub=mask[170:265,x0:x1];ls,n=label(sub);sizes=np.bincount(ls.ravel());sizes[0]=0;k=int(np.argmax(sizes));ys,xs=np.where(ls==k);xs=xs+x0;ys=ys+170;box=[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())];center=np.array([(xs.min()+xs.max())/2,(ys.min()+ys.max())/2]);mapped=(center*.72+np.array([162-.72*(233+35*col),62-.72*41]))/4;sb=sf[p]['hands'][side]['skin_patch_inclusive_bbox_xyxy'];sc=np.array([(sb[0]+sb[2])/2,(sb[1]+sb[3])/2]);items[side]={'raw_detected_skin_bbox':box,'raw_warm_component_pixels':len(xs),'mapped_bbox_center_logical':mapped.tolist(),'source_skin_bbox':sb,'source_bbox_center_logical':sc.tolist(),'center_residual_logical':(mapped-sc).tolist(),'source_tolerance_logical':2,'method_limit':'skin-color component is visible patch proxy, not wrist joint; lighting/mask selection adds uncertainty; visually audit overlays'};d.rectangle(box,outline='yellow',width=2)
 result.append({'phase':p,'hand_patches':items});board.paste(vis.resize((256,256),Image.Resampling.LANCZOS),(256*(p-57),0));draw.text((256*(p-57)+5,4),str(p),fill='white')
board.save(O/'HELDOUT_SKIN_PATCH_OVERLAYS_HD2.png');(O/'HELDOUT_HAND_READS.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
