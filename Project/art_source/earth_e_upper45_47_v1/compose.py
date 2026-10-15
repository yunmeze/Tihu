from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[1];D=R/'diagnostics/earth_e_upper45_47_v1';S=R/'art_source/earth_e_four_phase_rigid_study_v1'
raw=Image.open(P/'raw.png').convert('RGBA');w,h=raw.size;s=76/w;cw=w//2
board=Image.new('RGBA',(1536,1024),(128,128,128,255));rec={}
for row,f in enumerate([45,47]):
 cell=raw.crop((row*cw,0,(row+1)*cw,h));im=cell.transform((512,512),Image.Transform.AFFINE,(1/(4*s),0,-20/s,0,1/(4*s),-44/s),resample=Image.Resampling.BICUBIC)
 im.save(P/f'{f}-mapped-UNMASKED.png');a=np.array(im);mask=np.array(Image.open(P/f'{f}-fixed-support-HD4-mask.png'))>0;outside=int(((a[:,:,3]>0)&~mask).sum());a[~mask,3]=0;piece=Image.fromarray(a);piece.save(P/f'{f}-mapped-FIXED-MASK.png')
 out=Image.new('RGBA',(512,512));out.alpha_composite(piece)
 for side in (['left','right'] if f==45 else ['right','left']):out.alpha_composite(Image.open(S/f'{f}-{side}-rigid-HD4.png'))
 if f==45:
  for name in ['back','front']:out.alpha_composite(Image.open(R/f'diagnostics/earth_e_49_cloth_patch_v1/layer49-core-{name}.png'),(4,0))
 else:out.alpha_composite(Image.open(S/'47-using-arm49-CORE-ONLY-RESEARCH.png'))
 out.save(P/f'{f}-ASSEMBLY-FAILED-RESEARCH.png')
 src=Image.open(R/f'diagnostics/earth_e_source_shadow_index_audit_v1/{f}-index18-excluded-NOT-SEMANTICALLY-CERTIFIED.png').resize((512,512),Image.Resampling.NEAREST)
 for col,z in enumerate([src,im,out]):board.alpha_composite(z,(col*512,row*512))
 ImageDraw.Draw(board).text((row*0+5,row*512+5),f'{f} source | unmasked registered pants | frozen-mask incomplete assembly',fill='white')
 rec[f]={'raw_cell':[row*cw,0,(row+1)*cw,h],'mapped_nonzero_pixels_outside_frozen_support':outside,'unmasked_bbox':im.getbbox(),'mapped_fixed_mask_bbox':piece.getbbox(),'original_pants_used':False}
board.save(D/'source-rawmapping-assembly-gray.png')
for nm,c in [('light',(235,235,235,255)),('dark',(20,22,26,255))]:
 b=Image.new('RGBA',(1024,512),c)
 for i,f in enumerate([45,47]):b.alpha_composite(Image.open(P/f'{f}-ASSEMBLY-FAILED-RESEARCH.png'),(i*512,0))
 b.save(D/f'failed-assemblies-{nm}.png')
arr=np.array(raw)
j={'status':'FAILED output pose/layout; no corrective fit or retry','raw_sha256':hashlib.sha256((P/'raw.png').read_bytes()).hexdigest(),'raw_size':[w,h],'one_uniform_density_raw_to_logical':s,'target_origin':[20,44],'actual_logical_canvas_per_cell':[cw*s,h*s],'requested_logical_canvas_per_cell':[38,31],'alpha_zero_pixels':int((arr[:,:,3]==0).sum()),'alpha_max':int(arr[:,:,3].max()),'records':rec,'all_core_and_shin_modules_referenced_unchanged':True,'no_old_upper_pants_in_assembly':True}
(P/'RESULT.json').write_text(json.dumps(j,indent=2)+'\n');print(j)
