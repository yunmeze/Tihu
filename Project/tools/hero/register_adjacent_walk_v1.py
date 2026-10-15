"""Register complete generated strips with one group scale and per-frame rigid translation.
No body warps, frame substitution, rotation or per-frame scale. Read points are surface proxies.
"""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
R=Path(__file__).resolve().parents[2];names=['crown','neck_surface','sternum_clothing','pelvis_clothing','screen_left_boot','screen_right_boot'];w=np.array([1,.6,.4,.25,1,1.])
C={
'e':[[[203,52],[201,132],[224,192],[209,315],[128,467],[347,506]],[[201,52],[201,132],[224,192],[210,315],[142,465],[274,518]],[[217,52],[216,132],[244,194],[234,315],[242,521],[307,467]],[[207,44],[207,119],[237,180],[229,315],[131,512],[341,451]],[[202,44],[207,119],[237,180],[222,315],[155,505],[274,473]],[[225,47],[226,124],[250,183],[238,315],[208,480],[310,513]]],
's':[[[197,58],[196,155],[198,194],[198,315],[160,574],[226,439]],[[197,57],[197,154],[199,195],[198,315],[165,546],[236,441]],[[199,60],[199,156],[202,196],[204,315],[167,494],[240,558]],[[199,51],[199,146],[201,188],[201,315],[160,445],[239,564]],[[197,51],[198,146],[201,188],[201,315],[172,446],[247,544]],[[198,52],[198,147],[201,188],[201,315],[169,556],[244,499]]]}
S={
'e':[[[40,16],[42,27],[44,37],[42,54],[29,78],[60,81]],[[39,16],[41,27],[43,37],[41,54],[31,77],[48,87]],[[40,15],[42,26],[44,36],[42,53],[42,87],[51,78]],[[40,16],[42,27],[44,37],[42,54],[29,84],[60,74]],[[39,16],[41,27],[43,37],[41,54],[31,83],[48,77]],[[40,15],[42,26],[44,36],[42,53],[41,80],[51,86]]],
's':[[[40,16],[40,28],[40,37],[40,54],[35,91],[45,73]],[[41,15],[41,27],[41,36],[41,53],[35,88],[46,73]],[[41,15],[41,27],[41,36],[41,53],[35,83],[46,88]],[[41,16],[41,28],[41,37],[41,54],[35,73],[46,91]],[[40,15],[40,27],[40,36],[40,53],[35,74],[46,88]],[[41,15],[41,27],[41,36],[41,53],[35,87],[46,83]]]}
for d in ['e','s']:
 p=R/'art_source'/f'hero_{d}_walk_rebuild_v1';src=R/'art_source'/f'hero_{d}_walk_source_r8';c=np.array(C[d],float);s=np.array(S[d],float);cm=(c*w[None,:,None]).sum(1)/w.sum();sm=(s*w[None,:,None]).sum(1)/w.sum();ca=c-cm[:,None,:];sa=s-sm[:,None,:];scale=float((ca*sa*w[None,:,None]).sum()/(ca*ca*w[None,:,None]).sum());trans=sm-scale*cm
 raw=Image.open(p/'raw-v1.png').convert('RGBA');assert raw.size==(1310,1201);xs=[0,437,873,1310];ys=[0,601,1201];rebuild=Image.new('RGBA',raw.size);atlas=Image.new('RGBA',(768,128));records=[]
 ids=list(range(45,51)) if d=='e' else list(range(57,63))
 for i,fid in enumerate(ids):
  col=i%3;row=i//3;box=(xs[col],ys[row],xs[col+1],ys[row+1]);cell=raw.crop(box);rebuild.paste(cell,box[:2]);tx,ty=trans[i];mapped=c[i]*scale+trans[i];frame=cell.transform((128,128),Image.Transform.AFFINE,(1/scale,0,-tx/scale,0,1/scale,-ty/scale),resample=Image.Resampling.BICUBIC);atlas.paste(frame,(i*128,0));records.append({'source_id':fid,'raw_rectangle':box,'translation':trans[i].tolist(),'source_surface_points':dict(zip(names,s[i].tolist())),'raw_surface_points':dict(zip(names,c[i].tolist())),'mapped_surface_points':dict(zip(names,mapped.tolist())),'residuals':dict(zip(names,(mapped-s[i]).tolist())),'boot_right_minus_left_source':(s[i,-1]-s[i,-2]).tolist(),'boot_right_minus_left_candidate':(mapped[-1]-mapped[-2]).tolist()})
 assert raw.tobytes()==rebuild.tobytes();atlas.save(p/'v1-registered-atlas-128.png');sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();doc={'status':'registered_research_pending_original_size_review','direction':d.upper(),'source_ids':ids,'frame_size':[128,128],'native_root':[16,64],'common_uniform_scale':scale,'weights':dict(zip(names,w.tolist())),'registration':'Single group uniform scale; per-frame weighted surface-point rigid translation only. Clothing low weight due to armor displacement, not true skeleton.','uncertainty_px':{'source_clothing':3,'source_boot':2 if d=='e' else 1,'candidate_raw':8},'raw_sha256':sha(p/'raw-v1.png'),'atlas_sha256':sha(p/'v1-registered-atlas-128.png'),'raw_reassembles_byte_exact':True,'records':records};(p/'v1-registration.json').write_text(json.dumps(doc,indent=2)+'\n')
 bg=Image.new('RGBA',(768,384),(90,90,90,255));bg.alpha_composite(Image.open(src/'original-six-native-strip.png'),(0,0));bg.alpha_composite(atlas,(0,128));idle=Image.open(R/'assets/scifi/hero'/f'{d}_idle_v1/body.png').convert('RGBA');
 for i in range(6):bg.alpha_composite(idle.crop(((i%4)*128,0,(i%4+1)*128,128)),(i*128,256))
 bg.resize((1536,768),Image.Resampling.NEAREST).convert('RGB').save(p/'v1-source-candidate-idle-2x-gray.jpg',quality=95)
 print(d,scale,doc['atlas_sha256'],[(r['source_id'],r['boot_right_minus_left_candidate']) for r in records])
