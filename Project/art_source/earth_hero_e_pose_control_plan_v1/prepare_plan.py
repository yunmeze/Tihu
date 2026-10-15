from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil
P=Path(__file__).resolve().parent;A=P.parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();frames={45:{'crown':[40,16],'near_shoulder_cloth_proxy':[37,31],'near_elbow_cloth_proxy_uncertain':[33,43],'near_hand_surface':[33,57],'left_chain':[[33,64],[22,73],[29,78]],'right_chain':[[49,65],[49,80],[60,81]],'far_hand':[49,40]},49:{'crown':[39,16],'near_shoulder_cloth_proxy':[36,31],'near_elbow_cloth_proxy_uncertain':[38,44],'near_hand_surface':[43,56],'left_chain':[[34,66],[26,76],[31,83]],'right_chain':[[44,64],[40,75],[48,77]],'far_hand':None}}
board=Image.new('RGBA',(256,128))
for i,(n,pts) in enumerate(frames.items()):
 src=A/'earth_hero_e_input_plan_v1'/f'source-{n}.png';im=Image.open(src).convert('RGBA');board.paste(im,(128*i,0));im.resize((1024,1024),Image.Resampling.NEAREST).save(P/f'source-{n}-full128-8x.png')
 sc=6;bg=Image.new('RGBA',(768,768),(35,39,44,255));bg.alpha_composite(im.resize((768,768),Image.Resampling.NEAREST));d=ImageDraw.Draw(bg)
 def point(p,label,col):
  x,y=[q*sc for q in p];d.ellipse((x-4,y-4,x+4,y+4),fill=col);d.text((x+7,y-7),label,fill=col)
 def chain(ps,col):
  # Dashed visible-surface paths, deliberately not solid bones.
  for a,b in zip(ps,ps[1:]):
   for k in range(0,10,2):
    a1=[(a[c]+(b[c]-a[c])*k/10)*sc for c in [0,1]];b1=[(a[c]+(b[c]-a[c])*(k+1)/10)*sc for c in [0,1]];d.line(a1+b1,fill=col,width=2)
 for side,col in [('left_chain',(80,220,255)),('right_chain',(255,190,70))]:
  chain(pts[side],col)
  for q,label in zip(pts[side],['K~','A~','BOOT']):point(q,label,col)
 arm=[pts['near_shoulder_cloth_proxy'],pts['near_elbow_cloth_proxy_uncertain'],pts['near_hand_surface']];chain(arm,(245,140,230))
 for q,label in zip(arm,['S~ cloth','E? +/-4','HAND']):point(q,label,(245,140,230))
 point([16,64],'ROOT (not foot)','white')
 if pts['far_hand']:point(pts['far_hand'],'far fragment',(150,250,150))
 d.text((420,35),f'FRAME {n}: ANALYSIS ONLY',fill='white');d.text((420,60),'Dashed = visible surface proxies',fill='white');d.text((420,80),'NOT bones / NOT ground contacts',fill='white');d.text((420,115),'cyan: screen-left boot chain',fill=(80,220,255));d.text((420,135),'orange: screen-right boot chain',fill=(255,190,70));d.text((420,170),'49: left boot LOWER; right HIGHER' if n==49 else '45: dx31 only; right boot LOWER3',fill='white');d.text((420,195),'Far hand endpoint UNKNOWN' if n==49 else 'Small far hand fragment visible',fill='white');d.text((420,225),'No invented hidden-joint line',fill='white');bg.save(P/f'source-{n}-annotated-analysis.png')
board.resize((1536,768),Image.Resampling.NEAREST).save(P/'source45-and49-full128-pair-6x.png')
shutil.copyfile(A/'earth_hero_e_walk_plan_v2/approved-E-idle9-design-with-forearm.png',P/'approved-E-design-parts.png')
(P/'CONTROL_POINTS.json').write_text(json.dumps({'status':'analysis_only_not_generated_art','frames':frames,'uncertainty_logic_px':{'boot':2,'hand':3,'shoulder_cloth':3,'elbow_cloth':4,'knee_ankle_cloth':3},'reading_boundary':'screen-low boot is only a support candidate, not proved physical contact; no anatomical left/right or hidden skeleton inferred','inputs':[{'path':p.name,'sha256':sha(p)} for p in sorted(P.glob('*.png'))]},indent=2)+'\n')
(P/'GIT_SAVE_MANIFEST.json').write_text(json.dumps({'files':[{'path':p.name,'sha256':sha(p)} for p in sorted(P.iterdir()) if p.is_file() and p.name!='GIT_SAVE_MANIFEST.json'],'generation_called':False},indent=2)+'\n')
pair=Image.new('RGBA',(1536,768))
for i,n in enumerate([45,49]):pair.paste(Image.open(P/f'source-{n}-annotated-analysis.png'),(i*768,0))
pair.save(P/'source45-and49-annotated-pair.png')
(P/'GIT_SAVE_MANIFEST.json').write_text(json.dumps({'files':[{'path':p.name,'sha256':sha(p)} for p in sorted(P.iterdir()) if p.is_file() and p.name!='GIT_SAVE_MANIFEST.json'],'generation_called':False},indent=2)+'\n')
