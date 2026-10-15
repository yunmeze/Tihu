"""Reproducible original round-shrub source study; no generated art/runtime edits."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
mp=json.loads((P/'data/maps/A13.json').read_text());manifest=json.loads((P/'assets/original/manifest.json').read_text());pack=manifest['packs']['Map/Res/Plant'];mh=mp['height']
source_path=P.parent/pack['source'];assert sha(source_path)==pack['source_sha256']
map_source_path=P.parent/mp['source'];assert sha(map_source_path)==mp['sourceSha256']
page_path=P/pack['pages'][0]['file'][6:];page=Image.open(page_path).convert('RGBA');assert sha(page_path)==pack['pages'][0]['sha256']
assert pack['nativeAnimation'] is False
frame_ids=[143,144,145,146];tiles={};frames=[]
for i in frame_ids:
 f=pack['frames'][str(i)];ax,ay,aw,ah=f['rect'];tile=page.crop((ax,ay,ax+aw,ay+ah));tiles[i]=tile
 full=Image.new('RGBA',f['original']);full.paste(tile,tuple(f['crop']))
 assert hashlib.sha256(full.tobytes()).hexdigest()==f['rgba_sha256']
 assert f['format']=='BMP' and f['gifFrames']==1
 name=f'source-{i}.png';full.save(O/name)
 frames.append({'id':i,'frame':f,'extracted_full_canvas':name,'png_sha256':sha(O/name)})
all_owners=[]
for x in range(mp['width']):
 for y in range(mh):
  cell=mp['cells'][x*mh+y]
  if cell[2]==2 and cell[3] in frame_ids:all_owners.append((x,y,int(cell[3]),cell))
lookup={(x,y):(i,c)for x,y,i,c in all_owners};claimed=set();groups=[];selected=None
camera=np.array([61.,39.]);viewport=np.array([1024.,768.]);screen_origin=viewport*np.array([.5,.54])-camera*np.array([48,32])
for cx,by,idx,_ in all_owners:
 if idx!=145:continue
 cells=[(cx,by-3),(cx-1,by),(cx,by),(cx+1,by)];owners=[]
 for i,(x,y)in zip(frame_ids,cells):
  assert (x,y) in lookup and lookup[(x,y)][0]==i
  c=lookup[(x,y)][1];assert c[1]==(0 if i==143 else -1);claimed.add((x,y))
  f=pack['frames'][str(i)];w,h=tiles[i].size;wx=x*48+f['crop'][0];wy=y*32+32-f['original'][1]+f['crop'][1]
  owners.append({'key':f'Plant:{i}@{x},{y}','frame_id':i,'cell':[x,y],'source_cell':c,
   'flag':c[1],'layer':1,'sort_y':y,'stable_source_order':x*mh+y,
   'sort_tuple':[1,y,x*mh+y],'world_rect':[wx,wy,w,h],
   'native_source_offset':f['sourceOffset'],'native_source_bytes':f['sourceBytes'],
   'source_map_byte_offset':mp['cellByteOffsets'][x*mh+y] if isinstance(mp.get('cellByteOffsets'),list) else None,
   'atlas_page':pack['pages'][f['page']]['file'],'atlas_rect':f['rect'],'original_canvas':f['original'],'crop':f['crop']})
 x0=min(v['world_rect'][0]for v in owners);y0=min(v['world_rect'][1]for v in owners)
 x1=max(v['world_rect'][0]+v['world_rect'][2]for v in owners);y1=max(v['world_rect'][1]+v['world_rect'][3]for v in owners)
 im=Image.new('RGBA',(x1-x0,y1-y0));labels=np.zeros((y1-y0,x1-x0),np.uint8)
 for j,v in enumerate(owners):
  x,y,w,h=v['world_rect'];a=tiles[v['frame_id']];im.alpha_composite(a,(x-x0,y-y0))
  sub=labels[y-y0:y-y0+h,x-x0:x-x0+w];sub[np.asarray(a)[:,:,3]>0]=j+1
 pixel_sha=hashlib.sha256(im.tobytes()).hexdigest();screen=np.array([x0,y0])+screen_origin
 intersection=np.maximum(0,np.minimum(screen+[im.width,im.height],viewport)-np.maximum(screen,0))
 visible=bool(np.all(intersection>0));full=visible and bool(np.all(screen>=0) and np.all(screen+[im.width,im.height]<=viewport))
 g={'center_owner_cell':[cx,by],'owners_in_draw_order':owners,'world_bounds_xyxy':[x0,y0,x1,y1],
    'composite_size':list(im.size),'rgba_sha256':pixel_sha,'nominal_first_screen':{'screen_top_left':screen.tolist(),'intersection_size':intersection.tolist(),'visibility':'full' if full else ('partial'if visible else 'outside')}}
 groups.append(g)
 if (cx,by)==(57,38):selected=(g,im,labels)
assert len(all_owners)==32 and len(groups)==8 and len(claimed)==32
assert len({g['rgba_sha256']for g in groups})==1
assert selected is not None
g,im,labels=selected;im.save(O/'source-composite.png');a=np.asarray(im)
rois=[]
for name,b in [('right_external_dither',[120,46,124,71]),('lower_external_dither',[40,100,95,105])]:
 x,y,X,Y=b;t=a[y:Y,x:X];m=t[:,:,3]>0;values=t[m];assert np.all(values==[8,0,0,255]);yy,xx=np.where(m)
 rois.append({'id':name,'xyxy_exclusive':b,'rgba':[8,0,0,255],'nontransparent_pixels':len(values),
  'centroid_pixel_center':[float((xx+x+.5).mean()),float((yy+y+.5).mean())],
  'checker_parity_counts':np.bincount((xx+x+yy+y)%2,minlength=2).tolist(),
  'meaning':'exposed source checker near silhouette; not a complete separable cast or an independently calibrated light vector'})
leaf_samples=[]
for x,y in [(41,98),(65,99),(88,99)]:
 rgba=a[y,x].tolist();assert rgba[3]==255 and rgba[1]>rgba[0] and rgba[1]>rgba[2]
 leaf_samples.append({'pixel_index':[x,y],'rgba':rgba,'lower_texel_edge':[x+.5,y+1],
 'world_lower_edge':[g['world_bounds_xyxy'][0]+x+.5,g['world_bounds_xyxy'][1]+y+1],
 'meaning':'visible green lower-foliage edge; not woody root or proof of physical contact'})
# Native-size first-screen reconstruction of original scenery only. No runtime or CUA.
pages={};scene=Image.new('RGBA',(1024,768),(32,41,31,255));entries=[]
def get_page(path):
 if path not in pages:pages[path]=Image.open(P/path[6:]).convert('RGBA')
 return pages[path]
def draw_entry(pn,idx,wx,wy,top=0,use_offset=False):
 pk=manifest['packs'][pn];f=pk['frames'].get(str(idx))
 if not f:return
 ax,ay,w,h=f['rect'];dx=wx+f['crop'][0]+(f['offset'][0]if use_offset else 0)+screen_origin[0];dy=wy+top+f['crop'][1]+(f['offset'][1]if use_offset else 0)+screen_origin[1]
 if dx>=1024 or dy>=768 or dx+w<=0 or dy+h<=0:return
 tile=get_page(pk['pages'][f['page']]['file']).crop((ax,ay,ax+w,ay+h));scene.alpha_composite(tile,(round(dx),round(dy)))
group_names={1:'Map/Res/Debris',2:'Map/Res/Plant',3:'Map/Res/Wall',4:'Map/Res/Building',5:'Map/Res/Dynamic',8:'Data4'}
for x in range(mp['width']):
 for y in range(mh):
  c=mp['cells'][x*mh+y];fid=int(c[0]);kind=int(c[2]);idx=int(c[3])
  if fid:draw_entry('Map/Res/FloorBig'if fid<0 else'Map/Res/FloorSmall',abs(fid),x*48,y*32)
  if idx>0 and kind in group_names:
   layer=0 if c[1]in[1,-2]else(2 if c[1]==2 else 1);entries.append((layer,y,x*mh+y,group_names[kind],55 if kind==8 else idx,x*48,y*32,kind))
for nidx,n in enumerate(mp['npcs']):entries.append((1,n['y'],mp['width']*mh+nidx,'Npc',1+n['appearance']*12+n['direction']*4,n['x']*48,n['y']*32,7))
for _,_,_,pn,idx,x,y,kind in sorted(entries):
 f=manifest['packs'][pn]['frames'].get(str(idx))
 if f:draw_entry(pn,idx,x,y,0 if kind==7 else(-52 if kind==8 else 32-f['original'][1]),kind==7)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18);small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
d=ImageDraw.Draw(scene)
for gg in groups:
 if gg['nominal_first_screen']['visibility']=='outside':continue
 x,y=gg['nominal_first_screen']['screen_top_left'];d.rectangle((x,y,x+124,y+105),outline=(0,255,230,255),width=2);d.text((max(2,x),max(25,y-20)),str(gg['center_owner_cell']),font=small,fill=(255,255,255,255))
d.rectangle((0,0,1024,25),fill=(20,25,20,235));d.text((7,3),'Original scenery, camera61,39 / 1024x768 / marked shrub groups; offline sampling, no hero',font=small,fill=(255,255,255,255));scene.convert('RGB').save(O/'first-screen-source-context.jpg',quality=94)
# Integration board, original colors and explicit owner map kept separate.
board=Image.new('RGB',(1400,1080),(232,236,237));bd=ImageDraw.Draw(board)
bd.text((18,14),'A13 ROUND SHRUB / Plant143-146 / four simultaneous pieces, not animation',fill=(20,25,30),font=font)
bg=Image.new('RGBA',im.size,(105,117,98,255));bg.alpha_composite(im)
board.paste(bg.resize((620,525),Image.Resampling.NEAREST).convert('RGB'),(20,90))
bd.text((20,58),'Original composite124x105 at5x; no visible woody root',fill=(20,25,30),font=font)
colors=np.array([[105,117,98],[246,190,60],[90,170,245],[230,110,170],[90,210,135]],np.uint8)
owner_rgb=colors[labels];board.paste(Image.fromarray(owner_rgb).resize((620,525),Image.Resampling.NEAREST),(740,90));bd.text((740,58),'Owner labels on original alpha; preserve depth ordering',fill=(20,25,30),font=font)
for roi in rois:
 x,y,X,Y=roi['xyxy_exclusive'];bd.rectangle((20+x*5,90+y*5,20+X*5-1,90+Y*5-1),outline=(20,235,255),width=2)
for q in leaf_samples:
 x,y=q['lower_texel_edge'];bd.ellipse((20+x*5-4,90+y*5-4,20+x*5+4,90+y*5+4),outline=(255,160,30),width=2)
bd.text((20,632),'Cyan: exposed checker. Orange: leaf edges, NOT roots. Below: separate canvases bottom-aligned.',fill=(20,25,30),font=small)
for j,i in enumerate(frame_ids):
 full=Image.open(O/f'source-{i}.png').convert('RGBA');canvas=Image.new('RGBA',(48,96),(105,117,98,255));canvas.alpha_composite(full,(0,96-full.height))
 board.paste(canvas.resize((144,288),Image.Resampling.NEAREST).convert('RGB'),(20+j*155,700));bd.text((20+j*155,673),f'{i} / {full.width}x{full.height}',font=small,fill=(20,25,30))
lines=['Selected group: center owner(57,38)', '143 @57,35 sort(1,35,5735)', '144 @56,38 sort(1,38,5638)', '145 @57,38 sort(1,38,5738)', '146 @58,38 sort(1,38,5838)', 'Draw origin: local(41,73); not a root', 'All8 groups: (33,62),(39,56),(40,69),(46,63),', '(51,44),(57,38),(58,51),(64,45)', 'Viewport-contained:57,38 and64,45;', '51,44 left-clipped;58,51 bottom-clipped.', 'Single generated whole bush -> four owner pieces', '+ one separate shadow is technically possible.', 'Actual new root/contact and occlusion need new review.']
for j,line in enumerate(lines):bd.text((740,676+j*25),line,font=small,fill=(20,25,30))
bd.text((20,1027),'Do not erase dark RGB globally: checker-like dark pixels also occur throughout the foliage.',font=font,fill=(20,25,30))
board.save(O/'source-integration-board.png')
contract={'schema':'a13-original-round-shrub-source-study-v1','status':'source research only; no generated candidate or runtime integration',
 'inputs':{'map':{'path':'data/maps/A13.json','sha256':sha(P/'data/maps/A13.json')},'native_map':{'path':'../'+mp['source'],'sha256':sha(map_source_path)},'manifest':{'path':'assets/original/manifest.json','sha256':sha(P/'assets/original/manifest.json')},'plant_container':{'path':'../'+pack['source'],'sha256':sha(source_path)},'atlas':{'path':str(page_path.relative_to(P)),'sha256':sha(page_path)},'renderer':{'path':'scripts/world_view.gd','sha256':sha(P/'scripts/world_view.gd')},'project_config':{'path':'project.godot','sha256':sha(P/'project.godot')}},
 'frames':frames,'family':{'frame_ids':frame_ids,'kind':2,'owner_count':32,'instance_count':8,'complete_instances':8,'orphans':[],'duplicate_assignments':0,'all_composite_rgba_equal':True,'animation':{'nativeAnimation':False,'gifFrames_each':1,'phase_count':1,'reason':'kind2 does not advance frame in world_view; four spatial pieces coexist'}},
 'groups':groups,'selected_group_center':[57,38],'selected_composite':{'file':'source-composite.png','png_sha256':sha(O/'source-composite.png'),'rgba_sha256':g['rgba_sha256'],'world_origin':g['world_bounds_xyxy'][:2],'size':[124,105]},
 'registration_cautions':{'actual_woody_root':None,'reason':'No trunk/root is visibly separable from the dense foliage and dark dither; no physical root coordinate is proven.',
 'logical_center_owner_origin':{'world':[57*48,38*32],'composite_local':[41,73],'meaning':'map draw origin, not a root/contact point'},
 'bbox_bottom_y':105,'bbox_bottom_includes_checker':True,'visible_lower_foliage_samples':leaf_samples,'manual_lower_foliage_read_zone_xyxy':[40,94,95,100],
 'ground_height_or_plane':None,'future_rule':'Register generated foliage by silhouette/support-envelope review; read its visible base separately. Do not backfill an invented source root.'},
 'checker_evidence':{'spatial_rois':rois,'all_image_dark_color_count_unclassified':int(np.sum(np.all(a==[8,0,0,255],axis=2))),
 'warning':'The same dark checker color appears from y5 to y104, including leaf interiors. Only listed tiny exterior ROIs are classified. No global RGB removal/mask or complete ground-cast extraction is justified.',
 'direction':'The right exposed halo is right/up relative to lower visible foliage, but tiny and insufficient for an independent precise light calibration; the lower halo also extends downward.',
 'whole_cast_separable':False},
 'first_screen':{'camera':[61,39],'viewport':[1024,768],'screen_origin':screen_origin.tolist(),'origin_formula':'viewport*(0.5,0.54)-camera*(48,32)','geometric_visibility_only':True,'full_groups':[[57,38],[64,45]],'partial_groups':[[51,44],[58,51]],'actual_occlusion_not_proven':True,'context_board':'first-screen-source-context.jpg','context_note':'Original environment/NPC frames, integer CPU sampling of fractional origin; no hero or native-GPU parity claim.'},
 'one_image_feasibility':{'feasible':True,'scope':'One static whole generated RGBA bush, one common scale+translation, technical partition to four original owners. One separate full-alpha cast can be considered after contact review.',
 'preserve':['all original source cell flags','four owner keys','143 early sort row and three later owner sort tuples','no source RGB deletion','no per-cutout cast accumulation'],
 'requirements':['Generate no baked cast/checker or ground tile in the new body','Full generated alpha needs a normal runtime resource for a future single shadow','Suppress all four source owners together to avoid original dither/cast duplication','Keep new body owner partition and shadow as separate concerns','Flat-ground front/back actor and silhouette parity review before enabling any instance','Pilot selected57,38 first; other instances are translated instances but not automatically depth-accepted'],
 'limitations':['Hidden source root prevents exact root anchoring','Source leaf-interior dither is not a separable physical shadow','A round bush occupies depth; future one-plane projection is still a2D approximation','No new shader/API/runtime/imagegen work authorized in this study']},
 'art_redraw_input':{'subject':'compact low round green leafy shrub, yellow-green sunlit leaf tips, dense layered foliage with irregular natural outline','original_native_extent_including_dither':[124,105],
 'preserve':'low rounded silhouette/scale and broad lower foliage envelope; allow a clear readable new base for registration if visually natural','exclude':'baked cast shadow, checker dither, ground patch, rock base, oversized tree trunk, animation sheet'}}
(O/'source-group-contract.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n')
print('ROUND_SHRUB_SOURCE_PASS owners=32 groups=8 source_frames_exact=4 orphan=0 static=true composite=124x105 actual_root=unknown')
print('GROUPS',[(q['center_owner_cell'],q['nominal_first_screen']['visibility'])for q in groups])
