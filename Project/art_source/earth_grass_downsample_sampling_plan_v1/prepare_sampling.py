from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,__version__ as pillow_version
from scipy.spatial import ConvexHull,distance_matrix
from scipy.ndimage import distance_transform_edt,binary_dilation
O=Path(__file__).parent;P=O.parents[1];M=P/'art_source/earth_ground_material_layers_plan_v1';V=P/'art_source/earth_ground_cross_seam_revision_plan_v3';G=P/'art_source/earth_ground_grass_material_g_v2/raw.png';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
g=Image.open(G).convert('RGB');assert g.size==(1536,1024);grass=np.array(Image.open(M/'DOMAIN_grass_BINARY.png'))>0;yy,xx=np.mgrid[:1152,:1536];points=np.argwhere(grass)[:,::-1];hull=points[ConvexHull(points).vertices];distances=distance_matrix(hull,hull);a,b=np.unravel_index(np.argmax(distances),distances.shape);maxdistance=float(distances[a,b]);results=[]
for n,w,hh in [('050',768,512),('0625',960,640),('075',1152,768)]:
 im=g.resize((w,hh),Image.Resampling.LANCZOS);im.save(O/('INPUT_G2_downsample_'+n+'.png'));results.append({'name':n,'ratio':w/1536,'size':[w,hh],'single_rigid_max_distance':float(np.hypot(w-1,hh-1))})
sampled=Image.open(O/'INPUT_G2_downsample_0625.png').convert('RGB');data=np.asarray(sampled);segments=[];donors=[];expanded=[]
for name,sel,dx,dy in [('A',grass&(yy<560),-368,-72),('B',grass&(yy>=560),340,-442)]:
 ys,xs=np.where(sel);u=xs+dx;v=ys+dy;assert ((u>=0)&(u<960)&(v>=0)&(v<640)).all();dm=np.zeros((640,960),bool);dm[v,u]=True;assert dm.sum()==sel.sum();Image.fromarray(sel.astype('uint8')*255).save(O/('TARGET_'+name+'_TECHNICAL.png'));Image.fromarray(dm.astype('uint8')*255).save(O/('DONOR_'+name+'_TECHNICAL.png'));donors.append(dm)
 # Internal8raw transition is proposal only: each donor needs at most4 extra rows across split.
 ex=grass&((yy<564)if name=='A' else(yy>=556));ey,exx=np.where(ex);eu=exx+dx;ev=ey+dy;assert ((eu>=0)&(eu<960)&(ev>=0)&(ev<640)).all();em=np.zeros((640,960),bool);em[ev,eu]=True;expanded.append(em)
 segments.append({'name':name,'target_condition':'grass && y<560'if name=='A'else'grass && y>=560','pixels':int(sel.sum()),'integer_translation_to_downsampled_donor':[dx,dy],'donor_bbox':[int(u.min()),int(v.min()),int(u.max()+1),int(v.max()+1)],'source_mask_sha256':h(O/('DONOR_'+name+'_TECHNICAL.png')),'target_mask_sha256':h(O/('TARGET_'+name+'_TECHNICAL.png'))})
assert not (donors[0]&donors[1]).any();assert not(expanded[0]&expanded[1]).any();gap=float(distance_transform_edt(~expanded[0])[expanded[1]].min());assert gap>6
transition=grass&(yy>=556)&(yy<564);Image.fromarray(transition.astype('uint8')*255).save(O/'PROPOSED_internal_8raw_joint_NOT_APPLIED.png')
# Technical visualizations of donor allocation, not destination RGB assembly.
board=sampled.copy()
for dm,col in zip(donors,[(255,30,150),(30,220,255)]):board.paste(Image.new('RGB',board.size,col),(0,0),Image.fromarray(dm.astype('uint8')*75))
board.save(O/'DONOR_ALLOCATION_NOT_ART.png')
# Three native crops compare scale, not a reconstructed target image.
ref=Image.open(M/'approved_v4_grass_sample_native2x.png').convert('RGB');cmp=Image.new('RGB',(1024,280));cmp.paste(ref,(0,24));ImageDraw.Draw(cmp).text((0,0),'OLD approved 1:1',fill='white')
boxes=[(688,32,944,288),(320,256,576,512),(672,368,928,624)]
for i,box in enumerate(boxes):cmp.paste(sampled.crop(box),((i+1)*256,24));ImageDraw.Draw(cmp).text(((i+1)*256,0),'5/8 '+str(box[:2])+'1:1',fill='white')
cmp.save(O/'THREE_SAMPLES_0625_NOT_ART.png')
# Compare paired donor neighborhoods at the one planned joint, no pixel mixing.
xs=np.where(transition[560])[0];cx=int(np.median(xs));pair=Image.new('RGB',(256,152));joint_crops=[]
for i,(dx,dy)in enumerate([(-368,-72),(340,-442)]):
 u,v=cx+dx,560+dy;left=max(0,min(832,u-64));top=max(0,min(512,v-64));box=[left,top,left+128,top+128];pair.paste(sampled.crop(box),(i*128,24));ImageDraw.Draw(pair).text((i*128,0),['A donor','B donor'][i],fill='white');joint_crops.append(box)
