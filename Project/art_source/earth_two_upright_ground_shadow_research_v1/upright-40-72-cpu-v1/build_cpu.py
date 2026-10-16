"""Owned CPU study only. No Godot execution or production writes."""
from pathlib import Path
import json,hashlib,importlib.util
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
O=Path(__file__).resolve().parent; W=O.parent.parent; P=W/'recovery-work/upright-51-70-runtime-v1/Project'; G=P
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
spec=importlib.util.spec_from_file_location('geom',P/'tools/earth/build_flat_shadow_gate.py'); geom=importlib.util.module_from_spec(spec);spec.loader.exec_module(geom)
reg=read(P/'assets/earth/first_map_review/plant_reuse_registration.json');tree=reg['groups']['upright_tree_40_72'];origin=np.array(tree['owners'][0]['world_top_left']);ref=np.array([560,1329])/4.5
raw=np.array(Image.open(P/'assets/earth/environment/upright_tree_v1/raw.png').convert('RGBA'));a=raw[:,:,3];yy,xx=np.nonzero(a>0)
lo=(np.stack((xx,yy),1)-.5)/4.5;hi=(np.stack((xx,yy),1)+1.5)/4.5;M=np.array([[1,-1.2],[0,-.55]]);T=np.array([1.2*ref[1],1.55*ref[1]])
corners=np.stack((lo,np.stack((hi[:,0],lo[:,1]),1),hi,np.stack((lo[:,0],hi[:,1]),1)),1)@M.T+T
base=np.c_[corners.min(1)-1.8,corners.max(1)+1.8];base=np.r_[base,[[ref[0]-1.8,ref[1]-1.8,ref[0]+1.8,ref[1]+1.8]]]+np.tile(origin,2);error=base+[-7.2,-9.3,7.2,9.3]
B=np.array([1840,2302,2444,2496]);D=2;size=(B[2:]-B[:2])*D; nominal=geom.raster(base,B[:2],size);envelope=geom.raster(error,B[:2],size)
assert (error[:,:2]>=B[:2]).all() and (error[:,2:]<=B[2:]).all();geom.verify_coverage(nominal,base,B[:2]);geom.verify_coverage(envelope,error,B[:2])
reassembled=np.zeros_like(raw);overlap=np.zeros(a.shape,np.uint8)
for owner in tree['owners']:
 p=P/owner['texture'][6:];assert sha(p)==owner['texture_sha256'];im=np.array(Image.open(p).convert('RGBA'));nz=np.any(im!=0,axis=2);reassembled[nz]=im[nz];overlap+=nz
assert np.array_equal(raw,reassembled) and not (overlap>1).any();assert tree['owners'][-1]['index']==304 and tree['owners'][-1]['empty']
inv=read(W/'tihu-legend/recovery-work/full-a13-coverage/inventory.json');frames={f['key']:f for f in inv['frames']};gm=read(G/'ground_candidate/manifest.json');gr=read(G/'ground_candidate/registration.json');cs={r['key'] for r in gr['C']};floorrows={r['key']:r for r in gm['floors']};atlas={}
def sprite(o):
 f=frames[o['frames'][0]['frame_key']];path=P/f['atlas'][6:]
 if str(path) not in atlas:atlas[str(path)]=Image.open(path).convert('RGBA')
 x,y,w,h=f['atlas_rect'];return atlas[str(path)].crop((x,y,x+w,y+h))
def canvas(o,b=B,d=D):
 z=o['frames'][0]['draw_bounds_xyxy'];im=sprite(o);out=Image.new('RGBA',tuple((b[2:]-b[:2])*d));out.alpha_composite(im.resize((im.width*d,im.height*d),Image.Resampling.NEAREST),((z[0]-b[0])*d,(z[1]-b[1])*d));return out
owners=[]
for o in inv['owners']:
 z=o['frames'][0]['draw_bounds_xyxy']
 if z[0]<B[2] and z[2]>B[0] and z[1]<B[3] and z[3]>B[1]:owners.append(o)
