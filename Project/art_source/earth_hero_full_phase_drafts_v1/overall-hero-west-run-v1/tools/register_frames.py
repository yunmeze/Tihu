from PIL import Image
from pathlib import Path
import json,hashlib,shutil
p=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=json.loads((p/'provenance/original-reference-contract.json').read_text())
r={'schema':'hero-west-run-first-pass-v1','status':'candidate-not-runtime-accepted','action':'run','phases':6,'actor_ticks_per_phase':5,'logical_canvas':[128,128],'root':[16,64],'draw_offset':[-16,-64],'density':4,'output_frame':[512,512],'uniform_scale_all_frames':342/512,'method':'Uniform whole-cell resize 512 to342, fixed translation per direction across all six phases; no per-phase foot snap, no warp or mirror. Generated phase bob preserved; exact original head/hip agreement unverified.','alpha':'Preserved unedited; threshold127 only for measurements','directions':{}}
for d,tx,ty in [('S',0,25),('SW',20,25),('W',35,25),('NW',30,25)]:
 im=Image.open(p/f'raw/{d}-raw.png');a=im.getchannel('A');hist=a.histogram();rows=[];sheet=Image.new('RGBA',(3072,512))
 for n in range(6):
  x=n%3*512;y=n//3*512;c=im.crop((x,y,x+512,y+512));dst=Image.new('RGBA',(512,512));dst.alpha_composite(c.resize((342,342),Image.Resampling.LANCZOS),(tx,ty));dst.save(p/f'registered/{d}-phase{n}.png');sheet.alpha_composite(dst,(n*512,0));rows.append({'phase':n,'original_frame_id':ref['directions'][d][n]['frame_id'],'source_rect':[x,y,512,512],'output_rect':[n*512,0,512,512],'translation_px':[tx,ty],'visible_bbox_alpha_gt127':dst.getchannel('A').point(lambda a:255 if a>127 else 0).getbbox(),'rgba_sha256':hashlib.sha256(dst.tobytes()).hexdigest()})
 sheet.save(p/f'registered/{d}-body.png');r['directions'][d]={'raw':f'raw/{d}-raw.png','raw_size':im.size,'raw_sha256':sha(p/f'raw/{d}-raw.png'),'sheet':f'registered/{d}-body.png','sheet_sha256':sha(p/f'registered/{d}-body.png'),'alpha_extrema':a.getextrema(),'alpha_zero_pixels':hist[0],'alpha_1_to_10_pixels':sum(hist[1:11]),'alpha_11_to_127_pixels':sum(hist[11:128]),'alpha_128_to_254_pixels':sum(hist[128:255]),'phase_count':len(rows),'distinct_frames':len(set(x['rgba_sha256'] for x in rows)),'frames':rows}
(p/'registration-contract.json').write_text(json.dumps(r,indent=2));shutil.copy2(p.parent/'overall-hero-full-source-contract-v1.json',p/'provenance/full-source-contract.json')
files={str(f.relative_to(p)):sha(f) for f in p.rglob('*') if f.is_file() and f.name!='sourceSHA256.json'}
# Include exact external identity input hashes used by image generation.
for d in ['S','SW','W','NW']:
 for f in json.loads((p/f'provenance/{d}-actualargs.json').read_text())['referenced_image_paths']:files[f]=sha(Path(f))
(p/'provenance/sourceSHA256.json').write_text(json.dumps(files,indent=2))
print(json.dumps({d:{'phases':v['distinct_frames'],'alpha_zero':v['alpha_zero_pixels']} for d,v in r['directions'].items()}))
