from pathlib import Path
import ctypes as C,struct,json
ROOT=Path(__file__).resolve().parent.parent
source=ROOT/'reference/LP传奇单机版-重生v1.2.2E/LP传奇单机版_重生.exe';b=source.read_bytes()
pe=struct.unpack_from('<I',b,60)[0];base=struct.unpack_from('<I',b,pe+52)[0];count=struct.unpack_from('<H',b,pe+6)[0];start=pe+24+struct.unpack_from('<H',b,pe+20)[0]
sections=[struct.unpack_from('<8sIIII',b,start+i*40) for i in range(count)]
def va(p):
 for _,_,rva,size,raw in sections:
  if raw<=p<raw+size:return base+rva+p-raw
 return 0
class Ins(C.Structure):
 _fields_=[('id',C.c_uint),('address',C.c_uint64),('size',C.c_uint16),('bytes',C.c_uint8*16),('mnemonic',C.c_char*32),('op_str',C.c_char*160),('detail',C.c_void_p)]
dll=C.CDLL(str(ROOT/'.tools/python/TypeTreeGeneratorAPI/capstone.dll'));dll.cs_open.argtypes=[C.c_int,C.c_int,C.POINTER(C.c_size_t)];dll.cs_disasm.argtypes=[C.c_size_t,C.c_void_p,C.c_size_t,C.c_uint64,C.c_size_t,C.POINTER(C.POINTER(Ins))];dll.cs_disasm.restype=C.c_size_t;dll.cs_free.argtypes=[C.POINTER(Ins),C.c_size_t]
h=C.c_size_t();assert dll.cs_open(3,4,C.byref(h))==0
def instructions(p,n,count=0):
 code=C.create_string_buffer(b[p:p+n]);out=C.POINTER(Ins)();size=dll.cs_disasm(h,code,n,va(p),count,C.byref(out));rows=[(out[i].address,out[i].mnemonic.decode(),out[i].op_str.decode()) for i in range(size)];dll.cs_free(out,size);return rows

import hashlib,re

def offset(address):
 return next(raw+address-base-rva for _,_,rva,size,raw in sections if base+rva<=address<base+rva+size)
