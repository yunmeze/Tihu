from pathlib import Path
from PIL import Image,ImageDraw
from scipy.signal import fftconvolve
import numpy as np,json
P=Path(__file__).resolve().parent;R=P.parents[1];E=R/'art_source/earth_e_47_48_context_edits_v1';D=R/'diagnostics'/P.name;D.mkdir(parents=True,exist_ok=True)
boxes={47:{'head':(133,59,187,108),'shoulder':(106,110,145,158),'waist_metal':(157,157,185,177),'rear_shin':(172,270,188,290),'rear_boot':(162,298,209,323),'front_shin':(132,286,148,315),'front_boot':(115,326,173,358)},48:{'head':(133,63,187,112),'shoulder':(106,114,145,162),'waist_metal':(158,159,185,177),'rear_shin':(102,275,118,290),'rear_boot':(71,303,129,345),'front_shin':(179,267,194,289),'front_boot':(192,284,246,324)}}
def rgb(im):
 a=np.array(im).astype(float)/255;return a[:,:,:3]*a[:,:,3:]+0.5*(1-a[:,:,3:])
def match(tar,patch,region):
 x0,y0,x1,y1=region; target=tar[y0:y1,x0:x1]; h,w=patch.shape[:2]; n=h*w*3
 if h>target.shape[0] or w>target.shape[1]:return -1,(0,0)
 pp=patch-patch.mean();corr=sum(fftconvolve(target[:,:,c],pp[::-1,::-1,c],mode='valid') for c in range(3))
 kern=np.ones((h,w));su=sum(fftconvolve(target[:,:,c],kern,mode='valid') for c in range(3));sq=sum(fftconvolve(target[:,:,c]**2,kern,mode='valid') for c in range(3));den=np.sqrt(np.maximum(sq-su**2/n,1e-9)*(pp**2).sum());score=corr/den;iy,ix=np.unravel_index(score.argmax(),score.shape);return float(score[iy,ix]),(x0+ix+w/2,y0+iy+h/2)
allres={}
for phase,bb in boxes.items():
 src=Image.open(E/str(phase)/'input-context.png').convert('RGBA');raw=Image.open(E/str(phase)/'mapped-UNMASKED.png').convert('RGBA');tar=rgb(raw);rows=[]
 for name,box in bb.items():
  patch=src.crop(box);center=np.array([(box[0]+box[2])/2,(box[1]+box[3])/2]);guess=center*1.30+[-48,-20]; radius=90; region=(max(0,int(guess[0]-radius)),max(0,int(guess[1]-radius)),min(512,int(guess[0]+radius)),min(512,int(guess[1]+radius)))
  best=(-1,None,None)
  for scale in np.arange(1.0,1.651,0.01):
   p=rgb(patch.resize((round(patch.width*scale),round(patch.height*scale)),Image.Resampling.BICUBIC));score,xy=match(tar,p,region)
   if score>best[0]:best=(score,xy,float(scale))
  rows.append({'name':name,'box':box,'source_center':center.tolist(),'matched_center':best[1],'local_diagnostic_scale':best[2],'ncc':best[0],'role':'fit' if name in ['head','shoulder','waist_metal'] else 'held_out'})
 train=[r for r in rows if r['role']=='fit'];x=np.array([r['source_center'] for r in train]);y=np.array([r['matched_center'] for r in train]);xc=x-x.mean(0);yc=y-y.mean(0);s=float((xc*yc).sum()/(xc**2).sum());t=y.mean(0)-s*x.mean(0)
 for r in rows:
  pred=np.array(r['source_center'])*s+t;res=np.array(r['matched_center'])-pred;r['predicted_center']=pred.tolist();r['residual_HD4']=res.tolist();r['residual_logical_norm']=float(np.linalg.norm(res)/4)
 allres[str(phase)]={'uniform_scale_source_to_mapped_raw':s,'translation_source_to_mapped_raw':t.tolist(),'rows':rows,'note':'Independent template scale searches are measurement only, never applied. Global no-rotation uniform scale+translation fitted head/shoulder/waist; legs held out. Full mapped raw uses previous fixed 512/raw-width registration.'}
 board=Image.new('RGBA',(1024,512),(128,128,128,255));board.alpha_composite(src);board.alpha_composite(raw,(512,0));dr=ImageDraw.Draw(board)
 for i,r in enumerate(rows):
  col=(255,80,80) if r['role']=='fit' else (40,255,170);b=r['box'];dr.rectangle(b,outline=col,width=1);dr.text((b[0],b[1]-10),str(i)+' '+r['name'],fill=col)
  q=np.array(r['matched_center'])+[512,0];p=np.array(r['predicted_center'])+[512,0];dr.ellipse((q[0]-3,q[1]-3,q[0]+3,q[1]+3),outline=col,width=2);dr.line((p[0]-4,p[1],p[0]+4,p[1]),fill='yellow');dr.line((p[0],p[1]-4,p[0],p[1]+4),fill='yellow');dr.line((p[0],p[1],q[0],q[1]),fill=col);dr.text((q[0]+4,q[1]),str(i),fill=col)
 board.save(D/f'{phase}-independent-anchor-measurements.png')
(P/'MEASUREMENTS.json').write_text(json.dumps(allres,indent=2)+'\n');print(json.dumps(allres,indent=2))
