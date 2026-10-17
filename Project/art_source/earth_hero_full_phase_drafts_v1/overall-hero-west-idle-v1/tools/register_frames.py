from PIL import Image
from pathlib import Path
import json,hashlib
p=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ref=json.loads((p/'provenance/original-reference-contract.json').read_text())
out={'schema':'hero-west-idle-first-draft-registration-v1','status':'art-only-candidate-awaiting-runtime-and-direction-transition-review','logical_canvas':[128,128],'root':[16,64],'draw_offset':[-16,-64],'density':4,'output_frame_size':[512,512],'output_sheet_layout':'four horizontal row-major slots','source_frame_size':[627,627],'uniform_scale_all_directions':364/627,'method':'resize whole source cell uniformly to 364 square then translate whole frame; same translation for all four phases of each direction; no local warp, mirror, repaint, face synthesis or per-phase scaling','alpha':'original generated alpha preserved, including extremely faint stray pixels; threshold127 used only for measurement, never editing','runtime_modified':False,'directions':{}}
for d,tx,ty in [('SW',34,14),('W',38,29),('NW',25,14)]:
 im=Image.open(p/f'raw/{d}-raw.png')
 sheet=Image.new('RGBA',(2048,512));rows=[]
 for n in range(4):
  rect=[(n%2)*627,(n//2)*627,627,627];x,y,w,h=rect
  c=im.crop((x,y,x+w,y+h));a=c.getchannel('A').point(lambda x:255 if x>127 else 0);bb=a.getbbox()
  dst=Image.new('RGBA',(512,512));dst.alpha_composite(c.resize((364,364),Image.Resampling.LANCZOS),(tx,ty))
  dst.save(p/f'registered/{d}-phase{n}.png');sheet.alpha_composite(dst,(n*512,0))
  db=dst.getchannel('A').point(lambda x:255 if x>127 else 0).getbbox()
  original=ref['directions'][d][n]
  rows.append({'phase':n,'original_frame_id':original['frame_id'],'source_region':rect,'output_region':[n*512,0,512,512],'raw_visible_bbox_alpha_gt127':bb,'registered_visible_bbox_alpha_gt127':db,'whole_frame_translation_px':[tx,ty],'registered_rgba_sha256':hashlib.sha256(dst.tobytes()).hexdigest(),'source_composite_bbox':original['composite_bbox'],'bottom_edge_delta_px_against_original_composite':db[3]-4*original['composite_bbox'][3],'note':'bottom edge diagnostic only; original composite includes original checker shadow, so this is not a measured anatomical foot anchor'})
 sheet.save(p/f'registered/{d}-body.png')
 out['directions'][d]={'raw_file':f'raw/{d}-raw.png','raw_size':list(im.size),'raw_sha256':sha(p/f'raw/{d}-raw.png'),'sheet_file':f'registered/{d}-body.png','sheet_sha256':sha(p/f'registered/{d}-body.png'),'frames':rows,'distinct_rgba_frames':len(set(r['registered_rgba_sha256'] for r in rows))}
(p/'registration-contract.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
files={str(f.relative_to(p)):sha(f) for f in p.rglob('*') if f.is_file() and f.name!='sourceSHA256.json'}
(p/'provenance/sourceSHA256.json').write_text(json.dumps(files,indent=2))
print(json.dumps({d:{'distinct':v['distinct_rgba_frames'],'bottom_delta':[f['bottom_edge_delta_px_against_original_composite'] for f in v['frames']]} for d,v in out['directions'].items()}))
