from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent;V=P/'diagnostics/art_source/earth_grass_pair_candidate_v1';V.mkdir(parents=True,exist_ok=True)
im=Image.open(D/'raw.png').convert('RGBA');a=np.array(im);records=[];density=21
# One common density, translations fitted to visible support midpoints, no per-object stretch.
for name,region,pts,srcmid,world in [('A',(0,0,1300,724),[(445,618),(885,618)],(30.5,24),(2608,965)),('B',(1300,0,2172,724),[(1676,600),(1894,600)],(27.5,22),(2613,992))]:
 x0,y0,x1,y1=region;ys,xs=np.where(a[y0:y1,x0:x1,3]>127);bbox=[int(xs.min()+x0),int(ys.min()+y0),int(xs.max()+x0+1),int(ys.max()+y0+1)]
 mid=np.mean(pts,axis=0);origin=(mid-np.array(srcmid)*density).tolist();rec={'id':name,'raw_region_xyxy':region,'alpha_gt127_bbox':bbox,'body_size':[bbox[2]-bbox[0],bbox[3]-bbox[1]],'common_density':density,'uniform_scale':1/density,'raw_support_read_points':pts,'manual_uncertainty_raw_px':30,'source_support_midpoint':srcmid,'raw_origin_for_source_local_zero':origin,'world_top_left_of_full_raw':[world[i]-origin[i]/density for i in range(2)],'registered_support_span':(pts[1][0]-pts[0][0])/density,'registered_main_bbox_source_local':[(bbox[i]-origin[i%2])/density for i in range(4)],'physical_root':None};records.append(rec)
for n,c in [('gray',(120,120,120)),('dark',(24,29,35)),('light',(235,232,224))]:
 bg=Image.new('RGBA',im.size,c+(255,));bg.alpha_composite(im);bg.save(V/(n+'.png'))
for z in [1,2]:
 board=Image.new('RGBA',(160*z,110*z),(120,120,120,255));overlay=Image.new('RGBA',(160*z,55*z),(100,100,100,255))
 for rec,n,xy in zip(records,['grass239_54_30','grass241_54_31'],[(8,8),(90,8)]):
  src=Image.open(P/('art_source/earth_vegetation_input_plan_v1/'+n+'_source_native.png')).convert('RGBA');s=np.array(src);s[np.all(s==[8,0,0,255],axis=2)]=0;src=Image.fromarray(s)
  board.alpha_composite(src.resize((src.width*z,src.height*z),Image.Resampling.NEAREST),(xy[0]*z,xy[1]*z))
  # Full raw affine sampling limited to the selected sheet region, untouched raw kept separately.
  layer=Image.new('RGBA',im.size);layer.paste(im.crop(rec['raw_region_xyxy']),rec['raw_region_xyxy'][:2]);ox,oy=rec['raw_origin_for_source_local_zero'];gen=layer.transform((72*z,42*z),Image.Transform.AFFINE,(density/z,0,ox,0,density/z,oy),Image.Resampling.BICUBIC)
  board.alpha_composite(gen,(xy[0]*z,(xy[1]+55)*z))
  ga=np.array(gen);sa=np.zeros_like(ga);ss=np.array(src.resize((src.width*z,src.height*z),Image.Resampling.NEAREST));sa[:ss.shape[0],:ss.shape[1]]=ss
  color=np.zeros_like(ga);color[:,:,0]=sa[:,:,3];color[:,:,1]=ga[:,:,3];color[:,:,2]=ga[:,:,3];color[:,:,3]=np.maximum(sa[:,:,3],ga[:,:,3]);overlay.alpha_composite(Image.fromarray(color),(xy[0]*z,xy[1]*z))
 board.save(V/f'source_and_registered_{z}x.png');overlay.save(V/f'alpha_overlap_{z}x.png')
report={'raw_sha256':hashlib.sha256((D/'raw.png').read_bytes()).hexdigest(),'raw_size':im.size,'status':'single authorized generation; review only; no owner split or runtime','generation_input_plan':'earth_grass_pair_input_plan_v1','registration':'Provisional common density21 based on both body dimensions; independently translated by leaf-support midpoint. No per-body scaling/warp. Manual support points uncertain30rawpx; physical roots unknown.','records':records,'review':'Actual gray/dark/light composites required; preview RGB fringe alone is not a defect. A denser than old sparse source; both contain seedhead-like tips. B support span10.38logical vs original13, within combined uncertain band but needs parent acceptance. A support span20.95 vs19. No shadow/root/ground added. No automatic repair or second generation.'}
(D/'measurement.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
