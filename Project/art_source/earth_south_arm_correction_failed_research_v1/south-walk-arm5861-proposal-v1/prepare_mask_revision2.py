from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
from scipy.ndimage import binary_dilation
O=Path(__file__).parent;R=O.parent;D=O/'revision2';D.mkdir(exist_ok=True)
spec=json.load(open(O/'CONSTRAINTS.json'));report=[];board=Image.new('RGB',(1040,420),(70,75,80));dr=ImageDraw.Draw(board)
for n,f in enumerate(spec):
 p=f['phase'];im=Image.open(R/f'south-walk-mesh-correction-v1/raw/{p}.png').convert('RGBA');a=np.array(im)[:,:,3];yy,xx=np.indices(a.shape);combined=np.zeros(a.shape,np.uint8);sides={}
 for side,z in f['screen_sides'].items():
  old=np.array(Image.open(O/f'{p}-{side}-classes.png'));original=old==2
  # Finite expansion for a proposal only. All additions are explicitly colored/reported.
  rigid=binary_dilation(original,iterations=4)&(a>0)&(yy>=z['rigid_y_min'])
  # All one-cell vertex neighbors are handled, including diagonal contacts.
  ring=binary_dilation(rigid,structure=np.ones((3,3)))&~rigid&(a>0)
  cloth=old==1;fringe=ring&(a<64);high=ring&(a>=64)&~cloth
  c=np.zeros(a.shape,np.uint8);c[cloth]=1;c[rigid]=2;c[fringe]=3
  # High-alpha non-cloth conflicts are explicitly rejected, not freed.
  y,x=np.where(a>0);corn=np.stack([np.stack([x,y],1),np.stack([x+1,y],1),np.stack([x+1,y+1],1),np.stack([x,y+1],1)],1);uv,inv=np.unique(corn.reshape(-1,2),axis=0,return_inverse=True);cl=np.repeat(c[y,x],4);fix=np.zeros(len(uv),bool);rg=np.zeros(len(uv),bool);fix[inv[cl==0]]=True;rg[inv[cl==2]]=True;bad=uv[fix&rg]
  Image.fromarray(c).save(D/f'{p}-{side}-classes.png');sides[side]={'expanded_rigid_pixels':int((rigid&~original).sum()),'added_high_alpha_pixels':int((rigid&~original&(a>=128)).sum()),'fringe_transition_pixels':int(fringe.sum()),'remaining_high_alpha_noncloth_neighbors':int(high.sum()),'fixed_rigid_conflict_vertices':len(bad),'conflict_bbox':None if not len(bad) else [bad.min(0).tolist(),bad.max(0).tolist()]};combined=np.maximum(combined,c)
 v=np.array(im)
 for cls,color in [(1,[30,150,255]),(2,[255,180,30]),(3,[255,40,180])]:v[combined==cls,:3]=(.5*v[combined==cls,:3]+.5*np.array(color)).astype(np.uint8)
 base=Image.new('RGBA',im.size,(70,75,80,255));base.alpha_composite(Image.fromarray(v));board.paste(base.crop((120,90,380,270)).resize((520,360),Image.Resampling.NEAREST),(n*520,40));dr.text((n*520+4,4),f'{p} R2: cloth BLUE / rigid AMBER / fringe PINK',fill='white');report.append({'phase':p,'sides':sides})
board.save(D/'MASK_REVIEW_2X.png');(D/'PREFLIGHT.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
