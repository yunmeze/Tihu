"""Verify archived request bytes and replay deterministic mappings; never call generation."""
from pathlib import Path
import argparse,hashlib,json
from PIL import Image
A=argparse.ArgumentParser();A.add_argument('--output',required=True);args=A.parse_args()
H=Path(__file__).resolve().parent;P=H.parents[1];O=Path(args.output).resolve()
if O==P or P in O.parents:raise ValueError('Output must be outside Project')
O.mkdir(parents=True,exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def same(im,target,name):
 f=O/name;im.save(f);assert sha(f)==sha(target),(name,'PNG byte mismatch');assert im.convert('RGBA').tobytes()==Image.open(target).convert('RGBA').tobytes();return sha(f)
for n,h in read(H/'SHA256.json').items():assert sha(H/n)==h,n
meta=read(H/'ARCHIVE.json')
for r in meta['tracked_dependencies']:assert sha(P/r['path'])==r['sha256'],r['path']
result={'status':meta['status'],'generated_sampling_replayed':False,'input_byte_integrity':True,'outputs':{}}
if meta['kind']=='west-building':
 g=read(H/'source_geometry.json');b=g['group']['bounds_xyxy'];im=Image.new('RGBA',(b[2]-b[0],b[3]-b[1]));m=read(P/'data/maps/A13.json')
 for owner in g['group']['owners']:
  assert m['cells'][owner['stable_source_order']]==owner['source_cell']
  f=g['frames'][owner['frames'][0]['frame_key']];x,y,w,h=f['atlas_rect'];crop=Image.open(P/f['atlas'][6:]).convert('RGBA').crop((x,y,x+w,y+h));assert hashlib.sha256(crop.tobytes()).hexdigest()==f['rgba_sha256'];z=owner['all_frame_bounds_xyxy'];im.alpha_composite(crop,(z[0]-b[0],z[1]-b[1]))
 im.save(O/'source-235-253.png');contract=read(H/'contract-before-generation.json');expected=next(v for k,v in contract['input_sha256'].items() if k.endswith('/source-235-253.png'));assert sha(O/'source-235-253.png')==expected
 pad=Image.new('RGBA',(832,832));pad.alpha_composite(im,(25,138));result['outputs']['primary']=same(pad,H/'primary-source-complete-padded.png','primary.png')
 req=read(H/'actual_request.json');assert sha(H/req['prompt'])==req['prompt_sha256']
 for r in req['references']:assert sha(H/r['package_path'] if 'package_path' in r else P/r['project_path'])==r['sha256']
 result['raw_sha256']=sha(H/'generated-raw.png');result['mapping']={'canvas_world_origin':[1401,522],'logical_square':832,'density':Image.open(H/'generated-raw.png').width/832}
elif meta['kind']=='daotong':
 pack=read(P/'assets/original/manifest.json')['packs']['Npc'];f=pack['frames']['293'];x,y,w,h=f['rect'];im=Image.open(P/pack['pages'][int(f['page'])]['file'][6:]).convert('RGBA').crop((x,y,x+w,y+h));assert hashlib.sha256(im.tobytes()).hexdigest()==f['rgba_sha256'];pad=Image.new('RGBA',(640,640));pad.alpha_composite(im.resize((384,432),Image.Resampling.NEAREST),(112,80));same(pad,H/'primary-source293-complete-square.png','primary.png')
 for src,rect,dest in [('lingyunzi_v2',(180,304,265,390),'material-ling-jacket-hands.png'),('fangzhang_v1',(113,303,179,366),'material-fang-wrist-sleeve.png')]:same(Image.open(P/f'assets/earth/npc/{src}/body.png').convert('RGBA').crop(rect),H/dest,dest)
 req=read(H/'contract-before-generation.json');assert sha(H/'prompt_actual.txt')==req['prompt_sha256']
 for r in req['refs']:assert sha(H/Path(r['path']).name)==r['sha256']
 raw=Image.open(H/'generated-raw.png').convert('RGBA');mapped=raw.convert('RGBa').resize((320,320),Image.Resampling.LANCZOS).convert('RGBA');body=Image.new('RGBA',(512,640));body.alpha_composite(mapped,(84,296));result['outputs']['candidate']=same(body,H/'candidate293-density4.png','candidate293-density4.png')
else:
 resolution=read(H/'reference_resolution.json')
 for stage in ['generation-attempt1','phase59-attempt1','phase59-arm-edit1']:
  req=read(H/stage/'REQUEST_FROZEN.json');assert sha(H/stage/'PROMPT.txt')==req['prompt_sha256']
  for ref in req['references']:
   r=resolution[ref['path']];assert r['sha256']==ref['sha256'];assert sha(H/r['package_path'] if 'package_path' in r else P/r['project_path'])==ref['sha256']
 raw=Image.open(H/'phase59-attempt1/RAW.png').convert('RGBA');result['outputs']['display']=same(raw.resize((512,512),Image.Resampling.LANCZOS),H/'phase59-attempt1/DISPLAY_FULLCANVAS_512.png','DISPLAY_FULLCANVAS_512.png')
 frozen=read(H/'phase59-arm-edit1/OWNERSHIP_FROZEN.json');assert sha(H/'phase59-attempt1/RAW.png')==frozen['original_raw_sha256']
 for key,name in [('support_sha256','FROZEN_RIGHT_ARM_SUPPORT.png'),('core_priority_sha256','FROZEN_CORE_PRIORITY.png')]:assert sha(H/'phase59-arm-edit1'/name)==frozen[key]
 result['failed_arm_composition']='No executed donor extraction or composite exists; raw and frozen intended support retained.'
(O/'REPRODUCTION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
