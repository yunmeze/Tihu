"""Rebuild only the explicitly approved technical generation input, never final art."""
from pathlib import Path
from PIL import Image
import json,hashlib
P=Path(__file__).resolve().parents[2];O=Path(__file__).parent;I=P/'art_source/earth_south_ground_input_plan_v1'
a=Image.open(I/'source_floor_layout_native.png').convert('RGBA').resize((1536,1024),Image.Resampling.NEAREST)
b=Image.open(I/'approved_overlap_2x.png').convert('RGBA');assert b.size==(1344,128)
a.paste(b,(192,0));a.save(O/'INPUT_ONLY_source2x_with_frozen_overlap.png')
files=[I/'source_floor_layout_native.png',O/'INPUT_ONLY_source2x_with_frozen_overlap.png',I/'approved_material_context_2x.png',I/'approved_grass_scale_patch_2x.png',I/'approved_slab_scale_patch_2x.png']
j={'status':'Input-only technical context explicitly approved; not final art','source_operation':'Source layout nearest2x, paste unchanged approved2x overlap at [192,0,1536,128]. No alpha blending/recolor.','world':[2400,1408,3168,1920],'input_files':[{'path':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'size':list(Image.open(f).size)} for f in files]}
(O/'INPUT_SHA256.json').write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
