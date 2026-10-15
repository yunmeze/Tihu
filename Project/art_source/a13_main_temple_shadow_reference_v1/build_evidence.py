"""Reproduce bounded source-referenced 2D shadow RESEARCH masks. No runtime/art edits.
Only writes this directory; source/raw pixels are immutable. Requires Pillow,
NumPy and SciPy already present in the task environment.
"""
from pathlib import Path
import hashlib, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import binary_dilation, binary_fill_holes, gaussian_filter

P = Path(__file__).resolve().parents[2]
O = Path(__file__).resolve().parent
FILES = {
    'source_contract': 'art_source/a13_main_temple_source/source-group-contract.json',
    'candidate_raw': 'art_source/a13_main_temple_candidate_v2/raw.png',
    'registration': 'assets/scifi/environment/a13_temple_v2/registration.json',
    'map': 'data/maps/A13.json',
    'manifest': 'assets/original/manifest.json',
}
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
inputs = {k: {'path':v, 'sha256':sha(P/v)} for k,v in FILES.items()}
c = json.loads((P/FILES['source_contract']).read_text())
r = json.loads((P/FILES['registration']).read_text())
mp = json.loads((P/FILES['map']).read_text())
packs = json.loads((P/FILES['manifest']).read_text())['packs']
W,H = c['composite_size']; ox,oy = c['world_bounds_xyxy'][:2]
assert (W,H,ox,oy)==(796,665,2948,642)
assert inputs['candidate_raw']['sha256']=='3bf1876fd6b76831216668a645f4120dcbc737cfa2ba258e0fc3d2fee705c3e1'
assert inputs['registration']['sha256']=='ccd287a99b3ca2e5732890208a3f482125deba989e244bb4277fb027c38d4599'
pages={}
def page(path):
    if path not in pages: pages[path]=Image.open(P/path.removeprefix('res://')).convert('RGBA')
    return pages[path]
def blit(canvas, tile, x, y):
    # PIL clips destination edges; every source texel stays unchanged.
    canvas.alpha_composite(tile,(int(x),int(y)))
source=Image.new('RGBA',(W,H))
source_label=np.full((H,W),-1,np.int16)
for i,e in enumerate(c['owners_in_draw_order']):
    x,y,w,h=e['atlas_rect'];wx,wy,_,_=e['world_rect']
    tile=page(e['atlas_page']).crop((x,y,x+w,y+h));blit(source,tile,wx-ox,wy-oy)
    aa=np.asarray(tile)[:,:,3]>0
    sub=source_label[wy-oy:wy-oy+h,wx-ox:wx-ox+w];sub[aa]=i
src=np.asarray(source)
raw=np.asarray(Image.open(P/FILES['candidate_raw']).convert('RGBA'))
s=float(r['whole_building_registration']['scale']); origin=np.array(r['whole_building_registration']['world_top_left'])
yy,xx=np.indices((H,W));wx=ox+xx+.5;wy=oy+yy+.5
rx=np.floor((wx-origin[0])/s).astype(int);ry=np.floor((wy-origin[1])/s).astype(int)
valid=(rx>=0)&(ry>=0)&(rx<raw.shape[1])&(ry<raw.shape[0])
new=np.zeros((H,W,4),np.uint8);new[valid]=raw[ry[valid],rx[valid]]
# All body opacity levels and enclosed transparent openings are protected.
# This is a receiver veto, not a change to the body alpha or a ground footprint.
structural=binary_fill_holes(new[:,:,3]>0)
yk,xk=np.indices((5,5));disk=(xk-2)**2+(yk-2)**2<=4
exclusion=binary_dilation(structural,structure=disk)

