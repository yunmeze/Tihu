from PIL import Image,ImageDraw
from pathlib import Path
import numpy as np,json,hashlib
O=Path(__file__).parent;R=O.parent;B=R/'south-walk-mesh-correction-v1';sources={p:Image.open(B/f'raw/source-{p}.png').convert('RGBA') for p in range(57,63)};base={p:Image.open(B/f'baseline/{p}-s0.72.png').convert('RGBA') for p in range(57,63)};new={p:Image.open(O/f'output/mesh-{p}.png').convert('RGBA') for p in range(57,63)}
bgs=[(24,27,32),(128,128,128),(236,236,230)];audit={'playback_order':list(range(57,63)),'frame_duration_ms':140,'loop_duration_ms':840,'scope':'prescribed-phase GIF playback, not actual main-game50Hz or display wall-clock validation','gif_readback':{},'rendered_feet_driven_not_independent':[]}
def tile(im,w,bg,nearest=False):
 b=Image.new('RGBA',(w,w),bg+(255,));b.alpha_composite(im.resize((w,w),Image.Resampling.NEAREST if nearest else Image.Resampling.LANCZOS));return b.convert('RGB')
for scale in [1,2]:
 w=128*scale;board=Image.new('RGB',(6*w,3*(w+24)),(80,85,90));d=ImageDraw.Draw(board)
 for col,p in enumerate(range(57,63)):
  for row,frames in enumerate([sources,base,new]):
   board.paste(tile(frames[p],w,bgs[1],row==0),(col*w,row*(w+24)+24));d.text((col*w+3,row*(w+24)+5),f'{p} '+['SOURCE','COMMON BASE','GODOT ARAP'][row],fill='white')
 board.save(O/f'SOURCE_BASE_ARAP_SIX_{scale}X.png')
 edges=Image.new('RGB',(6*w,3*(w+24)),(80,85,90));ed=ImageDraw.Draw(edges)
 for row,bg in enumerate(bgs):
  for col,p in enumerate(range(57,63)):
   edges.paste(tile(new[p],w,bg),(col*w,row*(w+24)+24));ed.text((col*w+3,row*(w+24)+5),f'{p} '+['DARK','GRAY','LIGHT'][row],fill='white')
 edges.save(O/f'ARAP_SIX_THREE_BACKGROUNDS_{scale}X.png')
 frames=[]
 for p in range(57,63):
  frame=Image.new('RGB',(3*w,w+28),bgs[1]);fd=ImageDraw.Draw(frame)
  for col,ims in enumerate([sources,base,new]):frame.paste(tile(ims[p],w,bgs[1],col==0),(col*w,28));fd.text((col*w+3,5),f'{p} '+['SOURCE','BASE','ARAP'][col]+' 140ms',fill='white')
  frames.append(frame)
 path=O/f'SOURCE_BASE_ARAP_LOOP_140MS_{scale}X.gif';frames[0].save(path,save_all=True,append_images=frames[1:],duration=[140]*6,loop=0,disposal=2)
 gif=Image.open(path);dur=[]
 for i in range(gif.n_frames):gif.seek(i);dur.append(gif.info.get('duration'))
 audit['gif_readback'][path.name]={'frames':gif.n_frames,'durations_ms':dur,'total_ms':sum(dur),'loop':gif.info.get('loop')}
 # Freeze difficult adjacent transitions with no interpolation/crop-to-person.
 pairs=[(58,59),(61,62),(62,57)];tb=Image.new('RGB',(6*w,2*(w+24)),(80,85,90));td=ImageDraw.Draw(tb)
 for pairidx,pair in enumerate(pairs):
  for k,p in enumerate(pair):
   col=pairidx*2+k
   for row,ims in enumerate([sources,new]):tb.paste(tile(ims[p],w,bgs[1],row==0),(col*w,row*(w+24)+24));td.text((col*w+3,row*(w+24)+5),f'{pair[0]}>{pair[1]}: {p} '+['SRC','ARAP'][row],fill='white')
 tb.save(O/f'TRANSITIONS_58_59__61_62__62_57_{scale}X.png')
for p in range(57,63):
 a=np.array(new[p])[:,:,3];yy,xx=np.indices(a.shape);feet=[]
 for lo,hi in [(105,162),(162,215)]:
  ys,xs=np.where((a>=128)&(xx>=lo)&(xx<hi)&(yy>250));y=int(ys.max());feet.append([float(xs[ys==y].mean()),y])
 audit['rendered_feet_driven_not_independent'].append({'phase':p,'visible_sole_extrema_HD':feet,'delta_y_logical':(feet[0][1]-feet[1][1])/4})
(O/'REVIEW_AUDIT.json').write_text(json.dumps(audit,indent=2));(O/'REVIEW_SHA256.json').write_text(json.dumps({x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in O.iterdir() if x.suffix in ['.png','.gif']},indent=2));print(json.dumps(audit,indent=2))
