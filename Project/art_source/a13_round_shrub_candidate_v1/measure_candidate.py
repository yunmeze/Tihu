"""Single uniform-scale diagnostic only. Raw is never rewritten or partitioned."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent;O=P/'diagnostics/art_source/a13-round-shrub';O.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
raw=Image.open(D/'raw.png').convert('RGBA');src=Image.open(P/'art_source/a13_round_shrub_source/source-composite.png').convert('RGBA');a=np.asarray(raw);sa=np.asarray(src)
def box(m):
 y,x=np.where(m);return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
# Explicit measurement only, never applied as an image mask.
source_green=(sa[:,:,3]>0)&(sa[:,:,1]>sa[:,:,0])&(sa[:,:,1]>sa[:,:,2]);sb=box(source_green);assert sb==[0,0,120,100]
b=box(a[:,:,3]>=96);bw=b[2]-b[0];bh=b[3]-b[1]
scale=min((sb[2]-sb[0])/bw,(sb[3]-sb[1])/bh)
translation=np.array([(sb[0]+sb[2])/2-scale*(b[0]+b[2])/2,sb[3]-scale*b[3]])
canvas=(140,121);padding=np.array([8.,8.]);t=translation+padding
src_layer=Image.new('RGBA',canvas);src_layer.alpha_composite(src,(8,8))
nearest=raw.transform(canvas,Image.Transform.AFFINE,(1/scale,0,-t[0]/scale,0,1/scale,-t[1]/scale),Image.Resampling.NEAREST)
linear=raw.transform(canvas,Image.Transform.AFFINE,(1/scale,0,-t[0]/scale,0,1/scale,-t[1]/scale),Image.Resampling.BILINEAR)
# Same original grass crop in all comparisons, native-size only.
manifest=json.loads((P/'assets/original/manifest.json').read_text());pk=manifest['packs']['Map/Res/FloorBig'];f=pk['frames']['406'];x,y,w,h=f['rect'];page=Image.open(P/pk['pages'][f['page']]['file'][6:]).convert('RGBA');tile=page.crop((x,y,x+w,y+h))
grass=Image.new('RGBA',canvas)
for yy in range(0,canvas[1],tile.height):
 for xx in range(0,canvas[0],tile.width):grass.alpha_composite(tile,(xx,yy))
neutral=Image.new('RGBA',canvas,(94,108,95,255))
strips={}
for name,bg in [('neutral',neutral),('grass',grass)]:
 strip=Image.new('RGB',(canvas[0]*3,canvas[1]))
 for i,layer in enumerate([src_layer,nearest,linear]):
  im=bg.copy();im.alpha_composite(layer);strip.paste(im.convert('RGB'),(canvas[0]*i,0))
 strip.save(O/f'native-{name}-strip.png');strips[name]=strip
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18);small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
board=Image.new('RGB',(1680,820),(234,237,239));d=ImageDraw.Draw(board)
d.text((15,12),'One generated shrub / original vs same uniform scale / no owner partition, root or runtime claim',fill=(20,25,30),font=font)
for i,title in enumerate(['ORIGINAL + old dither','NEW nearest','NEW bilinear (offline only)']):d.text((i*560+15,51),title,fill=(20,25,30),font=font)
board.paste(strips['neutral'].resize((1680,484),Image.Resampling.NEAREST),(0,80))
d.text((15,582),'Below: native1x strips, original | new nearest | new bilinear. Source dark checker is retained only in original.',fill=(20,25,30),font=small)
board.paste(strips['neutral'],(15,616));board.paste(strips['grass'],(575,616))
d.text((15,755),f'Uniform scale {scale:.12f}; local translation({translation[0]:.4f},{translation[1]:.4f}); visible foliage envelope only.',fill=(20,25,30),font=small)
d.text((15,780),'No global alpha thresholding/RGB deletion. Bright new tips are abundant; review color and volume at native size.',fill=(20,25,30),font=small)
board.save(O/'whole-and-native-review.png')
metrics={'status':'one generation; parent accepted whole/native working candidate 2026-10-15T06:38:32Z; runtime depth pending',
 'raw_sha256':sha(D/'raw.png'),'source_composite_sha256':sha(P/'art_source/a13_round_shrub_source/source-composite.png'),
 'raw_size':list(raw.size),'raw_mode':'RGBA','source_measurement':{'criterion':'alpha>0 and G>R and G>B; measurement only, not image segmentation/removal','bbox_xyxy':sb,'meaning':'visible green foliage envelope; excludes no source data in delivered source art; not a physical footprint or root'},
 'candidate_alpha_bboxes_measurement_only':{str(q):box(a[:,:,3]>=q)for q in [1,32,96,192]},
 'common_transform':{'scale':scale,'translation_to_source_composite':translation.tolist(),'rotation':0,'shear':0,'anisotropic_scale':False,
 'rule':'fit alpha>=96 diagnostic bbox within source120x100 visible foliage envelope; center horizontally and align lower envelope y100','physical_root_claim':False},
 'native_diagnostic_canvas':{'size':list(canvas),'source_padding':[8,8],'sampling':['nearest','bilinear'],'rgba_body_edited':False},
 'candidate_alpha96_edges_over_canvas':[int((a[0,:,3]>=96).sum()),int((a[-1,:,3]>=96).sum()),int((a[:,0,3]>=96).sum()),int((a[:,-1,3]>=96).sum())],
 'cautions':['Very low alpha fringes touch left/bottom canvas; raw preserved exactly, not cleaned','Warm yellow-green new-leaf tips are more numerous than the requested small accent; parent accepted native working color, retained without cleanup','Current envelope fit does not establish physical root/contact, owner assignment or receiver plane','Source and generated crown gaps differ; judge natural volume and native silhouette rather than force pixel correspondence'],
 'diagnostic_outputs':[str((O/n).relative_to(P))for n in ['native-neutral-strip.png','native-grass-strip.png','whole-and-native-review.png']]}
(D/'geometry-diagnostic.json').write_text(json.dumps(metrics,indent=2)+'\n')
print(json.dumps(metrics['common_transform']));print('SHRUB_COMMON_SCALE_PASS raw_immutable=true uniform_only=true source_envelope=120x100 candidate_bbox='+str(b))
# Reproducible read-only artifact classification; this never masks/recolors raw.
from scipy.ndimage import label,find_objects
rgb=a[:,:,:3];alpha=a[:,:,3]
white=(rgb.min(2)>=210)&((rgb.max(2).astype(int)-rgb.min(2))<=30)
green=(rgb[:,:,1]>=220)&(rgb[:,:,0]<=70)&(rgb[:,:,2]<=100)
def levels(mask):return [{'alpha_range':[lo,hi],'pixels':int((mask&(alpha>=lo)&(alpha<=hi)).sum())}for lo,hi in [(0,0),(1,15),(16,63),(64,191),(192,255)]]
l,n=label(white&(alpha>=192));components=[]
for i,bb in enumerate(find_objects(l),1):
 if bb:
  y,x=bb;sel=l[bb]==i;count=int(sel.sum())
  if count>=3:components.append({'count':count,'raw_xyxy':[x.start,y.start,x.stop,y.stop],'alpha_min':int(alpha[bb][sel].min()),'alpha_max':int(alpha[bb][sel].max()),'median_rgb':np.median(rgb[bb][sel],axis=0).tolist()})
components.sort(key=lambda q:q['count'],reverse=True)
audit={'status':'read-only color/alpha audit; no cleanup or regeneration','raw_sha256':sha(D/'raw.png'),'white_indicator':'min(R,G,B)>=210 and max-min<=30, measurement only','white_alpha_histogram':levels(white),'high_alpha_white_components_at_least3pixels':components,'bright_green_indicator':'G>=220,R<=70,B<=100, measurement only','bright_green_alpha_histogram':levels(green),'native_render_samples':{},'conclusion':'White star/spot regions include real high-alpha near-white pixels, not merely transparent display. Saturated green fringe samples are alpha1..15 only. Raw immutable.'}
for name,q in [('nearest',nearest),('linear',linear)]:
 ar=np.asarray(q);cc=ar[:,:,:3];aa=ar[:,:,3];mask=(cc.min(2)>=210)&((cc.max(2).astype(int)-cc.min(2))<=30)&(aa>=192);yy,xx=np.where(mask)
 audit['native_render_samples'][name]={'white_pixels_high_alpha':int(mask.sum()),'canvas_xy':np.c_[xx,yy].tolist()}
(D/'rgba-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
