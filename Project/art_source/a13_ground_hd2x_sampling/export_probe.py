from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[2];D=P/'diagnostics/art_source/a13-ground/hd2x-first-screen';D.mkdir(parents=True,exist_ok=True);B=P/'assets/scifi/environment/a13_ground_mirror_v2_candidate';m=json.loads((B/'registration.json').read_text());c=json.loads((P/'art_source/a13_ground_source/source-group-contract.json').read_text());R=c['regions'][1];owners={o['key']:o for o in R['owners_in_draw_order']};sel={'-406':'Map/Res/FloorBig:406@60,36','-577':'Map/Res/FloorBig:577@56,40','-608':'Map/Res/FloorBig:608@58,40','-587':'Map/Res/FloorBig:587@58,42','-579':'Map/Res/FloorBig:579@60,38','-595':'Map/Res/FloorBig:595@60,40','-581':'Map/Res/FloorBig:581@60,42','-407':'Map/Res/FloorBig:407@62,36','-580':'Map/Res/FloorBig:580@62,38','-588':'Map/Res/FloorBig:588@62,40','-604':'Map/Res/FloorBig:604@62,42','-399':'Map/Res/FloorBig:399@64,36','-398':'Map/Res/FloorBig:398@64,38'}
O=P/'assets/scifi/environment/a13_ground_hd2x_probe';O.mkdir(parents=True,exist_ok=True);entries=[]
ma=np.asarray(Image.open(B/'semantic-atlas.png'));st=np.asarray(Image.open(B/'stone-atlas.png'));bindings={b['signed_id']:b for b in m['bindings']};tex={n:{k:np.asarray(Image.open(P/f'art_source/a13_ground_materials_v2/{k}/raw.png').convert('RGB').resize((n,n),Image.Resampling.LANCZOS))for k in ['grass','soil']}for n in [256,512]};raw=Image.open(P/'art_source/a13_ground_style_candidate_v1/raw.png').convert('RGB');scale=960/raw.width;stone2=raw.transform((960,512),Image.Transform.AFFINE,(1/scale,0,0,0,1/scale,0),Image.Resampling.BICUBIC)
region=c['regions'][0];x0,y0,x1,y1=region['complete_tile_context_bounds_xyxy'];outputs={n:Image.new('RGB',((x1-x0)*2,(y1-y0)*2))for n in [256,512]}
for a in region['owners_in_draw_order']:
 x,y,w,h=a['world_rect'];sid=a['signed_id'];b=bindings[sid];bx,by,_,_=b['mask_rect'];mask=ma[by:by+h,bx:bx+w,0]
 for n in [256,512]:
  density=n//256;yy,xx=np.indices((h*density,w*density));u=(x*density+xx)%(n*2);v=(y*density+yy)%(n*2);u=np.where(u<n,u,2*n-1-u);v=np.where(v<n,v,2*n-1-v);mk=np.repeat(np.repeat(mask,density,0),density,1);rgb=tex[n]['grass'][v,u].copy();rgb[mk==127]=tex[n]['soil'][v,u][mk==127]
  if (mk==255).any():
   if density==1:curb=st[by:by+h,bx:bx+w,:3]
   else:
    o=owners[sel[str(sid)]];ox,oy,_,_=o['world_rect'];curb=np.asarray(stone2.crop(((ox-2688)*2,(oy-1152)*2,(ox-2688+w)*2,(oy-1152+h)*2)))
   rgb[mk==255]=curb[mk==255]
  tile=Image.fromarray(rgb)
  if density==1:tile=tile.resize((w*2,h*2),Image.Resampling.NEAREST)
  outputs[n].paste(tile,((x-x0)*2,(y-y0)*2))
  if n==512:
   out=O/f'tile-{a["cell"][0]}-{a["cell"][1]}.png';tile.convert('RGBA').save(out);entries.append({**a,'texture':'res://'+str(out.relative_to(P)),'texture_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'texture_size':[w*2,h*2],'draw_world_rect':[x,y,w,h]})
for n,im in outputs.items():im.save(D/f'first143-world256-raster{n}.png')
box=((2880-x0)*2,(1216-y0)*2,(3072-x0)*2,(1344-y0)*2);board=Image.new('RGB',(768,280),(25,25,25));dr=ImageDraw.Draw(board)
for i,n in enumerate([256,512]):board.paste(outputs[n].crop(box),(i*384,24));dr.text((i*384+3,5),'256 texture x2 nearest'if n==256 else'512 texture / SAME world period256',fill='white')
board.save(D/'same-world-period-two-raster-densities.png')
(D/'report.json').write_text(json.dumps({'status':'offline technical density comparison; no native or full-screen asset acceptance','logical_world_period':256,'baseline':'256 texel raster enlarged2 nearest','candidate':'immutable1254 raw uniformly LANCZOS to512,2texels/world unit; mirror world superperiod512','road_stone':'source context raw directly sampled960x512 at same uniform world fit, not old stone-atlas enlargement','mask_geometry':'exact nearest2 duplication of existing logical mask; no boundary shift or mask smoothing','scope':143,'output_size':outputs[512].size,'raw_unchanged':True},indent=2)+'\n')
print(outputs[512].size)

(O/'registration.json').write_text(json.dumps({'schema':'a13-ground-hd2x-probe-v1','status':'isolatedHDdiagnostic, not selected','placements':entries,'logical_world_period':256,'texture_texels_per_world_unit':2,'mirror_superperiod_world':512,'filter':'nearest in true2x raster','geometry':'same143 original rectangles and exact2 replicated semantic mask','outside_scope':'source; full terrain not accepted','source_alpha':'all these143 original floor pixels alpha255; no small semi-alpha frames in this scope'},indent=2)+'\n');print('registration',hashlib.sha256((O/'registration.json').read_bytes()).hexdigest())
