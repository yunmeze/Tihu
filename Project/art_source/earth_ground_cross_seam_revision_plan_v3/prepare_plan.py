from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
import numpy as np
O=Path(__file__).parent;P=O.parents[1];D=P/'art_source';W=(2400,1296,3168,1872);SZ=(1536,1152);inputs={}
def bind(rel):
 p=P/rel;inputs[rel]=hashlib.sha256(p.read_bytes()).hexdigest();return p
def read(rel):return json.loads(bind(rel).read_text())
map=read('data/maps/A13.json');mf=read('assets/original/manifest.json');reg=read('assets/earth/environment/ground_plate_v4/registration.json');pages={};src=Image.new('RGBA',(768,576));records=[]
for i,c in enumerate(map['cells']):
 if not c[0]:continue
 x,y=divmod(i,100);pk='Map/Res/FloorBig' if c[0]<0 else 'Map/Res/FloorSmall';f=mf['packs'][pk]['frames'][str(abs(c[0]))];wx=x*48+f['crop'][0];wy=y*32+f['crop'][1];a,b,w,h=f['rect']
 if wx>=W[2] or wy>=W[3] or wx+w<=W[0] or wy+h<=W[1]:continue
 page=mf['packs'][pk]['pages'][f['page']]['file'][6:]
 if page not in pages:pages[page]=Image.open(bind(page)).convert('RGBA')
 im=pages[page].crop((a,b,a+w,b+h));src.paste(im,(wx-W[0],wy-W[1]));records.append({'key':f'{pk}:{abs(c[0])}@{x},{y}','cell':[x,y],'source_cell':c,'signed_floor_id':c[0],'crop':f['crop'],'original':f['original'],'ignored_offset':f['offset'],'source_rect_world':[wx,wy,wx+w,wy+h],'floor_pass':0,'sort_y':y,'stable_source_order':i,'source_rgba_sha256':hashlib.sha256(im.tobytes()).hexdigest(),'alpha_extrema':im.getchannel('A').getextrema()})
src.save(O/'INPUT_source_native.png');source2=src.resize(SZ,Image.Resampling.NEAREST);source2.save(O/'INPUT_source_2x_NEAREST.png')
old=Image.open(bind('assets/earth/environment/ground_plate_v4/plate.png')).convert('RGBA');south=Image.open(bind('art_source/earth_south_ground_candidate_v1/raw.png')).convert('RGBA');context=source2.copy();context.paste(south,(0,224));context.paste(old,(192,-672));context.save(O/'INPUT_ONLY_existing_art_context.png')
# Intended center is straight from old source upper kink to south source kink; no fit to erroneous art.
# Local coordinates = oldraw+(192,-672) = southraw+(0,224).
sp=[(1238,72),(1238,100),(88,862),(80,994),(0,1048)]
cp=[(1241,72),(1241,95),(1057,224),(970,288),(886,350),(872,352),(102,898),(94,998),(0,1066)]
mask=Image.new('L',SZ);d=ImageDraw.Draw(mask);d.polygon(sp+cp[::-1],fill=255);d.line(sp,fill=255,width=32,joint='curve');d.line(cp,fill=255,width=40,joint='curve');d.rectangle((72,928,128,980),fill=255)
# Hard top cut: both old/source have straight vertical curb here; no permission above joint.
d.rectangle((0,0,1535,71),fill=0)
oldkeys={f'Map/Res/FloorBig:{f}@{x},{y}' for f,x,y in [(604,62,42),(581,60,42),(604,60,44),(581,58,44),(588,62,40)]}
allowed=Image.new('L',SZ);ad=ImageDraw.Draw(allowed)
for q in records:
 if q['key'] in oldkeys or q['source_rect_world'][1]>=1472:
  x0,y0,x1,y1=q['source_rect_world'];ad.rectangle((2*(x0-W[0]),2*(y0-W[1]),2*(x1-W[0])-1,2*(y1-W[1])-1),fill=255)
