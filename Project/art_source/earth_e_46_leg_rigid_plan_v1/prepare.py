from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json,math,hashlib
P=Path(__file__).resolve().parent;R=P.parents[1];D=R/'diagnostics/earth_e_46_leg_rigid_plan_v1';D.mkdir(exist_ok=True,parents=True);rp=R/'art_source/earth_e_46_49_static_research_v1/46-lower-cleaned.png';raw=Image.open(rp).convert('RGBA');arr=np.array(raw);s=.16173127687142191;t=np.array([-3.0501319865696956,9.3690176482717]);polys={'rear_shin_boot':[(0,300),(206,300),(228,315),(235,330),(243,340),(241,349),(218,361),(213,385),(229,440),(0,440)],'main_shin_boot':[(244,353),(267,361),(291,351),(306,365),(360,410),(360,512),(222,512),(222,405),(234,375)]};masks={}
for k,p in polys.items():
 m=Image.new('L',(512,512));ImageDraw.Draw(m).polygon(p,fill=255);masks[k]=np.array(m)>0;m.save(P/f'{k}-SEGMENT-PROPOSED-mask.png')
overlap=masks['rear_shin_boot']&masks['main_shin_boot'];print('prepartition overlap alpha>=128',int((overlap&(arr[:,:,3]>=128)).sum()));masks['rear_shin_boot'] &= ~masks['main_shin_boot'];Image.fromarray((masks['rear_shin_boot']*255).astype('uint8')).save(P/'rear_shin_boot-SEGMENT-PROPOSED-mask.png');fixed=~(masks['rear_shin_boot']|masks['main_shin_boot']);Image.fromarray((fixed*255).astype('uint8')).save(P/'fixed-upper-and-rest-PROTECT-mask.png')
pts={'rear':{'knee':[230,331],'ankle':[159,376],'toe':[184,417],'source_knee':[32,65],'source_ankle':[26,72],'source_toe':[31,77]},'main':{'knee':[267,354],'ankle':[259,442],'toe':[312,465],'source_knee':[43,65],'source_ankle':[40,84],'source_toe':[48,87]}}
board=Image.new('RGBA',(1536,512),(110,110,110,255));src=Image.open(R/'diagnostics/earth_e_source_shadow_index_audit_v1/46-index18-excluded-NOT-SEMANTICALLY-CERTIFIED.png').convert('RGBA');board.alpha_composite(src.resize((512,512),Image.Resampling.NEAREST),(0,0));registered=raw.transform((512,512),Image.Transform.AFFINE,(1/(4*s),0,-t[0]/s,0,1/(4*s),-t[1]/s),resample=Image.Resampling.BICUBIC);board.alpha_composite(registered,(512,0));di=Image.new('RGBA',(512,512));f=arr.copy();f[:,:,:3]=[145,145,145];f[~fixed,3]=0;di.alpha_composite(Image.fromarray(f).transform((512,512),Image.Transform.AFFINE,(1/(4*s),0,-t[0]/s,0,1/(4*s),-t[1]/s),resample=Image.Resampling.BICUBIC));records={}
for name,color in [('rear',(65,200,255)),('main',(250,180,45))]:
 p=pts[name];ank=np.array(p['ankle'])*s+t;toe=np.array(p['toe'])*s+t;knee=np.array(p['knee'])*s+t;sa=np.array(p['source_ankle']);st=np.array(p['source_toe']);v=toe-ank;des=st-sa;th=math.atan2(des[1],des[0])-math.atan2(v[1],v[0]);Q=np.array([[math.cos(th),-math.sin(th)],[math.sin(th),math.cos(th)]]);delta=sa-Q@ank;newtoe=Q@toe+delta;newknee=Q@knee+delta;rawt=Q@t+delta;piece=arr.copy();piece[:,:,:3]=color;piece[~masks[name+'_shin_boot'],3]=0;inv=Q.T/(4*s);off=-Q.T@rawt/s;mapped=Image.fromarray(piece).transform((512,512),Image.Transform.AFFINE,(inv[0,0],inv[0,1],off[0],inv[1,0],inv[1,1],off[1]),resample=Image.Resampling.BICUBIC);di.alpha_composite(mapped)
 records[name]={'rotation_deg':math.degrees(th),'logical_rigid_translation':delta.tolist(),'raw_to_logical_translation':rawt.tolist(),'fixed_density':s,'source':p,'old_knee_proxy':knee.tolist(),'old_ankle_proxy':ank.tolist(),'old_toe_proxy':toe.tolist(),'proposed_ankle':sa.tolist(),'proposed_toe':newtoe.tolist(),'proposed_proximal_cut_proxy':newknee.tolist(),'cut_proxy_offset_from_fixed_knee':(newknee-knee).tolist(),'cut_proxy_vs_source_knee':(newknee-p['source_knee']).tolist(),'fixed_ankle_to_toe_length':float(np.linalg.norm(v)),'source_ankle_to_toe_length':float(np.linalg.norm(des))}
board.alpha_composite(di,(1024,0));dr=ImageDraw.Draw(board)
for name,p in pts.items():
 for col in [0,1]:
  coords=[np.array(p[k]) if col==0 else np.array(p[k.replace('source_','')])*s+t for k in ['source_knee','source_ankle','source_toe']]
  dr.line([(col*512+int(x*4),int(y*4)) for x,y in coords],fill=(0,255,255) if name=='rear' else (255,200,0),width=2)
  for x,y in coords:dr.ellipse((col*512+x*4-3,y*4-3,col*512+x*4+3,y*4+3),outline='white',width=1)
board.save(D/'source-current-proposed-COLORED-GEOMETRY-ONLY.png')
ov=Image.new('RGBA',(512,512),(110,110,110,255));ov.alpha_composite(raw);od=ImageDraw.Draw(ov)
for (name,poly),color in zip(polys.items(),['cyan','orange']):od.line(poly+[poly[0]],fill=color,width=2)
ov.crop((115,300,345,490)).resize((920,760),Image.Resampling.NEAREST).save(D/'proposed-segment-cuts-raw.png')
# New cloth support is explicitly only technical/authoring proposal in logical coordinates.
joints={'rear_knee_seam':[31,60,38,67],'main_knee_gap':[34,64,45,73]}
for name,box in joints.items():
 m=Image.new('L',(512,512));ImageDraw.Draw(m).rectangle(tuple(int(v*4) for v in box),fill=255);m.save(P/f'{name}-NEW-CLOTH-SUPPORT-REVIEW-mask.png')
 od=ImageDraw.Draw(board);od.rectangle(tuple([1024+box[0]*4,box[1]*4,1024+box[2]*4,box[3]*4]),outline=(255,0,220),width=2)
board.crop((1024,220,1536,380)).resize((1024,320)).save(D/'rigid-seam-support-NOT-ART.png')
j={'status':'no generation; no final limb edit; proposed segmentation and geometry only','raw_sha256':hashlib.sha256(rp.read_bytes()).hexdigest(),'coordinate_system':'512 original v2 frame46 cell; global old sheet x+512','density':s,'existing_lower_translation':t.tolist(),'polygons':polys,'masks_disjoint':True,'exact_alpha_partition':True,'moves':records,'new_cloth_support_logical_review':joints,'fixed_source_uncertainty':{'knee_ankle':3,'toe':2,'old_raw_surface':8},'limits':'source centers drive prospective rigid relation, not independent validation; proximal transformed knee proxy is cut interface, not moved hidden anatomical knee'};(P/'PLAN.json').write_text(json.dumps(j,indent=2)+'\n');print(json.dumps(records))
