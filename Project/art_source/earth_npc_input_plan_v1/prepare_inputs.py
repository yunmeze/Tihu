"""Source decoding and exact crop preparation only. No generation/runtime/GUI/Git."""
import sys,json,hashlib,itertools
from pathlib import Path
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[2]; R=P.parent; O=Path(__file__).parent; D=P/'diagnostics/earth-npc-input-plan-v1'
sys.path.insert(0,str(P/'tools'))
from lp_original import read_pack,decode_frame
from extract_a13_original import parse_map
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
old=json.loads((P/'art_source/a13_npc_source/source-contract.json').read_text())
mp=json.loads((P/'data/maps/A13.json').read_text());native=parse_map(R/'原版游戏/Data/Map/A13.lpMap')
assert native['npcs']==mp['npcs']
data,recs,anim,key=read_pack(R/'原版游戏/Data/Npc.lpRes')
contract={'status':'source_prepared_only; modern design boundary approved by parent 2026-10-15 09:13 UTC; no generation/runtime approval','sample_world_xywh':[2496,960,768,512],'source_clock':old['source_clock'],'registration':old['registration'],'render_contract':mp['render_contract'],'npcs':old['npcs'][:2],'frames':{},'groups':[],'design_approval':{'fangzhang':'Adult male close-combat coach, dark sleeveless functional training top; preserve bent staggered stance and crossed/front arm occlusion. New design from concept, not sex/age inferred from name.','lingyunzi':'Adult male mission instructor, gray-black sleeved short training jacket, trousers; remove tall crown/robe. Preserve visible head/torso/feet motion, not old crown top height. Four distinct phases remain.'}}
for slug,ids in [('fangzhang',list(range(261,265))),('lingyunzi',list(range(113,117)))]:
    folder=O/slug;folder.mkdir(exist_ok=True);strip=Image.new('RGBA',(512,160));registered=[]
    for j,i in enumerate(ids):
        im,meta=decode_frame(data,recs[i],'Npc',anim); assert meta['rgba_sha256']==old['frames'][str(i)]['rgba_sha256']
        im.save(folder/f'source-{i}.png'); off=meta['offset'];cell=Image.new('RGBA',(128,160));cell.paste(im,(32+off[0],104+off[1])); registered.append(cell);strip.paste(cell,(128*j,0))
        contract['frames'][str(i)]={**old['frames'][str(i)],'file':f'{slug}/source-{i}.png','file_sha256':sha(folder/f'source-{i}.png'),'fresh_native_decode_verified':True}
    strip.save(folder/'source-four-registered-native.png');strip.resize((2048,640),Image.Resampling.NEAREST).save(folder/'source-four-pose-4x.png')
    pairs=[]
    for a,b in itertools.combinations(range(4),2):
        pa=list(registered[a].getdata());pb=list(registered[b].getdata());pairs.append({'ids':[ids[a],ids[b]],'changed_rgba_pixels':sum(x!=y for x,y in zip(pa,pb)),'changed_visible_pixels':sum(x!=y and (x[3]>0 or y[3]>0) for x,y in zip(pa,pb))})
    contract['groups'].append({'slug':slug,'ids':ids,'unique_registered_rgba':len(set(im.tobytes() for im in registered)),'pairs':pairs,'phase_policy':'one static generated pose mapped to 4 unchanged IDs' if slug=='fangzhang' else 'one complete four-phase generation, one common transform; never four independent fits'})
    bg=Image.new('RGBA',strip.size,(90,96,100,255));bg.alpha_composite(strip);bg.resize((2048,640),Image.Resampling.NEAREST).save(D/f'{slug}-source-review-4x.png')
