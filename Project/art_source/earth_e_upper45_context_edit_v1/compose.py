from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,shutil
P=Path(__file__).resolve().parent;R=P.parents[1];A=R/'art_source/earth_e_upper45_context_edit_plan_v1';D=R/'diagnostics/earth_e_upper45_context_edit_v1';D.mkdir(parents=True,exist_ok=True)
old=Image.open(A/'input-complete45-context.png').convert('RGBA');raw=Image.open(P/'raw.png').convert('RGBA');s=512/raw.width
mapped=raw.transform((512,512),Image.Transform.AFFINE,(1/s,0,0,0,1/s,0),resample=Image.Resampling.BICUBIC);mapped.save(P/'mapped-whole-image-UNMASKED.png')
mask=np.array(Image.open(A/'fixed-union-edit-HD4-mask.png'))>0;protected=np.array(Image.open(A/'protected-core-hand-shins-HD4-mask.png'))>0
assert mask.sum()==5743 and not np.any(mask&protected)
a=np.array(old);b=np.array(mapped);n=a.copy();n[mask]=b[mask];out=Image.fromarray(n);out.save(P/'45-HD4-CONTEXT-EDIT-RESEARCH.png');out.resize((128,128),Image.Resampling.LANCZOS).save(P/'45-128-CONTEXT-EDIT-RESEARCH.png');shutil.copyfile(A/'fixed-union-edit-HD4-mask.png',P/'actual-fixed-union-mask.png')
src=Image.open(A/'input-source45-full128.png').convert('RGBA')
for nm,c in [('gray',(128,128,128,255)),('light',(235,235,235,255)),('dark',(20,22,26,255))]:
 for k in [1,2,4]:
  board=Image.new('RGBA',(128*k*3,128*k),c)
  for i,x in enumerate([src,old,out]):
   small=x.resize((128,128),Image.Resampling.LANCZOS) if i else x.resize((128,128),Image.Resampling.NEAREST)
   board.alpha_composite(small.resize((128*k,128*k),Image.Resampling.NEAREST),(128*k*i,0))
  board.save(D/f'source-context-new-{k}x-{nm}.png')
 board=Image.new('RGBA',(1200,520),c)
 for i,x in enumerate([old,mapped,out]):board.alpha_composite(x.crop((104,176,224,306)).resize((400,434),Image.Resampling.NEAREST),(400*i,0))
 board.save(D/f'waist-knees-context-raw-new-{nm}.png')
diff=np.any(n!=a,axis=2);v=np.zeros_like(n);v[diff]=[255,0,200,255];Image.fromarray(v).save(D/'actual-RGBA-diff.png')
j={'raw_sha256':hashlib.sha256((P/'raw.png').read_bytes()).hexdigest(),'raw_size':raw.size,'single_global_scale':s,'mapped_height':raw.height*s,'translation':[0,0],'union_pixels':int(mask.sum()),'outside_union_RGBA_changes':int((diff&~mask).sum()),'protected_RGBA_changes':int((diff&protected).sum()),'changed_inside_union':int((diff&mask).sum()),'raw_mapped_outside_union_changed_RGBA_discarded':int((np.any(b!=a,axis=2)&~mask).sum()),'raw_mapped_protected_changed_RGBA_discarded':int((np.any(b!=a,axis=2)&protected).sum()),'bbox_original_alpha128':Image.fromarray((a[:,:,3]>=128).astype('uint8')*255).getbbox(),'bbox_mapped_alpha128':Image.fromarray((b[:,:,3]>=128).astype('uint8')*255).getbbox(),'no_extra_fit':True,'raw_alpha0_pixels':int((np.array(raw)[:,:,3]==0).sum())}
(P/'PROOF.json').write_text(json.dumps(j,indent=2)+'\n');print(j)
