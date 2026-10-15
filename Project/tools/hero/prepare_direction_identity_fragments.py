"""Technical unchanged rectangular swatches for source-first E/S trials.
No full generated person, head silhouette or paired legs is included.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
ROOT=Path(__file__).resolve().parents[2];art=ROOT/'art_source';src=art/'hero_identity_rebuild_candidate_v1/identity-rebuild-v2-raw.png';im=Image.open(src).convert('RGBA')
parts=[('hair texture only',(500,35,590,108)),('eye eyebrow detail',(567,126,631,158)),('silver chest material',(520,293,610,373)),('wine shoulder material',(382,256,465,330)),('waist module',(510,505,620,575)),('fingerless glove',(724,548,800,650)),('knee material',(470,812,535,878)),('boot armor detail',(700,1060,784,1109))]
for d in ['e','s']:
 p=art/f'hero_{d}_idle_source_r7';board=Image.new('RGBA',(1000,440));dr=ImageDraw.Draw(board);records=[]
 for i,(label,b) in enumerate(parts):
  x=i%4*250+20;y=i//4*220+40;board.paste(im.crop(b),(x,y));dr.text((x,y-22),label,fill='white');records.append({'label':label,'source_box':b,'destination':[x,y],'resampling':'none'})
 board.save(p/'identity-small-material-features.png');(p/'identity-input-contract.json').write_text(json.dumps({'status':'reference_only_no_direction_design_generated','direction':d.upper(),'source':str(src.relative_to(art)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'parts':records,'excluded':['complete generated face/head silhouette','complete generated body or pairedlegs','SE stance/camera'],'direction_rule':'Original E four figures determine strict screen-right profile' if d=='e' else 'Original S four figures determine front-facing camera, never inherit SE torso turn','identity_uncertainty':'Current design has only SE fullbody reference. These small features/materials do not constitute an already-approved E/S head or plate projection; new direction must be independently reviewed.'},indent=2)+'\n')
