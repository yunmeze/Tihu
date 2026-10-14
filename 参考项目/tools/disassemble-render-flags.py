from pathlib import Path
import struct,ctypes,re
class Insn(ctypes.Structure):
 _fields_=[('id',ctypes.c_uint),('address',ctypes.c_uint64),('size',ctypes.c_ushort),('bytes',ctypes.c_ubyte*16),('mnemonic',ctypes.c_char*32),('op_str',ctypes.c_char*160),('detail',ctypes.c_void_p)]
c=ctypes.CDLL(str(Path('.tools/python/TypeTreeGeneratorAPI/capstone.dll').resolve()));c.cs_open.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.POINTER(ctypes.c_size_t)];c.cs_disasm.argtypes=[ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_uint64,ctypes.c_size_t,ctypes.POINTER(ctypes.POINTER(Insn))];c.cs_disasm.restype=ctypes.c_size_t;c.cs_free.argtypes=[ctypes.POINTER(Insn),ctypes.c_size_t];c.cs_option.argtypes=[ctypes.c_size_t,ctypes.c_int,ctypes.c_size_t];h=ctypes.c_size_t();print('open',c.cs_open(3,4,ctypes.byref(h)));c.cs_option(h,5,3)
for filename in ['LP传奇单机版_重生.exe','Module/Tool/MOD编辑器.exe']:
 b=(Path('reference/LP传奇单机版-重生v1.2.2E')/filename).read_bytes();pe=struct.unpack_from('<I',b,60)[0];base=struct.unpack_from('<I',b,pe+52)[0];n=struct.unpack_from('<H',b,pe+6)[0];so=pe+24+struct.unpack_from('<H',b,pe+20)[0];sec=next(struct.unpack_from('<8sIIII',b,so+i*40) for i in range(n) if b[so+i*40:so+i*40+5]==b'.text');_,sz,rva,rs,raw=sec;data=b[raw:raw+rs];ptr=ctypes.POINTER(Insn)();count=c.cs_disasm(h,data,len(data),base+rva,0,ctypes.byref(ptr));print(filename,count);matches=[]
 for i in range(count):
  ins=ptr[i];s=ins.op_str.decode()
  if ins.mnemonic in [b'cmp',b'mov'] and re.search(r', (0xffff|0xfffe|0xffffffff|0xfffffffe)$',s) and ('word ptr' in s or 'dword ptr' in s):
   matches.append((i,hex(ins.address),ins.mnemonic.decode(),s))
 print('total',len(matches));
 if 'Tool' in filename:
  lines=[]
  for i in range(count):
   ins=ptr[i]
   if 0x7c3cf0<=ins.address<=0x7c4250:lines.append(f'{ins.address:08x} {ins.mnemonic.decode():8} {ins.op_str.decode()}')
  Path('reports/native-editor-flag-assembly.txt').write_text('\n'.join(lines),encoding='utf8');print('\n'.join(lines))
 c.cs_free(ptr,count)
