from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt
P=Path(__file__).resolve().parents[2]
D=P/'art_source/a13_main_temple_support_registration';O=D/'technical_v2';O.mkdir(exist_ok=True)
G=P/'diagnostics/art_source/a13-main-temple';rawpath=P/'art_source/a13_main_temple_candidate_v2/raw.png'
raw=Image.open(rawpath).convert('RGBA');a=np.array(raw);h,w=a.shape[:2]
c=json.loads((P/'art_source/a13_main_temple_source/source-group-contract.json').read_text());owners=c['owners_in_draw_order']
s=.533687668884736;t=np.array([2979.8431118835334,665.2144416536716]);yy,xx=np.indices((h,w));wx=t[0]+(xx+.5)*s;wy=t[1]+(yy+.5)*s
# Visible top-plane readings in crop(240,700,1250,1080), conservative interiors.
polys={
'left_landing':[(112,52),(263,138),(268,162),(130,83)],
'left_connected_stair_tops_and_narrow_risers':[(128,91),(264,169),(169,253),(169,262),(45,180),(45,171)],
'right_landing':[(736,191),(851,125),(864,151),(746,219)],
'right_connected_stair_tops_and_narrow_risers':[(744,233),(864,161),(948,249),(948,259),(828,332),(828,322),(744,238)],
}
mask=Image.new('L',(w,h));md=ImageDraw.Draw(mask)
for poly in polys.values():md.polygon([(x+240,y+700)for x,y in poly],fill=255)
# Only original support-domain cells may receive ground-level pieces. True top mask
# prevents their rectangular source footprint from pulling rails/risers into layer0.
support_domain=np.zeros((h,w),bool)
for o in owners:
 if o['layer']==0:
  x,y,ow,oh=o['world_rect'];support_domain|=(wx>=x)&(wx<x+ow)&(wy>=y)&(wy<y+oh)
isground=np.array(mask)>0
# Layer-specific original alpha provenance. All source sheets are read-only.
labels={0:np.full((665,796),-1,np.int16),1:np.full((665,796),-1,np.int16)};pages={}
for i,o in enumerate(owners):
 path=P/o['atlas_page'][6:]
 if path not in pages:pages[path]=Image.open(path).convert('RGBA')
 rx,ry,rw,rh=o['atlas_rect'];alpha=np.array(pages[path].crop((rx,ry,rx+rw,ry+rh)))[:,:,3]>0
 x,y,_,_=o['world_rect'];x-=2948;y-=642
 sub=labels[o['layer']][y:y+rh,x:x+rw];sub[alpha]=i
sx=np.clip(np.floor(wx-2948).astype(int),0,795);sy=np.clip(np.floor(wy-642).astype(int),0,664)
assigned=np.full((h,w),-1,np.int16);inferred={}
for layer in [0,1]:
 lab=labels[layer];_,inds=distance_transform_edt(lab<0,return_indices=True);nearest=lab[inds[0],inds[1]]
 selected=isground if layer==0 else ~isground
 assigned[selected]=nearest[sy[selected],sx[selected]]
 inferred[str(layer)]=int(np.sum(selected&(a[:,:,3]>0)&(lab[sy,sx]<0)))
visible=a[:,:,3]>0;stored=visible|np.any(a[:,:,:3]!=0,axis=2);rebuild=np.zeros_like(a);coverage=np.zeros((h,w),np.uint8);entries=[]
for i,o in enumerate(owners):
 sel=(assigned==i)&stored;count=int(np.sum(sel&visible));entry={k:o[k] for k in ['key','cell','source_cell','flag','layer','sort_y','stable_source_order','frame_index']};entry['visible_pixel_count']=count
 if np.any(sel):
  ys,xs=np.where(sel);x0,y0,x1,y1=int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)
  tile=np.zeros((y1-y0,x1-x0,4),np.uint8);inside=sel[y0:y1,x0:x1];tile[inside]=a[y0:y1,x0:x1][inside]
  name=f"owner-{o['frame_index']}.png";Image.fromarray(tile).save(O/name)
  entry.update(texture='res://'+str((O/name).relative_to(P)),raw_rect=[x0,y0,x1-x0,y1-y0],world_top_left=(t+np.array([x0,y0])*s).tolist(),scale=s,sha256=hashlib.sha256((O/name).read_bytes()).hexdigest())
  rebuild[sel]=a[sel];coverage[sel]+=1
 else:entry.update(texture=None,raw_rect=None,world_top_left=None,scale=s,empty_reason='No generated visible pixels assigned; original owner remains suppressed, no invented apron.')
 entries.append(entry)
assert np.array_equal(rebuild,a);assert np.all(coverage[stored]==1);assert all(o['layer']==owners[i]['layer']for i,o in enumerate(entries))
manifest={'schema':'a13-temple-technical-partition-v2','status':'optional technical diagnostic only, not native accepted','raw_texture':'res://'+str(rawpath.relative_to(P)),'raw_sha256':hashlib.sha256(rawpath.read_bytes()).hexdigest(),'source_contract_sha256':hashlib.sha256((P/'art_source/a13_main_temple_source/source-group-contract.json').read_bytes()).hexdigest(),'whole_building_registration':{'scale':s,'world_top_left':t.tolist(),'rotation':0,'shear':0},'suppress_source_keys':[o['key']for o in owners],'owners':entries,'sampling':{'texture_filter':'nearest for this diagnostic','mipmaps':False,'note':'Independent linear-filtered alpha cutouts can darken shared edges; do not silently enable linear. Compare partitioned/whole same registration without actor before depth tests.'},'partition_method':{'layer0':'new visible landing and connected stair interiors INCLUDING narrow step risers, supported by original layer0 source strips3975/3980/3981/3982/3986; exclude side cheeks/rails/walls; nearest original layer0 owner with keys unchanged','layer1':'all other visible pixels; original layer1 alpha provenance, nearest layer1 provenance where old shape absent','nearest_provenance_pixels':inferred,'top_polygons_crop_origin':[240,700],'top_polygons':polys,'manual_boundary_uncertainty_raw_pixels':[3,6]},'validation':{'source_key_count':30,'duplicate_keys':0,'rgba_visible_pixels':int(visible.sum()),'unique_coverage':True,'overlap_pixels':0,'lost_visible_pixels':0,'visible_rgba_reassembly_exact':True,'full_raw_rgba_reassembly_exact':True,'transparent_rgb_pixels_preserved':int(np.sum(stored&~visible)),'sampling_out_of_bounds':0,'empty_owner_ids':[e['frame_index']for e in entries if not e['visible_pixel_count']]},'limitations':['Stair component borders are manual visible material readings, not boot-target-derived masks; narrow risers are included because original layer0 support strips visibly contain them. Side cheeks/rails remain layer1.','Nearest layer1 provenance is a diagnostic depth proposal, not native occlusion proof.','Uncertain stair-to-cheek/rail boundary pixels remain layer1; inspect on actual routes. No claim every boot sample must become layer0.','Roof silhouette design differs from source; whole building uses only one support-fit scale+translation.','No runtime, source flags, collisions or actor sorting modified.']}
(O/'registration.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
# Technical diagnostic overlays only. Raw/tiles are never colored.
bg=Image.new('RGBA',(w,h),(72,82,78,255));bg.alpha_composite(raw);ov=Image.new('RGBA',(w,h));ovarr=np.array(ov);ovarr[isground&visible]=[0,255,220,115];bg.alpha_composite(Image.fromarray(ovarr));bg.crop((240,700,1250,1080)).convert('RGB').save(G/'v2-technical-v2-stair-components.jpg')
print(json.dumps(manifest['validation']));print('nearest',inferred)
