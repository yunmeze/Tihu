from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,shutil
P=Path(__file__).resolve().parent;R=P.parents[1];D=R/'diagnostics/earth_e_upper45_47_v1';D.mkdir(parents=True,exist_ok=True);S=R/'art_source/earth_e_four_phase_rigid_study_v1'
polys={45:[(32,46),(47,46),(51,54),(54,63),(49,68),(48,73),(39,73),(37,67),(31,65),(25,65),(28,58)],47:[(32,45),(47,45),(50,54),(50,62),(49,68),(41,69),(40,73),(30,73),(30,65),(30,55)]}
box=(20,44,58,75);scale=20;srcboard=Image.new('RGBA',(1520,620),(110,110,110,255));guide=srcboard.copy()
B=Image.open(R/'diagnostics/earth_e_49_cloth_patch_v1/layer49-core-back.png');F=Image.open(R/'diagnostics/earth_e_49_cloth_patch_v1/layer49-core-front.png')
rec=json.loads((S/'GEOMETRY.json').read_text())['records'];params={}
for i,f in enumerate([45,47]):
 src=Image.open(R/f'diagnostics/earth_e_source_shadow_index_audit_v1/{f}-index18-excluded-NOT-SEMANTICALLY-CERTIFIED.png');srcboard.alpha_composite(src.crop(box).resize((760,620),Image.Resampling.NEAREST),(i*760,0))
 shift=(4,0) if f==45 else (4,-4);base=Image.new('RGBA',(512,512))
 for side in ['left','right']:base.alpha_composite(Image.open(S/f'{f}-{side}-rigid-HD4.png'))
 for im in [B,F]:base.alpha_composite(im,shift)
 crop=base.crop(tuple(x*4 for x in box)).resize((760,620),Image.Resampling.NEAREST);guide.alpha_composite(crop,(i*760,0));dr=ImageDraw.Draw(guide)
 cv=lambda p:(i*760+(p[0]-20)*20,(p[1]-44)*20)
 dr.polygon([cv(p) for p in polys[f]],outline='magenta',width=3)
 # visible interfaces, not hidden bones
 roots=[z['new_cut_proxy'] for z in rec[str(f)]['moves']]
 for x,y in roots:dr.rectangle((cv((x-3,y-2))+cv((x+3,y+2))),outline='cyan',width=3)
 dr.rectangle(cv((33,46 if f==45 else 45))+cv((47,49 if f==45 else 48)),outline='yellow',width=3)
 dr.text((i*760+8,8),f'upper{f}: magenta allowed; yellow waist; cyan cuff interface',fill='white')
 mask=Image.new('L',(512,512));ImageDraw.Draw(mask).polygon([(round(x*4),round(y*4)) for x,y in polys[f]],fill=255);mask.save(P/f'{f}-fixed-support-HD4-mask.png')
 params[f]={'support_polygon_logical':polys[f],'waist_overlap_logical':[33,46 if f==45 else 45,47,49 if f==45 else 48],'cuff_centers':roots,'cuff_overlap_assumption_halfheight':2,'core_shift_HD4':shift,'source_knee_proxies':[z['source_knee_ankle_toe'][0] for z in rec[str(f)]['moves']]}
srcboard.save(P/'input-source45-47-fixed-crop.png');guide.save(P/'input-interfaces-support.png')
shutil.copyfile(R/'art_source/earth_e_layered_parts_v1/approved-E-design-only.png',P/'input-approved-identity.png')
(P/'LAYOUT.json').write_text(json.dumps({'status':'pre-generation frozen support; not hidden anatomical model','two_cells':[[0,0,760,620],[760,0,1520,620]],'logical_context':box,'input_pixels_per_logical':20,'intended_mapping':'one sheet common density 38/(raw width/2), target origin(20,44) each cell; if geometry drifts report, never separately fit','params':params,'limits':'source knee proxies differ from frozen armor interface centers; visible cloth transition is authoring hypothesis, not proof of original anatomy; cuff overlap only 2 logical px'},indent=2)+'\n')
prompt="""Generate ONE transparent two-cell sprite PARTS sheet, left upper45 and right upper47, coordinated matching assets. Each equal cell uses precisely the same logical crop and pixel density as inputs 1 and 2. Do not independently enlarge either piece to fill space. Output only two separate BLACK FABRIC UPPER-PANTS pieces from waist insertion to knee-cuff interfaces: no head, torso, arms, hands, belt, side armor, shin armor or boots.
Input1 is the original visible pose authority: left short spread-step pants, right narrow passing-step pants. Preserve each distinct visible thigh/crotch silhouette; do not copy one into the other. Do not copy original white clothing or silver waist stripe. Input2 is ONLY a technical attachment guide: magenta maximum support, yellow hidden waist insertion 2–3 logical units, cyan frozen lower-module joining zones with only 2 units hidden overlap. Existing armor/core shown there are context and must NOT appear in output. The knees are visible surface regions, not invented hidden bones. Keep compact black thighs; no big side plates.
Input3 is the only costume/material reference. Match detailed black woven/soft armored fabric, restrained seams, coherent upper-left warm light, no gold trim. Make genuine high-definition painted 2D game-art cloth detail, not magnified low-resolution pixels. Both pieces share identical fabric, view, light, scale. Empty outside pants must be real transparent alpha, including the leg gap. No shadow, labels, guide colors, background, full character, extra fragments, stretched texture or duplicate old pants. Preserve the intended equal-cell positions and generous transparent margins."""
(P/'prompt.txt').write_text(prompt+'\n');paths=[P/'input-source45-47-fixed-crop.png',P/'input-interfaces-support.png',P/'input-approved-identity.png'];(P/'request.json').write_text(json.dumps({'transparent_background':True,'prompt':prompt,'referenced_image_paths':[str(x) for x in paths],'inputs':[{'path':x.name,'sha256':hashlib.sha256(x.read_bytes()).hexdigest()} for x in paths]},indent=2)+'\n')
