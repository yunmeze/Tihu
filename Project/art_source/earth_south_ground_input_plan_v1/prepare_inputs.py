"""Source/reference input preparation only. Does not alter final art or production."""
from pathlib import Path
import json,hashlib,collections
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[2];O=Path(__file__).parent;inputs={};pages={};ims={}
W=[2400,1408,3168,1920];OLD=[2496,960,3264,1472];OVER=[2496,1408,3168,1472]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bind(path):
 p=P/path;inputs[path]={'path':path,'sha256':sha(p),'bytes':p.stat().st_size};return p
def read(path):return json.loads(bind(path).read_text())
def save(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def hit(a,b):return a[0]<b[2] and a[2]>b[0] and a[1]<b[3] and a[3]>b[1]
def union(bs):return [min(a[0] for a in bs),min(a[1] for a in bs),max(a[2] for a in bs),max(a[3] for a in bs)]
m=read('data/maps/A13.json');manifest=read('assets/original/manifest.json');old=read('assets/earth/environment/ground_plate_v4/registration.json');assert sha(P/'data/maps/A13.json')==old['source_map_sha256'];assert sha(P/'assets/original/manifest.json')==old['source_manifest_sha256']
categories=read('art_source/a13_ground_full_map_plan/source-inventory.json')['classifications'];cat_by_id={i:k for k,v in categories.items() for i in v['ids']}
def frame(pack,idx):
 key=(pack,idx)
 if key not in ims:
  pk=manifest['packs'][pack];f=pk['frames'][str(idx)];path=pk['pages'][f['page']]['file'][6:]
  if path not in pages:pages[path]=Image.open(bind(path)).convert('RGBA')
  a,b,w,h=f['rect'];ims[key]=pages[path].crop((a,b,a+w,b+h))
 return manifest['packs'][pack]['frames'][str(idx)],ims[key]
allfloors=[]
for i,c in enumerate(m['cells']):
 signed=c[0]
 if not signed:continue
 x,y=divmod(i,100);pack='Map/Res/FloorBig' if signed<0 else 'Map/Res/FloorSmall';idx=abs(signed);f,im=frame(pack,idx);a=x*48+f['crop'][0];b=y*32+f['crop'][1];w,h=im.size;alpha=im.getchannel('A')
 allfloors.append({'key':f'{pack}:{idx}@{x},{y}','pack':pack,'frame_index':idx,'signed_id':signed,'cell':[x,y],'source_cell':c,'source_flag':c[1],'floor_pass_tag':0,'sort_y':y,'stable_source_order':i,'source_map_byte_offset':m['cellByteOffsets'][i],'original':f['original'],'crop':f['crop'],'offset_ignored':f['offset'],'world_bounds_xyxy':[a,b,a+w,b+h],'source_rgba_sha256':hashlib.sha256(im.tobytes()).hexdigest(),'source_alpha_sha256':hashlib.sha256(alpha.tobytes()).hexdigest(),'alpha_extrema':alpha.getextrema(),'nonopaque_pixel_count':sum(alpha.histogram()[:255]),'source_material_category':cat_by_id[signed]})
os=[a for a in allfloors if hit(a['world_bounds_xyxy'],W)];old_by_key={a['key']:a for a in old['owners']};assert len(os)==64
floor=Image.new('RGBA',(768,512));index=Image.new('I;16',(768,512));di=ImageDraw.Draw(index);cover=Image.new('L',(768,512));dc=ImageDraw.Draw(cover);cnt=collections.Counter()
for n,a in enumerate(os):
 f,im=frame(a['pack'],a['frame_index']);b=a['world_bounds_xyxy'];assert b[0]>=W[0] and b[1]>=W[1] and b[2]<=W[2] and b[3]<=W[3];assert im.getchannel('A').getextrema()==(255,255)
 x,y=b[0]-W[0],b[1]-W[1];floor.paste(im,(x,y));di.rectangle((x,y,x+im.width-1,y+im.height-1),fill=n+1);dc.rectangle((x,y,x+im.width-1,y+im.height-1),fill=255)
 a['status']='frozen_existing_v4' if a['key'] in old_by_key else 'new_exact_owner_proposal';a['proposed_density']=2;a['proposed_whole_canvas_region_px']=[2*x,2*y,2*im.width,2*im.height]
 a['source_png']='source_frames/FloorBig_'+str(a['frame_index'])+'.png';(O/'source_frames').mkdir(exist_ok=True);im.save(O/a['source_png'])
 if a['key'] in old_by_key:
  existing=old_by_key[a['key']];path=existing['texture'][6:];pic=Image.open(bind(path)).convert('RGBA');assert sha(P/path)==existing['texture_sha256'];a['keep_existing_asset']={'path':path,'sha256':sha(P/path),'size':list(pic.size),'existing_shared_region_px':existing['shared_region_px']};assert existing['source_cell']==a['source_cell']
 cnt[a['status']]+=1
floor.save(O/'source_floor_layout_native.png');floor.getchannel('A').save(O/'source_alpha_native.png');index.save(O/'source_owner_index_native.png')
# No resampling of approved art: direct 2x crops preserve every RGBA texel.
platepath=old['shared_plate']['texture'][6:];plate=Image.open(bind(platepath)).convert('RGBA');assert sha(P/platepath)==old['shared_plate']['texture_sha256'];assert plate.size==(1536,1024)
refs=[]
for name,b in [('approved_overlap_2x',OVER),('approved_north_seam_band_2x',[2496,1440,3168,1472]),('approved_west_seam_band_2x',[2496,1408,2528,1472]),('approved_material_context_2x',[2496,1344,3264,1472]),('approved_grass_scale_patch_2x',[3072,1408,3136,1472]),('approved_slab_scale_patch_2x',[2704,1408,2768,1472])]:
 crop=[2*(b[0]-OLD[0]),2*(b[1]-OLD[1]),2*(b[2]-OLD[0]),2*(b[3]-OLD[1])];im=plate.crop(crop);im.save(O/(name+'.png'));refs.append({'file':name+'.png','world_bounds_xyxy':b,'density':2,'source':platepath,'source_raw_pixel_crop_xyxy':crop,'pixel_operation':'integer crop only; no resize, recolor, blend, seam fix or changed alpha','rgba_sha256':hashlib.sha256(im.tobytes()).hexdigest()})
# Assert approved 7 tiles reconstruct exactly the frozen overlap crop.
re=Image.new('RGBA',(1344,128))
for a in os:
 if a['status']=='frozen_existing_v4':
  b=a['world_bounds_xyxy'];im=Image.open(P/a['keep_existing_asset']['path']).convert('RGBA');re.paste(im,(2*(b[0]-OVER[0]),2*(b[1]-OVER[1])))
assert re.tobytes()==Image.open(O/'approved_overlap_2x.png').convert('RGBA').tobytes()
# Contact ledger includes exact horizontal/vertical segments, old/new ownership and source neighbor seams.
def contact(a,b):
 A=a['world_bounds_xyxy'];B=b['world_bounds_xyxy']
 if A[2]==B[0] or B[2]==A[0]:
  lo=max(A[1],B[1]);hi=min(A[3],B[3]);x=A[2] if A[2]==B[0] else B[2]
  if hi>lo:return [x,lo,x,hi]
 if A[3]==B[1] or B[3]==A[1]:
  lo=max(A[0],B[0]);hi=min(A[2],B[2]);y=A[3] if A[3]==B[1] else B[3]
  if hi>lo:return [lo,y,hi,y]
 return None
internal=[]
for i,a in enumerate(os):
 for b in os[i+1:]:
  line=contact(a,b)
  if line:internal.append({'a':a['key'],'b':b['key'],'segment_xyxy':line,'class':'frozen_to_new' if a['status']!=b['status'] else 'frozen_to_frozen' if a['status']=='frozen_existing_v4' else 'new_to_new'})
selected={a['key'] for a in os};outer=[]
for a in os:
 for b in allfloors:
  if b['key'] in selected:continue
  line=contact(a,b)
  if line:outer.append({'selected':a['key'],'neighbor':b['key'],'neighbor_source_cell':b['source_cell'],'neighbor_bounds':b['world_bounds_xyxy'],'segment_xyxy':line,'neighbor_is_existing_v4':b['key'] in old_by_key})
# Seven complete Debris owners at root64,60, not only two intersecting window.
pond=[]
for idx,c in zip(range(55,62),[[64,60],[65,61],[66,62],[67,63],[68,63],[69,63],[70,63]]):
 x,y=c;s=m['cells'][x*100+y];assert s[2:]==[1,idx];f,im=frame('Map/Res/Debris',idx);a=x*48+f['crop'][0];b=y*32+32-f['original'][1]+f['crop'][1];w,h=im.size
 pond.append({'key':f'Debris:{idx}@{x},{y}','frame_index':idx,'cell':c,'source_cell':s,'flag':s[1],'layer':0 if s[1] in [1,-2] else 2 if s[1]==2 else 1,'sort_y':y,'order':x*100+y,'crop':f['crop'],'original':f['original'],'world_bounds_xyxy':[a,b,a+w,b+h],'source_rgba_sha256':hashlib.sha256(im.tobytes()).hexdigest(),'intersects_observation_window':hit([a,b,a+w,b+h],W)})
pb=union([a['world_bounds_xyxy'] for a in pond]);po=Image.new('RGBA',(pb[2]-pb[0],pb[3]-pb[1]))
for a in sorted(pond,key=lambda a:(a['layer'],a['sort_y'],a['order'])):
 im=frame('Map/Res/Debris',a['frame_index'])[1];b=a['world_bounds_xyxy'];po.alpha_composite(im,(b[0]-pb[0],b[1]-pb[1]))
po.save(O/'debris_pool_complete_source_native.png')
# Separate object context is never mixed into floor generation input.
cb=[pb[0]-48,pb[1]-32,pb[2]+48,pb[3]+32];co=Image.new('RGBA',(cb[2]-cb[0],cb[3]-cb[1]));cf=[a for a in allfloors if hit(a['world_bounds_xyxy'],cb)]
for a in cf:
 b=a['world_bounds_xyxy'];co.alpha_composite(frame(a['pack'],a['frame_index'])[1],(b[0]-cb[0],b[1]-cb[1]))
for a in sorted(pond,key=lambda a:(a['layer'],a['sort_y'],a['order'])):
 b=a['world_bounds_xyxy'];co.alpha_composite(frame('Map/Res/Debris',a['frame_index'])[1],(b[0]-cb[0],b[1]-cb[1]))
co.save(O/'debris_pool_source_context_native.png')
# A geometry-only annotated board; source RGB remains unmodified in separate pristine input.
board=floor.convert('RGB');dr=ImageDraw.Draw(board)
for a in os:
 b=a['world_bounds_xyxy'];x,y=b[0]-W[0],b[1]-W[1];dr.rectangle((x,y,x+95,y+63),outline=(255,220,80) if a['status'].startswith('frozen') else (100,210,245));dr.text((x+2,y+2),f"{a['signed_id']} @{a['cell'][0]},{a['cell'][1]}",fill=(255,255,255))
board.save(O/'source_owner_layout_reference.png')
for path in ['docs/EARTH_ART_BIBLE_V1.md','docs/EARTH_GROUND_PLATE_V1.md','art_source/earth_ground_plate_clean_regen_v4/prompt.txt','art_source/earth_ground_plate_clean_regen_v4/raw.png','art_source/earth_base_style_concept_v1/concept.png']:bind(path)
save('source_owner_evidence.json',{'source_map_sha256':sha(P/'data/maps/A13.json'),'window_xyxy':W,'frozen_overlap_xyxy':OVER,'owners':os,'summary':{'owners':len(os),'status_counts':dict(cnt),'FloorSmall':sum(a['pack'].endswith('FloorSmall') for a in os),'all_opaque':all(a['alpha_extrema']==(255,255) for a in os),'new_source_signed_ids':dict(collections.Counter(a['signed_id'] for a in os if a['status'].startswith('new'))),'new_source_categories':dict(collections.Counter(a['source_material_category'] for a in os if a['status'].startswith('new')))}})
save('seam_contact_ledger.json',{'internal':internal,'outer_source_neighbors':outer,'internal_counts':dict(collections.Counter(a['class'] for a in internal)),'outer_count':len(outer),'warning':'Outside expansion remains source; these are source geometric contacts, not new-art continuity acceptance.'})
save('approved_reference_crops.json',{'original_shared_plate_sha256':sha(P/platepath),'reference_crops':refs,'seven_existing_tiles_equal_overlap':True,'no_pixels_changed_in_approved_assets':True})
save('debris_pool_evidence.json',{'complete_group':pond,'bounds_xyxy':pb,'context_xyxy':cb,'context_floors':cf,'policy':'Do not generate, flatten, delete, mask out, move, or bake this independent object into floor. Original owner layers/flags unchanged. No physical height inferred from flags.'})
save('INPUT_SHA256.json',list(inputs.values()))
print('summary',dict(cnt));print('new categories',collections.Counter(a['source_material_category'] for a in os if a['status'].startswith('new')));print('seams',collections.Counter(a['class'] for a in internal),'outer',len(outer));print('pond',pb,[(a['key'],a['intersects_observation_window']) for a in pond]);print('pool floors',collections.Counter(a['pack'] for a in cf))
# Exact seam anchors are coordinates/texel bindings, not claimed surveyed road-center points.
anchors=[]
for x,y,role in [(2496,1472,'L-junction of frozen north and west contact'),(2592,1472,'north seam tile boundary1'),(2688,1472,'north seam tile boundary2'),(2784,1472,'north seam tile boundary3'),(2880,1472,'north seam tile boundary4'),(2976,1472,'north seam tile boundary5'),(3072,1472,'north seam tile boundary6'),(3168,1472,'east end north seam'),(2496,1408,'top end west contact')]:
 anchors.append({'world_corner_xy':[x,y],'role':role,'old_v4_pixel_edge_xy':[2*(x-OLD[0]),2*(y-OLD[1])],'proposed_south_pixel_edge_xy':[2*(x-W[0]),2*(y-W[1])],'note':'Pixel-edge anchor, not pixel center. No claim that a curb or real-height feature lies exactly here.'})
save('generation_proposal.json',{'status':'pending review; no generation or art modification','canvas':{'world_xyxy':W,'native_required_pixels':[1536,1024],'density':2,'world_top_left':W[:2],'sampling':'world = [2400,1408] + (texel_index + 0.5)/2'},'frozen_region_on_south_raw_xyxy':[192,0,1536,128],'new_region_rectangles_on_south_raw_xyxy':[[0,0,192,128],[0,128,1536,1024]],'exact_seam_coordinate_anchors':anchors,'generation_inputs':{'geometry':'source_floor_layout_native.png','owner_identity':'source_owner_evidence.json and source_owner_index_native.png','pixel_identity_reference':'approved_overlap_2x.png','material_scale_reference':['approved_material_context_2x.png','approved_grass_scale_patch_2x.png','approved_slab_scale_patch_2x.png'],'object_exclusion_context':['debris_pool_complete_source_native.png','debris_pool_source_context_native.png']},'required_final_ownership':'Keep 7 frozen v4 owners, add only 57 exact new owners. Discard generated overlap; never register a whole 64-owner override on top. No final blend/composite has been prepared.','seam_policy':'First compare candidate directly against frozen old pixels. If unacceptable, regenerate or seek explicit review of a new-side-only correction; no automatic blend, recolor or overwrite of old art.','alpha_policy':'All selected original alpha255. Preserve exact source nearest2x per-owner alpha, never infer from generated RGB or material guides.','casting':'No cast baked into floor; no receiver/gate expansion licensed by this proposal.'})
