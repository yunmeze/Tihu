from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;A=P.parent;D=P.parents[1]/'diagnostics'/P.name;D.mkdir(parents=True,exist_ok=True)
S=D.parent/'earth_s_source_shadow_index_audit_v1'
rows=json.loads((A/'earth_hero_s_input_plan_v1/SOURCE_PHASE_ANALYSIS.json').read_text())['walk']
colors={0:(130,134,142),1:(80,180,235),2:(230,120,195),3:(100,195,130),4:(245,175,65)}
boards={k:Image.new('RGBA',(1536,1024)) for k in ['original-full-source','source-index18-excluded','silhouette','surface-core']};proof=[]
for i,row in enumerate(rows):
 n=row['source_id'];path=S/f'{n}-index18-excluded-NOT-SEMANTICALLY-CERTIFIED.png';im=Image.open(path).convert('RGBA');a=np.array(im);alpha=a[:,:,3];on=alpha>0
 def shape(points,rectangle=False):
  m=Image.new('L',(128,128));d=ImageDraw.Draw(m)
  if rectangle:d.rectangle(points,fill=255)
  else:d.polygon(points,fill=255)
  return np.array(m)>0
 masks={k:np.zeros((128,128),bool) for k in range(1,5)};regions={}
 for side in ['L','R']:
  h=row['hands'][side];cx,cy=h['cuff_proxy_xy']
  # Visible sleeve tube proposal, shoulder-to-cuff, excluding torso. No elbow/joint inferred.
  shoulder=30 if side=='L' else 49
  poly=[(shoulder-2,29),(shoulder+2,29),(cx+2,cy-2),(cx-2,cy-2)]
  masks[1]|=shape(poly);regions[f'{side}_sleeve_proposal']=poly
  box=h['skin_patch_inclusive_bbox_xyxy'];masks[2]|=shape(box,True);regions[f'{side}_hand_proposal']=box
  leg=row['legs'][side];chain={p['id']:p['xy'] for p in leg['visible_material_chain']};x,y=chain['P'];c=chain['C']
  # Tiny visibly upper trouser core, above material transition, not hip or knee.
  box=[x-1,max(57,y-3),x+2,min(y+1,c[1]-2)]
  if box[3]>=box[1]:masks[3]|=shape(box,True)
  regions[f'{side}_trouser_proposal']=box
  # Distal visible boot patch only, no extension toward hidden shaft.
  b=leg['boot_region_inclusive_bbox_xyxy'];t=chain['T'];box=[b[0],max(b[1],t[1]-4),b[2],b[3]]
  masks[4]|=shape(box,True);regions[f'{side}_distal_boot_proposal']=box
 labels=np.zeros((128,128),np.uint8);overlap=sum(m.astype(np.uint8) for m in masks.values());support_inner=np.array(Image.fromarray(alpha).filter(ImageFilter.MinFilter(3)))>0
 for code,m in masks.items():
  inner=np.array(Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)))>0
  labels[inner&on&support_inner&(overlap==1)]=code
 flat=np.zeros_like(a);flat[:,:,:3]=(208,214,220);flat[:,:,3]=alpha
 region=np.zeros_like(a);region[:,:,3]=alpha
 for code,color in colors.items():region[labels==code,:3]=color
 assert np.array_equal(region[:,:,3],alpha) and np.array_equal(flat[:,:,3],alpha)
 Image.fromarray(flat).save(D/f'{n}-exact-alpha-silhouette.png');Image.fromarray(region).save(D/f'{n}-visible-core-partition.png')
 originals=Image.open(S/f'{n}-full128-evidence.png').convert('RGBA')
 for k,tile in [('original-full-source',originals),('source-index18-excluded',im),('silhouette',Image.fromarray(flat)),('surface-core',Image.fromarray(region))]:boards[k].paste(tile.resize((512,512),Image.Resampling.NEAREST),(i%3*512,i//3*512))
 proof.append({'frame':n,'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'regions':regions,'alpha_byte_exact':True,'support_xor_pixels':0,'core_pixel_counts':{str(k):int(((labels==k)&on).sum()) for k in colors},'hidden_geometry_added':False})
for k,b in boards.items():
 b.save(D/f'{k}-full128-sixphase-4x.png');gray=Image.new('RGBA',b.size,(35,39,44,255));gray.alpha_composite(b);gray.save(D/f'{k}-full128-sixphase-4x-gray.png')
review=Image.new('RGBA',(1536,4096),(35,39,44,255))
for i,b in enumerate(boards.values()):review.alpha_composite(b,(0,i*1024))
review.save(D/'source-silhouette-surface-review.png')
(P/'COORDINATE_PROOF.json').write_text(json.dumps({'status':'research_only_no_generation','grid':{'cell_logical':[128,128],'layout':[3,2],'source_order':[57,58,59,60,61,62],'root':[16,64],'display_scale':4,'transform':'q=4*p+[512*(i%3),512*(i//3)]'},'legend':{'blue':'visible sleeve core','pink':'visible hand skin core','green':'visible trouser core','gold':'visible distal boot core','gray':'unknown or uncertain; all torso/head/joints unclassified'},'semantic_limit':'index18 inferred checker shadow, not native renderer certified; shapes retain clothing exterior, not anatomical body','records':proof},indent=2)+'\n')
print('6 exact alpha/support checks passed')
