#!/usr/bin/env python3
"""Read-only CPU measurement; output only diagnostics; no body or runtime edits."""
from pathlib import Path
import hashlib,json,importlib.util
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[2];O=P/'diagnostics/earth-upright-shadow-study';O.mkdir(exist_ok=True)
def load(p):return json.loads((P/p).read_text())
def sha(p):return hashlib.sha256((P/p).read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('g',P/'tools/earth/build_flat_shadow_gate.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
a=np.array(Image.open(P/'assets/earth/environment/upright_tree_v1/raw.png').convert('RGBA'))[:,:,3];yy,xx=np.nonzero(a>0);density=4.5;root=np.array([560,1329]);ref=root/density;M=np.array([[1,-1.2],[0,-.55]]);T=np.array([1.2*ref[1],1.55*ref[1]])
lo=(np.stack((xx,yy),1)-.5)/density;hi=(np.stack((xx,yy),1)+1.5)/density
corners=np.stack((lo,np.stack((hi[:,0],lo[:,1]),1),hi,np.stack((lo[:,0],hi[:,1]),1)),1)@M.T+T
base=np.concatenate((corners.min(1)-1.8,corners.max(1)+1.8),1);base=np.concatenate((base,[[ref[0]-1.8,ref[1]-1.8,ref[0]+1.8,ref[1]+1.8]]))
origin=np.array([2200,960]);size=[2600,1800];sample_origin=np.array([2496,960]);sample_size=[1536,1024]
receiver=load('assets/earth/shadows/receiver_v2/manifest.json');forbidden=np.array(Image.open(P/receiver['files']['forbidden']['path'][6:]))>0
others={name:np.array(Image.open(P/c['envelope']['path'][6:]))>0 for name,c in receiver['casters'].items()}
measure=load('art_source/earth_shadow_next_stage_v1/measurements.json');fang=next(r for r in measure['records'] if r['name']=='fangzhang') if any(r['name']=='fangzhang' for r in measure['records'])else None
rows=[];globalmasks=[];inputs={}
for instance in ['left_50_41','bottom_61_51']:
 path='assets/earth/environment/upright_tree_v1/registration_'+instance+'.json';r=load(path);inputs[path]=sha(path);reg=r['whole_tree_registration'];world=np.array(reg['world_top_left']);rect=base+np.tile(world,2);env=g.raster(rect,origin,size);inside=g.raster(rect,sample_origin,sample_size);globalmasks.append(env)
 bounds=np.r_[rect[:,:2].min(0),rect[:,2:].max(0)];allinside=bool((bounds[:2]>=sample_origin).all()and(bounds[2:]<=sample_origin+[768,512]).all())
 row={'instance':instance,'density':density,'raw_size_wh':[a.shape[1],a.shape[0]],'alpha_positive_texels':len(xx),'world_origin':world.tolist(),'root_raw':root.tolist(),'root_logical':ref.tolist(),'root_world':(world+ref).tolist(),'root_uncertainty_raw':9,'source_root_uncertainty_logical':4,'cast':[1.2,.55],'slope_hypothesis':0,'opacity':.25,'blur_logical':.8,'blur_raw':3.6,'projection_matrix':M.tolist(),'projection_translation_logical':T.tolist(),'determinant':float(np.linalg.det(M)),'full_conservative_world_bounds_xyxy':bounds.tolist(),'full_envelope_cells_density2':int(env.sum()),'envelope_cells_inside_current_sample':int(inside.sum()),'envelope_cells_outside_current_sample':int(env.sum()-inside.sum()),'full_envelope_passes_current_sample':allinside,'current_receiver_forbidden_overlap_inside_sample':int((inside&forbidden).sum()),'overlap_existing_envelope_cells_inside_sample':{k:int((inside&v).sum())for k,v in others.items()},'source_keys':r['suppress_source_keys'],'owners':[{k:o[k]for k in ['key','cell','source_cell','layer','sort_y','stable_source_order','frame_index']}for o in r['owners']]};rows.append(row)
 im=np.full((size[1],size[0],3),240,np.uint8);im[env]=[80,115,155];x=int((2496-origin[0])*2);im[:1024,x:x+1536][forbidden]=[190,70,65];d=ImageDraw.Draw(Image.fromarray(im));image=Image.fromarray(im);d=ImageDraw.Draw(image);d.rectangle((x,0,x+1535,1023),outline=(0,0,0),width=3);rp=(world+ref-origin)*2;d.ellipse((rp[0]-6,rp[1]-6,rp[0]+6,rp[1]+6),fill=(230,150,0));d.text((10,10),instance+' full envelope BLUE; current receiver boundary BLACK; forbidden RED; fixed wood root ORANGE',fill=(0,0,0));image.save(O/(instance+'-envelope.png'))
for p in ['assets/earth/environment/upright_tree_v1/raw.png','assets/earth/shadows/receiver_v2/manifest.json','data/maps/A13.json','scripts/earth/upright_candidate.gd','tools/earth/build_flat_shadow_gate.py']:inputs[p]=sha(p)
report={'schema':'earth-upright-shadow-readonly-cpu-v1','method':'All alpha>0 texels expanded half a raw texel for bilinear support; density4.5 exact; transformed per-texel AABBs expanded logical1.8; fixed wood root included. Raster cell density2. No clipping used for eligibility.','instances':rows,'two_upright_full_envelope_overlap_cells':int((globalmasks[0]&globalmasks[1]).sum()),'root_neighborhood_alpha_5x5':a[1327:1332,558:563].tolist(),'input_sha256':inputs}
(O/'measurements.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({r['instance']:{k:v for k,v in r.items()if k not in ['owners','source_keys']}for r in rows},indent=2))