# Explicit manually reviewed spatial fences. Never classify full image by RGB.
rects=[(680,310,796,350),(684,350,796,360),(700,360,796,370),(728,370,796,390)]
roi=np.zeros((H,W),bool);source_checker=np.zeros((H,W),bool);roi_records=[]
for b in rects:
    x0,y0,x1,y1=b;tile=src[y0:y1,x0:x1];nonzero=tile[:,:,3]>0
    assert np.all(tile[nonzero]==[8,0,0,255]), ('non-checker material in fenced ROI',b)
    roi[y0:y1,x0:x1]=True;source_checker[y0:y1,x0:x1]=nonzero
    ys,xs=np.where(nonzero);gx=xs+x0;gy=ys+y0
    assert np.all((gx+gy)%2==1)
    ids,counts=np.unique(source_label[y0:y1,x0:x1][nonzero],return_counts=True)
    roi_records.append({'source_xyxy_exclusive':list(b),'world_xyxy_exclusive':[x0+ox,y0+oy,x1+ox,y1+oy],
        'checker_count':int(nonzero.sum()),'rgba':[8,0,0,255],
        'checker_parity':'(source_x+source_y)%2 == 1',
        'contributors':[{'key':c['owners_in_draw_order'][int(i)]['key'],'pixels':int(n)}for i,n in zip(ids,counts)]})

# Reproduce original floor draw order, preserving ownership at every pixel.
floor=Image.new('RGBA',(W,H));floor_labels=np.full((H,W),-1,np.int32);floor_records=[]
for x in range(mp['width']):
    for y in range(mp['height']):
        fid=mp['cells'][x*mp['height']+y][0]
        if not fid: continue
        pack_name='Map/Res/FloorBig' if fid<0 else 'Map/Res/FloorSmall'
        pack=packs[pack_name];f=pack['frames'][str(abs(fid))];ax,ay,aw,ah=f['rect'];dx=x*48+f['crop'][0]-ox;dy=y*32+f['crop'][1]-oy
        if dx>=W or dy>=H or dx+aw<=0 or dy+ah<=0: continue
        tile=page(pack['pages'][f['page']]['file']).crop((ax,ay,ax+aw,ay+ah));blit(floor,tile,dx,dy)
        i=len(floor_records);floor_records.append({'cell':[x,y],'pack':pack_name,'frame':abs(fid),'world_rect':[dx+ox,dy+oy,aw,ah]})
        x0=max(0,dx);y0=max(0,dy);x1=min(W,dx+aw);y1=min(H,dy+ah)
        mask=np.asarray(tile)[y0-dy:y1-dy,x0-dx:x1-dx,3]>0
        sub=floor_labels[y0:y1,x0:x1];sub[mask]=i
fa=np.asarray(floor)
assert np.all(fa[:,:,3][roi]==255)
fids,counts=np.unique(floor_labels[roi],return_counts=True)
used_floors=[dict(floor_records[int(i)],roi_pixels=int(n)) for i,n in zip(fids,counts)]
assert all(f['pack']=='Map/Res/FloorBig' and f['frame']==406 for f in used_floors)
# Read every original scenery and NPC animation placement using world_view rules.
# A bounding-box intersection is never treated as visible coverage by itself.
groups={1:'Map/Res/Debris',2:'Map/Res/Plant',3:'Map/Res/Wall',4:'Map/Res/Building',5:'Map/Res/Dynamic',8:'Data4'}
placements=[]
for x in range(mp['width']):
    for y in range(mp['height']):
        cell=mp['cells'][x*mp['height']+y];kind=int(cell[2]);index=int(cell[3])
        if index<=0 or kind not in groups: continue
        indices=range(55,60) if kind==8 else (range(index,index+5) if kind==5 else [index])
        for idx in indices:placements.append((groups[kind],idx,kind,x*48,y*32,x,y))
for n in mp['npcs']:
    base=1+int(n['appearance'])*12+int(n['direction'])*4
    for idx in range(base,base+4):placements.append(('Npc',idx,7,float(n['x'])*48,float(n['y'])*32,n['x'],n['y']))
