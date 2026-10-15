from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent;P=HERE.parents[1];D=P/'diagnostics/art_source/a13-main-temple';source=json.loads((P/'art_source/a13_main_temple_source/source-group-contract.json').read_text());im=Image.open(HERE/'raw.png').convert('RGBA');a=np.array(im.getchannel('A'));sp=np.array([x['source_composite_xy']for x in source['manual_visible_landmarks']],float)
cp=np.array([[764,979],[425,970],[370,804],[1050,1045],[1110,890],[103,380],[772,833],[1300,505]],float)
s=float(((cp-cp.mean(0))*(sp-sp.mean(0))).sum()/((cp-cp.mean(0))**2).sum());t=sp.mean(0)-s*cp.mean(0);delta=s*cp+t-sp
records=[]
bg=Image.new('RGBA',im.size,(100,110,100,255));bg.alpha_composite(im);local=Image.new('RGB',(720,360),(65,75,70));dr=ImageDraw.Draw(local)
for i,(src,pt,e)in enumerate(zip(source['manual_visible_landmarks'],cp,delta)):
 x,y=map(int,pt);unc=10 if i in [2,4]else 7;records.append({'id':src['id'],'source_xy':src['source_composite_xy'],'candidate_xy':pt.tolist(),'candidate_manual_uncertainty_px':unc,'candidate_alpha':int(a[y,x]),'mapped_source_xy':(s*pt+t).tolist(),'error_source_px':e.tolist(),'distance_source_px':float(np.linalg.norm(e)),'source_uncertainty_px':src['manual_read_uncertainty_px'],'note':'Independent visible material read; upper tread correspondence is less precise than column/lowest tread.'})
 c=bg.crop((x-36,y-36,x+37,y+37)).resize((159,159),Image.Resampling.NEAREST).convert('RGB');cx=i%4*180;cy=i//4*180;local.paste(c,(cx,cy+18));dr.text((cx+2,cy+2),src['id'].split('_')[0]+f'({x},{y}) +/-{unc}',fill='white');dr.rectangle((cx+78,cy+96,cx+83,cy+101),outline='cyan')
local.save(D/'candidate-v2-landmark-local-board.png')
registered=im.transform(tuple(source['composite_size']),Image.Transform.AFFINE,(1/s,0,-t[0]/s,0,1/s,-t[1]/s),resample=Image.Resampling.BICUBIC)
old=Image.open(D/'source-composite.png').convert('RGBA');board=Image.new('RGBA',(1592,695),(100,110,100,255));board.alpha_composite(old,(0,30));board.alpha_composite(registered,(796,30));draw=ImageDraw.Draw(board);draw.text((10,8),'Original 796x665',fill='white');draw.text((806,8),'Candidate: common scale + translation DIAGNOSTIC ONLY',fill='white');board.convert('RGB').save(D/'candidate-v2-common-scale-ab.jpg')
layerboard=Image.new('RGBA',registered.size,(100,110,100,255));layerboard.alpha_composite(registered);draw=ImageDraw.Draw(layerboard)
for o in source['owners_in_draw_order']:
 if o['layer']==0:
  x,y,w,h=o['world_rect'];x-=source['world_bounds_xyxy'][0];y-=source['world_bounds_xyxy'][1];draw.rectangle((x,y,x+w-1,y+h-1),outline=(255,180,30),width=1)
layerboard.convert('RGB').save(D/'candidate-v2-layer0-rectangle-diagnostic.jpg')
report={'status':'single_generated_candidate_geometry_pending_review','raw_sha256':hashlib.sha256((HERE/'raw.png').read_bytes()).hexdigest(),'raw_size':list(im.size),'registration_type':'single isotropic scale plus translation, no rotation/shear/anisotropic or local deformation','scale':s,'translation_source_canvas_px':t.tolist(),'rms_source_px':float(np.sqrt((delta**2).sum(1).mean())),'max_source_px':float(np.linalg.norm(delta,axis=1).max()),'points':records,'edge_alpha_over_32':{'top':int((a[0]>32).sum()),'bottom':int((a[-1]>32).sum()),'left':int((a[:,0]>32).sum()),'right':int((a[:,-1]>32).sum())},'independent_depth_status':'Not registered to original 30 owners; original layer0 rectangles shown only for diagnostic comparison. No native depth PASS.','limits':['Source read uncertainty4-5px and candidate7-10px, so a fit is not exact structure proof.','Left stair and left eave deviation exceeds several source pixels; report before further edits.','Raw PNG preserved byte-for-byte. Technical transformed copy only exists in ignored comparison board.','No ground cast, runtime change or second generation.']}
(HERE/'geometry-diagnostic.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:report[k]for k in ['scale','translation_source_canvas_px','rms_source_px','max_source_px','edge_alpha_over_32']}))
if __name__=='__main__':pass
