from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent
S=P.parent/'hero_se_walk_source_r5'
a=json.loads((S/'SE_WALK_SOURCE_ANALYSIS.json').read_text())
names=['crown','neck_surface','sternum_armor_proxy','pelvis','A_boot','B_boot']
# Raw points are manually read surface proxies on 512x512 equal cells, +/-6 raw pixels.
c=np.array([[[214,56],[222,143],[223,207],[215,330],[285,593],[172,461]],[[212,56],[220,143],[224,207],[214,329],[220,580],[0,0]],[[216,56],[225,143],[228,209],[222,329],[198,552],[301,540]],[[212,49],[219,136],[221,197],[215,319],[127,487],[342,562]],[[211,49],[220,136],[225,199],[220,318],[141,484],[286,532]],[[215,49],[228,138],[234,201],[226,320],[236,574],[255,497]]],float)
s=[];weights=[]
for i,f in enumerate(a['frames']):
 vals=[f['crown'],[42,28 if i not in (1,5) else 27],[42,39],f['pelvis'],f['A_boot'],f['B_boot']]
 w=[1,.6,.5,.5,1,1]
 if i ==1:w[-1]=0; vals[-1]=[0,0]
 s.append(vals);weights.append(w)
s=np.array(s,float);w=np.array(weights); cm=(c*w[:,:,None]).sum(1)/w.sum(1)[:,None];sm=(s*w[:,:,None]).sum(1)/w.sum(1)[:,None]
ca=c-cm[:,None,:];sa=s-sm[:,None,:];scale=float((ca*sa*w[:,:,None]).sum()/(ca*ca*w[:,:,None]).sum());t=sm-scale*cm
raw=Image.open(P/'raw-v3.png').convert('RGBA'); rebuilt=Image.new('RGBA',raw.size); atlas=Image.new('RGBA',(768,128));recs=[]
for i in range(6):
 xs=[0,409,817,1226];ys=[0,642,1283];x,y=xs[i%3],ys[i//3];cell=raw.crop((x,y,xs[i%3+1],ys[i//3+1]));rebuilt.paste(cell,(x,y));tx,ty=t[i];out=cell.transform((128,128),Image.Transform.AFFINE,(1/scale,0,-tx/scale,0,1/scale,-ty/scale),resample=Image.Resampling.BICUBIC);atlas.paste(out,(i*128,0));pts=c[i]*scale+t[i]
 recs.append({'source_id':51+i,'translation':t[i].tolist(),'points':{name:{'source':s[i,j].tolist() if w[i,j] else None,'raw':c[i,j].tolist() if w[i,j] else None,'mapped':pts[j].tolist() if w[i,j] else None,'delta':(pts[j]-s[i,j]).tolist() if w[i,j] else None,'weight':float(w[i,j])} for j,name in enumerate(names)}})
assert rebuilt.tobytes()==raw.tobytes()
atlas.save(P/'v3-registered-atlas-128.png')
bg=Image.new('RGBA',(768,256),(100,100,100,255));bg.alpha_composite(Image.open(S/'source-51-56-native-strip.png'),(0,0));bg.alpha_composite(atlas,(0,128));bg.resize((2304,768),Image.Resampling.NEAREST).convert('RGB').save(P/'v3-source-registered-3x-gray.jpg',quality=95)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m={'status':'research_pending_pose_review_not_runtime','raw_sha256':sha(P/'raw-v3.png'),'atlas_sha256':sha(P/'v3-registered-atlas-128.png'),'source_ids':list(range(51,57)),'frame_size':[128,128],'grid':[6,1],'native_draw_origin_in_cell':[16,64],'frame_ticks':7,'common_uniform_scale':scale,'registration_method':'one common uniform scale and per-frame weighted multipoint rigid translation; no rotation or deformation','exact_raw_rectangle_rebuild':True,'uncertainty':{'source_clothing_proxy':3,'source_boot_crown':1,'candidate_raw_manual':6},'records':recs,'visible_issues':['54 stride must be checked at native size','chest and waist panel design simplified relative to locked idle identity','registration cannot correct limb shape or occlusion']}
a=np.array(raw)[:,:,3]
m['raw_cell_boundaries']={'x':[0,409,817,1226],'y':[0,642,1283]}
m['split_boundary_max_alpha']={'x408':int(a[:,408].max()),'x409':int(a[:,409].max()),'x816':int(a[:,816].max()),'x817':int(a[:,817].max()),'y641_642':int(a[641:643].max())}
(P/'v3-registration.json').write_text(json.dumps(m,indent=2)+'\n');print(scale)
