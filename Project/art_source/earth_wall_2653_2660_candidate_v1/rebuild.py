#!/usr/bin/env python3
"""Offline deterministic reconstruction of the accepted D2 eight-owner candidate.
Uses only bundled unaltered AI pixels and original source geometry; no imagegen.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, __version__ as pillow_version
import argparse, hashlib, json, math, platform, os, stat, numpy as np

P=Path(os.path.abspath(__file__)).parent
def lexical_absolute(path):
 p=Path(path)
 if '..' in p.parts:raise ValueError('Parent traversal is not allowed')
 return p if p.is_absolute() else Path.cwd()/p
def ordinary_path(path,leaf_kind):
 """lstat every component; never resolve a symlink before rejecting it."""
 p=lexical_absolute(path)
 for part in [*reversed(p.parents),p]:
  mode=part.lstat().st_mode
  if stat.S_ISLNK(mode):raise ValueError('Symlink path component refused: '+str(part))
  if part!=p or leaf_kind=='directory':
   if not stat.S_ISDIR(mode):raise ValueError('Not an ordinary directory: '+str(part))
  elif not stat.S_ISREG(mode):raise ValueError('Not an ordinary file: '+str(part))
 return p
def input_file(path):return ordinary_path(path,'file')
class FreshOutput:
 """Only a new directory with an existing, ordinary parent is accepted.
 Every file is exclusively created. Existing empty directories also fail.
 """
 def __init__(self,path):
  self.path=lexical_absolute(path)
  ordinary_path(self.path.parent,'directory')
  try:self.path.lstat()
  except FileNotFoundError:pass
  else:raise FileExistsError('Output must be a fresh nonexistent directory: '+str(self.path))
  self.path.mkdir(mode=0o700)
  st=self.path.lstat();self.identity=(st.st_dev,st.st_ino)
 def new_file(self,name):
  if not isinstance(name,str) or not name or '/' in name or '\\' in name or name in ['.','..'] or '\x00' in name:raise ValueError('Invalid output filename')
  ordinary_path(self.path,'directory')
  st=self.path.lstat()
  if (st.st_dev,st.st_ino)!=self.identity:raise ValueError('Output directory identity changed')
  target=self.path/name
  try:target.lstat()
  except FileNotFoundError:pass
  else:raise FileExistsError('Refusing existing file or link: '+str(target))
  return target.open('xb') # O_EXCL: no overwrite, including a raced-in final symlink.
 def png(self,image,name):
  with self.new_file(name) as f:image.save(f,format='PNG',optimize=True)
 def json(self,value,name):
  with self.new_file(name) as f:f.write((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(65536),b''):h.update(b)
 return h.hexdigest()
def digest(a):return hashlib.sha256(a.tobytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=P/'runtime');ap.add_argument('--project-root',type=Path);args=ap.parse_args();out=lexical_absolute(args.out)
 ordinary_path(P,'directory')
 project=args.project_root
 if project is None:
  project=next((p for p in [P,*P.parents] if (p/'assets/original/manifest.json').is_file() and (p/'data/maps/A13.json').is_file()),None)
 if project is None:raise SystemExit('A complete Project checkout is required. Place under Project/art_source or pass --project-root PATH_TO_Project.')
 project=ordinary_path(project,'directory')
 def resolve(ref):
  is_project=ref.startswith('project://');rel=ref[len('project://'):] if is_project else ref
  if not rel or '\\' in rel or '\x00' in rel or ':' in rel or any(s in ['','.','..'] for s in rel.split('/')):raise ValueError('Invalid relative dependency path')
  rp=Path(rel)
  if rp.is_absolute():raise ValueError('Absolute dependency path refused')
  return input_file((project if is_project else P)/rp)
 closure=json.loads(input_file(P/'SOURCE_CLOSURE.json').read_text())
 for rec in closure['files']:
  q=resolve(rec['path']);assert q.is_file() and q.stat().st_size==rec['bytes'] and sha(q)==rec['sha256'],str(q)
 r=json.loads(input_file(P/'REBUILD_RECIPE.json').read_text()); contract=json.loads((resolve(r['source_contract'])).read_text()); owners=contract['owners_original_draw_order']
 source=Image.open(resolve(r['source_image'])).convert('RGBA'); alpha=np.asarray(source)[:,:,3]; atlas=Image.open(resolve(r['source_atlas'])).convert('RGBA'); smap=json.loads((resolve(r['source_map'])).read_text()); manifest=json.loads((resolve(r['source_manifest'])).read_text())
 rebuilt_source=Image.new('RGBA',source.size); source_checks=[]
 assert len(owners)==8 and smap['id']=='A13' and smap['width']==smap['height']==100
 for owner in owners:
  f0=owner['frame'];x,y,w,h=f0['atlas_rect'];frame=atlas.crop((x,y,x+w,y+h));a=np.asarray(frame)
  assert digest(a)==f0['rgba_sha256'] and digest(a[:,:,3])==f0['alpha_sha256']
  assert smap['cells'][owner['stable_source_order']]==owner['source_cell']
  assert owner['stable_source_order']==owner['cell'][0]*100+owner['cell'][1]
  bx,by,ex,ey=owner['fixed_bounds_xyxy'];assert frame.size==(ex-bx,ey-by)
  rebuilt_source.alpha_composite(frame,(bx,by))
  source_checks.append({'key':owner['key'],'alpha_values':np.unique(a[:,:,3]).tolist(),'weak_alpha_pixels':int(((a[:,:,3]>0)&(a[:,:,3]<255)).sum()),'native_opaque_pixels':int((a[:,:,3]>0).sum()),'native_alpha_sha256':digest(a[:,:,3]),'source_cell_exact':True})
 assert np.array_equal(np.asarray(rebuilt_source),np.asarray(source)),'Source atlas reconstruction mismatch'
 arrays={k:np.asarray(Image.open(resolve(v)).convert('RGB'),dtype=np.float32) for k,v in r['raw_paths'].items()}
 def sample(k,rx,ry,wrap=False):
  a=arrays[k];hh,ww=a.shape[:2];z=rx-.5;t=ry-.5;ix=np.floor(z).astype(int);iy=np.floor(t).astype(int);fx=z-ix;fy=t-iy
  if wrap:xx0=ix%ww;xx1=(ix+1)%ww;yy0=iy%hh;yy1=(iy+1)%hh
  else:
   assert ix.min()>=0 and (ix+1).max()<ww and iy.min()>=0 and (iy+1).max()<hh
   xx0=ix;xx1=ix+1;yy0=iy;yy1=iy+1
  return a[yy0,xx0]*(1-fx[:,None])*(1-fy[:,None])+a[yy0,xx1]*fx[:,None]*(1-fy[:,None])+a[yy1,xx0]*(1-fx[:,None])*fy[:,None]+a[yy1,xx1]*fx[:,None]*fy[:,None]
 scale=4;rt=math.sqrt(13);period=8*rt;f=3/rt
 yy,xx=np.indices((384*scale,256*scale),dtype=np.float32);xx=(xx+.5)/scale;yy=(yy+.5)/scale
 aa=np.repeat(np.repeat(alpha,scale,0),scale,1);active=aa>0;Q=yy+2*(xx-32)/3;S=(3*(xx-32)-2*(yy-20))/rt;rgb=np.zeros((*aa.shape,3),np.float32)
 for name,lo,hi in [('ridge',-999,198),('main',198,259),('eave',259,267),('M2',267,322),('M3',322,999)]:
  m=active&(Q>=lo)&(Q<hi);sx=xx[m];sy=yy[m];q=Q[m]
  if name in r['specs']:
   s=r['specs'][name];rgb[m]=sample(s['raw'],s['x0']+np.mod(S[m],period)*s['D'],s['y0']+(q-s['nominal_Q0'])*f*s['D'])
  else:
   a=arrays[name];u=np.mod((3*(sx-32)-2*sy)/832,1);v=np.mod((2*(sx-32)+3*sy-420)/832,1);rgb[m]=sample(name,u*a.shape[1],v*a.shape[0],True)
 body4=Image.fromarray(np.dstack([np.uint8(np.clip(np.rint(rgb),0,255)),aa]));body=body4.resize((512,768),Image.Resampling.BOX);ba=np.asarray(body)
 assert digest(ba)==r['accepted_D2_RGBA_sha256'],'Accepted D2 pixels changed'
 alpha2=np.repeat(np.repeat(alpha,2,0),2,1);assert np.array_equal(ba[:,:,3],alpha2)
 assert not ba[alpha2==0].any(),'Transparent RGB must remain zero'
 writer=FreshOutput(out)
 writer.png(body,'body-d2.png');writer.png(Image.fromarray(alpha),'source-alpha-native.png');writer.png(Image.fromarray(alpha2),'source-alpha-d2.png')
 owner_id=np.zeros(alpha2.shape,np.uint8);coverage=np.zeros(alpha2.shape,np.uint8);combined=Image.new('RGBA',body.size);records=[];slices=[];world=r['source_world_origin'];assetroot='res://assets/earth/environment/wall_2653_2660_anchor18_17_v1/'
 for oid,owner in enumerate(owners,1):
  x0,y0,x1,y1=owner['fixed_bounds_xyxy'];box=(x0*2,y0*2,x1*2,y1*2);piece=body.crop(box);pa=np.asarray(piece);srca=alpha[y0:y1,x0:x1];assert np.array_equal(pa[:,:,3],np.repeat(np.repeat(srca,2,0),2,1))
  name=f"owner-{owner['frame']['frame_index']}.png";writer.png(piece,name);combined.alpha_composite(piece,(x0*2,y0*2));opaque=pa[:,:,3]>0
  coverage[y0*2:y1*2,x0*2:x1*2]+=opaque;owner_id[y0*2:y1*2,x0*2:x1*2][opaque]=oid
  rec={k:owner[k] for k in ['key','cell','source_cell','flag','layer','sort_y','stable_source_order']};rec.update({'pack':'Map/Res/Wall','frame_index':owner['frame']['frame_index'],'runtime_kind':3,'owner_id':oid,'world_top_left':[world[0]+x0,world[1]+y0],'world_anchor':owner['anchor_world'],'texture':assetroot+name,'local_texture':name,'texture_size':list(piece.size),'texture_sha256':sha(out/name),'texture_RGBA_sha256':digest(pa),'scale':.5,'logical_bounds_xyxy':owner['world_bounds_xyxy'],'fixed_canvas_bounds_xyxy':owner['fixed_bounds_xyxy'],'source_frame':owner['frame'],'source_native_alpha_sha256':digest(srca),'D2_alpha_sha256':digest(pa[:,:,3]),'alpha_nonzero_count_D2':int(opaque.sum()),'weak_alpha_pixels_D2':int(((pa[:,:,3]>0)&(pa[:,:,3]<255)).sum()),'empty':False})
  records.append(rec);slices.append((np.array(box),pa))
 assert coverage.max()==1 and np.array_equal(coverage>0,alpha2>0)
 assert np.array_equal(np.asarray(combined),ba),'Eight-owner composition differs from body'
 writer.png(Image.fromarray(owner_id),'owner-id-d2.png')
 # CPU nearest sampling at varied fractional positions, including owner edges.
 rng=np.random.default_rng(1817);points=np.column_stack([rng.uniform(0,256,24000),rng.uniform(0,384,24000)])*2
 grid=np.floor(points).astype(int);master=ba[grid[:,1],grid[:,0]];sampled=np.zeros_like(master);claim=np.zeros(len(points),np.uint8)
 for box,pa in slices:
  m=(points[:,0]>=box[0])&(points[:,0]<box[2])&(points[:,1]>=box[1])&(points[:,1]<box[3]);local=np.floor(points[m]-box[:2]).astype(int);v=pa[local[:,1],local[:,0]];sampled[m]=v;claim[m]+=v[:,3]>0
 assert np.array_equal(sampled,master) and claim.max()<=1
 reg={'schema':r['schema'],'status':'owned CPU assets only; no engine validation or publication','map':'A13','anchor_cell':[18,17],'source_map_sha256':sha(resolve(r['source_map'])),'source_manifest_sha256':sha(resolve(r['source_manifest'])),'source_wall_atlas_sha256':sha(resolve(r['source_atlas'])),'source_index_sha256':sha(resolve(r['source_index'])),'density':2,'body':{'file':'body-d2.png','sha256':sha(out/'body-d2.png'),'RGBA_sha256':digest(ba),'size':[512,768],'world_top_left':world,'scale':.5},'owners':records,'source_support':{'native_alpha_values':np.unique(alpha).tolist(),'native_nonzero_pixels':int((alpha>0).sum()),'D2_nonzero_pixels':int((alpha2>0).sum()),'verbatim_native_repeat_D2':True},'filter_contract':r['filter_contract'],'atomic_group_activation':True,'frame_global_override_forbidden':True,'source_collision_cells_read_only':True,'neighbor_scope':r['neighbor_scope'],'art_acceptance':'bounded baked2D candidate; U tone modulation and absent exact lower-contact shade retained'}
 writer.json(reg,'registration.json')
 check={'offline_input_closure_files_verified':len(closure['files']),'generation_calls':0,'source_atlas_recomposite_equals_fixed_source':True,'source_owner_checks':source_checks,'accepted_D2_RGBA_exact':True,'accepted_D2_PNG_sha_equal':sha(out/'body-d2.png')==r['accepted_D2_PNG_sha256'],'eight_owner_recomposition_RGBA_exact':True,'max_owner_claims_per_pixel':int(coverage.max()),'nonzero_source_omissions':int(((alpha2>0)&(coverage==0)).sum()),'new_support_pixels':int(((alpha2==0)&(coverage>0)).sum()),'flag0_tail_native_pixels':sum(z['native_opaque_pixels'] for z,o in zip(source_checks,owners) if o['flag']==0),'weak_source_alpha_retained_without_threshold':True,'nearest_fractional_CPU_points_checked':len(points),'nearest_fractional_sample_differences':0,'engine_run':False,'production_linear_filter_not_tested':True,'environment':{'python':platform.python_version(),'numpy':np.__version__,'pillow':pillow_version}}
 writer.json(check,'CPU_ASSET_VALIDATION.json')
 print(json.dumps({'body_sha256':sha(out/'body-d2.png'),'owner_count':len(records),'runtime_bytes':sum(q.stat().st_size for q in out.iterdir() if q.is_file()),'validation':check},indent=2))
if __name__=='__main__':main()
