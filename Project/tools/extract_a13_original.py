"""Reproducible R1: native A13 cell records and only referenced original frame atlases.
Original/reference trees are read-only. No EXE, gameplay script, or reference main runs.
"""
from pathlib import Path
import json,hashlib,collections,argparse
from PIL import Image
from lp_original import Reader,read_pack,decode_frame,REFERENCE_PARSER_SHA256
P=Path(__file__).resolve().parents[1];ROOT=P.parent;SOURCE=ROOT/'原版游戏';OUT=P/'assets/original'
GROUPS={1:'Debris',2:'Plant',3:'Wall',4:'Building',5:'Dynamic'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def parse_map(path):
 data=path.read_bytes();r=Reader(data,3);name=r.string();home=[r.short(),r.short()];w,h=r.short(),r.short();assert 1<=w<=2000 and 1<=h<=2000
 grid=r.pos;cells=[];spawns=[];offsets=[]
 for x in range(w):
  for y in range(h):
   offsets.append(r.pos);c=[r.short()for _ in range(4)];cells.append(c)
   if c[2]==6:spawns.append({'x':x,'y':y,'monsterId':c[3],'name':r.string()})
 tail=r.pos;portals=[];count=r.short();assert 0<=count<=10000
 for _ in range(count):
  x,y,tx,ty=[r.short()for _ in range(4)];portals.append({'x':x,'y':y,'targetX':tx,'targetY':ty,'target':r.string()})
 npcs=[];count=r.short();assert 0<=count<=10000
 for _ in range(count):
  x,y,appearance,direction=[r.short()for _ in range(4)];npcs.append({'x':x,'y':y,'appearance':appearance,'direction':direction,'name':r.string(),'script':r.string()})
 load=r.string()if r.pos+4<=len(data)else''
 return {'schema':'lp-original-map-r1','id':path.stem,'name':name,'home':home,'width':w,'height':h,'cells':cells,'cellOrder':'x-major','cellFields':['floor','flag','kind','index'],'cellByteOffsets':offsets,'gridOffset':grid,'tailOffset':tail,'spawns':spawns,'portals':portals,'npcs':npcs,'loadScript':load,'unmappedTail':data[r.pos:].hex(),'source':'原版游戏/'+str(path.relative_to(SOURCE)),'sourceSha256':sha(path),'sourceBytes':len(data),'parsedBytes':r.pos,'tile_size':[48,32]}
def layer(flag):return 0 if flag in [1,-2] else 2 if flag==2 else 1

def main():
 m=parse_map(SOURCE/'Data/Map/A13.lpMap');req=collections.defaultdict(set)
 for floor,flag,kind,index in m['cells']:
  if floor:req['Map/Res/'+('FloorBig'if floor<0 else'FloorSmall')].add(abs(floor))
  if index>0 and kind in GROUPS:req['Map/Res/'+GROUPS[kind]].update(range(index,index+(5 if kind==5 else 1)))
  if index>0 and kind==8:req['Data4'].update(range(55,60))
 for n in m['npcs']:req['Npc'].update(range(1+n['appearance']*12+n['direction']*4,5+n['appearance']*12+n['direction']*4))
 packs={};reference_comp=[];refcache={};atlascache={}
 for name,indices in sorted(req.items()):
  src=SOURCE/'Data'/f'{name}.lpRes';data,records,animated,key=read_pack(src);directory=OUT/name;directory.mkdir(parents=True,exist_ok=True);frames={};pages=[];page=Image.new('RGBA',(2048,2048));x=y=row=0;pn=0;used=False
  def finish():
   nonlocal page,x,y,row,pn,used
   if used:
    file=directory/f'{pn}.png';page.save(file);pages.append({'file':'res://'+str(file.relative_to(P)),'size':[2048,2048],'sha256':sha(file)});pn+=1
   page=Image.new('RGBA',(2048,2048));x=y=row=0;used=False
  for i in sorted(indices):
   assert 0<=i<len(records),(name,i,len(records));im,meta=decode_frame(data,records[i],name,animated);box=tuple(meta['reference_extraction_bounds']);crop=im.crop(box);ww,hh=crop.size;assert ww+2<=2048 and hh+2<=2048
   if x+ww+2>2048:x=0;y+=row;row=0
   if y+hh+2>2048:finish()
   page.paste(crop,(x+1,y+1));frames[str(i)]={**meta,'page':pn,'rect':[x+1,y+1,ww,hh],'crop':[box[0],box[1]]};x+=ww+2;row=max(row,hh+2);used=True
   # Independently compare decoded pixels against the committed reference atlas when available.
   rp=ROOT/'参考项目/public/assets/sprites'/name/'index.json'
   if rp.exists():
    
    if str(rp)not in refcache:refcache[str(rp)]=json.load(open(rp))
    ref=refcache[str(rp)];rf=ref['frames'][i];ap=ROOT/'参考项目/public/assets'/ref['pages'][rf['page']]['file']
    if str(ap)not in atlascache:atlascache[str(ap)]=Image.open(ap).convert('RGBA')
    atlas=atlascache[str(ap)];xx,yy,rw,rh=rf['rect'];ri=atlas.crop((xx,yy,xx+rw,yy+rh));reference_comp.append({'pack':name,'index':i,'pixels_equal':ri.size==crop.size and ri.tobytes()==crop.tobytes(),'metadata_equal':rf['original']==meta['original']and rf['offset']==meta['offset']and rf['crop']==list(box[:2])})
  finish();packs[name]={'id':name,'source':'原版游戏/Data/'+name+'.lpRes','source_sha256':sha(src),'nativeAnimation':animated,'container_key':key,'total_source_records':len(records),'pages':pages,'frames':frames}
 floors=[];objects=[]
 for x in range(m['width']):
  for y in range(m['height']):
   floor,flag,kind,index=m['cells'][x*m['height']+y];base={'cell':[x,y],'flag':flag,'layer':layer(flag),'sort_y':y,'source_cell_offset':m['cellByteOffsets'][x*m['height']+y]}
   if floor:floors.append({**base,'pack':'Map/Res/'+('FloorBig'if floor<0 else'FloorSmall'),'index':abs(floor),'anchor_world':[48*x,32*y],'use_frame_offset':False})
   if index>0 and (kind in GROUPS or kind==8):
    name='Data4'if kind==8 else'Map/Res/'+GROUPS[kind];ids=list(range(55,60))if kind==8 else list(range(index,index+(5 if kind==5 else 1)));draw=[]
    for i in ids:
     f=packs[name]['frames'][str(i)];top=-52 if kind==8 else 32-f['original'][1];draw.append({'index':i,'top':top,'world_draw_origin':[48*x,32*y+top],'world_rgba_top_left':[48*x+f['crop'][0],32*y+top+f['crop'][1]]})
    objects.append({**base,'pack':name,'index':index,'kind':kind,'key':f'{name}:{index}:{x},{y}','frames':draw,'use_frame_offset':False})
 write(P/'diagnostics/maps/A13-placements.json',{'floors':floors,'objects':objects,'note':'Audit projection only; renderer can derive from unchanged native cells.'})
 m['render_contract']={'floor_first':True,'objects_sort':['layer','sort_y','stable_source_order'],'ordinary_object_top':'32-original_height; ignore frame offset; add crop offset','floor_origin':'cell*[48,32]; ignore frame offset; add crop offset','npc_origin':'cell*[48,32] + original frame offset + crop offset','npc_layer':1,'npc_ticks':17,'source_fps':50,'dynamic_ticks':8,'kind8_top':-52,'kind8_pingpong':[55,56,57,58,59,59,58,57,56,55],'kind6':'spawn record, not scenery','kind7':'NPC-list reference, not extra scenery','scripts_preserved_not_executed':True}
 refmap=ROOT/'参考项目/public/assets/maps/A13.json';mapmatch={}
 if refmap.exists():
  r=json.load(open(refmap));mapmatch={k:m[k]==r[k]for k in ['name','home','width','height','cells','spawns','portals','npcs','loadScript','unmappedTail','sourceSha256']};assert all(mapmatch.values()),mapmatch
 write(P/'diagnostics/maps/A13-reference-frame-comparison.json',reference_comp)
 assert all(c['pixels_equal']and c['metadata_equal']for c in reference_comp),'Reference atlas mismatch; see comparison JSON'
 manifest={'schema':'lp-original-textures-r1','packs':packs,'reference_parser':'参考项目/tools/extract-lp.py','reference_parser_sha256':REFERENCE_PARSER_SHA256,'alpha_policy':'Exact BMP black or palette-index0 transparency per reference; original checker RGB retained. No RGB remaster.','r1_map':'A13'}
 write(P/'data/maps/A13.json',m);write(OUT/'manifest.json',manifest);report={'status':'PASS','map_source_sha256':m['sourceSha256'],'map_dimensions':[m['width'],m['height']],'cells':len(m['cells']),'floors':len(floors),'objects':len(objects),'npcs':len(m['npcs']),'spawns':len(m['spawns']),'source_tail_bytes':len(m['unmappedTail'])//2,'packs':len(packs),'unique_frames':sum(len(q['frames'])for q in packs.values()),'pages':sum(len(q['pages'])for q in packs.values()),'reference_map_equality':mapmatch,'reference_frame_comparisons':len(reference_comp),'all_reference_frames_equal':all(c['pixels_equal']and c['metadata_equal']for c in reference_comp),'object_counts':dict(collections.Counter(o['pack']for o in objects)),'output_sha256':{'map':sha(P/'data/maps/A13.json'),'textures':sha(OUT/'manifest.json')}};write(P/'diagnostics/maps/A13-extraction-audit.json',report);print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
