"""Only deterministic crop/enlarge/guide preparation; no new artwork or raw edits."""
from pathlib import Path
import hashlib
import json
import math

import numpy as np
from PIL import Image,ImageDraw,ImageFont

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
V2=ROOT/'earth_training_hall_candidate_v2'
SRC=ROOT/'earth_training_hall_source_v1'
PLAN=ROOT/'earth_training_hall_edit_plan_v1'
SHA='5dc43ba8c8f2b5c23832aa5e3178cde41546e5077dfb96ae7c5163d73e851d75'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
 assert sha(V2/'raw.png')==SHA
 raw=Image.open(V2/'raw.png').convert('RGBA');source=Image.open(SRC/'source-full.png').convert('RGBA')
 plan=json.loads((PLAN/'edit-plan.json').read_text());qa=json.loads((V2/'measurements.json').read_text())
 d=plan['reference']['density'];t=np.array(plan['reference']['raw_translation'])
 try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
 except OSError:font=ImageFont.load_default()
 sides={'left':{'crop_xyxy':[130,550,642,1062],'guide_key':'left_stair','critical_cell':[66,36],'critical_foot':1},'right':{'crop_xyxy':[850,635,1362,1147],'guide_key':'right_stair','critical_cell':[74,37],'critical_foot':1}}
 records={}
 for side,definition in sides.items():
  out=HERE/side;out.mkdir(exist_ok=True);box=definition['crop_xyxy'];origin=np.array(box[:2],float)
  crop=raw.crop(tuple(box));assert crop.size==(512,512)
  crop.save(out/'current-native.png')
  enlarged=crop.resize((1024,1024),Image.Resampling.NEAREST);enlarged.save(out/'current-2x-reference.png')
  # Literal source rectangle, preserved at native pixels and enlarged only for reading.
  s0=(origin-t)/d;s1=(np.array(box[2:])-t)/d
  sb=[math.floor(s0[0]),math.floor(s0[1]),math.ceil(s1[0]),math.ceil(s1[1])]
  source_crop=source.crop(tuple(sb));source_crop.save(out/'source-context-native.png')
  source_crop.resize((source_crop.width*4,source_crop.height*4),Image.Resampling.NEAREST).save(out/'source-context-4x-reference.png')
  local=lambda p:((np.array(p,float)-origin)*2).tolist()
  guide=Image.new('RGBA',(1024,1024),(90,100,105,255));guide.alpha_composite(enlarged);guide=guide.convert('RGB');gd=ImageDraw.Draw(guide)
  geom=plan['stair_boundary_guides'][definition['guide_key']]
  target_poly=[local(p)for p in geom['target_raw_boundary']]
  current_poly=[local(p)for p in qa['visible_boundary_readings'][side+'_v2_raw']]
  gd.line([tuple(p)for p in current_poly+[current_poly[0]]],fill='cyan',width=3)
  gd.line([tuple(p)for p in target_poly+[target_poly[0]]],fill='magenta',width=3)
  gd.text((12,12),side.upper()+' LOCAL PLAN ONLY | magenta = source support edge',font=font,fill='white',stroke_width=1,stroke_fill='black')
  gd.text((12,36),'Cyan = current edge; keep materials/context; no marks in output',font=font,fill='white',stroke_width=1,stroke_fill='black')
  relevant=[]
  for row in qa['source_owner_foot_rows']:
   if (row['cell'][0]<70)!=(side=='left'):continue
   rr={'owner':row['owner'],'cell':row['cell'],'source_flag':row['source_flag'],'samples':[]}
   for q in row['samples']:
    pp=local(q['candidate_raw_xy']);r=2*d*2 # original toe uncertainty +/-2 source px
    critical=row['cell']==definition['critical_cell']and q['phase17_foot_index']==definition['critical_foot']
    required=q['must_restore_support'];ground=q['source_material_read']=='source_grass_apron'
    color='orange'if critical else (0,255,180)if required else 'yellow'if ground else 'white'
    gd.ellipse((pp[0]-r,pp[1]-r,pp[0]+r,pp[1]+r),outline=color,width=3 if critical else 2)
    if critical:
     text='MUST BE TREAD, not cheek'if side=='left'else'MUST STAY TRANSPARENT GROUND'
     tx=pp[0]-215 if side=='left'else pp[0]-360;ty=pp[1]+30
     gd.line((pp[0],pp[1],tx+170,ty),fill='orange',width=3)
     gd.text((max(8,tx),ty),text,font=font,fill='orange',stroke_width=1,stroke_fill='black')
    rr['samples'].append({'source_cell':row['cell'],'foot':q['phase17_foot_index'],'raw_xy':q['candidate_raw_xy'],'local_2x_xy':pp,'source_material':q['source_material_read'],'required_support':required,'required_ground_transparency':ground,'critical_for_this_edit':critical,'local_read_radius_px':r})
   relevant.append(rr)
  gd.text((12,990),'2x nearest input enlargement = reading aid only, NOT new high-density art',font=font,fill='white',stroke_width=1,stroke_fill='black')
  guide.save(out/'local-target-guide-2x.png')
  # Review source/current side by side, separate from proposed model inputs.
  review=Image.new('RGB',(1024*2,1064),(90,100,105));rd=ImageDraw.Draw(review)
  source_background=Image.new('RGBA',source_crop.size,(90,100,105,255));source_background.alpha_composite(source_crop)
  source_view=source_background.resize((source_crop.width*4,source_crop.height*4),Image.Resampling.NEAREST).convert('RGB')
  review.paste(source_view,(0,40));review.paste(guide,(1024,40));rd.text((12,12),'ORIGINAL SOURCE CROP: geometry/material boundary only',font=font,fill='white');rd.text((1036,12),'CURRENT V2 + FIXED SOURCE TARGETS',font=font,fill='white');review.save(out/'source-current-local-review.png')
  files={}
  for name in ['current-native.png','current-2x-reference.png','source-context-native.png','source-context-4x-reference.png','local-target-guide-2x.png']:
   im=Image.open(out/name);files[name]={'sha256':sha(out/name),'size':list(im.size),'mode':im.mode}
  records[side]={'raw_v2_crop_xyxy_half_open':box,'raw_crop_size':[512,512],'source_context_xyxy_half_open':sb,'source_crop_size':list(source_crop.size),'input_reference_enlargement':{'current':2,'source':4,'filter':'nearest','meaning':'technical reading enlargement only; no synthesized pixels/detail and no density credit'},'recommended_future_inputs':['current-2x-reference.png','local-target-guide-2x.png','source-context-4x-reference.png'],'target_support_boundary_local_2x':target_poly,'current_support_boundary_local_2x':current_poly,'source_foot_and_ground_constraints':relevant,'files':files,'fixed_return_contract':{'expected_output_canvas':[1024,1024],'local_generated_to_frozen_raw_scale':0.5,'local_generated_to_frozen_raw_translation':box[:2],'raw_to_source_scale':1/d,'raw_to_source_translation':(-t/d).tolist(),'condition':'For 1024x1024 output use 0.5. If actual output is another square NxN canvas, use the single full-canvas scale 512/N on both axes and record it. If aspect ratio changes or context shifts independently, reject; never bbox-fit, refit controls, or warp. Context anchors must verify framing after the canvas-ratio mapping.','do_not_claim_density':'Enlarged input is not new detail. Any native generated local detail and eventual imported density require independent measurement.'}}
 report={'status':'LOCAL INPUT PLAN ONLY. No new imagegen/edit call, no composite replacement, no runtime changes.','raw_v2_sha256':SHA,'fixed_reference_from_plan_sha256':sha(PLAN/'edit-plan.json'),'fixed_reference':plan['reference'],'scope':'Prefer one left-stair local edit first, inspect it under unchanged mapping; only then consider a separate right-stair edit. No third whole-building regeneration.','sides':records,'replacement_constraints':['Current whole-building v2 remains untouched. Future result must be archived raw before any placement work.','A local generated context crop must not be pasted as a rectangle over the building. Keep context for alignment; replace only the actual stair/side-cheek/necessary landing-seam material with documented transparent ownership.','Old staircase pixels must be explicitly retired where the approved new assembly replaces them. Do not overlay a new flight while retaining ghost old cheeks/steps underneath.','Allowed pixel operations after approval: fixed scale/translation, crop and transparent material partition only. No mesh warp, local affine pull, perspective correction, procedural stair drawing, RGB retouch or blur to hide a seam.','Any newly exposed part needs genuine generated material or true transparency; never invent hidden geometry with code.','Compare seam joins at raw 100% and source-logical scale. Door sill, landing plane, side-cheek connection and adjoining main pier/foundation must match. Reject if a seam or change outside the stairs cannot be resolved by the fixed placement.','Inspect the full stair edge, all 24 source foot samples and source grass boundary. A point/alpha pass alone is not a support, collision, height or native depth pass.'],'reproduce':'python Project/art_source/earth_training_hall_local_stair_plan_v1/build_local_inputs.py'}
 (HERE/'local-input-contract.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 assert sha(V2/'raw.png')==SHA
 print(json.dumps({'sides':{k:{'crop':v['raw_v2_crop_xyxy_half_open'],'source_crop':v['source_context_xyxy_half_open'],'critical':[q for r in v['source_foot_and_ground_constraints']for q in r['samples']if q['critical_for_this_edit']]}for k,v in records.items()},'raw_unchanged':True,'imagegen_calls':0}))


if __name__=='__main__':main()
