"""Add one native map and its missing frame textures without modifying previous stages."""
from pathlib import Path
import argparse,copy,json,hashlib,collections
from PIL import Image
from lp_original import Reader,read_pack,decode_frame,REFERENCE_PARSER_SHA256
from extract_a13_original import parse_map,layer,P,ROOT,SOURCE,GROUPS,write,sha

def main():
 ap=argparse.ArgumentParser();ap.add_argument('map_id',choices=['A00','A01','A02']);ap.add_argument('--base',default='assets/original/manifest.json');args=ap.parse_args();mid=args.map_id;basepath=P/args.base;base=json.load(open(basepath));frozen={str(basepath):sha(basepath),str(P/'data/maps/A13.json'):sha(P/'data/maps/A13.json')}
 for pack in base['packs'].values():
  for page in pack['pages']:
   f=P/page['file'].removeprefix('res://');frozen[str(f)]=sha(f)
 m=parse_map(SOURCE/f'Data/Map/{mid}.lpMap');m['schema']='lp-original-map-r1';req=collections.defaultdict(set)
 for floor,flag,kind,index in m['cells']:
  if floor:req['Map/Res/'+('FloorBig'if floor<0 else'FloorSmall')].add(abs(floor))
  if index>0 and kind in GROUPS:req['Map/Res/'+GROUPS[kind]].update(range(index,index+(5 if kind==5 else 1)))
  if index>0 and kind==8:req['Data4'].update(range(55,60))
 for n in m['npcs']:req['Npc'].update(range(1+n['appearance']*12+n['direction']*4,5+n['appearance']*12+n['direction']*4))
 packs=copy.deepcopy(base['packs']);out=P/'assets/original/maps'/mid;refcache={};atlascache={};comparisons=[];newcount=0;newpages=0;requests={}
 for name,ids in sorted(req.items()):
  src=SOURCE/'Data'/f'{name}.lpRes';data,records,animated,key=read_pack(src)
  if name in packs:assert packs[name]['source_sha256']==sha(src)
  else:packs[name]={'id':name,'source':'原版游戏/Data/'+name+'.lpRes','source_sha256':sha(src),'nativeAnimation':animated,'container_key':key,'total_source_records':len(records),'pages':[],'frames':{}}
  pack=packs[name];missing=sorted(ids-set(map(int,pack['frames'])));requests[name]={'required':sorted(ids),'new':missing,'reused':sorted(ids-set(missing))};directory=out/'sprites'/name;directory.mkdir(parents=True,exist_ok=True);page=Image.new('RGBA',(2048,2048));x=y=row=0;pn=len(pack['pages']);used=False
  def finish():
   nonlocal page,x,y,row,pn,used,newpages
   if used:
    f=directory/f'{pn}.png';page.save(f);pack['pages'].append({'file':'res://'+str(f.relative_to(P)),'size':[2048,2048],'sha256':sha(f)});pn+=1;newpages+=1
   page=Image.new('RGBA',(2048,2048));x=y=row=0;used=False
  for i in missing:
   assert 0<=i<len(records),(name,i);im,meta=decode_frame(data,records[i],name,animated);box=tuple(meta['reference_extraction_bounds']);crop=im.crop(box);w,h=crop.size;assert w+2<=2048 and h+2<=2048
   if x+w+2>2048:x=0;y+=row;row=0
   if y+h+2>2048:finish()
   page.paste(crop,(x+1,y+1));pack['frames'][str(i)]={**meta,'page':pn,'rect':[x+1,y+1,w,h],'crop':list(box[:2])};x+=w+2;row=max(row,h+2);used=True;newcount+=1
   rp=ROOT/'参考项目/public/assets/sprites'/name/'index.json'
   if rp.exists():
    if str(rp)not in refcache:refcache[str(rp)]=json.load(open(rp))
    ref=refcache[str(rp)];rf=ref['frames'][i];af=ROOT/'参考项目/public/assets'/ref['pages'][rf['page']]['file']
    if str(af)not in atlascache:atlascache[str(af)]=Image.open(af).convert('RGBA')
    xx,yy,rw,rh=rf['rect'];ri=atlascache[str(af)].crop((xx,yy,xx+rw,yy+rh));comparisons.append({'pack':name,'index':i,'pixels_equal':ri.size==crop.size and ri.tobytes()==crop.tobytes(),'metadata_equal':rf['original']==meta['original']and rf['offset']==meta['offset']and rf['crop']==list(box[:2])})
  finish()
 assert all(c['pixels_equal']and c['metadata_equal']for c in comparisons)
 for f,h in frozen.items():assert sha(Path(f))==h,('Frozen input modified',f)
 # Explicit byte locations for preserved portal/NPC/load-script records.
 raw=(SOURCE/f'Data/Map/{mid}.lpMap').read_bytes();r=Reader(raw,3,start=m['tailOffset']);count=r.short();portalrecords=[]
 for i in range(count):
  start=r.pos;coords=[r.short()for _ in range(4)];target=r.string();portalrecords.append({'record_index':i,'source_offset':start,'source_end':r.pos,**m['portals'][i]})
 count=r.short();npcrecords=[]
 for i in range(count):
  start=r.pos;vals=[r.short()for _ in range(4)];name=r.string();script_offset=r.pos;script=r.string();n=m['npcs'][i];assert script==n['script'];npcrecords.append({'record_index':i,'source_offset':start,'script_field_offset':script_offset,'source_end':r.pos,**n,'frame_indices':list(range(1+n['appearance']*12+n['direction']*4,5+n['appearance']*12+n['direction']*4)),'script_sha256_utf8':hashlib.sha256(script.encode()).hexdigest()})
 load_offset=r.pos;load=r.string();assert load==m['loadScript'];index={'schema':'lp-original-entity-text-index-v1','map':mid,'source_sha256':m['sourceSha256'],'portals':portalrecords,'npcs':npcrecords,'spawns':m['spawns'],'load_script':{'field_offset':load_offset,'source_end':r.pos,'text':load,'sha256_utf8':hashlib.sha256(load.encode()).hexdigest()},'scope':'Original scripts preserved only; no VM, story execution, monster art or runtime integration in this extraction stage.'}
 m['texture_manifest']='res://'+str((out/'manifest.json').relative_to(P));m['entity_index']='res://data/maps/'+mid+'-entities.json';m['render_contract']=json.load(open(P/'data/maps/A13.json'))['render_contract'];manifest={'schema':'lp-original-textures-r1','packs':packs,'base_manifest':'res://'+str(basepath.relative_to(P)),'base_manifest_sha256':sha(basepath),'map':mid,'required_frames':requests,'alpha_policy':base['alpha_policy'],'reference_parser_sha256':REFERENCE_PARSER_SHA256}
 write(P/'data/maps'/f'{mid}.json',m);write(P/'data/maps'/f'{mid}-entities.json',index);write(out/'manifest.json',manifest)
 counts=collections.Counter(GROUPS[c[2]]if c[2]in GROUPS else'Data4'for c in m['cells']if c[3]>0 and(c[2]in GROUPS or c[2]==8));report={'status':'PASS','map':mid,'dimensions':[m['width'],m['height']],'cells':len(m['cells']),'floor_placements':sum(bool(c[0])for c in m['cells']),'object_counts':dict(counts),'npc_records':len(m['npcs']),'portals':len(m['portals']),'spawns':len(m['spawns']),'new_frames':newcount,'new_atlas_pages':newpages,'reused_required_frames':sum(len(x['reused'])for x in requests.values()),'new_reference_frame_comparisons':len(comparisons),'all_reference_pixels_metadata_equal':True,'frozen_files_unchanged':len(frozen),'source_tail_bytes':len(m['unmappedTail'])//2,'runtime_integrated':False,'sha256':{'map':sha(P/'data/maps'/f'{mid}.json'),'entity_index':sha(P/'data/maps'/f'{mid}-entities.json'),'texture_manifest':sha(out/'manifest.json')}}
 refmap=json.load(open(ROOT/'参考项目/public/assets/maps'/f'{mid}.json'));report['reference_map_equality']={k:m[k]==refmap[k]for k in ['name','home','width','height','cells','spawns','portals','npcs','loadScript','unmappedTail','sourceSha256']};assert all(report['reference_map_equality'].values())
 write(P/'diagnostics/maps'/f'{mid}-incremental-extraction-audit.json',report);write(P/'diagnostics/maps'/f'{mid}-reference-frame-comparison.json',comparisons);print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
