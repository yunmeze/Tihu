#!/usr/bin/env python3
"""Static A01 source contract. Only reads --repo; writes exclusively --out.
Python 3 stdlib + GNU objdump. Does not import repository modules, launch EXE,
launch Godot, create resources, install packages, or touch Git state.
"""
from pathlib import Path
import argparse, collections, hashlib, json, re, struct, subprocess

HERE = Path(__file__).resolve().parents[1]
EXE = '原版游戏/LP传奇单机版_重生.exe'
MAP = '原版游戏/Data/Map/A01.lpMap'
MON = '原版游戏/Data/Mon/0.lpRes'
RANGES = {
    'map_binding': (0x59e5cc, 0x59e855),
    'name_lookup': (0x5a0330, 0x5a0447),
    'definition_loader': (0x5a8ee0, 0x5a988b),
    'entity_definition_copy': (0x5a0960, 0x5a0b75),
    'special_888_prefix': (0x5a0eb5, 0x5a111f),
    'string_reader': (0x634cb0, 0x634e1a),
}
# Byte strings are the reviewed instructions, not regenerated expectations.
ANCHORS = {
    0x59e5df: ('833cca06', 'kind == 6 gate'),
    0x59e5e9: ('e8c2660900', 'read serialized spawn name via 0x634cb0'),
    0x59e604: ('e8271d0000', 'call name lookup 0x5a0330'),
    0x59e610: ('ff1504124000', '__vbaI4Var converts lookup result'),
    0x59e62d: ('8944d104', 'overwrite cell cached index with lookup result'),
    0x59e660: ('0f8ec8010000', 'nonpositive ID skips creation via 0x59e82e'),
    0x59e71b: ('668994c88c000000', 'store resolved ID into entity +0x8c'),
    0x59e7e0: ('e87b210000', 'call entity initialization 0x5a0960'),
    0x59e82e: ('c70000000000', 'failed lookup clears kind'),
    0x5a0359: ('8b3d0c114000', 'edi = __vbaStrCmp IAT'),
    0x5a0367: ('b801000000', 'lookup starts at native ID 1'),
    0x5a036f: ('b958020000', 'lookup upper bound 600'),
    0x5a0382: ('c1e6052bf0', 'native ID multiplied by 31'),
    0x5a038c: ('c1e602', 'multiply by 4: record stride 124'),
    0x5a0393: ('68b8ed4000', 'compare candidate database name to BSTR zero'),
    0x5a03aa: ('68e0ba4000', 'compare candidate database name to empty BSTR'),
    0x5a03bb: ('7425', 'sentinel terminates search, does not skip record'),
    0x5a03cd: ('ffd7', 'compare query to candidate via __vbaStrCmp'),
    0x5a03d1: ('7418', 'first exact match jumps to return ID'),
    0x5a03e2: ('c745d400000000', 'sentinel result integer zero'),
    0x5a03eb: ('668b55ec668955d4', 'return matched loop index'),
    0x5a9032: ('be01000000', 'definition loader starts record index at 1'),
    0x5a9037: ('b858020000', 'definition loader ends at 600'),
    0x5a904a: ('b820000000', '32 serialized fields per definition'),
    0x5a906f: ('e83cbc0800', 'first field reads name string'),
    0x5a9082: ('c1e1052bc8', 'loader uses native record index times 31'),
    0x5a9087: ('a114026400', 'loader and lookup share table 0x640214'),
    0x5a908c: ('8d0c88', 'name destination table + 124 * native ID'),
    0x5a9114: ('89548808', 'appearance raw field goes to definition +8'),
    0x5a9818: ('b80100000003f0', 'next record index +1, no sparse ID read'),
    0x5a099d: ('0fbf868c000000', 'read entity resolved native ID +0x8c'),
    0x5a0a91: ('8b540808895608', 'definition +8 copied to entity appearance +8'),
    0x5a0eb5: ('3d78030000', '888 special appearance gate'),
    0x5a0ec7: ('3d78030000', '888-specific branch'),
    0x5a0ef2: ('ff15ac104000', '888 path calls MSVBVM60 ordinal 593 (RNG identification is prior context)'),
    0x5a0f38: ('66ff0d74ed6300', 'special path can decrement entity count'),
    0x5a0f5f: ('c704c800000000', 'special path can clear occupied cell'),
}


