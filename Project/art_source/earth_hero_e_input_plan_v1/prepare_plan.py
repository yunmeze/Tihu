from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
P=Path(__file__).resolve().parent; R=P.parents[1]; A=P.parent
D=R/'diagnostics/earth_hero_e_input_plan_v1';D.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
J=lambda p:json.loads(p.read_text())
m=J(R/'data/hero/movement.json'); records=[]
for action,ids,cols,scale,old in [('idle',list(range(9,13)),4,6,'hero_e_idle_source_r7'),('walk',list(range(45,51)),3,8,'hero_e_walk_source_r8')]:
 board=Image.new('RGBA',(64*cols,88*((len(ids)+cols-1)//cols))); full=Image.new('RGBA',(128*len(ids),128))
 for i,n in enumerate(ids):
  im=Image.new('RGBA',(128,128)); layers={}
  for name in ['body','head']:
   layer=m['layers'][name]; f=layer['frames'][str(n)];atlas=Image.open(R/layer['atlas'].removeprefix('res://')).convert('RGBA');x,y,w,h=f['rect']; tile=atlas.crop((x,y,x+w,y+h)); digest=hashlib.sha256(tile.tobytes()).hexdigest();assert digest==f['rgba_sha256']
   im.alpha_composite(tile,(16+f['offset'][0],64+f['offset'][1]));layers[name]={'offset':f['offset'],'rect':f['rect'],'rgba_sha256':digest}
  original=Image.open(A/old/f'source-{n}.png').convert('RGBA');assert im.tobytes()==original.tobytes()
  out=P/f'source-{n}.png';im.save(out);board.paste(im.crop((12,8,76,96)),(i%cols*64,i//cols*88));full.paste(im,(i*128,0))
  records.append({'source_id':n,'action':action,'layers':layers,'sha256':sha(out),'rgba_sha256':hashlib.sha256(im.tobytes()).hexdigest(),'matches_historical_source_rgba':True})
 board.resize((board.width*scale,board.height*scale),Image.Resampling.NEAREST).save(P/f'source-{action}-complete-pose-main-{scale}x.png');full.save(P/f'source-{action}-full-128-native.png')
 diag=board.resize((board.width*scale,board.height*scale),Image.Resampling.NEAREST);bg=Image.new('RGBA',diag.size,(45,49,54,255));bg.alpha_composite(diag);draw=ImageDraw.Draw(bg)
 for i,n in enumerate(ids):
  x=i%cols*64*scale;y=i//cols*88*scale;draw.text((x+5,y+5),f'{n} / p{i}',fill='yellow');rx=x+4*scale;ry=y+56*scale;draw.line((rx-8,ry,rx+8,ry),fill='red');draw.line((rx,ry-8,rx,ry+8),fill='red')
 bg.save(D/f'{action}-labelled-root-review.png')
identity=A/'earth_hero_se_idle_v1/raw-v1.png';im=Image.open(identity).convert('RGBA')
parts={'head_face':(213,53,319,171),'chest_black_abdomen':(208,174,340,317),'red_shoulder':(137,157,220,258),'low_waist':(202,303,334,367),'black_thigh_small_side_plate':(180,352,285,466),'fingerless_glove':(119,374,183,448),'graphite_knee':(151,477,240,545),'dark_boot':(255,553,375,649)}
b=Image.new('RGBA',(800,430));draw=ImageDraw.Draw(b)
for i,(name,rect) in enumerate(parts.items()):
 x=i%4*200+10;y=i//4*215+30;draw.text((x,y-20),name,fill='white');b.alpha_composite(im.crop(rect),(x,y))
b.save(P/'approved-se-idle13-disconnected-parts.png')
provenance={'status':'preparation_only_no_generation_no_runtime_no_git','root':[16,64],'canvas':[128,128],'common_crop':[12,8,76,96],'crop_root':[4,56],'source_formula':'base + direction(2) * phases + p','timing':{'idle_ticks':12,'walk_ticks':7,'reference_hz':50,'idle_ms_per_phase':240,'walk_ms_per_phase':140,'boundary':'50 Hz reference/current adapter; not original EXE stopwatch, entry/exit lifecycle or movement-speed proof'},'records':records,'identity_source':str(identity.relative_to(R)),'identity_sha256':sha(identity),'identity_unmodified_crop_rects':parts,'excluded_identity':['old E rebuilt artwork','earlier canonical long silver thighs','old courtyard'],'inputs':[]}
for p in sorted(P.glob('*.png')):provenance['inputs'].append({'path':p.name,'sha256':sha(p)})
(P/'INPUT_PROVENANCE.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
# Preserve only original geometry measurements, explicitly not previous identity or generation strategy.
analysis={'status':'all_10_source_phases_visually_reviewed_2026-10-15','coordinates':'128 canvas, root16,64; points are visible surface proxies, not bones or proven contacts','idle':J(A/'hero_e_idle_source_r7/SOURCE_PHASE_ANALYSIS.json')['frames'],'walk':J(A/'hero_e_walk_source_r8/SOURCE_PHASE_ANALYSIS.json')['frames'],'measurement_origin':'historical source geometry proxies rechecked against full original boards; no old redesigned art used','uncertainty_px':{'crown':1,'boot':2,'clothing_and_hand':3}}
(P/'SOURCE_PHASE_ANALYSIS.json').write_text(json.dumps(analysis,ensure_ascii=False,indent=2)+'\n')
files=[p for p in sorted(P.iterdir()) if p.is_file() and p.name!='MINIMAL_SHA_MANIFEST.json']
deps=[R/'data/hero/movement.json',R/'assets/original/hero/body-movement.png',R/'assets/original/hero/head-movement.png',identity,R/'docs/EARTH_ART_BIBLE_V1.md',A/'earth_base_style_concept_v1/concept.png',R.parent/'参考项目/src/animation.js',R/'docs/HERO_ACTION_TIMING_EVIDENCE.md']
(P/'MINIMAL_SHA_MANIFEST.json').write_text(json.dumps({'purpose':'archive allowlist only; no Git command executed','files':[{'path':p.name,'sha256':sha(p)} for p in files],'read_only_dependencies':[{'path':str(p.relative_to(R.parent)),'sha256':sha(p)} for p in deps],'excluded':['Project/diagnostics/**','runtime assets/scripts','all old rebuilt E artwork']},ensure_ascii=False,indent=2)+'\n')
print('Verified 10 source composites and 20 layer hashes; inputs and provenance saved.')
