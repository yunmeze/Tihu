from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,math,hashlib
P=Path(__file__).resolve().parent;R=P.parents[1];D=R/'diagnostics/earth_e_four_phase_rigid_study_v1';D.mkdir(parents=True,exist_ok=True)
V=R/'art_source/earth_hero_e_walk_v2';raw=Image.open(V/'raw-v2.png').convert('RGBA');reg=json.loads((V/'registration-v2.json').read_text());s=reg['common_uniform_scale_raw_to_logical'];srcpts=json.loads((R/'art_source/earth_e_six_phase_parts_plan_v1/SOURCE_PROXIES.json').read_text())['frames']
# Hand-traced visible armor-root boundaries on each native 512 cell. No hidden anatomy.
data={
45:{'points':[[[162,348],[94,400],[126,443]],[[285,367],[309,433],[370,451]]],'polys':[
[(0,330),(137,330),(150,337),(170,350),(177,358),(157,373),(140,393),(150,470),(0,470)],
[(260,366),(285,375),(310,365),(325,403),(400,403),(400,480),(280,480),(274,410)]]},
47:{'points':[[[226,356],[211,427],[261,461]],[[285,344],[265,391],[307,426]]],'polys':[
[(198,351),(225,358),(248,369),(244,400),(243,419),(286,442),(286,490),(180,490),(183,408)],
[(271,334),(297,345),(314,347),(291,378),(278,391),(321,411),(330,445),(262,444),(243,412),(248,379)]]},
48:{'points':[[[163,353],[94,420],[130,466]],[[292,341],[309,419],[368,426]]],'polys':[
[(0,333),(140,333),(155,343),(173,355),(181,364),(161,383),(143,410),(153,490),(0,490)],
[(269,339),(291,349),(315,340),(324,390),(400,401),(400,460),(279,460),(277,390)]]},
50:{'points':[[[220,357],[203,426],[253,444]],[[302,368],[270,436],[333,475]]],'polys':[
[(195,348),(218,358),(243,370),(230,402),(220,420),(265,432),(269,460),(172,460),(175,408)],
[(279,365),(300,376),(326,365),(332,383),(304,426),(289,438),(347,465),(350,497),(260,497),(241,450),(253,415)]]}}
allrec={}; board=Image.new('RGBA',(1536,2200),(105,105,105,255));cuts=Image.new('RGBA',(1024,1024),(105,105,105,255))
def transform(im,Q,t,density=s):
 inv=Q.T/(4*density);off=-Q.T@t/density
 return im.transform((512,512),Image.Transform.AFFINE,(inv[0,0],inv[0,1],off[0],inv[1,0],inv[1,1],off[1]),resample=Image.Resampling.BICUBIC)
