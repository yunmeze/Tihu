"""Read-only portable source check. Python 3, Pillow, NumPy and Git required."""
from pathlib import Path
import argparse,hashlib,json,subprocess,io
import numpy as np
from PIL import Image,ImageDraw
p=argparse.ArgumentParser();p.add_argument('--repo',required=True,type=Path);p.add_argument('--report',required=True,type=Path);a=p.parse_args();root=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def data(n):return (root/n).read_bytes()
def j(n):return json.loads(data(n))
for f in j('FILES_SHA256.json'):
 assert sha(data(f['path']))==f['sha256'],f['path']
deps={}
for f in j('DEPENDENCIES.json'):
 b=subprocess.check_output(['git','-C',str(a.repo),'cat-file','blob',f['blob']]);assert len(b)==f['bytes'] and sha(b)==f['sha256'];deps[f['path']]=b
mapping=j('PATH_MAP.json')
def reference(path):
 target=mapping[path]
 return deps[target['git']] if isinstance(target,dict) else data(target)
report={'archive_sha_checks':True,'git_dependency_count':len(deps),'actual_requests':[],'scope':'Read-only reconstruction and numerical checks. No engine, AI regeneration, solver, or production sprite.'}
if (root/'fourphase').exists():
 stages=['fourphase','single-base','local-edit']
 for stage in stages:
  req=j(stage+'/REQUEST.json');args=req.get('arguments',req);prompt=data(stage+'/PROMPT.txt').decode();assert prompt.strip()==args['prompt'].strip()
  refs=args.get('referenced_image_paths',[x['path'] for x in args.get('refs',[])])
  vals=[sha(reference(x)) for x in refs]
  if 'refs' in args:assert vals==[x['sha256'] for x in args['refs']]
  assert args['transparent_background'] is True
  report['actual_requests'].append({'stage':stage,'ordered_ref_sha256':vals,'raw_sha256':sha(data(stage+'/RAW.png'))})
 mv=json.loads(deps['Project/data/hero/movement.json']);full=Image.new('RGBA',(4096,1024));canvases=[]
 for i in range(21,25):
  layers=[]
  for part in ['body','head']:
   layer=mv['layers'][part];f=layer['frames'][str(i)];atlas=Image.open(io.BytesIO(deps['Project/'+layer['atlas'].removeprefix('res://')]));x,y,w,h=f['rect'];im=atlas.crop((x,y,x+w,y+h));c=Image.new('RGBA',(128,128));c.paste(im,(16+f['offset'][0],64+f['offset'][1]));layers.append(c)
  c=Image.alpha_composite(*layers);canvases.append(c);full.alpha_composite(c.resize((1024,1024),Image.Resampling.NEAREST),((i-21)*1024,0))
 def same_png(im,relative):
  b=io.BytesIO();im.save(b,format='PNG');original=data(relative);assert b.getvalue()==original,relative;return sha(original)
 report['reconstructed_source_sheet']=same_png(full,'source/source21-24-composite-8x.png')
 report['reconstructed_source21']=same_png(full.crop((0,0,1024,1024)),'references/INPUT-original-SW21-full-canvas-8x.png')
 raw=Image.open(io.BytesIO(data('fourphase/RAW.png'))).convert('RGBA');report['reconstructed_actual_first_cell']=same_png(raw.crop((0,0,576,725)),'references/INPUT-candidate-first-cell-full-RGBA.png')
 source=j('source/source-analysis.json');board=Image.new('RGBA',(640,360),(71,75,79,255));draw=ImageDraw.Draw(board)
 for k,f in enumerate(source['material_fragments']):
  src='se_idle_v1' if f['source']=='SE13' else 's_idle_v1';im=Image.open(io.BytesIO(deps['Project/assets/earth/hero/'+src+'/body.png'])).convert('RGBA').crop((0,0,512,512)).crop(f['source_crop_xyxy_half_open']);im=im.resize((im.width*3,im.height*3),Image.Resampling.NEAREST);x=k%4*160;y=k//4*180;board.alpha_composite(im,(x+(160-im.width)//2,y+30));draw.text((x+5,y+5),f['label'],fill='white');draw.text((x+5,y+160),f['source']+' '+','.join(map(str,f['source_crop_xyxy_half_open'])),fill='white')
 report['reconstructed_material_ref']=same_png(board,'source/modern-disconnected-material-reference.png')
 reg=j('local-edit/SOURCE21_COMMON_REGISTRATION.json');rp=np.array([x['raw_xy'] for x in reg['proxies']]);sp=np.array([x['source21_native_xy'] for x in reg['proxies']]);weights=np.array(reg['single_transform']['weights']);xm=np.sum(rp*weights[:,None],0)/sum(weights);ym=np.sum(sp*weights[:,None],0)/sum(weights);xc=rp-xm;yc=sp-ym;s=float(np.sum(weights[:,None]*xc*yc)/np.sum(weights[:,None]*xc*xc));t=ym-s*xm
 assert s==reg['single_transform']['uniform_scale_native_per_raw'];assert t.tolist()==reg['single_transform']['translation_native_xy'];report['common_registration']={'scale':s,'translation':t.tolist(),'numeric_exact':True,'all_four_are_training_proxies':True,'not_independent_heldout':True}
else:
 for stage in ['m2','m3','m1','m1-edit']:
  req=j(stage+'/ACTUAL_TOOL_ARGUMENTS.json');assert req['transparent_background'] is False;assert data(stage+'/PROMPT_ACTUAL.txt').decode().strip()==req['prompt'].strip();vals=[sha(reference(x)) for x in req['referenced_image_paths']];pins=j(stage+'/INPUT_SHA256.json');assert vals==[x['sha256'] for x in pins]
  im=Image.open(io.BytesIO(data(stage+'/generated-raw.png')));v=np.asarray(im).astype(float);edge=np.abs(v[:,0]-v[:,-1]);inside=np.abs(np.diff(v,axis=1));band=v[:,:8].mean(axis=(0,1))-v[:,-8:].mean(axis=(0,1));saved=j(stage+'/MEASUREMENTS.json')
  expected=saved.get('edge_to_interior_mean_ratio',saved.get('edge_mean_ratio',saved.get('edge_to_internal_mean_ratio')));ratio=float(edge.mean()/inside.mean());assert expected is not None and abs(ratio-expected)<1e-12,(stage,expected,ratio)
  report['actual_requests'].append({'stage':stage,'ordered_ref_sha256':vals,'raw_sha256':sha(data(stage+'/generated-raw.png')),'size':im.size,'mode':im.mode,'edge_ratio_exact':ratio,'edge_band_rgb':band.tolist()})
 surface=j('surface-plan/SURFACE_UV_REVIEW.json');support_bytes=deps['Project/art_source/earth_wall_straight_two_failed_research_v1/source/INPUT_01_SOURCE_FIXED_256x384.png'];assert sha(support_bytes)==surface['source_sha256'];support=np.asarray(Image.open(io.BytesIO(support_bytes)).convert('RGBA'))[:,:,3]>0
 assert int(support.sum())==surface['support_native_pixel_count'];rebuilt=np.zeros_like(support)
 for row in surface['source_support_column_runs']:
  for y0,y1 in row['y_half_open_runs']:rebuilt[y0:y1,row['x']]=True
 assert np.array_equal(rebuilt,support)
 report['source_geometry_reference_verified']={'exact_support_pixels':int(support.sum()),'column_runs_exact':True,'uv_not_applied':True}
# Only caller-selected small report is written; raw and archive remain unchanged.
a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
