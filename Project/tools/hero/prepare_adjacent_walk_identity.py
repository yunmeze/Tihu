"""Technical, unwarped crops from frozen direction idle raw; no complete generated body input."""
from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
R=Path(__file__).resolve().parents[2]
rects={
'e':{'direction_profile_head':[195,65,300,177],'chest_material':[245,205,300,290],'wine_shoulder':[185,200,246,263],'waist_modules':[225,310,301,350],'fingerless_glove':[185,380,233,438],'knee_material':[220,445,276,510],'shin_material':[185,522,220,575],'boot_material':[180,625,258,668]},
's':{'direction_front_head':[200,55,290,175],'chest_material':[185,195,302,266],'wine_shoulder':[125,139,181,193],'waist_modules':[205,307,277,340],'fingerless_glove':[97,320,143,368],'knee_material':[165,440,219,505],'shin_material':[175,520,208,567],'boot_material':[166,590,206,629]}}
for d in ['e','s']:
 p=R/'art_source'/f'hero_{d}_walk_source_r8';rawp=R/'art_source'/f'hero_{d}_idle_rebuild_v1/raw-v1.png';raw=Image.open(rawp).convert('RGBA')
 board=Image.new('RGBA',(1000,440),(0,0,0,0));dr=ImageDraw.Draw(board)
 for i,(name,box) in enumerate(rects[d].items()):
  x=(i%4)*250;y=(i//4)*220;dr.text((x+8,y+8),name,fill='white');tile=raw.crop(box);board.alpha_composite(tile,(x+30,y+45))
 board.save(p/'direction-matched-identity-fragments.png')
 ids=range(45,51) if d=='e' else range(57,63);main=Image.new('RGBA',(192,176));lower=Image.new('RGBA',(192,100))
 for i,fid in enumerate(ids):
  im=Image.open(p/f'source-{fid}.png').convert('RGBA');main.paste(im.crop((12,8,76,96)),((i%3)*64,(i//3)*88));lower.paste(im.crop((12,46,76,96)),((i%3)*64,(i//3)*50))
 main.resize((1536,1408),Image.Resampling.NEAREST).save(p/'original-six-body-common-crop-main-8x.png');lower.resize((1536,800),Image.Resampling.NEAREST).save(p/'original-six-lower-detail-8x.png')
 contract={'status':'prepared_only_pending_parent_review_no_generation','direction':d.upper(),'source_raw':str(rawp.relative_to(R)),'source_raw_sha256':hashlib.sha256(rawp.read_bytes()).hexdigest(),'rectangles':rects[d],'operations':'Exact rectangular crop and unscaled paste; no edited RGBA, no full body/whole standing leg/paired legs. Head is direction-matched identity only, not pose authority.','pose_inputs':['original-six-body-common-crop-main-8x.png','original-six-lower-detail-8x.png'],'pose_crop_native':[12,8,76,96],'pose_crop_root':[4,56],'identity_input':'direction-matched-identity-fragments.png','priority':'All original six complete bodies are sole pose/camera/phase authority. Identity fragments only specify face/material/armor construction; never freeze head motion or copy idle leg silhouette.','source_shadow':'Original checker retained; partial checker outside common body crop may be omitted by rectangle only. No black/same-color subtraction.'}
 (p/'identity-input-contract.json').write_text(json.dumps(contract,indent=2)+'\n')
