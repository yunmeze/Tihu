from pathlib import Path
import runpy,json,numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[2];O=P/'diagnostics/earth-upright-receiver-review';n=runpy.run_path(str(P/'art_source/earth_upright_shadow_study_v1/measure.py'));e=n['globalmasks'][1];org=n['origin'];packs=json.loads((P/'assets/original/manifest.json').read_text())['packs'];pack=packs['Map/Res/Debris'];page=Image.open(P/pack['pages'][0]['file'][6:]).convert('RGBA');rows=json.loads((O/'report.json').read_text())[1]['records'];out=[]
for rec in rows:
 if 'Debris'not in rec['pack']:continue
 f=pack['frames'][str(rec['frame_index'])];x,y,w,h=f['rect'];im=page.crop((x,y,x+w,y+h));a=np.array(im);ox,oy=rec['world_rgba_rect'][:2];hit=np.zeros((h,w),bool)
 for yy,xx in zip(*np.nonzero(a[:,:,3])):
  gx=int((ox+xx-org[0])*2);gy=int((oy+yy-org[1])*2)
  if 0<=gx<e.shape[1]-1 and 0<=gy<e.shape[0]-1:hit[yy,xx]=e[gy:gy+2,gx:gx+2].any()
 ys,xs=np.nonzero(hit);out.append({'index':rec['frame_index'],'positive_source_texels_hit':len(xs),'local_xy':np.stack((xs,ys),1).tolist()});a[hit,:3]=[255,0,0];Image.fromarray(a).crop((0,0,w,55)).resize((w*8,440)).save(O/f'debris-{rec["frame_index"]}-contact-top.png')
(O/'debris-contact.json').write_text(json.dumps(out,indent=2)+'\n');print([(q['index'],q['positive_source_texels_hit'],q['local_xy'][:3])for q in out])