for row,(f,z) in enumerate(data.items()):
 rec=next(x for x in reg['records'] if x['source_id']==f);cell=raw.crop(rec['raw_rect']);a=np.array(cell);t=np.array(rec['translation_logical']);ms=[]
 for poly in z['polys']:
  m=Image.new('L',(512,512));ImageDraw.Draw(m).polygon(poly,fill=255);ms.append(np.array(m)>0)
 # Left screen piece foreground at 47; right foreground otherwise. Exclusive ownership, full RGBA partition.
 front=0 if f==47 else 1;back=1-front;overlap=ms[0]&ms[1];ms[back]&=~ms[front];fixed=~(ms[0]|ms[1]);assert np.all(sum(x.astype(int) for x in ms+[fixed])==1)
 for name,m in zip(['left','right','fixed'],ms+[fixed]):Image.fromarray((m*255).astype('uint8')).save(P/f'{f}-{name}-exclusive-mask.png')
 ov=cell.copy();od=ImageDraw.Draw(ov)
 for poly,col in zip(z['polys'],['cyan','orange']):od.line(poly+[poly[0]],fill=col,width=2)
 for pp in z['points']:
  for x,y in pp:od.ellipse((x-4,y-4,x+4,y+4),outline='magenta',width=2)
 cuts.alpha_composite(ov,(row%2*512,row//2*512));ImageDraw.Draw(cuts).text((row%2*512+8,row//2*512+8),str(f),fill='white')
 layers=[];moves=[];source=srcpts[str(f)]
 for i in range(2):
  cut,ank,toe=np.array(z['points'][i],float);sk,sa,st=np.array(source[1+i*3:4+i*3],float);v=(toe-ank)*s;want=st-sa;th=math.atan2(want[1],want[0])-math.atan2(v[1],v[0]);Q=np.array([[math.cos(th),-math.sin(th)],[math.sin(th),math.cos(th)]]);tt=sa-Q@ank*s
  piece=a.copy();piece[~ms[i],3]=0;layer=transform(Image.fromarray(piece),Q,tt);layers.append(layer);layer.save(P/f'{f}-{["left","right"][i]}-rigid-HD4.png')
  newcut=Q@cut*s+tt;oldcut=cut*s+t
  moves.append({'raw_visible_root_ankle_toe':z['points'][i],'source_knee_ankle_toe':[sk.tolist(),sa.tolist(),st.tolist()],'rotation_deg':math.degrees(th),'raw_to_logical_translation':tt.tolist(),'density':s,'old_cut_proxy':oldcut.tolist(),'new_cut_proxy':newcut.tolist(),'cut_shift_from_fixed_upper':(newcut-oldcut).tolist(),'cut_shift_length':float(np.linalg.norm(newcut-oldcut)),'new_toe':(Q@toe*s+tt).tolist(),'ankle_to_toe_length':float(np.linalg.norm(v)),'source_ankle_to_toe_length':float(np.linalg.norm(want)),'toe_length_residual':float(np.linalg.norm(v)-np.linalg.norm(want))})
 fixeda=a.copy();fixeda[~fixed,3]=0;F=transform(Image.fromarray(fixeda),np.eye(2),t);out=Image.new('RGBA',(512,512))
 for im in [layers[back],layers[front],F]:out.alpha_composite(im)
 out.save(P/f'{f}-RIGID-UNPATCHED-RESEARCH.png');old=transform(cell,np.eye(2),t)
 src=Image.open(R/f'diagnostics/earth_e_source_shadow_index_audit_v1/{f}-index18-excluded-NOT-SEMANTICALLY-CERTIFIED.png').convert('RGBA').resize((512,512),Image.Resampling.NEAREST)
 for col,im in enumerate([src,old,out]):board.alpha_composite(im,(col*512,row*550+24))
 ImageDraw.Draw(board).text((8,row*550+5),f'{f} source | old original registration | rigid only: gaps NOT repaired',fill='white')
 # Actual overlap with fixed upper is measurable, but does not prove believable anatomy.
 fixedalpha=np.array(F)[:,:,3]>=128
 overlaps=[int(((np.array(l)[:,:,3]>=128)&fixedalpha).sum()) for l in layers]
 allrec[f]={'raw_rect':rec['raw_rect'],'original_translation':t.tolist(),'polygons':z['polys'],'exclusive_partition_all_pixels':262144,'preexclusive_overlap_alpha_ge128':int((overlap&(a[:,:,3]>=128)).sum()),'front_piece':front,'moves':moves,'hard_alpha_overlap_with_fixed_upper_HD4_pixels':overlaps,'upper_raw_RGBA_unchanged':True}
board.save(D/'source-old-rigid-four-phase.png');cuts.save(D/'native-cell-cut-lines-and-proxies.png')
(P/'GEOMETRY.json').write_text(json.dumps({'status':'rigid unpatched study, not source pass','uncertainty_source_knee_ankle':3,'uncertainty_source_toe':2,'uncertainty_raw_proxy':8,'records':allrec},indent=2)+'\n')
print(json.dumps({f:[{'angle':round(m['rotation_deg'],2),'root_shift':round(m['cut_shift_length'],2),'length_residual':round(m['toe_length_residual'],2)} for m in v['moves']] for f,v in allrec.items()}))
