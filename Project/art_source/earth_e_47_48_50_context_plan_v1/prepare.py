from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,math,hashlib
P=Path(__file__).resolve().parent;R=P.parents[1];D=R/'diagnostics/earth_e_47_48_50_context_plan_v1';D.mkdir(parents=True,exist_ok=True);S=R/'art_source/earth_e_four_phase_rigid_study_v1';V=R/'art_source/earth_hero_e_walk_v2'
raw=Image.open(V/'raw-v2.png').convert('RGBA');reg=json.loads((V/'registration-v2.json').read_text());s=reg['common_uniform_scale_raw_to_logical']
# Explicit visible upper-pants extraction plus known old near-hand removal proposals in each native cell.
defs={
47:{'pants':[(211,242),(271,246),(315,282),(343,308),(339,330),(309,346),(281,335),(266,352),(245,366),(214,358),(201,339),(207,301)],'hand':[(228,263),(274,264),(284,291),(270,304),(245,300),(232,287)]},
48:{'pants':[(204,244),(266,244),(297,286),(309,317),(317,340),(294,350),(271,341),(251,333),(225,332),(208,355),(180,368),(155,348),(177,310)],'hand':[(211,267),(243,267),(255,294),(247,306),(229,305),(215,289)]},
50:{'pants':[(211,245),(274,247),(306,282),(339,314),(345,343),(326,365),(301,377),(278,367),(267,346),(249,349),(240,370),(212,359),(194,344),(203,313)],'hand':[(191,265),(222,265),(234,287),(229,305),(209,303),(193,289)]}}
def mapped(im,t):
 return im.transform((512,512),Image.Transform.AFFINE,(1/(4*s),0,-t[0]/s,0,1/(4*s),-t[1]/s),resample=Image.Resampling.BICUBIC)
