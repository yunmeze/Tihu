#!/usr/bin/env python3
"""CPU candidate only. Material labels from reviewed source-pixel curves; originals unchanged."""
from pathlib import Path
import json,hashlib,runpy
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt
P=Path(__file__).resolve().parents[2];O=P/'diagnostics/earth-upright-receiver-candidate';O.mkdir(exist_ok=True)
n=runpy.run_path(str(P/'art_source/earth_upright_shadow_study_v1/measure.py'));g=n['g'];rows=json.loads((P/'art_source/earth_upright_shadow_study_v1/measurements.json').read_text())['instances'];packs=json.loads((P/'assets/original/manifest.json').read_text())['packs'];pack=packs['Map/Res/Debris'];atlas=np.array(Image.open(P/pack['pages'][0]['file'][6:]).convert('RGBA'));records=json.loads((P/'art_source/earth_upright_receiver_review_v1/report.json').read_text())[1]['records']
# Manual source-pixel lower limits of positively identified apron. Bounds are conservative,
# intentionally leaving uncertain transition pixels forbidden. Never selected to make a cast pass.
curves={57:[[0,32],[8,28],[16,23],[24,18],[32,14],[40,10],[47,8]],58:[[0,8],[5,8],[10,9],[15,6],[20,5],[25,7],[30,11],[35,15],[40,17],[47,20]],59:[[0,12],[5,15],[10,21],[15,28],[20,35],[25,40],[47,40]]}
# Inner known stone/water/vertical regions. Everything outside these and the reviewed apron
# is unknown and remains forbidden; no optimistic semantic extrapolation.
corecurves={57:[[0,48],[8,44],[16,39],[24,34],[32,28],[40,22],[47,18]],58:[[0,18],[5,18],[10,17],[15,13],[20,11],[25,15],[30,21],[35,25],[40,28],[47,34]],59:[[0,24],[5,29],[10,36],[15,43],[20,50],[25,58],[47,70]]}
labels={};trace=[]
for rec in records:
 if rec['pack']!='Map/Res/Debris':continue
 index=rec['frame_index'];f=pack['frames'][str(index)];x,y,w,h=f['rect'];rgba=atlas[y:y+h,x:x+w];alpha=rgba[:,:,3]>0;xx=np.arange(w);yy=np.arange(h)[:,None];apron=alpha&(yy<np.floor(np.interp(xx,*np.array(curves[index]).T))[None,:]);core=alpha&(yy>=np.ceil(np.interp(xx,*np.array(corecurves[index]).T))[None,:])&(yy<45);unknown=alpha&~apron&~core;labels[index]={'apron':apron,'core':core,'unknown':unknown,'origin':rec['world_rgba_rect'][:2]}
 # These source-label maps are diagnostic masks, not replacement assets.
 rgb=np.array(rgba[:,:,:3]);rgb[apron]=rgb[apron]*.5+np.array([30,190,50])*.5;rgb[core]=rgb[core]*.5+np.array([230,30,20])*.5;rgb[unknown]=rgb[unknown]*.5+np.array([230,170,20])*.5;rgb[~alpha]=[25,25,25];Image.fromarray(rgb.astype(np.uint8)).resize((w*6,h*6)).save(O/f'debris-{index}-material-labels.png')
 trace.append({'frame':index,'world_origin':rec['world_rgba_rect'][:2],'source_cell':rec['source_cell'],'source_order':rec['order'],'reviewed_apron_upper_open_y_curve':curves[index],'known_nonflat_seed_lower_closed_y_curve':corecurves[index],'apron_texels':int(apron.sum()),'known_nonflat_seed_texels':int(core.sum()),'unknown_forbidden_texels':int(unknown.sum()),'rule':'only positive-alpha pixels above the apron curve are admitted as reviewed grass/soil; all other positive alpha remains forbidden, known core or unknown'})
