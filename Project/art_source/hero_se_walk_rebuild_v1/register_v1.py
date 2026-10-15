from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent
S=P.parent/'hero_se_walk_source_r5'
a=json.loads((S/'SE_WALK_SOURCE_ANALYSIS.json').read_text())
names=['crown','neck_surface','sternum_armor_proxy','pelvis','A_boot','B_boot']
# Raw points are manually read surface proxies on 512x512 equal cells, +/-6 raw pixels.
c=np.array([[[309,16],[312,99],[313,148],[300,250],[364,480],[232,360]],[[278,16],[284,99],[285,148],[277,250],[306,472],[0,0]],[[251,16],[255,99],[258,148],[253,250],[245,473],[292,441]],[[303,17],[307,99],[310,147],[302,238],[182,342],[420,449]],[[283,18],[291,100],[295,151],[282,246],[205,382],[365,459]],[[248,19],[259,103],[262,152],[252,249],[263,472],[0,0]]],float)
s=[];weights=[]
for i,f in enumerate(a['frames']):
 vals=[f['crown'],[42,28 if i not in (1,5) else 27],[42,39],f['pelvis'],f['A_boot'],f['B_boot']]
 w=[1,.6,.5,.5,1,1]
 if i in (1,5):w[-1]=0; vals[-1]=[0,0]
 s.append(vals);weights.append(w)
s=np.array(s,float);w=np.array(weights); cm=(c*w[:,:,None]).sum(1)/w.sum(1)[:,None];sm=(s*w[:,:,None]).sum(1)/w.sum(1)[:,None]
ca=c-cm[:,None,:];sa=s-sm[:,None,:];scale=float((ca*sa*w[:,:,None]).sum()/(ca*ca*w[:,:,None]).sum());t=sm-scale*cm
raw=Image.open(P/'raw-v1.png').convert('RGBA'); rebuilt=Image.new('RGBA',raw.size); atlas=Image.new('RGBA',(768,128));recs=[]
for i in range(6):
 x,y=i%3*512,i//3*512;cell=raw.crop((x,y,x+512,y+512));rebuilt.paste(cell,(x,y));tx,ty=t[i];out=cell.transform((128,128),Image.Transform.AFFINE,(1/scale,0,-tx/scale,0,1/scale,-ty/scale),resample=Image.Resampling.BICUBIC);atlas.paste(out,(i*128,0));pts=c[i]*scale+t[i]
 recs.append({'source_id':51+i,'translation':t[i].tolist(),'points':{name:{'source':s[i,j].tolist() if w[i,j] else None,'raw':c[i,j].tolist() if w[i,j] else None,'mapped':pts[j].tolist() if w[i,j] else None,'delta':(pts[j]-s[i,j]).tolist() if w[i,j] else None,'weight':float(w[i,j])} for j,name in enumerate(names)}})
assert rebuilt.tobytes()==raw.tobytes()
atlas.save(P/'v1-registered-atlas-128.png')
bg=Image.new('RGBA',(768,256),(100,100,100,255));bg.alpha_composite(Image.open(S/'source-51-56-native-strip.png'),(0,0));bg.alpha_composite(atlas,(0,128));bg.resize((2304,768),Image.Resampling.NEAREST).convert('RGB').save(P/'v1-source-registered-3x-gray.jpg',quality=95)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m={'status':'research_pending_pose_review_not_runtime','raw_sha256':sha(P/'raw-v1.png'),'atlas_sha256':sha(P/'v1-registered-atlas-128.png'),'source_ids':list(range(51,57)),'frame_size':[128,128],'grid':[6,1],'native_draw_origin_in_cell':[16,64],'frame_ticks':7,'common_uniform_scale':scale,'registration_method':'one common uniform scale and per-frame weighted multipoint rigid translation; no rotation or deformation','exact_raw_rectangle_rebuild':True,'uncertainty':{'source_clothing_proxy':3,'source_boot_crown':1,'candidate_raw_manual':6},'records':recs,'visible_issues':['55 far hand more exposed than source','56 second short boot mostly occluded unlike source visible right ankle boot; excluded unreliable endpoint from fitting','registration cannot correct limb shape or occlusion']}
(P/'v1-registration.json').write_text(json.dumps(m,indent=2)+'\n');print(scale)
