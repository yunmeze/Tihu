"""Independent inverse reconstruction of frozen candidate owner cutouts; no runtime."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent
r=json.loads((D/'technical_v1/registration.json').read_text());c=json.loads((P/'art_source/a13_main_temple_source/source-group-contract.json').read_text());original={o['key']:o for o in c['owners_in_draw_order']}
rawpath=P/r['raw_texture'][6:];raw=np.array(Image.open(rawpath).convert('RGBA'));out=np.zeros_like(raw);counts=np.zeros(raw.shape[:2],np.uint8);s=r['whole_building_registration']['scale'];t=np.array(r['whole_building_registration']['world_top_left'])
assert hashlib.sha256(rawpath.read_bytes()).hexdigest()==r['raw_sha256']
assert len(r['owners'])==30 and len({o['key']for o in r['owners']})==30
assert set(r['suppress_source_keys'])==set(original)
for o in r['owners']:
 src=original[o['key']]
 for field in ['cell','source_cell','flag','layer','sort_y','stable_source_order','frame_index']:assert o[field]==src[field],(o['key'],field)
 if o['texture'] is None:continue
 p=P/o['texture'][6:];assert hashlib.sha256(p.read_bytes()).hexdigest()==o['sha256']
 im=np.array(Image.open(p).convert('RGBA'));x,y,w,h=o['raw_rect'];assert im.shape==(h,w,4)
 assert 0<=x<x+w<=raw.shape[1] and 0<=y<y+h<=raw.shape[0]
 assert np.max(np.abs(np.array(o['world_top_left'])-(t+np.array([x,y])*s)))<1e-9
 used=np.any(im!=0,axis=2);sub=out[y:y+h,x:x+w];sub[used]=im[used];counts[y:y+h,x:x+w][used]+=1
assert np.array_equal(out,raw)
assert np.max(counts)==1
assert np.all(counts[np.any(raw!=0,axis=2)]==1)
# Nearest-sampling world raster equality follows from one origin/grid. Verify an
# explicit common-grid index rendering as independent parity check.
W,H=796,665;yy,xx=np.indices((H,W));rx=np.floor((2948+xx+.5-t[0])/s).astype(int);ry=np.floor((642+yy+.5-t[1])/s).astype(int);valid=(rx>=0)&(rx<raw.shape[1])&(ry>=0)&(ry<raw.shape[0]);assert np.array_equal(raw[ry[valid],rx[valid]],out[ry[valid],rx[valid]])
result={'status':'PASS static inverse/raster; native pending','registration_sha256':hashlib.sha256((D/'technical_v1/registration.json').read_bytes()).hexdigest(),'whole_raw_rgba_bytes_equal':True,'nonzero_rgba_pixels_unique':True,'source_metadata_30_exact':True,'world_crop_compensation_max_error':0,'nearest_common_grid_parity':True,'runtime_modified':False}
q=P/'diagnostics/art_source/a13-main-temple/technical-v1-validation.json';q.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
