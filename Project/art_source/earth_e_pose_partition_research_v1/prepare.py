from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;A=P.parent;D=P.parents[1]/'diagnostics/earth_e_pose_partition_research_v1';D.mkdir(parents=True,exist_ok=True)
S=P.parents[1]/'diagnostics/earth_e_source_shadow_index_audit_v1'
rows=json.loads((A/'earth_hero_e_input_plan_v1/SOURCE_PHASE_ANALYSIS.json').read_text())['walk']
# Conservative human-read VISIBLE surface cores, not anatomy or hidden parts.
sleeves=[[(35,34),(38,35),(35,43),(33,49),(30,49),(32,43)],[(35,35),(39,35),(38,43),(37,50),(34,50),(34,43)],[(38,35),(41,36),(42,43),(43,50),(39,50),(37,43)],[(40,35),(43,36),(45,44),(47,51),(43,51),(40,43)],[(36,35),(39,35),(40,43),(41,50),(37,50),(36,43)],[(35,35),(38,35),(37,43),(37,50),(33,50),(34,43)]]
colors={0:(130,134,142),1:(80,180,235),2:(230,120,195),3:(100,195,130),4:(245,175,65),5:(215,215,205)}
boards={name:Image.new('RGBA',(1536,1024)) for name in ['silhouette','surface-core','source-index18-excluded']}
proof=[]
for i,row in enumerate(rows):
 n=45+i;path=S/f'{n}-index18-excluded-NOT-SEMANTICALLY-CERTIFIED.png';im=Image.open(path).convert('RGBA');a=np.array(im);alpha=a[:,:,3];on=alpha>0
 labels=np.zeros((128,128),np.uint8);unc=np.zeros((128,128),bool)
 masks={}
 def poly(points):
  m=Image.new('L',(128,128));ImageDraw.Draw(m).polygon(points,fill=255);return np.array(m)>0
 def rect(box):
  m=Image.new('L',(128,128));ImageDraw.Draw(m).rectangle(box,fill=255);return np.array(m)>0
 masks[1]=poly(sleeves[i])
 h=row['visible_hand_surface_proxies'][0];masks[2]=rect([h[0]-2,h[1]-2,h[0]+2,h[1]+2])
 # Only visibly central upper trouser area. Knees/shins/occlusion remain unknown.
 masks[3]=rect([35,59,44,63])
 masks[4]=np.zeros((128,128),bool)
 toe_boxes=[]
 for key in ['screen_left_boot_chain','screen_right_boot_chain']:
  t=row['visible_lower_chains'][key]['boot_tip'];box=[t[0]-5,t[1]-4,t[0]+2,t[1]+2];toe_boxes.append(box);masks[4]|=rect(box)
 # Recognizable head core; no inference of hidden head/neck shape.
 masks[5]=rect([37,18,42,24])
 overlap=np.zeros((128,128),np.uint8)
 for code,m in masks.items():overlap+=m.astype(np.uint8);labels[m&on]=code
 labels[overlap>1]=0
 # 1px boundary of each proposed region is explicitly uncertain, while true outer alpha stays exact.
 for code,m in masks.items():
  inner=np.array(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.MinFilter(3)))>0
  unc|=(m&~inner&on)
 unc|=(labels==0)&on
 flat=np.zeros_like(a);flat[:,:,:3]=(208,214,220);flat[:,:,3]=alpha
 region=np.zeros_like(a);region[:,:,3]=alpha
 for code,c in colors.items():region[labels==code,:3]=c
 # Unknown and uncertain region boundary shown gray; no fabricated surface split.
 region[unc,:3]=(130,134,142)
 assert np.array_equal(flat[:,:,3],alpha) and np.array_equal(region[:,:,3],alpha)
 Image.fromarray(flat).save(D/f'{n}-exact-alpha-silhouette.png');Image.fromarray(region).save(D/f'{n}-visible-core-partition.png')
 for name,tile in [('silhouette',Image.fromarray(flat)),('surface-core',Image.fromarray(region)),('source-index18-excluded',im)]:
  boards[name].paste(tile.resize((512,512),Image.Resampling.NEAREST),(i%3*512,i//3*512))
 proof.append({'frame':n,'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'full128_root':[16,64],'alpha_unchanged':True,'opaque_support_xor_pixels':0,'sleeve_core_proposal':sleeves[i],'hand_region':[h[0]-2,h[1]-2,h[0]+2,h[1]+2],'trouser_core_box':[35,59,44,63],'toe_surface_boxes':toe_boxes,'uncertainty_pixels':int(unc.sum()),'class_pixel_counts':{str(code):int(((labels==code)&~unc&on).sum()) for code in colors},'no_hidden_geometry':True})
for name,b in boards.items():
 b.save(D/f'{name}-full128-sixphase-4x.png')
 gray=Image.new('RGBA',b.size,(35,39,44,255));gray.alpha_composite(b);gray.save(D/f'{name}-full128-sixphase-4x-gray.png')
# Review board: source/silhouette/partitions align exactly in each column, all full128 at4x.
review=Image.new('RGBA',(1536,3*1024+120),(45,49,53,255))
for i,name in enumerate(['source-index18-excluded','silhouette','surface-core']):review.alpha_composite(boards[name],(0,i*1024))
dr=ImageDraw.Draw(review);dr.text((12,3080),'All rows:45/46/47 then48/49/50. SAME full128 cells, nearest4x, root(64,256).',fill='white');dr.text((12,3105),'Blue sleeve core; pink hand core; green trousers core; gold boot/toe surface core; ivory head.',fill='white');dr.text((12,3130),'Gray=UNKNOWN/uncertain boundary. NO bones, joints, hidden limbs or generated final art.',fill='white')
review.save(D/'source-silhouette-surface-review.png')
(P/'COORDINATE_PROOF.json').write_text(json.dumps({'status':'analysis_only_not_final_art_not_generation_input_approval','semantic_limit':'index18 shadow role strongly inferred, not native renderer certified','grid':{'cell_logical':[128,128],'cell_display':[512,512],'layout':[3,2],'scale':4,'root':[16,64],'transform':'q=4*p+[512*(i%3),512*(i//3)]'},'regions':'human-read conservative visible cores; gray includes source boundary uncertainty, unclassified torso, knees, shins, overlapping surfaces; no artificial outer boundaries','records':proof},indent=2)+'\n')
print('six exact alpha checks passed')
