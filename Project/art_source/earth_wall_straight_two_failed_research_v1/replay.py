"""Bounded technical replay. No art repair, fitting, generation, or engine."""
from pathlib import Path
import argparse,json,hashlib,subprocess,io
import numpy as np
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--selection',type=Path);p.add_argument('--report',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parent;prefix='Project/art_source/earth_wall_straight_two_failed_research_v1/'
selection=json.loads(a.selection.read_text())['files'] if a.selection else None
paths={r['path'][len(prefix):]:Path(r['copy_source']) for r in selection} if selection else {}
def path(rel):return paths.get(rel,root/rel)
def sha(b):return hashlib.sha256(b).hexdigest()
deps=json.loads(path('DEPENDENCIES.json').read_text());blobs={}
for r in deps['files']:
 b=subprocess.check_output(['git','-C',str(a.repo),'show',deps['commit']+':'+r['path']]);assert sha(b)==r['sha256'] and len(b)==r['bytes'];blobs[r['path']]=b
index=json.loads(path('source/SOURCE_INDEX.json').read_text());frames={f['key']:f for f in index['frames']};atlas=Image.open(io.BytesIO(blobs['Project/assets/original/Map/Res/Wall/0.png'])).convert('RGBA')
def compose(owners,bounds):
 im=Image.new('RGBA',(bounds[2]-bounds[0],bounds[3]-bounds[1]))
 for o in sorted(owners,key=lambda o:(o['layer'],o['sort_y'],o['stable_source_order'])):
  f=frames[o['frame_key']];x,y,w,h=f['atlas_rect'];tile=atlas.crop((x,y,x+w,y+h));assert sha(tile.tobytes())==f['rgba_sha256'];b=o['world_bounds_xyxy'];im.alpha_composite(tile,(b[0]-bounds[0],b[1]-bounds[1]))
 return im
for name,owners,bounds in [('INPUT_01_SOURCE_FIXED_256x384.png',index['pilot_owners'],[688,333,944,717]),('INPUT_02_TRUE_NEIGHBORS_624x569.png',index['left_repeat_owners']+index['pilot_owners']+index['right_corner_owners'],[528,257,1152,826])]:
 im=compose(owners,bounds);buf=io.BytesIO();im.save(buf,format='PNG');assert sha(buf.getvalue())==sha(path('source/'+name).read_bytes())
results=[]
for trial in ('pilot','edit'):
 raw=path(trial+'/generated-raw.png');m=json.loads(path(trial+'/MEASUREMENTS.json').read_text());pins=json.loads(path(trial+'/ACTUAL_INPUT_SHA256.json').read_text());args=json.loads(path(trial+'/ACTUAL_TOOL_ARGUMENTS.json').read_text());prompt=path(trial+'/PROMPT_ACTUAL.txt').read_text();assert args['prompt']==prompt and args['transparent_background'] is True;assert len(pins)==len(deps['actual_refs'][trial])==3;assert args['referenced_image_paths']==[r['path'] for r in pins]
 for r,ref in zip(pins,deps['actual_refs'][trial]):
  b=blobs[ref['repository_path']] if isinstance(ref,dict) else path(ref).read_bytes();assert sha(b)==r['sha256'] and len(b)==r['bytes']
 im=Image.open(raw);assert im.mode=='RGBA' and im.size==(1024,1536);rgba=np.array(im);alpha=rgba[:,:,3];assert sha(raw.read_bytes())==m['png_sha256'] and sha(im.tobytes())==m['rgba_sha256'];assert np.bincount(alpha.ravel(),minlength=256).tolist()==m['raw_alpha_histogram']
 sx=688+(np.arange(1024)+.5)/4;sy=333+(np.arange(1536)+.5)/4;union=np.zeros(alpha.shape,bool)
 for o in index['pilot_owners']:
  l,t,r,b=o['world_bounds_xyxy'];union|=(sx[None,:]>=l)&(sx[None,:]<r)&(sy[:,None]>=t)&(sy[:,None]<b)
 source=np.array(Image.open(path('source/INPUT_01_SOURCE_FIXED_256x384.png')))[:,:,3];support=np.repeat(np.repeat(source>0,4,axis=0),4,axis=1)
 for key,r in m['thresholds'].items():
  mask=alpha>=int(key);assert int(mask.sum())==r['count'];assert int((mask&~union).sum())==r['outside_original_owner_rectangle_union'];assert int((mask&~support).sum())==r['outside_original_source_alpha_support']
 seam=json.loads(path(trial+'/REPEAT_SEAM_MEASUREMENTS.json').read_text());mask=alpha>=128;overlap=int((mask[512:,:256]&mask[:-512,768:]).sum());assert overlap==seam['high_alpha128_overlap_pixel_count']
 results.append({'trial':trial,'raw_sha256':m['png_sha256'],'alpha_and_support_threshold_counts_exact':True,'repeat_alpha128_overlap_exact':overlap,'status':'FAIL retained'})
a.report.write_text(json.dumps({'reference_png_byte_exact':True,'actual_refs_in_order_verified':True,'results':results,'limits':'Does not reproduce all semantic reading, full map/source investigation, review boards or runtime. No changes to raw, no registration/repair. Whole1024x1536 ->256x384 RGBA LANCZOS is display only, world=[688,333]+raw/4.'},indent=2)+'\n');print(a.report)
