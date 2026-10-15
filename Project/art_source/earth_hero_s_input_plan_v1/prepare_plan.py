#!/usr/bin/env python3
"""Read original packs; write only this input package and its diagnostics. No generation/runtime/Git."""
from pathlib import Path
import hashlib,json,sys,itertools
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent; R=P.parents[1]; A=P.parent
D=R/'diagnostics/earth_hero_s_input_plan_v1';D.mkdir(parents=True,exist_ok=True)
sys.dont_write_bytecode=True
sys.path.insert(0,str(R/'tools'))
from lp_original import read_pack,decode_frame
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rgba=lambda im:hashlib.sha256(im.tobytes()).hexdigest()
J=lambda p:json.loads(p.read_text())
def dump(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
m=J(R/'data/hero/movement.json');assert m['directions'].index('S')==4
packs={};deps=[R/'data/hero/movement.json',R/'tools/lp_original.py']
for name in ['body','head']:
 l=m['layers'][name];path=R.parent/l['source'];assert sha(path)==l['source_sha256']
 packs[name]=read_pack(path);deps += [path,R/l['atlas'].removeprefix('res://')]
records=[];composites={};pairwise=[]
for action,count,base,ticks,old in [('idle',4,1,12,'hero_s_idle_source_r7'),('walk',6,33,7,'hero_s_walk_source_r8')]:
 assert m['actions'][action]=={'base':base,'phases':count,'actor_ticks_per_phase':ticks}
 ids=[base+4*count+p for p in range(count)];full=Image.new('RGBA',(128*count,128))
 for phase,n in enumerate(ids):
  im=Image.new('RGBA',(128,128));layers={}
  for name in ['body','head']:
   data,recs,animated,key=packs[name];l=m['layers'][name];f=l['frames'][str(n)]
   tile,meta=decode_frame(data,recs[n],l['pack'],animated)
   x,y,w,h=f['rect'];at=Image.open(R/l['atlas'].removeprefix('res://')).convert('RGBA').crop((x,y,x+w,y+h))
   assert rgba(tile)==rgba(at)==f['rgba_sha256'];assert meta['offset']==f['offset']
   im.alpha_composite(tile,(16+f['offset'][0],64+f['offset'][1]));layers[name]={'offset':f['offset'],'rect':f['rect'],'rgba_sha256':rgba(tile),'decoded_directly_from_lpRes':True}
  oldpath=A/old/f'source-{n}.png';deps.append(oldpath)
  oldim=Image.open(oldpath).convert('RGBA');assert im.tobytes()==oldim.tobytes()
  im.save(P/f'source-{n}.png');full.paste(im,(128*phase,0));composites[n]=im
  records.append({'source_id':n,'action':action,'phase':phase,'reference_start_tick':phase*ticks,'duration_ticks':ticks,'layers':layers,'sha256':sha(P/f'source-{n}.png'),'rgba_sha256':rgba(im),'historical_source_rgba_match':True})
 full.save(P/f'source-{action}-full-128-native.png')
 full.resize((full.width*4,512),Image.Resampling.NEAREST).save(P/f'source-{action}-full-128-4x.png')
 bg=Image.new('RGBA',(full.width*4,512),(45,49,54,255));bg.alpha_composite(full.resize(bg.size,Image.Resampling.NEAREST));dr=ImageDraw.Draw(bg)
 for i,n in enumerate(ids):
  x=i*512;dr.rectangle((x,0,x+511,511),outline='gray');dr.text((x+8,8),f'{n} / p{i} / {ticks} ticks',fill='yellow');dr.line((x+56,256,x+72,256),fill='red');dr.line((x+64,248,x+64,264),fill='red')
 bg.save(D/f'{action}-full-labelled.png')
 for a,b in itertools.combinations(ids,2):pairwise.append({'a':a,'b':b,'different_rgba_pixels':sum(x!=y for x,y in zip(composites[a].getdata(),composites[b].getdata()))})
# Approved current Earth assets only. Native HD4 parts, not full figures or paired legs.
part_specs={
 'se_idle13':('se_idle_v1',{'head_face':(140,60,199,118),'small_chest':(144,121,190,171),'red_shoulder':(108,117,145,157),'black_thigh_sideplate':(127,199,168,251),'glove':(103,205,130,236),'knee':(131,249,162,278),'boot':(167,295,214,326)}),
 'e_idle9':('e_idle_v1',{'head_face':(139,57,187,106),'chest_side':(165,112,195,158),'red_shoulder':(132,106,159,139),'black_thigh_sideplate':(143,201,181,242),'glove':(128,193,151,215),'knee':(132,263,151,290),'boot':(122,318,177,351)})}
identity=[]
for label,(folder,parts) in part_specs.items():
 path=R/'assets/earth/hero'/folder/'body.png';manifest=path.with_name('manifest.json');im=Image.open(path).convert('RGBA');board=Image.new('RGBA',(1050,140));dr=ImageDraw.Draw(board)
 assert sha(path)==J(manifest)['texture_sha256']
 for i,(name,rect) in enumerate(parts.items()):
  crop=im.crop(rect);board.alpha_composite(crop,(i*150+15,35));dr.text((i*150+3,8),name,fill='white')
 board.save(P/f'approved-{label}-disconnected-parts.png');identity.append({'source':str(path.relative_to(R)),'sha256':sha(path),'parts_native_hd4_xyxy':parts,'role':'SE13 canonical identity' if label=='se_idle13' else 'E9 secondary side construction only; not S pose'})
 deps += [path,manifest]
# Historical numeric source proxies only; deliberately exclude old generated identity and old prompts.
idle=J(A/'hero_s_idle_source_r7/SOURCE_PHASE_ANALYSIS.json')['frames']
walk=J(A/'hero_s_walk_source_r8/SOURCE_VISIBLE_CHAIN_ANALYSIS.json')
for f in idle:
 assert f['composite_rgba_sha256']==rgba(composites[f['source_id']])
 f.pop('surface_proxies_common_crop_px',None)
 f['boot_proxy_semantics']='Legacy boot_tip is bright-toe interior proxy; terminal edge separately L(33,83),R(47,87), tolerance1. Do not mix.'
 f['visible_material_chains']={'L':{'P':[33,59],'C':[33,64],'S':[33,72],'A':[33,78],'T':[33,83]},'R':{'P':[44,59],'C':[45,64],'S':[46,75],'A':[46,82],'T':[47,87]}}
 f['chain_uncertainty_px']={'P':3,'C':2,'S':2,'A':2,'T':1}
 f['occlusion']='Separated screen-side shafts; upper legs obscured by coat/trousers. No proved front/back physical leg identity or contact. Both hand patches visible, cuffs hide wrist.'
for f in walk['frames']:assert f['source_rgba_sha256']==rgba(composites[f['source_id']])
analysis={'status':'10 full source phases visually reviewed; numeric legacy source proxies cross-checked; no new S design approved','root':[16,64],'canvas':[128,128],'coordinate_policy':'screen L/R, not anatomical side. P cloth fold, C material boundary, S boot surface, A narrowing above toe, T visible terminal. Not joints/contact. Hidden points null.','idle':idle,'walk':walk['frames'],'walk_transitions':walk['adjacent_transitions'],'walk_loop':walk['loop_62_to_57'],'idle_to_walk':walk['idle_to_walk'],'pairwise':pairwise,'proxy_comparison_policy':'Do not compare source hand-patch center with new fingertips; use homologous visible material regions with uncertainty. Crown-relative differences include head bob and hairstyle, not recovered bone swing. Compare absolute same-root and crown-relative changes separately; no automatic anatomical pass score.'}
dump(P/'SOURCE_PHASE_ANALYSIS.json',analysis)
# Annotated evidence is diagnostic only.
for action,frames in [('idle',idle),('walk',walk['frames'])]:
 board=Image.new('RGBA',(len(frames)*256,352),(45,49,54,255));dr=ImageDraw.Draw(board)
 for i,f in enumerate(frames):
  n=f['source_id'];tile=composites[n].crop((16,8,80,96)).resize((256,352),Image.Resampling.NEAREST);board.alpha_composite(tile,(i*256,0));dr.text((i*256+4,4),f'{n}: surface only',fill='white')
  for side,col in [('L','cyan'),('R','orange')]:
   chain=f['visible_material_chains'][side] if action=='idle' else {p['id']:p['xy'] for p in f['legs'][side]['visible_material_chain']}
   pts=[(i*256+(xy[0]-16)*4,(xy[1]-8)*4) for xy in chain.values()];dr.line(pts,fill=col,width=1)
   for (name,xy),pt in zip(chain.items(),pts):dr.ellipse((pt[0]-2,pt[1]-2,pt[0]+2,pt[1]+2),fill=col);dr.text((pt[0]+4,pt[1]-4),name,fill=col)
 board.save(D/f'{action}-surface-chains-not-skeleton.png')
provenance={'status':'preparation only; no generation/Git/runtime/GUI','direction_index':4,'source_formula':'base + 4*phases + p','root':[16,64],'timing':{'idle_ticks':12,'walk_ticks':7,'reference_hz':50,'idle_cycle_ticks':48,'walk_cycle_ticks':42,'boundary':'reference/current adapter only; original EXE clock producer/state lifecycle/speed not proven'},'records':records,'identity':identity,'excluded_identity':['all old hero_s rebuilt/generated artwork','courtyard','earlier long silver thigh canonical','E walk rejected candidates'],'reproduction':'python Project/art_source/earth_hero_s_input_plan_v1/prepare_plan.py'}
dump(P/'INPUT_PROVENANCE.json',provenance)
deps += [A/'hero_s_idle_source_r7/SOURCE_PHASE_ANALYSIS.json',A/'hero_s_walk_source_r8/SOURCE_VISIBLE_CHAIN_ANALYSIS.json',R/'docs/EARTH_ART_BIBLE_V1.md',A/'earth_base_style_concept_v1/concept.png',R.parent/'参考项目/src/animation.js',R/'docs/HERO_ACTION_TIMING_EVIDENCE.md',R/'assets/earth/hero/se_walk_v1/body.png',R/'assets/earth/hero/se_walk_v1/manifest.json']
assert sha(R/'assets/earth/hero/se_walk_v1/body.png')==J(R/'assets/earth/hero/se_walk_v1/manifest.json')['texture_sha256']
files=[p for p in sorted(P.iterdir()) if p.is_file() and p.name!='MINIMAL_SHA_MANIFEST.json']
dump(P/'MINIMAL_SHA_MANIFEST.json',{'purpose':'archive allowlist, NOT a Git commit','files':[{'path':p.name,'sha256':sha(p)} for p in files],'read_only_dependencies':[{'path':str(p.relative_to(R.parent)),'sha256':sha(p)} for p in deps],'exclude':['Project/diagnostics/**','runtime changes','old generated S identity']})
assert all(x['different_rgba_pixels']>0 for x in pairwise)
print('PASS: 20 direct LP decoded layers = atlas hashes; 10 composites = historical source RGBA; 21 distinct pairs. No generation/runtime/Git/GUI.')
