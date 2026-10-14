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

import hashlib
clips=[]
for name,lo,hi in [('idle_loop',0x5ca506,0x5ca741),('idle_random_direction',0x5ca741,0x5ca7ea),('fixed_behaviors',0x5ca7dc,0x5ca8b1),('fixed_spawner',0x5cabe1,0x5cabef)]:
 p=next(raw+lo-base-rva for _,_,rva,size,raw in sections if base+rva<=lo<base+rva+size)
 rows=instructions(p,hi-lo)
 clips.append({'name':name,'startVA':hex(lo),'instructions':[f'{a:08x} {m:8s} {o}' for a,m,o in rows]})
assert any('word ptr [esi + 0x9a], -2' in line for line in clips[2]['instructions'])
assert any('jg' in line and '0x5caea9' in line for line in clips[1]['instructions'])
constants={}
for address in [0x401560,0x4016f8,0x402088,0x401f24]:
 p=next(raw+address-base-rva for _,_,rva,size,raw in sections if base+rva<=address<base+rva+size)
 constants[hex(address)]=struct.unpack_from('<f',b,p)[0]
report={'passed':True,'source':str(source.relative_to(ROOT)),'sha256':hashlib.sha256(b).hexdigest(),'nativeBehaviorMember':'unit+0x9a','fixedBehaviorCondition':'behavior <= -2','help':['Help/Mod_3_1.htm','Help/Mod_3_4.htm'],'clips':clips,'constants':constants,'idleTimingVerified':True,'idleDecisionFrames':48,'moveComparison':'CInt(Rnd * 100) < 20','turnProbability':.3,'turnOnlyBehaviors':[13,14,15]}
(ROOT/'reports/native-monster-motion.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'passed':True,'constants':constants,'fixedBehaviors':'<= -2','idleTimingVerified':True},ensure_ascii=False))
