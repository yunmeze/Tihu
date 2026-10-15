"""Reproduce original A13 upright six-piece tree; source preparation only."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1];OUT=P/'art_source/a13_upright_tree_source';D=P/'diagnostics/art_source/a13-upright-tree'
OFFSETS={299:(0,0),300:(-2,4),301:(-1,4),302:(1,4),303:(2,4),304:(3,4)}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
 OUT.mkdir(parents=True,exist_ok=True);D.mkdir(parents=True,exist_ok=True);mp=P/'data/maps/A13.json';mf=P/'assets/original/manifest.json';m=json.loads(mp.read_text());pk=json.loads(mf.read_text())['packs']['Map/Res/Plant'];pages={};ims={}
 def cell(x,y):return m['cells'][x*m['height']+y]
 def owners(root):
  result=[]
  for k,(dx,dy)in OFFSETS.items():
   x,y=root[0]+dx,root[1]+dy;c=cell(x,y);assert c[2:]==[2,k];f=pk['frames'][str(k)];page=pk['pages'][f['page']]['file'];a,b,w,h=f['rect']
   if page not in pages:pages[page]=Image.open(P/page[6:]).convert('RGBA')
   if k not in ims:ims[k]=pages[page].crop((a,b,a+w,b+h))
   result.append({'key':f'Plant:{k}@{x},{y}','pack':'Map/Res/Plant','frame_index':k,'cell':[x,y],'source_cell':c,'source_cell_index':x*m['height']+y,'source_map_byte_offset':m['cellByteOffsets'][x*m['height']+y],'flag':c[1],'layer':0 if c[1]in[1,-2]else 2 if c[1]==2 else 1,'sort_y':y,'stable_source_order':x*m['height']+y,'original_canvas':f['original'],'crop':f['crop'],'offset_ignored':f['offset'],'atlas_page':page,'atlas_rect':f['rect'],'native_source_offset':f['sourceOffset'],'native_source_bytes':f['sourceBytes'],'source_rgba_sha256':hashlib.sha256(ims[k].tobytes()).hexdigest(),'world_rect':[x*48+f['crop'][0],y*32+32-f['original'][1]+f['crop'][1],w,h]})
  return sorted(result,key=lambda o:(o['layer'],o['sort_y'],o['stable_source_order']))
 selected=owners([61,51]);bounds=[min(o['world_rect'][0]for o in selected),min(o['world_rect'][1]for o in selected),max(o['world_rect'][0]+o['world_rect'][2]for o in selected),max(o['world_rect'][1]+o['world_rect'][3]for o in selected)];size=[bounds[2]-bounds[0],bounds[3]-bounds[1]];comp=Image.new('RGBA',size)
 for o in selected:x,y,_,_=o['world_rect'];comp.alpha_composite(ims[o['frame_index']],(x-bounds[0],y-bounds[1]))
 comp.save(D/'source-composite.png');bg=Image.new('RGBA',size,(70,75,70,255));bg.alpha_composite(comp);bg.save(D/'source-preview.png')
 roots=[list(divmod(i,m['height']))for i,c in enumerate(m['cells'])if c[2:]==[2,299]];family=[];V=[2416,833.28,3440,1601.28]
 for root in roots:
  os=owners(root);dx,dy=(root[0]-61)*48,(root[1]-51)*32;assert all(o['world_rect']==[s['world_rect'][0]+dx,s['world_rect'][1]+dy,*s['world_rect'][2:]]and o['frame_index']==s['frame_index']and o['layer']==s['layer']for o,s in zip(os,selected));vis=[o['key']for o in os if o['world_rect'][0]<V[2]and o['world_rect'][1]<V[3]and o['world_rect'][0]+o['world_rect'][2]>V[0]and o['world_rect'][1]+o['world_rect'][3]>V[1]];family.append({'root_cell':root,'complete':True,'same_source_rgba_and_relative_layout':True,'flag_differences_from_selected':[{'frame_index':o['frame_index'],'flag':o['flag'],'selected_flag':s['flag']}for o,s in zip(os,selected)if o['flag']!=s['flag']],'world_translation_from_selected':[dx,dy],'potential_first_screen_owner_keys':vis,'owners_in_draw_order':os})
 R=[125,294];region=[121,290,129,298];world=[R[0]+bounds[0],R[1]+bounds[1]];contributors=[]
 for o in selected:
  x,y,w,h=o['world_rect'];px,py=world[0]-x,world[1]-y
  if 0<=px<w and 0<=py<h and ims[o['frame_index']].getpixel((px,py))[3]:contributors.append(o['key'])
 root={'id':'R0_woody_root_flare_contact_band','source_composite_xy':R,'world_xy':world,'manual_uncertainty_px':4,'read_region_xyxy':region,'contributors_at_read_point':contributors,'material_read':'Center of visible woody root-flare/contact band, approximate +/-4 original pixels. Read from painted wood; not checker cast, transparency bbox or logical cell bottom. The broad wood-foot silhouette extends into frame302 at the right edge, so preserve six-owner registration.','wood_foot_inspection_region_xyxy':[104,278,152,298],'caution':'Exact ground contact is not surveyed; lowest wood overlaps source trim bottom. Do not claim the bbox bottom independently establishes the physical anchor.'}
 board=bg.copy();dr=ImageDraw.Draw(board);dr.rectangle(region,outline='cyan');dr.text((143,279),'R0 +/-4',fill='white');board.save(D/'root-landmark-board.png');bg.crop((95,260,165,298)).resize((700,380),Image.Resampling.NEAREST).save(D/'root-wood-local-10x.png')
 slices=Image.new('RGB',(6*132,350),(70,75,70));dr=ImageDraw.Draw(slices)
 for i,o in enumerate(selected):
  layer=Image.new('RGBA',size);x,y,_,_=o['world_rect'];layer.alpha_composite(ims[o['frame_index']],(x-bounds[0],y-bounds[1]));layer.thumbnail((128,310));slices.paste(layer,(i*132,36),layer);dr.text((i*132,2),f"{o['frame_index']} y{o['sort_y']}",fill='white');dr.text((i*132,18),f"layer{o['layer']} flag{o['flag']}",fill='white')
 slices.save(D/'owner-slices-board.png')
 roles={299:'central trunk, root flare, central foliage and baked checker cast',300:'left outer crown fragment',301:'left inner crown and baked checker cast',302:'right inner crown, baked checker cast and tiny right wood-foot continuation',303:'right outer crown and baked checker cast',304:'outer baked checker cast; no foliage identified in inspected original slice'}
 contract={'schema':'a13-upright-tree-original-group-v1','status':'Source preparation only; no generated art or runtime installation.','source':{'map_json_sha256':sha(mp),'map_source_sha256':m['sourceSha256'],'manifest_sha256':sha(mf),'plant_source_sha256':pk['source_sha256'],'renderer_sha256':sha(P/'scripts/world_view.gd')},'selected_root_owner_cell':[61,51],'frame_range':[299,304],'owner_count':6,'world_bounds_xyxy':bounds,'composite_size':size,'owners_in_draw_order':selected,'manual_wood_root_landmark':root,'manual_material_roles':roles,'instance_family':family,'first_screen_roots':[f['root_cell']for f in family if f['potential_first_screen_owner_keys']],'coordinate_contract':m['render_contract'],'animation':{'phase_count':1,'evidence':'Map kind2 is static;299-304 are simultaneous spatial pieces with distinct owner cells, not six animation phases.'},'depth_contract':{'selected_trunk299':{'layer':1,'sort_y':51},'selected_other300_304':{'layer':1,'sort_y':55},'rule':'Keep each owner original y and stable x-major order. At y52-54 actor may be after trunk but before crown/cast slices. Do not flatten the tree or move all shadows to root y.'},'identity':{'different_from_selected_first_tree':'This six-piece281x298 green/gold upright tree is not the312x311 seven-piece292-298 golden tree. No color-based, guessed mirrored or resized reuse.','exact_translation':'All10 complete299-304 groups have same frameRGBA, relative rectangles and layers. Root51,70 differs in blocking flags for301/302/303; preserve those source flags. The three first-screen instances have matching flags. First-screen roots50,41 /55,57 /61,51 intersect4/5/6 owner AABBs respectively. Potential intersection is not exposure proof.'},'production_limits':['Generated crown/trunk/cast must register back into six owners including wood continuation in302 and cast-only304.','Keep original baked shadow ownership; do not retain original checker cast beneath an extra generated shadow.','Whole tree must be approved against native source and root read before image generation.','No gameplay path, current HD rendering or occlusion acceptance performed.']}
 save(OUT/'source-group-contract.json',contract)
 (OUT/'PLAN.md').write_text('''# A13 upright tree299–304: source only

Reproduce: python Project/tools/prepare_a13_upright_tree_source.py.

Selected root owner(61,51); complete six-piece original composition281x298, world[2839,1352,3120,1650]. Same family has10 complete A13 instances. Three potentially intersect first screen: roots(50,41),(55,57),(61,51), with4/5/6 intersecting owner AABBs. They are exact translations of the same source frameRGBA/layout; not proof of unoccluded visibility.

Inspect diagnostics/art_source/a13-upright-tree/source-preview.png, owner-slices-board.png and root-wood-local-10x.png before producing art. R0 is manually read wood root-flare/contact-band center(125,294), world(2964,1646), +/-4 original pixels. It is not a mathematically known ground anchor. Root foot extends slightly into302; source trim bottom is not independent physical-ground evidence.

299 is the trunk/root/central crown owner at layer1,y51. 300–304 are simultaneous static kind2 spatial pieces at layer1,y55.304 is outer checker cast only in the inspected original;302 includes a tiny right woody-foot continuation. Preserve the six owner keys, crop/original dimensions and stable draw order. Do not flatten to a single sprite or move every cast piece to the trunk depth. This281x298 green/gold upright tree is a distinct source from the previously selected312x311 golden292–298 tree.

No image generation, runtime changes, source edits or gameplay/occlusion validation. Future candidate must be reviewed as a whole native-scale tree, retain wood-root anchor uncertainty, map art and cast back to six original owners, and avoid duplicate shadows.
''')
 print(json.dumps({'size':size,'bounds':bounds,'root':root,'map_instances':len(family),'first_screen_roots':contract['first_screen_roots']},ensure_ascii=False))
if __name__=='__main__':main()
