"""Replay frozen raw registrations at4x texel density without changing logical geometry."""
from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
R=Path(__file__).resolve().parents[2];out=R/'assets/scifi/diagnostics/hero_hd4';out.mkdir(parents=True,exist_ok=True);diag=R/'diagnostics/hero/hd4';diag.mkdir(parents=True,exist_ok=True)
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();groups=[]
for name,v in [('se_idle','v1'),('se_walk','v3'),('e_idle','v1'),('e_walk','v1'),('s_idle','v1'),('s_walk','v1')]:
 p=R/f'art_source/hero_{name}_rebuild_v1';rp=p/f'{v}-registration.json';d=json.loads(rp.read_text());rawp=p/f'raw-{v}.png';assert H(rawp)==d['raw_sha256'];raw=Image.open(rawp).convert('RGBA');n=len(d['records']);atlas=Image.new('RGBA',(512*n,512));oldreplay=Image.new('RGBA',(128*n,128));rebuild=Image.new('RGBA',raw.size);records=[];scale=d['common_uniform_scale']
 for i,r in enumerate(d['records']):
  if 'raw_rectangle' in r: box=r['raw_rectangle']
  elif 'raw_cell_boundaries' in d:
   xs=d['raw_cell_boundaries']['x'];ys=d['raw_cell_boundaries']['y'];col=i%3;row=i//3;box=[xs[col],ys[row],xs[col+1],ys[row+1]]
  elif 'raw_cell_x_edges' in d:
   xs=d['raw_cell_x_edges'];box=[xs[i],0,xs[i+1],raw.height]
  elif name=='se_idle':box=[543*i,0,543*(i+1),724]
  else:raise ValueError(name)
  cell=raw.crop(box);rebuild.paste(cell,box[:2]);tx,ty=r['translation']
  for density,target in [(1,oldreplay),(4,atlas)]:
   k=scale*density;frame=cell.transform((128*density,128*density),Image.Transform.AFFINE,(1/k,0,-tx/scale,0,1/k,-ty/scale),resample=Image.Resampling.BICUBIC);target.paste(frame,(i*128*density,0))
  records.append({'source_id':r['source_id'],'region_px':[i*512,0,512,512],'raw_rectangle':box,'logical_translation':[tx,ty],'texture_translation':[4*tx,4*ty]})
 assert rebuild.tobytes()==raw.tobytes()
 old=Image.open(p/f'{v}-registered-atlas-128.png').convert('RGBA');assert oldreplay.tobytes()==old.tobytes(),name+' existing registration replay mismatch'
 dest=out/(name+'_body.png');atlas.save(dest)
 entry={'name':name,'atlas':'res://'+str(dest.relative_to(R)),'sha256':H(dest),'raw':str(rawp.relative_to(R)),'raw_sha256':H(rawp),'registration':str(rp.relative_to(R)),'registration_sha256':H(rp),'logical_frame_size':[128,128],'texture_frame_size':[512,512],'texels_per_logical_pixel':4,'logical_root':[16,64],'texture_root':[64,256],'logical_draw_offset':[-16,-64],'sprite_scale':[.25,.25],'texture_offset_if_scaled_sprite':[-64,-256],'common_logical_scale':scale,'common_raw_to_texture_scale':4*scale,'frame_ticks':12 if 'idle' in name else 7,'records':records,'old128_replay_rgba_exact':True,'raw_rectangle_rebuild_rgba_exact':True}
 groups.append(entry)
 # Same apparent size at4x viewer zoom: left old128 interpolated; right directrawHD.
 oldframe=old.crop((0,0,128,128)).resize((512,512),Image.Resampling.BILINEAR);newframe=atlas.crop((0,0,512,512));board=Image.new('RGBA',(1024,544),(80,80,80,255));board.alpha_composite(oldframe,(0,32));board.alpha_composite(newframe,(512,32));dr=ImageDraw.Draw(board);dr.text((10,10),name+' old128 enlarged4x',fill='white');dr.text((522,10),'same logical frame, direct raw registration HD4',fill='white');board.convert('RGB').save(diag/(name+'-density-comparison.jpg'))
manifest={'schema':'hero-hd-density-diagnostic-v1','status':'pending_actual_HD_engine_review','method':'Replay identical frozen uniform scale + per-frame rigid translation directly from original generated RGBA. No new image generation, deformation, crop change or enlarged128 intermediate.','groups':groups,'shadow_contract':{'logical_receiver_y':86,'logical_cast':[148/279,-111/279],'texture_receiver_y_if_projecting_in_texture_units':344,'texture_blur_for_logical_0_9':3.6,'note':'Prefer retain ground projection geometry in logical128 units and sample512 texture UV. If using texture units multiply ALL positions/heights/root/blur by4 then scale drawing0.25. Never feed512 height into logical128 projection unchanged.'},'scope':'E/SE/S approved idle+walk only. Density preserves character world/screen footprint; visual improvement must be tested at real HD viewport, not by scaling character geometry.'}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('PASS',[(g['name'],g['sha256']) for g in groups])
