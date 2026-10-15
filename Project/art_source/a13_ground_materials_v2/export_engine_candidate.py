"""Export bounded diagnostic-only mirror terrain. Does not modify runtime or maps."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,runpy
P=Path(__file__).resolve().parents[2]; B=Path(__file__).resolve().parent
q=runpy.run_path(str(B/'diagnose_world_materials.py')); ID,RGB,F=q['ID'],q['RGB'],q['F']; d=P/'assets/scifi/environment/a13_ground_mirror_v2_candidate';d.mkdir(parents=True,exist_ok=True)
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
material={}
for k in ['grass','soil']:
 raw=B/k/'raw.png';im=Image.open(raw).convert('RGB');out=d/f'{k}-768.png';im.resize((768,768),Image.Resampling.LANCZOS).save(out)
 material[k]={'texture':'res://'+str(out.relative_to(P)),'sha256':h(out),'size':[768,768],'raw_provenance':str(raw.relative_to(P)),'raw_sha256':h(raw),'derivation':'one uniform LANCZOS resample of immutable raw; no per-tile RGB edits'}
mask=np.zeros((192,480,3),dtype='uint8');stone=np.zeros((192,480,4),dtype='uint8'); bindings=[]
for i,sid in enumerate(sorted(ID)):
 x=(i%5)*96;y=(i//5)*64;s=ID[sid];enc=np.choose(s,[0,127,255]).astype('uint8');mask[y:y+64,x:x+96,:]=enc[:,:,None]
 if sid in RGB:stone[y:y+64,x:x+96,:3]=RGB[sid]
 stone[y:y+64,x:x+96,3]=np.where(s==2,255,0).astype('uint8')
 bindings.append({'signed_id':sid,'source_pack':'Map/Res/FloorBig','source_frame':abs(sid),'size':[96,64],'mask_rect':[x,y,96,64],'stone_rect':[x,y,96,64],'semantic_counts':{k:int((s==v).sum()) for k,v in [('grass',0),('soil',1),('visible_stone',2)]}})
Image.fromarray(mask).save(d/'semantic-atlas.png');Image.fromarray(stone).save(d/'stone-atlas.png')
placements=[]
for f in F['owners_in_draw_order']:
 placements.append({k:f[k] for k in ['key','signed_id','cell','stable_source_order','source_cell','source_map_byte_offset','world_rect']})
m={'schema':'a13-ground-mirror-material-candidate-v1','status':'optional bounded engine diagnostic approved; not default/final terrain','map':'A13','scope_policy':'only exact listed143 placement keys; all others original source even if same ID','placements':placements,'bindings':bindings,'materials':material,'semantic_atlas':{'texture':'res://'+str((d/'semantic-atlas.png').relative_to(P)),'sha256':h(d/'semantic-atlas.png'),'size':[480,192],'values':{'0':'grass','127':'soil','255':'visible_generated_stone'},'filter':'nearest'},'stone_atlas':{'texture':'res://'+str((d/'stone-atlas.png').relative_to(P)),'sha256':h(d/'stone-atlas.png'),'size':[480,192],'filter':'nearest','alpha':'binary technical material mask; RGB from frozen uniformly sampled context'},'sampling':{'world_origin':[0,0],'material_period':[768,768],'mode':'mirror-repeat','superperiod':[1536,1536],'filter':'nearest','address':'i=floor(world_pixel); r=posmod(i,1536); texel=r if r<768 else 1535-r; sample (texel+0.5)/768','local_mask':'floor(local pixel) in original96x64 rect; atlas sample at texel center','camera_independent':True,'claim':'sampling-assisted continuity, not naturally seamless raw'},'source_contract_sha256':h(P/'art_source/a13_ground_source/source-group-contract.json'),'context_raw_provenance':'art_source/a13_ground_style_candidate_v1/raw.png','context_raw_sha256':h(P/'art_source/a13_ground_style_candidate_v1/raw.png'),'context_uniform_scale':480/1717,'geometry':'original placement rectangles preserved; source visible road centerline read +/-3px; visible stone faces read +/-1px. No collision changes.','limitations':['Only143 listed placements; map outside scope remains original.','Mirror symmetric dark motifs and residual fine grain remain.','Stone masks follow visible source/generated material evidence, not exact source pixel geometry; inspect road width and fringe.','No native approval yet.','No new terrain shadow: receive existing scene shadows in original draw order.']}
(d/'registration.json').write_text(json.dumps(m,indent=2)+'\n')
# Standalone numerical decode checks for exported atlases/fields against offline raster.
ma=np.asarray(Image.open(d/'semantic-atlas.png'));sa=np.asarray(Image.open(d/'stone-atlas.png')); tex={k:np.asarray(Image.open(d/f'{k}-768.png')) for k in material};bd={b['signed_id']:b for b in bindings}
x0,y0,x1,y1=F['complete_tile_context_bounds_xyxy'];out=np.zeros((y1-y0,x1-x0,3),dtype='uint8')
for f in placements:
 x,y,w,hh=f['world_rect'];b=bd[f['signed_id']];ax,ay,_,_=b['mask_rect'];codes=ma[ay:ay+hh,ax:ax+w,0];yy,xx=np.indices((hh,w));u=(xx+x)%1536;v=(yy+y)%1536;u=np.where(u<768,u,1535-u);v=np.where(v<768,v,1535-v);a=tex['grass'][v,u].copy();a[codes==127]=tex['soil'][v,u][codes==127];a[codes==255]=sa[ay:ay+hh,ax:ax+w,:3][codes==255];out[y-y0:y-y0+hh,x-x0:x-x0+w]=a
ref=np.asarray(Image.open(P/'diagnostics/art_source/a13-ground/world-material-v2/first143-period768-mirror.png'));diff=np.abs(out.astype(int)-ref.astype(int));assert diff.max()==0
assert len(placements)==143 and len({f['key'] for f in placements})==143 and len(bindings)==15
files=[{'path':str(f.relative_to(P.parent)),'bytes':f.stat().st_size,'sha256':h(f)} for f in sorted(d.iterdir()) if f.is_file() and f.suffix in ['.png','.json']]
qa={'placements':143,'unique_keys':143,'bindings':15,'exported_vs_offline_max_rgb':int(diff.max()),'changed_pixels':int(np.any(diff,axis=2).sum()),'sampling_rects_out_of_bounds':0,'runtime_scripts_modified':False,'stage':files}
(P/'diagnostics/art_source/a13-ground/materials-v2-engine-export-qa.json').write_text(json.dumps(qa,indent=2)+'\n');(P/'diagnostics/art_source/a13-ground/materials-v2-engine-git-stage.json').write_text(json.dumps({'files':files,'total_bytes':sum(f['bytes'] for f in files)},indent=2)+'\n');print(json.dumps({k:v for k,v in qa.items() if k!='stage'}));print('registration',h(d/'registration.json'))
