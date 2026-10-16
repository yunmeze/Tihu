from PIL import Image,ImageDraw
from pathlib import Path
import json,hashlib,shutil
import numpy as np
import os
O=Path(__file__).parent; project=Path(os.environ['ARAP_SOURCE_PROJECT']); (O/'raw').mkdir(exist_ok=True); (O/'baseline').mkdir(exist_ok=True); raw=Image.open(project/'art_source/earth_s_whole_six_fitted_redraw_research_v1/RAW.png').convert('RGBA'); order=[57,60,58,61,62,59]
source=project/'art_source/hero_s_walk_source_r8'
frames={}
for i,p in enumerate(order):
 q=raw.crop((i%2*512,i//2*512,i%2*512+512,i//2*512+512));q.save(O/f'raw/{p}.png');frames[p]=q
 shutil.copyfile(source/f'source-{p}.png',O/f'raw/source-{p}.png')
# No foot or whole-body bounding box used to solve this provisional calibration.
# Fixed top reference after column translation: raw (233,41) -> source (40.5,15.5)*4.
for s in [.68,.72,.76]:
 tx=162-s*233;ty=62-s*41
 for p in order:
  col=order.index(p)%2;dx=tx-s*35*col
  q=frames[p].transform((512,512),Image.Transform.AFFINE,(1/s,0,-dx/s,0,1/s,-ty/s),Image.Resampling.BICUBIC)
  q.save(O/f'baseline/{p}-s{s:.2f}.png')
for scale in [1,2]:
 w=128*scale; board=Image.new('RGB',(6*w,4*(w+24)),(83,88,94));d=ImageDraw.Draw(board)
 for c,p in enumerate(range(57,63)):
  paths=[O/f'raw/source-{p}.png']+[O/f'baseline/{p}-s{s:.2f}.png' for s in [.68,.72,.76]]
  for r,path in enumerate(paths):
   q=Image.open(path).convert('RGBA').resize((w,w),Image.Resampling.NEAREST if r==0 else Image.Resampling.LANCZOS)
   bg=Image.new('RGBA',(w,w),(83,88,94,255));bg.alpha_composite(q);board.paste(bg,(c*w,r*(w+24)+24));d.text((c*w+3,r*(w+24)+4),f'{p} '+(['SOURCE','.68 BASE','.72 BASE','.76 BASE'][r]),fill='white')
 board.save(O/f'BASELINE_SENSITIVITY_{scale}X.png')
manifest={'status':'CPU baseline only; no mesh or Godot execution yet','raw_sha256':hashlib.sha256((project/'art_source/earth_s_whole_six_fitted_redraw_research_v1/RAW.png').read_bytes()).hexdigest(),'slot_order':order,'common_scale':.72,'sensitivity_scales':[.68,.72,.76],'scale_status':'provisional diagnostic calibration; NOT fitted or proven anatomy','column_shift_HD':[0,-35],'common_reference_raw_HD':[233,41],'common_reference_source_HD':[162,62],'reference_meaning':'visible hair crown registration, not joint','uncertainty_source_logical_px':1.5,'raw_crown_uncertainty_HD_px':3,'no_per_frame_scale':True,'foot_or_full_bbox_used_to_fit_scale':False,'timing_ms':140,'root_logical':[16,64]}
(O/'CALIBRATION.json').write_text(json.dumps(manifest,indent=2))
