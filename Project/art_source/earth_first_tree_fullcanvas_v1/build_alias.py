from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
O=Path(__file__).resolve().parent;P=O.parents[1];S=P/'art_source/earth_first_tree_registration_v1';R=P/'art_source/earth_first_tree_boundary_repair_v2/raw.png'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
raw=np.array(Image.open(R).convert('RGBA'));labels=np.array(Image.open(S/'owner-labels.png'));reg=json.loads((S/'registration.json').read_text());out=np.zeros_like(raw)
for i,o in enumerate(reg['owners'],1):
 a=np.zeros_like(raw);mask=labels==i;a[mask]=raw[mask];out[mask]=a[mask];f=O/f'owners/owner-{o["frame_index"]}.png';Image.fromarray(a).save(f);o.update({'texture':'res://'+str(f.relative_to(P)),'texture_size':[1254,1254],'raw_rect':[0,0,1254,1254],'world_top_left':[2630.25,784.],'sha256':sha(f),'texture_sha256':sha(f)})
assert np.array_equal(out,raw)
reg['status']='fullcanvas technical alias for GPU parity; owner labels unchanged, no runtime promotion';reg['schema']='earth-first-tree-candidate-registration-v1';reg['technical_alias']={'source_registration_sha256':sha(S/'registration.json'),'all_owner_canvas':[1254,1254],'all_world_top_left':[2630.25,784.],'all_scale':.25,'owner_assignment_unchanged':True,'all_rgba_reassembly_equal':True,'empty298_fullsize_transparent':True}
(O/'registration.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n')
files=['build_alias.py','registration.json']+[f'owners/owner-{i}.png'for i in range(292,299)];(O/'ARCHIVE_SHA256.json').write_text(json.dumps({'files':[{'path':n,'sha256':sha(O/n),'bytes':(O/n).stat().st_size}for n in files]},indent=2)+'\n');print('FULLCANVAS_7_EQUAL')
