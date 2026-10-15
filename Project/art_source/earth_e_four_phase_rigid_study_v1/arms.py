from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,math
P=Path(__file__).resolve().parent;R=P.parents[1];D=R/'diagnostics/earth_e_four_phase_rigid_study_v1';PD=R/'diagnostics/earth_e_49_cloth_patch_v1'
sheet=Image.open(R/'art_source/earth_e_layered_parts_v1/raw.png').convert('RGBA');keep=Image.open(R/'art_source/earth_e_parts_density_review_v1/background-only-proposed-keep-mask.png');s=.079
coreanchor=np.array([30.3023255814,34.8449612403]);records=[]
B=Image.open(PD/'layer49-core-back.png').convert('RGBA');F=Image.open(PD/'layer49-core-front.png').convert('RGBA')
board=Image.new('RGBA',(1536,1024),(105,105,105,255))
for row,f in enumerate([47,48]):
 shift=np.array([1,-1] if f==47 else [1,0]);anchor=coreanchor+shift;target=np.array([44,56] if f==47 else [49,56]);src=Image.open(R/f'diagnostics/earth_e_source_shadow_index_audit_v1/{f}-index18-excluded-NOT-SEMANTICALLY-CERTIFIED.png').convert('RGBA').resize((512,512),Image.Resampling.NEAREST);board.alpha_composite(src,(0,row*512))
 for col,family in enumerate([46,49],1):
  x=512 if family==46 else 1024;arm=sheet.crop((x,0,x+512,512));a=np.array(arm);a[np.array(keep.crop((x,0,x+512,512)))==0,3]=0;arm=Image.fromarray(a)
  pa=np.array([230.5,132.5] if family==46 else [226.5,137.5]);ph=np.array([271,436.5] if family==46 else [321.5,434]);v=(ph-pa)*s;desired=target-anchor;th=math.atan2(desired[1],desired[0])-math.atan2(v[1],v[0]);Q=np.array([[math.cos(th),-math.sin(th)],[math.sin(th),math.cos(th)]]);t=anchor-Q@pa*s;inv=Q.T/(4*s);off=-Q.T@t/s
  layer=arm.transform((512,512),Image.Transform.AFFINE,(inv[0,0],inv[0,1],off[0],inv[1,0],inv[1,1],off[1]),resample=Image.Resampling.BICUBIC)
  out=Image.new('RGBA',(512,512))
  def sh(im):
   z=Image.new('RGBA',(512,512));z.alpha_composite(im,(int(shift[0]*4),int(shift[1]*4)));return z
  for im in [sh(B),layer,sh(F)]:out.alpha_composite(im)
  out.save(P/f'{f}-using-arm{family}-CORE-ONLY-RESEARCH.png');board.alpha_composite(out,(col*512,row*512));hand=Q@ph*s+t
  dr=ImageDraw.Draw(board);xx=col*512;yy=row*512;dr.rectangle((xx+(target[0]-3)*4,yy+(target[1]-3)*4,xx+(target[0]+3)*4,yy+(target[1]+3)*4),outline='magenta',width=2);dr.text((xx+8,yy+8),f'phase{f}, arm{family}: no lower substituted',fill='white')
  records.append({'phase':f,'arm_family_asset':family,'density':s,'anchor':anchor.tolist(),'core_shift':shift.tolist(),'rotation_deg':math.degrees(th),'translation':t.tolist(),'hand':hand.tolist(),'source_hand_region':[target[0]-3,target[1]-3,target[0]+3,target[1]+3],'hand_residual':(hand-target).tolist(),'proxy_span':float(np.linalg.norm(v)),'desired_span':float(np.linalg.norm(desired)),'inside_hand_region':bool(np.all(abs(hand-target)<=3))})
board.save(D/'47-48-source-arm46-arm49-fixed-density.png');(P/'ARMS.json').write_text(json.dumps(records,indent=2,default=float)+'\n');print(records)
