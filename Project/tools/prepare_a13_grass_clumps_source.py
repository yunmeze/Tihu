"""Two static A13 grass-clump source groups, preserving both spatial owners."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1];OUT=P/'art_source/a13_grass_clumps_source';D=P/'diagnostics/art_source/a13-grass-clumps'
SPECS=[{'id':'grass239-240','frames':[239,240],'selected_root':[54,30],'feet':[[21,24],[40,24]],'uncertainty':3,'read':'Sparse spreading upright shoots and multiple low stems. Two visible green basal contact-band reads; no visible woody root. Avoid black checker cast and empty bbox corners.'},{'id':'grass241-242','frames':[241,242],'selected_root':[54,26],'feet':[[21,22],[34,22]],'uncertainty':2,'read':'Two downward-tapering green basal tips below denser upper blades, with large baked checker cast to right. Basal tips are visible material landmarks; precise botanical root/physical-ground location is inferred, not surveyed.'}]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
 OUT.mkdir(parents=True,exist_ok=True);D.mkdir(parents=True,exist_ok=True);mp=P/'data/maps/A13.json';mf=P/'assets/original/manifest.json';m=json.loads(mp.read_text());pk=json.loads(mf.read_text())['packs']['Map/Res/Plant'];pages={};ims={};groups=[];V=[2416,833.28,3440,1601.28];composites={}
 def owners(root,ids):
  os=[]
  for dx,k in enumerate(ids):
   x,y=root[0]+dx,root[1];c=m['cells'][x*m['height']+y];assert c[2:]==[2,k];f=pk['frames'][str(k)];page=pk['pages'][f['page']]['file'];a,b,w,h=f['rect']
   if page not in pages:pages[page]=Image.open(P/page[6:]).convert('RGBA')
   if k not in ims:ims[k]=pages[page].crop((a,b,a+w,b+h))
   os.append({'key':f'Plant:{k}@{x},{y}','pack':'Map/Res/Plant','frame_index':k,'cell':[x,y],'source_cell':c,'source_cell_index':x*m['height']+y,'source_map_byte_offset':m['cellByteOffsets'][x*m['height']+y],'flag':c[1],'layer':0 if c[1]in[1,-2]else 2 if c[1]==2 else 1,'sort_y':y,'stable_source_order':x*m['height']+y,'original_canvas':f['original'],'offset_ignored':f['offset'],'crop':f['crop'],'atlas_page':page,'atlas_rect':f['rect'],'native_source_offset':f['sourceOffset'],'native_source_bytes':f['sourceBytes'],'rgba_sha256':hashlib.sha256(ims[k].tobytes()).hexdigest(),'world_rect':[x*48+f['crop'][0],y*32+32-f['original'][1]+f['crop'][1],w,h]})
  return sorted(os,key=lambda o:(o['layer'],o['sort_y'],o['stable_source_order']))
 for spec in SPECS:
  selected=owners(spec['selected_root'],spec['frames']);b=[min(o['world_rect'][0]for o in selected),min(o['world_rect'][1]for o in selected),max(o['world_rect'][0]+o['world_rect'][2]for o in selected),max(o['world_rect'][1]+o['world_rect'][3]for o in selected)];size=[b[2]-b[0],b[3]-b[1]];im=Image.new('RGBA',size)
  for o in selected:x,y,_,_=o['world_rect'];im.alpha_composite(ims[o['frame_index']],(x-b[0],y-b[1]))
  slug=spec['id'];im.save(D/f'{slug}-source-composite.png');composites[slug]=im;bg=Image.new('RGBA',size,(70,75,70,255));bg.alpha_composite(im);bg.save(D/f'{slug}-source-preview.png');bg.resize((size[0]*10,size[1]*10),Image.Resampling.NEAREST).save(D/f'{slug}-material-local-10x.png');landmarks=[]
  marked=bg.copy();dr=ImageDraw.Draw(marked)
  for i,(x,y)in enumerate(spec['feet']):
   assert im.getpixel((x,y))[3]>0;wx,wy=x+b[0],y+b[1];contributors=[]
   for o in selected:
    X,Y,W,H=o['world_rect'];px,py=wx-X,wy-Y
    if 0<=px<W and 0<=py<H and ims[o['frame_index']].getpixel((px,py))[3]:contributors.append(o['key'])
   u=spec['uncertainty'];region=[max(0,x-u),max(0,y-u),min(size[0],x+u+1),min(size[1],y+u+1)];dr.rectangle((region[0],region[1],region[2]-1,region[3]-1),outline='cyan');landmarks.append({'id':f'B{i+1}_visible_green_basal_read','source_composite_xy':[x,y],'world_xy':[wx,wy],'manual_uncertainty_px':u,'read_region_xyxy':region,'source_rgba_at_point':list(im.getpixel((x,y))),'contributors':contributors})
  marked.resize((size[0]*10,size[1]*10),Image.Resampling.NEAREST).save(D/f'{slug}-basal-landmarks-10x.png')
  family=[]
  for index,c in enumerate(m['cells']):
   if c[2:]!=[2,spec['frames'][0]]:continue
   root=list(divmod(index,m['height']));os=owners(root,spec['frames']);dx,dy=(root[0]-spec['selected_root'][0])*48,(root[1]-spec['selected_root'][1])*32;assert all(o['world_rect']==[s['world_rect'][0]+dx,s['world_rect'][1]+dy,*s['world_rect'][2:]]for o,s in zip(os,selected));visible=[o['key']for o in os if o['world_rect'][0]<V[2]and o['world_rect'][1]<V[3]and o['world_rect'][0]+o['world_rect'][2]>V[0]and o['world_rect'][1]+o['world_rect'][3]>V[1]]
   family.append({'root_cell':root,'complete':True,'same_rgba_and_relative_layout':True,'world_translation_from_selected':[dx,dy],'potential_first_screen_keys':visible,'owners_in_draw_order':os,'flag_differences':[{'frame_index':o['frame_index'],'flag':o['flag'],'selected_flag':s['flag']}for o,s in zip(os,selected)if o['flag']!=s['flag']]})
  groups.append({'id':slug,'selected_root_owner_cell':spec['selected_root'],'frame_indices':spec['frames'],'owner_count':2,'world_bounds_xyxy':b,'composite_size':size,'owners_in_draw_order':selected,'visible_basal_landmarks':landmarks,'material_read':spec['read'],'physical_anchor_limit':'These are visible basal-material reads with stated uncertainty. No woody root is visible, so a unique physical root/ground contact cannot be proven. Do not substitute checker-shadow tip, alpha bbox bottom or logical cell center.','instances':family,'first_screen_roots':[f['root_cell']for f in family if f['potential_first_screen_keys']],'animation':{'phase_count':1,'proof':'Both are map kind2 static placements at adjacent x cells, same y; neither kind5 nor kind8. These two frames coexist spatially, not two animation phases.'}})
 sheet=Image.new('RGBA',(150,60));dr=ImageDraw.Draw(sheet)
 for x,(name,im)in zip([0,80],composites.items()):sheet.alpha_composite(im,(x,20));dr.text((x,0),name,fill='white')
 sheet.save(D/'two-families-native-sheet.png');bg=Image.new('RGBA',sheet.size,(70,75,70,255));bg.alpha_composite(sheet);bg.resize((900,360),Image.Resampling.NEAREST).save(D/'two-families-source-sheet-6x.png')
 alias=[]
 for a in [239,240]:
  for b in [241,242]:
   if ims[a].size==ims[b].size and ims[a].tobytes()==ims[b].tobytes():alias.append([a,b])
 contract={'schema':'a13-two-grass-clumps-original-source-v1','status':'Source preparation only; no generation or runtime installation.','source':{'map_sha256':sha(mp),'native_map_sha256':m['sourceSha256'],'manifest_sha256':sha(mf),'plant_source_sha256':pk['source_sha256'],'renderer_sha256':sha(P/'scripts/world_view.gd')},'coordinate_contract':m['render_contract'],'groups':groups,'first_screen_scope':{'239-240':[[54,30]],'241-242':[[54,26],[54,31]],'visibility':'Original AABB potential only; top pair is clipped by first-screen top edge. Contract and boards contain complete family pixels, never viewport-cut fragments.'},'shape_distinction':{'239-240':'64x27 sparse spreading upward shoots, broad low stem band.','241-242':'58x26 differently shaped denser upper blades and two tapering basal tips with checker cast.','cross_family_exact_rgba_frame_aliases':alias,'proof':'Different dimensions, cropped-frame hashes, native pair composites and outline arrangement. No mirror/rotation/scale equivalence asserted.'},'depth':'Both selected pairs are layer1, same owner y within each pair, stable x-major order. Preserve individual keys/crop/canvas. Do not merge family identity or convert spatial slices to animation.','limits':['Baked checker cast belongs to original Plant frames; do not add a second shadow beneath retained source cast.','Basal reads are low-resolution visual estimates, not precise surveyed root anchors.','Original alpha and frame crops remain unchanged.','No current-HD, gameplay or occlusion acceptance performed.']}
 save(OUT/'source-group-contract.json',contract)
 (OUT/'PLAN.md').write_text('''# A13 two grass-clump source groups

Reproduce: python Project/tools/prepare_a13_grass_clumps_source.py.

239–240: selected root(54,30), complete64x27 source.241–242: selected root(54,26), complete58x26 source; exact family duplicate at(54,31) also potentially enters first screen. Both families have8 complete A13 instances, each composed of2 simultaneous static kind2 owners, not animation phases.

Inspect diagnostics/art_source/a13-grass-clumps/two-families-source-sheet-6x.png and separate complete source-composite/source-preview files. The two families have different silhouettes and no exact cross-familyRGBA frame alias. Keep original48x32 canvases/crop offsets, actual trimmed bounds, layer1, owner y and stable x-major order. Do not generate only the visible viewport fragment of the top241–242 instance.

Basal material reads are explicitly uncertain:239–240 local(21,24),(40,24), +/-3px;241–242 local(21,22),(34,22), +/-2px. These points lie on visible green material, not checker cast. They provide low-resolution placement landmarks; no woody root or unique physical ground contact is proved. Both complete species/family silhouettes and original cast should be reviewed before a future dual-asset sheet is generated. Do not invent a precise ground anchor from alpha bbox or cast tip.

Only source preparation here. No new materials, generation, runtime edits or visual gameplay acceptance. Future generated material/cast must be registered back to two owners per group and avoid duplicate shadows.
''')
 print(json.dumps({'groups':[{'id':g['id'],'size':g['composite_size'],'bounds':g['world_bounds_xyxy'],'instances':len(g['instances']),'first_screen_roots':g['first_screen_roots'],'feet':g['visible_basal_landmarks']}for g in groups]},ensure_ascii=False))
if __name__=='__main__':main()
