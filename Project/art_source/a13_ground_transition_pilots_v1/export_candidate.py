"""Reproduce three bounded source-driven mask pilots and immediate-neighbor native package."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageFilter
D=Path(__file__).resolve().parent;P=D.parents[1]
B=P/'assets/scifi/environment/a13_ground_mirror_v2_candidate'
O=P/'assets/scifi/environment/a13_ground_transition_pilots_v1';O.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
m=json.loads((B/'registration.json').read_text());packs=json.loads((P/'assets/original/manifest.json').read_text())['packs'];inv=json.loads((P/'art_source/a13_ground_full_map_plan/source-inventory.json').read_text());mp=json.loads((P/'data/maps/A13.json').read_text());specs=[json.loads((D/f'{s}-contract.json').read_text())for s in ['minus405','minus407','385']]
tex={k:np.asarray(Image.open(P/f'art_source/a13_ground_materials_v2/{k}/raw.png').convert('RGB').resize((256,256),Image.Resampling.LANCZOS),dtype=float)for k in ['grass','soil']};ma=np.asarray(Image.open(B/'semantic-atlas.png'));st=np.asarray(Image.open(B/'stone-atlas.png'));bindings={b['signed_id']:b for b in m['bindings']};oldscope={(a['signed_id'],tuple(a['cell']))for a in m['placements']};grass=set(inv['classifications']['grass-base']['ids']);soil=set(inv['classifications']['tan-earth-gravel-base']['ids']);curb=set(inv['classifications']['narrow-stone-curb-road-edge']['ids']);alias={-607:-579,-597:-588};images={};pages={};entries=[];pilots=[]
def source(sid):
 if sid not in images:
  pk=packs['Map/Res/FloorBig'if sid<0 else'Map/Res/FloorSmall'];fr=pk['frames'][str(abs(sid))];pg=pk['pages'][fr['page']]['file'];x,y,w,h=fr['rect']
  if pg not in pages:pages[pg]=Image.open(P/pg[6:]).convert('RGBA')
  images[sid]=pages[pg].crop((x,y,x+w,y+h))
 return images[sid]
weights={}
for s in specs:
 sid=s['id'];im=source(sid);a=np.asarray(im.convert('RGB').filter(ImageFilter.GaussianBlur(1)),dtype=float)
 def anchor(rs):return np.concatenate([a[y0:y1,x0:x1].reshape(-1,3)for x0,y0,x1,y1 in rs]).mean(axis=0)
 g=anchor(s['grass_rects'])
 if s['soil_rects']:
  v=anchor(s['soil_rects'])-g;w=np.rint(np.clip(((a-g)*v).sum(axis=2)/(v*v).sum(),0,1)*255).astype('uint8')
 else:w=np.zeros(a.shape[:2],dtype='uint8')
 slug=str(sid).replace('-','minus');out=O/f'{slug}-soil-weight.png';Image.fromarray(w).save(out);weights[(sid,tuple(s['cell']))]=w
 pilots.append({'signed_id':sid,'cell':s['cell'],'world_rect':s['owner']['world_rect'],'context_bounds':s['world_context_bounds'],'weight_texture':'res://'+str(out.relative_to(P)),'weight_sha256':sha(out),'source_alpha_sha256':hashlib.sha256(np.asarray(im)[:,:,3].tobytes()).hexdigest(),'read_uncertainty_px':s['line_uncertainty_px']})
for order,cell in enumerate(mp['cells']):
 sid=cell[0]
 if not sid:continue
 cx,cy=divmod(order,mp['height']);x,y=cx*48,cy*32;im=source(sid);w,h=im.size
 if not any(x<b[2]and y<b[3]and x+w>b[0]and y+h>b[1]for b in [s['world_context_bounds']for s in specs]):continue
 raw=np.asarray(im);mode=None;bind=None;status='source_neighbor'
 if sid in grass:mode=np.zeros((h,w),dtype='uint8');status='known_grass_base'
 elif sid in soil:mode=np.full((h,w),127,dtype='uint8');status='known_soil_base'
 elif sid in curb and(sid in bindings or sid in alias):bind=bindings[alias.get(sid,sid)];status='known_curb_or_exact_alias'
 elif(sid,(cx,cy))in oldscope:bind=bindings[sid];status='existing143_candidate'
 if bind:
  bx,by,bw,bh=bind['mask_rect'];mode=ma[by:by+bh,bx:bx+bw,0]
 yy,xx=np.indices((h,w));u=(x+xx)%512;v=(y+yy)%512;u=np.where(u<256,u,511-u);v=np.where(v<256,v,511-v);base=raw.copy()
 if mode is not None:
  rgb=tex['grass'][v,u].copy();rgb[mode==127]=tex['soil'][v,u][mode==127]
  if bind:rgb[mode==255]=st[by:by+h,bx:bx+w,:3][mode==255]
  base=np.dstack([rgb.astype('uint8'),raw[:,:,3]])
 candidate=base.copy();weight=weights.get((sid,(cx,cy)))
 if weight is not None:
  t=weight.astype(float)/255;rgb=np.rint(tex['grass'][v,u]*(1-t[...,None])+tex['soil'][v,u]*t[...,None]).astype('uint8');candidate=np.dstack([rgb,raw[:,:,3]])
 paths={}
 for variant,rgba in [('base',base),('pilot',candidate)]:
  p=O/f'{variant}-{cx}-{cy}.png';Image.fromarray(rgba).save(p);paths[variant]={'texture':'res://'+str(p.relative_to(P)),'sha256':sha(p)};assert np.array_equal(rgba[:,:,3],raw[:,:,3])
 entries.append({'key':f'Map/Res/{"FloorBig"if sid<0 else"FloorSmall"}:{abs(sid)}@{cx},{cy}','signed_id':sid,'cell':[cx,cy],'source_cell':cell,'stable_source_order':order,'world_rect':[x,y,w,h],'status':status,'is_pilot':weight is not None,'variants':paths})
r={'schema':'a13-three-transition-neighbor-native-v1','status':'isolated diagnostic only; parent accepted radius1 working masks pending native','map':'A13','placements':entries,'pilots':pilots,'variants':{'source':'all original floor','base':'new known base/curb in exact neighbor scope; pilot transitions remain pre-pilot','pilot':'same base plus exactly three radius1 masks'},'outside_scope':'original source; do not also enable old143 or fullmap renderer','sampling':{'world_origin':[0,0],'material_period':[256,256],'mode':'mirror-repeat','superperiod':[512,512],'filter':'nearest','derivation':'whole immutable material raw uniformly LANCZOS resized256 before nearest world sampling','address':'i=floor(world_pixel); r=posmod(i,512); texel=r if r<256 else 511-r'},'alpha':'original source alpha byte-identical for every output texel, including +385 alpha240 edge','classification':'manual seeds per source tile; radius1 classifier input only; weights mix material RGB, source/raw RGB unmodified','geometry':'original cell rectangle, stable draw order, flags and roads unchanged; boundary weights are artistic inferred material selection, not pixelwise semantic equivalence','limitations':['Only three representative instances; other27 transition IDs not inferred.','Source neighbors and isolated scope outer edges remain visible; do not claim fullmap approval.','Manual approximate read lines do not force masks. Small fragmented islands simplified with explicit approval.','No runtime or native acceptance yet.'],'materials_registration_sha256':sha(B/'registration.json'),'source_map_sha256':sha(P/'data/maps/A13.json')}
assert len({e['key']for e in entries})==len(entries);assert sum(e['is_pilot']for e in entries)==3
dump(O/'registration.json',r);print(json.dumps({'placements':len(entries),'pilots':3,'registration_sha256':sha(O/'registration.json'),'alpha_preserved':True}))
