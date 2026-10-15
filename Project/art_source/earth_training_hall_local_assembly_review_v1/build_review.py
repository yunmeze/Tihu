"""Technical alpha ownership and fixed canvas-scale diagnostic, never paint/warp stairs."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent;A=HERE.parent
SHA='5dc43ba8c8f2b5c23832aa5e3178cde41546e5077dfb96ae7c5163d73e851d75'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mask(poly):
 m=Image.new('L',(512,512));ImageDraw.Draw(m).polygon(poly,fill=255);return m
# These select existing pixels only. Exterior contours remain generated alpha, not polygon-colored material.
left_new=[(185,166),(207,154),(227,169),(229,186),(325,249),(371,290),(391,281),(405,291),(405,310),(385,322),(385,385),(295,433),(284,434),(274,425),(273,415),(111,304),(101,295),(87,300),(80,287),(84,254),(95,245),(183,177)]
left_old=[(185,166),(208,154),(228,169),(230,185),(327,249),(327,265),(340,271),(352,283),(352,293),(342,300),(342,366),(276,404),(261,404),(249,388),(249,380),(113,297),(94,291),(94,258),(103,246),(186,178)]
old_pier=[(326,238),(374,259),(435,233),(435,260),(428,266),(393,278),(393,290),(378,299),(369,300),(351,290),(350,280),(339,271),(328,269),(325,264)]
right_new=[(134,267),(151,263),(170,277),(306,205),(304,196),(304,183),(318,176),(332,184),(416,278),(419,317),(404,326),(393,324),(241,408),(226,416),(213,409),(148,372),(148,286),(133,282)]
right_old=[(133,267),(151,263),(170,278),(307,206),(304,197),(304,183),(318,176),(332,184),(418,278),(420,320),(405,327),(393,326),(242,411),(226,418),(211,409),(147,373),(147,286),(132,282)]
def main():
 assert sha(A/'earth_training_hall_candidate_v2/raw.png')==SHA
 original=Image.open(A/'earth_training_hall_candidate_v2/raw.png').convert('RGBA');base=original.copy();records={}
 for side,origin,np_,op_ in [('left',(130,550),left_new,left_old),('right',(850,635),right_new,right_old)]:
  path=A/f'earth_training_hall_{side}_stair_candidate_v1/raw.png';generated=Image.open(path).convert('RGBA');assert generated.width==generated.height
  local=generated.resize((512,512),Image.Resampling.LANCZOS);nm=mask(np_);om=mask(op_);newarr=np.asarray(local).copy();newarr[:,:,3]=np.minimum(newarr[:,:,3],np.asarray(nm));layer=Image.fromarray(newarr);layer.save(HERE/f'{side}-stair-pixel-layer.png');nm.save(HERE/f'{side}-new-material-selection.png');om.save(HERE/f'{side}-old-stair-retirement.png')
  arr=np.asarray(base).copy();x,y=origin;ret=(np.asarray(nm)>0)|(np.asarray(om)>0);region=arr[y:y+512,x:x+512];region[ret]=0;base=Image.fromarray(arr);base.alpha_composite(layer,origin)
  if side=='left':
   pm=mask(old_pier);old=original.crop((x,y,x+512,y+512));oa=np.asarray(old).copy();oa[:,:,3]=np.minimum(oa[:,:,3],np.asarray(pm));preserve=Image.fromarray(oa);preserve.save(HERE/'left-original-main-pier-preserved.png');ba=np.asarray(base).copy();rr=ba[y:y+512,x:x+512];sel=np.asarray(pm)>0;rr[sel]=np.asarray(old)[sel];base=Image.fromarray(ba);pm.save(HERE/'left-original-main-pier-selection.png')
  records[side]={'raw_path':str(path.relative_to(A.parent)),'raw_sha256':sha(path),'actual_raw_size':list(generated.size),'scale_to_512_crop':512/generated.width,'whole_raw_translation':list(origin),'new_material_selection_512_xy':np_,'old_stair_retirement_512_xy':op_,'original_main_pier_overlay_512_xy':old_pier if side=='left'else None,'operations':'One uniform full-canvas Lanczos reduction, transparent alpha selection, original-stair retirement, original left pier overlay. No RGB painting/blur/warp; no bbox refit.'}
 base.save(HERE/'full-building-candidate-review.png')
 bg=Image.new('RGBA',base.size,(90,100,105,255));bg.alpha_composite(base);bg.convert('RGB').save(HERE/'full-building-native-gray.png')
 font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
 for side,origin in [('left',(130,550)),('right',(850,635))]:
  x,y=origin;b=Image.new('RGB',(1536,552),(90,100,105));dr=ImageDraw.Draw(b)
  for off,im,label in [(0,original.crop((x,y,x+512,y+512)),'ORIGINAL V2 CONTEXT'),(512,Image.open(A/f'earth_training_hall_{side}_stair_candidate_v1/raw.png').resize((512,512),Image.Resampling.LANCZOS),'FIXED-SCALE LOCAL CANDIDATE'),(1024,base.crop((x,y,x+512,y+512)),'PIXEL-LAYER SEAM REVIEW; NOT FINAL')]:
   q=Image.new('RGBA',(512,512),(90,100,105,255));q.alpha_composite(im);b.paste(q.convert('RGB'),(off,40));dr.text((off+8,12),label,font=font,fill='white')
  b.save(HERE/f'{side}-native-seam-review.png')
 report={'status':'MANUAL REVIEW DIAGNOSTIC ONLY; no runtime assets replaced, no promotion. Selection boundaries are visible material traces and must be inspected at native pixels.','base_v2_sha256':SHA,'fixed_reference':'Inherited edit_plan_v1 density/translation unchanged. These operations do not establish a valid runtime registration.','sides':records,'seam_limits':['Binary alpha partition; no feathering, blur, cloning or color repaint.','Selected cut follows staircase material. Any missing surface, old-cheek remnant or mismatch is a review failure; do not invent concealed pixels.','Original left main pier deliberately overlaid because candidate shortened its lower foot by about9-10 raw pixels. This may create a local contact notch and must be reviewed, not concealed.','Right original ground proxy is alpha-edge uncertain within original +/-2 source-pixel read budget; not fully transparent.','This compound has not passed native walking, depth, collision or final density acceptance.'],'reproduce':'python Project/art_source/earth_training_hall_local_assembly_review_v1/build_review.py','output_sha256':sha(HERE/'full-building-candidate-review.png')}
 (HERE/'partition-contract.json').write_text(json.dumps(report,indent=2)+'\n');assert sha(A/'earth_training_hall_candidate_v2/raw.png')==SHA;print(json.dumps({'review_size':list(base.size),'review_sha256':report['output_sha256'],'base_unchanged':True}))
if __name__=='__main__':main()
