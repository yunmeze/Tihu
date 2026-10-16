from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from scipy.ndimage import distance_transform_edt
O=Path(__file__).parent;P=O.parents[1];S=P/'art_source/earth_grass_downsample_sampling_plan_v1';M=P/'art_source/earth_ground_material_layers_plan_v1';V=P/'art_source/earth_ground_cross_seam_revision_plan_v3';D=P/'diagnostics/art_source/earth-grass-two-segment-composite-v1';D.mkdir(parents=True,exist_ok=True);h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
original=np.array(Image.open(V/'INPUT_ONLY_existing_art_context.png').convert('RGBA'));F=np.array(Image.open(S/'INPUT_G2_downsample_0625.png').convert('RGBA'));assert F.shape==(640,960,4);grass=np.array(Image.open(M/'DOMAIN_grass_BINARY.png'))>0;fixed=np.array(Image.open(V/'PROPOSED_fixed_replace_mask.png'))>0;internal=np.array(Image.open(S/'PROPOSED_internal_8raw_joint_NOT_APPLIED.png'))>0;allowed_outer=np.array(Image.open(M/'PROPOSED_same_grass_transition_zone_NOT_APPLIED.png'))>0;yy,xx=np.mgrid[:1152,:1536]
def decode(a):
 v=a.astype(np.float64)/255;return np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
def encode(a):
 v=np.where(a<=.0031308,12.92*a,1.055*np.maximum(a,0)**(1/2.4)-.055);return np.clip(np.floor(v*255+.5),0,255).astype('uint8')
def mix(a,b,w):return encode(decode(a)*(1-w[...,None])+decode(b)*w[...,None])
hard=original.copy();a=grass&(yy<560);b=grass&~a
hard[a]=F[yy[a]-72,xx[a]-368];hard[b]=F[yy[b]-442,xx[b]+340];hard[:,:,3]=255
assert int(internal.sum())==500
weights_i=np.zeros(grass.shape,np.float64);t=(yy[internal]+.5-556)/8;weights_i[internal]=t*t*(3-2*t)
joint=hard.copy();sy,sx=np.where(internal);va=F[sy-72,sx-368,:3];vb=F[sy-442,sx+340,:3];joint[sy,sx,:3]=mix(va,vb,weights_i[sy,sx])
# Existing grass-side safeguard: trim only, never enlarge approved outer zone. Exclude old curb/road near exits.
plan=json.loads((V/'PLAN.json').read_text());cp=plan['candidate_cover_polyline_localraw'];existing_grass_side=Image.new('1',(1536,1152));from PIL import ImageDraw
ImageDraw.Draw(existing_grass_side).polygon([(1535,0),(1241,0)]+cp+[(0,1151),(1535,1151)],fill=1)
x=xx+.5;y=yy+.5;cd=np.full(grass.shape,np.inf)
for p,q in zip(cp,cp[1:]):
 ax,ay=p;dx,dy=q[0]-ax,q[1]-ay;t2=np.clip(((x-ax)*dx+(y-ay)*dy)/(dx*dx+dy*dy),0,1);cd=np.minimum(cd,np.hypot(x-ax-t2*dx,y-ay-t2*dy))
outer=allowed_outer&grass&np.array(existing_grass_side)&(cd>=14)
# Conservative source-center margin independently check original allowed zone (>=curb halfwidth+4).
dist=np.full(grass.shape,np.inf)
for p,q in zip(plan['source_center_polyline_localraw'],plan['source_center_polyline_localraw'][1:]):
 ax,ay=p;dx,dy=q[0]-ax,q[1]-ay;t2=np.clip(((x-ax)*dx+(y-ay)*dy)/(dx*dx+dy*dy),0,1);dist=np.minimum(dist,np.hypot(x-ax-t2*dx,y-ay-t2*dy))
