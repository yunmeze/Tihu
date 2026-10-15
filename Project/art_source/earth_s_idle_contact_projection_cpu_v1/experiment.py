#!/usr/bin/env python3
"""S-only fixed CPU shadow sampling experiment. No runtime writes or GUI."""
from pathlib import Path
import json,hashlib,time,importlib.util
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import map_coordinates
P=Path(__file__).resolve().parents[2];H=Path(__file__).parent;D=P/'diagnostics/earth-s-idle-contact-projection-cpu-v1';D.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={}
def track(p):
 q=P/p;inputs[p]=sha(q);return q
def load(p):return json.loads(track(p).read_text())
track(str(Path(__file__).relative_to(P)));track(str((H/'PREIMPLEMENTATION_PLAN.md').relative_to(P)))
m=load('assets/earth/hero/s_idle_v1/manifest.json');im=Image.open(track(m['texture'][6:])).convert('RGBA');atlas=np.array(im);assert inputs[m['texture'][6:]]==m['texture_sha256'];assert atlas.shape==(512,2048,4)
old=load('art_source/earth_es_idle_shadow_study_v1/measurements.json')['directions']['s'];gate=load('assets/earth/shadows/se_flat_v1/manifest.json');allowed=np.array(Image.open(track(gate['allowed']['texture'][6:])))>0;assert sha(P/gate['allowed']['texture'][6:])==gate['allowed']['sha256']
for p in ['scripts/earth/sample_world.gd','scripts/earth/max_ground_shadow.gd','shaders/earth_max_ground_shadow.gdshader','assets/earth/hero/e_idle_v1/body.png','assets/earth/hero/se_idle_v1/body.png','assets/earth/shadows/se_flat_v1/envelope.png']:track(p)
spec=importlib.util.spec_from_file_location('g',track('tools/earth/build_flat_shadow_gate.py'));g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
B=85.3125;DELTA=2.0625;Y0=60.;Y1=80.;L=20.;TL=-39.46875;TR=-35.46875;V=np.array([1.2,1.55])
points=np.array([f['visible_bottom_edge_points_logical']for f in old['frames']]);assert points[:,:,1].mean()==B;assert points[:,0,1].mean()==B-DELTA;assert points[:,1,1].mean()==B+DELTA
uniona=np.maximum.reduce([atlas[:,i*512:(i+1)*512,3]for i in range(4)]);ys,xs=np.nonzero(uniona>0);xc=(xs+.5)/4;yc=(ys+.5)/4;tt=1.55*xc-1.2*yc
assert abs(tt[(yc>=80)&(xc<40)].max()+.6875-TL)<1e-10;assert abs(tt[(yc>=80)&(xc>=40)].min()-.6875-TR)<1e-10
assert (uniona[240:320,159:161]==0).all()
def f(t):return -DELTA+2*DELTA*np.clip((t-TL)/(TR-TL),0,1)
def forward(p):
 t=p[...,0]*1.55-p[...,1]*1.2;b=B+np.clip((p[...,1]-Y0)/L,0,1)*f(t);return p+(b-p[...,1])[...,None]*V

def inverse(q):
 t=q[...,0]*1.55-q[...,1]*1.2;fv=f(t);qy=q[...,1];q0=1.55*B-.55*Y0;q1=1.55*(B+fv)-.55*Y1
 yt=(qy-1.55*B+1.55*fv*Y0/L)/(-.55+1.55*fv/L);yb=(1.55*(B+fv)-qy)/.55;yu=(1.55*B-qy)/.55
 y=np.where(qy>=q0,yu,np.where(qy<=q1,yb,yt));x=(t+1.2*y)/1.55;return np.stack((x,y),-1)
def ownership(p):
 t=1.55*p[...,0]-1.2*p[...,1];return np.where((p[...,1]>=Y0)&(t<=TL),1,np.where((p[...,1]>=Y0)&(t>=TR),2,0))
