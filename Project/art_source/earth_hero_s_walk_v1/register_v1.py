from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,itertools
P=Path(__file__).resolve().parent;R=P.parents[1];D=R/'diagnostics/earth_hero_s_walk_v1';D.mkdir(exist_ok=True,parents=True);S=P.parent/'earth_hero_s_input_plan_v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
im=Image.open(P/'raw-v1.png').convert('RGBA');assert im.size==(1536,1024);analysis=json.loads((S/'SOURCE_PHASE_ANALYSIS.json').read_text());parts=[];raw=[];target=[];sources=[]
for i,f in enumerate(analysis['walk']):
 n=57+i;t=im.crop(((i%3)*512,(i//3)*512,(i%3+1)*512,(i//3+1)*512));parts.append(t);a=np.array(t);yy,xx=np.where(a[:,:,3]>=128);y=int(yy.min());cx=float(np.where(a[y,:,3]>=128)[0].mean());pts=[[cx,y]]
 for l,h in [(int(cx-75),int(cx)),(int(cx),int(cx+75))]:
  yy,xx=np.where(a[270:,l:h,3]>=128);y=int(yy.max()+270);x=float(np.where(a[y,l:h,3]>=128)[0].mean()+l);pts.append([x,y])
 raw.append(pts);src=Image.open(S/f'source-{n}.png').convert('RGBA');sources.append(src);ar=np.array(src);yy,xx=np.where(ar[:,:,3]>0);y=int(yy.min());x=float(np.where(ar[y,:,3]>0)[0].mean());target.append([[x,y]]+[f['legs'][side]['visible_material_chain'][-1]['xy'] for side in ['L','R']])
raw=np.array(raw);target=np.array(target);ac=raw-raw.mean(axis=1,keepdims=True);bc=target-target.mean(axis=1,keepdims=True);s=float((ac*bc).sum()/(ac*ac).sum());trans=target.mean(axis=1)-raw.mean(axis=1)*s
out=Image.new('RGBA',(3072,512));rows=[];re=Image.new('RGBA',im.size)
for i,t in enumerate(parts):
 tx,ty=trans[i];k=4*s;tile=t.transform((512,512),Image.Transform.AFFINE,(1/k,0,-tx/s,0,1/k,-ty/s),Image.Resampling.BICUBIC);out.paste(tile,(i*512,0));re.paste(t,((i%3)*512,(i//3)*512));a=np.array(t);yy,xx=np.where(a[:,:,3]>=128);res=raw[i]*s+trans[i]-target[i];h=int(yy.max()-yy.min());sh=max(target[i,1:,1])-target[i,0,1]
 rows.append({'source_id':57+i,'raw_cell_xywh':[(i%3)*512,(i//3)*512,512,512],'raw_crown_Lboot_Rboot':raw[i].tolist(),'source_crown_Lboot_Rboot':target[i].tolist(),'translation':trans[i].tolist(),'raw_height_span':h,'source_height_span':float(sh),'raw_density':float(h/sh),'registered_crown_Lboot_Rboot':(raw[i]*s+trans[i]).tolist(),'residual_logical':res.tolist(),'max_proxy_residual_norm':float(np.linalg.norm(res,axis=1).max()),'frame_rgba_sha256':hashlib.sha256(tile.tobytes()).hexdigest()})
assert re.tobytes()==im.tobytes();out.save(P/'body-density4-DIAGNOSTIC.png');dump(P/'registration-v1.json',{'status':'unapproved_six_walk_diagnostic_not_runtime','raw_sha256':sha(P/'raw-v1.png'),'common_scale_raw_to_logical':s,'method':'one global isotropic scale + per-frame rigid translation only; no warp or independent frame normalization','root':[16,64],'density':4,'ids':list(range(57,63)),'ticks':7,'source_order':'57,58,59 /60,61,62 input; strip57..62 output','exact_raw_reassembly':True,'records':rows,'uncertainty':{'raw_contour_proxy_px':3,'source_crown_boot_px':1},'boundary':'crown and boot ends are nonhomologous costume surface proxies, not bones/contact. Residuals cannot be corrected by moving limbs.'})
for scale in [1,2,4]:
 u=128*scale;b=Image.new('RGBA',(6*u,3*u),(64,68,72,255));dr=ImageDraw.Draw(b);idle=Image.open(R/'assets/earth/hero/s_idle_v1/body.png').convert('RGBA').crop((0,0,512,512))
 for i in range(6):
  for row,t in enumerate([sources[i],out.crop((i*512,0,(i+1)*512,512)),idle]):
   b.alpha_composite(t.resize((u,u),Image.Resampling.NEAREST if row==0 else Image.Resampling.LANCZOS),(i*u,row*u));dr.text((i*u+4,row*u+4),['source','S walk candidate','S idle17 approved'][row]+f' {57+i}' if row<2 else 'S idle17 approved',fill='white')
 b.save(D/f'source-walk-idle-same-logical-{scale}x.png')
# Closure and actual action comparison; not invented intermediate phases.
b=Image.new('RGBA',(1536,256),(64,68,72,255));dr=ImageDraw.Draw(b);idleatlas=Image.open(R/'assets/earth/hero/s_idle_v1/body.png').convert('RGBA')
for j,(label,t) in enumerate([('idle20',idleatlas.crop((1536,0,2048,512))),('walk62',out.crop((2560,0,3072,512))),('walk57',out.crop((0,0,512,512))),('walk60',out.crop((1536,0,2048,512))),('walk62',out.crop((2560,0,3072,512))),('idle17',idleatlas.crop((0,0,512,512)))]):
 b.alpha_composite(t.resize((256,256),Image.Resampling.LANCZOS),(j*256,0));dr.text((j*256+4,4),label,fill='white')
b.save(D/'loop62-57-and-idle-transitions-2x.png')
# Source/candidate arm panels same logical crop and scale.
b=Image.new('RGBA',(6*192,2*192),(64,68,72,255));dr=ImageDraw.Draw(b)
for i in range(6):
 for row,t in enumerate([sources[i].crop((16,18,64,66)).resize((192,192),Image.Resampling.NEAREST),out.crop((i*512+64,72,i*512+256,264))]):b.alpha_composite(t,(i*192,row*192));dr.text((i*192+3,row*192+3),str(57+i),fill='white')
b.save(D/'arms-source-candidate-same-scale.png')
print(json.dumps({'common_scale':s,'minimum_raw_density':min(x['raw_density'] for x in rows),'max_residual':max(x['max_proxy_residual_norm'] for x in rows),'rows':[{'id':x['source_id'],'foot_dy_generated':x['registered_crown_Lboot_Rboot'][1][1]-x['registered_crown_Lboot_Rboot'][2][1],'foot_dy_source':x['source_crown_Lboot_Rboot'][1][1]-x['source_crown_Lboot_Rboot'][2][1]} for x in rows]},indent=2))
