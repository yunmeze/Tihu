"""Extract original Item0 templates without executing the game or changing inputs."""
from pathlib import Path
import hashlib,json,struct,subprocess,re
from lp_original import Reader
P=Path(__file__).resolve().parents[1]; ROOT=P.parent
SOURCE=ROOT/'原版游戏/Data/Item0.lpRes'
def sha(b): return hashlib.sha256(b).hexdigest()
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def source(p):
 b=p.read_bytes();return {'path':str(p.relative_to(ROOT)),'sha256':sha(b),'bytes':len(b)}
def main():
 b=SOURCE.read_bytes();r=Reader(b,0);records=[];legacy=[];tail=None
 slots={7:['helmet'],8:['necklace'],9:['armor'],10:['boots'],11:['braceletLeft','braceletRight'],12:['ringLeft','ringRight'],13:['shield'],14:['weapon']}
 labels={0:'type',1:'icon_index',2:'appearance_1',3:'appearance_2',4:'hp',5:'mp',6:'attack_min',7:'attack_max',8:'tao_min',9:'tao_max',10:'magic_min',11:'magic_max',12:'defense_min',13:'defense_max',14:'magic_defense_min',15:'magic_defense_max',16:'fast_attack',17:'fast_cast',18:'physical_evade',19:'magic_evade',20:'accuracy',21:'freeze',22:'burn',23:'poison',24:'paralysis',25:'vampire',26:'reflect',27:'luck',30:'attached_skill_raw',31:'required_level',32:'required_attack',33:'required_tao',34:'required_magic',35:'forge_raw',36:'usage_counter_raw',37:'sale_factor_raw',38:'weight'}
 while r.pos<len(b):
  start=r.pos
  try:
   name=r.string()
   if not name or any(ord(c)<32 for c in name):raise ValueError('Invalid item name')
   words_at=r.pos;f=[r.short() for _ in range(39)];price_at=r.pos;price=r.long();reserved=r.short()
   if not -1<=f[0]<=100:raise ValueError('Invalid type')
  except Exception as e:
   tail={'source_offset':start,'bytes':len(b)-start,'raw_hex':b[start:].hex(),'reason':str(e),'interpreted':False};break
  rid=len(records)
  old=dict(id=rid,name=name,type=f[0],icon=f[1],appearance=f[2:4],hp=f[4],mp=f[5],attack=f[6:8],tao=f[8:10],magic=f[10:12],defense=f[12:14],magicDefense=f[14:16],weight=f[38],price=price,rawFields=f,reserved=reserved,sourceOffset=start)
  legacy.append(old)
  words=[]
  for i,value in enumerate(f):
   runtime=0x30+2*i if i<=27 else (0x6c if i in [28,29] else 0x70+2*(i-30))
   words.append({'index':i,'value':value,'source_offset':words_at+2*i,'encoded_hex':b[words_at+2*i:words_at+2*i+2].hex(),'meaning':labels.get(i),'runtime_offset_reference':runtime})
  records.append({**old,'placeholder':name=='0','sourceLength':r.pos-start,'raw_record_hex':b[start:r.pos].hex(),'raw_record_sha256':sha(b[start:r.pos]),'words':words,'name_field':{'source_offset':start,'encoded_length_bytes':words_at-start-4},'price_source_offset':price_at,'reserved_source_offset':price_at+4,'requirements':dict(zip(['level','attack','tao','magic'],f[31:35])),'compatible_slots_reference':slots.get(f[0],[]),'unknown_fields':{'raw28':f[28],'raw29':f[29],'reserved':reserved}})
 reference=ROOT/'参考项目/public/assets/data/items.json';expected=json.loads(reference.read_text());assert legacy==expected,'Reference catalogue differs'
 # Independent numerical decode at stored byte offsets (not Reader), and byte-exact round trip.
 rebuilt=bytearray(b[:10])
 for rec in records:
  rebuilt.extend(bytes.fromhex(rec['raw_record_hex']))
  for w in rec['words']:
   value=struct.unpack_from('<H',b,w['source_offset'])[0]^b[3];value=value-65536 if value&32768 else value
   assert value==w['value']
 if tail:rebuilt.extend(bytes.fromhex(tail['raw_hex']))
 assert bytes(rebuilt)==b
 refs=[ROOT/'参考项目/tools/extract-lp.py',ROOT/'参考项目/tools/inspect-refining.py',ROOT/'参考项目/tools/inspect-item-fields.py',ROOT/'参考项目/src/character.js',ROOT/'参考项目/src/native-stats.js',ROOT/'原版游戏/Help/Mod_2_1.htm',ROOT/'原版游戏/Help/Mod_2_2.htm']
 schema={'schema':'lp-original-item-templates-v1','source':source(SOURCE),'header_hex':b[:10].hex(),'xor_key':b[3],'disk_layout':'variable-length GB18030 name (u32 length), 39 signed 16-bit words, u32 price, signed16 reserved; numeric field XOR after unpack','record_count':len(records),'named_count':sum(not x['placeholder'] for x in records),'placeholder_count':sum(x['placeholder'] for x in records),'sources':[source(x) for x in refs],'semantics':'Raw values and offsets are verified directly; field meanings and runtime offsets are source-parser/reference-native-analysis interpretations. No game EXE was executed.','records':records,'uninterpreted_tail':tail}
 write(P/'data/items/catalogue.json',schema)
 adapter={'schema':'lp-catalogue-adapter-v1','catalogue':'res://data/items/catalogue.json','id_is_original_record_index':True,'ordinary_equipment_type_to_named_slots':{str(k):v for k,v in slots.items()},'slot_mapping_evidence':source(ROOT/'参考项目/src/character.js'),'native_numeric_slot_ids':None,'unresolved':['Native numeric slot IDs and appearance slots 13/14 require their own native slot contract; named shield/weapon type13/14 are item TYPES, not appearance SLOT13/14.'],'instance_rules':['Template is immutable; instance fieldOverrides/raw record values take precedence for weight, requirements and stats.','raw36 maps to runtime +0x7c usage counter; it is not heroAP or an aggregated attack value.','Keep unknown raw28/raw29/reserved. Loader reportedly writes raw28 then raw29 to +0x6c; do not silently merge them in the source catalogue.','Do not pack serialized template bytes as a 140-byte instance. Runtime name/pointer/layout data must have a separately verified schema.','Do not grant wood sword298 or potions automatically: the reference legacy fixture differs from normal creation.','Reject placeholder name0 as a usable item while retaining its original ID.']}
 adapter['inventory_state_adapter_proposal']={'contract': 'Dictionary[int, {weight:int, equipment_slots:Array[String], consumable:bool}]', 'weight': 'Use rawFields[38] when nonnegative; instance properties.weight overrides when supplied. Never derive from icon/type.', 'equipment_slots': 'Named list from ordinary_equipment_type_to_named_slots is reference-supported; numeric native slots remain a separate contract.', 'consumable': 'Unresolved by this data stage. Do not coerce unknown to false; build only an explicitly reviewed item subset or require an external verified consumption policy.', 'raw_proficiency': 'rawFields[36] may seed raw_proficiency only when the instance schema explicitly preserves original usage semantics, not heroAP.', 'initial_grants': 'No grants in catalogue adapter. Initial profile remains separate reference-derived evidence.'}
 write(P/'data/items/catalogue-adapter.json',adapter)
 # Static EXE disassembly only. Store addresses/raw spans and hashes, no execution.
 exe=ROOT/'原版游戏/LP传奇单机版_重生.exe';eb=exe.read_bytes();pe=struct.unpack_from('<I',eb,60)[0];base=struct.unpack_from('<I',eb,pe+52)[0];st=pe+24+struct.unpack_from('<H',eb,pe+20)[0]
 sections=[struct.unpack_from('<8sIIII',eb,st+40*i) for i in range(struct.unpack_from('<H',eb,pe+6)[0])]
 def off(va):return next(raw+va-base-rva for _,_,rva,size,raw in sections if base+rva<=va<base+rva+size)
 evidence=[]
 for name,lo,hi in [('item_loader',0x5a8660,0x5a8d50),('warrior_create',0x593085,0x593299),('taoist_create',0x5932b4,0x5934c8),('mage_create',0x5934e3,0x59374a)]:
  raw=eb[off(lo):off(hi)];dis=subprocess.check_output(['objdump','-d','-Mintel',f'--start-address={lo}',f'--stop-address={hi}',str(exe)],text=True)
  evidence.append({'name':name,'va_start':hex(lo),'va_end':hex(hi),'source_offset':off(lo),'bytes':len(raw),'sha256':sha(raw),'raw_hex':raw.hex(),'disassembly':dis.splitlines()[5:]})
 write(P/'data/items/native-static-evidence.json',{'source':source(exe),'method':'objdump static decoding; never executes EXE','ranges':evidence})
 profiles={'战士':{'hp':25,'mp':5,'attack':[1,3],'tao':[0,1],'magic':[0,1],'defense':[0,3],'magicDefense':[0,1],'accuracy':7,'capacity':25},'道士':{'hp':22,'mp':15,'attack':[0,2],'tao':[1,2],'magic':[0,2],'defense':[0,2],'magicDefense':[0,2],'accuracy':7,'capacity':22},'法师':{'hp':17,'mp':15,'attack':[0,1],'tao':[0,1],'magic':[1,3],'defense':[0,1],'magicDefense':[0,3],'accuracy':6,'capacity':20}}
 write(P/'data/items/initial-character-reference.json',{'schema':'lp-initial-character-reference-v1','status':'reference-derived profile; not a complete independently reconstructed native save','sources':[source(ROOT/'参考项目/src/character.js'),source(ROOT/'参考项目/tools/inspect-entry.py'),source(exe)],'native_creation_va':'0x591980','class_cached_totals_reference':profiles,'normal_creation_reference':{'armor_template_id':252,'inventory':[],'skills':[],'skill_points':1,'attribute_points':1},'initial_state_unknowns':{'heroAP':None,'full_native_record':None},'notes':['Class cached totals include starter cloth defense. Do not add cloth defense twice.','Legacy createCharacter fixture grants weapon and potions; createNewCharacter normal path does not.','Static EXE ranges supplied for further independent field verification; all class values here are explicitly attributed to the reference implementation.']})
 audit={'status':'PASS','records':len(records),'named':schema['named_count'],'placeholders':schema['placeholder_count'],'numeric_word_checks':39*len(records),'reference_records_equal':True,'full_byte_roundtrip_equal':True,'source_unchanged':sha(SOURCE.read_bytes())==sha(b),'tail_bytes':tail['bytes'] if tail else 0,'runtime_integrated':False,'special_items':{str(i):legacy[i] for i in [252,298,299]}}
 write(P/'diagnostics/items/extraction-validation.json',audit);print(json.dumps({k:v for k,v in audit.items() if k!='special_items'},ensure_ascii=False))
if __name__=='__main__':main()
