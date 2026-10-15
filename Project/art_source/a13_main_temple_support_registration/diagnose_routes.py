from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent;D=P/'diagnostics/art_source/a13-main-temple';c=json.loads((P/'art_source/a13_main_temple_source/source-group-contract.json').read_text());g=json.loads((P/'art_source/a13_main_temple_candidate_v2/independent-support-roof-check.json').read_text())['support'];s=g['scale'];tx,ty=g['translation'];raw=Image.open(P/'art_source/a13_main_temple_candidate_v2/raw.png').convert('RGBA');new=raw.transform(tuple(c['composite_size']),Image.Transform.AFFINE,(1/s,0,-tx/s,0,1/s,-ty/s),resample=Image.Resampling.BICUBIC);old=Image.open(D/'source-composite.png').convert('RGBA');m=json.loads((P/'data/maps/A13.json').read_text());h=json.loads((P/'data/hero/movement.json').read_text());f=h['layers']['body']['frames']['17'];feet=[[10,64],[24,69]];relative=[[x+f['offset'][0],y+f['offset'][1]]for x,y in feet];rows=[];board=Image.new('RGBA',(1592,695),(100,110,100,255));board.alpha_composite(old,(0,30));board.alpha_composite(new,(796,30));d=ImageDraw.Draw(board)
for k,off in [('SOURCE',0),('V2 SUPPORT COMMON SCALE ONLY',796)]:d.text((off+6,8),k,fill='white')
for o in c['owners_in_draw_order']:
 if o['layer']!=0:continue
 x,y=o['cell'];origin=[x*48-2948,y*32-642];samples=[]
 for rx,ry in relative:
  q=[origin[0]+rx,origin[1]+ry];candidate=[(q[0]-tx)/s,(q[1]-ty)/s];samples.append({'source_canvas':q,'candidate_raw':candidate})
 for off in [0,796]:
  ox,oy=origin[0]+off,origin[1]+30;d.line((ox-3,oy,ox+3,oy),fill='orange');d.line((ox,oy-3,ox,oy+3),fill='orange');d.text((ox-6,oy-12),f'{x},{y}',fill='white')
  for sample in samples:
   px,py=sample['source_canvas'];px+=off;py+=30;d.ellipse((px-2,py-2,px+2,py+2),outline='cyan',width=1)
 rows.append({'cell':[x,y],'flag':o['flag'],'source_owner':o['key'],'original_layer':o['layer'],'sort_y':y,'actor_draw_origin_source_canvas':origin,'phase17_boot_samples':samples})
board.convert('RGB').save(D/'v2-support-registration-foot-samples.jpg')
# Lower-half detail retains same uniform scale, no additional geometry manipulation.
board.crop((120,410,1592,695)).convert('RGB').save(D/'v2-support-registration-lower-detail.jpg')
report={'status':'read_only_route_foot_diagnostic_not_native','registration':{'kind':'single uniform scale+translation for whole candidate','scale':s,'translation_source_canvas':[tx,ty],'world_origin_of_source_canvas':[2948,642],'raw_rgba_changed':False},'hero_evidence':{'manifest':'res://data/hero/movement.json','phase':17,'body_original':f['original'],'body_offset':f['offset'],'actual_boot_read_local':feet,'actual_boot_relative_to_actor_origin':relative,'uncertainty_px':2,'read_method':'Manual visible pale boot toe pixels; excludes checker shadow and does not use alpha bbox as feet.','limitation':'Two stationary south-facing toe/contact samples, not all movement foot phases or full anatomical contact polygons.'},'samples':rows,'source_connectivity':'All12 layer0 cells have static no-corner-cut paths from61,39 in prior support-analysis.json; no runtime route claimed here.','depth_limits':['Whole candidate shown only as geometric context; no full-building layer assignment is proposed.','Original twelve layer0 support strips must be re-partitioned by true top/riser/rail boundaries, preserving source keys and y/layer.','New generated rail/riser boundaries cannot be assigned by old rectangles alone.','Original source faces sometimes occlude paths; native source/new draw order must be compared before acceptance.']};(HERE/'route-foot-diagnostic.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report['hero_evidence']))
