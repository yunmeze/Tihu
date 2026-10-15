from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil
P=Path(__file__).resolve().parent;A=P.parent;D=P.parents[1]/'diagnostics/earth_hero_e_walk_edit_plan_v1';D.mkdir(parents=True,exist_ok=True)
shutil.copy2(A/'earth_hero_e_walk_v2/raw-v2.png',P/'edit-base-v2-UNCHANGED.png')
shutil.copy2(A/'earth_hero_e_walk_plan_v2/source45-50-full128-equal-grid-4x.png',P/'source45-50-full128-equal-grid-4x.png')
rows=json.loads((A/'earth_hero_e_input_plan_v1/SOURCE_PHASE_ANALYSIS.json').read_text())['walk']
B=Image.new('RGBA',(1800,1800),(42,46,50,255));meta=[]
for i,row in enumerate(rows):
 n=45+i;src=Image.open(A/'earth_hero_e_input_plan_v1'/f'source-{n}.png').convert('RGBA');tile=Image.new('RGBA',(600,900),(42,46,50,255));d=ImageDraw.Draw(tile)
 d.text((14,12),f'{n} ORIGINAL ONLY: low sleeve + legs',fill='white')
 # Equal crops/scales across all6; actual source unchanged under annotations.
 tile.alpha_composite(src.crop((24,24,58,62)).resize((340,380),Image.Resampling.NEAREST),(16,48))
 hand=row['visible_hand_surface_proxies'][0];h=[hand[0]-3,hand[1]-3,hand[0]+3,hand[1]+3];waist=[43,47,50,51]
 for box,c in [(h,(245,130,220)),(waist,(130,230,160))]:
  q=[16+(box[0]-24)*10,48+(box[1]-24)*10,16+(box[2]-24)*10,48+(box[3]-24)*10];d.rectangle(q,outline=c,width=2)
 d.text((370,70),'Pink: hand GROUP',fill=(245,130,220));d.text((370,95),'Green: waist band',fill=(130,230,160));d.text((370,130),'Approx +/-3 source px',fill='white')
 d.text((370,165),'Read actual sleeve',fill='white');d.text((370,190),'descending contour.',fill='white');d.text((370,225),'No hidden elbow.',fill='white')
 d.text((16,445),'45/50 near arm PRESERVE' if n in [45,50] else '46-49: low forward sleeve/wrist/hand; NOT high horizontal fist',fill='white')
 tile.alpha_composite(src.crop((12,58,68,92)).resize((448,272),Image.Resampling.NEAREST),(16,488))
 leg={}
 for key,c in [('screen_left_boot_chain',(80,215,250)),('screen_right_boot_chain',(250,180,60))]:
  chain=row['visible_lower_chains'][key];ps=[chain['ankle_outer_surface_proxy'],chain['boot_tip']];leg[key]=ps
  for j,p in enumerate(ps):
   x=16+(p[0]-12)*8;y=488+(p[1]-58)*8;d.rectangle((x-8,y-8,x+8,y+8),outline=c,width=2);d.text((x+10,y),'ankle~' if j==0 else 'toe~',fill=c)
 notes={45:'EDIT spread shorter; preserve small right-lower ordering.',46:'PRESERVE leg chain; inspect only.',47:'PRESERVE separated passing feet; inspect only.',48:'EDIT spread shorter; preserve opposite toe ordering.',49:'EDIT short tucked RIGHT shin/ankle; LEFT toe lower.',50:'EDIT narrower passing; RIGHT toe lower.'}
 d.text((16,790),notes[n],fill='white');d.text((16,820),'Colored regions are surfaces, not joints/contact.',fill='white');d.text((16,850),'Original shadow remains evidence; do NOT generate a shadow.',fill='white')
 B.paste(tile,(i%3*600,i//3*900));meta.append({'source_id':n,'hand_group_region':h,'waist_reference_approx':waist,'ankle_toe_proxies':leg})
B.save(P/'source-sixphase-sleeve-waist-leg-regions.png')
regions={45:{'legs':[55,296,405,486]},46:{'near_arm':[184,163,291,312]},47:{'near_arm':[210,164,327,310]},48:{'legs':[55,296,405,493],'near_arm':[155,163,343,315]},49:{'right_shin_ankle_boot':[224,338,329,480],'near_arm':[182,164,319,320]},50:{'passing_legs':[185,300,335,492]}}
base=Image.open(P/'edit-base-v2-UNCHANGED.png').convert('RGBA');diag=Image.new('RGBA',base.size,(64,68,72,255));diag.alpha_composite(base);d=ImageDraw.Draw(diag)
for n,rs in regions.items():
 ox=(n-45)%3*512;oy=(n-45)//3*512
 for label,r in rs.items():d.rectangle((r[0]+ox,r[1]+oy,r[2]+ox,r[3]+oy),outline=(245,130,220) if 'arm' in label else (80,215,250),width=2);d.text((ox+8,oy+8),str(n)+' context envelopes, NOT masks',fill='white')
diag.save(D/'proposed-context-envelopes.png')
fs=['edit-base-v2-UNCHANGED.png','source45-50-full128-equal-grid-4x.png','source-sixphase-sleeve-waist-leg-regions.png']
j={'status':'prepared_not_generated','inputs':[{'path':f,'sha256':hashlib.sha256((P/f).read_bytes()).hexdigest()} for f in fs],'source_regions':meta,'source_upper_crop':[24,24,58,62],'upper_nearest_scale':10,'source_lower_crop':[12,58,68,92],'lower_nearest_scale':8,'base_cell_local_context_envelopes':regions,'note':'envelopes are inspection context, not masks; torso within arm rectangles protected; no programmatic final-art editing'}
(P/'INPUT_PROVENANCE.json').write_text(json.dumps(j,indent=2)+'\n')
