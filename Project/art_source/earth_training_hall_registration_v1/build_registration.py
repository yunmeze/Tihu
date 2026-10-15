"""Register the approved joint-review assembly to unchanged A13 owner identities.
Pixel partition only: no generation, image warp, source-map or runtime edits.
"""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt
HERE=Path(__file__).resolve().parent;P=HERE.parents[1];A=P/'art_source';O=HERE/'owners';O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 source=A/'a13_main_temple_source/source-group-contract.json';c=json.loads(source.read_text());owners=c['owners_in_draw_order'];rawpath=A/'earth_training_hall_local_assembly_review_v1/full-building-candidate-review.png';raw=Image.open(rawpath).convert('RGBA');a=np.asarray(raw);h,w=a.shape[:2]
 assert sha(source)=='30a726db95de66c5ec266ebea7d5d0903a84ebd5f478b3f2778f9e649123d0d3'
 assert sha(rawpath)=='be82bef2c8d7aa9e26675e69dc076acbca76f0878eaf78eee3a18e501a12464b'
 fixed=json.loads((A/'earth_training_hall_local_stair_plan_v1/local-input-contract.json').read_text())['fixed_reference'];s=1/fixed['density'];world=np.array(fixed['source_canvas_origin_world'])-np.array(fixed['raw_translation'])*s
 yy,xx=np.indices((h,w));wx=world[0]+(xx+.5)*s;wy=world[1]+(yy+.5)*s
 # Visible surface traces on 512-native local crops. They are not source target quads or foot-driven fill masks.
 # Narrow risers remain with connected stairs because original source support strips include them.
 surfaces={
  'left_landing':{'origin':[130,550],'poly':[(209,155),(241,139),(275,157),(298,150),(352,120),(363,127),(326,248),(230,187),(229,171)]},
  'left_landing_front_narrow_riser':{'origin':[130,550],'poly':[(230,187),(326,248),(325,260),(208,195)]},
  'left_treads_and_narrow_risers':{'origin':[130,550],'poly':[(208,195),(325,260),(339,270),(350,280),(369,290),(273,388),(272,409),(112,303),(112,294)]},
  'right_visible_inner_floor':{'origin':[850,635],'poly':[(116,179),(168,146),(215,175),(236,178),(113,244)]},
  'right_landing':{'origin':[850,635],'poly':[(113,244),(236,178),(309,208),(170,278),(136,266),(108,294),(68,271)]},
  'right_treads_and_narrow_risers':{'origin':[850,635],'poly':[(170,278),(309,208),(310,224),(332,249),(354,272),(375,295),(388,307),(388,318),(245,396),(243,370),(240,365),(236,360),(228,350),(221,340),(213,330),(205,320),(197,310),(189,300),(181,290),(173,280)]},
 }
 mask=Image.new('L',(w,h));md=ImageDraw.Draw(mask)
 for v in surfaces.values():
  ox,oy=v['origin'];md.polygon([(x+ox,y+oy)for x,y in v['poly']],fill=255)
 # Original pier is retained at native raw positions. It is structural foreground, never support.
 partition=json.loads((A/'earth_training_hall_local_assembly_review_v1/partition-contract.json').read_text());pier=partition['sides']['left']['original_main_pier_overlay_512_xy'];md.polygon([(x+130,y+550)for x,y in pier],fill=0)
 ground=np.asarray(mask)>0
 labels={0:np.full((665,796),-1,np.int16),1:np.full((665,796),-1,np.int16)};pages={}
 for i,o in enumerate(owners):
  path=P/o['atlas_page'][6:]
  if path not in pages:pages[path]=Image.open(path).convert('RGBA')
  rx,ry,rw,rh=o['atlas_rect'];alpha=np.asarray(pages[path].crop((rx,ry,rx+rw,ry+rh)))[:,:,3]>0
  x,y,_,_=o['world_rect'];x-=2948;y-=642;sub=labels[o['layer']][y:y+rh,x:x+rw];sub[alpha]=i
 sx=np.clip(np.floor(wx-2948).astype(int),0,795);sy=np.clip(np.floor(wy-642).astype(int),0,664);assigned=np.full((h,w),-1,np.int16);inferred={}
 for layer in [0,1]:
  lab=labels[layer];_,inds=distance_transform_edt(lab<0,return_indices=True);nearest=lab[inds[0],inds[1]];selected=ground if layer==0 else ~ground;assigned[selected]=nearest[sy[selected],sx[selected]];inferred[str(layer)]=int(np.sum(selected&(a[:,:,3]>0)&(lab[sy,sx]<0)))
 stored=np.any(a!=0,axis=2);visible=a[:,:,3]>0;rebuilt=np.zeros_like(a);coverage=np.zeros((h,w),np.uint8);entries=[]
 fields=['pack','key','cell','source_cell','flag','layer','sort_y','stable_source_order','frame_index']
 for i,o in enumerate(owners):
  selected=(assigned==i)&stored;entry={k:o[k]for k in fields};entry['visible_pixel_count']=int((selected&visible).sum());entry['nonzero_rgba_pixel_count']=int(selected.sum())
  if selected.any():
   ys,xs=np.where(selected);x0,y0,x1,y1=int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1);tile=np.zeros((y1-y0,x1-x0,4),np.uint8);inside=selected[y0:y1,x0:x1];tile[inside]=a[y0:y1,x0:x1][inside];path=O/f"owner-{o['frame_index']}.png";Image.fromarray(tile).save(path);entry.update(texture='res://'+str(path.relative_to(P)),raw_rect=[x0,y0,x1-x0,y1-y0],world_top_left=(world+np.array([x0,y0])*s).tolist(),scale=s,sha256=sha(path),texture_sha256=sha(path),texture_size=[x1-x0,y1-y0],empty=False);rebuilt[selected]=a[selected];coverage[selected]+=1
  else:entry.update(empty=True,texture_size=None,texture_sha256=None,texture=None,raw_rect=None,world_top_left=None,scale=s,empty_reason='Owner identity retained and original suppressed, but no candidate material belongs here; do not invent grass/apron.')
  entries.append(entry)
 assert np.array_equal(rebuilt,a);assert np.all(coverage[stored]==1);assert len(entries)==30
 # Stable owner-id raster is QA only; never an art output.
 Image.fromarray((assigned+1).astype(np.uint16)).save(HERE/'owner-labels.png');mask.save(HERE/'support-material-mask.png')
 validation={'source_key_count':30,'layer0_count':12,'layer1_count':18,'duplicate_keys':0,'visible_pixel_count':int(visible.sum()),'nonzero_rgba_pixel_count':int(stored.sum()),'pixel_assignment_once':bool(np.all(coverage[stored]==1)),'overlap_pixels':int((coverage>1).sum()),'lost_nonzero_rgba_pixels':int((stored&(coverage==0)).sum()),'full_rgba_reassembly_exact':bool(np.array_equal(rebuilt,a)),'transparent_rgb_pixels_preserved':int((stored&~visible).sum()),'empty_owner_ids':[e['frame_index']for e in entries if not e['visible_pixel_count']]}
 report={'schema':'earth-training-hall-candidate-registration-v1','status':'registered candidate for independent Earth-entry joint native review; not final accepted','approval_scope':'Original30 owners,12 support+18upper. No source flags/events/identity/order changes; no single-sprite replacement.','raw_texture':'res://'+str(rawpath.relative_to(P)),'raw_sha256':sha(rawpath),'source_contract_sha256':sha(source),'assembly_partition_contract_sha256':sha(A/'earth_training_hall_local_assembly_review_v1/partition-contract.json'),'whole_building_registration':{'scale':s,'world_top_left':world.tolist(),'rotation':0,'shear':0,'origin':'frozen pre-edit common reference; no later refit'},'suppress_source_keys':[o['key']for o in owners],'owners':entries,'sampling':{'texture_filter':'nearest for parity and first joint review','mipmaps':False,'reason':'Disjoint alpha-owner partitions share one raw sampling grid. Independent linear filtering can darken their shared edges; do not enable it without explicit parity verification.'},'partition_method':{'layer0':'Visible landing and actual connected treads+narrow risers; exclude both side cheeks, structural piers, walls. Assign to same-layer original alpha provenance or its nearest extension.','layer1':'All other stored pixels, original same-layer alpha provenance or nearest extension. Original left main pier explicitly excluded from support mask.','surface_trace_coordinate_space':'512-native local crop units, origins in frozen whole raw pixels','surface_traces':surfaces,'old_left_main_pier_exclusion_512_xy':pier,'nearest_provenance_visible_pixels':inferred,'manual_material_boundary_uncertainty_raw_px':[2,4],'not_claimed':'Nearest provenance proposes depth ownership, not native occlusion acceptance; no source cell rectangle was mistaken for a surface mask.'},'validation':validation,'density':{'registered_raster_texels_per_logical_unit':1/s,'native_whole_canvas':list(raw.size),'note':'Raster ratio of this fixed candidate registration only. Whole building native-detail quality and source alignment still subject to joint review. 2x reading inputs were not counted as generated detail.'},'known_residuals':['Left upper-mouth thin seam and retained old main-pier/new-side-cheek contact notch are visible and accepted only for candidate joint review.','Right source ground proxy at74,37 foot1 lies at antialiased front-riser silhouette, signed exterior distance about0.112 source px versus original +/-2 read budget. Edge-uncertain, not completely transparent clearance.','Runtime walk/depth/platform shadow receiver and final source registration acceptance are pending.','Source support owner records may be empty where the original art only contributed excluded grass; never remove their identities.'],'reproduce':'python Project/art_source/earth_training_hall_registration_v1/build_registration.py'}
 (HERE/'registration.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 bg=Image.new('RGBA',raw.size,(80,90,95,255));bg.alpha_composite(raw);over=np.zeros((h,w,4),np.uint8);over[ground&visible]=[0,255,190,100];bg.alpha_composite(Image.fromarray(over));bg.crop((190,680,1310,1075)).convert('RGB').save(HERE/'support-material-review.png')
 print(json.dumps(validation));print('world',world.tolist(),'scale',s)
if __name__=='__main__':main()