def jacobian(p):
 t=p[...,0]*1.55-p[...,1]*1.2;fv=f(t);w=np.clip((p[...,1]-Y0)/L,0,1);fp=np.where((t>TL)&(t<TR),2*DELTA/(TR-TL),0);wp=np.where((p[...,1]>Y0)&(p[...,1]<Y1),1/L,0)
 bx=w*fp*1.55;by=wp*fv-w*fp*1.2
 J=np.zeros(p.shape[:-1]+(2,2));J[...,0,0]=1+1.2*bx;J[...,0,1]=1.2*(by-1);J[...,1,0]=1.55*bx;J[...,1,1]=1+1.55*(by-1);return J
rng=np.random.default_rng(20261015);sample=rng.uniform([0,0],[128,128],(200000,2));err=np.max(abs(inverse(forward(sample))-sample));assert err<1e-10
J=jacobian(sample);det=np.linalg.det(J);assert det.max()<-.39
# Numeric differentiation away from piecewise derivative boundaries.
t=sample[:,0]*1.55-sample[:,1]*1.2;keep=(abs(t-TL)>1e-3)&(abs(t-TR)>1e-3)&(abs(sample[:,1]-Y0)>1e-3)&(abs(sample[:,1]-Y1)>1e-3);q=sample[keep][:20000];eps=1e-5
Jn=np.stack([(forward(q+np.array([eps,0]))-forward(q-np.array([eps,0])))/(2*eps),(forward(q+np.array([0,eps]))-forward(q-np.array([0,eps])))/(2*eps)],-1);jerr=float(abs(Jn-jacobian(q)).max());assert jerr<1e-7
boundary=[]
for key in ['y60','y80','tL','tR']:
 if key.startswith('y'):p=np.c_[np.linspace(0,128,1025),np.full(1025,float(key[1:]))];delta=np.array([0,1e-7])
 else:
  yy=np.linspace(0,128,1025);p=np.c_[((TL if key=='tL'else TR)+1.2*yy)/1.55,yy];delta=np.array([1e-7,0])
 jump=float(np.max(np.linalg.norm(forward(p+delta)-forward(p-delta),axis=1)));boundary.append({'boundary':key,'across_epsilon_distance':jump});assert jump<1e-5
# Sample full original bilinear alpha once, then restrict by exact ownership.
# Three equal-transform branches reconstruct alpha without filtering cut atlases.
def alpha_at(a,p):
 raw=p*4;ok=(raw[...,0]>=0)&(raw[...,1]>=0)&(raw[...,0]<512)&(raw[...,1]<512);coords=np.stack((np.clip(raw[...,1],.5,511.5)-.5,np.clip(raw[...,0],.5,511.5)-.5));return map_coordinates(a.astype(float)/255,coords,order=1,mode='nearest',prefilter=False)*ok

def envelope_bounds(lo,hi):
 tlo=1.55*lo[:,0]-1.2*hi[:,1];thi=1.55*hi[:,0]-1.2*lo[:,1];fl=f(tlo);fh=f(thi);wl=np.clip((lo[:,1]-Y0)/L,0,1);wh=np.clip((hi[:,1]-Y0)/L,0,1);products=np.stack([wl*fl,wl*fh,wh*fl,wh*fh],1);bl=B+products.min(1);bh=B+products.max(1);hlo=bl-hi[:,1];hhi=bh-lo[:,1]
 return np.concatenate((lo+V*hlo[:,None]-1.8,hi+V*hhi[:,None]+1.8),1)
