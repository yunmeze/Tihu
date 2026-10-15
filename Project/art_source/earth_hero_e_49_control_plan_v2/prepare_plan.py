from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil
P=Path(__file__).resolve().parent;A=P.parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
src=A/'earth_hero_e_input_plan_v1/source-49.png';im=Image.open(src).convert('RGBA');im.resize((1024,1024),Image.Resampling.NEAREST).save(P/'source49-full128-8x.png')
crop=(16,32,64,96);s=12;b=Image.new('RGBA',(960,768),(35,39,44,255));b.alpha_composite(im.crop(crop).resize((576,768),Image.Resampling.NEAREST));d=ImageDraw.Draw(b)
def xy(p):return ((p[0]-16)*s,(p[1]-32)*s)
def pt(p,label,color):
 x,y=xy(p);d.ellipse((x-5,y-5,x+5,y+5),fill=color);d.text((x+9,y-10),label,fill=color)
def dash(a,c,color):
 a=xy(a);c=xy(c)
 for k in range(0,20,2):
  d.line((a[0]+(c[0]-a[0])*k/20,a[1]+(c[1]-a[1])*k/20,a[0]+(c[0]-a[0])*(k+1)/20,a[1]+(c[1]-a[1])*(k+1)/20),fill=color,width=2)
left=[[34,66],[26,76],[31,83]];right=[[44,64],[40,75],[48,77]]
for chain,color in [(left,(70,220,255)),(right,(255,190,70))]:
 for a,c in zip(chain,chain[1:]):dash(a,c,color)
 for p,label in zip(chain,['K~ cloth','A~ region','TOE region']):pt(p,label,color)
# Approximate torso-front band projected downward: an image-space aid, never an invented contact plane.
dash([48,37],[48,85],(160,200,160))
pt([43,56],'visible near HAND',(245,140,230))
lines=['49 ONLY: ANALYSIS, not output art','Cyan: left screen visible chain','Orange: right screen visible chain','','OBSERVED: right ankle stays inward','Right visible shin segment compact','Right toe near torso-front projection','Left ankle -> toe points DOWN-RIGHT','Left toe lower on screen, NOT load','','MEDIUM interpretation: fuller left','trouser/knee surface continues back;','right upper chain partly overlapped.','','Green guide: approximate front edge','NOT a floor or skeleton constraint.','Dashed chains are surface proxies.','Knee +/-3; ankle +/-3; toe +/-2 px.','Do not force hidden joints or flat sole.']
for i,t in enumerate(lines):d.text((585,20+i*28),t,fill='white' if i!=14 else (160,200,160))
b.save(P/'source49-visible-chain-occlusion-analysis.png')
shutil.copyfile(A/'earth_hero_e_walk_plan_v2/approved-E-idle9-design-with-forearm.png',P/'approved-E-design-only.png')
j={'status':'source_preparation_no_generation','source_sha256':sha(src),'full_canvas':[128,128],'root':[16,64],'full_display_scale':8,'analysis_crop':crop,'analysis_scale':12,'observed_proxies':{'left_knee_cloth':[34,66],'left_ankle_region':[26,76],'left_toe_region':[31,83],'right_knee_cloth':[44,64],'right_ankle_region':[40,75],'right_toe_region':[48,77]},'approximate_graphic_relation':'right toe x~48 lies near torso front contour projection x~48, not anatomical or calibrated 3D','medium_confidence_inference':'more complete foreground trouser/knee surface continues into left/rear screen chain; obscured right upper segment not reconstructed','unknown':['anatomical left/right','physical load/contact','hidden joints','3D depth'],'inputs':[{'path':f.name,'sha256':sha(f)} for f in sorted(P.glob('*.png'))]};(P/'INPUT_PROVENANCE.json').write_text(json.dumps(j,indent=2)+'\n')
(P/'GIT_SAVE_MANIFEST.json').write_text(json.dumps({'files':[{'path':f.name,'sha256':sha(f)} for f in sorted(P.iterdir()) if f.is_file() and f.name!='GIT_SAVE_MANIFEST.json'],'generation_called':False},indent=2)+'\n')