# Coverage starts transparent. The floor pass background color is deliberately absent.
floor=Image.new('RGBA',tuple(size));pool=np.zeros(nominal.shape,bool);floor_report=[];object_report=[]
for o in sorted(owners,key=lambda v:(0 if v['category']=='floor' else 1,v['layer'],v['sort_y'],v['stable_source_order'])):
 can=canvas(o);al=np.array(can)[:,:,3]
 if o['category']=='floor':
  floor.alpha_composite(can);row=floorrows[o['key']];assert row['source_cell']==o['source_cell'] and row['cell']==o['cell']
  kind='C' if o['key'] in cs else ('grass' if row['reuse'] else ('current' if row['current'] else 'source'))
  floor_report.append({'key':o['key'],'source_frame':o['frames'][0]['frame_key'],'source_rgba_sha256':row['source_rgba_sha256'],'source_cell':o['source_cell'],'cell':o['cell'],'floor_stream_index':row['floor_stream_index'],'stable_source_order':o['stable_source_order'],'candidate_kind':kind,'draw_bounds':o['frames'][0]['draw_bounds_xyxy'],'nominal_hit_cells':int(((al>0)&nominal).sum()),'error_hit_cells':int(((al>0)&envelope).sum()),'source_alpha_extrema':row['alpha_extrema']})
 else:
  hit=(al>0)&envelope;object_report.append({'key':o['key'],'bounds':o['frames'][0]['draw_bounds_xyxy'],'error_hit_cells':int(hit.sum()),'nominal_hit_cells':int(((al>0)&nominal).sum()),'role':'pool water/wall/apron conservatively excluded' if o['pack']=='Map/Res/Debris' and 55<=o['index']<=61 else 'foreground occlusion; embedded baked-shadow risk remains'})
  if o['pack']=='Map/Res/Debris' and 55<=o['index']<=61:pool|=al>0
coverage=np.array(floor)[:,:,3]==255
# Exclude ALL positive pool source alpha, even apron, plus 4 logical uncertainty
# and 1 logical filter support. No dark-pixel or alpha>=128 shortcut.
# Include off-patch pool alpha before dilation; crop only after the filter.
pad=12; PB=B+[-pad,-pad,pad,pad]; padded=np.zeros(tuple(((PB[2:]-PB[:2])*D)[::-1]),bool)
for o in inv['owners']:
 if o['pack']=='Map/Res/Debris' and 55<=o['index']<=61:
  z=o['frames'][0]['draw_bounds_xyxy']
  if z[0]<PB[2] and z[2]>PB[0] and z[1]<PB[3] and z[3]>PB[1]:padded|=np.array(canvas(o,PB,D))[:,:,3]>0
pool=padded[pad*D:-pad*D,pad*D:-pad*D]
excluded=(np.array(Image.fromarray(padded.astype('uint8')*255).filter(ImageFilter.MaxFilter(21)))>0)[pad*D:-pad*D,pad*D:-pad*D]
allowed=coverage&~excluded&envelope
for n,mask in [('nominal-envelope',nominal),('root-error-envelope',envelope),('floor-opaque-coverage',coverage),('pool-positive-alpha',pool),('pool-filter-uncertainty-excluded',excluded),('allowed-provisional',allowed)]:Image.fromarray(mask.astype('uint8')*255).save(O/(n+'.png'))
# Six referenced floor frames, actual RGBA, with immutable keys. Source image only.
keys=sorted({r['source_frame'] for r in floor_report});board=Image.new('RGB',(440,len(keys)*155),(35,35,35));dr=ImageDraw.Draw(board)
for i,k in enumerate(keys):
 o=next(o for o in owners if o['category']=='floor' and o['frames'][0]['frame_key']==k)
 board.paste(sprite(o).resize((192,128),Image.Resampling.NEAREST),(0,i*155+23));dr.text((0,i*155+3),k+' complete 2x',fill='white')
 rows=[r for r in floor_report if r['source_frame']==k];hits=sum(r['error_hit_cells'] for r in rows)
 dr.text((205,i*155+35),'bbox owners: '+str(len(rows)),fill='white');dr.text((205,i*155+55),'error-support cells: '+str(hits),fill='white')
 dr.text((205,i*155+75),'alpha255; grass/soil',fill='white')
board.save(O/'SOURCE_FLOOR_FRAMES.png')
# Source context is diagnostic, never the new rendered shadow.
CB=np.array([1792,1984,2496,2592]);context=Image.new('RGBA',tuple(CB[2:]-CB[:2]),(32,41,31,255))
for o in sorted(inv['owners'],key=lambda v:(0 if v['category']=='floor' else 1,v['layer'],v['sort_y'],v['stable_source_order'])):
 z=o['frames'][0]['draw_bounds_xyxy']
 if z[0]<CB[2] and z[2]>CB[0] and z[1]<CB[3] and z[3]>CB[1]:context.alpha_composite(canvas(o,CB,1))