def sha(b): return hashlib.sha256(b).hexdigest()
def write(p, v):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(v, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def load(p): return json.loads(p.read_text(encoding='utf-8'))

class Reader:
    def __init__(self, b, kind): self.b, self.key, self.pos = b, b[3] ^ kind, 10
    def number(self, fmt):
        n = struct.calcsize(fmt)
        assert self.pos + n <= len(self.b)
        v = struct.unpack_from(fmt, self.b, self.pos)[0]; self.pos += n
        if fmt == '<f': return v
        v ^= self.key
        if fmt == '<H' and v & 0x8000: v -= 65536
        return v
    def short(self): return self.number('<H')
    def string(self):
        n = self.number('<I'); assert 0 <= n <= 2000000 and self.pos+n <= len(self.b)
        s = bytes(x ^ self.key for x in self.b[self.pos:self.pos+n]).decode('gb18030')
        self.pos += n; return s


def parse_map(b):
    r=Reader(b,3); name=r.string(); home=[r.short(),r.short()]; w,h=r.short(),r.short()
    grid=r.pos; cells=[]; offsets=[]; spawns=[]; pins=[]
    for x in range(w):
        for y in range(h):
            start=r.pos; offsets.append(start); c=[r.short() for _ in range(4)]; cells.append(c)
            if c[2] == 6:
                ns=r.pos; s=r.string(); spawn={'x':x,'y':y,'monsterId':c[3],'name':s};spawns.append(spawn)
                pins.append({'source_spawn_index':len(spawns)-1,'cell_index_x_major':x*h+y,
                    'source_cell_offset':start,'source_name_field_offset':ns,'source_record_end':r.pos,
                    'encoded_record_hex':b[start:r.pos].hex(),'record_sha256':sha(b[start:r.pos])})
    tail=r.pos; portals=[]
    for i in range(r.short()):
        x,y,tx,ty=[r.short() for _ in range(4)]; portals.append({'x':x,'y':y,'targetX':tx,'targetY':ty,'target':r.string()})
    npcs=[]
    for i in range(r.short()):
        x,y,a,d=[r.short() for _ in range(4)]; npcs.append({'x':x,'y':y,'appearance':a,'direction':d,'name':r.string(),'script':r.string()})
    load_start=r.pos; script=r.string(); end=r.pos
    return dict(name=name,home=home,width=w,height=h,gridOffset=grid,tailOffset=tail,
        cells=cells,cellByteOffsets=offsets,spawns=spawns,portals=portals,npcs=npcs,
        loadScript=script,unmappedTail=b[end:].hex(),parsedBytes=end,sourceBytes=len(b),sourceSha256=sha(b)), pins, {'field_offset':load_start,'source_end':end,'text':script,'sha256_utf8':sha(script.encode())}


def parse_definitions(b):
    r=Reader(b,6); records=[]
    for i in range(600):
        start=r.pos; fields=[]
        def get(name, kind):
            off=r.pos
            v=r.string() if kind=='string' else r.short() if kind=='signed16' else r.number('<f')
            fields.append({'name':name,'source_offset':off,'source_end':r.pos,'encoding':kind,'value':v,'encoded_hex':b[off:r.pos].hex()})
            return v
        name=get('name','string');sound=get('sound','string')
        raw=[get(f'rawFields[{k}]','signed16') for k in range(11)]
        speed=get('speed','float32_le_unkeyed')
        extra=[get(f'rawExtra[{k}]','signed16') for k in range(11)]
        drops=get('drops','string');color=[get(f'color[{k}]','signed16') for k in range(4)]
        exp=get('experience','signed16');event=get('event','string')
        records.append(dict(id=i,name=name,sound=sound,appearance=raw[0],rawFields=raw,speed=speed,
            rawExtra=extra,drops=drops,color=color,experience=exp,event=event,sourceOffset=start,
            sourceLength=r.pos-start,raw_record_hex=b[start:r.pos].hex(),fields=fields))
    assert b[:10]+b''.join(bytes.fromhex(x['raw_record_hex']) for x in records)+b[r.pos:] == b
    return records, {'source_offset':r.pos,'bytes':len(b)-r.pos,'sha256':sha(b[r.pos:])}


def resolve_name(name, records):
    """Reconstructed static model, not an execution of VB6 or the original EXE."""
    for native_id, record in enumerate(records[:600],1):
        candidate=record['name']
        if candidate in ('','0'): return 0
        if candidate == name: return native_id
    return 0


def pe_info(b):
    p=struct.unpack_from('<I',b,0x3c)[0];assert b[p:p+4]==b'PE\0\0'
    machine,n=struct.unpack_from('<HH',b,p+4); opt=p+24
    assert machine == 0x14c and struct.unpack_from('<H',b,opt)[0] == 0x10b
    base=struct.unpack_from('<I',b,opt+28)[0]
    start=opt+struct.unpack_from('<H',b,p+20)[0];sections=[]
    for i in range(n):
        name,vs,rva,rs,off=struct.unpack_from('<8sIIII',b,start+i*40)
        sections.append({'name':name.rstrip(b'\0').decode(),'virtual_size':vs,'rva':rva,'raw_size':rs,'raw_offset':off})
    def offset(va):
        for s in sections:
            rva=va-base
            if s['rva'] <= rva < s['rva']+s['raw_size']:return s['raw_offset']+rva-s['rva']
        raise ValueError(hex(va))
    return {'machine':'i386','optional_header':'PE32','image_base':hex(base),'sections':sections},offset


def pack_table(b):
    """Validate native animated image table only; do not decode or invent clips."""
    key=b[3]^2;n=struct.unpack_from('<H',b,10)[0]^key;assert 0<n<20000
    records=[];assert 12+n*8 < len(b)
    for i in range(n):
        p=(struct.unpack_from('<I',b,12+i*8)[0]^key)-1
        size=struct.unpack_from('<I',b,16+i*8)[0]^key
        assert p>=12+n*8 and p+4+size<=len(b)
        assert b[p+4:p+6]==b'BM' or b[p+4:p+12]==b'\x89PNG\r\n\x1a\n' or b[p+4:p+7]==b'GIF'
        records.append((p,size))
    return {'record_count':n,'xor_key':key,'all_image_ranges_and_signatures_valid':True,'pixel_decode_performed':False}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--out',type=Path,default=HERE);args=ap.parse_args()
    repo=args.repo.resolve();out=args.out.resolve()
    assert out != repo and repo not in out.parents, 'Refuse to write inside source repository'
    pins=load(HERE/'SOURCE_PINS.json')
    for p in pins['files']:
        b=(repo/p['path']).read_bytes();assert len(b)==p['bytes'] and sha(b)==p['sha256'],p['path']
    raw=(repo/MAP).read_bytes();m,spawnpins,loadpin=parse_map(raw)
    current=load(repo/'Project/data/maps/A01.json');reference=load(repo/'参考项目/public/assets/maps/A01.json')
    for k,v in m.items(): assert current[k]==v,k
    for k in ['name','home','width','height','cells','spawns','portals','npcs','loadScript','unmappedTail','sourceSha256']:assert reference[k]==m[k],k
    entities=load(repo/'Project/data/maps/A01-entities.json')
    assert entities['spawns']==m['spawns'] and entities['load_script']==loadpin
    defs,tail=parse_definitions((repo/MON).read_bytes())
    saved=load(repo/'Project/data/monsters/definitions.json');refdefs=load(repo/'参考项目/public/assets/data/monsters.json')
    assert len(saved['records'])==len(refdefs)==len(defs)==600
    for d,saved_d,ref_d in zip(defs,saved['records'],refdefs):
        for k,v in d.items():assert saved_d[k]==v,(d['id'],k)
        for k in ['id','name','sound','appearance','speed','rawExtra','drops','color','experience','event','sourceOffset']:assert ref_d[k]==d[k],(d['id'],k)
    assert saved['uninterpreted_tail']['source_offset']==tail['source_offset']
    assert saved['uninterpreted_tail']['bytes']==tail['bytes']
    exe=(repo/EXE).read_bytes();pe,offset=pe_info(exe);assert pe['image_base']=='0x400000'
    textsec=next(s for s in pe['sections'] if s['name']=='.text');assert textsec['raw_offset']==textsec['rva']==0x1000
    (out/'evidence').mkdir(parents=True,exist_ok=True)
    import_text=subprocess.check_output(['objdump','-p',str(repo/EXE)],text=True)
    imported={}
    for rva,name in [(0x110c,'__vbaStrCmp'),(0x1204,'__vbaI4Var'),(0x1030,'__vbaVarMove'),(0x10ac,'593')]:
        line=next((l.strip() for l in import_text.splitlines() if re.search(rf'\b{rva:08x}\b',l) and name in l),None)
        assert line,(hex(rva),name);imported[hex(0x400000+rva)]=line
    anchors=[]
    for va,(expected,note) in ANCHORS.items():
        b=bytes.fromhex(expected);off=offset(va);assert exe[off:off+len(b)]==b,(hex(va),note)
        anchors.append({'va':hex(va),'file_offset':off,'bytes_hex':expected,'interpretation':note})
    ranges=[]
    for name,(lo,hi) in RANGES.items():
        assembly=subprocess.check_output(['objdump','-d','-Mintel','--insn-width=16',f'--start-address={lo}',f'--stop-address={hi}',str(repo/EXE)],text=True)
        # Remove only environment-dependent filename; preserve disassembly output verbatim otherwise.
        assembly=assembly.replace(str(repo/EXE),EXE)
        (out/'evidence'/f'{name}.asm.txt').write_text(assembly,encoding='utf-8')
        code=exe[offset(lo):offset(lo)+(hi-lo)]
        ranges.append({'name':name,'start_va':hex(lo),'end_va_exclusive':hex(hi),'file_offset':offset(lo),'size':len(code),'sha256':sha(code),'raw_hex':code.hex()})
    literals={}
    for va in [0x40edb8,0x40bae0]:
        off=offset(va);n=struct.unpack_from('<I',exe,off-4)[0];literals[hex(va)]={'byte_length':n,'text':exe[off:off+n].decode('utf-16le')}
    assert [literals[x]['text'] for x in ['0x40edb8','0x40bae0']]==['0','']
    assert struct.unpack_from('<I',exe,offset(0x5a988c))[0]==0x5a906f
    binding=[]
    for s,p in zip(m['spawns'],spawnpins):
        native=resolve_name(s['name'],defs);assert native>0
        d=defs[native-1]
        binding.append({**p,'cell':[s['x'],s['y']],'serialized_monster_id':s['monsterId'],
            'serialized_name':s['name'],'extracted_definition_id':d['id'],'native_definition_id':native,
            'definition_source_offset':d['sourceOffset'],'definition_source_length':d['sourceLength'],
            'definition_record_sha256':sha(bytes.fromhex(d['raw_record_hex'])),'appearance':d['appearance'],
            'initialization_class':'special_888_requires_separate_contract' if d['appearance']==888 else 'ordinary_appearance'})
    counter=collections.Counter((s['serialized_monster_id'],s['serialized_name'],s['extracted_definition_id'],s['native_definition_id'],s['appearance']) for s in binding)
    grouped=[{'serialized_monster_id':k[0],'name':k[1],'extracted_definition_id':k[2],'native_definition_id':k[3],'appearance':k[4],'count':v} for k,v in sorted(counter.items())]
    assert [(x['serialized_monster_id'],x['native_definition_id'],x['count']) for x in grouped]==[(4,7,29),(5,8,5),(6,9,1),(7,10,1),(9,11,9),(215,4,3)]
    special=[s['cell'] for s in binding if s['appearance']==888];assert special==[[49,72],[93,50],[108,86]]
    assert (m['width'],m['height'],len(binding))==(150,150,48)
    assert collections.Counter(s['appearance'] for s in binding)=={5:36,7:9,888:3}
    sentinel=next(d['id']+1 for d in defs if d['name'] in ('','0'));assert sentinel==579
    cases=[('first duplicate wins',[{'name':'a'},{'name':'a'}],'a',1),('zero sentinel terminates',[{'name':'0'},{'name':'a'}],'a',0),('empty sentinel terminates',[{'name':''},{'name':'a'}],'a',0),('no trimming',[{'name':'a'}],' a',0),('case-sensitive model',[{'name':'a'}],'A',0),('no match',[{'name':'a'}],'b',0),('600 limit',[{'name':'a'}]*600+[{'name':'b'}],'b',0)]
    tests=[]
    for label,records,q,want in cases:got=resolve_name(q,records);assert got==want;tests.append({'case':label,'expected':want,'actual':got})
    for q in ['','0','not-a-monster', '鹿 ']:assert resolve_name(q,defs)==0
    # A mismatching old ID must never be used as fallback.
    assert resolve_name('not-a-monster',defs)==0 and defs[4]['name']=='鸡'
    packs={str(i):pack_table((repo/f'原版游戏/Data/Mon/{i}.lpRes').read_bytes()) for i in [5,7,888]}
    contract={'schema':'a01-source-contract-v1','status':'STATIC_SOURCE_VERIFIED','source_repository_commit':pins['repository_commit'],
        'map':{'id':'A01','name':m['name'],'width':m['width'],'height':m['height'],'home':m['home'],'cell_order':'x-major','cell_count':len(m['cells']),'kind6_source_records':len(binding),'portal_records':len(m['portals']),'npc_records':len(m['npcs']),'grid_offset':m['gridOffset'],'tail_offset':m['tailOffset'],'uninterpreted_tail_bytes':len(bytes.fromhex(m['unmappedTail'])),'uninterpreted_tail_sha256':sha(bytes.fromhex(m['unmappedTail'])),'load_script':loadpin},
        'identity_contract':{'serialized_id_is_authoritative':False,'runtime_resolution':'sequential exact name match; native indices 1..600; first match; terminate at empty or literal zero database name; failed result 0; no numeric fallback','native_definition_id':'extracted_definition_id + 1','definition_stride_bytes':124,'entity_definition_id_offset':'0x8c','entity_appearance_offset':'0x8','current_first_sentinel_native_id':sentinel},
        'groups':grouped,'ordinary_source_records':45,'special_888_source_records':3,'special_cells':special,
        'sprite_pack_table_checks':packs,'runtime_spawn_count':None,'runtime_integrated':False,'godot_or_original_exe_executed':False,
        'hard_boundaries':['48 source records is not a claim of 48 final ordinary live actors.','Three appearance-888 inputs must remain separately classified until their RNG/transformation/lifecycle contract is implemented.','Mon/888.lpRes exists; special does not mean missing asset.','Keep source serializedMonsterId and source offsets unchanged; store resolved IDs separately.','Use zero as failure; never look up a definition by old map ID after name resolution fails.','Raw fields are preserved; names in an existing extractor are not independent proof of combat semantics.'],
        'unresolved':['Full appearance-888 special initialization and its RNG consumption, exact probability, transformations and final occupancy are not implemented or asserted here.','Monster action clips, timing, AI, movement, attack, drops, death and respawn require separate contracts.','The 68-byte A01 tail and 9020-byte monster-definition tail remain uninterpreted.','No Windows/VB6 execution or Godot runtime validation was performed.','The reconstructed Python resolver is a static model; no claim of a general VB6 string-runtime emulator.']}
    write(out/'A01_SOURCE_CONTRACT.json',contract);write(out/'A01_SPAWN_BINDINGS.json',binding)
    relevant=sorted({s['extracted_definition_id'] for s in binding})
    write(out/'A01_DEFINITION_SOURCE_RECORDS.json',{'records':[defs[i] for i in relevant],'definition_count':len(defs),'uninterpreted_tail':tail})
    write(out/'evidence/EXE_EVIDENCE.json',{'source':EXE,'sha256':sha(exe),'pe':pe,'anchors':anchors,'ranges':ranges,'imports':imported,'literals':literals,'definition_name_jump_table_first_target':'0x5a906f','tool':subprocess.check_output(['objdump','--version'],text=True).splitlines()[0]})
    write(out/'evidence/LOOKUP_MODEL_TESTS.json',{'status':'PASS','tests':tests,'actual_table_negative_cases':['','0','not-a-monster','鹿 '],'scope':'Static reconstructed model tests; not executed native tests.'})
    # Detect accidental change to every pinned source after all operations.
    for p in pins['files']:assert sha((repo/p['path']).read_bytes())==p['sha256'],p['path']
    report={'status':'PASS','source_pins_verified_before_and_after':len(pins['files']),'map_fields_equal_to_production':len(m),'definition_records_equal_to_production':len(defs),'definition_source_fields_compared':sum(len(d['fields']) for d in defs),'native_instruction_anchors':len(anchors),'disassembly_ranges':len(ranges),'spawn_records':len(binding),'ordinary_source_records':45,'special_888_source_records':3,'source_mutation_detected':False,'runtime_tests':'NOT RUN by instruction'}
    write(out/'VALIDATION.json',report)
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
