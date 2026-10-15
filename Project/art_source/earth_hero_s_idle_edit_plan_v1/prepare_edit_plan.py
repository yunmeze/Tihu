from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[1];D=R/'diagnostics/earth_hero_s_idle_edit_plan_v1';D.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parts={
 'SE13':('se_idle_v1',{'chest_black_abdomen_waist':(131,112,202,202),'black_thigh_small_plate':(125,190,169,251)}),
 'E9':('e_idle_v1',{'chest_black_abdomen_waist':(148,109,191,193),'black_thigh_small_plate':(142,192,182,244)})}
refs=[];b=Image.new('RGBA',(600,220));dr=ImageDraw.Draw(b)
for i,(label,(folder,crops)) in enumerate(parts.items()):
 p=R/'assets/earth/hero'/folder/'body.png';im=Image.open(p).convert('RGBA')
 for j,(name,rect) in enumerate(crops.items()):
  b.alpha_composite(im.crop(rect),(i*300+j*150+20,45));dr.text((i*300+j*150+4,8),label+' '+('torso' if j==0 else 'thigh'),fill='white')
 refs.append({'path':str(p.relative_to(R)),'sha256':sha(p),'crop_rectangles_xyxy_native_hd4':crops})
b.save(P/'approved-SE-E-torso-thigh-fragments.png')
raw=P.parent/'earth_hero_s_idle_v1/raw-v1.png';im=Image.open(raw).convert('RGBA');bg=Image.new('RGBA',im.size,(64,68,72,255));bg.alpha_composite(im);dr=ImageDraw.Draw(bg)
# Broad garment-only proposals, not a pixel mask or anatomical landmark.
rois={'abdomen_waist':[219,240,310,337],'screen_left_thigh_plate':[185,347,237,431],'screen_right_thigh_plate':[307,347,355,431]}
for i in range(4):
 for name,rect in rois.items():
  x0,y0,x1,y1=rect;dr.rectangle((i*543+x0,y0,i*543+x1,y1),outline=(255,180,30),width=2)
bg.save(D/'proposed-clothing-areas-not-a-mask.png')
contract={'status':'plan_only_not_approved_for_edit','edit_target':str(raw.relative_to(R)),'edit_target_sha256':sha(raw),'reference_parts':refs,'proposed_local_cell_rois':rois,'roi_boundary':'broad clothing area guide only; not tool-enforced mask; do not alter hands or outer body silhouette','constraints':['one whole four-frame edit only after parent approval','same2172x724 canvas and543x724 cells','face, hair, posture, hands, boots, lighting, frame placement unchanged','only reduce continuous silver abdomen chain and outer thigh plates','preserve original raw and use identical global registration for edited candidate; no refit to hide movement drift']}
(P/'EDIT_INPUT_CONTRACT.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n')
files=[x for x in sorted(P.iterdir()) if x.is_file() and x.name!='MINIMAL_SHA_MANIFEST.json'];(P/'MINIMAL_SHA_MANIFEST.json').write_text(json.dumps({'files':[{'path':x.name,'sha256':sha(x)} for x in files],'target_sha256':sha(raw),'diagnostics_excluded':True},ensure_ascii=False,indent=2)+'\n')
