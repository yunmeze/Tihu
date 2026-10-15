from PIL import Image,ImageDraw
from pathlib import Path
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[1];D=R/'diagnostics/earth_e_parts_density_review_v1';D.mkdir(exist_ok=True,parents=True)
src=R/'art_source/earth_e_layered_parts_v1/raw.png';old=R/'art_source/earth_hero_e_49_control_v2/raw.png';im=Image.open(src).convert('RGBA');a=np.array(im)
# Conservative rectangular outside-body envelopes, manually chosen after viewing raw.
# NOT final silhouette matte. Close fringe retained for later manual review.
rects=[[115,8,393,440],[690,73,838,505],[1205,84,1404,496],[61,522,476,996],[601,527,963,990]]
m=Image.new('L',im.size,0);md=ImageDraw.Draw(m)
for r in rects:md.rectangle(r,fill=255)
m.save(D/'background-only-proposed-keep-mask.png');aa=np.array(m);removed=(aa==0)&(a[:,:,3]>0)
counts={'removed_nonzero_alpha':int(removed.sum()),'removed_alpha_ge128':int((removed&(a[:,:,3]>=128)).sum()),'max_removed_alpha':int(a[:,:,3][removed].max()),'note':'Conservative manually chosen outer rectangles; close brown fringe retained. Not an applied production mask.'}
masked=im.copy();masked.putalpha(Image.fromarray(np.where(aa>0,a[:,:,3],0).astype('uint8')))
for name,c in [('gray',(128,128,128,255)),('light',(235,235,235,255)),('dark',(20,22,26,255))]:
 b=Image.new('RGBA',(3072,1024),c);b.alpha_composite(im,(0,0));b.alpha_composite(masked,(1536,0));b.save(D/f'background-proposal-before-after-{name}.png')
b=Image.new('RGBA',im.size,(90,90,90,255));b.alpha_composite(im);dr=ImageDraw.Draw(b)
for r in rects:dr.rectangle(r,outline=(0,255,255),width=3)
for r in [[730,115,755,150],[763,414,803,459],[1235,120,1266,155],[1324,414,1367,454]]:dr.rectangle(r,outline=(255,100,240),width=3)
b.save(D/'density-regions-and-background-envelopes.png')
o=Image.open(old).convert('RGBA');b=Image.new('RGBA',o.size,(100,100,100,255));b.alpha_composite(o);dr=ImageDraw.Draw(b)
for r,c,label in [([330,440,480,495],'cyan','waist interface: estimate'),([337,492,417,571],'red','old hand + missing trouser'),([220,572,520,835],'lime','lower visible geometry')]:dr.rectangle(r,outline=c,width=3);dr.text((r[0],r[1]-12),label,fill=c)
b.crop((200,400,540,850)).resize((680,900)).save(D/'old49-reuse-interface-risks.png')
info={'status':'density_and_mask_proposal_only_not_passed','inputs':[{'path':str(x.relative_to(R)),'sha256':hashlib.sha256(x.read_bytes()).hexdigest()} for x in [src,old]],'core_density':{'logical_per_raw_pixel':33/387,'anchor_y_raw':[29,416],'anchor_y_logical':[16,49],'waist_interface_is_authored':True},'arms_family':{'proposed_fixed_logical_per_raw_pixel':0.079,'exploratory_interval':[0.069,0.089],'raw_attachment_and_hand_regions_local':{'46':[[218,115,243,150],[251,414,291,459]],'49':[[211,120,242,155],[300,414,343,454]]},'source_attachment_region':[33,29,40,35],'source_hand_centers':{'46':[37,56],'49':[43,56]},'rule':'one shared scalar for BOTH arm assets and all future uses; never per phase. Regions are surface/production interfaces not skeleton.'},'old49_lower':{'retain_existing_scale':0.1028549998260168,'retain_existing_translation':[-1.4220149316246022,-0.25108997251065546],'toe_delta':[17.7939149699,-4.4227649925],'source_toe_delta':[17,-6],'old_hand_occluded_region_raw':[337,492,417,571],'missing_region_is_not_recoverable_by_mask':True},'background_proposal':{'rectangles_global':rects,**counts}}
(P/'EVALUATION.json').write_text(json.dumps(info,indent=2)+'\n');print(json.dumps(counts))
# Proposed local cloth completion only; no synthesis called.
poly=[(333,476),(359,475),(389,483),(414,503),(421,541),(414,570),(401,578),(370,575),(348,560),(333,536)]
pm=Image.new('L',o.size,0);ImageDraw.Draw(pm).polygon(poly,fill=255);pm.save(D/'old49-PROPOSED-cloth-patch-mask.png')
ob=Image.new('RGBA',o.size,(100,100,100,255));ob.alpha_composite(o);od=ImageDraw.Draw(ob);od.line(poly+[poly[0]],fill=(255,60,220),width=3);od.rectangle((300,425,500,600),outline=(0,255,255),width=2);ob.crop((280,410,530,625)).resize((1000,860)).save(D/'old49-PROPOSED-cloth-patch-region.png')
o.crop((300,425,500,600)).save(D/'old49-patch-context-RAW-CROP.png')
info['cloth_patch_pending_approval']={'context_crop_raw':[300,425,500,600],'replacement_polygon_raw':poly,'fixed_logical_per_raw_pixel':0.1028549998260168,'mask_feather_max_raw_px':2,'feather_inside_only':True,'protected':'all pixels outside mask, especially entire legs below y578; no regenerated leg/boot used','uncertainty':'under-glove trouser surface and hidden outer contour must be newly authored; not recovered original anatomy','approval':'parent review of exact region required before one imagegen call'}
(P/'EVALUATION.json').write_text(json.dumps(info,indent=2)+'\n')
