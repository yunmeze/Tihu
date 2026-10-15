from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,shutil
P=Path(__file__).resolve().parent;R=P.parents[1];C=P.parent/'earth_hero_s_walk_v1';D=R/'diagnostics/earth_hero_s_walk_edit_v1';D.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
aim=Image.open(C/'raw-v1.png').convert('RGBA');bim=Image.open(P/'raw-edit-v1.png').convert('RGBA');assert aim.size==bim.size==(1536,1024);req=json.loads((P/'request-v1.json').read_text());assert sha(C/'registration-v1.json')==req['frozen_registration_sha256'];shutil.copyfile(C/'registration-v1.json',P/'frozen-registration.json');reg=json.loads((P/'frozen-registration.json').read_text());s=reg['common_scale_raw_to_logical'];aa=np.array(aim);bb=np.array(bim);oldclear=aa[:,:,3]==0
alpha={'old_clear_pixel_count':int(oldclear.sum()),'old_clear_now_nonzero':int(((bb[:,:,3]>0)&oldclear).sum()),'old_clear_now_alpha128plus':int(((bb[:,:,3]>=128)&oldclear).sum()),'edited_alpha_zero_total':int((bb[:,:,3]==0).sum()),'edited_alpha_min':int(bb[:,:,3].min()),'edited_alpha_max':int(bb[:,:,3].max()),'max_new_alpha_in_old_clear':int(bb[:,:,3][oldclear].max()),'warning':'NO mask cleanup or background removal performed; all original edited alpha retained in raw and registered diagnostic.'}
out=Image.new('RGBA',(3072,512));rows=[]
for i,r in enumerate(reg['records']):
 x=(i%3)*512;y=(i//3)*512;old=aim.crop((x,y,x+512,y+512));new=bim.crop((x,y,x+512,y+512));tr=np.array(r['translation']);tx,ty=tr;k=4*s;t=new.transform((512,512),Image.Transform.AFFINE,(1/k,0,-tx/s,0,1/k,-ty/s),Image.Resampling.BICUBIC);out.paste(t,(i*512,0));rows.append({'source_id':57+i,'old_registered_crown_Lboot_Rboot':r['registered_crown_Lboot_Rboot'],'old_LminusR_terminal_y':r['registered_crown_Lboot_Rboot'][1][1]-r['registered_crown_Lboot_Rboot'][2][1],'source_LminusR_terminal_y':r['source_crown_Lboot_Rboot'][1][1]-r['source_crown_Lboot_Rboot'][2][1],'edited_contour_measurement':None,'reason':'Edited alpha has no reliable body/background contour; do not recover body by masking or pretend alpha extrema are toes.'})

out.save(P/'body-density4-REJECTED-DIAGNOSTIC.png');dump(P/'EDIT_REVIEW.json',{'status':'FAILED_transparency_and_costume_no_native_no_runtime','same_raw_dimensions':True,'registration_unchanged':True,'registration_sha256':sha(P/'frozen-registration.json'),'raw_sha256':sha(P/'raw-edit-v1.png'),'alpha':alpha,'measurement_threshold':None,'measurement_boundary':'Prior alpha254 contour attempt failed because body also lacks alpha254 pixels. No reliable new contour measurements claimed. Old/source values preserved; no masks applied to raw/diagnostic.','records':rows})
for factor in [1,2]:
 u=factor*128;b=Image.new('RGBA',(6*u,4*u),(64,68,72,255));dr=ImageDraw.Draw(b);oldatlas=Image.open(C/'body-density4-DIAGNOSTIC.png');idle=Image.open(R/'assets/earth/hero/s_idle_v1/body.png').crop((0,0,512,512))
 for i in range(6):
  source=Image.open(P.parent/'earth_hero_s_input_plan_v1'/f'source-{57+i}.png').convert('RGBA')
  for row,t in enumerate([source,oldatlas.crop((i*512,0,(i+1)*512,512)),out.crop((i*512,0,(i+1)*512,512)),idle]):
   b.alpha_composite(t.resize((u,u),Image.Resampling.NEAREST if row==0 else Image.Resampling.LANCZOS),(i*u,row*u));dr.text((i*u+3,row*u+3),['source','old walk','FAILED edit','approved idle'][row]+str(57+i),fill='white')
 b.save(D/f'source-old-edit-idle-same-logical-{factor}x.png')
b=Image.new('RGBA',(1536,256),(64,68,72,255));dr=ImageDraw.Draw(b)
for j,(label,t) in enumerate([('idle17',idle),('edit60',out.crop((1536,0,2048,512))),('edit61',out.crop((2048,0,2560,512))),('edit62',out.crop((2560,0,3072,512))),('edit57',out.crop((0,0,512,512))),('idle17',idle)]):b.alpha_composite(t.resize((256,256),Image.Resampling.LANCZOS),(j*256,0));dr.text((j*256+3,3),label,fill='white')
b.save(D/'FAILED-loop-and-idle-2x.png')
print(json.dumps({'alpha':alpha,'gaps':[{'id':r['source_id'],'source':r['source_LminusR_terminal_y'],'old':r['old_LminusR_terminal_y'],'edit':r['edited_contour_measurement']} for r in rows]},indent=2))