roi_intersections=[]
for pn,idx,kind,wx0,wy0,cx,cy in placements:
    pack=packs[pn];f=pack['frames'].get(str(idx))
    if not f:continue
    ax,ay,aw,ah=f['rect'];top=0 if kind==7 else (-52 if kind==8 else 32-f['original'][1])
    dx=int(wx0+f['crop'][0]+(f['offset'][0] if kind==7 else 0)-ox)
    dy=int(wy0+f['crop'][1]+top+(f['offset'][1] if kind==7 else 0)-oy)
    x0=max(0,dx);y0=max(0,dy);x1=min(W,dx+aw);y1=min(H,dy+ah)
    if x1<=x0 or y1<=y0 or not np.any(roi[y0:y1,x0:x1]):continue
    tile=np.asarray(page(pack['pages'][f['page']]['file']))[ay+y0-dy:ay+y1-dy,ax+x0-dx:ax+x1-dx]
    visible=(tile[:,:,3]>0)&roi[y0:y1,x0:x1]
    if not np.any(visible):continue
    assert pn=='Map/Res/Building' and idx in range(3966,3996),('non-temple receiver obstruction',pn,idx,cx,cy)
    assert np.all(tile[visible]==[8,0,0,255]),('non-checker temple receiver obstruction',idx)
    roi_intersections.append({'pack':pn,'frame':idx,'cell':[cx,cy],'visible_checker_pixels':int(visible.sum())})
# All original nonzero alpha outside the explicitly verified checker is conservatively
# treated as structure OR unknown, including unclassified old shadow/apron. No global
# RGB search/removal is performed. Its 2D guard catches cross-band boundary adjacency.
source_uncertain=(src[:,:,3]>0)&~source_checker
source_exclusion=binary_dilation(source_uncertain,structure=disk)
receiver=roi & ~source_exclusion

# Fill ONLY checker gaps bracketed by original supported texels on one axis.
# No dilation of the cast footprint, no extrapolation behind the building.
left=np.zeros_like(roi);left[:,1:]=source_checker[:,:-1]
right=np.zeros_like(roi);right[:,:-1]=source_checker[:,1:]
up=np.zeros_like(roi);up[1:]=source_checker[:-1]
down=np.zeros_like(roi);down[:-1]=source_checker[1:]
bracketed=(left&right)|(up&down)
envelope=(source_checker|bracketed)&receiver
assert np.all(src[:,:,3][bracketed&~source_checker&receiver]==0)
# A single normalized Gaussian operates on the observed half-density checker.
# Compensation restores a continuous .30 core; cap and all fences apply last.
soft=np.minimum(.30,gaussian_filter(source_checker.astype(float),sigma=1.25,truncate=3.0,mode='constant')*.60)
soft*=envelope & receiver & ~exclusion
alpha=np.rint(soft*255).astype(np.uint8)
assert not np.any(alpha[exclusion]) and not np.any(alpha[~receiver]) and not np.any(alpha[~envelope])
assert alpha.max()<=77
masks={'source_checker_support.png':source_checker.astype(np.uint8)*255,
       'receiver_allowed.png':receiver.astype(np.uint8)*255,
       'source_structure_or_unknown_exclusion.png':source_exclusion.astype(np.uint8)*255,
       'new_structure_exclusion.png':exclusion.astype(np.uint8)*255,
       'soft_reference_alpha.png':alpha}
for name,a in masks.items():Image.fromarray(a).save(O/name)

def bbox(a):
    ys,xs=np.where(a)
    return [int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] if len(xs) else None
