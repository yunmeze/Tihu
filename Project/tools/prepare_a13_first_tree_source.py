"""Reproduce A13's first complete common tree. Source-only: no runtime or reference writes."""
from pathlib import Path
import hashlib,json,collections
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1]; ROOT=P.parent
OUT=P/'art_source/a13_first_tree_source'; DIAG=P/'diagnostics/art_source/a13-first-tree'
OFFSETS={292:(0,0),293:(-2,3),294:(-1,3),295:(1,3),296:(2,3),297:(3,3),298:(4,3)}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,obj): p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def main():
 OUT.mkdir(parents=True,exist_ok=True);DIAG.mkdir(parents=True,exist_ok=True)
 mp=P/'data/maps/A13.json'; mf=P/'assets/original/manifest.json'; m=json.loads(mp.read_text()); pack=json.loads(mf.read_text())['packs']['Map/Res/Plant']; pages={i:Image.open(P/p['file'][6:]).convert('RGBA') for i,p in enumerate(pack['pages'])}
 def cell(x,y):return m['cells'][x*m['height']+y]
 family=[]
 for i,c in enumerate(m['cells']):
  if c[2:]!=[2,292]:continue
  x,y=divmod(i,m['height']); slots=[{'frame_index':f,'cell':[x+dx,y+dy],'source_cell':cell(x+dx,y+dy)}for f,(dx,dy)in OFFSETS.items()]
  family.append({'root_owner_cell':[x,y],'complete':all(s['source_cell'][2:]==[2,s['frame_index']]for s in slots),'slots':slots})
 assert len(family)==2 and all(g['complete']for g in family)
 owners=[]; ims={}
 for f,(dx,dy)in OFFSETS.items():
  x,y=57+dx,34+dy;c=cell(x,y);assert c[2:]==[2,f];frame=pack['frames'][str(f)];rx,ry,w,h=frame['rect'];im=pages[frame['page']].crop((rx,ry,rx+w,ry+h));ims[f]=im;wx=x*48+frame['crop'][0];wy=y*32+32-frame['original'][1]+frame['crop'][1];i=x*m['height']+y
  owners.append({'key':f'Plant:{f}@{x},{y}','pack':'Map/Res/Plant','frame_index':f,'cell':[x,y],'source_cell':c,'cell_linear_index':i,'source_map_byte_offset':m['cellByteOffsets'][i],'flag':c[1],'layer':0 if c[1]in [1,-2]else 2 if c[1]==2 else 1,'sort_y':y,'stable_source_order':i,'original_canvas':frame['original'],'source_frame_offset_ignored':frame['offset'],'crop':frame['crop'],'atlas_page':pack['pages'][frame['page']]['file'],'atlas_rect':frame['rect'],'native_source_offset':frame['sourceOffset'],'native_source_bytes':frame['sourceBytes'],'world_rect':[wx,wy,w,h],'role': 'trunk and inner crown, baked cast pixels' if f==292 else 'left crown slice; no separate cast classification asserted' if f==293 else 'crown slice and baked cast pixels' if f<298 else 'outer baked cast shadow slice'})
 owners.sort(key=lambda o:(o['layer'],o['sort_y'],o['stable_source_order']))
 b=[min(o['world_rect'][0]for o in owners),min(o['world_rect'][1]for o in owners),max(o['world_rect'][0]+o['world_rect'][2]for o in owners),max(o['world_rect'][1]+o['world_rect'][3]for o in owners)];sz=(b[2]-b[0],b[3]-b[1]);comp=Image.new('RGBA',sz)
 for n,o in enumerate(owners):o['group_draw_order']=n;x,y,_,_=o['world_rect'];comp.alpha_composite(ims[o['frame_index']],(x-b[0],y-b[1]))
 comp.save(DIAG/'source-composite.png');bg=Image.new('RGBA',sz,(90,95,90,255));bg.alpha_composite(comp);bg.save(DIAG/'source-preview.png')
 # Material read: wood/root flare, excluding the lower green/brown tuft and checker cast.
 rootxy=[119,300];unc=4;wx,wy=rootxy[0]+b[0],rootxy[1]+b[1];contrib=[]
 for o in owners:
  x,y,w,h=o['world_rect'];px,py=wx-x,wy-y
  if 0<=px<w and 0<=py<h and ims[o['frame_index']].getpixel((px,py))[3]:contrib.append(o['key'])
 assert contrib==['Plant:292@57,34']
 root={'id':'R0_woody_root_ground_contact','source_composite_xy':rootxy,'world_xy':[wx,wy],'manual_read_uncertainty_px':unc,'read_region_xyxy':[115,296,123,304],'contributors_in_draw_order':contrib,'material_interpretation':'Center of visible woody root-flare contact band; approximate ground contact inferred from painted wood boundary. Excludes checker cast, lower grass/soil tuft, transparency bbox and tile/canvas bottom.','certainty':'Manual material read +/-4 original pixels, not exact surveyed ground coordinate.'}
 board=bg.copy();d=ImageDraw.Draw(board);d.rectangle(root['read_region_xyxy'],outline='cyan',width=1);d.text((140,291),'R0 +/-4',fill='white');board.save(DIAG/'root-landmark-board.png');bg.crop((91,272,151,311)).resize((600,390),Image.Resampling.NEAREST).save(DIAG/'root-material-local.png')
 plate=Image.new('RGB',(7*116,370),(90,95,90));dr=ImageDraw.Draw(plate)
 for n,o in enumerate(owners):
  im=Image.new('RGBA',sz);x,y,_,_=o['world_rect'];im.alpha_composite(ims[o['frame_index']],(x-b[0],y-b[1]));im.thumbnail((112,330));base=Image.new('RGBA',im.size,(90,95,90,255));base.alpha_composite(im);plate.paste(base.convert('RGB'),(n*116,38));dr.text((n*116+2,2),str(o['frame_index'])+' y='+str(o['sort_y']),fill='white');dr.text((n*116+2,18),'flag '+str(o['flag']),fill='white')
 plate.save(DIAG/'owner-slices-board.png')
 route=[[61,39],[60,39],[59,39],[59,38],[59,37],[58,37],[58,36],[58,35],[58,34],[58,33],[58,32],[57,32],[56,32],[56,33],[56,34],[56,35],[57,35],[58,35],[58,36],[59,36],[59,37],[59,38],[59,39],[60,39],[61,39]]
 occupied={(n['x'],n['y'])for n in m['npcs']};checks=[]
 for i,(x,y)in enumerate(route):
  c=cell(x,y);assert c[1]not in [-1,-2,-3] and (x,y)not in occupied
  if i: assert abs(x-route[i-1][0])+abs(y-route[i-1][1])==1
  checks.append({'cell':[x,y],'flag':c[1],'npc_occupied':False})
 proofs=[]
 for p,lines,claim in [('参考项目/src/map-effects.js','6-22','kind2 yields one base frame; top=32-original[1]. Only kinds5/8 animate.'),('参考项目/src/game.js','152','drawWorld calls batch.frame(...,false); map objects and hero sort together.'),('参考项目/src/batch.js','19','frame anchor=false ignores resource offset, always adds crop.'),('参考项目/src/map-flags.js','9-18','flag -1 is blocked layer1; 0 is enterable layer1; comparison layer then y.'),('Project/scripts/world_view.gd','45-58,75-78,91-101,115-140','Current runtime preserves source order and static kind2 dispatch.'),('Project/scripts/core/movement.gd','15-31','Current movement blocks -1/-2/-3 and forbids corner cutting.')]:
  f=ROOT/p;proofs.append({'path':p,'lines_hint':lines,'sha256':sha(f),'claim':claim})
 contract={'schema':'a13-first-tree-original-group-v1','status':'source preparation only; no generated art, runtime changes or GUI walk validation','map_source_sha256':m['sourceSha256'],'map_json_sha256':sha(mp),'texture_manifest_sha256':sha(mf),'plant_resource_source_sha256':pack['source_sha256'],'selected_root_owner_cell':[57,34],'frame_range':[292,298],'owner_count':7,'coordinate_contract':m['render_contract'],'world_bounds_xyxy':b,'composite_size':list(sz),'owners_in_draw_order':owners,'manual_root_landmark':root,'instance_family':family,'animation':{'proven':'Seven simultaneous spatial pieces, not seven animation phases. kind2 is static.','phase_count':1},'shadow':{'proven':'Baked checker/stipple cast exists within Plant frames of this group; no separate shadow owner is supplied by kind2 renderer.','manual_interpretation':'292 has trunk/cast; 293 is left crown (cast not separately established); 294-297 have foliage/cast; 298 is outer cast only. Exact per-pixel material masks have not been segmented.','preservation':'Keep all original owner keys, layer1, y34 for292 and y37 for293-298. Do not assign all art/shadow to root y34 or flatten into one sprite.'},'reference_evidence':proofs,'recommended_static_route':{'start':[61,39],'checked_unit_steps':checks,'back_probe':[57,32],'front_probe':[57,35],'side_probes':[[58,33],[58,34],[58,35],[56,33],[56,34],[56,35]],'full_group_front_probe':[59,38],'expectations':['At back y32 actor sorts before all seven tree owners.','At y35 actor sorts after trunk292 (y34), but before crown/cast293-298 (y37). This mixed owner depth is intentional original behavior.','At y38 actor sorts after all group owners.','At equal y the existing stable source order remains; avoid equality as primary proof.'],'verification':'All route cells are nonblocked original flags and not original NPC cells; cardinal unit moves checked. Static feasibility only: actual head/body overlap, movement, camera and neighboring occlusion remain untested.'},'limits':['Woody contact is a manual +/-4px region; grass, checker and alpha bbox are not physical root anchors.','Golden-tree visual identity is inferred from the composite, not a botanical species claim.','Family is exact frame-ID+offset match within A13 only; not a claim of global game inventory.','No source game/reference files modified. No runtime art installed. No image generation or GUI performed.']}
 save(OUT/'source-group-contract.json',contract)
 (OUT/'PLAN.md').write_text('''# A13 first common tree: source-only plan\n\nSelected complete 7-owner static family: Plant 292–298, trunk owner 57,34; duplicate translated by +13,+13.\n\n1. Reproduce: python Project/tools/prepare_a13_first_tree_source.py from repository root. Runtime source JSON/atlas are inputs; only this source contract and ignored diagnostics are outputs.\n2. Inspect source-composite, owner-slices and root-material-local diagnostics. Root R0 is manual wood contact (119,300) +/-4 source px, world (2761,1090); do not use grass tuft, checker shadow or canvas bottom.\n3. Before future art production, approve tree style and size against this original composition. Keep stem/root readable; separate designed crown/trunk/cast material planning, without changing owner depth. No art generation is included here.\n4. Future registration must map candidate coverage into the seven original owners. Preserve y34 trunk and y37 crown/cast, original layer1 and stable order. Whole-tree single-sprite replacement is not faithful. Original shadow must not be retained underneath an extra generated shadow.\n5. Future runtime validation must use the contract's original-flags route: back y32, trunk-front y35 (still before crown y37), and full-group front y38. Capture both sides and intermediate crossings; static path checks do not establish visual runtime success.\n\nProven: source placements, complete duplicated family, static dispatch, owner keys and flag/depth behavior. Manual/inferred: woody ground-contact region, visual material classification, and expected visual overlap until runtime-tested.\n''')
 print(json.dumps({'owners':7,'bounds':b,'root':root,'instances':len(family),'route_steps':len(route),'contract_sha256':sha(OUT/'source-group-contract.json')}))
if __name__=='__main__':main()
