from pathlib import Path
from PIL import Image
import numpy as np,json
P=Path(__file__).resolve().parent;C=P.parent/'earth_hero_s_idle_v1';im=Image.open(C/'raw-v1.png');reg=json.loads((C/'registration-v1.json').read_text());s=reg['common_uniform_scale_raw_to_logical'];rows=[]
for i in range(4):
 a=np.array(im.crop((543*i,0,543*(i+1),724)));tr=np.array(reg['records'][i]['translation_raw_scaled_to_logical']);hands={}
 for side,(x0,y0,x1,y1) in [('L',(130,320,180,415)),('R',(355,320,410,415))]:
  yy,xx=np.where(a[y0:y1,x0:x1,3]>=128);y=int(yy.max()+y0);xx=np.where(a[y,x0:x1,3]>=128)[0]+x0;q=np.array([float(xx.mean()),y]);hands[side]={'raw_roi':[x0,y0,x1,y1],'raw_outline_terminal':q.tolist(),'registered_outline_terminal':(q*s+tr).tolist()}
 rows.append({'source_id':17+i,'registered_crown_Lboot_Rboot':(np.array(reg['records'][i]['raw_surface_anchors_crown_Lterminal_Rterminal'])*s+tr).tolist(),'hands':hands})
(P/'PHASE_PROXY_CHECK.json').write_text(json.dumps({'status':'static_surface_only_no_exact_animation_certification','method':'alpha128 extrema inside fixed hand-outline ROIs and original global registration','uncertainty_raw_px':4,'source_crown_boot_uncertainty_logical_px':1,'source_hand_surface_uncertainty_logical_px':3,'boundary':'new hand outline ends only; not homologous to old source skin-patch centers; no direct swing subtraction','records':rows},ensure_ascii=False,indent=2)+'\n')