rects=[];phase_reports=[];sampling_grid=np.stack(np.meshgrid((np.arange(352)+.5)/2,(np.arange(320)+.5)/2),-1);oldA=np.array(old['fixed_line']['matrix_rows']);oldT=np.array(old['fixed_line']['translation_logical']);oldinv=np.linalg.inv(oldA)
board=Image.new('RGB',(352*4,320*3+50),(48,53,58));draw=ImageDraw.Draw(board);timings=[];all_new=[];all_old=[]
for i,sid in enumerate([17,18,19,20]):
 rgba=atlas[:,i*512:(i+1)*512];a=rgba[:,:,3];y,x=np.nonzero(a>0);rawpts=np.c_[(x+.5)/4,(y+.5)/4];owners=ownership(rawpts);assert np.all((owners>=0)&(owners<=2));counts=[int((owners==k).sum())for k in range(3)];assert sum(counts)==len(x)
 ptest=np.concatenate((rawpts,sample[:40000]),0);av=alpha_at(a,ptest);parts=np.stack([np.where(ownership(ptest)==k,av,0)for k in range(3)]);recon=parts.max(0);assert np.array_equal(recon,av);assert np.array_equal(parts.sum(0),av)
 lo=np.c_[x,y]/4-.125;hi=lo+.5;br=envelope_bounds(lo,hi);rects.append(br)
 # Independently sample corners+midpoint of every support rectangle to check interval bounds.
 probes=np.stack([lo,hi,np.c_[lo[:,0],hi[:,1]],np.c_[hi[:,0],lo[:,1]],(lo+hi)/2],1);mapped=forward(probes);assert (mapped.min(1)>=br[:,:2]+1.8-1e-9).all() and(mapped.max(1)<=br[:,2:]-1.8+1e-9).all()
 sv=np.linalg.svd(jacobian(rawpts),compute_uv=False);cond=sv[:,0]/sv[:,1];opaque=a[y,x]>=128
 boot=points[i];bp=forward(boot);delta=bp-boot
 start=time.perf_counter();new=np.zeros((320,352));oldshadow=np.zeros_like(new)
 for dy in [-1,0,1]:
  for dx in [-1,0,1]:
   q=sampling_grid+np.array([dx*.8,dy*.8]);p=inverse(q);v=alpha_at(a,p);own=ownership(p);merged=np.maximum.reduce([np.where(own==k,v,0)for k in range(3)]);assert np.array_equal(v,merged);weight=(2 if dx==0 else 1)*(2 if dy==0 else 1)/16
   new+=merged*weight;oldshadow+=alpha_at(a,(q-oldT)@oldinv.T)*weight
 elapsed=time.perf_counter()-start;timings.append(elapsed);new*=.25;oldshadow*=.25;all_new.append(new);all_old.append(oldshadow);assert new.max()<=.25+1e-12
 np.savez_compressed(D/f'phase-{sid}-alpha.npz',new=new,old=oldshadow)
 for row,shadow in enumerate([np.zeros_like(new),oldshadow,new]):
  # True 2x logical sample grid. Original d4 RGBA sampled without modifying source.
  background=np.full((320,352,3),[174,179,183],float);background=background*(1-shadow[:,:,None])+np.array([.035,.045,.055])*255*shadow[:,:,None]
  raw=sampling_grid*4;valid=(raw[:,:,0]<512)&(raw[:,:,1]<512);coords=np.stack((np.clip(raw[:,:,1],.5,511.5)-.5,np.clip(raw[:,:,0],.5,511.5)-.5));body=np.stack([map_coordinates(rgba[:,:,c].astype(float),coords,order=1,mode='nearest',prefilter=False)for c in range(4)],-1);body[:,:,3]*=valid;ba=body[:,:,3:]/255;pix=np.rint(body[:,:,:3]*ba+background*(1-ba)).clip(0,255).astype('uint8');tile=Image.fromarray(pix,'RGB');td=ImageDraw.Draw(tile);td.text((4,4),f'S{sid} '+['NO SHADOW','OLD fixed slope .257637','NEW invariant contact lanes'][row],fill=(25,25,25));board.paste(tile,(i*352,row*320+50))
 phase_reports.append({'source_id':sid,'alpha_positive_texels':int(len(x)),'partition_counts_body_left_right':counts,'partition_reconstruction_exact':True,'fullalpha_coverage_no_discard':True,'visible_boot_points':boot.tolist(),'projected_boot_points':bp.tolist(),'boot_projection_delta':delta.tolist(),'max_boot_displacement':float(np.linalg.norm(delta,axis=1).max()),'shadow_alpha_at_visible_boot_proxies_new':[float(sum(alpha_at(a,inverse(point[None,:]+np.array([dx*.8,dy*.8])))[0]*(2 if dx==0 else 1)*(2 if dy==0 else 1)/16 for dy in [-1,0,1]for dx in [-1,0,1])*.25)for point in boot],'jacobian_anisotropy_max_positive_alpha':float(cond.max()),'jacobian_anisotropy_max_opaque':float(cond[opaque].max()),'opaque_anisotropy_gt10_count':int(((cond>10)&opaque).sum()),'opaque_texels':int(opaque.sum()),'new_alpha_gt1_255_d2_samples':int((new>1/255).sum()),'old_alpha_gt1_255_d2_samples':int((oldshadow>1/255).sum()),'render_seconds_old_and_new':elapsed})
