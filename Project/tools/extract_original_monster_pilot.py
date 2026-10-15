"""Preserve native monster definitions; extract only A13's unique 彩蛋鸡 sprite pack."""
from pathlib import Path
import hashlib,json,re,struct
from PIL import Image
from lp_original import Reader,read_pack,decode_frame,REFERENCE_PARSER_SHA256
from extract_a13_original import parse_map
P=Path(__file__).resolve().parents[1];ROOT=P.parent;SRC=ROOT/'原版游戏'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def provenance(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def main():
 # Previous assets/data are hash-frozen; outputs are a new isolated scope.
 frozen={str(p):sha(p) for folder in ['assets/original','data/maps','data/items'] for p in (P/folder).rglob('*') if p.is_file() and '.import'not in p.suffix and 'monsters/a13-chicken'not in str(p)}
 src=SRC/'Data/Mon/0.lpRes';b=src.read_bytes();r=Reader(b,6);records=[];canonical=[];tail=None;wordchecks=0
 while r.pos<len(b):
  start=r.pos;fields=[]
  def get(name,kind):
   off=r.pos;v=r.string() if kind=='string' else r.short() if kind=='signed16' else r.number('<f');fields.append({'name':name,'source_offset':off,'source_end':r.pos,'encoding':kind,'value':v,'encoded_hex':b[off:r.pos].hex()});return v
  try:
   name=get('name','string');sound=get('sound','string')
   if not name or any(ord(c)<32 for c in name):raise ValueError('Invalid monster name')
   f=[get('rawFields['+str(i)+']','signed16')for i in range(11)];speed=get('speed','float32_le_unkeyed');extra=[get('rawExtra['+str(i)+']','signed16')for i in range(11)];drops=get('drops','string');color=[get('color['+str(i)+']','signed16')for i in range(4)];exp=get('experience','signed16');event=get('event','string')
   if not 0<=f[0]<1000 or f[3]<0 or not 0<=speed<50:raise ValueError('Invalid monster record')
  except Exception as e:tail={'source_offset':start,'bytes':len(b)-start,'raw_hex':b[start:].hex(),'reason':str(e)};break
  rules=[]
  for token in drops.split():
   match=re.match(r'^(.*?)(\d+)/(\d+)$',token)
   if match:rules.append({'item':match[1],'quantity':int(match[2]),'denominator':int(match[3])})
  old=dict(id=len(records),name=name,sound=sound,appearance=f[0],death=f[1],attackKind=f[2],hp=f[3],regenFrames=f[4],attack=f[5],defense=f[6],magicDefense=f[7],physicalEvade=f[8],magicEvade=f[9],vision=f[10],speed=speed,attackFrames=extra[0],paralysis=extra[1],poison=extra[2],freeze=extra[3],burn=extra[4],behavior=extra[7],rawExtra=extra,event=event,drops=drops,dropRules=rules,color=color,experience=exp,description='',sourceOffset=start)
  canonical.append(old);records.append({**old,'rawFields':f,'sourceLength':r.pos-start,'raw_record_hex':b[start:r.pos].hex(),'fields':fields,'unknown_extra_indices':{str(i):extra[i]for i in [5,6,8,9,10]},'description_status':'not serialized by reference parser; empty reference compatibility value only'})
  for field in fields:
   if field['encoding']=='signed16':
    v=struct.unpack_from('<H',b,field['source_offset'])[0]^(b[3]^6);v=v-65536 if v&32768 else v;assert v==field['value'];wordchecks+=1
 reference=ROOT/'参考项目/public/assets/data/monsters.json';assert canonical==json.loads(reference.read_text())
 assert b[:10]+b''.join(bytes.fromhex(x['raw_record_hex'])for x in records)+(bytes.fromhex(tail['raw_hex'])if tail else b'')==b
 write(P/'data/monsters/definitions.json',{'schema':'lp-original-monster-definitions-v1','source':provenance(src),'parser':provenance(ROOT/'参考项目/tools/extract-lp.py'),'header_hex':b[:10].hex(),'xor_key':b[3]^6,'records':records,'uninterpreted_tail':tail,'scope':'Source bytes and reference field names preserved. No AI, spawn, combat, drop RNG or runtime behavior implemented.'})
 m=parse_map(SRC/'Data/Map/A13.lpMap');assert m['loadScript']==json.loads((P/'data/maps/A13.json').read_text())['loadScript']
 calls=re.findall(r'^#addmon\s+(\d+)\s+(\d+)\s+(.+?)\s*$',m['loadScript'],re.I|re.M);assert calls==[('49','53','彩蛋鸡')],calls
 matches=[x for x in records if x['name']==calls[0][2]];assert len(matches)==1
 mon=matches[0];name='Mon/'+str(mon['appearance']);srcpack=SRC/'Data'/f'{name}.lpRes';data,packrecords,animated,key=read_pack(srcpack)
 assert len(packrecords)>=217
 out=P/'assets/original/monsters/a13-chicken';out.mkdir(parents=True,exist_ok=True);frames={};pages=[];page=Image.new('RGBA',(2048,2048));x=y=row=0;pn=0;used=False;comparisons=[];cache={}
 ref=json.loads((ROOT/'参考项目/public/assets/sprites'/name/'index.json').read_text())
 def finish():
  nonlocal page,x,y,row,pn,used
  if used:
   path=out/f'{pn}.png';page.save(path);pages.append({'file':'res://'+str(path.relative_to(P)),'size':[2048,2048],'sha256':sha(path)});pn+=1
  page=Image.new('RGBA',(2048,2048));x=y=row=0;used=False
 for i in range(217):
  im,meta=decode_frame(data,packrecords[i],name,animated);box=meta['reference_extraction_bounds'];crop=im.crop(box);w,h=crop.size
  assert w+2<=2048 and h+2<=2048
  if x+w+2>2048:x=0;y+=row;row=0
  if y+h+2>2048:finish()
  page.paste(crop,(x+1,y+1));frames[str(i)]={**meta,'page':pn,'rect':[x+1,y+1,w,h],'crop':box[:2]};x+=w+2;row=max(row,h+2);used=True
  rf=ref['frames'][i];af=ROOT/'参考项目/public/assets'/ref['pages'][rf['page']]['file']
  if str(af)not in cache:cache[str(af)]=Image.open(af).convert('RGBA')
  xx,yy,ww,hh=rf['rect'];ri=cache[str(af)].crop((xx,yy,xx+ww,yy+hh));assert ri.size==crop.size and ri.tobytes()==crop.tobytes();assert rf['offset']==meta['offset']and rf['original']==meta['original']and rf['crop']==box[:2];comparisons.append(i)
 finish()
 manifest={'schema':'lp-original-textures-r1','map':'A13-chicken','packs':{name:{'id':name,'source':'原版游戏/Data/'+name+'.lpRes','source_sha256':sha(srcpack),'nativeAnimation':animated,'container_key':key,'total_source_records':len(packrecords),'pages':pages,'frames':frames}},'reference_parser_sha256':REFERENCE_PARSER_SHA256,'alpha_policy':'Same native exact-black color key and reference pre-normalization crop as shared lp_original; checker shadows retained.'}
 write(out/'manifest.json',manifest)
 clips={'idle':(1,4,.96),'walk':(33,6,.48),'attack':(81,6,.48),'death':(129,10,1.2)}
 actions={k:{'base':base,'count_per_direction':count,'reference_duration_seconds':sec,'directions':{str(d):list(range(base+d*count,base+(d+1)*count))for d in range(8)}}for k,(base,count,sec)in clips.items()}
 pilot={'schema':'lp-a13-monster-pilot-v1','definition_id':mon['id'],'name':mon['name'],'appearance':mon['appearance'],'pack':name,'texture_manifest':'res://'+str((out/'manifest.json').relative_to(P)),'definition_source_offset':mon['sourceOffset'],'definition_source_length':mon['sourceLength'],'map_source':provenance(SRC/'Data/Map/A13.lpMap'),'load_script':m['loadScript'],'load_script_sha256_utf8':hashlib.sha256(m['loadScript'].encode()).hexdigest(),'addmon':{'cell':[49,53],'name':mon['name'],'resolved_id':mon['id'],'name_matches':len(matches),'guard_text':'#if rnd < 5','execution_status':'not executed; RNG semantics belong to VM'},'actions_reference':actions,'corpse_reference_indices':list(range(209,217)),'frame0':'preserved source frame, not treated as an idle action','action_schema_evidence':provenance(ROOT/'参考项目/src/animation.js'),'timing_status':'Reference animation mapping only; not independently verified original EXE lifecycle. attackFrames50 is retained separately, not overwritten by generic reference duration.','unknowns':{'native_spawn_initial_direction':None,'native_spawn_layer':None,'native_action_lifecycle':None},'runtime_integrated':False}
 write(P/'data/monsters/a13-chicken.json',pilot)
 for p,h in frozen.items():assert sha(Path(p))==h,p
 report={'status':'PASS','definition_count':len(records),'definition_reference_equal':True,'raw_roundtrip_equal':True,'numeric_word_checks':wordchecks,'tail_bytes':tail['bytes']if tail else 0,'name_match_count':len(matches),'monster_id':mon['id'],'appearance':mon['appearance'],'frames':len(frames),'reference_frame_rgba_metadata_checks':len(comparisons),'pages':len(pages),'frozen_files_unchanged':len(frozen),'runtime_integrated':False}
 write(P/'diagnostics/monsters/a13-chicken-validation.json',report);print(json.dumps(report))
if __name__=='__main__':main()
