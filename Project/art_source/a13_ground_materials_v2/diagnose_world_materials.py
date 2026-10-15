"""Offline semantic-mask candidate; immutable RGB sources, no runtime writes."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[2]; G=P/'diagnostics/art_source/a13-ground'; D=G/'world-material-v2'; D.mkdir(parents=True,exist_ok=True)
c=json.loads((P/'art_source/a13_ground_source/source-group-contract.json').read_text()); F,R=c['regions']
sel={'-406': 'Map/Res/FloorBig:406@60,36', '-577': 'Map/Res/FloorBig:577@56,40', '-608': 'Map/Res/FloorBig:608@58,40', '-587': 'Map/Res/FloorBig:587@58,42', '-579': 'Map/Res/FloorBig:579@60,38', '-595': 'Map/Res/FloorBig:595@60,40', '-581': 'Map/Res/FloorBig:581@60,42', '-407': 'Map/Res/FloorBig:407@62,36', '-580': 'Map/Res/FloorBig:580@62,38', '-588': 'Map/Res/FloorBig:588@62,40', '-604': 'Map/Res/FloorBig:604@62,42', '-399': 'Map/Res/FloorBig:399@64,36', '-398': 'Map/Res/FloorBig:398@64,38'}
raw_context=Image.open(P/'art_source/a13_ground_style_candidate_v1/raw.png').convert('RGB'); scale=480/raw_context.width
mapped=raw_context.transform((480,256),Image.Transform.AFFINE,(1/scale,0,0,0,1/scale,0),resample=Image.Resampling.BICUBIC)
# Visible source curb centerline manually read; uncertainty +/-3 source pixels.
source_line=[(-1,225),(192,97),(288,99),(332,126),(332,195),(244,256)]
# Generated curb centerline measured independently under frozen uniform fit.
generated_line=[(0,225.32),(192.8946,97.0064),(289.0623,97.28596),(334.070,126.919),(333.231,192.895),(242.94,256.0745)]
soil=Image.new('L',(480,256));ImageDraw.Draw(soil).polygon(source_line+[(0,256)],fill=255)
# Individual visible stone faces, read at native sampled context resolution.
# Binary technical extraction only; retained RGB is unchanged generated context.
stone_faces=[
 {'name':'left_long_face','polygon':[(0,222),(191,94),(194,100),(0,229)]},
 {'name':'top_cap','polygon':[(193,94),(289,94),(290,100),(193,101)]},
 {'name':'upper_right_cap','polygon':[(291,95),(337,124),(333,130),(287,102)]},
 {'name':'right_visible_upper','polygon':[(332,130),(335,131),(335,157),(332,158)]},
 {'name':'right_visible_lower','polygon':[(332,175),(335,174),(335,191),(332,194)]},
 {'name':'lower_right_face','polygon':[(332,191),(336,195),(246,256),(237,256)]}]
curb=Image.new('L',(480,256));cd=ImageDraw.Draw(curb)
for face in stone_faces:cd.polygon(face['polygon'],fill=255)
curb.save(D/'stone-only-mask.png')
# Display evidence; color is diagnostic overlay, never an artwork output.
proof=mapped.copy();pd=ImageDraw.Draw(proof)
for face in stone_faces:pd.line(face['polygon']+[face['polygon'][0]],fill=(255,0,255),width=1)
proof.resize((960,512),Image.Resampling.NEAREST).save(D/'stone-mask-boundary-proof.png')
sem=np.where(np.asarray(soil)>0,1,0).astype('uint8');sem[np.asarray(curb)>0]=2
# ID geometry derives from corresponding original placement, with marked curb uncertainty.
owners={o['key']:o for o in R['owners_in_draw_order']}
ID={}; RGB={}
for sid,k in sel.items():
 p=owners[k];x,y,w,h=p['world_rect'];b=(x-2688,y-1152,x-2688+w,y-1152+h)
 ID[int(sid)]=sem[b[1]:b[3],b[0]:b[2]].copy();RGB[int(sid)]=np.asarray(mapped.crop(b)).copy()
for sid in [-594,-586]:ID[sid]=np.ones((64,96),dtype='uint8')
# Preserve the original source alias evidence: both pure grass IDs use the same world field.
for sid in [-406,-399]:ID[sid]=np.zeros((64,96),dtype='uint8')
palette=np.array([[66,130,65],[190,157,108],[190,50,150]],dtype='uint8')
Image.fromarray(palette[sem]).save(D/'context-semantic-diagnostic.png')
textures={k:Image.open(P/f'art_source/a13_ground_materials_v2/{k}/raw.png').convert('RGB') for k in ['grass','soil']}
def render(region,period,mode="repeat"):
 x0,y0,x1,y1=region['complete_tile_context_bounds_xyxy'];h=y1-y0;w=x1-x0
 tex={k:np.asarray(v.resize((period,period),Image.Resampling.LANCZOS)) for k,v in textures.items()}
 yy,xx=np.indices((h,w)); u=(xx+x0)%period;v=(yy+y0)%period
 if mode=='mirror':
  u=np.where(((xx+x0)//period)%2==0,u,period-1-u);v=np.where(((yy+y0)//period)%2==0,v,period-1-v)
 mats={k:t[v,u] for k,t in tex.items()}
 out=mats['grass'].copy(); mask=np.zeros((h,w),dtype='uint8');cov=np.zeros((h,w),dtype='uint8')
 for p in region['owners_in_draw_order']:
  x,y,tw,th=p['world_rect'];x-=x0;y-=y0;sid=p['signed_id'];s=ID[sid];slot=out[y:y+th,x:x+tw];mask[y:y+th,x:x+tw]=s;cov[y:y+th,x:x+tw]+=1
  ground=mats['soil'][y:y+th,x:x+tw];slot[s==1]=ground[s==1]
  if sid in RGB:slot[s==2]=RGB[sid][s==2]
 Image.fromarray(mask).save(D/f'{region["name"]}-mask-index.png') if 'name' in region else None
 return Image.fromarray(out),cov
stats=[]
for period in [512,768,1024]:
 for label,reg in [('context20',R),('first143',F)]:
  out,cov=render(reg,period);out.save(D/f'{label}-period{period}.png')
  stats.append({'period_world_pixels':period,'scope':label,'placements':len(reg['owners_in_draw_order']),'uncovered_pixels':int((cov==0).sum()),'multiply_owned_pixels':int((cov>1).sum())})
# Native-scale source/current/generated-material comparison at requested central period.
x0,y0,x1,y1=F['complete_tile_context_bounds_xyxy'];a=Image.new('RGB',(x1-x0,y1-y0)); original={}
for f in c['minimum_first_screen_group']['frames']:
 at=Image.open(P/f['atlas_page'].replace('res://','')).convert('RGB');x,y,w,h=f['atlas_rect'];original[f['signed_id']]=at.crop((x,y,x+w,y+h))
for f in F['owners_in_draw_order']:
 x,y,w,h=f['world_rect'];a.paste(original[f['signed_id']],(x-x0,y-y0))
b=Image.open(D/'first143-period768.png')
board=Image.new('RGB',(a.width*2,a.height+24),(30,30,30));board.paste(a,(0,24));board.paste(b,(a.width,24));dr=ImageDraw.Draw(board);dr.text((6,6),'SOURCE 143 placements',fill='white');dr.text((a.width+6,6),'DIAGNOSTIC shared world grass/soil + narrow visible generated stone faces; period768',fill='white');board.thumbnail((2000,1000));board.save(D/'first143-comparison.jpg')
report={'status':'offline diagnostic, semantic ribbons require visual review; not runtime accepted','source_curb_centerline':source_line,'source_read_uncertainty_px':3,'generated_curb_centerline':generated_line,'stone_faces':stone_faces,'manual_stone_boundary_uncertainty_px':1,'curb_rgb':'unchanged uniform sampled generated context pixels, selected same-ID occurrence','soil_grass_boundary':'original source visible road centerline; retained stone is individually bounded visible generated faces','missing_ids':{'-594':3,'-586':1},'missing_semantics':'original images pure interior road soil; same world soil field; no synthetic curb','grass_aliases':[-406,-399],'mask_edge_warning':'binary face bounds are manually read +/-1 native px; right occluded stretch is excluded, no hidden stone reconstruction; inspect fringe before runtime','world_uv_origin':[0,0],'sampling':'raw uniformly resampled once to explicit period, integer modulo world coords; no per-tile RGB changes','tests':stats,'raw_hashes':{k:hashlib.sha256((P/f'art_source/a13_ground_materials_v2/{k}/raw.png').read_bytes()).hexdigest() for k in textures}}
(D/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(stats))

for label,reg in [('context20',R),('first143',F)]:
 out,_=render(reg,768,'mirror');out.save(D/f'{label}-period768-mirror.png')
 a=Image.open(D/f'{label}-period768.png');bd=Image.new('RGB',(a.width*2,a.height+24),(30,30,30));bd.paste(a,(0,24));bd.paste(out,(a.width,24));dd=ImageDraw.Draw(bd);dd.text((5,5),'repeat 768',fill='white');dd.text((a.width+5,5),'mirror-repeat 768 (sampling assisted)',fill='white');bd.thumbnail((2000,1000));bd.save(D/f'{label}-repeat-mirror.jpg')