context.save(O/'SOURCE_CONTEXT.png')
maskrgb=np.zeros((*nominal.shape,4),np.uint8);maskrgb[envelope]=[255,180,0,110];maskrgb[nominal]=[30,130,255,110];maskrgb[excluded]=[255,30,45,145];maskrgb[~coverage]=[220,0,220,160]
sem=context.copy();sem.alpha_composite(Image.fromarray(maskrgb).resize(tuple(size//2),Image.Resampling.NEAREST),tuple(B[:2]-CB[:2]));d=ImageDraw.Draw(sem);r=origin+ref-CB[:2];d.ellipse((r[0]-3,r[1]-3,r[0]+3,r[1]+3),fill='white');d.text((5,5),'SOURCE: blue nominal / amber root error / red pool+5px / white fixed root',fill='white');sem.save(O/'SEMANTIC_SUPPORT.png')
pins={}
for path in [P/'data/maps/A13.json',P/'assets/original/manifest.json',P/'assets/earth/first_map_review/plant_reuse_registration.json',P/'assets/earth/environment/upright_tree_v1/raw.png',P/'assets/earth/environment/upright_tree_v1/registration_left_50_41.json',P/'assets/earth/first_map_review/static_props_registration.json']+[P/o['texture'][6:] for o in tree['owners']]+[Path(p) for p in atlas]:pins['res://'+str(path.relative_to(P))]=sha(path)
for p in ['ground_candidate/manifest.json','ground_candidate/registration.json','scripts/earth/first_map_floor_pass.gd','scripts/earth/ground_candidate_guard.gd','ground_candidate/ground.gdshader']:pins['res://'+p]=sha(G/p)
contract={'schema':'upright-40-72-local-ground-only-cpu-v1','status':'CPU provisional, local semantic review required; NOT runtime-admitted','caster':'upright_tree_40_72','world_rect_xyxy':B.tolist(),'density':2,'body_origin':origin.tolist(),'body_root_raw':[560,1329],'body_density':4.5,'root_world':(origin+ref).tolist(),'cast':[1.2,.55],'blur':.8,'opacity':.25,'tint':[.035,.045,.055],'root_uncertainty_expansion':[7.2,9.3],'tree':tree,'inputs':pins,'ground_binding':{'tested_resource_path':'res://ground_candidate/registration.json','candidate_registration_sha256':sha(G/'ground_candidate/registration.json'),'freeze_sha256':sha(W/'recovery-work/earth-unified-candidate-v2/FROZEN_INPUTS_v3.json'),'mode':'explicit verified source or modern snapshot required; no live binding yet','generation':'future controller adapter must provide shared revoke token; no fabricated generation','relocation':'repin new real runtime paths and all transitive closure before GPU'},'coverage_rule':'transparent start; ordered actual source floor RGBA alpha255 only; never background; candidate modes must preserve proved coverage; locally bounded root-error support only','pool_rule':'all actual source Debris55..61 alpha>0 plus5logical; includes water/wall/apron and weak-alpha border; no pool-plane reception claimed','semantic_status':'local grass406 support CPU proof; foreground bamboo/baked shadows remain observation items; no whole-map authorization','composition':'future same max pass with old casters; foreground objects after ground shadow; embedded source object shadows cannot be deduplicated by max','files':{p.name:sha(p) for p in O.glob('*.png')}}
(O/'contract.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2));(O/'SOURCE_ENUMERATION.json').write_text(json.dumps({'floors':floor_report,'objects':object_report},ensure_ascii=False,indent=2))
metrics={'raw_positive_alpha':int((a>0).sum()),'raw_weak_alpha':int(((a>0)&(a<128)).sum()),'raw_rgba_sha256':hashlib.sha256(raw.tobytes()).hexdigest(),'owner_reassembly_exact':True,'owner304_empty':True,'per_texel_support_boxes':len(base),'complete_bounds':np.r_[error[:,:2].min(0),error[:,2:].max(0)].tolist(),'nominal_cells':int(nominal.sum()),'root_error_cells':int(envelope.sum()),'error_no_floor_cells':int((envelope&~coverage).sum()),'nominal_pool_excluded_cells':int((nominal&excluded).sum()),'error_pool_excluded_cells':int((envelope&excluded).sum()),'provisional_allowed_cells':int(allowed.sum()),'full_support_qualification':bool((envelope&~allowed).sum()==0),'ground_only_policy':'explicit receiver clipping, not full-support PASS','runtime_ready':False}
(O/'CPU_RESULT.json').write_text(json.dumps(metrics,indent=2));print(json.dumps(metrics))