# Proxy uncertainty positions are covered using the same nonlinear fixed map.
pp=points.reshape(-1,2);u=np.array([1,.75]);rects.append(envelope_bounds(pp-u,pp+u));rects.append(np.concatenate((pp-u-1.8,pp+u+1.8),1));rr=np.concatenate(rects);off=np.floor(rr[:,:2].min(0)*2)/2;end=np.ceil(rr[:,2:].max(0)*2)/2;env=g.raster(rr,off,np.rint((end-off)*2).astype(int));g.verify_coverage(env,rr,off);Image.fromarray(env.astype('uint8')*255,'L').save(D/'full-four-phase-envelope.png')
def allows(cell):
 base=(np.array(cell)*[48,32]+[-16,-64]+off-[2496,960])*2;bx,by=np.floor(base).astype(int);ex,ey=np.ceil(base+np.array(env.shape[::-1])).astype(int)
 if bx<0 or by<0 or ex>1536 or ey>1024:return False
 return all(bool(allowed[by+dy:by+dy+env.shape[0],bx+dx:bx+dx+env.shape[1]][env].all())for dx in range(int(np.ceil(base[0])-bx)+1)for dy in range(int(np.ceil(base[1])-by)+1))
cells=[[x,y]for x in range(50,70)for y in range(28,48)if allows([x,y])]
draw.text((5,8),'S-only CPU experiment / actual unchanged d4 body / true 2x logical sampling / cast(1.2,.55), blur.8, opacity.25',fill='white');draw.text((5,26),'Rows: no shadow / rejected old narrow cast / new continuous shadow-only map. Four phases share every parameter. NOT native approval.',fill='white');board.save(D/'four-phase-off-old-new-2x.png')
# Show local contacts at4x screen scale by re-rendering these retained CPU2x samples; labeled enlargement only.
contact=Image.new('RGB',(4*240,3*120),(48,53,58))
for row in range(3):
 for i in range(4):contact.paste(board.crop((i*352+40,row*320+50+140,i*352+160,row*320+50+200)).resize((240,120),Image.Resampling.NEAREST),(i*240,row*120))
contact.save(D/'contact-detail-ENLARGED-from-2x.png')
# Evaluate real existing static descriptors under the same light, in hero-local output ROI.
rv=load('assets/earth/shadows/receiver_v2/manifest.json');fg=load('assets/earth/shadows/fangzhang_flat_v1/manifest.json')
fr=load('assets/earth/npc/fangzhang_v1/manifest.json');fa=np.array(Image.open(track(fr['texture'][6:])))[:,:,3]
ls=rv['casters']['lingyunzi'];la=np.array(Image.open(track(ls['shadow_texture']['path'][6:])))[:,:,3]
ts=rv['casters']['first_tree'];ta=np.array(Image.open(track(ts['shadow_texture']['path'][6:])))[:,:,3]
def existing_shadow(a,ref,slope,origin,world):
 bb=ref[1]-slope*ref[0];AA=np.array([[1+1.2*slope,-1.2],[1.55*slope,-.55]]);TT=np.array([1.2*bb,1.55*bb]);iv=np.linalg.inv(AA);hh,ww=a.shape;out=np.zeros(world.shape[:2])
 for dy in [-1,0,1]:
  for dx in [-1,0,1]:
   pp=(world+np.array([dx*.8,dy*.8])-origin-TT)@iv.T*4;ok=(pp[:,:,0]>=0)&(pp[:,:,1]>=0)&(pp[:,:,0]<ww)&(pp[:,:,1]<hh);co=np.stack((np.clip(pp[:,:,1],.5,hh-.5)-.5,np.clip(pp[:,:,0],.5,ww-.5)-.5));out+=map_coordinates(a.astype(float)/255,co,order=1,mode='nearest',prefilter=False)*ok*(2 if dx==0 else 1)*(2 if dy==0 else 1)/16
 return out*.25
