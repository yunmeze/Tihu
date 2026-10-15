from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
O=Path(__file__).parent;D=O.parent
oldsrc=D/'earth_ground_plate_source_v1/source-floor-native.png';southsrc=D/'earth_south_ground_input_plan_v1/source_floor_layout_native.png';oldreview=D/'earth_ground_plate_clean_regen_v4/review.json'
a=Image.open(oldsrc).convert('RGB');b=Image.open(southsrc).convert('RGB');aa=np.array(a.crop((0,448,672,512)));bb=np.array(b.crop((96,0,768,64)));assert np.array_equal(aa,bb)
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=json.loads(oldreview.read_text());points=[]
for q in prior['source_layout']['samples']:
 p=q['source_center_raw'];v=q['v4_center_raw_approx'];points.append(dict(q,source_world=[2496+p[0]/2,960+p[1]/2],source_south_raw=[p[0]+192,p[1]-896],v4_south_raw=[v[0]+192,v[1]-896]))
r={'status':'CROSSCHECK ONLY; no art change','mapping':{'coordinate_type':'Continuous image edge coordinates used in manual readings; texel center adds0.5 before dividing by2. Never mix conventions for differences.','south_raw_to_world':'world=(2400,1408)+south_raw/2','old_v4_raw_to_world':'world=(2496,960)+old_raw/2','south_raw_to_old_v4_raw':'old_raw=south_raw+(-192,+896)','south_raw_to_south_source_native':'source_native=south_raw/2','south_raw_to_old_source_native':'old_source_native=(south_raw+(-192,+896))/2','interface':'south y128 => world y1472 => oldraw y1024 boundary. Last immutable old texel row1023 spans world1471.5..1472; new first row128 spans1472..1472.5. Compare one-sided extrapolated edges, not identical pixelrow.','south_overlap':'southraw[192,0,1536,128] corresponds oldraw[0,896,1344,1024]'},'overlap_source_byte_check':{'old_native_crop':[0,448,672,512],'south_native_crop':[96,0,768,64],'rgb_unequal_pixels':0},'historical_six_points_mapped':points,'historical_conclusion_limit':'3.041381 max logical distance applies only to those six manually recorded center landmarks, not every curb point or every edge. None is the new interface at world y1472. Last old-source landmark maps south(1064,0),128raw above interface (approximately192raw horizontal progression along slope-2/3); exact visual definition needs independent re-read.','current_definition_limit':'Current five source points are thin dark/light curb feature proxies; current candidate center is average of newly wider paving/curb and curb/grass transitions. They are not proven homologous. Original source is geometric authority. Do not equate old7 freeze with source accuracy.','preliminary_interface_correction':'24–30raw horizontal gap was a provisional different-width center comparison, NOT established12–15logical source-geometry error. Horizontal intercept displacement must be converted to perpendicular distance for straight-line comparison: dx*|m|/sqrt(1+m*m), then /2 logical, approximately0.277*dx for m=-2/3. Material-width and source-read uncertainty remain.','required_disposition':'Independent review must identify homologous source/v4 boundaries and re-read last historical point before calling old-v4 wrong. If confirmed wrong, explicitly reopen affected old region preserving v4; do not curve source line or secretly edit old pixels.','inputs':[{'path':str(p),'sha256':h(p)} for p in [oldsrc,southsrc,oldreview]]}
(O/'HISTORICAL_CROSSCHECK.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
s=b.resize((1536,1024),Image.Resampling.NEAREST);raw=Image.open(D/'earth_south_ground_candidate_v1/raw.png').convert('RGB');j=raw.copy();j.paste(Image.open(D/'earth_south_ground_input_plan_v1/approved_overlap_2x.png'),(192,0))
for n,im in [('source',s),('candidate',raw),('frozen_join',j)]:
 out=Image.new('RGB',(1000,480))
 for i,(x,y) in enumerate([(208,580),(400,450),(600,310),(800,180),(900,115)]):
  c=im.crop((x-32,y-56,x+32,y+64)).resize((192,360),Image.Resampling.NEAREST);d=ImageDraw.Draw(c)
  for yy in range(((y-56)//8+1)*8,y+64,8):
   py=(yy-y+56)*3;d.line((0,py,192,py),fill=(40,90,180));d.text((1,py),str(yy),fill='white')
  d.line((96,0,96,360),fill='red');out.paste(c,(i*200,24));ImageDraw.Draw(out).text((i*200,4),'x='+str(x),fill='white')
 out.save(O/(n+'_five_point_read.png'))
for n,im in [('source',s),('frozen',j)]:
 c=im.crop((816,80,944,176)).resize((768,576),Image.Resampling.NEAREST);d=ImageDraw.Draw(c)
 for x in range(816,944,8):
  xx=(x-816)*6;d.line((xx,0,xx,576),fill=(40,90,180));d.text((xx,0),str(x),fill='white')
 d.line((0,288,768,288),fill='red',width=2);c.save(O/(n+'_seam_read.png'))
