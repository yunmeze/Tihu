"""Rebuild one original A13 temple group and its evidence. No art generation/runtime edits."""
from pathlib import Path
import json,hashlib,collections
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1];ROOT=P.parent
OUT=P/'art_source/a13_main_temple_source';DIAG=P/'diagnostics/art_source/a13-main-temple'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
 OUT.mkdir(parents=True,exist_ok=True);DIAG.mkdir(parents=True,exist_ok=True)
 mp=P/'data/maps/A13.json';mf=P/'assets/original/manifest.json';m=json.loads(mp.read_text());pack=json.loads(mf.read_text())['packs']['Map/Res/Building'];pages={i:Image.open(P/x['file'][6:]).convert('RGBA')for i,x in enumerate(pack['pages'])};owners=[];images={}
 for index,c in enumerate(m['cells']):
  if c[2]!=4 or not 3966<=c[3]<=3995:continue
  x,y=index//m['height'],index%m['height'];f=pack['frames'][str(c[3])];layer=0 if c[1]in [1,-2]else 2 if c[1]==2 else 1;wx=x*48+f['crop'][0];wy=y*32+32-f['original'][1]+f['crop'][1];rx,ry,w,h=f['rect'];im=pages[f['page']].crop((rx,ry,rx+w,ry+h));images[c[3]]=im
  owners.append({'key':f'Building:{c[3]}@{x},{y}','cell':[x,y],'cell_linear_index':index,'source_map_byte_offset':m['cellByteOffsets'][index],'source_cell':c,'pack':'Map/Res/Building','frame_index':c[3],'flag':c[1],'layer':layer,'sort_y':y,'stable_source_order':index,'original_canvas':f['original'],'source_frame_offset_ignored':f['offset'],'crop':f['crop'],'atlas_page':pack['pages'][f['page']]['file'],'atlas_rect':f['rect'],'world_rect':[wx,wy,w,h],'native_source_offset':f['sourceOffset'],'native_source_bytes':f['sourceBytes'],'visible_alpha_pixels':sum(v>0 for v in im.getchannel('A').tobytes())})
 assert len(owners)==30 and sorted(o['frame_index']for o in owners)==list(range(3966,3996))
 owners.sort(key=lambda o:(o['layer'],o['sort_y'],o['stable_source_order']))
 b=[min(o['world_rect'][0]for o in owners),min(o['world_rect'][1]for o in owners),max(o['world_rect'][0]+o['world_rect'][2]for o in owners),max(o['world_rect'][1]+o['world_rect'][3]for o in owners)];size=(b[2]-b[0],b[3]-b[1]);composite=Image.new('RGBA',size);layers={0:Image.new('RGBA',size),1:Image.new('RGBA',size),2:Image.new('RGBA',size)}
 for order,o in enumerate(owners):
  o['group_draw_order']=order;wx,wy,w,h=o['world_rect'];xy=(wx-b[0],wy-b[1]);im=images[o['frame_index']];composite.alpha_composite(im,xy);layers[o['layer']].alpha_composite(im,xy)
 composite.save(DIAG/'source-composite.png')
 bg=Image.new('RGBA',size,(100,110,100,255));bg.alpha_composite(composite);bg.convert('RGB').save(DIAG/'source-preview.jpg')
 # Human-read visible material landmarks, not a solved 3-D model or registration fit.
 anchors=[('C0_front_column_foot',437,553,4,'white corner column cut bottom; not front railing post or stone apron'),('S0_left_stair_ground_edge',258,543,5,'front lower stone tread edge; adjacent grass excluded'),('S1_left_stair_top',231,455,5,'upper tread/platform junction, partly bordered by railing'),('S2_right_stair_ground_edge',596,578,5,'lowest right stone tread edge; adjacent grass excluded'),('S3_right_stair_top',622,489,5,'upper right tread/platform junction'),('E0_left_eave_lip',43,209,4,'visible upturned wooden eave lip sample, not extreme tip or ground foot'),('E1_front_eave_corner',437,472,4,'front eave end above corner column, not its foot'),('E2_right_eave_lip',733,281,4,'visible right wooden eave lip sample, not a claimed extremal tip')]
 points=[];board=bg.copy();draw=ImageDraw.Draw(board);local=Image.new('RGB',(4*180,2*180),(65,75,70));ld=ImageDraw.Draw(local)
 for n,(ident,x,y,unc,note)in enumerate(anchors):
  contributors=[]
  for o in owners:
   wx,wy,w,h=o['world_rect'];px=x+b[0]-wx;py=y+b[1]-wy
   if 0<=px<w and 0<=py<h and images[o['frame_index']].getpixel((px,py))[3]>0:contributors.append(o['key'])
  assert contributors,(ident,x,y)
  points.append({'id':ident,'source_composite_xy':[x,y],'world_xy':[x+b[0],y+b[1]],'manual_read_uncertainty_px':unc,'read_region_xyxy':[x-unc,y-unc,x+unc,y+unc],'alpha_at_point':composite.getpixel((x,y))[3],'material_interpretation':note,'contributors_in_draw_order':contributors,'certainty':'visible feature with finite pixel region; not exact surveyed coordinate'})
  draw.ellipse((x-4,y-4,x+4,y+4),outline=(20,255,240,255),width=2);draw.text((x+6,y-8),ident.split('_')[0],fill='white')
  crop=bg.crop((x-26,y-26,x+27,y+27)).resize((159,159),Image.Resampling.NEAREST).convert('RGB');cx=(n%4)*180;cy=(n//4)*180;local.paste(crop,(cx,cy+18));ld.text((cx+3,cy+2),ident.split('_')[0]+f' ({x},{y}) +/-{unc}',fill='white');ld.rectangle((cx+78,cy+96,cx+83,cy+101),outline='cyan',width=1)
 board.convert('RGB').save(DIAG/'source-landmark-board.jpg');local.save(DIAG/'source-landmark-local-board.png')
 layerboard=Image.new('RGB',(size[0]*2,size[1]),(100,110,100));
 for j,l in enumerate([0,1]):
  base=Image.new('RGBA',size,(100,110,100,255));base.alpha_composite(layers[l]);layerboard.paste(base.convert('RGB'),(j*size[0],0))
 layerboard.thumbnail((1200,600));layerboard.save(DIAG/'source-layer0-layer1.jpg')
 nearby=[{k:n[k]for k in ['x','y','name','appearance','direction']}for n in m['npcs']if 59<=n['x']<=78 and 30<=n['y']<=41]
 contract={'schema':'a13-main-temple-original-group-v1','status':'source preparation only; generated building and registration not yet approved','map_source_sha256':m['sourceSha256'],'map_json_sha256':sha(mp),'texture_manifest_sha256':sha(mf),'building_resource_source_sha256':pack['source_sha256'],'frame_range':[3966,3995],'owner_count':len(owners),'layer_counts':dict(collections.Counter(o['layer']for o in owners)),'world_bounds_xyxy':b,'composite_size':list(size),'coordinate_contract':m['render_contract'],'owners_in_draw_order':owners,'manual_visible_landmarks':points,'nearby_original_npcs':nearby,'limits':['Landmarks are material-specific manual read regions, uncertainty 4-5 source pixels. No zero-error geometry claim.','Source has baked checker cast and grass/stone apron. They are visible evidence, not structural foot anchors or desired generated ground.','Two stair/platform directions and compound roofs are distinct planes. A global affine fit cannot prove their separate correspondence.','Layer0 support owners must remain ahead of original layer1 actor depth; never put whole generated building in one background/foreground sprite.','No collisions, flags, cells, NPC scripts or runtime changed.','Nearby actor routes and landing visibility require runtime evidence after any generated candidate exists.']}
 write(OUT/'source-group-contract.json',contract);print(json.dumps({'owners':30,'layers':contract['layer_counts'],'bounds':b,'size':size,'nearby_npcs':nearby,'contract_sha256':sha(OUT/'source-group-contract.json')}))
if __name__=='__main__':main()
