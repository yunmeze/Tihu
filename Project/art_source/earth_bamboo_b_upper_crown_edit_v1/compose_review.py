"""Approved A-only fixed-mask composite; no production edits."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw
O=Path(__file__).parent;P=O.parents[1];A=O.parent;D=P/'diagnostics/art_source/earth-bamboo-b-upper-crown-edit-v1';D.mkdir(parents=True,exist_ok=True)
c=json.loads((O/'contract_before_generation.json').read_text());V=A/'earth_bamboo_b_candidate_v2';base=Image.open(V/'raw.png').convert('RGBA');b=np.array(base);gen=Image.open(O/'generated_crop_raw.png').convert('RGBA');assert gen.width==gen.height,'NON-SQUARE: STOP, NO COMPOSITE';assert hashlib.sha256((V/'raw.png').read_bytes()).hexdigest()==c['base_raw_sha256'];assert hashlib.sha256((O/'final_composite_weight.png').read_bytes()).hexdigest()==c['mask_sha256']
# Predeclared crop mapping only, no alignment optimization. Resample premultiplied channels to avoid halos.
G=np.array(gen).astype(float)/255;G[:,:,:3]*=G[:,:,3:4];small=np.stack([np.array(Image.fromarray(G[:,:,i].astype('float32'),'F').resize((760,760),Image.Resampling.LANCZOS))for i in range(4)],axis=2);small=np.clip(small,0,1)
B=b.astype(float)/255;B[:,:,:3]*=B[:,:,3:4];patch=B.copy();x,y,r,bot=c['crop_xyxy'];patch[y:bot,x:r]=small;w=np.array(Image.open(O/'final_composite_weight.png')).astype(float)/255;out=B*(1-w[:,:,None])+patch*w[:,:,None];alpha=out[:,:,3:4];rgb=np.divide(out[:,:,:3],alpha,out=np.zeros_like(out[:,:,:3]),where=alpha>0);q=np.rint(np.clip(np.concatenate([rgb,alpha],axis=2),0,1)*255).astype('uint8');q[w==0]=b[w==0];im=Image.fromarray(q);im.save(O/'composite_candidate.png')
fixed=np.array(Image.open(A/'earth_bamboo_b_local_layers_plan_v1/fixed_guard_proposal.png'))>0;hold=np.array(Image.open(A/'earth_bamboo_b_local_layers_plan_v1/no_cut_hold_proposal.png'))>0;conn=np.array(Image.open(O/'connection_guards.png'))>0;outside=w==0
checks={'outside_final_mask_changed_pixels':int(np.any(q[outside]!=b[outside],axis=1).sum()),'fixed_guard_changed_pixels':int(np.any(q[fixed]!=b[fixed],axis=1).sum()),'hold_changed_pixels':int(np.any(q[hold]!=b[hold],axis=1).sum()),'connection_guard_changed_pixels':int(np.any(q[conn]!=b[conn],axis=1).sum())};assert all(z==0 for z in checks.values())
# Donor changes inside immutable regions quantify why raw generator output is not accepted directly.
sm=np.array(gen.resize((760,760),Image.Resampling.LANCZOS));localfixed=(fixed|hold|conn)[y:bot,x:r];donor_diff=int(np.any(sm[localfixed]!=b[y:bot,x:r][localfixed],axis=1).sum())
# Metrics use frozen V2 scale/translation, no refit.
m=json.loads((V/'measurements.json').read_text());den=m['density'];t=m['raw_from_source_translation'];src=Image.open(A/'earth_bamboo_b_input_plan_v1/reference/source-body-index52-excluded.png').convert('RGBA');sa=np.array(src)[:,:,3];src_at_raw=src.transform(base.size,Image.Transform.AFFINE,(1/den,0,-t[0]/den,0,1/den,-t[1]/den),Image.Resampling.NEAREST);sr=np.array(src_at_raw)[:,:,3];a=q[:,:,3]
def bbox(ar,th=128):
 yy,xx=np.where(ar>=th);return [int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
edit=w>0;counts={'source_A_alpha128':int(((sr>=128)&edit).sum()),'v2_A_alpha128':int(((b[:,:,3]>=128)&edit).sum()),'A_candidate_alpha128':int(((a>=128)&edit).sum())};bb=bbox(a);crown=(bb[1]-t[1])/den
# Full three-background review of composite, plus donor is retained separately.
for name,col in [('white',(245,245,245,255)),('gray',(80,84,82,255)),('dark',(18,23,22,255))]:
 bg=Image.new('RGBA',im.size,col);bg.alpha_composite(im);bg.convert('RGB').save(D/f'composite-on-{name}.png')
board=Image.new('RGB',(760*3,795),(78,81,80));dr=ImageDraw.Draw(board)
for n,(img,title)in enumerate([(src_at_raw.crop(c['crop_xyxy']),'SOURCE same-window geometry aid'),(base.crop(c['crop_xyxy']),'V2 before A edit'),(im.crop(c['crop_xyxy']),'A-only fixed-mask composite')]):
 board.paste(img,(n*760,35),img);dr.text((n*760+10,8),title,fill='white')
board.save(D/'source-v2-A-native-window.png')
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
res={'status':'A-only candidate; awaiting visual join judgement; no production','generated_native_size':gen.size,'frozen_crop_size':[760,760],'single_uniform_downsample':760/gen.width,'generator_crop_equivalent_density':den*gen.width/760,'composite_density_unchanged':den,'base_sha256':c['base_raw_sha256'],'frozen_mask_sha256':c['mask_sha256'],'generated_raw_sha256':hashlib.sha256((O/'generated_crop_raw.png').read_bytes()).hexdigest(),'composite_sha256':hashlib.sha256((O/'composite_candidate.png').read_bytes()).hexdigest(),'RGBA_checks':checks,'generator_donor_changed_protected_pixels_before_restore':donor_diff,'six_end_neighborhoods':ends,'composite_alpha128_bbox':bb,'crown_top_logical_relative_source0':crown,'right_over_source_logical':(bb[2]-t[0])/den-271,'A_region_counts':counts,'A_candidate_over_source_occupancy':counts['A_candidate_alpha128']/counts['source_A_alpha128'],'A_reduction_vs_v2':1-counts['A_candidate_alpha128']/counts['v2_A_alpha128'],'global_coverage_ratio':float((a>=128).sum()/den**2/(sa>0).sum()),'limits':'Counts not leaf counts; no sourcepixel hard alpha. B/C unchanged. Do not accept raw donor: guard restoration was required and junctions still require visual review.'}
(O/'measurements.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n');print(json.dumps(res,ensure_ascii=False,indent=2))
