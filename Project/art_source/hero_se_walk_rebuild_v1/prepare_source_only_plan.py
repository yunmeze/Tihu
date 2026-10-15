from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
P=Path(__file__).resolve().parent;S=P.parent/'hero_se_walk_source_r5';I=P.parent/'hero_identity_rebuild_candidate_v1/identity-rebuild-v2-raw.png';D=P/'source_only_plan';D.mkdir(exist_ok=True)
# Same crop for all original cells; only layout and nearest magnification.
box=(12,8,68,96);sheet=Image.new('RGBA',(56*3,88*2));refs=[]
for i in range(6):
 f=S/f'source-{51+i}.png';im=Image.open(f).convert('RGBA');tile=im.crop(box);sheet.paste(tile,(i%3*56,i//3*88));refs.append({'source_id':51+i,'path':str(f.relative_to(P.parent)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
sheet.resize((1344,1408),Image.Resampling.NEAREST).save(D/'original-six-common-crop-main-8x.png')
im=Image.open(I).convert('RGBA');parts=[('face hair',(470,15,665,217)),('wine shoulder',(350,230,495,390)),('chest panel',(510,270,640,405)),('waist module',(490,490,665,590)),('fingerless glove',(724,535,805,654)),('knee panel',(450,795,555,905)),('shin panel',(620,865,706,995)),('boot',(618,1014,805,1130))]
board=Image.new('RGBA',(1000,600));d=ImageDraw.Draw(board);records=[]
for i,(label,b) in enumerate(parts):
 x=(i%4)*250+15;y=(i//4)*300+30;crop=im.crop(b);board.paste(crop,(x,y));d.text((x,y-20),label,fill='white');records.append({'label':label,'source_box':b,'destination':[x,y],'resampling':'none'})
board.save(D/'identity-disconnected-small-panels.png');json.dump({'status':'prepared_only_no_generation_authorized_yet','main_crop_per_frame':box,'cropped_native_root':[4,56],'main_magnification':8,'source_frames':refs,'identity_source':str(I.relative_to(P.parent)),'identity_sha256':hashlib.sha256(I.read_bytes()).hexdigest(),'identity_parts':records,'exclusions':['raw-v1','raw-v2','all other generated complete bodies','whole paired legs'],'preservation':'all source pixel RGBA unchanged; no semantic masking or color key; same rectangle crop per sourceframe; body+head complete, source ground checker partly remains'},open(D/'input-provenance.json','w'),indent=2)
