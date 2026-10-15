from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt
O=Path(__file__).resolve().parent;P=O.parents[1];D=P/'diagnostics/art_source/earth_round_shrub_registration_v1';D.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
R=P/'art_source/earth_round_shrub_candidate_v1/raw.png';rawim=Image.open(R).convert('RGBA');raw=np.asarray(rawim);h,w=raw.shape[:2]
C=P/'art_source/earth_vegetation_input_plan_v1/source_contract.json';g=next(g for g in json.loads(C.read_text())['groups'] if g['id']=='round_shrub_57_38');owners=g['owners_in_draw_order'];assert [o['frame_index']for o in owners]==[143,144,145,146]
origin=[2695.,1141.];scale=1/11;yy,xx=np.indices((h,w));wx=origin[0]+(xx+.5)*scale;wy=origin[1]+(yy+.5)*scale;best=np.full((h,w),np.inf);labels=np.zeros((h,w),np.uint8)
for i,o in enumerate(owners,1):
 x,y,bw,bh=o['world_rect'];dx=np.maximum(np.maximum(x-wx,0),wx-x-bw);dy=np.maximum(np.maximum(y-wy,0),wy-y-bh);d=dx*dx+dy*dy;take=d<best;labels[take]=i;best[take]=d[take]
assert np.all(labels>0);Image.fromarray(labels).save(O/'owner-labels.png');records=[];assembly=np.zeros_like(raw);coverage=np.zeros((h,w),np.uint8)
for i,o in enumerate(owners,1):
 mask=labels==i;a=np.zeros_like(raw);a[mask]=raw[mask];assembly[mask]=a[mask];coverage[mask]+=1;fn=O/f'owners/owner-{o["frame_index"]}.png';Image.fromarray(a).save(fn)
 e={k:o[k]for k in['pack','key','cell','source_cell','flag','layer','sort_y','stable_source_order','frame_index']};e.update({'texture':'res://'+str(fn.relative_to(P)),'texture_size':[w,h],'sha256':sha(fn),'texture_sha256':sha(fn),'scale':scale,'world_top_left':origin,'raw_rect':[0,0,w,h],'empty':False,'visible_pixel_count':int(np.count_nonzero(raw[:,:,3][mask])),'nonzero_rgba_pixel_count':int(np.count_nonzero(np.any(raw[mask]!=0,axis=1))),'assigned_raw_pixel_count':int(mask.sum())});records.append(e)
assert np.array_equal(raw,assembly)and np.all(coverage==1)
readback=np.zeros_like(raw)
for i,e in enumerate(records,1):
 a=np.asarray(Image.open(P/e['texture'][6:]));mask=labels==i;readback[mask]=a[mask]
assert np.array_equal(raw,readback)
mp=P/'data/maps/A13.json';m=json.loads(mp.read_text())
for o in records:
 x,y=o['cell'];assert m['cells'][x*m['height']+y]==o['source_cell']
alpha=raw[:,:,3];far=(alpha>0)&(alpha<=16)&(distance_transform_edt(alpha<=16)>44)
reg={'schema':'earth-round-shrub-candidate-registration-v1','status':'source-overlay/fullcanvas partition for parent review; not runtime installed','approval_scope':'Only original143–146center57,38. No ground shadow or root claim, no collision/order changes.','raw_texture':'res://'+str(R.relative_to(P)),'raw_sha256':sha(R),'source_contract_sha256':sha(C),'source_map_sha256':sha(mp),'density':11,'whole_shrub_registration':{'scale':scale,'world_top_left':origin,'rotation':0,'shear':0,'physical_root':None,'registration_basis':'Source lower green leaf support band; candidate manual rawband440,1060..1040,1120 maps to source-local40,94.36..94.55,99.82 with origin y=-2logical. No bbox-bottom/root anchor.','manual_candidate_band_uncertainty_raw_px':15,'source_band_approximate':True},'suppress_source_keys':[o['key']for o in records],'owners':records,'partition':{'method':'Nearest Euclidean original cropped owner rectangle, ties original draw order, all raw pixels allocated once; all4use identical fullcanvas size/world origin','owner_labels':'res://'+str((O/'owner-labels.png').relative_to(P)),'owner_labels_sha256':sha(O/'owner-labels.png'),'all_rgba_bytes_equal':True},'shadow':'None; suppress original4 atomically including original baked shadow','low_alpha_far_pixels':{'criterion':'alpha1..16 and >44rawpixels(4logical) fromalpha>16; retained','count':int(far.sum()),'max_alpha':int(alpha[far].max())if np.any(far)else 0}}
(O/'registration.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n')
# independent source/new native logical and true2x gray, plus original-alpha overlap.
src=Image.open(P/'art_source/earth_vegetation_input_plan_v1/round_shrub_57_38_source_native.png').convert('RGBA');view=[2685,1131,144,125]
for den in[1,2]:
 size=(view[2]*den,view[3]*den);new=rawim.transform(size,Image.Transform.AFFINE,(11/den,0,(view[0]-origin[0])*11,0,11/den,(view[1]-origin[1])*11),Image.Resampling.BICUBIC)
 old=Image.new('RGBA',size);old.alpha_composite(src.resize((124*den,105*den),Image.Resampling.NEAREST),((2695-view[0])*den,(1143-view[1])*den))
 for name,im in[('source',old),('candidate',new)]:
  bg=Image.new('RGBA',size,(128,128,128,255));bg.alpha_composite(im);bg.convert('RGB').save(D/f'{name}_gray_{den}x.png')
 sa=np.array(old)[:,:,3]>0;na=np.array(new)[:,:,3]>127;rgb=np.full((size[1],size[0],3),55,np.uint8);rgb[sa]=[0,200,220];rgb[na]=[230,60,170];rgb[sa&na]=[200,200,200];Image.fromarray(rgb).save(D/f'alpha_overlap_{den}x.png')
validation={'raw_pixel_count':w*h,'owner_count':4,'coverage_min':int(coverage.min()),'coverage_max':int(coverage.max()),'written_reassembly_all_rgba_equal':True,'raw_rgba_sha256':hashlib.sha256(raw.tobytes()).hexdigest(),'readback_rgba_sha256':hashlib.sha256(readback.tobytes()).hexdigest(),'original_source_identities_match':True,'no_physical_root_asserted':True,'no_runtime_route_or_gpu_claim':True,'alpha127_world_bbox':[origin[0]+7/11,origin[1]+15/11,origin[0]+1359/11,origin[1]+1130/11],'low_alpha_far':reg['low_alpha_far_pixels']}
(O/'validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n')
files=['README.md','build_registration.py','registration.json','validation.json','owner-labels.png']+[f'owners/owner-{n}.png'for n in range(143,147)];(O/'ARCHIVE_SHA256.json').write_text(json.dumps({'files':[{'path':n,'sha256':sha(O/n),'bytes':(O/n).stat().st_size}for n in files]},indent=2)+'\n');print('REG_SHA',sha(O/'registration.json'));print('RGBA_EQUAL',w*h)
