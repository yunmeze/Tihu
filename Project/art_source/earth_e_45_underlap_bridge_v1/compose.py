from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,shutil
P=Path(__file__).resolve().parent;R=P.parents[1];S=R/'art_source/earth_e_upper45_context_edit_v1';A=R/'art_source/earth_e_upper45_context_edit_plan_v1';M=R/'art_source/earth_e_45_gap_donor_proposal_v1';D=R/'diagnostics/earth_e_45_underlap_bridge_v1';D.mkdir(parents=True,exist_ok=True)
old=Image.open(S/'45-HD4-CONTEXT-EDIT-RESEARCH.png').convert('RGBA');donor=Image.open(S/'mapped-whole-image-UNMASKED.png').convert('RGBA');protected=Image.open(A/'protected-core-arm-shins.png').convert('RGBA');a=np.array(old);pr=np.array(protected);w=np.array(Image.open(M/'waist-UNDERLAP-PROPOSED-mask.png'))>0;k=np.array(Image.open(M/'knee-GAP-PROPOSED-mask.png'))>0;assert w.sum()==89 and k.sum()==178 and not np.any(w&k)
def under(base,don,m):
 # Source-over original original protected texture over new donor at approved pixels only.
 lay=don.copy();lay.alpha_composite(protected);c=np.array(lay);b=np.array(base);b[m]=c[m];return Image.fromarray(b)
waist=under(old,donor,w);shift=Image.new('RGBA',(512,512));shift.alpha_composite(donor,(5,45));both=under(waist,shift,k)
waist.save(P/'45-HD4-WAIST-ONLY-RESEARCH.png');both.save(P/'45-HD4-WAIST-KNEE-BRIDGE-RESEARCH.png')
for nm,im in [('WAIST-ONLY',waist),('WAIST-KNEE-BRIDGE',both)]:im.resize((128,128),Image.Resampling.LANCZOS).save(P/f'45-128-{nm}-RESEARCH.png')
for nm,mask in [('waist89',w),('knee178',k)]:Image.fromarray((mask*255).astype('uint8')).save(P/f'{nm}-actual-mask.png')
src=Image.open(A/'input-source45-full128.png').convert('RGBA')
for nm,col in [('gray',(128,128,128,255)),('light',(235,235,235,255)),('dark',(20,22,26,255))]:
 for z in [1,2]:
  board=Image.new('RGBA',(128*z*4,128*z),col)
  for i,im in enumerate([src,old,waist,both]):
   lo=im.resize((128,128),Image.Resampling.NEAREST if i==0 else Image.Resampling.LANCZOS);board.alpha_composite(lo.resize((128*z,128*z),Image.Resampling.NEAREST),(128*z*i,0))
  board.save(D/f'source-before-waist-bridge-{z}x-{nm}.png')
 for name,box in [('waist',(130,184,190,212)),('knee',(154,262,210,298))]:
  board=Image.new('RGBA',(1260,400),col)
  for i,im in enumerate([old,waist,both]):board.alpha_composite(im.crop(box).resize((420,280),Image.Resampling.NEAREST),(i*420,0))
  board.save(D/f'{name}-before-waist-bridge-{nm}.png')
b=np.array(waist);c=np.array(both);dw=np.any(b!=a,axis=2);dk=np.any(c!=b,axis=2);solid=pr[:,:,3]>=128
assert not np.any(dw&~w) and not np.any(dk&~k) and not np.any(np.any(c!=a,axis=2)&solid)
provenance=np.zeros_like(a);provenance[w]=[0,220,255,255];provenance[k]=[255,0,220,255];Image.fromarray(provenance).save(D/'changed-pixel-provenance.png')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
j={'status':'two approved independent research steps, not pose/material passed','waist_final_composite_changed_pixels':int(dw.sum()),'knee_incremental_final_composite_changed_pixels':int(dk.sum()),'outside_waist_mask_changes':int((dw&~w).sum()),'outside_knee_mask_changes':int((dk&~k).sum()),'original_solid_protected_alpha_ge128_final_changes':int((np.any(c!=a,axis=2)&solid).sum()),'original_protected_texture_layer_RGBA_changed':0,'final_original_semtransparent_protected_pixels_changed':int((np.any(c!=a,axis=2)&(pr[:,:,3]>0)&(pr[:,:,3]<128)).sum()),'new_donor_mapping':'existing mapped raw; waist shift0,0; knee shift+5,+45 HD4, rotation0, no scale change','inputs':[{'path':str(p.relative_to(R)),'sha256':sha(p)} for p in [S/'45-HD4-CONTEXT-EDIT-RESEARCH.png',S/'mapped-whole-image-UNMASKED.png',A/'protected-core-arm-shins.png',M/'waist-UNDERLAP-PROPOSED-mask.png',M/'knee-GAP-PROPOSED-mask.png']]}
(P/'PROOF.json').write_text(json.dumps(j,indent=2)+'\n');print(j)