anchor=offset(0x5ca7dc);p=b.rfind(b'\x55\x8b\xec',max(0,anchor-30000),anchor)
end=offset(0x5d2240);rows=instructions(p,end-p)
for lo,hi in [(0x5d1bb0,0x5d1f10),(0x5c9930,0x5c9fb3),(0x5d2230,0x5d3440),(0x5d3440,0x5d37d0),(0x5d5370,0x5d5af0),(0x5a0330,0x5a0445),(0x59e5cc,0x59e63d),(0x5a0960,0x5a0b85)]:rows.extend(instructions(offset(lo),hi-lo))
(ROOT/'reports/native-ai-assembly.txt').write_text('\n'.join(f'{a:08x} {m:8s} {o}' for a,m,o in rows),encoding='utf8')
refs=[{'va':hex(a),'instruction':m+' '+o} for a,m,o in rows if '0x9a]' in o or ('word ptr [esi +' in o and m=='cmp')]
report={'source':str(source.relative_to(ROOT)),'sha256':hashlib.sha256(b).hexdigest(),'range':[hex(va(p)),'0x5d2240'],'refs':refs,'rules':{'sight':'Chebyshev rings up to native vision; 0x5d5370','negativeBehavior':'No retaliation when behavior < 0; 0x5c9144','aggroFrames':750,'aggroVA':'0x5ca033','ranged':'attackKind > 10 uses native vision; 0x5d3264','lowHP':{'9':{'threshold':0.2,'speedMultiplier':1.5,'VA':'0x5ca2f2'},'10':{'threshold':0.3,'attackIntervalMultiplier':0.7,'VA':'0x5ca35b'},'15':{'threshold':0.3,'attackIntervalMultiplier':0.7,'VA':'0x5ca3c5'}},'flee':{'behaviors':[6,8,20],'probability':0.1,'cooldownFrames':200,'offsetRange':[-4,5],'offsetMultiplier':9,'VA':'0x5d1bb0','note':'Called after an attack, while aggro and not already fleeing. This shipped executable does not gate behaviors 8/20 by HP, unlike the older Help table.'},'idle':{'decisionFrames':48,'moveProbability':0.2,'turnProbability':0.3,'VA':'0x5ca506'}},'fullAIEquivalent':False,'constants':{hex(a):{kind:struct.unpack_from('<f' if kind=='float' else '<d',b,offset(a))[0]} for a,kind in [(0x4016f8,'float'),(0x401560,'float'),(0x401ee4,'float'),(0x401798,'double'),(0x4017a0,'double'),(0x4020e0,'double'),(0x402420,'double'),(0x402428,'double'),(0x401f30,'double'),(0x402124,'float')]},'specialJumpMap':{str(i+7):struct.unpack_from('<I',b,offset(0x5cd190)+b[offset(0x5cd1a8)+i]*4)[0] for i in range(14)},'literals':{hex(a):b[offset(a):offset(a)+struct.unpack_from('<I',b,offset(a)-4)[0]].decode('utf-16le',errors='replace') for a in [0x412618,0x412624,0x412638,0x412654,0x41266c]}}
by_va={a:(m,o) for a,m,o in rows}
expected={0x5ca033:('cmp','dword ptr [esi + 0x4c], 0x2ee'),0x5d3268:('cmp','word ptr [esi + 0x32], 0xa'),0x5d1c4e:('mov','word ptr [esi + 0x5c], 0xc8'),0x5ca353:('fstp','dword ptr [esi + 0x40]'),0x5ca435:('mov','word ptr [esi + 0x30], ax'),0x5ccd05:('mov','word ptr [esi + 0x2e], dx'),0x5ccd43:('call','0x5d1bb0'),0x5a03cd:('call','edi'),0x59e604:('call','0x5a0330'),0x59e62d:('mov','dword ptr [ecx + edx*8 + 4], eax')}
for address,instruction in expected.items():assert by_va.get(address)==instruction,(hex(address),by_va.get(address),instruction)
assert report['constants']['0x402124']['float']==9
assert report['constants']['0x401f30']['double']==1.5
assert report['constants']['0x4017a0']['double']==.2
assert report['constants']['0x4020e0']['double']==.3
assert report['constants']['0x401798']['double']==.7
report['passed']=True
report['verifiedInstructionAnchors']={hex(a):m+' '+o for a,(m,o) in expected.items()}
report['rules']['spawnLookup']={'lookupVA':'0x5a0330','mapLoadVA':'0x59e604','overwriteCachedIndexVA':'0x59e62d','rule':'Read cell kind 6 BSTR, compare against the monster database name and overwrite the saved numeric index. Exported source bytes are preserved; runtime resolves by name.'}
report['rules']['attackTiming']={'frameTicks':4,'frames':6,'strikeFrame':5,'attackKind5StrikeFrame':1,'cooldownStarts':'after animation completes','completionVA':'0x5cccde','aggroRefresh':'each completed attack writes aggro timer to 1','normalAnimationSeconds':.48,'note':'Freeze/paralysis timing is now handled by statuses.js; see native-combat-source.json for remaining adaptations.'}
report['rules']['lowHP']['note']='The program writes speed/attack interval in place, without a recovery branch; the boost persists until unit reset.'
report['rules']['idle']['moveComparison']='CInt(Rnd * 100) < 20, with VB bankers rounding'
report['rules']['idle']['stationaryTurnOnlyBehaviors']=[13,14,15]
report['adaptations']=['Bounded A* routing and swept projectile collision replace native directional/occupancy routing.','Core damage, statuses, eggs, parent spawners and two summoned allies are implemented; evidence and remaining limits are in native-combat-source.json.','Complete pet progression and higher special behavior/attack branches remain incomplete.']
(ROOT/'reports/native-ai-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'range':report['range'],'instructions':len(rows),'constants':report['constants'],'specialJumpMap':report['specialJumpMap'],'literals':report['literals']},ensure_ascii=False))