external=[]
for cell in [[61,39],[61,37],[63,38]]:
 world=sampling_grid+np.array(cell)*[48,32]+[-16,-64]
 fang=existing_shadow(fa,fg['shadow']['reference_logical'],fg['shadow']['slope'],np.array([3040,1080]),world)
 tree=existing_shadow(ta,ts['shadow']['reference_logical'],ts['shadow']['slope'],np.array(ts['world_body_origin']),world)
 for li in range(4):
  ling=existing_shadow(la[:,li*512:(li+1)*512],ls['shadow']['reference_logical'],ls['shadow']['slope'],np.array(ls['world_body_origin']),world)
  for i,hero in enumerate(all_new):
   maximum=np.maximum.reduce([hero,fang,ling,tree]);over=1-(1-hero)*(1-fang)*(1-ling)*(1-tree);assert maximum.max()<=.25+1e-12
   external.append({'cell':cell,'s_id':17+i,'ling_phase':li,'hero_enabled':allows(cell),'overlap_d2_alpha_gt1_255':{k:int(((hero>1/255)&(a>1/255)).sum())for k,a in [('fang',fang),('ling',ling),('tree',tree)]},'max_composite_alpha':float(maximum.max()),'independent_over_alpha':float(over.max())})

assert all(sha(P/p)==h for p,h in inputs.items())
report={'status':'CPU_EXPERIMENT_ONLY_NOT_VISUALLY_APPROVED','preimplementation_plan_sha256':inputs[str((H/'PREIMPLEMENTATION_PLAN.md').relative_to(P))],'parameters':{'b0':B,'left_b':B-DELTA,'right_b':B+DELTA,'y_transition':[Y0,Y1],'invariant_t_blend':[TL,TR],'cast':[1.2,.55],'logical_blur':.8,'opacity':.25,'constant_across_phases':True},'proof':{'analytic_det_interval':[-.70984375,-.39015625],'numeric_det_minmax':[float(det.min()),float(det.max())],'roundtrip_200000_points_max_error':float(err),'numeric_jacobian_max_error':jerr,'boundary_epsilon_tests':boundary,'global_inverse':'t invariant; q_y strictly decreasing continuous for fixedt. Exactly one global inverse including transition, not multi-branch choice.','alpha_partition':'original bilinear full alpha restricted by unique source ownership; same-transform max and sum both exactly reconstruct. No independently filtered cut atlases.','nonlinear_fulltexel_interval_coverage_verified':True,'inputs_unchanged_after_run':True},'phases':phase_reports,'envelope':{'path':str((D/'full-four-phase-envelope.png').relative_to(P)),'sha256':sha(D/'full-four-phase-envelope.png'),'offset_logical':off.tolist(),'size_logical':(end-off).tolist(),'density':2,'positive_cells':int(env.sum()),'method':'interval bounds of every full-alpha texel plus .125bilinear support,1.8padding, visible and mapped proxy read-error boxes; one union all4 phases','eligible_integer_count':len(cells),'eligible_integer_cells':cells,'probes':[{'cell':c,'allows':allows(c)}for c in [[61,39],[63,41],[61,37],[63,38],[62,36],[66,35],[66,36],[61.6875,39.6875],[51,39],[67,45]]]},'performance':{'cpu_seconds_per_phase_old_and_new':timings,'native_not_measured':True,'texture_fetches_per_hero_pixel':9,'ownership_branches_need_not_add_texture_reads':True,'added_math':'invariant, clamp/interpolation, piecewise analytic inverse per9tap; existing single-affine inverse becomes nonlinear. Retain one hero output and external4caster max.','alternative_prebake':'possible future dedicated d4 shadow atlas generated from full alpha and frozen map, but not implemented or authorized for runtime here'},'external_max_with_current_static_descriptors':external,'input_sha256':inputs}
(D/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in ['parameters','proof','phases','envelope','performance']},indent=2))