counts={
 'roi_pixels':int(roi.sum()),'receiver_after_source_safety_pixels':int(receiver.sum()),
 'checker_pixels_excluded_by_source_structure_or_unknown':int((source_checker&source_exclusion).sum()),'original_checker_pixels':int(source_checker.sum()),
 'bracketed_checker_gaps':int((envelope&~source_checker).sum()),
 'observed_plus_bracketed_envelope_pixels':int(envelope.sum()),
 'checker_pixels_excluded_by_new_structure':int((source_checker&exclusion).sum()),
 'final_nonzero_pixels':int((alpha>0).sum()),'final_max_alpha_byte':int(alpha.max()),
 'final_max_float_alpha':float(soft.max()),'final_alpha_sum_in_opaque_pixel_equivalents':float(alpha.sum()/255),
 'protected_pixel_leak_count':int(np.count_nonzero(alpha[exclusion])),
 'unknown_receiver_leak_count':int(np.count_nonzero(alpha[~receiver])),
 'outside_observed_envelope_leak_count':int(np.count_nonzero(alpha[~envelope])),
}
contract={
 'schema':'a13-temple-source-referenced-ground-shadow-research-v1',
 'status':'offline evidence only; no runtime integration or native acceptance',
 'meaning':'Source-referenced 2D ground-shadow fragment, not physical illumination reconstructed for the new roof.',
 'inputs':inputs,'source_texture_pages':{path:{'sha256':sha(P/path.removeprefix('res://'))} for path in sorted(pages)},'source_rgba_reconstruction_sha256':hashlib.sha256(src.tobytes()).hexdigest(),
 'canvas':{'size':[W,H],'world_top_left':[ox,oy],'pixel_center_convention':'x+0.5,y+0.5; rectangles upper bounds exclusive'},
 'source_rois':roi_records,'floor_receiver_provenance':used_floors,
 'all_scene_receiver_audit':{'placements_including_animation_frames_scanned':len(placements),'only_visible_intersections':roi_intersections,'non_temple_or_structural_obstructions':0},
 'raw_to_world':r['whole_building_registration'],
 'classification':{'scope':'Only the listed external-ground rectangles; exact RGBA is verified inside each rectangle, never searched globally.',
   'unconfirmed_regions':'zero; no extrapolation to hidden or lower checker fragments',
   'source_checker_isolation':'original transparent/opaque odd-parity checker pattern; all nontransparent pixels inside every fence must match',
   'receiver_assumption':'FloorBig406 visible grass with no other original scenery/NPC coverage; this is rendered flat ground, not surveyed terrain elevation'},
 'source_safety_exclusion':{'source':'All source nonzero alpha except the spatially verified checker; unknown shadow/apron also treated conservatively as blocked','safety_band_native_px':2,'metric':'Euclidean disk radius2','global_rgb_segmentation':False},
 'structure_exclusion':{'source':'new raw sampled by registered nearest pixel-center mapping, all alpha>0',
   'fill_enclosed_holes':True,'safety_band_native_px':2,'metric':'Euclidean disk radius2',
   'purpose':'Protect all visible building material, enclosed doors/interiors and edges. Not a ground/contact footprint.'},
 'softening':{'diagnostic_tint_rgb_bytes':[9,11,14],'passes':1,'kernel':'normalized Gaussian','sigma_native_px':1.25,'truncate_sigma':3.0,
   'input':'original binary half-density checker only','density_compensation':2.0,'opacity_cap':.30,
   'finite_support':'Within the source safety receiver, only original checker pixels or transparent gaps bracketed on opposite sides by original checker within one pixel',
   'order':'Gaussian, density compensation, opacity cap, then observed-envelope AND verified-receiver AND NOT structural-exclusion',
   'quantization':'round(alpha*255); mathematical cap .30 may serialize as byte77'},
 'counts':counts,'source_checker_bbox':bbox(source_checker),'final_alpha_bbox':bbox(alpha>0),
 'runtime':{'connected':False,'proposed_order':'floor -> one reference-shadow pass -> original interleaved scenery-and-actor ordering, including layer0 stair objects before layer1 actors where the original rules require',
    'source_group_rule':'if later used, suppress all30 original owners together; never retain old checker beside the new pass',
    'ordinary_dependency_gate':'research paths are not runtime dependencies; any future integration must close normal resource paths and test complete source fallback'},
 'limitations':['Only an exposed right-side fragment survives; it is not a full building shadow.',
   'Left ROI fences and source 2px safety guard intentionally truncate unknown/structural areas; no hidden support is filled. The stepped lower-left truncation remains visibly artificial in the enlarged board.',
   'Source exterior edge itself ends at the original grouped canvas boundary; nothing beyond is inferred.',
   'New roof shape differs, so preserving source outer extent does not reproduce new-roof physical lighting.',
   'Nearest CPU diagnostic is not GPU sampler parity. No native alpha/receiver/character or stair-route acceptance yet.',
   'Exclusion prevents underlying material leakage at measured native pixels, but camera subpixels and filter footprints need later GPU validation.'],
 'artifacts':{name:{'sha256':sha(O/name),'kind':'single-channel L8 technical mask'}for name in masks},
}
(O/'reference-contract.json').write_text(json.dumps(contract,indent=2,ensure_ascii=False)+'\n')

