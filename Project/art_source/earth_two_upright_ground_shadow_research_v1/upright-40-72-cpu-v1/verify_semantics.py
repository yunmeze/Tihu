"""Read actual source RGBA; output CPU evidence only. No runtime authorization."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageFilter
O=Path(__file__).resolve().parent; W=O.parent.parent; P=W/'recovery-work/upright-51-70-runtime-v1/Project'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
invpath=W/'tihu-legend/recovery-work/full-a13-coverage/inventory.json';inv=read(invpath);frames={f['key']:f for f in inv['frames']}; enum=read(O/'SOURCE_ENUMERATION.json');c=read(O/'contract.json');B=np.array(c['world_rect_xyxy']); e=np.array(Image.open(O/'root-error-envelope.png'))>0
atlases={};pins={}
def sprite(o):
 f=frames[o['frames'][0]['frame_key']];p=P/f['atlas'][6:];pins[f['atlas']]=sha(p)
 if str(p) not in atlases:atlases[str(p)]=Image.open(p).convert('RGBA')
 x,y,w,h=f['atlas_rect'];im=atlases[str(p)].crop((x,y,x+w,y+h));assert hashlib.sha256(im.tobytes()).hexdigest()==f['rgba_sha256']
 return im
rows=[r for r in enum['floors'] if r['error_hit_cells']]; assert len(rows)==18
coverage=np.zeros(e.shape,bool); fs=[]
for r in rows:
 o=next(o for o in inv['owners'] if o['key']==r['key']);im=sprite(o);a=np.array(im)[:,:,3]
 assert r['source_frame']=='Map/Res/FloorBig:406' and r['candidate_kind']=='grass' and (a==255).all()
 assert hashlib.sha256(im.tobytes()).hexdigest()==r['source_rgba_sha256']
 can=Image.new('RGBA',(e.shape[1],e.shape[0]));z=o['frames'][0]['draw_bounds_xyxy'];can.alpha_composite(im.resize((im.width*2,im.height*2),Image.Resampling.NEAREST),((z[0]-B[0])*2,(z[1]-B[1])*2));coverage|=np.array(can)[:,:,3]==255
 fs.append({'key':o['key'],'rgba_sha256':r['source_rgba_sha256'],'size':list(im.size),'alpha_min':int(a.min()),'alpha_max':int(a.max()),'all_pixels_opaque':True,'support_half_cells':r['error_hit_cells']})
assert not (e&~coverage).any()
# Build pool mask in a padded region to include off-patch sources before dilation.
pad=12; pb=B+[-pad,-pad,pad,pad];shape=tuple((pb[2:]-pb[:2])*2);pool=Image.new('L',shape);poolrows=[]
for o in inv['owners']:
 if o['pack']!='Map/Res/Debris' or not 55<=o['index']<=61:continue
 z=o['frames'][0]['draw_bounds_xyxy']
 if not(z[0]<pb[2] and z[2]>pb[0] and z[1]<pb[3] and z[3]>pb[1]):continue
 im=sprite(o); al=im.getchannel('A').point(lambda v:255 if v else 0);one=Image.new('L',shape);one.paste(al.resize((al.width*2,al.height*2),Image.Resampling.NEAREST),((z[0]-pb[0])*2,(z[1]-pb[1])*2));pool=Image.fromarray(np.maximum(np.array(pool),np.array(one)))
 ex=np.array(one.filter(ImageFilter.MaxFilter(21)))[pad*2:-pad*2,pad*2:-pad*2]>0
 poolrows.append({'key':o['key'],'full_alpha_plus5_error_hit_cells':int((ex&e).sum()),'rgba_sha256':frames[o['frames'][0]['frame_key']]['rgba_sha256']})
ex=np.array(pool.filter(ImageFilter.MaxFilter(21)))[pad*2:-pad*2,pad*2:-pad*2]>0
assert np.array_equal(ex,np.array(Image.open(O/'pool-filter-uncertainty-excluded.png'))>0)
bamboo=[]
for o in inv['owners']:
 if o['pack']!='Map/Res/Plant' or not 316<=o['index']<=322:continue
 r=next((r for r in enum['objects'] if r['key']==o['key']),None)
 if not r:continue
 im=sprite(o);a=np.array(im)[:,:,3];bamboo.append({'key':o['key'],'bounds':o['frames'][0]['draw_bounds_xyxy'],'layer':o['layer'],'sort_y':o['sort_y'],'support_hit_cells':r['error_hit_cells'],'rgba_sha256':frames[o['frames'][0]['frame_key']]['rgba_sha256'],'positive_pixels':int((a>0).sum()),'weak_1_to_254_pixels':int(((a>0)&(a<255)).sum()),'zero_alpha_pixels':int((a==0).sum()),'semantic':'Foreground original RGBA includes leaf gaps and baked/checker shadow risk. Alpha statistics do not identify physical shadow pixels.'})
result={'source_inventory_sha256':sha(invpath),'source_atlas_pins':pins,'actual_18_floor_rgba':fs,'support_cells':int(e.sum()),'uncovered_support_cells':int((e&~coverage).sum()),'padded_pool_mask_matches':True,'pool_sources':poolrows,'bamboo_instances':bamboo,'foreground_rule':'Same original world object order after single ground shadow max pass; retain full RGBA and fractional alpha. No mask punching or color-key removal. Dark baked RGB may multiply with ground shadow under partial alpha; visual observation remains pending.','base':'Old approved unified v2 resources via frozen single-tree staging. New stable plant bank must be repinned before runtime integration.'}
gp=P/'ground_candidate/grass.png';ga=np.array(Image.open(gp).convert('RGBA'));assert (ga[:,:,3]==255).all()
result['modern_grass']={'path':'res://ground_candidate/grass.png','sha256':sha(gp),'size':[int(ga.shape[1]),int(ga.shape[0])],'alpha_min':255,'alpha_max':255,'coverage_preserved':True}
(O/'SEMANTIC_PIXEL_AUDIT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps({'floors':len(fs),'uncovered':result['uncovered_support_cells'],'pool_sources':poolrows,'bamboo_count':len(bamboo)}))
