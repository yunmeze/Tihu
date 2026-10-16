"""Read-only legacy inputs; independently pad all pool pieces before dilation."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageFilter
D=Path(__file__).resolve().parent;W=D.parent.parent;O=W/'recovery-work/upright-51-70-cpu-v1';P=W/'recovery-work/upright-51-70-runtime-v1/Project'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
invpath=W/'tihu-legend/recovery-work/full-a13-coverage/inventory.json';inv=json.loads(invpath.read_text());fs={f['key']:f for f in inv['frames']};c=json.loads((O/'contract.json').read_text());B=np.array(c['world_rect_xyxy']);pad=12;PB=B+[-pad,-pad,pad,pad];size=tuple((PB[2:]-PB[:2])*2);pool=np.zeros(size[::-1],bool);sources=[];per_source={};pins={}
load=lambda n:np.array(Image.open(O/(n+'.png')))>0
old=load('pool-filter-uncertainty-excluded');env=load('root-error-envelope');nom=load('nominal-envelope');floor=load('floor-opaque-coverage');allowed=load('allowed-provisional')
for o in inv['owners']:
 if o['pack']!='Map/Res/Debris' or not 55<=o['index']<=61:continue
 z=o['frames'][0]['draw_bounds_xyxy']
 if not(z[0]<PB[2] and z[2]>PB[0] and z[1]<PB[3] and z[3]>PB[1]):continue
 f=fs[o['frames'][0]['frame_key']];x,y,w,h=f['atlas_rect'];path=P/f['atlas'][6:];pins[f['atlas']]=sha(path);im=Image.open(path).convert('RGBA').crop((x,y,x+w,y+h));assert hashlib.sha256(im.tobytes()).hexdigest()==f['rgba_sha256'];a=im.getchannel('A').point(lambda v:255 if v else 0);can=Image.new('L',size);can.paste(a.resize((w*2,h*2),Image.Resampling.NEAREST),((z[0]-PB[0])*2,(z[1]-PB[1])*2));pool|=np.array(can)>0
 per_source[o['key']]=(np.array(can.filter(ImageFilter.MaxFilter(21)))>0)[24:-24,24:-24];sources.append({'key':o['key'],'rgba_sha256':f['rgba_sha256'],'bounds':z})
new=(np.array(Image.fromarray(pool.astype('uint8')*255).filter(ImageFilter.MaxFilter(21)))>0)[24:-24,24:-24];anew=env&floor&~new;delta=old!=new
coords=[]
for y,x in zip(*np.nonzero(delta)):
 coords.append({'center_world':[float(B[0]+(x+.5)/2),float(B[1]+(y+.5)/2)],'old_excluded':bool(old[y,x]),'new_excluded':bool(new[y,x]),'tree_error_support':bool(env[y,x]),'source_keys':[k for k,m in per_source.items() if m[y,x]]})
r={'scope':'Independent read-only51,70 padding audit; no GPU; no frozen input changes','pool_sources':sources,'inventory_sha256':sha(invpath),'atlas_pins':pins,'padding_logical':pad,'dilation_radius_logical':5,'whole_patch_excluded_diff_cells':int(delta.sum()),'error_support_excluded_diff_cells':int((delta&env).sum()),'nominal_support_excluded_diff_cells':int((delta&nom).sum()),'allowed_diff_cells':int((allowed!=anew).sum()),'old_allowed_new_excluded_leak_cells':int((allowed&new).sum()),'new_allowed_sha256_decoded_u8':hashlib.sha256(anew.astype('uint8').tobytes()).hexdigest(),'old_allowed_sha256_decoded_u8':hashlib.sha256(allowed.astype('uint8').tobytes()).hexdigest(),'original_freeze_sha256':sha(O/'FILES_SHA256.json'),'exact_difference_cells':coords}
assert r['allowed_diff_cells']==0 and r['old_allowed_new_excluded_leak_cells']==0
# Verify every frozen old file still equals its original evidence hash.
f=json.loads((O/'FILES_SHA256.json').read_text());rows=f.get('files',f);checked=0
for n,v in rows.items():
 h=v.get('sha256') if isinstance(v,dict) else v
 if isinstance(h,str) and len(h)==64:assert sha(O/n)==h,n;checked+=1
r['original_frozen_files_verified']=checked
out=D/'RESULT.json';assert not out.is_symlink();out.write_text(json.dumps(r,indent=2));print(json.dumps({k:r[k] for k in ['whole_patch_excluded_diff_cells','error_support_excluded_diff_cells','allowed_diff_cells','original_frozen_files_verified']}))
