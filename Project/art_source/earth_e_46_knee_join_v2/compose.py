from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,shutil
P=Path(__file__).resolve().parent;R=P.parents[1];S=R/'art_source/earth_e_46_knee_join_v1';A=R/'art_source/earth_e_46_knee_gap_mask_addendum_v1';D=R/'diagnostics/earth_e_46_knee_join_v2';D.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=Image.open(S/'46-HD4-RIGID-JOIN-RESEARCH.png').convert('RGBA');baseline=Image.open(S/'rigid46-BEFORE-JOIN.png').convert('RGBA');mask=Image.open(A/'ADDITIONAL-GAP-ONLY-PROPOSED-mask.png').convert('L');m=np.array(mask)>0;a=np.array(old);b=np.array(baseline)
assert m.sum()==49 and not np.any(m&(b[:,:,3]>=128))
prior=np.array(Image.open(S/'actual-gap-only-replacement-mask.png'))>0;assert not np.any(m&prior)
donor=Image.new('RGBA',(512,512));donor.paste(Image.open(S/'patch-mapped-HD4-crop.png'),(128,244));d=np.array(donor);d[~m,3]=0;under=Image.fromarray(d);under.alpha_composite(old);n=np.array(under);n[~m]=a[~m];out=Image.fromarray(n)
out.save(P/'46-HD4-RIGID-JOIN-RESEARCH.png');out.resize((128,128),Image.Resampling.LANCZOS).save(P/'46-128-RIGID-JOIN-RESEARCH.png');mask.save(P/'additional-49-pixels-mask.png');Image.fromarray(((prior|m)*255).astype('uint8')).save(P/'complete-407-pixels-mask.png')
src=Image.open(R/'diagnostics/earth_e_source_shadow_index_audit_v1/46-index18-excluded-NOT-SEMANTICALLY-CERTIFIED.png').convert('RGBA');static=Image.open(R/'art_source/earth_e_46_49_static_research_v1/46-HD4-STATIC-RESEARCH.png').convert('RGBA')
for name,c in [('gray',(128,128,128,255)),('light',(235,235,235,255)),('dark',(20,22,26,255))]:
 for k in (1,2):
  board=Image.new('RGBA',(384*k,128*k),c)
  for i,x in enumerate([src,static.resize((128,128),Image.Resampling.LANCZOS),out.resize((128,128),Image.Resampling.LANCZOS)]):board.alpha_composite(x.resize((128*k,128*k),Image.Resampling.NEAREST),(128*k*i,0))
  board.save(D/f'source-old-corrected-{k}x-{name}.png')
 board=Image.new('RGBA',(1440,420),c)
 for i,x in enumerate([old,donor,out]):board.alpha_composite(x.crop((128,244,188,300)).resize((480,448),Image.Resampling.NEAREST),(480*i,0))
 board.save(D/f'seam-failed-donor-corrected-{name}.png')
diff=np.any(n!=a,axis=2);assert not np.any(diff&~m);assert not np.any(np.any(n!=b,axis=2)&(b[:,:,3]>=128))
v=np.zeros_like(n);v[diff]=[255,0,220,255];Image.fromarray(v).save(D/'additional-pixel-diff.png')
proof={'status':'49-pixel authorized same-donor completion; research only','additional_mask_pixels':int(m.sum()),'complete_mask_pixels':int((m|prior).sum()),'changed_RGBA_pixels_from_failed':int(diff.sum()),'outside_additional_mask_RGBA_changes':int((diff&~m).sum()),'original_alpha_ge128_RGBA_changes':int((np.any(n!=b,axis=2)&(b[:,:,3]>=128)).sum()),'protected_core_arm_and_feet_unchanged_from_failed':True,'no_new_generation_or_resampling_of_donor':True,'mapping':'same 60/1298 uniform mapping, placement HD4(128,244)','coordinate_list_source':str(A/'PROPOSAL.json'),'inputs':[{ 'path':str(p.relative_to(R)), 'sha256':sha(p)} for p in [S/'raw.png',S/'patch-mapped-HD4-crop.png',S/'46-HD4-RIGID-JOIN-RESEARCH.png',S/'rigid46-BEFORE-JOIN.png',S/'actual-gap-only-replacement-mask.png',A/'ADDITIONAL-GAP-ONLY-PROPOSED-mask.png',A/'PROPOSAL.json']]}
(P/'PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');print(proof)
