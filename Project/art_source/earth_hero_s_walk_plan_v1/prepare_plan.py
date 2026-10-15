from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil
P=Path(__file__).resolve().parent;R=P.parents[1];A=P.parent;S=A/'earth_hero_s_input_plan_v1';D=R/'diagnostics/earth_hero_s_walk_plan_v1';D.mkdir(parents=True,exist_ok=True)
sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
analysis=json.loads((S/'SOURCE_PHASE_ANALYSIS.json').read_text());prov=json.loads((S/'INPUT_PROVENANCE.json').read_text());full=Image.new('RGBA',(384,256));strip=Image.new('RGBA',(768,128));arm=Image.new('RGBA',(144,92));phases=[]
for i,f in enumerate(analysis['walk']):
 n=f['source_id'];p=S/f'source-{n}.png';im=Image.open(p).convert('RGBA');assert hashlib.sha256(im.tobytes()).hexdigest()==f['source_rgba_sha256'];full.paste(im,((i%3)*128,(i//3)*128));strip.paste(im,(i*128,0));arm.paste(im.crop((16,18,64,64)),((i%3)*48,(i//3)*46));phases.append({'source_id':n,'input_source_sha256':sha(p),'rgba_sha256':f['source_rgba_sha256'],'source_cell_origin':[128*(i%3),128*(i//3)],'duration_ticks':7,'visible_chains':f['legs'],'hands':f['hands'],'chest_surface_band_y':[32,39],'waist_clothing_band_y':[46,53],'band_uncertainty_px':3,'height_band_rule':'coarse source garment bands only, not new costume exact joints. Visible hands stay below chest region; alternate sleeve silhouette and cuff/hand regions, no raised fighting elbows.'})
full.save(P/'source-six-full-128-3x2-native.png');full.resize((1536,1024),Image.Resampling.NEAREST).save(P/'source-six-full-128-3x2-4x.png');strip.save(P/'source-six-full-128-strip-native.png')
# Diagnostic upper-body only; not a separate pose input that can override whole phases.
arm=arm.resize((1152,736),Image.Resampling.NEAREST);bg=Image.new('RGBA',arm.size,(64,68,72,255));bg.alpha_composite(arm);dr=ImageDraw.Draw(bg)
for i,f in enumerate(phases):
 x=(i%3)*384;y=(i//3)*368;dr.text((x+4,y+4),str(f['source_id'])+' visible garment, not joints',fill='white')
 for side,color in [('L','cyan'),('R','orange')]:
  rect=f['hands'][side]['skin_patch_inclusive_bbox_xyxy'];x0,y0,x1,y1=rect;dr.rectangle((x+(x0-16)*8,y+(y0-18)*8,x+(x1-16+1)*8,y+(y1-18+1)*8),outline=color,width=2)
  xx,yy=f['hands'][side]['cuff_proxy_xy'];dr.ellipse((x+(xx-16)*8-2,y+(yy-18)*8-2,x+(xx-16)*8+2,y+(yy-18)*8+2),fill=color)
 bg.save(D/'six-arm-garment-regions.png')
identity=A/'earth_hero_s_idle_edit_v1/raw-edit-v1.png';im=Image.open(identity).convert('RGBA');parts={'face_hair':(228,80,310,190),'short_chest_black_abdomen':(218,190,309,336),'red_shoulder':(162,160,216,216),'black_thigh_small_sideplate':(185,347,243,455),'glove':(137,330,180,392),'knee':(185,463,253,527),'boot':(181,563,248,641)}
b=Image.new('RGBA',(1260,220));dr=ImageDraw.Draw(b)
for i,(label,rect) in enumerate(parts.items()):b.alpha_composite(im.crop(rect),(i*180+20,45));dr.text((i*180+4,8),label,fill='white')
b.save(P/'approved-S17-edited-identity-parts.png')
dump(P/'PHASE_CONTRACT.json',{'status':'input_plan_only_do_not_generate_before_S_idle_native_pass_and_parent_approval','direction':'S','index':4,'ids':[57,58,59,60,61,62],'native_canvas':[128,128],'native_root':[16,64],'main_board_order':'3 columns,2 rows;57,58,59 /60,61,62','source_formula':'33+4*6+p','ticks':7,'cycle_ticks':42,'reference_hz':50,'reference_cycle_ms':840,'timing_boundary':'reference/current adapter only; no EXE clock/entry/speed proof','phases':phases,'loop62to57':analysis['walk_loop'],'uncertainty':'P/cuff3px; material boundaries1–2px; hand skin bbox2px. Hidden knees/ankles null; not support state.','identity_source':str(identity.relative_to(R)),'identity_sha256':sha(identity),'identity_crops':parts,'prohibited_identity':'old unedited S raw with long silver abdomen chain; old courtyard S; rejected E walk'})
deps=[identity,A/'earth_hero_s_idle_edit_v1/candidate/manifest.json',S/'SOURCE_PHASE_ANALYSIS.json',S/'INPUT_PROVENANCE.json',R/'data/hero/movement.json']+[S/f'source-{n}.png' for n in range(57,63)]
files=[p for p in sorted(P.iterdir()) if p.is_file() and p.name!='MINIMAL_SHA_MANIFEST.json'];dump(P/'MINIMAL_SHA_MANIFEST.json',{'purpose':'preparation only; no Git','files':[{'path':p.name,'sha256':sha(p)} for p in files],'read_only_dependencies':[{'path':str(p.relative_to(R.parent)),'sha256':sha(p)} for p in deps],'exclude':['Project/diagnostics/**','frozen previous packages'],'generation_allowed':False});print('Verified6 full original RGBA; built2 actual generation inputs and native boards; no frozen files changed.')
