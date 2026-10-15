from pathlib import Path
from PIL import Image,ImageDraw
O=Path(__file__).parent;D=O.parent
for n,path in [('source','earth_ground_plate_source_v1/source-floor-native.png'),('v4','earth_ground_plate_clean_regen_v4/raw.png')]:
 im=Image.open(D/path)
 if n=='source':im=im.resize((1536,1024),Image.Resampling.NEAREST)
 c=im.crop((976,736,1088,832)).resize((672,576),Image.Resampling.NEAREST);d=ImageDraw.Draw(c)
 for x in range(976,1088,8):
  xx=(x-976)*6;d.line((xx,0,xx,576),fill=(40,90,180));d.text((xx+1,1),str(x),fill='white')
 for y in range(736,832,8):
  yy=(y-736)*6;d.line((0,yy,672,yy),fill=(40,90,180));d.text((1,yy+1),str(y),fill='white')
 c.save(O/(n+'_upstream_read_NOT_ART.png'))
s=Image.open(D/'earth_south_ground_input_plan_v1/source_floor_layout_native.png').resize((1536,1024),Image.Resampling.NEAREST);r=Image.open(D/'earth_south_ground_candidate_v1/raw.png');out=Image.new('RGB',(1024,720))
for k,(y,cx) in enumerate([(256,680),(384,490),(512,304),(638,120),(704,90)]):
 for j,im in enumerate([s,r]):
  x=cx-64;c=im.crop((x,y-8,x+128,y+9)).resize((512,68),Image.Resampling.NEAREST);d=ImageDraw.Draw(c)
  for xx in range((x//8+1)*8,x+128,8):
   px=(xx-x)*4;d.line((px,0,px,68),fill=(40,90,180));d.text((px,0),str(xx),fill='white')
  d.line((0,32,512,32),fill='red');out.paste(c,(j*512,k*144+32));ImageDraw.Draw(out).text((j*512,k*144+8),f'{["source","candidate"][j]} south y{y}',fill='white')
out.save(O/'south_same_scanline_reads_NOT_ART.png')
