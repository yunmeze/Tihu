from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,shutil
from scipy.ndimage import distance_transform_edt
P=Path(__file__).resolve().parent;R=P.parents[1];C=P.parent/'earth_hero_s_idle_v1';D=R/'diagnostics/earth_hero_s_idle_edit_v1';D.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
old=Image.open(C/'raw-v1.png').convert('RGBA');new=Image.open(P/'raw-edit-v1.png').convert('RGBA');assert old.size==new.size==(2172,724)
req=json.loads((P/'request-v1.json').read_text());assert sha(C/'registration-v1.json')==req['frozen_original_registration_sha256']
shutil.copyfile(C/'registration-v1.json',P/'frozen-original-registration.json');reg=json.loads((P/'frozen-original-registration.json').read_text());s=reg['common_uniform_scale_raw_to_logical'];out=Image.new('RGBA',(2048,512));rows=[]
rois={'face_hair':[225,75,310,190],'Lhand':[130,320,180,415],'Rhand':[355,320,410,415],'Lboot':[150,500,275,690],'Rboot':[275,500,400,690]}
for i in range(4):
 o=old.crop((543*i,0,543*(i+1),724));n=new.crop((543*i,0,543*(i+1),724));aa=np.array(o);bb=np.array(n);tr=reg['records'][i]['translation_raw_scaled_to_logical'];tx,ty=tr;k=4*s
 tile=n.transform((512,512),Image.Transform.AFFINE,(1/k,0,-tx/s,0,1/k,-ty/s),Image.Resampling.BICUBIC);out.paste(tile,(512*i,0))
 masks=[aa[:,:,3]>=128,bb[:,:,3]>=128];stats={}
 for name,(x0,y0,x1,y1) in rois.items():
  om=masks[0][y0:y1,x0:x1];nm=masks[1][y0:y1,x0:x1];dist1=distance_transform_edt(~om)[nm];dist2=distance_transform_edt(~nm)[om];ys,xs=np.where(nm)
  stats[name]={'max_mask_to_mask_distance_raw':float(max(dist1.max(),dist2.max())),'p95_bidirectional_distance_raw':float(np.percentile(np.concatenate([dist1,dist2]),95)),'bbox_new_raw':[int(xs.min()+x0),int(ys.min()+y0),int(xs.max()+1+x0),int(ys.max()+1+y0)]}
 # old/new direct contours, no re-fit.
 landmarks=[]
 for ar in [aa,bb]:
  yy,xx=np.where(ar[:,:,3]>=128);y=int(yy.min());pts=[[float(np.where(ar[y,:,3]>=128)[0].mean()),y]]
  for x0,x1 in [(150,275),(275,400)]:
   yy,xx=np.where(ar[500:,x0:x1,3]>=128);y=int(yy.max()+500);pts.append([float((np.where(ar[y,x0:x1,3]>=128)[0]+x0).mean()),y])
  landmarks.append(np.array(pts))
 delta=(landmarks[1]-landmarks[0])*s;ys,xs=np.where(masks[1]);allowed=np.zeros(masks[1].shape,bool)
 for x0,y0,x1,y1 in [[219,240,310,337],[185,347,237,431],[307,347,355,431]]:allowed[y0:y1,x0:x1]=True
 union=masks[0]|masks[1];outside=(~allowed)&union;rgbdiff=np.abs(bb[:,:,:3].astype(int)-aa[:,:,:3].astype(int)).max(axis=2)
 rows.append({'source_id':17+i,'raw_body_height_span':int(ys.max()-ys.min()),'density_vs_source72':float((ys.max()-ys.min())/72),'new_crown_Lboot_Rboot_raw':landmarks[1].tolist(),'new_crown_Lboot_Rboot_registered':(landmarks[1]*s+np.array(tr)).tolist(),'delta_edit_minus_original_logical':delta.tolist(),'protected_regions':stats,'outside_roi_visible_pixels':int(outside.sum()),'outside_roi_rgb_max_channel_diff_gt16_pixels':int(((rgbdiff>16)&outside).sum()),'outside_roi_mean_max_channel_rgb_diff':float(rgbdiff[outside].mean())})
out.save(P/'body-density4-CANDIDATE.png')
dump(P/'registration-review.json',{'status':'candidate_static_review_only_no_runtime','same_dimensions':True,'old_new_raw_size':list(new.size),'frozen_registration_sha256':sha(P/'frozen-original-registration.json'),'old_raw_sha256':sha(C/'raw-v1.png'),'new_raw_sha256':sha(P/'raw-edit-v1.png'),'one_common_scale_from_original':s,'refit_performed':False,'warp_or_independent_scale':False,'density_ge2_all':all(x['density_vs_source72']>=2 for x in rows),'records':rows,'boundary':'Mask distances measure visible alpha geometry only. RGB differences outside ROIs mean not pixel-locked; assess whether lighting/identity changed materially. No bone/contact inference.'})
for density in [1,2,4]:
 u=128*density;b=Image.new('RGBA',(4*u,5*u),(64,68,72,255));dr=ImageDraw.Draw(b)
 for i in range(4):
  sources=[Image.open(P.parent/'earth_hero_s_input_plan_v1'/f'source-{17+i}.png').convert('RGBA'),Image.open(C/'body-density4-CANDIDATE.png').crop((512*i,0,512*(i+1),512)),out.crop((512*i,0,512*(i+1),512)),Image.open(R/'assets/earth/hero/se_idle_v1/body.png').crop((512*i,0,512*(i+1),512)),Image.open(R/'assets/earth/hero/e_idle_v1/body.png').crop((512*i,0,512*(i+1),512))]
  for j,t in enumerate(sources):b.alpha_composite(t.resize((u,u),Image.Resampling.NEAREST if j==0 else Image.Resampling.LANCZOS),(i*u,j*u));dr.text((i*u+4,j*u+4),f'{["source S","old S","edited S","approved SE","approved E"][j]} {i}',fill='white')
 b.save(D/f'source-old-edit-SE-E-same-logical-{density}x.png')
b=Image.new('RGBA',(1200,300),(64,68,72,255));dr=ImageDraw.Draw(b)
for i,(label,t) in enumerate([('old S',Image.open(C/'body-density4-CANDIDATE.png')),('edited S',out),('SE13',Image.open(R/'assets/earth/hero/se_idle_v1/body.png')),('E9',Image.open(R/'assets/earth/hero/e_idle_v1/body.png'))]):
 b.alpha_composite(t.crop((88,80,240,280)),(i*300+70,40));dr.text((i*300+10,10),label+' same HD4',fill='white')
b.save(D/'garment-before-after-SE-E.png')
b=Image.new('RGBA',(1536,256),(64,68,72,255));dr=ImageDraw.Draw(b)
for j,i in enumerate([3,0,1,2,3,0]):b.alpha_composite(out.crop((512*i,0,512*(i+1),512)).resize((256,256),Image.Resampling.LANCZOS),(j*256,0));dr.text((j*256+4,4),str(17+i),fill='white')
b.save(D/'edited-loop20-17-18-19-20-17-2x.png')
print(json.dumps({'max_crown_boot_delta_logical':max(np.linalg.norm(np.array(x['delta_edit_minus_original_logical']),axis=1).max() for x in rows),'min_raw_density':min(x['density_vs_source72'] for x in rows),'protected_max_distance_raw':{name:max(x['protected_regions'][name]['max_mask_to_mask_distance_raw'] for x in rows) for name in rois},'outside_rgb_changes':[x['outside_roi_rgb_max_channel_diff_gt16_pixels'] for x in rows]},indent=2))
