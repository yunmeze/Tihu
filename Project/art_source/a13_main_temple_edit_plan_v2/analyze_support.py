from pathlib import Path
from collections import deque
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent;D=P/'diagnostics/art_source/a13-main-temple';m=json.loads((P/'data/maps/A13.json').read_text());contract=json.loads((P/'art_source/a13_main_temple_source/source-group-contract.json').read_text());g=json.loads((P/'art_source/a13_main_temple_candidate_v1/geometry-diagnostic.json').read_text())
def can(x,y):return 0<=x<m['width']and 0<=y<m['height']and m['cells'][x*m['height']+y][1]not in [-1,-2,-3]
def path(target):
 start=(61,39);q=deque([start]);parent={start:None}
 while q:
  p=q.popleft()
  if p==target:
   out=[]
   while p is not None:out.append(list(p));p=parent[p]
   return out[::-1]
  for dx,dy in [(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1)]:
   n=(p[0]+dx,p[1]+dy)
   if n in parent or not can(*n):continue
   if dx and dy and(not can(p[0]+dx,p[1])or not can(p[0],p[1]+dy)):continue
   parent[n]=p;q.append(n)
 return None
support=[o for o in contract['owners_in_draw_order']if o['layer']==0];rows=[]
for o in support:
 x,y=o['cell'];rows.append({'cell':[x,y],'frame':o['frame_index'],'original_flag':o['flag'],'layer':0,'sort_y':y,'world_cell_rect':[x*48,y*32,48,32],'source_draw_rect':o['world_rect'],'static_flag_route':path((x,y)),'native_walk_validation':False})
# An annotated source-grid diagram, not a generated texture or a gameplay edit.
a=Image.open(D/'source-composite.png').convert('RGBA');bg=Image.new('RGBA',a.size,(100,110,100,255));bg.alpha_composite(a);draw=ImageDraw.Draw(bg)
for r in rows:
 x,y,w,h=r['world_cell_rect'];x-=2948;y-=642;draw.rectangle((x,y,x+w-1,y+h-1),outline='cyan',width=1);draw.text((x+2,y+2),','.join(map(str,r['cell'])),fill='white')
bg.convert('RGB').save(D/'edit-plan-source-walkable-grid.jpg')
pts={v['id'].split('_')[0]:v for v in g['points']}
def vector(a,b,key):return [pts[b][key][i]-pts[a][key][i]for i in range(2)]
report={'status':'read_only_pre_edit_analysis','support_owner_count':len(rows),'all_12_flag_cells_statically_reachable':all(r['static_flag_route']for r in rows),'support_owners':rows,'measurement_basis':'Existing uncertain manual points, no newly asserted exact support polygon. Grid origin is not a measured anatomical hero foot.','left_stair_upper_to_lower':{'source_vector':vector('S1','S0','source_xy'),'candidate_mapped_vector':vector('S1','S0','mapped_source_xy')},'right_stair_upper_to_lower':{'source_vector':vector('S3','S2','source_xy'),'candidate_mapped_vector':vector('S3','S2','mapped_source_xy')},'diagnosis':['Central pillar nearly matches while left stair shifts left and left eave shifts right. A single global translation or single uniform scale cannot remove opposing residuals.','Left stair selected upper/lower vertical separation remains about88px after scale, so current readings support lateral arm/stair displacement more strongly than uniform stair-depth growth. Upper-tread correspondence remains uncertain.','New straight thick plinth replaces rounded stone masonry/landscaping profile; apparent mass increase is partly changed base geometry. No numerical base-height claim without separating masonry from original landscaping.','Right stair selected direction differs; do not correct by moving only the left stair and assuming other true faces are proven.'],'constraints':['Preserve all original flags/cells/NPC scripts and layer0 ownership semantics.','Preserve two doors, both outer ground-tread edges, both upper support junctions and pillar bases as separate constraints.','Do not treat grass/stone apron extent as target support width.','Do not use rail cheek caps as exact homologues of original tread corners.'],'proposed_gate':{'preferred_support_landmark_residual_source_px':5,'ambiguous_read_overlap':'Original ±4–5px and candidate mapped uncertainty must overlap for equivalent material features. Re-read junctions before computing acceptance fit.','hold_condition':'Any consistent support-edge displacement beyond8 source px, any reachable actor landing on a riser/rail/transparent void, or any changed door opening requires review; numeric gate alone never means native PASS.','eave_design_residual':'Can be documented separately if it does not move pillars/doors or affect intended occlusion; not used to force the supports to fit.'}}
sp=np.array([v['source_xy']for v in g['points'][:5]]);cp=np.array([v['candidate_xy']for v in g['points'][:5]]);ss=float(((cp-cp.mean(0))*(sp-sp.mean(0))).sum()/((cp-cp.mean(0))**2).sum());tt=sp.mean(0)-ss*cp.mean(0);ee=ss*cp+tt-sp
report['support_only_uniform_fit_diagnostic']={'scale':ss,'translation':tt.tolist(),'rms':float(np.sqrt((ee**2).sum(1).mean())),'errors':ee.tolist(),'applied_to_asset':False}
(HERE/'support-analysis.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:report[k]for k in ['all_12_flag_cells_statically_reachable','left_stair_upper_to_lower','right_stair_upper_to_lower']}))