board=Image.new('RGBA',(1536,1536),(128,128,128,255));results={}
for row,f in enumerate([47,48,50]):
 rec=next(x for x in reg['records'] if x['source_id']==f);t=np.array(rec['translation_logical']);cell=raw.crop(rec['raw_rect']);ca=np.array(cell);ms=[]
 for key in ['pants','hand']:
  im=Image.new('L',(512,512));ImageDraw.Draw(im).polygon(defs[f][key],fill=255);ms.append(np.array(im)>0);im.save(P/f'{f}-old-{key}-RAW-mask.png')
 pants,hand=ms;pants&=np.array(Image.open(S/f'{f}-fixed-exclusive-mask.png'))>0
 # Remove only proposed old-hand overlap, not fill it. Keep holes explicit.
 oldarr=ca.copy();oldarr[~pants|hand,3]=0;old=mapped(Image.fromarray(oldarr),t);old.save(P/f'{f}-old-upper-WITH-HAND-HOLE.png')
 if f in [47,48]:upper=Image.open(S/f'{f}-using-arm49-CORE-ONLY-RESEARCH.png').convert('RGBA');armnote='existing arm49 fixed .079; central shoulder candidate from ARMS.json'
 else:
  sheet=Image.open(R/'art_source/earth_e_layered_parts_v1/raw.png').convert('RGBA');arm=sheet.crop((512,0,1024,512));aa=np.array(arm);keep=np.array(Image.open(R/'art_source/earth_e_parts_density_review_v1/background-only-proposed-keep-mask.png').crop((512,0,1024,512)));aa[keep==0,3]=0
  pa=np.array([230.5,132.5]);ph=np.array([271,436.5]);anchor=np.array([31.3023255814,33.8449612403]);target=np.array([36.,57.]);vec=(ph-pa)*.079;dv=target-anchor;th=math.atan2(dv[1],dv[0])-math.atan2(vec[1],vec[0]);Q=np.array([[math.cos(th),-math.sin(th)],[math.sin(th),math.cos(th)]]);at=anchor-Q@pa*.079;iv=Q.T/(4*.079);of=-Q.T@at/.079
  ar=Image.fromarray(aa).transform((512,512),Image.Transform.AFFINE,(iv[0,0],iv[0,1],of[0],iv[1,0],iv[1,1],of[1]),resample=Image.Resampling.BICUBIC);upper=Image.new('RGBA',(512,512))
  for nm in ['back']:upper.alpha_composite(Image.open(R/f'diagnostics/earth_e_49_cloth_patch_v1/layer49-core-{nm}.png'),(4,-4))
  upper.alpha_composite(ar);upper.alpha_composite(Image.open(R/'diagnostics/earth_e_49_cloth_patch_v1/layer49-core-front.png'),(4,-4));ar.save(P/'50-arm46-rigid-context.png');armnote={'family':46,'density':.079,'rotation_deg':math.degrees(th),'translation':at.tolist(),'hand':(Q@ph*.079+at).tolist(),'source_hand':[36,57],'status':'context candidate only'}
 protected=Image.new('RGBA',(512,512))
 for side in (['right','left'] if f==47 else ['left','right']):protected.alpha_composite(Image.open(S/f'{f}-{side}-rigid-HD4.png'))
 protected.alpha_composite(upper);protected.save(P/f'{f}-protected-original-layers.png')
 out=old.copy();out.alpha_composite(protected);out.save(P/f'{f}-FULL-CONTEXT-UNPATCHED.png')
 # Explicit hand-hole evidence in logical canvas, not automatic inpaint authority.
 handimg=ca.copy();handimg[~(hand&pants),3]=0;hh=mapped(Image.fromarray(handimg),t);hp=np.array(hh)[:,:,3]>0;solid=np.array(protected)[:,:,3]>=128;visible=hp&~solid
 Image.fromarray((visible*255).astype('uint8')).save(P/f'{f}-old-hand-hole-visible-PROPOSED-mask.png')
 src=Image.open(R/f'diagnostics/earth_e_source_shadow_index_audit_v1/{f}-index18-excluded-NOT-SEMANTICALLY-CERTIFIED.png').convert('RGBA').resize((512,512),Image.Resampling.NEAREST)
 annotated=Image.new('RGBA',(512,512),(128,128,128,255));annotated.alpha_composite(out);na=np.array(annotated);na[visible,:3]=[255,0,200];annotated=Image.fromarray(na);dr=ImageDraw.Draw(annotated)
 dr.rectangle((124,176,204,212),outline='yellow',width=2);dr.rectangle((116,240,220,300),outline='cyan',width=2)
 for col,z in enumerate([src,out,annotated]):board.alpha_composite(z,(col*512,row*512))
 ImageDraw.Draw(board).text((row*0+8,row*512+8),f'{f} source | full context unpatched | pink old-hand region; yellow waist; cyan cuffs',fill='white')
 results[f]={'old_raw_rect':rec['raw_rect'],'old_density':s,'old_translation':t.tolist(),'old_upper_polygon':defs[f]['pants'],'old_hand_polygon':defs[f]['hand'],'arm':armnote,'remaining_visible_old_hand_hole_pixels_HD4':int(visible.sum()),'old_upper_note':'explicit old upper context only, hand region cut for diagnosis; no new fabric filled','protection':'original texture layers stay intact; source-over handles semi-alpha; no all-alpha final freeze'}
board.save(D/'three-source-context-defects.png')
for f in [47,48,50]:
 im=Image.open(P/f'{f}-FULL-CONTEXT-UNPATCHED.png');b=Image.new('RGBA',(720,720),(128,128,128,255));b.alpha_composite(im.crop((112,172,232,292)).resize((720,720),Image.Resampling.NEAREST));b.save(D/f'{f}-waist-hand-cuffs-close.png')
(P/'PLAN.json').write_text(json.dumps(results,indent=2)+'\n')
print({f:z['remaining_visible_old_hand_hole_pixels_HD4'] for f,z in results.items()})