pair.save(O/'JOINT_DONORS_SIDE_BY_SIDE_NOT_ASSEMBLED.png')
sy,sx=np.where(transition);va=data[sy-72,sx-368].astype(float);vb=data[sy-442,sx+340].astype(float);la=va@np.array([.2126,.7152,.0722]);lb=vb@np.array([.2126,.7152,.0722])
r={'status':'SAMPLING PLAN ONLY; material downsampling and technical masks/crops, no repaired-image assembly','original_G2_sha256':h(G),'selected_downsample':{'ratio':[5,8],'original':[1536,1024],'result':[960,640],'filter':'Pillow LANCZOS','pillow_version':pillow_version,'sha256':h(O/'INPUT_G2_downsample_0625.png'),'original_sample_center_formula':'original_raw=((u+0.5)/(5/8)-0.5,(v+0.5)/(5/8)-0.5), low-pass support radius approximately3/(5/8)=4.8input pixels','logical_density_after_material_reassignment':'donor output sampled1:1 at2texels/world unit; original G2 world framing is NOT retained as geometry, only material grain is minified'},'candidate_scales':results,'minimum_segment_proof':{'target_max_pair_distance_raw':maxdistance,'target_pair_xy':[hull[a].tolist(),hull[b].tolist()],'donor_max_pair_distance_raw':float(np.hypot(959,639)),'single_translation_or_rigid_rotation_impossible':bool(maxdistance>np.hypot(959,639)),'two_feasible_segments':True,'minimum_segments_under_current_rigid_rule':2},'segments':segments,'source_disjointness':{'base_shared_downsampled_texels':0,'expanded_joint_shared_downsampled_texels':0,'expanded_min_distance_downsampled_pixels':gap,'lanczos_support_disjoint':gap>6,'no_repeated_tile_or_mirrored_or_stretched_segment':True,'caveat':'Unique source coordinates do not prove generative texture has no naturally similar motifs.'},'planned_internal_joint':{'local_y':560,'world_y':1576,'proposed_zone_y_halfopen':[556,564],'max_width_raw':8,'pixels':int(transition.sum()),'mask':'PROPOSED_internal_8raw_joint_NOT_APPLIED.png','approval':'New internal same-grass joint, submitted separately; prior outer transition authorization does not silently authorize this joint. No weights or RGB blend applied.','donor_neighborhood_crops':joint_crops,'paired_region_mean_RGB_A':va.mean(0).tolist(),'paired_region_mean_RGB_B':vb.mean(0).tolist(),'paired_luma_mean_A':float(la.mean()),'paired_luma_mean_B':float(lb.mean()),'warning':'Similar means do not prove no visible joint; texture phase/detail and crop review still required.'},'protected':'Original source geometry, three-domain union, B seam and all non-grass RGB unchanged; no destination art made','inputs':[{'path':str(p.relative_to(P)),'sha256':h(p)}for p in [G,M/'DOMAIN_grass_BINARY.png',V/'PLAN.json',V/'PROPOSED_fixed_replace_mask.png']]}
(O/'SAMPLING_PLAN.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'proof':r['minimum_segment_proof'],'segments':segments,'disjoint':r['source_disjointness'],'joint':r['planned_internal_joint']}))
