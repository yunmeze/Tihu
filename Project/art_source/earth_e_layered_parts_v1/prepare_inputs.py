from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil
P=Path(__file__).resolve().parent;A=P.parent
S=P.parents[1]/'diagnostics/earth_e_source_shadow_index_audit_v1'
ims={n:Image.open(S/f'{n}-index18-excluded-NOT-SEMANTICALLY-CERTIFIED.png').convert('RGBA') for n in [46,49]}
# Technical layout windows, not masks for final art. Source geometry remains unwarped.
layout=Image.new('RGBA',(2304,1536),(35,39,44,255));regions=[('CORE shared',46,[30,14,51,53]),('ARM46',46,[28,28,43,59]),('ARM49',49,[32,28,49,59]),('LOWER46',46,[20,47,53,91]),('LOWER49',49,[20,47,53,91])]
for i,(label,n,r) in enumerate(regions):
 tile=Image.new('RGBA',(128,128));tile.paste(ims[n].crop(r),(r[0],r[1]));tile=tile.resize((768,768),Image.Resampling.NEAREST);x=i%3*768;y=i//3*768;layout.alpha_composite(tile,(x,y));d=ImageDraw.Draw(layout);d.text((x+15,y+15),label+' : same128 coordinates, no zoom',fill='white');d.text((x+15,y+710),'Window is context, NOT exact part edge / anatomy.',fill='white')
d=ImageDraw.Draw(layout);d.text((1550,800),'EMPTY cell6: leave TRANSPARENT in output',fill='white')
layout.save(P/'five-part-full128-layout-GUIDE.png')
shutil.copy2(A/'earth_e_layered_46_49_plan_v1/source46-left49-right-full128-6x.png',P/'source46-49-fullgeometry.png');shutil.copy2(A/'earth_e_layered_46_49_plan_v1/approved-E-idle-design-only.png',P/'approved-E-design-only.png')
prompt="""Generate ONE transparent coordinated 2D cutout COMPONENT SHEET, exactly3 columns x2 rows of equal full128-coordinate cells. Layout image1: CORE(shared), ARM46, ARM49 / LOWER46, LOWER49, EMPTY. All5 pieces at ONE TRUE BODY SCALE and original coordinate placement; small arms must stay small, NOT individually zoomed to fill cells. No assembled full characters in output.
Image1 is a technical WINDOW layout, not precise cut masks: remove any neighboring body visible in each window. Image2 supplies original complete46/49 geometry and occlusion ONLY, not old clothing. Image3 is the ONLY costume identity: adult short black-haired E-facing man, compact silver chest/abdomen, restrained red shoulder, black LONG sleeves, matching silver forearm guards/gloves, BLACK thighs with SMALL side plates, same knee/shin/boots.
CORE: head,neck,complete torso/back,red shoulder cover and waist/belt ONLY, no arms below shoulder/no legs. Actually paint the small torso surfaces revealed when near arm is removed, with matching black/silver materials. Keep core suitable for both poses.
ARM46 / ARM49: each ONE complete visible upper-sleeve-to-forearm-guard-to-glove cutout, no torso/legs, no duplicate red shoulder plate.46 hand low near x37,y56;49 low modestly forward near x43,y56. Descending forearms, NOT horizontal high fists. Extend each upper sleeve slightly under the common red shoulder cover.
LOWER46 / LOWER49: each ONE complete pelvis+both trouser legs+shin armor+both boots, no torso or hands. Extend waistband slightly under common belt.46 left toe at31,77 and right48,87;49 left31,83 and right48,77 in logical cells.49 RIGHT visible shin must be short/tucked under torso front; left ankle above-left of its toe. Do NOT copy46 chains into49, and do not widen the compact17px toe spread. Preserve actual visible knee/shin outlines and overlap from image2.
Shared body crown reference39,16; root16,64. Hidden shoulder/waist overlap allowance2–3 logical pixels is an AUTHORING ASSUMPTION, not invented skeleton. Keep all five compatible with one scale; do not normalize each part size. Real finely rendered pixels, not pixel-art upscale. Source white clothes/waist stripes and guide colors/text must not appear. Fixed warm upper-left light, genuine clean transparency, NO shadows,glow,haze,labels,guides,weapons or extra parts. Sixth cell entirely transparent."""
(P/'prompt.txt').write_text(prompt+'\n')
fs=[P/f for f in ['five-part-full128-layout-GUIDE.png','source46-49-fullgeometry.png','approved-E-design-only.png']]
(P/'request.json').write_text(json.dumps({'tool_arguments':{'prompt':prompt+'\n','referenced_image_paths':[str(f.resolve()) for f in fs],'transparent_background':True},'input_sha256':{str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in fs},'guide_windows':regions,'guide_limit':'source actual pixels in windows; not segmentation; hidden join extension2-3px is authoring assumption','coordinate':'full128 cell at6x, shared root16,64; no zoom'},indent=2)+'\n')
