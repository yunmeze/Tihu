#!/usr/bin/env python3
"""Non-runtime candidate registration. One common scale; rigid translations only."""
from pathlib import Path
import json,hashlib,itertools
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;R=P.parents[1];D=R/'diagnostics/earth_hero_s_idle_v1';D.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
im=Image.open(P/'raw-v1.png').convert('RGBA');assert im.size==(2172,724)
a=np.asarray(im);parts=[im.crop((i*543,0,(i+1)*543,724)) for i in range(4)]
# Visible alpha contour crown and terminal tips only. Not bones or contact points.
anchors=np.array([[[272.5,87],[211,639],[333,670]],[[273,93],[206.5,634],[334.5,670]],[[271,94],[209.5,639],[336.5,670]],[[273.5,87],[211,639],[332.5,670]]])
target=np.array([[40,15],[33,83],[47,87]])
centered=anchors-anchors.mean(axis=1,keepdims=True);tc=target-target.mean(axis=0)
s=float((centered*tc).sum()/(centered**2).sum());translation=target.mean(axis=0)-s*anchors.mean(axis=1)
out=Image.new('RGBA',(2048,512));rows=[]
for i,tile in enumerate(parts):
 tx,ty=translation[i];factor=4*s
 # Inverse affine is isotropic, no rotation/shear/warp. Direct raw->HD4 only.
 reg=tile.transform((512,512),Image.Transform.AFFINE,(1/factor,0,-tx/s,0,1/factor,-ty/s),Image.Resampling.BICUBIC)
 out.paste(reg,(i*512,0))
 z=np.array(tile);ys,xs=np.where(z[:,:,3]>=128);res=s*anchors[i]+translation[i]-target
 rows.append({'source_id':17+i,'raw_cell_xywh':[543*i,0,543,724],'raw_body_bbox_alpha128':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'raw_body_height_span':int(ys.max()-ys.min()),'raw_density_vs_source72':float((ys.max()-ys.min())/72),'raw_surface_anchors_crown_Lterminal_Rterminal':anchors[i].tolist(),'translation_raw_scaled_to_logical':translation[i].tolist(),'logical_anchor_residuals':res.tolist(),'max_anchor_residual_norm':float(np.linalg.norm(res,axis=1).max()),'registered_nontransparent_bbox':reg.getbbox()})
out.save(P/'body-density4-CANDIDATE.png')
re=Image.new('RGBA',im.size)
for i,t in enumerate(parts):re.paste(t,(i*543,0))
assert re.tobytes()==im.tobytes()
dump(P/'registration-v1.json',{'status':'candidate_only_identity_review_required_not_runtime','raw_sha256':sha(P/'raw-v1.png'),'candidate_sha256':sha(P/'body-density4-CANDIDATE.png'),'common_uniform_scale_raw_to_logical':s,'effective_raw_texels_per_logical_after_registration':1/s,'frame_size':[128,128],'logical_root':[16,64],'texture_frame_size':[512,512],'texture_root':[64,256],'ticks':12,'source_ids':[17,18,19,20],'exact_raw_reassembly':True,'method':'global least squares over crown and visible boot terminal contours; one common scale and per-cell rigid translation; direct raw to HD4','uncertainty':{'raw_visible_edge_proxy_px':4,'source_crown_and_terminal_px':1},'limits':['Contour anchors are different visible surfaces between costume designs; not bone/contact homologues. Fit is a visual registration, not proof of motion preservation.','Crown shape/hairstyle affects anchor. Full original-relative arm/cloth changes require visual review.','No individual body normalization or deformation; no low-alpha deletion.','HD4 output is a downsample from detailed raw; density alone does not certify material quality.'],'records':rows})
for name,tile in [('raw-gray',im),('candidate-gray',out)]:
 bg=Image.new('RGBA',tile.size,(64,68,72,255));bg.alpha_composite(tile);bg.save(D/f'{name}.png')
for density in [1,2,4]:
 unit=128*density;board=Image.new('RGBA',(4*unit,4*unit),(64,68,72,255));draw=ImageDraw.Draw(board)
 for i in range(4):
  original=Image.open(P.parent/'earth_hero_s_input_plan_v1'/f'source-{17+i}.png').convert('RGBA')
  s_tile=out.crop((i*512,0,(i+1)*512,512))
  se=Image.open(R/'assets/earth/hero/se_idle_v1/body.png').convert('RGBA').crop((i*512,0,(i+1)*512,512))
  e=Image.open(R/'assets/earth/hero/e_idle_v1/body.png').convert('RGBA').crop((i*512,0,(i+1)*512,512))
  for row,tile in enumerate([original,s_tile,se,e]):
   tile=tile.resize((unit,unit),Image.Resampling.NEAREST if row==0 else Image.Resampling.LANCZOS);board.alpha_composite(tile,(i*unit,row*unit))
   draw.text((i*unit+4,row*unit+4),f'{["source S","candidate S","approved SE","approved E"][row]} {i}',fill='white')
 board.save(D/f'source-S-SE-E-same-logical-{density}x.png')
# Identity crop comparison at registered HD4: these are non-homologous view projections.
b=Image.new('RGBA',(900,320),(64,68,72,255));draw=ImageDraw.Draw(b)
for i,(name,tile) in enumerate([('S candidate',out.crop((0,0,512,512))),('SE13 canonical',Image.open(R/'assets/earth/hero/se_idle_v1/body.png').crop((0,0,512,512))),('E9 approved',Image.open(R/'assets/earth/hero/e_idle_v1/body.png').crop((0,0,512,512)))]):
 b.alpha_composite(tile.crop((88,80,240,280)),(i*300+70,40));draw.text((i*300+12,10),name+' same HD4 scale',fill='white')
b.save(D/'chest-thigh-same-scale.png')
# Loop order 20,17,18,19,20,17, no invented frames and no temporal image blending.
b=Image.new('RGBA',(1536,256),(64,68,72,255));dr=ImageDraw.Draw(b)
for j,i in enumerate([3,0,1,2,3,0]):
 b.alpha_composite(out.crop((512*i,0,512*(i+1),512)).resize((256,256),Image.Resampling.LANCZOS),(j*256,0));dr.text((j*256+5,5),str(17+i),fill='white')
b.save(D/'loop20-17-18-19-20-17-true2x.png')
# Pixel differences only: no inference of independent animation from texture noise.
pairs=[]
for i,j in itertools.combinations(range(4),2):
 aa=np.array(out.crop((i*512,0,(i+1)*512,512)));bb=np.array(out.crop((j*512,0,(j+1)*512,512)));pairs.append({'a':17+i,'b':17+j,'different_rgba_pixels':int(np.any(aa!=bb,axis=2).sum())})
dump(P/'pixel-distinctness.json',{'pairs':pairs,'boundary':'Different pixels do not prove correct animation; compare source pose and surface contour changes.'})
# Optional review GIF only; frames at existing 12ticks*20ms adapter rate, not a runtime test.
g=[]
for i in range(4):
 bg=Image.new('RGBA',(512,512),(64,68,72,255));bg.alpha_composite(out.crop((512*i,0,512*(i+1),512)));g.append(bg.convert('RGB'))
g[0].save(D/'idle-reference-cadence-review.gif',save_all=True,append_images=g[1:],duration=240,loop=0)
print(json.dumps({'scale':s,'minimum_raw_density':min(r['raw_density_vs_source72'] for r in rows),'max_anchor_residual':max(r['max_anchor_residual_norm'] for r in rows)},indent=2))
