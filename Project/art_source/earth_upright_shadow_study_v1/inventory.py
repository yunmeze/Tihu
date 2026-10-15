from pathlib import Path
import json, numpy as np
P=Path(__file__).resolve().parents[2];d=P/'diagnostics/earth-upright-shadow-study';r=json.loads((d/'measurements.json').read_text());m=json.loads((P/'data/maps/A13.json').read_text());packs=json.loads((P/'assets/original/manifest.json').read_text())['packs'];groups={1:'Map/Res/Debris',2:'Map/Res/Plant',3:'Map/Res/Wall',4:'Map/Res/Building'}
for row in r['instances']:
 b=np.array(row['full_conservative_world_bounds_xyxy']);lo=np.floor(b[:2]).astype(int);hi=np.ceil(b[2:]).astype(int);row['minimal_integer_validation_world_rect']=[*lo.tolist(),*(hi-lo).tolist()];row['root_uncertainty_review_world_rect']=[*(lo-10).tolist(),*(hi-lo+20).tolist()];query=np.r_[lo-10,hi+10];records=[]
 for order,cell in enumerate(m['cells']):
  x,y=divmod(order,100)
  for kind,index,pack,top in [('floor',abs(cell[0]),'Map/Res/FloorBig' if cell[0]<0 else 'Map/Res/FloorSmall',0),('object',cell[3],groups.get(cell[2]),None)]:
   if pack not in packs or (kind=='floor' and not cell[0]):continue
   f=packs[pack]['frames'].get(str(index))
   if not f:continue
   origin=np.array([x*48,y*32])+f['crop']+[0,(32-f['original'][1])if top is None else top];bounds=np.r_[origin,origin+f['rect'][2:]]
   if not ((bounds[2:]>query[:2]).all()and(bounds[:2]<query[2:]).all()):continue
   records.append({'kind':kind,'pack':pack,'frame_index':index,'cell':[x,y],'source_cell':cell,'order':order,'world_rgba_rect':bounds.tolist(),'page':packs[pack]['pages'][f['page']]['file'],'page_sha256':packs[pack]['pages'][f['page']]['sha256']})
 row['source_records_aabb_review_superset']=records;row['source_record_counts']={k:sum(t['pack']==k for t in records)for k in sorted({t['pack']for t in records})}
(d/'measurements.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps([{k:row[k]for k in ['instance','minimal_integer_validation_world_rect','root_uncertainty_review_world_rect','source_record_counts']}for row in r['instances']],indent=2))