width=np.where(y<100,18-10*np.clip((y-72)/28,0,1),8);assert np.all(dist[outer]>=width[outer]/2+3.4) # pixel-center vs legacy integer-coordinate guide tolerance
# Use tighter >=4raw margin to avoid ambiguity; only trim allowed mask.
outer &= dist>=width/2+4
inside=distance_transform_edt(fixed);wo=np.zeros(grass.shape,np.float64);t=np.clip((inside[outer]-.5)/8,0,1);wo[outer]=t*t*(3-2*t) # weight of new grass; old original at outer boundary
final=joint.copy();oy,ox=np.where(outer);final[oy,ox,:3]=mix(original[oy,ox,:3],joint[oy,ox,:3],wo[oy,ox]);final[:,:,3]=255
np.savez_compressed(O/'reproducible_weights_float64.npz',internal_weight_B=weights_i,outer_weight_new=wo)
np.savez_compressed(O/'stage_RGBA_differences_int16.npz',delta_01_to_02=joint.astype('int16')-hard.astype('int16'),delta_02_to_03=final.astype('int16')-joint.astype('int16'))
Image.fromarray(np.round(weights_i*65535).astype('uint16')).save(O/'internal_weight_B_preview16.png');Image.fromarray(np.round(wo*65535).astype('uint16')).save(O/'outer_weight_new_preview16.png');Image.fromarray(outer.astype('uint8')*255).save(O/'ACTUAL_outer_transition_mask.png')
arrays=[('01_G_ONLY_hard.png',hard),('02_internal_8raw.png',joint),('03_outer_8raw.png',final)];checks=[]
for n,im in arrays:
 assert np.array_equal(im[~grass],original[~grass]);assert np.array_equal(im[~fixed],original[~fixed]);assert (im[:,:,3]==255).all();Image.fromarray(im).save(O/n);checks.append({'file':n,'sha256':h(O/n),'outside_grass_RGBA_changed':int(np.any(im!=original,axis=2)[~grass].sum()),'outside_fixed_RGBA_changed':int(np.any(im!=original,axis=2)[~fixed].sum()),'alpha_extrema':[int(im[:,:,3].min()),int(im[:,:,3].max())]})
for n,left,right,permit in [('01_to_02',hard,joint,internal),('02_to_03',joint,final,outer)]:
 changed=np.any(left!=right,axis=2);assert not np.any(changed&~permit);Image.fromarray(changed.astype('uint8')*255).save(O/(n+'_changed_mask.png'));checks.append({'step':n,'changed_pixels':int(changed.sum()),'outside_step_mask_changed':int((changed&~permit).sum()),'permitted_pixels':int(permit.sum())})
for name,box in [('internal_joint',[512,528,656,592]),('old_new_interface',[784,304,976,416]),('middle_outer',[480,544,704,672]),('south_kinks',[40,816,176,1040]),('upstream',[1184,64,1280,160])]:
 w,hh=box[2]-box[0],box[3]-box[1];board=Image.new('RGBA',(4*w,hh))
 for i,im in enumerate([original,hard,joint,final]):board.paste(Image.fromarray(im).crop(box),(i*w,0))
 board.save(D/(name+'_original_hard_internal_outer.png'))
r={'status':'RESEARCH ONLY; pending visual acceptance','donor_F_sha256':h(S/'INPUT_G2_downsample_0625.png'),'F_dimensions':[960,640],'mapping_A':[-368,-72],'mapping_B':[340,-442],'split_local_y':560,'internal_pixels':int(internal.sum()),'outer_original_allowed_pixels':int(allowed_outer.sum()),'outer_actual_pixels':int(outer.sum()),'outer_trim_reason':'Do not mix existing curb/paving at canvas exits into new grass; same-grass side only, >=4raw from source curb, no expansion','color_math':'sRGB decode threshold0.04045 /12.92 or((v+.055)/1.055)^2.4; mix linear using saved float64 weights; encode threshold0.0031308 then floor(255*v+.5); alpha255','internal_formula':'B weight smoothstep((y+.5-556)/8) only500px; outside use hard','outer_formula':'New weight smoothstep(clamp((EDT(fixed_mask)-.5)/8,0,1)) only ACTUAL_outer_transition_mask; outside use internal result','checks':checks,'C_lighting_B':'Not executed. Original B-seam correction scope not broadened; G-only geometry study remains incomplete curb art.','inputs':[{'path':str(p.relative_to(P)),'sha256':h(p)}for p in [S/'SAMPLING_PLAN.json',S/'INPUT_G2_downsample_0625.png',S/'PROPOSED_internal_8raw_joint_NOT_APPLIED.png',M/'DOMAIN_grass_BINARY.png',M/'PROPOSED_same_grass_transition_zone_NOT_APPLIED.png',V/'INPUT_ONLY_existing_art_context.png',V/'PROPOSED_fixed_replace_mask.png']]}
bmask=Image.new('L',(1536,1152));bmask.paste(Image.open(P/'art_source/earth_south_ground_local_revision_plan_v1/B_grass_only_allowed_mask.png'),(0,224));bm=np.array(bmask)>0
r['B_changed_pixels']={n:int((np.any(im!=original,axis=2)&bm).sum())for n,im in arrays};assert all(v==0 for v in r['B_changed_pixels'].values())
r['visual_review']='5/8 grain improved; internal joint not a salient horizontal stripe at reviewed crops; outer transition reduces hard join but narrow fine-grain strip remains distinguishable against coarser south candidate grass. C/contact finish absent. Root review required; not whole-ground approval.'
(O/'review.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'internal':r['internal_pixels'],'outer':r['outer_actual_pixels'],'allowed':r['outer_original_allowed_pixels'],'checks':checks}))
