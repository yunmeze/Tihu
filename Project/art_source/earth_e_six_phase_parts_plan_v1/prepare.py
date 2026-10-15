from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[1];D=R/'diagnostics/earth_e_six_phase_parts_plan_v1';D.mkdir(parents=True,exist_ok=True)
V=R/'art_source/earth_hero_e_walk_v2';reg=json.loads((V/'registration-v2.json').read_text());raw=Image.open(V/'raw-v2.png').convert('RGBA');s=reg['common_uniform_scale_raw_to_logical']
pts={45:[[40,16],[33,64],[22,73],[29,78],[49,65],[49,80],[60,81],[33,57]],46:[[39,16],[32,65],[26,72],[31,77],[43,65],[40,84],[48,87],[37,56]],47:[[40,15],[36,64],[33,80],[42,87],[46,61],[43,74],[51,78],[44,56]],48:[[40,16],[38,66],[23,78],[29,84],[49,64],[49,75],[60,74],[49,56]],49:[[39,16],[34,66],[26,76],[31,83],[44,64],[40,75],[48,77],[43,56]],50:[[40,15],[34,61],[32,76],[41,80],[47,64],[42,81],[51,86],[36,57]]}
board=Image.new('RGBA',(1536,4*550),(105,105,105,255));sources=[]
for row,f in enumerate([45,47,48,50]):
 sp=R/f'diagnostics/earth_e_source_shadow_index_audit_v1/{f}-index18-excluded-NOT-SEMANTICALLY-CERTIFIED.png';src=Image.open(sp).convert('RGBA');sources.append(sp);record=next(x for x in reg['records'] if x['source_id']==f);cell=raw.crop(record['raw_rect']);tx,ty=record['translation_logical'];old=cell.transform((512,512),Image.Transform.AFFINE,(1/(s*4),0,-tx/s,0,1/(s*4),-ty/s),resample=Image.Resampling.BICUBIC)
 annotated=src.resize((512,512),Image.Resampling.NEAREST);dr=ImageDraw.Draw(annotated)
 for j,p in enumerate(pts[f]):
  x,y=[v*4 for v in p];col=(255,90,130,255) if j==7 else (60,230,230,255)
  dr.rectangle((x-4,y-4,x+4,y+4),outline=col,width=2)
 # Boxes are evidence windows only, not approved art editing masks.
 dr.rectangle((25*4,48*4,55*4,62*4),outline=(255,90,130,255),width=2)
 dr.rectangle((19*4,59*4,63*4,89*4),outline=(255,215,70,255),width=2)
 for i,im in enumerate([src.resize((512,512),Image.Resampling.NEAREST),annotated,old]):board.alpha_composite(im,(512*i,row*550+28))
 ImageDraw.Draw(board).text((8,row*550+7),f'{f}: SOURCE full128 | visible surface proxies / evidence windows | v2 original fixed-density registration',fill='white')
board.save(D/'source-v2-four-phase-evidence.png')
# Whole six frames retain original canvas, including crown bob. No final body drawing.
six=Image.new('RGBA',(1536,1024),(105,105,105,255))
for i,f in enumerate(range(45,51)):
 sp=R/f'diagnostics/earth_e_source_shadow_index_audit_v1/{f}-index18-excluded-NOT-SEMANTICALLY-CERTIFIED.png';im=Image.open(sp).convert('RGBA').resize((512,512),Image.Resampling.NEAREST);six.alpha_composite(im,(i%3*512,i//3*512));ImageDraw.Draw(six).text((i%3*512+8,i//3*512+8),str(f),fill='white')
six.save(D/'source-six-full128-fixed-grid.png')
(P/'SOURCE_PROXIES.json').write_text(json.dumps({'order':['crown','left_screen_knee_surface','left_screen_ankle_region','left_screen_toe','right_screen_knee_surface','right_screen_ankle_region','right_screen_toe','near_hand_region'],'frames':pts,'uncertainty_logical':{'crown':1,'knees_ankles_hand':3,'toe':2},'not_hidden_bones_or_contact_state':True,'v2_density':s},indent=2)+'\n')
inputs=sources+[V/'raw-v2.png',V/'registration-v2.json',R/'art_source/earth_e_46_knee_join_v2/46-HD4-RIGID-JOIN-RESEARCH.png',R/'art_source/earth_e_46_49_static_research_v1/49-HD4-STATIC-RESEARCH.png']
(P/'INPUT_SHA.json').write_text(json.dumps([{'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in inputs],indent=2)+'\n')