concept_path=P/'art_source/earth_base_style_concept_v1/concept.png';concept=Image.open(concept_path)
# Exact unretouched crops; full character crops for human review, disconnected material crops for model input.
crops={'concept-fangzhang-context.png':[902,433,1010,566],'concept-lingyunzi-context.png':[775,372,856,507], 'concept-fangzhang-head.png':[943,444,968,473],'concept-fangzhang-upper-material.png':[936,471,971,495],'concept-fangzhang-trouser-boot.png':[946,502,979,548], 'concept-lingyunzi-head.png':[797,382,825,408],'concept-lingyunzi-upper-material.png':[789,405,831,437],'concept-lingyunzi-trouser-boot.png':[792,450,833,495]}
for name,box in crops.items():concept.crop(box).save(O/name)
for slug in ['fangzhang','lingyunzi']:
    names=[f'concept-{slug}-head.png',f'concept-{slug}-upper-material.png',f'concept-{slug}-trouser-boot.png'];board=Image.new('RGB',(600,240),(70,75,80))
    for j,n in enumerate(names):
        im=Image.open(O/n);im=im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST);board.paste(im,(j*200+10,15))
    board.save(O/f'concept-{slug}-disconnected-local-4x.png')
hero_path=P/'assets/earth/hero/se_idle_v1/body.png';hero=Image.open(hero_path)
# Material only: no head, full pose, red shoulder insignia or complete hero identity.
hero_crops={'hero-black-cloth-material.png':[164,213,185,251],'hero-gray-plate-material.png':[149,126,177,153],'hero-boot-material.png':[130,310,155,336]}
for name,box in hero_crops.items():hero.crop(box).save(O/name)
provenance={'concept':{'path':str(concept_path.relative_to(P)),'sha256':sha(concept_path),'size':list(concept.size)},'concept_crops_xyxy':crops,'concept_enlargements':'Nearest 4x is viewing convenience, not new detail; source concept character detail limited. Context crops are HUMAN REVIEW only; generation receives disconnected local patches plus original pose sheet.','hero':{'path':str(hero_path.relative_to(P)),'sha256':sha(hero_path),'density':4,'crops_xyxy':hero_crops,'use':'material/scale only; no hero face, full body, emblem or identity transfer'},'input_hashes':{}}
paths=['data/maps/A13.json','assets/original/manifest.json','tools/lp_original.py','tools/extract_a13_original.py','scripts/world_view.gd','scripts/art/selected_npc_pair.gd','docs/EARTH_ART_BIBLE_V1.md','assets/earth/hero/se_idle_v1/manifest.json','assets/earth/hero/se_walk_v1/manifest.json','assets/earth/hero/se_walk_v1/body.png','art_source/a13_npc_source/source-contract.json']
for f in paths:provenance['input_hashes'][f]=sha(P/f)
for f in ['原版游戏/Data/Npc.lpRes','原版游戏/Data/Map/A13.lpMap']:provenance['input_hashes']['../'+f]=sha(R/f)
contract['contact_review']={'exact_anatomical_contact':'unresolved; source alpha includes baked checker, do not derive sole from bbox','fangzhang_source261_raw_boot_rois_xyxy':[[14,49,25,57],[29,59,40,67]],'fangzhang_roi_uncertainty_px':3,'lingyunzi_source113_raw_boot_rois_xyxy':[[4,64,11,72],[19,64,26,72]],'lingyunzi_roi_uncertainty_px':2,'old_candidate_feet':'(44,118),(61,130) are legacy generated-candidate proxies, NOT authoritative new anchors','light':'warm upper-left, future independent lower-right cast; no baked cast/contact ellipse','old_shadow_params_rejected':[148/279,-111/279]}
dump(O/'SOURCE_CONTRACT.json',contract);dump(O/'INPUT_PROVENANCE.json',provenance)
# Diagnostic review sheet of contexts only, do not use as pose input.
review=Image.new('RGB',(960,600),(64,70,75));dr=ImageDraw.Draw(review)
for j,slug in enumerate(['fangzhang','lingyunzi']):
    im=Image.open(O/f'concept-{slug}-context.png');im=im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST);review.paste(im,(20+j*480,40));dr.text((20+j*480,15),slug+' / approved concept crop only',fill='white')
review.save(D/'concept-two-identities-review.png')
dump(D/'decode-audit.json',{'native_map_npcs_equal_current':True,'fresh_native_8_frames_equal_existing_rgba':True,'writes':'only this art_source folder and diagnostics/earth-npc-input-plan-v1','source_inputs_sha256':provenance['input_hashes']})
print('Prepared 8 source frames, 2 full pose boards, exact concept/material crops. No new artwork.')
