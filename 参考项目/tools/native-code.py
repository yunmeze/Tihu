"""Small read-only PE/Capstone helper for native-rule verification scripts."""
from pathlib import Path
import ctypes as C,struct
ROOT=Path(__file__).resolve().parent.parent
class Ins(C.Structure):
 _fields_=[('id',C.c_uint),('address',C.c_uint64),('size',C.c_uint16),('bytes',C.c_uint8*16),('mnemonic',C.c_char*32),('op_str',C.c_char*160),('detail',C.c_void_p)]
class NativeCode:
 def __init__(self,path='reference/LP传奇单机版-重生v1.2.2E/LP传奇单机版_重生.exe'):
  self.source=ROOT/path;self.data=self.source.read_bytes();b=self.data;pe=struct.unpack_from('<I',b,60)[0];self.base=struct.unpack_from('<I',b,pe+52)[0];start=pe+24+struct.unpack_from('<H',b,pe+20)[0]
  self.sections=[struct.unpack_from('<8sIIII',b,start+i*40) for i in range(struct.unpack_from('<H',b,pe+6)[0])]
  self.dll=C.CDLL(str(ROOT/'.tools/python/TypeTreeGeneratorAPI/capstone.dll'));self.dll.cs_open.argtypes=[C.c_int,C.c_int,C.POINTER(C.c_size_t)];self.dll.cs_disasm.argtypes=[C.c_size_t,C.c_void_p,C.c_size_t,C.c_uint64,C.c_size_t,C.POINTER(C.POINTER(Ins))];self.dll.cs_disasm.restype=C.c_size_t;self.dll.cs_free.argtypes=[C.POINTER(Ins),C.c_size_t]
  self.handle=C.c_size_t();assert self.dll.cs_open(3,4,C.byref(self.handle))==0
 def offset(self,address):
  return next(raw+address-self.base-rva for _,_,rva,size,raw in self.sections if self.base+rva<=address<self.base+rva+size)
 def va(self,p):
  return next(self.base+rva+p-raw for _,_,rva,size,raw in self.sections if raw<=p<raw+size)
 def disasm(self,lo,hi):
  code=C.create_string_buffer(self.data[self.offset(lo):self.offset(hi)]);out=C.POINTER(Ins)();size=self.dll.cs_disasm(self.handle,code,hi-lo,lo,0,C.byref(out));rows=[(out[i].address,out[i].mnemonic.decode(),out[i].op_str.decode()) for i in range(size)];self.dll.cs_free(out,size);return rows
 def dump(self,name,ranges):
  rows=[]
  for lo,hi in ranges:rows.extend(self.disasm(lo,hi))
  (ROOT/'reports'/name).write_text('\n'.join(f'{a:08x} {m:8s} {o}' for a,m,o in rows),encoding='utf8');return rows
 def number(self,address,fmt='<f'):return struct.unpack_from(fmt,self.data,self.offset(address))[0]
 def string(self,address):
  p=self.offset(address);size=struct.unpack_from('<I',self.data,p-4)[0];assert size<10000;return self.data[p:p+size].decode('utf-16le')
 def literal_refs(self,text):
  b=self.data;p=b.find(text.encode('utf-16le'));needle=struct.pack('<I',self.va(p));out=[];at=b.find(needle)
  while at>=0:
   if at>100000:out.append(self.va(at))
   at=b.find(needle,at+4)
  return out
 def callers(self,address):
  b=self.data;out=[]
  for _,_,rva,size,raw in self.sections:
   p=raw
   while p<raw+size-5:
    p=b.find(b'\xe8',p,raw+size-5)
    if p<0:break
    if self.va(p)+5+struct.unpack_from('<i',b,p+1)[0]==address:out.append(self.va(p))
    p+=1
  return out
 def prolog(self,address):
  p=self.offset(address);return self.va(self.data.rfind(b'\x55\x8b\xec',max(0,p-60000),p))
if __name__=='__main__':
 import sys
 code=NativeCode();lo=int(sys.argv[1],16);hi=int(sys.argv[2],16);rows=code.dump(f'native-{lo:x}.txt',[(lo,hi)]);print({'instructions':len(rows),'end':hex(rows[-1][0])})
