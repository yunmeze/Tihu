from pathlib import Path
from PIL import Image,ImageDraw
import io,sys,json,hashlib,numpy as np
P=Path(__file__).resolve().parent;R=P.parents[2];sys.path.insert(0,str(R/'Project/tools'));from lp_original import read_pack,decode_frame
D=R/'Project/diagnostics/earth_e_source_shadow_index_audit_v1';D.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=[R/'原版游戏/Data/Hero/2.lpRes',R/'原版游戏/Data/Hero/Head/0.lpRes'];packs=[read_pack(p) for p in paths];scans=[]
for path,(b,records,anim,key) in zip(paths,packs):
 present=[];mixed=[];pal=set();duplicates=set()
 for i,(off,l,ox,oy) in enumerate(records):
  im=Image.open(io.BytesIO(b[off:off+l]));a=np.array(im);pa=im.getpalette()
  if im.mode!='P':continue
  pal.add(tuple(pa[54:57]));duplicates.update(k for k in range(len(pa)//3) if k!=18 and pa[k*3:k*3+3]==pa[54:57]);yy,xx=np.where(a==18)
  if len(xx):
   present.append(i)
   if len(set(((xx+yy)%2).tolist()))>1:mixed.append(i)
 scans.append({'path':str(path.relative_to(R)),'sha256':sha(path),'records':len(records),'records_with_index18':present,'mixed_parity_records':mixed,'index18_rgb':list(pal),'duplicate_palette_entries_with_same_rgb':list(duplicates)})
proof=[];board=Image.new('RGBA',(1536,1536),(64,68,72,255))
for i,n in enumerate(range(45,51)):
 full=Image.new('RGBA',(128,128));keep=Image.new('RGBA',(128,128));removed=Image.new('RGBA',(128,128));layerstats=[]
 for layer,(b,records,anim,key) in enumerate(packs):
  rec=records[n];off,l,ox,oy=rec;src=Image.open(io.BytesIO(b[off:off+l]));indices=np.array(src);rgba,meta=decode_frame(b,rec,'Hero/2' if layer==0 else 'Hero/Head/0',True);a=np.array(rgba);mask=indices==18;kept=a.copy();cut=a.copy();kept[mask,3]=0;cut[~mask,3]=0
  assert np.array_equal(kept[~mask],a[~mask]);re=np.array(Image.alpha_composite(Image.fromarray(kept),Image.fromarray(cut)));assert np.array_equal(re,a)
  pos=(16+ox,64+oy);full.alpha_composite(rgba,pos);keep.alpha_composite(Image.fromarray(kept),pos);removed.alpha_composite(Image.fromarray(cut),pos)
  yy,xx=np.where(mask);layerstats.append({'layer':layer,'source_byte_offset':off,'source_bytes':l,'dimensions':src.size,'native_offset':[ox,oy],'index18_count':int(mask.sum()),'index18_xy_native':[[int(x),int(y)] for y,x in zip(yy,xx)],'parity':sorted(set(((xx+yy)%2).tolist())),'non18_rgba_unchanged':True,'recomposition_exact':True})
 original=Image.open(P.parent/'earth_hero_e_input_plan_v1'/f'source-{n}.png').convert('RGBA');assert full.tobytes()==original.tobytes()
 # Composite head may occlude body removal. Exact full recomposition is checked too.
 joined=Image.alpha_composite(keep,removed);same=joined.tobytes()==full.tobytes();assert same
 full.save(D/f'{n}-full128-evidence.png');keep.save(D/f'{n}-index18-excluded-NOT-SEMANTICALLY-CERTIFIED.png');removed.save(D/f'{n}-index18-only.png')
 for row,(label,tile) in enumerate([('ORIGINAL',full),('INDEX18 EXCLUDED / inferred body',keep),('INDEX18 ONLY / inferred shadow',removed)]):
  x=i%3*512;y=(i//3*3+row)*256;z=tile.resize((256,256),Image.Resampling.NEAREST);board.alpha_composite(z,(x,y));ImageDraw.Draw(board).text((x+260,y+10),f'{n} {label}',fill='white')
 proof.append({'frame':n,'layers':layerstats,'matches_frozen_full128':True,'full_composite_reconstruction_exact':same})
board.save(D/'original-index-separated-technical-board.png')
j={'status':'exact_index_partition_proven_semantic_shadow_role_strongly_inferred_not_native_renderer_verified','scan':scans,'proof':proof,'source_code_sha':{str(p.relative_to(R)):sha(p) for p in [R/'Project/tools/lp_original.py',R/'参考项目/tools/extract-lp.py',R/'参考项目/tools/native-color-key.py',R/'参考项目/src/batch.js']},'no_generation':True,'no_source_modification':True}
(P/'PIXEL_PROOF.json').write_text(json.dumps(j,indent=2)+'\n')
print('exact6 composite comparisons and partitions passed')
