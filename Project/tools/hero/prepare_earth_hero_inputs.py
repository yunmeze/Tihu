"""Source-preserving preparation for the Earth visual baseline; no generation."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
R=Path(__file__).resolve().parents[2];p=R/'art_source/earth_hero_input_plan_v1';p.mkdir(exist_ok=True);diag=R/'diagnostics/hero/earth-identity-plan';diag.mkdir(parents=True,exist_ok=True);H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cp=R/'art_source/earth_base_style_concept_v1/concept.png';concept=Image.open(cp).convert('RGBA');rects={'concept-hero-local.png':[715,515,775,636],'concept-hero-light-context.png':[705,510,880,685]}
for name,rect in rects.items():concept.crop(rect).save(p/name)
parts={'head_unknown_detail':[733,519,760,546],'chest_black_underlayer':[728,540,761,577],'visible_red_shoulder':[721,541,739,560],'hip_thigh_material':[728,574,760,601],'shin_boot_material':[722,593,769,632]};board=Image.new('RGBA',(720,280));dr=ImageDraw.Draw(board)
for i,(name,rect) in enumerate(parts.items()):
 x=i*144;dr.text((x+2,5),name,fill='white');cut=concept.crop(rect);board.alpha_composite(cut.resize((cut.width*3,cut.height*3),Image.Resampling.NEAREST),(x+10,35))
board.save(p/'concept-disconnected-appearance-3x.png')
m=json.loads((R/'data/hero/movement.json').read_text());strip=Image.new('RGBA',(512,128));main=Image.new('RGBA',(256,88));records=[]
for i,fid in enumerate(range(13,17)):
 im=Image.new('RGBA',(128,128));rec={'source_id':fid,'layers':{}}
 for n in ['body','head']:
  l=m['layers'][n];f=l['frames'][str(fid)];a=Image.open(R/l['atlas'].removeprefix('res://')).convert('RGBA');x,y,w,h=f['rect'];t=a.crop((x,y,x+w,y+h));assert hashlib.sha256(t.tobytes()).hexdigest()==f['rgba_sha256'];ox,oy=f['offset'];im.alpha_composite(t,(16+ox,64+oy));rec['layers'][n]={k:f[k] for k in ['rect','offset','rgba_sha256']}
 im.save(p/f'source-{fid}.png');strip.paste(im,(128*i,0));main.paste(im.crop((12,8,76,96)),(64*i,0));rec['composite_rgba_sha256']=hashlib.sha256(im.tobytes()).hexdigest();records.append(rec)
 if fid==13:im.crop((12,8,76,96)).resize((512,704),Image.Resampling.NEAREST).save(p/'source13-pose-main-8x.png')
strip.save(p/'source13-16-native.png');main.resize((1536,528),Image.Resampling.NEAREST).save(p/'source13-16-pose-main-6x.png')
prov={'status':'prepared_only_pending_parent_generation_approval','concept':{'path':str(cp.relative_to(R)),'sha256':H(cp),'dimensions':list(concept.size),'full_direction_accepted':'2026-10-15 07:38UTC per parent; no isolated exact face specification implied'},'concept_local_crops':rects,'disconnected_appearance_rects':parts,'technical_enlargement':'Nearest only, no recovered/invented detail','source_manifest_sha256':H(R/'data/hero/movement.json'),'source_canvas':[128,128],'source_root':[16,64],'common_body_crop':[12,8,76,96],'source_records':records,'source_rgba_policy':'Original body then head including nonblack checker/colors preserved. No semantic deletion.','old_generated_body_inputs':[]}
(p/'INPUT_PROVENANCE.json').write_text(json.dumps(prov,indent=2)+'\n')
