"""Frozen-reference v2 QA. Does not register, warp, crop or alter either raw asset."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw

HERE=Path(__file__).resolve().parent
PLAN=HERE.parent/'earth_training_hall_edit_plan_v1'
SRC=HERE.parent/'earth_training_hall_source_v1'
V1=HERE.parent/'earth_training_hall_candidate_v1'
SHA='5dc43ba8c8f2b5c23832aa5e3178cde41546e5077dfb96ae7c5163d73e851d75'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
 assert sha(HERE/'raw.png')==SHA
 p=json.loads((PLAN/'edit-plan.json').read_text());d=p['reference']['density'];t=np.array(p['reference']['raw_translation'])
 raw=Image.open(HERE/'raw.png').convert('RGBA');old=Image.open(V1/'raw.png').convert('RGBA');src=Image.open(SRC/'source-full.png').convert('RGBA')
 gray=Image.new('RGBA',raw.size,(90,100,105,255));gray.alpha_composite(raw)
 sb=Image.new('RGBA',src.size,(90,100,105,255));sb.alpha_composite(src)
 points={'S0':([377,925],10),'S1':([353,744],8),'S2':([1105,1020],8),'S3':([1145,848],8),'P0':([796,1045],8)}
 measured=[]
 for q in p['targets']:
  xy,unc=points[q['id']];target=np.array(q['target_raw_xy']);delta=np.array(xy)-target
  measured.append({'id':q['id'],'v2_raw_xy':xy,'raw_read_uncertainty_px':unc,'fixed_target_raw_xy':target.tolist(),'raw_error_xy':delta.tolist(),'source_error_xy':(delta/d).tolist(),'source_error_distance':float(np.linalg.norm(delta)/d),'conservative_raw_read_budget':q['source_read_uncertainty_px']*d+unc,'within_conservative_budget':bool(np.linalg.norm(delta)<=q['source_read_uncertainty_px']*d+unc)})
 # One clearly failed original stair sample remains on the cheek, not supported material.
 rows=[];sheet=Image.new('RGB',(600,12*126),(65,75,80));sd=ImageDraw.Draw(sheet)
 for i,r in enumerate(p['support_owner_rows']):
  x,y=r['cell'];base=np.array([x*48-2948,y*32-642]);box=[*(base+[-6,2]),*(base+[48,37])];rbox=[*(d*np.array(box[:2])+t),*(d*np.array(box[2:])+t)]
  for off,im,b in [(90,sb,box),(350,gray,[round(v)for v in rbox])]:sheet.paste(im.crop(tuple(b)).resize((194,100),Image.Resampling.NEAREST).convert('RGB'),(off,i*126+24))
  sd.text((3,i*126+3),f'cell {x},{y}',fill='white');sd.text((190,i*126+3),'SOURCE',fill='white');sd.text((350,i*126+3),'V2 SAME FIXED REFERENCE',fill='white')
  rr={'owner':r['owner'],'cell':r['cell'],'source_flag':r['source_flag'],'samples':[]}
  for q in r['samples']:
   sq=q['source_canvas_xy'];rq=q['candidate_raw_xy'];ix,iy=map(round,rq);alpha=raw.getpixel((ix,iy))[3] if 0<=ix<raw.width and 0<=iy<raw.height else 0
   foot=q['phase17_foot_index'];orig=q['source_material_read']
   new='support_tread_or_landing' if q['must_restore_support'] else 'transparent_ground'
   if (x,y)==(66,36)and foot==1:new='solid_side_cheek_not_tread'
   if (x,y)==(74,37)and foot==1:new='new_lowest_tread_or_front_lip_over_source_grass'
   if orig=='uncertain_cheek_edge':new='candidate_tread_at_uncertain_source_edge'
   rr['samples'].append({**q,'v2_candidate_alpha':alpha,'v2_material_read':new})
   color='orange'if new in ['solid_side_cheek_not_tread','new_lowest_tread_or_front_lip_over_source_grass']else'cyan'if q['must_restore_support']else'yellow'
   px=(sq[0]-box[0])/54*194;py=(sq[1]-box[1])/35*100
   for off in [90,350]:sd.ellipse((off+px-3,i*126+24+py-3,off+px+3,i*126+24+py+3),outline=color,width=2)
  rows.append(rr)
 sheet.save(HERE/'fixed-reference-support-feet.png')
 marked=gray.convert('RGB');md=ImageDraw.Draw(marked);md.text((10,10),'V2 FIXED REFERENCE ONLY: cyan=actual, magenta=original target; NO REFIT',fill='white')
 for q in measured:
  x,y=q['v2_raw_xy'];u,v=q['fixed_target_raw_xy'];md.ellipse((x-5,y-5,x+5,y+5),outline='cyan',width=2);md.line((x,y,u,v),fill='magenta',width=2);md.line((u-6,v,u+6,v),fill='magenta',width=2);md.line((u,v-6,u,v+6),fill='magenta',width=2);md.text((x+9,y-8),q['id'],fill='white')
 marked.save(HERE/'fixed-reference-points.png')
 # Raw v1 is padded by one transparent row only for same-origin comparison; never rescaled.
 old_pad=Image.new('RGBA',raw.size);old_pad.alpha_composite(old,(0,0));a=np.array(old_pad).astype(np.int16);b=np.array(raw).astype(np.int16)
 roi=np.zeros((raw.height,raw.width),bool)
 for g in p['stair_boundary_guides'].values():
  x0,y0,x1,y1=g['edit_roi_raw_xyxy'];roi[y0:y1,x0:x1]=True
 both=(a[:,:,3]>128)&(b[:,:,3]>128)&~roi
 mae=np.abs(a[:,:,:3]-b[:,:,:3]).mean(2);sil1=a[:,:,3]>128;sil2=b[:,:,3]>128
 nonroi={'v1_comparison_padding':'one transparent bottom row to match v2 height; origin unchanged, no rescaling or image output modification','opaque_overlap_pixels_outside_edit_regions':int(both.sum()),'mean_absolute_rgb_difference_on_overlap':float(mae[both].mean()),'fraction_mean_rgb_difference_gt12':float((mae[both]>12).mean()),'visible_silhouette_xor_pixels_outside_edit_regions':int(((sil1^sil2)&~roi).sum()),'interpretation':'Non-target areas were re-rendered. Pixel differences alone are not a new geometric calibration; manual roof/canopy comparison is required. Do not claim unchanged bytes or repair with a new fit.'}
 # This pair is only review evidence: full images at their actual pixel dimensions.
 pair=Image.new('RGB',(raw.width*2,raw.height+30),(90,100,105));og=Image.new('RGBA',raw.size,(90,100,105,255));og.alpha_composite(old,(0,0));pair.paste(og.convert('RGB'),(0,30));pair.paste(gray.convert('RGB'),(raw.width,30));pd=ImageDraw.Draw(pair);pd.text((10,8),'V1 ACTUAL PIXELS',fill='white');pd.text((raw.width+10,8),'V2 ACTUAL PIXELS; same origin, no resize',fill='white');pair.save(HERE/'v1-v2-native-review.jpg',quality=95)
 alpha=np.asarray(raw)[:,:,3];positive=alpha[alpha>0];boxes={}
 for threshold in [0,8,128,240]:
  yy,xx=np.where(alpha>threshold);boxes[str(threshold)]=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
 report={'status':'V2 still fails local support geometry; not approved for partition/runtime. No refit, warp or pixel edits.','raw_sha256':SHA,'actual_size':list(raw.size),'v1_size':list(old.size),'size_change':[raw.width-old.width,raw.height-old.height],'fixed_reference_unchanged':p['reference'],'measured_points':measured,'source_owner_foot_rows':rows,'improved':['Source (65,35) clear supporting second toe now lands on actual tread rather than transparency.','Source (66,36) first toe now lands on actual tread rather than near-transparent pixels.'],'remaining_failures':['Source (66,36) second toe at raw(395.74,914.75) still lies on the raised right side cheek, not source-equivalent tread.','S0 lower/front right stair extent remains too far left in the unchanged reference, so the left staircase is still too narrow at the critical edge.','S3 right upper junction remains about 13.5 logical pixels from its original target; the requested right/up correction was not achieved.','Source (74,37) second toe at raw(1188.92,980.85), originally grass/apron and transparent in v1, now has alpha249 on the new lowest tread/front lip. Right flight intrudes into source ground.'],'visible_boundary_readings':{'left_v2_raw':[[353,744],[484,817],[383,929],[249,847]],'right_v2_raw':[[1018,916],[1145,848],[1243,950],[1105,1032]],'boundary_uncertainty_raw_px':8,'note':'Approximate full visible support/tread plus narrow front-lip extent, not an exact segmentation polygon. Point samples can lie inside these material boundaries.'},'non_target_region_change':nonroi,'alpha':{'zero':int((alpha==0).sum()),'positive':int((alpha>0).sum()),'common_positive_values':Counter(positive.tolist()).most_common(6),'threshold_bboxes':boxes,'note':'Genuine transparent background, no visible separate external cast or marker residue; low-alpha colored fringe retained. Raw untouched.'},'density':'No valid source registration exists; cannot certify effective >=2 texels/logical unit. No resizing/upscaling performed. Height increased by one pixel rather than requested exact canvas.','next_step':'No third whole-building edit. Prepare stricter local staircase crops/source material and allowed-support/ground constraints; await approval.','reproduce':'python Project/art_source/earth_training_hall_candidate_v2/measure_fixed_reference.py'}
 (HERE/'measurements.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');assert sha(HERE/'raw.png')==SHA
 print(json.dumps({'point_errors':{q['id']:q['source_error_distance']for q in measured},'non_target_region_change':nonroi,'raw_unchanged':True,'support_gate':'FAIL'}))


if __name__=='__main__':main()
