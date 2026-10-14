"""Inspect native trade/warehouse code and constants without executing the game."""
from pathlib import Path
import ctypes as C,struct,json,hashlib
ROOT=Path(__file__).resolve().parent.parent;source=ROOT/'reference/LP传奇单机版-重生v1.2.2E/LP传奇单机版_重生.exe';data=source.read_bytes()
pe=struct.unpack_from('<I',data,60)[0];base=struct.unpack_from('<I',data,pe+52)[0];count=struct.unpack_from('<H',data,pe+6)[0];start=pe+24+struct.unpack_from('<H',data,pe+20)[0]
sections=[struct.unpack_from('<8sIIII',data,start+i*40) for i in range(count)]
def va(offset):
 for _,_,rva,size,raw in sections:
  if raw<=offset<raw+size:return base+rva+offset-raw
def offset(address):
 for _,_,rva,size,raw in sections:
  if base+rva<=address<base+rva+size:return raw+address-base-rva
dll=C.CDLL(str(ROOT/'.tools/python/TypeTreeGeneratorAPI/capstone.dll'))
class Instruction(C.Structure):
 _fields_=[('id',C.c_uint),('address',C.c_uint64),('size',C.c_uint16),('bytes',C.c_uint8*16),('mnemonic',C.c_char*32),('op_str',C.c_char*160),('detail',C.c_void_p)]
dll.cs_open.argtypes=[C.c_int,C.c_int,C.POINTER(C.c_size_t)];dll.cs_disasm.argtypes=[C.c_size_t,C.c_void_p,C.c_size_t,C.c_uint64,C.c_size_t,C.POINTER(C.POINTER(Instruction))];dll.cs_disasm.restype=C.c_size_t;dll.cs_free.argtypes=[C.POINTER(Instruction),C.c_size_t]
handle=C.c_size_t();assert dll.cs_open(3,4,C.byref(handle))==0
def disasm(lo,hi):
 code=C.create_string_buffer(data[lo:hi]);out=C.POINTER(Instruction)();n=dll.cs_disasm(handle,code,hi-lo,va(lo),0,C.byref(out));lines=[f'{out[i].address:08x} {out[i].mnemonic.decode():8s} {out[i].op_str.decode()}' for i in range(n)];dll.cs_free(out,n);return lines
records=[];lines=[]
for text in ['该道具无法出售','此物分文不值','该道具不能出售','携带金币不足','非爆出装备不能放入次元箱','只有装备类道具才能放入次元箱！','锻造后的装备不能放入次元箱！','合成后的装备不能放入次元箱！','不能将非当前模式下得到的装备放进次元箱']:
 p=data.find(text.encode('utf-16le'));refs=[]
 for address in [va(p),va(p-4)]:
  needle=struct.pack('<I',address);at=data.find(needle)
  while at>=0:
   if at>100000:refs.append(at)
   at=data.find(needle,at+4)
 records.append({'text':text,'sourceOffset':p,'literalVA':hex(va(p)),'refs':[hex(va(at)) for at in refs]})
 for at in refs:
  lines.append(f'\n{text} ref={va(at):08x}');lines.extend(disasm(at-900,at+1000))
(ROOT/'reports/native-trade-assembly.txt').write_text('\n'.join(lines),encoding='utf8')
pricing=[]
for name,lo,hi in [('display',0x57d7b4,0x57d829),('payout',0x584dfa,0x584e41)]:
 instructions=disasm(offset(lo),offset(hi));text='\n'.join(instructions)
 assert '0x66666667' in text and any('sar' in line and 'edx, 1' in line for line in instructions) and any('inc' in line and line.endswith('eax') for line in instructions)
 pricing.append({'path':name,'startVA':hex(lo),'endVA':hex(hi),'instructions':instructions})
report={'passed':True,'source':str(source.relative_to(ROOT)),'sha256':hashlib.sha256(data).hexdigest(),'literals':records,'baseItemSale':{'formula':'floor(price/5)+1','scope':'Positive-price, unmodified base items. Native runtime instance premium at +0x7e is not modeled; enhanced equipment pricing is not verified.','paths':pricing}}
(ROOT/'reports/native-service-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'passed':True,'nativeSalePaths':len(pricing),'constraintLiterals':len(records)},ensure_ascii=False))
