from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent;r=json.loads((D/'technical_v1/registration.json').read_text());c=json.loads((P/'art_source/a13_first_tree_source/source-group-contract.json').read_text());src={o['key']:o for o in c['owners_in_draw_order']};rawpath=P/r['raw_texture'][6:];raw=np.array(Image.open(rawpath).convert('RGBA'));rebuilt=np.zeros_like(raw);counts=np.zeros(raw.shape[:2],np.uint8);s=r['whole_tree_registration']['scale'];t=np.array(r['whole_tree_registration']['world_top_left'])
assert hashlib.sha256(rawpath.read_bytes()).hexdigest()==r['raw_sha256']
assert len(r['owners'])==7 and set(r['suppress_source_keys'])==set(src)
for o in r['owners']:
 for k in ['cell','source_cell','flag','layer','sort_y','stable_source_order','frame_index']:assert o[k]==src[o['key']][k]
 if not o['texture']:continue
 p=P/o['texture'][6:];assert hashlib.sha256(p.read_bytes()).hexdigest()==o['sha256'];im=np.array(Image.open(p).convert('RGBA'));x,y,w,h=o['raw_rect'];assert im.shape==(h,w,4) and 0<=x<x+w<=raw.shape[1] and 0<=y<y+h<=raw.shape[0];assert np.max(np.abs(np.array(o['world_top_left'])-t-np.array([x,y])*s))<1e-9
 used=np.any(im!=0,axis=2);rebuilt[y:y+h,x:x+w][used]=im[used];counts[y:y+h,x:x+w][used]+=1
assert np.array_equal(rebuilt,raw) and counts.max()==1 and np.all(counts[np.any(raw!=0,axis=2)]==1)
v={'status':'PASS static; no native/tree cast acceptance','registration_sha256':hashlib.sha256((D/'technical_v1/registration.json').read_bytes()).hexdigest(),'all_rgba_bytes_exact':True,'unique_pixels':True,'source_metadata_seven_exact':True,'sampling_out_of_bounds':0,'source_trunk_sort_y':34,'source_crown_sort_y':37};q=P/'diagnostics/art_source/a13-first-tree/technical-v1-validation.json';q.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
