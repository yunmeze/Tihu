from pathlib import Path
import hashlib,json
from PIL import Image,ImageDraw
import numpy as np
O=Path(__file__).parent;P=O.parents[1];D=P/'art_source';R=D/'earth_south_ground_candidate_v1/raw.png';S=D/'earth_south_ground_input_plan_v1/source_floor_layout_native.png';V=D/'earth_south_ground_input_plan_v1/approved_overlap_2x.png'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=Image.open(R).convert('RGB');s=Image.open(S).convert('RGB').resize(r.size,Image.Resampling.NEAREST)
# Manually inspected thin-feature/curb-center proxies, not collision/navigation geometry.
points=[{'x':208,'source_y':558,'candidate_inner_y':588,'candidate_outer_y':612},{'x':400,'source_y':430,'candidate_inner_y':448,'candidate_outer_y':470},{'x':600,'source_y':298,'candidate_inner_y':309,'candidate_outer_y':332},{'x':800,'source_y':166,'candidate_inner_y':166,'candidate_outer_y':188},{'x':900,'source_y':102,'candidate_inner_y':96,'candidate_outer_y':120}]
for q in points:q.update(candidate_center_y=(q['candidate_inner_y']+q['candidate_outer_y'])/2,source_uncertainty_raw=6,candidate_edge_uncertainty_raw=4)
for q in points:q['delta_center_y']=q['candidate_center_y']-q['source_y']
# Canonical intended straight diagonal from source slope 2:3, approximate center intercept 698.
# No spline, bend or joining to the erroneous candidate diagonal.
sp=[(855,128),(88,638),(80,770),(0,824)];cp=[(872,128),(102,674),(94,774),(0,842)]
m=Image.new('L',r.size);d=ImageDraw.Draw(m);d.polygon(sp+cp[::-1],fill=255);d.line(sp,fill=255,width=32,joint='curve');d.line(cp,fill=255,width=40,joint='curve');d.rectangle((72,704,128,756),fill=255)
a=np.array(m);a[:128,192:]=0;m=Image.fromarray(a);m.save(O/'A2_PROPOSED_complete_strip_mask.png')
band=Image.new('L',r.size);ImageDraw.Draw(band).line(sp,fill=255,width=13,joint='curve');band.save(O/'A2_source_uncertainty_band.png')
f=np.zeros(a.shape,bool);f[:128,192:]=True
assert not np.any((a>0)&f)
over=r.copy();over.paste(Image.new('RGB',r.size,(240,35,160)),(0,0),m.point(lambda v:80 if v else 0));d=ImageDraw.Draw(over);d.rectangle((192,0,1535,127),outline='yellow',width=2);d.line(sp,fill='cyan',width=2);d.line(cp,fill='red',width=2);over.save(O/'A2_SCOPE_ONLY_not_art.png')
for name,im in [('source',s),('candidate',r)]:
 c=im.copy();dr=ImageDraw.Draw(c)
 for q in points:
  x=q['x'];y=q['source_y'] if name=='source' else q['candidate_center_y'];dr.ellipse((x-5,y-5,x+5,y+5),outline='red',width=2);dr.text((x+8,y),str((x,y)),fill='red')
 c.save(O/(name+'_five_anchors_NOT_ART.png'))
x=np.array([q['x'] for q in points]);fits={key:np.polyfit(x,[q[key] for q in points],1).tolist() for key in ['source_y','candidate_center_y']}
res={'status':'PROPOSAL ONLY; blocked at frozen interface; no generation or final RGB assembly','coordinate_contract':'raw1536x1024; world=(2400,1408)+raw/2; boxes half-open','inputs':[{'path':str(p.relative_to(P)),'sha256':h(p)} for p in [R,S,V]],'five_read_points':points,'least_squares_y_equals_mx_plus_b':fits,'limits':'Manual source proxy +/-6raw, candidate edge +/-4raw. Different material widths mean centers are not identical physical semantics. Fits describe visible trend, not replacement geometry.','interpretation':'Continuous diagonal orientation drift plus visibly widened curb, and displaced upper kink. Not constant parallel translation, not an isolated corner defect.','source_intended_diagonal':'approx y=698-(2/3)x; use source uncertainty band, never fit replacement to erroneous candidate','proposed_strip':{'file':'A2_PROPOSED_complete_strip_mask.png','source_control_polyline_raw':sp,'candidate_cover_polyline_raw':cp,'bbox_raw':list(m.getbbox()),'pixels':int((a>0).sum()),'source_line_width_raw':32,'candidate_cover_line_width_raw':40,'purpose':'Smallest conservative complete ribbon under declared margins: source/candidate gap plus their curb material and 8raw neighborhood, tuft included. Not globally optimized pixel segmentation.','old7_mask_pixels':int(((a>0)&f).sum()),'row128_allowed_x_halfopen':[int(np.where(a[128]>0)[0].min()),int(np.where(a[128]>0)[0].max()+1)],'assembly':'Only after scope approval: fixed binary mask and generated patch texels; everything else candidate-v1 exactly; old7 final layer remains original assets.'},'frozen_interface':{'raw_y':128,'source_center_x_range':[852,870],'old_v4_inner_edge_x_range':[866,874],'old_v4_outer_edge_x_range':[898,906],'old_v4_center_x_range':[882,890],'candidate_v1_inner_edge_x_range':[852,860],'candidate_v1_outer_edge_x_range':[884,892],'result':'Compatibility unresolved. Different thin-source proxy / thick generated curb center definitions and finite uncertainty prohibit treating the initial horizontal gap as proven geometric error. See HISTORICAL_CROSSCHECK.json and await independent homologous-edge review.','decision_needed':'Review source feature meaning against old v4 INNER edge vs center; if inner-edge convention is accepted as source boundary, freeze that convention explicitly and measure continuation before generation. Otherwise stop A; relaxing old7 freeze requires separate approval and is not proposed here.'},'B':'v1 grass-only plan remains pending, unchanged; no B weights applied','fallback_material_plan':'Generate separate local grass/slab/curb material patches only after approval; construct fixed source-geometry coverage masks, assemble texels from explicit generated patch coordinates at2x without repeated tile, mirror, warp or scale. Does not solve frozen-interface incompatibility; geometry convention must be agreed first.'}
(O/'ANALYSIS.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(res['proposed_strip']));print(fits)
