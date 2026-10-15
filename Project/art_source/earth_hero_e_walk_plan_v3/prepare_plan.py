from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil
P=Path(__file__).resolve().parent;A=P.parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=json.loads((A/'earth_hero_e_input_plan_v1/SOURCE_PHASE_ANALYSIS.json').read_text())['walk']
shutil.copyfile(A/'earth_hero_e_walk_plan_v2/source45-50-full128-equal-grid-4x.png',P/'source45-50-full128-equal-grid-4x.png')
shutil.copyfile(A/'earth_hero_e_walk_plan_v2/approved-E-idle9-design-with-forearm.png',P/'approved-E-design-only.png')
board=Image.new('RGBA',(2304,1536),(35,39,44,255))
for i,row in enumerate(rows):
 n=row['source_id'];im=Image.open(A/'earth_hero_e_input_plan_v1'/f'source-{n}.png').convert('RGBA');b=Image.new('RGBA',(768,768),(35,39,44,255));b.alpha_composite(im.resize((768,768),Image.Resampling.NEAREST));d=ImageDraw.Draw(b)
 def pt(p,label,c):
  x,y=p[0]*6,p[1]*6;d.ellipse((x-4,y-4,x+4,y+4),fill=c);d.text((x+7,y-6),label,fill=c)
 def chain(ps,c):
  for a,z in zip(ps,ps[1:]):
   for k in range(0,10,2):d.line((6*(a[0]+(z[0]-a[0])*k/10),6*(a[1]+(z[1]-a[1])*k/10),6*(a[0]+(z[0]-a[0])*(k+1)/10),6*(a[1]+(z[1]-a[1])*(k+1)/10)),fill=c,width=2)
 for name,c in [('screen_left_boot_chain',(70,220,255)),('screen_right_boot_chain',(255,190,70))]:
  rr=row['visible_lower_chains'][name];ps=[rr['knee_clothing_fold_proxy'],rr['ankle_outer_surface_proxy'],rr['boot_tip']];chain(ps,c)
  for p,l in zip(ps,['K~','A~','TOE~']):pt(p,l,c)
 hands=row['visible_hand_surface_proxies'];pt(hands[0],'NEAR HAND',(245,140,230))
 if hands[1]:pt(hands[1],'far fragment',(150,240,170))
 d.text((425,30),f'{n}: SOURCE ONLY ANALYSIS',fill='white');d.text((425,60),f'Near hand: {hands[0]}',fill=(245,140,230));d.text((425,90),'Far hand: fragment' if hands[1] else 'Far endpoint: UNKNOWN',fill='white');d.text((425,120),'No hidden elbow or bones added',fill='white');d.text((425,160),'Leg AND sleeve shape both required',fill='white');d.text((425,190),'Boot height is NOT ground contact',fill='white');d.text((425,230),'Cyan:left / orange:right screen chain',fill='white')
 board.paste(b,(i%3*768,i//3*768))
board.save(P/'source45-50-visible-chain-hand-analysis.png')
(P/'INPUT_PROVENANCE.json').write_text(json.dumps({'status':'prepared_not_generated','inputs':[{'path':p.name,'sha256':sha(p)} for p in sorted(P.glob('*.png'))],'sole_pose_authority':'original45-50 each independently','generated49_input':False,'generated49_role':'textual method finding only for phase49; no candidate raw used','hand_checks':'source visible hand groups and sleeves, not crown-to-hand bone angles','unknown_joints':'not reconstructed'},indent=2)+'\n')
(P/'GIT_SAVE_MANIFEST.json').write_text(json.dumps({'files':[{'path':p.name,'sha256':sha(p)} for p in sorted(P.iterdir()) if p.is_file() and p.name!='GIT_SAVE_MANIFEST.json'],'generation_called':False},indent=2)+'\n')