# Evidence board: source RGB/alpha and generated RGB/alpha are sampled only, never rewritten.
def composite(base,overlay):
    out=base.copy();out.alpha_composite(overlay);return out
base=Image.new('RGBA',(W,H),(32,41,31,255));base.alpha_composite(floor)
source_panel=composite(base,source)
for b in rects:ImageDraw.Draw(source_panel).rectangle((b[0],b[1],b[2]-1,b[3]-1),outline=(0,230,230,255),width=1)
new_panel=composite(base,Image.fromarray(new))
# Show reviewed spatial ROI in cyan, new-structure exclusion in magenta; the actual receiver additionally removes source safety.
ov=np.zeros_like(new);ov[roi]=[0,225,230,75];ov[exclusion & (xx>=650)&(yy>=285)&(yy<420)]=[255,65,180,90]
mask_panel=composite(new_panel,Image.fromarray(ov))
shadow=np.zeros_like(new);shadow[:,:,:3]=[9,11,14];shadow[:,:,3]=alpha
candidate_panel=composite(composite(base,Image.fromarray(shadow)),Image.fromarray(new))
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
board=Image.new('RGB',(W*2,H*2+150),(235,237,239));d=ImageDraw.Draw(board)
items=[(source_panel,'SOURCE + fenced external-floor ROI',0,35),
       (mask_panel,'NEW + reviewed ROI cyan / new exclusion magenta',W,35),
       (candidate_panel,'OFFLINE reference fragment ON (not runtime acceptance)',0,H+75),
       (new_panel,'OFFLINE reference fragment OFF',W,H+75)]
for panel,label,x,y in items:board.paste(panel.convert('RGB'),(x,y));d.text((x+8,y-27),label,fill=(20,25,30),font=font)
d.text((8,H*2+118),'One source-referenced 2D matte. Unknown regions remain zero. No inferred 3D height or whole-building projection.',fill=(20,25,30),font=small)
board.save(O/'source-new-mask-board.jpg',quality=94)
# Focused comparison at 4x nearest, technical masks clearly labeled.
box=(650,290,796,410);thumbs=[source_panel,new_panel,Image.fromarray(np.repeat(source_checker[:,:,None],4,axis=2).astype(np.uint8)*255).convert('RGBA'),Image.fromarray(alpha).convert('RGBA'),candidate_panel]
labels=['SOURCE / fences','NEW / no cast','Original checker mask','Soft alpha / cap0.30','Offline ON']
w=(box[2]-box[0])*4;h=(box[3]-box[1])*4;detail=Image.new('RGB',(w*len(thumbs),h+40),(235,237,239));dd=ImageDraw.Draw(detail)
for i,(im,label) in enumerate(zip(thumbs,labels)):
    crop=im.crop(box).resize((w,h),Image.Resampling.NEAREST)
    detail.paste(crop.convert('RGB'),(i*w,40));dd.text((i*w+8,9),label,fill=(20,25,30),font=font)
detail.save(O/'receiver-detail-board.png')
print('TEMPLE_REFERENCE_EVIDENCE_PASS',json.dumps(counts))
print('FLOORS',json.dumps(used_floors))
print('ROIS',json.dumps(roi_records))