report=[]
for i,row in enumerate(rows):
 rect=row['root_uncertainty_review_world_rect'];origin=np.array(rect[:2]);size=np.array(rect[2:])*2;world=np.array(row['world_origin']);envelope=g.raster(n['base']+np.tile(world,2),origin,size)
 # Conservative combined root uncertainty: +/-2logical root selection plus +/-4 source anchor.
 # Projection/root shifts bounded by +/-7.2x and +/-9.3y logical; enlarge entire envelope.
 uncertain=g.raster(n['base']+np.tile(world,2)+[-7.2,-9.3,7.2,9.3],origin,size)
 forbidden=np.zeros(envelope.shape,bool);known=np.zeros_like(forbidden);unknown=np.zeros_like(forbidden);apron=np.zeros_like(forbidden)
 for lab in labels.values():
  for key,target,pad in [('core',known,4),('unknown',unknown,4),('apron',apron,0)]:target|=g.raster(g.rects_for(lab[key],lab['origin'],1,pad),origin,size)
 forbidden=known|unknown;allowed=~forbidden
 core_raw=np.zeros_like(forbidden)
 for lab in labels.values():core_raw|=g.raster(g.rects_for(lab['core'],lab['origin'],1,0),origin,size)
 core_gap=distance_transform_edt(~core_raw)/2 if core_raw.any()else None
 fullrect=n['base']+np.tile(world,2);fullbounds=np.r_[fullrect[:,:2].min(0),fullrect[:,2:].max(0)];errorbounds=fullbounds+[-7.2,-9.3,7.2,9.3]
 assert (errorbounds[:2]>=origin).all()and(errorbounds[2:]<=origin+np.array(rect[2:])).all(), 'error envelope crosses patch' 
 gap=distance_transform_edt(~forbidden)/2 if forbidden.any()else None
 for name,a in [('allowed',allowed),('forbidden',forbidden),('nominal-envelope',envelope),('root-error-envelope',uncertain)]:Image.fromarray(a.astype(np.uint8)*255).save(O/f'{row["instance"]}-{name}.png')
 floor=Image.open(P/'diagnostics/earth-upright-receiver-review'/f'{row["instance"]}-floor.png').convert('RGB').resize(tuple(size));rgb=np.array(floor).astype(float);rgb[envelope]=rgb[envelope]*.6+[25,70,180]*np.ones(3)*.4;rgb[forbidden]=rgb[forbidden]*.5+np.array([225,35,35])*.5;rgb[uncertain&~envelope]=rgb[uncertain&~envelope]*.6+np.array([200,150,10])*.4;Image.fromarray(np.uint8(rgb)).save(O/f'{row["instance"]}-candidate-overlay.png')
 report.append({'instance':row['instance'],'world_rect':rect,'nominal_envelope_cells':int(envelope.sum()),'uncertainty_envelope_cells':int(uncertain.sum()),'forbidden_cells':int(forbidden.sum()),'full_nominal_bounds_xyxy':fullbounds.tolist(),'full_uncertainty_bounds_xyxy':errorbounds.tolist(),'complete_error_envelope_inside_patch':True,'nominal_known_nonflat_seed_min_center_distance':None if core_gap is None else float(core_gap[envelope].min()),'error_known_nonflat_seed_min_center_distance':None if core_gap is None else float(core_gap[uncertain].min()),'nominal_overlap_forbidden':int((envelope&forbidden).sum()),'nominal_overlap_known_core_plus4':int((envelope&known).sum()),'nominal_overlap_unknown_plus4':int((envelope&unknown).sum()),'uncertainty_overlap_forbidden':int((uncertain&forbidden).sum()),'uncertainty_overlap_known_core_plus4':int((uncertain&known).sum()),'uncertainty_overlap_unknown_plus4':int((uncertain&unknown).sum()),'nominal_min_forbidden_cell_center_distance':None if gap is None else float(gap[envelope].min()),'uncertainty_min_forbidden_cell_center_distance':None if gap is None else float(gap[uncertain].min()),'nominal_pass':not bool((envelope&forbidden).any()),'uncertainty_pass':not bool((uncertain&forbidden).any())})
result={'schema':'earth-upright-receiver-two-patch-cpu-candidate-v1','status':'parent material/overlay review required; no runtime/GPU promotion','left_road_border_semantics':'parent-approved coplanar decorative approximation; not physical elevation evidence','density':4.5,'root_raw':[560,1329],'cast':[1.2,.55],'opacity':.25,'blur_logical':.8,'dilation_logical':4,'uncertainty_expansion_logical_xy':[7.2,9.3],'traces':trace,'patches':report};(O/'candidate.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(report,indent=2))
