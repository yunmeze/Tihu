"""Authorized technical CPU preview, actual atlas alpha only; no generated art."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import map_coordinates
P=Path(__file__).resolve().parents[2];H=Path(__file__).parent;D=P/'diagnostics/earth-es-idle-shadow-study-v1';j=json.loads((H/'measurements.json').read_text());details={}
SCALE=2;W,HGT=176,224
y,x=np.indices((HGT*SCALE,W*SCALE));p0=np.stack(((x+.5)/SCALE,(y+.5)/SCALE),axis=0)
for direction in ['e','s']:
 r=j['directions'][direction];s=r['fixed_line']['slope'];b=r['fixed_line']['intercept'];A=np.array(r['fixed_line']['matrix_rows']);T=np.array(r['fixed_line']['translation_logical']);inv=np.linalg.inv(A);atlas=Image.open(P/f'assets/earth/hero/{direction}_idle_v1/body.png').convert('RGBA');board=Image.new('RGB',(W*SCALE*4,HGT*SCALE*3+45),(48,53,58));dr=ImageDraw.Draw(board);rows=[]
 for i,sid in enumerate(r['ids']):
  im=atlas.crop((i*512,0,(i+1)*512,512));a=np.array(im)[:,:,3];out=np.zeros((HGT*SCALE,W*SCALE))
  for iy in [-1,0,1]:
   for ix in [-1,0,1]:
    p=np.einsum('ij,jhw->ihw',inv,p0+np.array([ix*.8,iy*.8])[:,None,None]-T[:,None,None])*4;valid=(p[0]>=0)&(p[1]>=0)&(p[0]<512)&(p[1]<512);coords=np.stack((np.clip(p[1],.5,511.5)-.5,np.clip(p[0],.5,511.5)-.5));out+=map_coordinates(a.astype(float)/255,coords,order=1,mode='nearest',prefilter=False)*valid*(2 if ix==0 else 1)*(2 if iy==0 else 1)/16
  overlay=Image.fromarray(np.dstack([np.full(out.shape,9),np.full(out.shape,11),np.full(out.shape,14),np.rint(out*.25*255)]).astype(np.uint8),'RGBA')
  for row in range(3):
   tile=Image.new('RGBA',(W*SCALE,HGT*SCALE),(172,177,181,255));td=ImageDraw.Draw(tile)
   for gy in range(0,HGT,16):td.line((0,gy*SCALE,W*SCALE,gy*SCALE),fill=(158,164,170,255));td.text((2,gy*SCALE+2),str(gy),fill=(105,110,117,255))
   for gx in range(0,W,16):td.line((gx*SCALE,0,gx*SCALE,HGT*SCALE),fill=(158,164,170,255))
   if row==0:body=Image.open(P/f'art_source/earth_hero_{direction}_input_plan_v1/source-{sid}.png').convert('RGBA').resize((256,256),Image.Resampling.NEAREST)
   else:body=im.resize((256,256),Image.Resampling.LANCZOS)
   if row==2:tile=Image.alpha_composite(tile,overlay)
   tile.alpha_composite(body,(0,0));td=ImageDraw.Draw(tile)
   if row==2:
    td.line((0,b*SCALE,W*SCALE,(s*W+b)*SCALE),fill=(195,125,25,255),width=1)
    for point in r['frames'][i]['visible_bottom_edge_points_logical']:
     q=A@point+T;x1,y1=np.array(point)*SCALE;x2,y2=q*SCALE;td.line((x1,y1,x2,y2),fill=(220,30,30,255),width=1);td.ellipse((x1-2,y1-2,x1+2,y1+2),outline=(220,30,30,255));td.ellipse((x2-2,y2-2,x2+2,y2+2),outline=(10,135,55,255))
   td.text((5,5),f'{direction.upper()} {sid}: '+['ORIGINAL complete + checker','CANDIDATE actual atlas','CPU fixed cast; red=sole green=projected'][row],fill=(25,28,31,255));board.paste(tile.convert('RGB'),(i*W*SCALE,row*HGT*SCALE+45))
  bands=[]
  for threshold in [1,16,64,128,255]:
   yy,xx=np.nonzero(a>=threshold);lo=np.stack((xx,yy),1)/4-.125;hi=lo+.5;corners=np.stack([lo,np.stack((hi[:,0],lo[:,1]),1),hi,np.stack((lo[:,0],hi[:,1]),1)],1);q=corners@A.T+T;lower=q.min((0,1))-1.8;upper=q.max((0,1))+1.8;height=s*((xx+.5)/4)+b-(yy+.5)/4;imax=np.unravel_index(q[:,:,1].argmax(),q[:,:,1].shape);pix=imax[0]
   bands.append({'alpha_at_least':threshold,'texels':int(len(xx)),'projected_bounds_with_padding':np.r_[lower,upper].tolist(),'projected_height':float(upper[1]-lower[1]),'proxy_height_minmax':[float(height.min()),float(height.max())],'furthest_y_source_texel_xy':[int(xx[pix]),int(yy[pix])],'furthest_y_source_texel_alpha':int(a[yy[pix],xx[pix]])})
  rows.append({'source_id':sid,'bands':bands})
 dr.text((5,8),f'{direction.upper()} CPU proposal only / same 2x scale, no per-frame shift / cast(1.2,.55), opacity.25, blur.8 / fixed slope {s:.6f}',fill='white');dr.text((5,25),'FULL alpha retained. Orange is proxy line, not measured terrain. Original row retains original checker. Grid:16 logical px.',fill='white');board.save(D/f'{direction}-source-body-fixed-shadow-2x.png');details[direction]=rows
(H/'alpha-envelope-attribution.json').write_text(json.dumps(details,indent=2)+'\n');print(json.dumps(details,indent=2))
