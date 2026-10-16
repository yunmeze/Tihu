from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[1];E=R/'art_source/earth_e_47_48_context_edits_v1';A=R/'art_source/earth_e_47_48_similarity_audit_v1';D=R/'diagnostics'/P.name;D.mkdir(parents=True,exist_ok=True)
load=lambda p:Image.open(p).convert('RGBA');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reg=json.loads((A/'MEASUREMENTS.json').read_text());allproof={}
for phase in [47,48]:
 d=E/str(phase);outdir=P/str(phase);outdir.mkdir(exist_ok=True);old=load(d/'input-context.png');raw=load(d/'raw.png');prot=load(d/'protected-original-layers.png');m=np.array(Image.open(d/'fixed-union-mask.png'))>0;v=reg[str(phase)];s=v['uniform_scale_source_to_mapped_raw'];tx,ty=v['translation_source_to_mapped_raw'];q=512/raw.width
 affine=(s/q,0,tx/q,0,s/q,ty/q)
 mapped=raw.transform((512,512),Image.Transform.AFFINE,affine,resample=Image.Resampling.BICUBIC);mapped.save(outdir/'registered-whole-raw-TECHNICAL-ONLY.png');b=np.array(mapped);donor=b.copy();donor[~m,3]=0;Image.fromarray(donor).save(outdir/'sampled-pants-union-donor.png');Image.fromarray((m*255).astype('uint8')).save(outdir/'unchanged-fixed-union-mask.png')
 composite=Image.alpha_composite(Image.fromarray(donor),prot);a=np.array(old);pr=np.array(prot);result=a.copy();result[m]=np.array(composite)[m];im=Image.fromarray(result);im.save(outdir/f'{phase}-HD4-DENSITY-REGISTERED-PANTS-RESEARCH.png');im.resize((128,128),Image.Resampling.LANCZOS).save(outdir/f'{phase}-128-DENSITY-REGISTERED-PANTS-RESEARCH.png')
 diff=np.any(result!=a,axis=2);solid=pr[:,:,3]>=128;assert not np.any(diff&~m);assert not np.any(diff&solid)
 ys,xs=np.where(m);rx=affine[0]*xs+affine[2];ry=affine[4]*ys+affine[5]
 # Conservative raw bicubic-tap footprint; includes ±2 around mapped output pixel centers.
 footprint=np.zeros((raw.height,raw.width),bool)
 for ox in [-2,-1,0,1,2]:
  for oy in [-2,-1,0,1,2]:
   xx=np.floor(rx).astype(int)+ox;yy=np.floor(ry).astype(int)+oy;valid=(xx>=0)&(xx<raw.width)&(yy>=0)&(yy<raw.height);footprint[yy[valid],xx[valid]]=True
 Image.fromarray((footprint*255).astype('uint8')).save(outdir/'raw-sampling-conservative-footprint-NOT-EDIT-MASK.png')
 hashes={n:sha(d/n) for n in ['raw.png','input-context.png','input-source.png','fixed-union-mask.png','protected-original-layers.png','BEFORE_CONTRACT.json']}
 proof={'phase':phase,'status':'new research registration only, previous fixed-contract failure preserved; no local fit or production','logical_canvas':[128,128],'root_logical':[16,64],'HD4_root':[64,256],'input_sha256':hashes,'frozen_measurements_sha256':sha(A/'MEASUREMENTS.json'),'frozen_context_to_previous_mapped_raw':{'scale':s,'translation':[tx,ty]},'new_raw_to_logical_density':q/s/4,'new_raw_to_HD4_scale':q/s,'new_raw_to_HD4_translation':[-tx/s,-ty/s],'direct_single_resample_output_to_raw_affine':affine,'rotation_deg':0,'union_pixels':int(m.sum()),'union_mask_sha_matches':sha(outdir/'unchanged-fixed-union-mask.png')==sha(d/'fixed-union-mask.png'),'changed_final_RGBA':int(diff.sum()),'changed_outside_union':int((diff&~m).sum()),'protected_alpha128_or_greater_final_changes':int((diff&solid).sum()),'protected_source_texture_changes':0,'protected_semi_final_changes':int((diff&(pr[:,:,3]>0)&~solid).sum()),'registered_donor_alpha0_inside_union':int(((b[:,:,3]==0)&m).sum()),'registered_donor_alpha_partial_inside_union':int(((b[:,:,3]>0)&(b[:,:,3]<255)&m).sum()),'raw_sample_center_bbox':[float(rx.min()),float(ry.min()),float(rx.max()),float(ry.max())],'raw_footprint_note':'conservative ±2 raw pixels around output->raw sample coordinates; not an edit mask','unadopted_generated_head_core_arms_shins_boots':True,'retained_holdout_rows':v['rows']}
 (outdir/'PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');allproof[str(phase)]=proof
 source=load(d/'input-source.png');failed=load(d/f'{phase}-HD4-FIXED-CONTRACT-RESEARCH.png')
 for bg,col in [('gray',(128,128,128,255)),('light',(235,235,235,255)),('dark',(20,22,26,255))]:
  for z in [1,2]:
   board=Image.new('RGBA',(128*z*4,128*z),col)
   for i,x in enumerate([source,old,failed,im]):
    lo=x.resize((128,128),Image.Resampling.NEAREST if i==0 else Image.Resampling.LANCZOS);board.alpha_composite(lo.resize((128*z,128*z),Image.Resampling.NEAREST),(128*z*i,0))
   board.save(D/f'{phase}-source-context-oldfailed-registered-{z}x-{bg}.png')
  box=(96,172,224,304);board=Image.new('RGBA',(512*3,528),col)
  for i,x in enumerate([old,mapped,im]):board.alpha_composite(x.crop(box).resize((512,528),Image.Resampling.NEAREST),(i*512,0))
  board.save(D/f'{phase}-joints-context-donor-registered-{bg}.png')
 # Mark the fixed adoption domain over whole registered image, not an enlarged mask.
 marked=Image.new('RGBA',(512,512),(128,128,128,255));marked.alpha_composite(mapped);arr=np.array(marked);edge=m&~(np.roll(m,1,0)&np.roll(m,-1,0)&np.roll(m,1,1)&np.roll(m,-1,1));arr[edge,:3]=(255,50,180);Image.fromarray(arr).save(D/f'{phase}-frozen-union-on-registered-raw.png')
 for n,h in hashes.items():assert sha(d/n)==h
print(json.dumps({k:{n:v[n] for n in ['new_raw_to_logical_density','union_pixels','changed_final_RGBA','changed_outside_union','protected_alpha128_or_greater_final_changes','protected_semi_final_changes','registered_donor_alpha0_inside_union']} for k,v in allproof.items()},indent=2))
