from pathlib import Path
import json,hashlib
from PIL import Image
import numpy as np
O=Path(__file__).resolve().parent;P=O.parents[1];D=P/'diagnostics/art_source/earth_round_shrub_candidate_v1';D.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
im=Image.open(O/'raw.png').convert('RGBA');a=np.asarray(im);alpha=a[:,:,3];out={'status':'one authorized full shrub generation; raw review only; no registration/runtime or second call','raw_size':list(im.size),'raw_sha256':sha(O/'raw.png'),'alpha':{}}
for t in[0,16,127,250]:
 y,x=np.where(alpha>t);out['alpha'][str(t)]={'bbox_xyxy':[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)],'count':int(len(x)),'edge_top_bottom_left_right':[int(np.count_nonzero(v>t))for v in[alpha[0],alpha[-1],alpha[:,0],alpha[:,-1]]]}
for n,c in[('gray',(128,128,128,255)),('dark',(22,27,35,255)),('light',(240,240,240,255))]:
 b=Image.new('RGBA',im.size,c);b.alpha_composite(im);b.convert('RGB').save(D/(n+'.png'))
out['density']={'source_logical_extent':[124,105],'alpha127_body_size':[1352,1115],'body_pixels_per_source_extent':[1352/124,1115/105],'minimum_true_density2_met_in_raw':True,'provisional_uniform_density11_logical_canvas':[im.width/11,im.height/11],'no_registered_transform':True,'note':'Actual output1363x1154, not requested1024square. Native new leaf detail; not source upscaling. Final GPU density untested.'}
out['support_read']={'physical_root':None,'source_lower_foliage_band_local_xyxy':[40,94,95,100],'candidate_manual_visible_lower_foliage_read_zone_raw_xyxy':[440,1060,1040,1120],'manual_uncertainty_raw_px':15,'candidate_zone_if_uniform_density11':[40,1060/11,1040/11,1120/11],'caution':'Visible green leaf edge zone only. No wooden root is shown or proven, no exact ground plane or root anchor. This zone is an approximate manual inspection read, not an automatic silhouette registration.'}
out['visual_review']={'positive':['Low rounded bush, no trunk/root/planter/background or separate ground shadow','Natural green shaded foliage with warm upper-left leaf highlights','Three standard alpha-composited backgrounds show no conspicuous independent red/yellow matte fringe','Actual high-resolution leaf/twig detail'], 'remaining':['Highlights are strongly yellow-green; joint Earth palette review needed','Very narrow left/right margins: alpha>127 x7..1358. Low alpha touches left/right/bottom; requested wide transparent margin not delivered','Individual leaves are prominent in raw; native game-scale reading still needs checking','Source support band and new outline have not been accepted or partitioned into original4owners'],'no_second_call':True}
plan=P/'art_source/earth_round_shrub_input_plan_v1/INPUT_PLAN.json';out['input_plan_sha256']=sha(plan);out['inputs']=json.loads(plan.read_text())['input_images']
(O/'measurements.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
files=['README.md','prompt.txt','raw.png','measure_candidate.py','measurements.json'];(O/'ARCHIVE_SHA256.json').write_text(json.dumps({'diagnostics_excluded':True,'files':[{'path':n,'sha256':sha(O/n),'bytes':(O/n).stat().st_size}for n in files]},indent=2)+'\n');print('RAW_SHA',sha(O/'raw.png'))
