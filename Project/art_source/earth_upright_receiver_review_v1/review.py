from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[2];O=P/'diagnostics/earth-upright-receiver-review';r=json.loads((P/'art_source/earth_upright_shadow_study_v1/measurements.json').read_text());packs=json.loads((P/'assets/original/manifest.json').read_text())['packs'];pages={}
def rgba(pack,index):
 p=packs[pack];f=p['frames'][str(index)];path=p['pages'][f['page']]['file'][6:]
 if path not in pages:pages[path]=Image.open(P/path).convert('RGBA')
 x,y,w,h=f['rect'];return pages[path].crop((x,y,x+w,y+h))
results=[]
for row in r['instances']:
 x,y,w,h=row['root_uncertainty_review_world_rect'];canvas=Image.new('RGBA',(w,h));cover=np.zeros((h,w),np.uint16);obj=Image.new('RGBA',(w,h));records=[]
 for rec in row['source_records_aabb_review_superset']:
  image=rgba(rec['pack'],rec['frame_index']);rx,ry,_,_=rec['world_rgba_rect'];layer=Image.new('RGBA',(w,h));layer.paste(image,(rx-x,ry-y));a=np.array(layer)[:,:,3];d={**rec,'actual_positive_alpha_pixels_inside_review':int((a>0).sum()),'source_draw_layer':('floor' if rec['kind']=='floor' else 0 if rec['source_cell'][1] in [1,-2] else 2 if rec['source_cell'][1]==2 else 1),'alpha_max_inside_review':int(a.max()),'alpha_128_pixels_inside_review':int((a>=128).sum())};records.append(d)
  if rec['kind']=='floor':canvas=Image.alpha_composite(canvas,layer);cover+=(a>0)
  else:obj=Image.alpha_composite(obj,layer)
 composite=Image.alpha_composite(canvas,obj);canvas.save(O/(row['instance']+'-floor.png'));composite.resize((w*2,h*2)).save(O/(row['instance']+'-source-context.png'))
 Image.fromarray((cover>0).astype(np.uint8)*255).save(O/(row['instance']+'-floor-coverage.png'))
 results.append({'instance':row['instance'],'review_world_rect':[x,y,w,h],'floor_zero_alpha_pixels':int((np.array(canvas)[:,:,3]==0).sum()),'floor_not_opaque_pixels':int((np.array(canvas)[:,:,3]<255).sum()),'max_floor_overlap':int(cover.max()),'records':records})
for index in [57,58,59]:rgba('Map/Res/Debris',index).resize((192,rgba('Map/Res/Debris',index).height*4)).save(O/f'debris-{index}-4x.png')
(O/'report.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps([{k:v for k,v in row.items()if k!='records'}for row in results],indent=2));print(json.dumps([rec for row in results for rec in row['records']if 'Debris' in rec['pack']],indent=2))
