"""Planning masks only. Never edits candidate RGBA or creates production alpha."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
O=Path(__file__).parent;P=O.parents[1];A=P/'art_source';V=A/'earth_bamboo_b_candidate_v2';D=P/'diagnostics/art_source/earth-bamboo-b-local-layers-plan-v1';D.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda name,v:(O/name).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
raw=Image.open(V/'raw.png').convert('RGBA');m=json.loads((V/'measurements.json').read_text());d=m['density'];t=np.array(m['raw_from_source_translation']);W,H=raw.size
# Conservative hand-traced screen-space corridors; hidden segments stay protected, not asserted recovered wood.
paths=[('outer_left',[(294,996),(298,850),(309,690),(324,530),(344,420)],22),('left_inner',[(355,1064),(358,900),(367,735),(377,565),(379,420),(369,310)],24),('left_front_A',[(453,1131),(449,960),(435,810),(423,650),(407,495),(390,385)],24),('left_front_B',[(504,1122),(506,950),(509,780),(517,610),(513,480)],24),('lowest_front',[(526,1185),(522,1010),(522,850),(528,690),(539,530)],26),('middle_back',[(589,1102),(589,920),(599,740),(608,560),(612,430)],24),('middle_high',[(645,1119),(642,935),(646,745),(648,570),(640,410),(625,285)],26),('right_middle',[(708,1041),(701,875),(696,720),(691,560)],24),('right_back_A',[(738,935),(736,770),(746,610),(750,440),(749,315)],22),('right_back_B',[(772,966),(768,800),(777,630),(790,470)],24),('right_front',[(837,997),(832,835),(834,680),(860,520),(884,420)],26),('outer_right',[(862,903),(875,750),(890,590),(921,425),(946,325)],24)]
protect=Image.new('L',raw.size);pd=ImageDraw.Draw(protect);pd.rectangle((0,900,W-1,H-1),fill=255)
for name,pts,width in paths:
 pd.line(pts,fill=255,width=width,joint='curve')
 for x,y in pts:pd.ellipse((x-width//2,y-width//2,x+width//2,y+width//2),fill=255)
for lm in m['landmarks']:
 x,y=lm['raw_xy'];pd.ellipse((x-20,y-20,x+20,y+20),fill=255)
protect.save(O/'fixed_guard_proposal.png')
# A conservative no-cut gate retains uncertain occluded junctions. It is NOT a leaf alpha mask.
uncertain=[{'id':'left_branch_crossing','rect':[330,400,450,575],'reason':'overlapping thin culms/side branches; opaque foliage hides connections'}, {'id':'central_overlap','rect':[475,430,700,900],'reason':'multiple culms intersect foliage, no clean rear wood plate'}, {'id':'right_crossing','rect':[725,400,870,660],'reason':'right-side branch junction and depth assignment unclear'}]
hold=Image.new('L',raw.size);hd=ImageDraw.Draw(hold)
for z in uncertain:hd.rectangle(z['rect'],fill=255)
hold.save(O/'no_cut_hold_proposal.png')
# Broad local working regions, deliberately not the source pixel silhouette.
regions=[{'id':'A_upper_crown','rect':[310,65,935,445],'source_goal':'central peak and upper lobes; bring meaningful top near source y0=>raw144, preserve upper culm/twig junctions','priority':1}, {'id':'B_left_outer_fans','rect':[150,220,500,905],'source_goal':'left outer fine branches and transparent bays; avoid main culm corridors','priority':2}, {'id':'C_right_outer_fans','rect':[695,220,1090,905],'source_goal':'reduce right envelope toward source x271=>raw1015; preserve right culm paths','priority':3}]
g=np.array(protect)>0;h=np.array(hold)>0;used=np.zeros_like(g)
for z in regions:
 mask=Image.new('L',raw.size);md=ImageDraw.Draw(mask);md.rectangle(z['rect'],fill=255);ar=np.array(mask)>0;ar &= ~g & ~h & ~used;used |= ar;Image.fromarray(ar.astype('uint8')*255).save(O/(z['id']+'-editable-proposal.png'));z['editable_pixels']=int(ar.sum());z['mask_sha256']=sha(O/(z['id']+'-editable-proposal.png'))
# Coarse source occupancy per16 logical px supports semantic transparency targets; no hard source silhouette mask.
src=np.array(Image.open(A/'earth_bamboo_b_input_plan_v1/reference/source-body-index52-excluded.png'))[:,:,3]>0;tiles=[]
for y in range(0,341,16):
 for x in range(0,271,16):
  sub=src[y:min(y+16,341),x:min(x+16,271)];tiles.append({'source_rect':[x,y,min(x+16,271),min(y+16,341)],'source_visible_fraction':round(float(sub.mean()),5),'raw_target_rect':[(d*x+t[0]),(d*y+t[1]),(d*min(x+16,271)+t[0]),(d*min(y+16,341)+t[1])]})
save('source_coarse_occupancy.json',{'block_logical_pixels':16,'purpose':'Review guide only. Leaf rendering must stay natural; never multiply source bitmap/occupancy into final alpha.','uncertainty':'source index52 exclusion has66 opposite-parity pixels; source is low-res and occupancy is not physical leaf count','tiles':tiles})
save('layer_plan.json',{'status':'unapproved analytical fixed-mask proposals only; no image generation or alpha edits','base_raw_sha256':sha(V/'raw.png'),'canvas':raw.size,'frozen_transform':{'density':d,'raw_from_source_translation':t.tolist()},'six_endpoints':m['landmarks'],'fixed_guard':{'file':'fixed_guard_proposal.png','meaning':'White forbids changes to existing RGBA, including transparent gaps; includes all bottomy>=900 and conservative hand-traced corridors','paths':[{'id':a,'points':b,'width':c}for a,b,c in paths],'uncertainty':'Manual corridors are conservative spatial guards, not proven semantic trunk segmentation. Review against native raw before edit.'},'no_cut_hold':{'file':'no_cut_hold_proposal.png','regions':uncertain,'meaning':'White forbids transparent erasure; hidden connectivity unresolved. Protected even if source coarse guide suggests a hole.'},'three_work_regions':regions,'outside_all_regions':'unchanged; no free global foliage thinning','layer_semantics':'three local edit regions, NOT already recovered physical front/back layers or runtime owners','minimum_progress_gate':'If fixed/hold regions prevent useful thinning, stop and request a local hidden-junction reconstruction plan; never silently relax protection.'})
# Reference review overlays are generated under diagnostics, never used as final art.
b=Image.new('RGBA',raw.size,(65,70,67,255));b.alpha_composite(raw);ov=Image.new('RGBA',raw.size);od=ImageDraw.Draw(ov)
for name,pts,width in paths:od.line(pts,fill=(0,220,255,130),width=width)
for z in uncertain:od.rectangle(z['rect'],outline=(255,50,50,255),width=3)
for z in regions:od.rectangle(z['rect'],outline=(255,220,30,255),width=3);od.text((z['rect'][0]+5,z['rect'][1]+5),z['id'],fill=(255,255,255,255))
b.alpha_composite(ov);b.convert('RGB').save(D/'proposed-guards-regions.png')
save('INPUT_SHA256.json',[{'path':str(p.relative_to(P)),'sha256':sha(p)}for p in [V/'raw.png',V/'measurements.json',A/'earth_bamboo_b_input_plan_v1/reference/source-body-index52-excluded.png',A/'earth_bamboo_b_input_plan_v1/source_contract.json']])
print('mask stats',[(z['id'],z['editable_pixels'])for z in regions])
