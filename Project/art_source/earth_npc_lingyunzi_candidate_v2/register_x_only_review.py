from pathlib import Path
from PIL import Image
import json,numpy as np
O=Path(__file__).parent;P=O.parents[1];D=P/'diagnostics/earth-npc-lingyunzi-v2'
r=json.loads((O/'review.json').read_text());m=json.loads((O/'phase-feature-measurements.json').read_text());s=r['uniform_registration']['scale_raw_to_logical'];tx,ty=r['uniform_registration']['translation_to_logical_canvas'];raw=Image.open(O/'raw-v2.png')
corrections=[-(m['generated']['left_boot']['deltas'][j]['dx']+m['generated']['right_boot']['deltas'][j]['dx'])/2 for j in range(4)]
for den in [1,2,4]:
 sheet=Image.new('RGBA',(512*den,160*den))
 for j,c in enumerate(corrections):
  ph=raw.crop((j*543,0,(j+1)*543,724));ph=ph.transform((128*den,160*den),Image.Transform.AFFINE,(1/(s*den),0,-tx/s-c,0,1/(s*den),-ty/s),resample=Image.Resampling.BICUBIC);sheet.paste(ph,(j*128*den,0))
 sheet.save(D/f'candidate-x-only-register-{den}x.png')
 source=Image.open(P/'art_source/earth_npc_input_plan_v1/lingyunzi/source-four-registered-native.png').resize((512*den,160*den),Image.Resampling.NEAREST);b=Image.new('RGBA',(512*den,320*den),(95,102,108,255));b.alpha_composite(source,(0,0));b.alpha_composite(sheet,(0,160*den));b.convert('RGB').save(D/f'source-candidate-x-only-{den}x.png')
b=Image.new('RGBA',raw.size,(95,102,108,255));b.alpha_composite(raw);b.convert('RGB').save(D/'raw-on-gray.png')
j={'status':'parent-authorized x-only rigid diagnostic; original uncorrected evidence retained','shared_scale_raw_to_logical':s,'shared_translation_logical':[tx,ty],'per_phase_additional_translation_raw_x':corrections,'per_phase_additional_translation_logical_x':[s*v for v in corrections],'per_phase_additional_translation_y':[0,0,0,0],'method':'average left/right boot local texture x displacement relative phase0, reversed; no body morph or y normalization','source_ids':[113,114,115,116],'density4_asset_production':False}
(O/'x-only-registration.json').write_text(json.dumps(j,indent=2)+'\n');print(j)
