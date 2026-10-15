from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[1];D=R/'diagnostics/earth_e_45_gap_donor_proposal_v1';D.mkdir(parents=True,exist_ok=True);S=R/'art_source/earth_e_upper45_context_edit_v1';A=R/'art_source/earth_e_upper45_context_edit_plan_v1'
im=Image.open(S/'45-HD4-CONTEXT-EDIT-RESEARCH.png').convert('RGBA');a=np.array(im);rawmapped=Image.open(S/'mapped-whole-image-UNMASKED.png').convert('RGBA');b=np.array(rawmapped);u=np.array(Image.open(A/'fixed-union-edit-HD4-mask.png'))>0;pr=np.array(Image.open(A/'protected-core-hand-shins-HD4-mask.png'))>0
regions={'waist':[(138,193),(181,193),(181,202),(138,202)],'knee':[(178,272),(199,272),(199,277),(191,281),(181,286),(164,286),(164,280),(176,277)]}
record={};overview=Image.new('RGBA',(512,512),(128,128,128,255));overview.alpha_composite(im);ov=np.array(overview)
for name,poly in regions.items():
 gate=Image.new('L',(512,512));ImageDraw.Draw(gate).polygon(poly,fill=255);g=np.array(gate)>0
 # actual low-opacity gap candidates, bounded by visible edge tracing (authoring envelope)
 m=g&(a[:,:,3]<128);Image.fromarray((m*255).astype('uint8')).save(P/f'{name}-GAP-PROPOSED-mask.png')
 # no edits: display same-location donor for waist, one rigid offset for knee
 dx,dy=(0,0) if name=='waist' else (5,45)
 donor=Image.new('RGBA',(512,512));donor.alpha_composite(rawmapped,(dx,dy));da=np.array(donor)
 coords=np.argwhere(m);cols={str(int(x)):np.where(m[:,x])[0].tolist() for x in np.where(m.any(axis=0))[0]}
 runs=[]
 for x in np.where(m.any(axis=0))[0]:
  ys=np.where(m[:,x])[0];runs.extend([len(q) for q in np.split(ys,np.where(np.diff(ys)>1)[0]+1)])
 bbox=Image.fromarray((m*255).astype('uint8')).getbbox();record[name]={'manual_envelope':poly,'actual_mask_rule':'inside manual envelope and current alpha<128, not global color threshold','HD4_pixels':int(m.sum()),'equivalent_logical_area':float(m.sum()/16),'maximum_vertical_contiguous_thickness_HD4':max(runs),'maximum_vertical_thickness_logical':max(runs)/4,'bbox_HD4':bbox,'inside_original_union':int((m&u).sum()),'outside_original_union':int((m&~u).sum()),'intersects_original_protected_alpha_gt0':int((m&pr).sum()),'changes_current_alpha_ge128':0,'donor':'earth_e_upper45_context_edit_v1/mapped-whole-image-UNMASKED.png','donor_translation_HD4':[dx,dy],'donor_rotation':0,'donor_scale_change':0,'donor_source_bbox_HD4':[bbox[0]-dx,bbox[1]-dy,bbox[2]-dx,bbox[3]-dy],'donor_alpha_range':[int(da[:,:,3][m].min()),int(da[:,:,3][m].max())],'donor_alpha_ge250_pixels':int((da[:,:,3][m]>=250).sum()),'pixel_coordinates_xy':[[int(x),int(y)] for y,x in coords]}
 ov[m,:3]=[255,0,200]
 crop=(130,184,190,212) if name=='waist' else (154,262,210,298)
 board=Image.new('RGBA',(1260,420),(128,128,128,255))
 for i,z in enumerate([im,Image.fromarray(ov),donor]):board.alpha_composite(z.crop(crop).resize((420,280),Image.Resampling.NEAREST),(420*i,0))
 ImageDraw.Draw(board).text((5,300),f'{name}: current | exact proposed low-alpha mask | donor at target (NO COMPOSITE)',fill='white');board.save(D/f'{name}-current-mask-donor.png')
Image.fromarray(ov).save(D/'full-current-gap-locations.png')
for nm,c in [('gray',(128,128,128,255)),('light',(235,235,235,255)),('dark',(20,22,26,255))]:
 bg=Image.new('RGBA',(512,512),c);bg.alpha_composite(im);bg.save(D/f'current-full-{nm}.png')
j={'status':'analysis proposal only, no patch applied','alpha_threshold':128,'geometry_uncertainty':'manual envelope traces current visible gap; filling the whole envelope is a clothing authoring choice, not anatomical proof','current_sha256':hashlib.sha256((S/'45-HD4-CONTEXT-EDIT-RESEARCH.png').read_bytes()).hexdigest(),'same_raw_sha256':hashlib.sha256((S/'raw.png').read_bytes()).hexdigest(),'records':record};(P/'PROPOSAL.json').write_text(json.dumps(j,indent=2)+'\n');print({n:{k:v for k,v in z.items() if k!='pixel_coordinates_xy'} for n,z in record.items()})
# Separate narrow underlap proposal: original protected-layer alpha remains unedited.
prot=np.array(Image.open(A/'protected-core-arm-shins.png'));wm=np.array(Image.open(P/'waist-GAP-PROPOSED-mask.png'))>0
n=wm&(prot[:,:,3]>0)&(prot[:,:,3]<128)&(b[:,:,3]>=250)
Image.fromarray((n*255).astype('uint8')).save(P/'waist-UNDERLAP-PROPOSED-mask.png')
j['waist_underlap']={'pixels':int(n.sum()),'original_layer_alpha_range':[int(prot[:,:,3][n].min()),int(prot[:,:,3][n].max())],'donor_alpha_range':[int(b[:,:,3][n].min()),int(b[:,:,3][n].max())],'outside_prior_union':int((n&~u).sum()),'solid_alpha_ge128_intersection':0,'method':'original protected layer source-over same-location black cloth underlap; keep layer RGBA, honestly record final composite change; proposal only','coords_xy':[[int(x),int(y)] for y,x in zip(*np.where(n))]}
(P/'PROPOSAL.json').write_text(json.dumps(j,indent=2)+'\n')
