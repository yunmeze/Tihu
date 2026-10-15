from pathlib import Path
import json,hashlib
from PIL import Image
import numpy as np
O=Path(__file__).resolve().parent;P=O.parents[1];D=P/'diagnostics/art_source/earth_upright_tree_candidate_v1';D.mkdir(parents=True,exist_ok=True);I=P/'art_source/earth_vegetation_input_plan_v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
im=Image.open(O/'raw.png').convert('RGBA');a=np.asarray(im);alpha=a[:,:,3];out={'status':'one approved generation; root-aligned diagnostic proposal only; no runtime/slices or second call','raw_size':list(im.size),'raw_sha256':sha(O/'raw.png'),'alpha':{}}
for t in[0,16,127,250]:
 y,x=np.where(alpha>t);out['alpha'][str(t)]={'bbox_xyxy':[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)],'count':int(len(x)),'edge_top_bottom_left_right':[int(np.count_nonzero(v>t))for v in[alpha[0],alpha[-1],alpha[:,0],alpha[:,-1]]]}
for n,c in[('gray',(128,128,128,255)),('dark',(22,27,35,255)),('light',(240,240,240,255))]:
 b=Image.new('RGBA',im.size,c);b.alpha_composite(im);b.convert('RGB').save(D/(n+'.png'))
density=4.5;root=[560,1329];origin=[2964-root[0]/density,1646-root[1]/density];left=[origin[0]-528,origin[1]-320];view=[2825,1340,310,325]
src=Image.open(I/'upright_tree_61_51_source_native.png').convert('RGBA')
for den in[1,2]:
 size=(view[2]*den,view[3]*den);new=im.transform(size,Image.Transform.AFFINE,(density/den,0,(view[0]-origin[0])*density,0,density/den,(view[1]-origin[1])*density),Image.Resampling.BICUBIC)
 old=Image.new('RGBA',size);old.alpha_composite(src.resize((281*den,298*den),Image.Resampling.NEAREST),((2839-view[0])*den,(1352-view[1])*den))
 for name,q in[('source',old),('root_aligned',new)]:
  b=Image.new('RGBA',size,(128,128,128,255));b.alpha_composite(q);b.convert('RGB').save(D/f'{name}_gray_{den}x.png')
 sa=np.asarray(old)[:,:,3]>0;na=np.asarray(new)[:,:,3]>127;rgb=np.full((size[1],size[0],3),55,np.uint8);rgb[sa]=[0,200,220];rgb[na]=[230,60,170];rgb[sa&na]=[200,200,200];Image.fromarray(rgb).save(D/f'alpha_overlap_{den}x.png')
out['registration_study']={'density':density,'scale':1/density,'manual_raw_root_xy':root,'candidate_root_uncertainty_raw_px':9,'source_local_root':[125,294],'source_manual_uncertainty_logical_px':4,'bottom_world_root':[2964,1646],'bottom_world_top_left':origin,'left_world_root':[2436,1326],'left_world_top_left':left,'world_translation_left_to_bottom':[528,320],'rotation':0,'shear':0,'status':'proposal for source-shape/root overlay review only; no per-owner mapping or route acceptance','raw_logical_canvas_size':[im.width/density,im.height/density],'alpha127_body_logical_size':[1077/density,1326/density],'alpha127_body_height_density_ratio_source298':1326/298,'root_is_manual_wood_band_not_bbox':True}
out['review']={'positive':['Slender upright trunk, vertically separated side branches; different silhouette family from first tree','Actual detailed new bark/leaves, minimum2 density comfortably met','No obvious separate ground shadow, planter or background','Three standard alpha composites show complete visible tips/root and no conspicuous independent matte ring'],'remaining':['Leaf masses denser than old source and warm-yellow highlights remain strong','Large transparent padding request not delivered; lowalpha touches top/left/bottom, mainalpha127 topmargin11px','Root/branch shape and both placements must be judged on overlays and later native routes; no exact shadow/body source segmentation asserted'],'no_second_call':True}
out['inputs']=json.loads((P/'art_source/earth_upright_tree_input_plan_v1/INPUT_PLAN.json').read_text())['input_images']
prior=P/'art_source/earth_vegetation_stage_archive_v1/MINIMAL_SHA256.json';d=json.loads(prior.read_text())
for f in d['files']:assert sha(P/f['path'])==f['sha256']
out['frozen41_unchanged']=True
(O/'measurements.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
files=['README.md','prompt.txt','raw.png','measure_candidate.py','measurements.json'];(O/'ARCHIVE_SHA256.json').write_text(json.dumps({'files':[{'path':n,'sha256':sha(O/n),'bytes':(O/n).stat().st_size}for n in files]},indent=2)+'\n');print('RAW_SHA',sha(O/'raw.png'));print('BOTTOM_ORIGIN',origin,'LEFT_ORIGIN',left)
