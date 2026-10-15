from pathlib import Path
import numpy as np,json,hashlib
from PIL import Image,ImageDraw
from scipy.ndimage import map_coordinates
P=Path(__file__).resolve().parents[2];D=P/'diagnostics/earth-e-idle-contact-projection-cpu-v1';read=lambda p:json.loads((P/p).read_text())
B=83.53125;DELTA=-3.96875;TL=-38.50625;TR=-29.36875
f=lambda t:-DELTA+2*DELTA*np.clip((t-TL)/(TR-TL),0,1)
def forward(p):
 t=1.55*p[...,0]-1.2*p[...,1];b=B+np.clip((p[...,1]-60)/16,0,1)*f(t);return p+(b-p[...,1])[...,None]*[1.2,1.55]
def jac(p):
 t=1.55*p[:,0]-1.2*p[:,1];fv=f(t);w=np.clip((p[:,1]-60)/16,0,1);fp=np.where((t>TL)&(t<TR),2*DELTA/(TR-TL),0);wp=np.where((p[:,1]>60)&(p[:,1]<76),1/16,0);bx=w*fp*1.55;by=wp*fv-w*fp*1.2
 return np.stack([np.stack([1+1.2*bx,1.2*(by-1)],-1),np.stack([1.55*bx,1+1.55*(by-1)],-1)],-2)
report=read('diagnostics/earth-e-idle-contact-projection-cpu-v1/report.json');old=read('art_source/earth_es_idle_shadow_study_v1/measurements.json')['directions']['e'];allim=np.array(Image.open(P/'assets/earth/hero/e_idle_v1/body.png'));ph=[]
for i in range(4):
 a=allim[:,i*512:(i+1)*512,3];y,x=np.nonzero(a>0);p=np.c_[(x+.5)/4,(y+.5)/4];q=forward(p);t=1.55*p[:,0]-1.2*p[:,1];sv=np.linalg.svd(jac(p),compute_uv=False);an=sv[:,0]/sv[:,1];opaque=a[y,x]>=128;high=opaque&(an>10);bridge=opaque&(t>TL)&(t<TR)&(p[:,1]>=60);transition=opaque&(p[:,1]>60)&(p[:,1]<76)
 box=lambda v:np.r_[v.min(0),v.max(0)].tolist() if len(v) else None
 boot=[]
 for roi in [(29,81,45,91),(41.5,73,51,80)]:
  inside=(p[:,0]>=roi[0])&(p[:,0]<roi[2])&(p[:,1]>=roi[1])&(p[:,1]<roi[3]);boot.append({'roi':roi,'alpha_positive_count':int(inside.sum()),'fullalpha_t_centers':[float(t[inside].min()),float(t[inside].max())],'bridge_positive_count':int((inside&(t>TL)&(t<TR)).sum()),'bridge_opaque_count':int((inside&bridge).sum())})
 alpha1=a[y,x]==1;ph.append({'source_id':9+i,'opaque_count':int(opaque.sum()),'transition_opaque_count':int(transition.sum()),'bridge_opaque_count':int(bridge.sum()),'high_anisotropy_source_bbox':box(p[high]),'high_anisotropy_projected_bbox':box(q[high]),'high_anisotropy_raw_y_rows':[int(y[high].min()),int(y[high].max())],'alpha1_count':int(alpha1.sum()),'allalpha_projected_bbox':box(q),'alpha1_projected_bbox':box(q[alpha1]),'boot_support':boot})
# Invariant error test: fixed read boxes expanded; no per-phase refitting.
pts=np.array([k['visible_bottom_edge_points_logical']for k in old['frames']]);errs=[]
for i in range(4):
 corners=pts[i,:,None,:]+np.array([[-1,-.75],[-1,.75],[1,-.75],[1,.75]])[None,:,:];delta=forward(corners)-corners;errs.append({'source_id':i+9,'max_errorbox_contact_displacement':float(np.linalg.norm(delta,axis=-1).max())})
