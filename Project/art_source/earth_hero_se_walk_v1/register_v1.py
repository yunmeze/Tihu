from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent
S=P.parent/'hero_se_walk_source_r5'
a=json.loads((S/'SE_WALK_SOURCE_ANALYSIS.json').read_text())
names=['crown','neck_surface','sternum_armor_proxy','pelvis','A_boot','B_boot']
# Manually read visible surface proxies, +/-8 raw pixels; hidden boot52 remains null.
c=np.array([[[235,60],[240,150],[242,211],[237,323],[310,612],[184,477]],[[218,60],[222,150],[226,211],[224,323],[239,585],[0,0]],[[231,61],[235,150],[240,211],[239,323],[218,568],[321,555]],[[230,43],[237,132],[242,199],[242,314],[127,491],[367,579]],[[223,44],[230,134],[238,200],[237,315],[163,499],[304,550]],[[245,44],[251,136],[259,202],[258,315],[266,581],[279,530]]],float)
s=[];weights=[]
for i,f in enumerate(a['frames']):
 vals=[f['crown'],[42,28 if i not in (1,5) else 27],[42,39],f['pelvis'],f['A_boot'],f['B_boot']]
 w=[1,.6,.5,.5,1,1]
 if i ==1:w[-1]=0; vals[-1]=[0,0]
 s.append(vals);weights.append(w)
s=np.array(s,float);w=np.array(weights); cm=(c*w[:,:,None]).sum(1)/w.sum(1)[:,None];sm=(s*w[:,:,None]).sum(1)/w.sum(1)[:,None]
ca=c-cm[:,None,:];sa=s-sm[:,None,:];scale=float((ca*sa*w[:,:,None]).sum()/(ca*ca*w[:,:,None]).sum());t=sm-scale*cm
raw=Image.open(P/'raw-v1.png').convert('RGBA'); rebuilt=Image.new('RGBA',raw.size); atlas=Image.new('RGBA',(768,128));recs=[]
for i in range(6):
 xs=[0,409,817,1226];ys=[0,642,1283];x,y=xs[i%3],ys[i//3];cell=raw.crop((x,y,xs[i%3+1],ys[i//3+1]));rebuilt.paste(cell,(x,y));tx,ty=t[i];out=cell.transform((128,128),Image.Transform.AFFINE,(1/scale,0,-tx/scale,0,1/scale,-ty/scale),resample=Image.Resampling.BICUBIC);atlas.paste(out,(i*128,0));pts=c[i]*scale+t[i]
 recs.append({'source_id':51+i,'translation':t[i].tolist(),'points':{name:{'source':s[i,j].tolist() if w[i,j] else None,'raw':c[i,j].tolist() if w[i,j] else None,'mapped':pts[j].tolist() if w[i,j] else None,'delta':(pts[j]-s[i,j]).tolist() if w[i,j] else None,'weight':float(w[i,j])} for j,name in enumerate(names)}})
assert rebuilt.tobytes()==raw.tobytes()
atlas.save(P/'body-density1.png')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m={'status':'research_pending_pose_review_not_runtime','raw_sha256':sha(P/'raw-v1.png'),'atlas_sha256':sha(P/'body-density1.png'),'source_ids':list(range(51,57)),'frame_size':[128,128],'grid':[6,1],'native_draw_origin_in_cell':[16,64],'frame_ticks':7,'common_uniform_scale':scale,'registration_method':'one common uniform scale and per-frame weighted multipoint rigid translation; no rotation or deformation','exact_raw_rectangle_rebuild':True,'uncertainty':{'source_clothing_proxy':3,'source_boot_crown':1,'candidate_raw_manual':8},'records':recs,'visible_issues':['54 stride must be checked at native size','52 rear edge visibility and 54 stride/55 fold/56 short boot need sequence review','registration cannot correct limb shape or occlusion']}
a=np.array(raw)[:,:,3]
m['raw_cell_boundaries']={'x':[0,409,817,1226],'y':[0,642,1283]}
m['split_boundary_max_alpha']={'x408':int(a[:,408].max()),'x409':int(a[:,409].max()),'x816':int(a[:,816].max()),'x817':int(a[:,817].max()),'y641_642':int(a[641:643].max())}
(P/'registration-v1.json').write_text(json.dumps(m,indent=2)+'\n');print(scale)

# Direct original-density sampling: never upscale the 128 atlas.
hd=Image.new('RGBA',(3072,512))
for i in range(6):
 xs=[0,409,817,1226];ys=[0,642,1283];r=(xs[i%3],ys[i//3],xs[i%3+1],ys[i//3+1]); cell=raw.crop(r);tx,ty=t[i];out=cell.transform((512,512),Image.Transform.AFFINE,(1/(scale*4),0,-tx/scale,0,1/(scale*4),-ty/scale),resample=Image.Resampling.BICUBIC);hd.paste(out,(512*i,0));recs[i]['raw_rect']=list(r);recs[i]['region_px']=[512*i,0,512,512]
hd.save(P/'body-density4.png');m.update({'texture_density':4,'texture_frame_size':[512,512],'logical_frame_size':[128,128],'logical_root':[16,64],'texture_root':[64,256],'atlas':'body-density4.png','atlas_sha256':sha(P/'body-density4.png'),'lighting':'warm screen upper-left daylight; no cast shadow; old right-up cast prohibited'})
(P/'registration-v1.json').write_text(json.dumps(m,indent=2)+'\n')
D=P.parents[1]/'diagnostics/hero/earth-se-walk-v1';D.mkdir(parents=True,exist_ok=True)
for d in [1,2]:
 b=Image.new('RGBA',(768*d,256*d),(100,100,100,255));src=Image.open(S/'source-51-56-native-strip.png').convert('RGBA').resize((768*d,128*d),Image.Resampling.NEAREST);b.alpha_composite(src,(0,0));b.alpha_composite(hd.resize((768*d,128*d),Image.Resampling.LANCZOS),(0,128*d));b.convert('RGB').save(D/f'source-candidate-true{d}x.png')
print(m['atlas_sha256'])
