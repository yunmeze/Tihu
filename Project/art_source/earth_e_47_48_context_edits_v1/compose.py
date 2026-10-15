from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[1];D=R/'diagnostics/earth_e_47_48_context_edits_v1';D.mkdir(parents=True,exist_ok=True)
for f in [47,48]:
 d=P/str(f);old=Image.open(d/'input-context.png').convert('RGBA');raw=Image.open(d/'raw.png').convert('RGBA');pr=Image.open(d/'protected-original-layers.png').convert('RGBA');s=512/raw.width
 mapped=raw.transform((512,512),Image.Transform.AFFINE,(1/s,0,0,0,1/s,0),resample=Image.Resampling.BICUBIC);mapped.save(d/'mapped-UNMASKED.png');m=np.array(Image.open(d/'fixed-union-mask.png'))>0
 a=np.array(old);p=np.array(pr);b=np.array(mapped);over=mapped.copy();over.alpha_composite(pr);c=np.array(over);out=a.copy();out[m]=c[m];im=Image.fromarray(out);im.save(d/f'{f}-HD4-FIXED-CONTRACT-RESEARCH.png');im.resize((128,128),Image.Resampling.LANCZOS).save(d/f'{f}-128-FIXED-CONTRACT-RESEARCH.png')
 diff=np.any(out!=a,axis=2);solid=p[:,:,3]>=128;assert not np.any(diff&~m) and not np.any(diff&solid)
 bbox=lambda x:Image.fromarray(((x[:,:,3]>=128)*255).astype('uint8')).getbbox()
 j={'phase':f,'raw_sha256':hashlib.sha256((d/'raw.png').read_bytes()).hexdigest(),'raw_size':raw.size,'one_canvas_scale':s,'no_content_fit':True,'original_bbox_alpha128':bbox(a),'mapped_bbox_alpha128':bbox(b),'union_pixels':int(m.sum()),'changed_final_RGBA':int(diff.sum()),'outside_union_changed_final_RGBA':int((diff&~m).sum()),'original_solid_protected_final_RGBA_changed':int((diff&solid).sum()),'original_texture_layer_RGBA_changed':0,'semi_protected_final_RGBA_changed':int((diff&(p[:,:,3]>0)&~solid).sum()),'mapped_raw_outside_union_changed_discarded':int((np.any(b!=a,axis=2)&~m).sum()),'raw_alpha_zero':int((np.array(raw)[:,:,3]==0).sum())};(d/'PROOF.json').write_text(json.dumps(j,indent=2)+'\n');print(j)
 src=Image.open(d/'input-source.png').convert('RGBA')
 for nm,col in [('gray',(128,128,128,255)),('light',(235,235,235,255)),('dark',(20,22,26,255))]:
  for z in [1,2]:
   board=Image.new('RGBA',(128*z*4,128*z),col)
   for i,x in enumerate([src,old,mapped,im]):
    lo=x.resize((128,128),Image.Resampling.NEAREST if i==0 else Image.Resampling.LANCZOS);board.alpha_composite(lo.resize((128*z,128*z),Image.Resampling.NEAREST),(128*z*i,0))
   board.save(D/f'{f}-source-context-raw-composite-{z}x-{nm}.png')
  board=Image.new('RGBA',(1260,480),col)
  for i,x in enumerate([old,mapped,im]):board.alpha_composite(x.crop((100,172,228,304)).resize((420,433),Image.Resampling.NEAREST),(i*420,0))
  board.save(D/f'{f}-joints-{nm}.png')