# Re-render unchanged source body and available post-blur alpha at identical2x scale.
grid=np.stack(np.meshgrid((np.arange(352)+.5)/2,(np.arange(320)+.5)/2),-1)
def render(direction,phase,shadow):
 atlas=np.array(Image.open(P/f'assets/earth/hero/{direction}_idle_v1/body.png'));rgba=atlas[:,phase*512:(phase+1)*512];raw=grid*4;valid=(raw[:,:,0]<512)&(raw[:,:,1]<512);coords=np.stack((np.clip(raw[:,:,1],.5,511.5)-.5,np.clip(raw[:,:,0],.5,511.5)-.5));body=np.stack([map_coordinates(rgba[:,:,c].astype(float),coords,order=1,mode='nearest',prefilter=False)for c in range(4)],-1);body[:,:,3]*=valid;ba=body[:,:,3:]/255;bg=np.array([174,179,183])*(1-shadow[:,:,None])+np.array([.035,.045,.055])*255*shadow[:,:,None];return Image.fromarray(np.rint(body[:,:,:3]*ba+bg*(1-ba)).clip(0,255).astype('uint8'))
se=read('assets/earth/shadows/se_flat_v1/manifest.json')['projection'];ref=np.array(se['reference_logical']);s=se['slope'];bb=ref[1]-s*ref[0];A=np.array([[1+1.2*s,-1.2],[1.55*s,-.55]]);T=np.array([1.2*bb,1.55*bb]);iv=np.linalg.inv(A);a=np.array(Image.open(P/'assets/earth/hero/se_idle_v1/body.png'))[:,:512,3];sa=np.zeros((320,352))
for dy in [-1,0,1]:
 for dx in [-1,0,1]:
  pp=(grid+[dx*.8,dy*.8]-T)@iv.T*4;valid=(pp[:,:,0]>=0)&(pp[:,:,1]>=0)&(pp[:,:,0]<512)&(pp[:,:,1]<512);coords=np.stack((np.clip(pp[:,:,1],.5,511.5)-.5,np.clip(pp[:,:,0],.5,511.5)-.5));sa+=map_coordinates(a.astype(float)/255,coords,order=1,mode='nearest',prefilter=False)*valid*(2 if dx==0 else 1)*(2 if dy==0 else 1)/16*.25
es=np.load(D/'phase-9-alpha.npz')['new'][:320];ss=np.load(P/'diagnostics/earth-s-idle-contact-projection-cpu-v1/phase-17-alpha.npz')['new'];board=Image.new('RGB',(352*5,320));metrics={}
for i,(label,d,shadow) in enumerate([('SE13 unchanged','se',sa),('S17 approved','s',ss),('E9 CPU only','e',es),('S17 approved','s',ss),('SE13 unchanged','se',sa)]):
 tile=render(d,0,shadow);ImageDraw.Draw(tile).text((5,5),label,fill=(25,25,25));board.paste(tile,(352*i,0));y,x=np.nonzero(shadow>1/255);points=np.c_[(x+.5)/2,(y+.5)/2];axis=np.array([-.55,1.2]);axis/=np.linalg.norm(axis);perp=points@axis;metrics[label]={'visible_gt1_255_area_logical':len(x)/4,'visible_bbox':np.r_[points.min(0),points.max(0)].tolist(),'light_perp_width':float(perp.max()-perp.min()),'alpha_mass_logical':float(shadow.sum()/4),'distal_x_ge65_perp_width':float(np.ptp(perp[points[:,0]>=65])),'distal_x_ge65_area':int((points[:,0]>=65).sum())/4}
board.save(D/'se-s-e-s-se-same-scale-2x.png')
# Technical source overlay: source pixels are only displayed, never edited as assets.
over=Image.new('RGB',(512*4,512),(45,45,45))
for i in range(4):
 tile=Image.new('RGBA',(512,512),(45,45,45,255));tile.alpha_composite(Image.fromarray(allim[:,i*512:(i+1)*512]));tile=tile.convert('RGB');dr=ImageDraw.Draw(tile)
 for yy in [60,76]:dr.line((0,yy*4,512,yy*4),fill=(255,210,0),width=1)
 for tt in [TL,TR]:dr.line((((tt+1.2*60)/1.55*4,240),((tt+1.2*95)/1.55*4,380)),fill=(255,80,180),width=1)
 for roi in [(29,81,45,91),(41.5,73,51,80)]:dr.rectangle(tuple(v*4 for v in roi),outline=(80,230,220))
 dr.text((5,5),f'E{i+9}: yellow y60/76; pink t core limits',fill='white');over.paste(tile,(i*512,0))
over.save(D/'source-transition-and-boot-roi-4x.png')
out={'phases':ph,'readerror_contact':errs,'turn_comparison':metrics,'note':'Threshold1/255 is for visual comparison only, never envelope coverage or source deletion.'};(D/'support-and-turn-analysis.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
