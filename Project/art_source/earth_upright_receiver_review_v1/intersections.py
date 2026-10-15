from pathlib import Path
import runpy,json,numpy as np
from PIL import Image
P=Path(__file__).resolve().parents[2];ns=runpy.run_path(str(P/'art_source/earth_upright_shadow_study_v1/measure.py'));g=ns['g'];origin=ns['origin'];size=ns['size'];envs=ns['globalmasks'];r=json.loads((P/'diagnostics/earth-upright-receiver-review/report.json').read_text());packs=json.loads((P/'assets/original/manifest.json').read_text())['packs'];cache={}
for i,row in enumerate(r):
 for rec in row['records']:
  p=packs[rec['pack']];f=p['frames'][str(rec['frame_index'])];page=p['pages'][f['page']]['file'][6:]
  if page not in cache:cache[page]=np.array(Image.open(P/page).convert('RGBA'))[:,:,3]
  x,y,w,h=f['rect'];a=cache[page][y:y+h,x:x+w];o=np.array(rec['world_rgba_rect'][:2]);rect=g.rects_for(a>0,o,1,0);mask=g.raster(rect,origin,size);expanded=g.raster(g.rects_for(a>0,o,1,4),origin,size);rec['full_shadow_envelope_overlap_cells']=int((envs[i]&mask).sum());rec['full_shadow_envelope_overlap_plus4_cells']=int((envs[i]&expanded).sum())
(P/'diagnostics/earth-upright-receiver-review/report.json').write_text(json.dumps(r,indent=2)+'\n')
for row in r:
 print(row['instance']);print([(x['pack'],x['frame_index'],x['cell'],x['full_shadow_envelope_overlap_cells'],x['full_shadow_envelope_overlap_plus4_cells'])for x in row['records']if 'Debris' in x['pack']or(x['kind']=='floor' and x['full_shadow_envelope_overlap_cells'])])
