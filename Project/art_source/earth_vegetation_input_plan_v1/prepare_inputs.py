"""Offline source geometry preparation. No generation, runtime edit, Git or GUI."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
import numpy as np
P=Path(__file__).resolve().parents[2]; O=Path(__file__).resolve().parent
D=P/'diagnostics/art_source/earth_vegetation_input_plan_v1';D.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
write=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
m=read(P/'data/maps/A13.json');manifest=read(P/'assets/original/manifest.json');pk=manifest['packs']['Map/Res/Plant'];V=(2496,960,3264,1472)
inputs=[P/'data/maps/A13.json',P/'assets/original/manifest.json',P/'docs/EARTH_ART_BIBLE_V1.md',P/'art_source/earth_base_style_concept_v1/concept.png',P/'scripts/world_view.gd',P/'scripts/core/movement.gd',P.parent/m['source'],P.parent/pk['source']]
assert sha(P.parent/m['source'])==m['sourceSha256'];assert sha(P.parent/pk['source'])==pk['source_sha256']
pages={}
for page in pk['pages']:
 p=P/page['file'][6:];assert sha(p)==page['sha256'];inputs.append(p);pages[page['file']]=Image.open(p).convert('RGBA')
history={}
for n in ['first_tree','upright_tree','round_shrub','grass_clumps']:
 p=P/f'art_source/a13_{n}_source/source-group-contract.json';inputs.append(p);history[n]=read(p)
def owner(x,y,idx):
 c=m['cells'][x*m['height']+y];assert c[2:]==[2,idx]
 f=pk['frames'][str(idx)];a,b,w,h=f['rect'];page=pk['pages'][f['page']]['file'];tile=pages[page].crop((a,b,a+w,b+h))
 full=Image.new('RGBA',f['original']);full.paste(tile,tuple(f['crop']));assert hashlib.sha256(full.tobytes()).hexdigest()==f['rgba_sha256']
 wx=x*48+f['crop'][0];wy=y*32+32-f['original'][1]+f['crop'][1]
 xx,yy,X,Y=max(wx,V[0]),max(wy,V[1]),min(wx+w,V[2]),min(wy+h,V[3]);n=0
 if X>xx and Y>yy:n=int(np.count_nonzero(np.asarray(tile.getchannel('A'))[yy-wy:Y-wy,xx-wx:X-wx]))
 return {'key':f'Plant:{idx}@{x},{y}','pack':'Map/Res/Plant','frame_index':idx,'cell':[x,y],'source_cell':c,'flag':c[1],'layer':0 if c[1] in [1,-2] else (2 if c[1]==2 else 1),'sort_y':y,'stable_source_order':x*m['height']+y,'original_canvas':f['original'],'crop':f['crop'],'ignored_frame_offset':f['offset'],'atlas_page':page,'atlas_rect':f['rect'],'frame_rgba_sha256':f['rgba_sha256'],'native_source_offset':f['sourceOffset'],'native_source_bytes':f['sourceBytes'],'world_rect':[wx,wy,w,h],'viewport_aabb_intersects':X>xx and Y>yy,'viewport_nonzero_alpha_pixels':n},tile
patterns=[('broad_tree',292,[(292,0,0),(293,-2,3),(294,-1,3),(295,1,3),(296,2,3),(297,3,3),(298,4,3)]),('upright_tree',299,[(299,0,0),(300,-2,4),(301,-1,4),(302,1,4),(303,2,4),(304,3,4)]),('round_shrub',145,[(143,0,-3),(144,-1,0),(145,0,0),(146,1,0)]),('grass239',239,[(239,0,0),(240,1,0)]),('grass241',241,[(241,0,0),(242,1,0)])]
groups=[];claimed=set();scene=Image.new('RGBA',(768,512),(65,72,65,255))
for fam,root,pattern in patterns:
 for x in range(m['width']):
  for y in range(m['height']):
   if m['cells'][x*m['height']+y][2:]!=[2,root]:continue
   pair=[owner(x+dx,y+dy,idx) for idx,dx,dy in pattern];pair.sort(key=lambda t:(t[0]['layer'],t[0]['sort_y'],t[0]['stable_source_order']))
   if not any(o['viewport_nonzero_alpha_pixels'] for o,t in pair):continue
   os=[o for o,t in pair];x0=min(o['world_rect'][0] for o in os);y0=min(o['world_rect'][1] for o in os);x1=max(o['world_rect'][0]+o['world_rect'][2] for o in os);y1=max(o['world_rect'][1]+o['world_rect'][3] for o in os)
   im=Image.new('RGBA',(x1-x0,y1-y0));labels=np.zeros((im.height,im.width),np.uint8)
   for j,(o,t) in enumerate(pair,1):
    ox,oy,w,h=o['world_rect'];im.alpha_composite(t,(ox-x0,oy-y0));labels[oy-y0:oy-y0+h,ox-x0:ox-x0+w][np.asarray(t.getchannel('A'))>0]=j;claimed.add(o['key'])
   ident=f'{fam}_{x}_{y}';im.save(O/f'{ident}_source_native.png');Image.fromarray(labels).save(O/f'{ident}_owner_ids.png');im.getchannel('A').save(O/f'{ident}_alpha.png')
   neutral=Image.new('RGBA',im.size,(165,175,165,0));neutral.putalpha(im.getchannel('A'));neutral.save(O/f'{ident}_geometry_only.png')
   anchor={'type':'draw_origin_not_physical_root','world':[x*48,y*32],'local':[x*48-x0,y*32-y0]}
   if fam=='broad_tree': anchor=history['first_tree']['manual_root_landmark']
   if fam=='upright_tree':
    src=history['upright_tree'];anchor=json.loads(json.dumps(src['manual_wood_root_landmark']));anchor['world_xy']=[anchor['world_xy'][0]+(x-61)*48,anchor['world_xy'][1]+(y-51)*32]
   if fam in ['grass239','grass241']:
    original=next(g for g in history['grass_clumps']['groups'] if g['frame_indices'][0]==root)
    rx,ry=original['selected_root_owner_cell'];reads=json.loads(json.dumps(original['visible_basal_landmarks']))
    for point in reads:
     point['world_xy']=[point['world_xy'][0]+(x-rx)*48,point['world_xy'][1]+(y-ry)*32]
    anchor={'type':'visible_basal_material_bands_not_surveyed_roots','draw_origin':anchor,'historical_reads':reads,'limit':original['physical_anchor_limit']}
   if fam=='round_shrub':
    anchor['physical_root']=None;anchor['source_lower_foliage_local_read_zone_xyxy']=[40,94,95,100];anchor['warning']='Visible leaf support band only, not a proven ground plane or physical root; bbox includes checker cast.'
   g={'id':ident,'family':fam,'root_or_center_owner_cell':[x,y],'priority':'first_generation' if (fam,x,y) in [('broad_tree',57,34),('round_shrub',57,38)] else 'inventory_only','world_bounds_xyxy':[x0,y0,x1,y1],'logical_size':[im.width,im.height],'minimum_true_density2_size':[im.width*2,im.height*2],'recommended_density4_size':[im.width*4,im.height*4],'anchor':anchor,'owners_in_draw_order':os,'source_alpha_pixels_in_view_sum':sum(o['viewport_nonzero_alpha_pixels']for o in os),'file_prefix':ident,'owner_id_encoding':'0 transparent; 1..N maps to owners_in_draw_order; source alpha ownership, not a newly approved body/cast segmentation'}
   groups.append(g)
# Independent all-kind2 alpha enumeration prevents silently omitted families.
visible=[]
for x in range(m['width']):
 for y in range(m['height']):
  c=m['cells'][x*m['height']+y]
  if c[2]==2 and c[3]>0:
   o,t=owner(x,y,c[3])
   if o['viewport_nonzero_alpha_pixels']:visible.append(o['key'])
assert set(visible)<=claimed,sorted(set(visible)-claimed)
for g in groups:
 for o in g['owners_in_draw_order']:
  a,b,w,h=o['atlas_rect'];t=pages[o['atlas_page']].crop((a,b,a+w,b+h));x,y,_,_=o['world_rect'];scene.alpha_composite(t,(x-V[0],y-V[1]))
scene.save(D/'source_vegetation_only_native.png')
concept=Image.open(P/'art_source/earth_base_style_concept_v1/concept.png').convert('RGB')
refs=[('concept_tree_branch_foliage',[270,0,716,356],'Natural green broadleaf crown, warm upper-left highlights, branching trunk. Crop includes background; do not transfer planter or layout.'),('concept_bark_detail',[420,190,502,354],'Bark and branch junction material only; no anchor evidence.'),('concept_shrub_material',[547,254,714,347],'Small natural green shrub clusters, leaf-scale and warm/cool separation. Includes planter edge; prohibit planter transfer.')]
for n,b,meaning in refs:concept.crop(b).save(O/(n+'.png'))
write(O/'concept_crops.json',{'source_size':list(concept.size),'source_sha256':sha(P/'art_source/earth_base_style_concept_v1/concept.png'),'coordinate_units':'native pixels; xyxy exclusive; no resize','references':[{'file':n+'.png','crop_xyxy':b,'use':s} for n,b,s in refs]})
write(O/'source_contract.json',{'schema':'earth-bounded-vegetation-input-v1','status':'source preparation only; no generated art, runtime integration, gameplay or new-art occlusion acceptance','world_xywh':[2496,960,768,512],'visibility':'nonzero original alpha intersects fixed rectangle, before other-object occlusion; includes baked checker cast. Does not claim final GPU exposure.','group_count':len(groups),'owner_count':sum(len(g['owners_in_draw_order'])for g in groups),'visible_alpha_owner_count':len(visible),'visible_alpha_owner_keys':visible,'groups':groups,'coordinate_contract':history['first_tree']['coordinate_contract'],'root_limits':'Shrub origin is not a root; grass basal bands not surveyed roots. Tree anchors carry historical manual +/-4 logical px uncertainty.','shadow_limits':'Source alpha includes baked dither shadow; owner ID maps are not material masks. No global dark-RGB removal. New body/cast segmentation and right-down Earth shadow remain unapproved.'})
write(O/'INPUT_SHA256.json',[{'path':str(p.relative_to(P.parent)),'sha256':sha(p)} for p in inputs])
# Explicit archive whitelist. Diagnostics and manifest itself are deliberately excluded.
files=['README.md','prepare_inputs.py','source_contract.json','concept_crops.json','INPUT_SHA256.json']+[n+'.png' for n,b,s in refs]
for g in groups:files += [g['file_prefix']+s for s in ['_source_native.png','_owner_ids.png','_alpha.png','_geometry_only.png']]
assert all((O/n).is_file()for n in files)
write(O/'ARCHIVE_SHA256.json',{'format':'explicit relative-path whitelist; excludes diagnostics, runtime and this self-referential manifest','files':[{'path':n,'bytes':(O/n).stat().st_size,'sha256':sha(O/n)}for n in sorted(files)]})
print(json.dumps({'groups':len(groups),'owners':sum(len(g['owners_in_draw_order'])for g in groups),'visible_alpha_owners':len(visible),'inventory':[(g['id'],g['source_alpha_pixels_in_view_sum'])for g in groups]},indent=2))
