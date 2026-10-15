from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil
P=Path(__file__).resolve().parent;A=P.parent;D=P.parents[1]/'diagnostics/earth_hero_e_49_arm_edit_plan_v1';D.mkdir(parents=True,exist_ok=True)
src=Image.open(A/'earth_hero_e_input_plan_v1/source-49.png').convert('RGBA')
shutil.copy2(A/'earth_hero_e_49_control_v2/raw.png',P/'edit-base-raw49-UNCHANGED.png')
src.resize((1024,1024),Image.Resampling.NEAREST).save(P/'source49-full128-8x.png')
crop=(24,24,58,62);k=16;tile=src.crop(crop).resize((544,608),Image.Resampling.NEAREST)
b=Image.new('RGBA',(1200,760),(49,53,57,255));b.alpha_composite(tile,(16,52));b.alpha_composite(tile,(640,52));dr=ImageDraw.Draw(b)
dr.text((16,16),'SOURCE49 actual pixels; same crop / same scale',fill='white')
dr.text((640,16),'VISIBLE SURFACE REGIONS, not joints',fill='white')
regions={'sleeve surface (approx)':([34,39,43,51],(65,210,235)),'cuff / wrist transition':([35,50,43,54],(235,150,55)),'hand group envelope':([40,53,46,59],(245,120,200)),'waist reference band':([43,47,50,51],(140,220,120))}
for name,(r,c) in regions.items():
 q=[640+(r[0]-24)*k,52+(r[1]-24)*k,640+(r[2]-24)*k,52+(r[3]-24)*k];dr.rectangle(q,outline=c,width=2)
for i,(name,(r,c)) in enumerate(regions.items()):dr.text((16+(i%2)*590,680+(i//2)*25),name+' '+str(r),fill=c)
dr.text((16,739),'Boxes approximate; hidden elbow UNKNOWN. Hand is BELOW waist band, not chest-high.',fill='white')
b.save(P/'source49-sleeve-wrist-hand-regions.png')
raw=Image.open(P/'edit-base-raw49-UNCHANGED.png').convert('RGBA');b=Image.new('RGBA',raw.size,(64,68,72,255));b.alpha_composite(raw);dr=ImageDraw.Draw(b);dr.rectangle((330,365,485,580),outline=(245,120,200),width=3);dr.text((500,380),'Arm edit envelope only; torso inside is protected',fill='white');dr.text((500,405),'No pixel mask supplied; preserve all other anatomy',fill='white');b.save(D/'proposed-local-envelope.png')
meta={'edit_target':'edit-base-raw49-UNCHANGED.png','source_crop':crop,'nearest_scale':16,'source_region_boxes':{n:r for n,(r,c) in regions.items()},'raw_edit_envelope_context_not_mask':[330,365,485,580],'source_boxes_uncertainty':'approx +/-2 to3 logical px, overlapping surface categories; no joint centers','raw_envelope_note':'near black sleeve below shoulder, forearm guard, glove and minimal revealed underlying surface only; torso inside envelope is not globally editable','inputs':[{'path':f,'sha256':hashlib.sha256((P/f).read_bytes()).hexdigest()} for f in ['edit-base-raw49-UNCHANGED.png','source49-full128-8x.png','source49-sleeve-wrist-hand-regions.png']]}
(P/'INPUT_PROVENANCE.json').write_text(json.dumps(meta,indent=2)+'\n')