ma=np.array(mask);allow=np.array(allowed);outside=(ma>0)&(allow==0);assert not outside.any(),f'mask would touch {outside.sum()} unauthorized pixels'
mask.save(O/'PROPOSED_fixed_replace_mask.png');Image.fromarray(255-ma).save(O/'PROTECT_unchanged_pixels.png')
unc=Image.new('L',SZ);ImageDraw.Draw(unc).line(sp,fill=255,width=13,joint='curve');unc.save(O/'SOURCE_center_uncertainty_NOT_ART.png')
# Fixed geometry guide only, not final RGB. 8raw nominal normal width with +/-6raw source-read uncertainty.
guide=Image.new('L',SZ);ImageDraw.Draw(guide).line(sp,fill=255,width=8,joint='curve');guide.save(O/'PROPOSED_curb_footprint_NOT_ART.png')
owner_scope=[];rb={x['key']:x for x in reg['owners']}
for q in records:
 x0,y0,x1,y1=q['source_rect_world'];box=[2*(x0-W[0]),2*(y0-W[1]),2*(x1-W[0]),2*(y1-W[1])];n=int(np.count_nonzero(np.array(mask.crop(box))))
 if n:
  z=dict(q,mask_pixels=n,raw_owner_rect=box,status='explicit_old_reopen_proposal' if q['key'] in oldkeys else 'new_south_candidate_only')
  if q['key'] in rb:
   t=rb[q['key']]['texture'][6:];bind(t);z['preserved_original_texture']=t;z['preserved_original_texture_sha256']=inputs[t]
  owner_scope.append(z)
over=context.convert('RGB');over.paste(Image.new('RGB',SZ,(240,30,160)),(0,0),mask.point(lambda v:80 if v else 0));dr=ImageDraw.Draw(over);dr.line((0,352,1536,352),fill='yellow',width=2);dr.line(sp,fill='cyan',width=2)
for q in owner_scope:
 if q['status'].startswith('explicit'):
  b=q['raw_owner_rect'];dr.rectangle(b,outline='orange',width=2);dr.text((b[0]+2,max(0,b[1])+2),q['key'].split(':')[-1],fill='white')
over.save(O/'SCOPE_ONLY_not_art.png')
# Separate exact patch evidence for every touched complete owner, even where context crops its bounds.
(O/'owner_masks').mkdir(exist_ok=True)
for q in owner_scope:
 name=q['key'].split(':')[-1].replace('@','_').replace(',','_')+'.png';mask.crop(q['raw_owner_rect']).save(O/'owner_masks'/name);q['owner_mask']='owner_masks/'+name
for p in ['diagnostics/art_source/earth-ground-seam-independent-audit/REPORT.md','diagnostics/art_source/earth-ground-seam-independent-audit/identity-checks.json','art_source/earth_ground_plate_source_v1/source-layout-contract.json','art_source/earth_south_ground_local_revision_plan_v2/PLAN.md','docs/EARTH_ART_BIBLE_V1.md']:bind(p)
result={'status':'INPUT/MASK PROPOSAL ONLY. No image generation or final assembly. Parent must approve five-old-owner reopen and source-faithful curb width convention.','world_xyxy':W,'native_pixels':SZ,'density':2,'mapping':{'world':'[2400,1296]+localraw/2','from_old_raw':'localraw=oldraw+(192,-672)','from_south_raw':'localraw=southraw+(0,224)','interface_local_y':352},'source_center_polyline_localraw':sp,'source_center_polyline_world':[[2400+x/2,1296+y/2]for x,y in sp],'source_uncertainty_raw':6,'corner_uncertainty_raw':8,'candidate_edge_uncertainty_raw':4,'candidate_cover_polyline_localraw':cp,'fixed_mask_pixels':int((ma>0).sum()),'fixed_mask_bbox':mask.getbbox(),'old_reopen_keys':sorted(oldkeys),'owners':owner_scope,'protected_pixel_count':int((ma==0).sum()),'protected_rules':['All nonmask RGB exact to original v4 or south raw by context provenance','Old plate and owner assets never overwritten; create versioned candidates only','Other road edge, road center, cap and distant grass remain protected','Original sourcecell/alpha/order unchanged; no frameID scope replacement','Debris pool remains independent and is not in any input art'], 'context_provenance':[{'source':'source native nearest2x','role':'base reference only; uncovered northwest area immutable'},{'source':'south candidate raw','paste_local':[0,224],'operation':'exact copy'},{'source':'old v4 plate','paste_local':[192,-672],'operation':'exact copy, later layer wins overlap'}],'generation_gate':'One local generation after explicit approval; requested native1536x1152 at2x. If actual output differs, reject, retain raw, no automatic resample/retry. Fixed mask applied only after visual geometry acceptance.','assembly_future':'Binary fixed-mask replace by corresponding generated texel at same local coordinate; outside exact original provenance. No feathering/color matching. Complete owners exported atomically into a separate candidate version; no production change authorized.'}
(O/'PLAN.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');(O/'INPUT_SHA256.json').write_text(json.dumps(inputs,indent=2)+'\n');print(json.dumps({'mask':result['fixed_mask_pixels'],'old':[(q['key'],q['mask_pixels'])for q in owner_scope if q['status'].startswith('explicit')],'new':[(q['key'],q['mask_pixels'])for q in owner_scope if not q['status'].startswith('explicit')]}))
