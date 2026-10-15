"""Approved AC fixed-mask composite; no production edits."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw
O=Path(__file__).parent;P=O.parents[1];A=O.parent;D=P/'diagnostics/art_source/earth-bamboo-b-right-fans-edit-v1';D.mkdir(parents=True,exist_ok=True)
c=json.loads((O/'contract_before_generation.json').read_text());V=A/'earth_bamboo_b_candidate_v2';base=Image.open(A/'earth_bamboo_b_upper_crown_edit_v1/composite_candidate.png').convert('RGBA');b=np.array(base);gen=Image.open(O/'generated_crop_raw.png').convert('RGBA');assert gen.width==gen.height,'NON-SQUARE: STOP, NO COMPOSITE';assert hashlib.sha256((A/'earth_bamboo_b_upper_crown_edit_v1/composite_candidate.png').read_bytes()).hexdigest()==c['base_raw_sha256'];assert hashlib.sha256((O/'final_composite_weight.png').read_bytes()).hexdigest()==c['mask_sha256']
# Predeclared crop mapping only, no alignment optimization. Resample premultiplied channels to avoid halos.
G=np.array(gen).astype(float)/255;G[:,:,:3]*=G[:,:,3:4];small=np.stack([np.array(Image.fromarray(G[:,:,i].astype('float32'),'F').resize((900,900),Image.Resampling.LANCZOS))for i in range(4)],axis=2);small=np.clip(small,0,1)
B=b.astype(float)/255;B[:,:,:3]*=B[:,:,3:4];patch=B.copy();x,y,r,bot=c['crop_xyxy'];patch[y:bot,x:r]=small;w=np.array(Image.open(O/'final_composite_weight.png')).astype(float)/255;out=B*(1-w[:,:,None])+patch*w[:,:,None];alpha=out[:,:,3:4];rgb=np.divide(out[:,:,:3],alpha,out=np.zeros_like(out[:,:,:3]),where=alpha>0);q=np.rint(np.clip(np.concatenate([rgb,alpha],axis=2),0,1)*255).astype('uint8');q[w==0]=b[w==0];im=Image.fromarray(q);im.save(O/'composite_candidate.png')
fixed=np.array(Image.open(A/'earth_bamboo_b_local_layers_plan_v1/fixed_guard_proposal.png'))>0;hold=np.array(Image.open(A/'earth_bamboo_b_local_layers_plan_v1/no_cut_hold_proposal.png'))>0;conn=np.array(Image.open(O/'connection_guards.png'))>0;outside=w==0
checks={'outside_final_mask_changed_pixels':int(np.any(q[outside]!=b[outside],axis=1).sum()),'fixed_guard_changed_pixels':int(np.any(q[fixed]!=b[fixed],axis=1).sum()),'hold_changed_pixels':int(np.any(q[hold]!=b[hold],axis=1).sum()),'connection_guard_changed_pixels':int(np.any(q[conn]!=b[conn],axis=1).sum())};assert all(z==0 for z in checks.values())
# Donor changes inside immutable regions quantify why raw generator output is not accepted directly.
sm=np.array(gen.resize((900,900),Image.Resampling.LANCZOS));localfixed=(fixed|hold|conn)[y:bot,x:r];donor_diff=int(np.any(sm[localfixed]!=b[y:bot,x:r][localfixed],axis=1).sum())
# Metrics use frozen V2 scale/translation, no refit.
m=json.loads((V/'measurements.json').read_text());den=m['density'];t=m['raw_from_source_translation'];src=Image.open(A/'earth_bamboo_b_input_plan_v1/reference/source-body-index52-excluded.png').convert('RGBA');sa=np.array(src)[:,:,3];src_at_raw=src.transform(base.size,Image.Transform.AFFINE,(1/den,0,-t[0]/den,0,1/den,-t[1]/den),Image.Resampling.NEAREST);sr=np.array(src_at_raw)[:,:,3];a=q[:,:,3]
def bbox(ar,th=128):
 yy,xx=np.where(ar>=th);return [int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
edit=w>0;counts={'source_C_alpha128':int(((sr>=128)&edit).sum()),'base_C_alpha128':int(((b[:,:,3]>=128)&edit).sum()),'C_candidate_alpha128':int(((a>=128)&edit).sum())};bb=bbox(a);crown=(bb[1]-t[1])/den
# Full three-background review of composite, plus donor is retained separately.
for name,col in [('white',(245,245,245,255)),('gray',(80,84,82,255)),('dark',(18,23,22,255))]:
 bg=Image.new('RGBA',im.size,col);bg.alpha_composite(im);bg.convert('RGB').save(D/f'composite-on-{name}.png')
board=Image.new('RGB',(900*3,935),(78,81,80));dr=ImageDraw.Draw(board)
for n,(img,title)in enumerate([(src_at_raw.crop(c['crop_xyxy']),'SOURCE same-window geometry aid'),(base.crop(c['crop_xyxy']),'A base before C edit'),(im.crop(c['crop_xyxy']),'AC fixed-mask composite')]):
 board.paste(img,(n*900,35),img);dr.text((n*900+10,8),title,fill='white')
board.save(D/'source-A-AC-native-window.png')
joinboard=Image.new('RGB',(5*240,2*240+40),(78,81,80));dr=ImageDraw.Draw(joinboard)
for n,z in enumerate(c['connections']):
 cx,cy=z['raw_xy'];box=[cx-60,cy-60,cx+60,cy+60]
 for row,img in enumerate([base,im]):
  crop=img.crop(box).resize((240,240),Image.Resampling.NEAREST);joinboard.paste(crop,(n*240,40+row*240),crop)
 dr.text((n*240+5,8),z['id'],fill='white')
joinboard.save(D/'connections-before-after-2x-analysis.png')
# Existing six end neighborhoods all lie in fixedRGBA. No refit necessary.
ends=[]
for z in m['landmarks']:
 cx,cy=map(int,z['raw_xy']);r=20;eq=np.array_equal(q[cy-r:cy+r+1,cx-r:cx+r+1],b[cy-r:cy+r+1,cx-r:cx+r+1]);ends.append({'id':z['id'],'raw_xy':z['raw_xy'],'radius':r,'RGBA_equal':eq})
res={'status':'AC candidate; awaiting visual join judgement; no production','generated_native_size':gen.size,'frozen_crop_size':[900,900],'single_uniform_downsample':900/gen.width,'generator_crop_equivalent_density':den*gen.width/900,'composite_density_unchanged':den,'base_sha256':c['base_raw_sha256'],'frozen_mask_sha256':c['mask_sha256'],'generated_raw_sha256':hashlib.sha256((O/'generated_crop_raw.png').read_bytes()).hexdigest(),'composite_sha256':hashlib.sha256((O/'composite_candidate.png').read_bytes()).hexdigest(),'RGBA_checks':checks,'generator_donor_changed_protected_pixels_before_restore':donor_diff,'six_end_neighborhoods':ends,'composite_alpha128_bbox':bb,'crown_top_logical_relative_source0':crown,'right_over_source_logical':(bb[2]-t[0])/den-271,'C_region_counts':counts,'C_candidate_over_source_occupancy':counts['C_candidate_alpha128']/counts['source_C_alpha128'],'C_reduction_vs_base':1-counts['C_candidate_alpha128']/counts['base_C_alpha128'],'global_coverage_ratio':float((a>=128).sum()/den**2/(sa>0).sum()),'limits':'Counts not leaf counts; no sourcepixel hard alpha. B and A unchanged. Do not accept raw donor: guard restoration was required and junctions still require visual review.'}
(O/'measurements.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n');print(json.dumps(res,ensure_ascii=False,indent=2))

a_region=np.array(Image.open(A/'earth_bamboo_b_upper_crown_edit_v1/final_composite_weight.png'))>0
res['RGBA_checks']['previous_A_region_changed_pixels']=int(np.any(q[a_region]!=b[a_region],axis=1).sum());assert res['RGBA_checks']['previous_A_region_changed_pixels']==0
for name,col in [('white',(245,245,245,255)),('gray',(80,84,82,255)),('dark',(18,23,22,255))]:
 local=im.crop(c['crop_xyxy']);bg=Image.new('RGBA',local.size,col);bg.alpha_composite(local);bg.convert('RGB').save(D/f'C-window-on-{name}.png')
# Four complete groups at identical logical scale, not fitted again.
L=[-30,-35,330,370];z=2;size=(720,810);board=Image.new('RGB',(2880,845),(78,81,80));dr=ImageDraw.Draw(board);v2=Image.open(V/'raw.png')
for n,(img,dd,tt,title)in enumerate([(src,1,[0,0],'SOURCE body guide'),(v2,den,t,'V2'),(base,den,t,'A approved candidate'),(im,den,t,'AC candidate fixed mapping')]):
 tile=img.transform(size,Image.Transform.AFFINE,(dd/z,0,dd*L[0]+tt[0],0,dd/z,dd*L[1]+tt[1]),Image.Resampling.NEAREST if n==0 else Image.Resampling.BICUBIC);board.paste(tile,(n*720,35),tile);dr.text((n*720+8,8),title,fill='white')
board.save(D/'source-v2-A-AC-full-same-logical.png');(O/'measurements.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
# Endpoint guards are radius20 disks, not circumscribed squares. Report both honestly.
Y,X=np.ogrid[:b.shape[0],:b.shape[1]]
for item in res['six_end_neighborhoods']:
 cx,cy=item['raw_xy'];mask=(X-cx)**2+(Y-cy)**2<=20**2;item['circumscribed_square_RGBA_equal']=item.pop('RGBA_equal');item['protected_disk_RGBA_equal']=bool(np.array_equal(q[mask],b[mask]));item['protected_disk_changed_pixels']=int(np.any(q[mask]!=b[mask],axis=1).sum());assert item['protected_disk_changed_pixels']==0
res['crop_local_tri_backgrounds']=['C-window-on-white.png','C-window-on-gray.png','C-window-on-dark.png'];(O/'measurements.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
