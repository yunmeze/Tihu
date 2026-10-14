"""Check native editor column captions against the preserved item word fields."""
from pathlib import Path
import ctypes as C,struct,json,hashlib
ROOT=Path(__file__).resolve().parent.parent
source=ROOT/'reference/LP传奇单机版-重生v1.2.2E/Module/Tool/MOD编辑器.exe';b=source.read_bytes()
pe=struct.unpack_from('<I',b,60)[0];base=struct.unpack_from('<I',b,pe+52)[0];count=struct.unpack_from('<H',b,pe+6)[0];start=pe+24+struct.unpack_from('<H',b,pe+20)[0]
sections=[struct.unpack_from('<8sIIII',b,start+i*40) for i in range(count)]
def va(p):
 for _,_,rva,size,raw in sections:
  if raw<=p<raw+size:return base+rva+p-raw
 raise ValueError('Outside PE sections')
class Ins(C.Structure):
 _fields_=[('id',C.c_uint),('address',C.c_uint64),('size',C.c_uint16),('bytes',C.c_uint8*16),('mnemonic',C.c_char*32),('op_str',C.c_char*160),('detail',C.c_void_p)]
dll=C.CDLL(str(ROOT/'.tools/python/TypeTreeGeneratorAPI/capstone.dll'));dll.cs_open.argtypes=[C.c_int,C.c_int,C.POINTER(C.c_size_t)];dll.cs_disasm.argtypes=[C.c_size_t,C.c_void_p,C.c_size_t,C.c_uint64,C.c_size_t,C.POINTER(C.POINTER(Ins))];dll.cs_disasm.restype=C.c_size_t;dll.cs_free.argtypes=[C.POINTER(Ins),C.c_size_t]
handle=C.c_size_t();assert dll.cs_open(3,4,C.byref(handle))==0
def instructions(p,n):
 code=C.create_string_buffer(b[p:p+n]);out=C.POINTER(Ins)();size=dll.cs_disasm(handle,code,n,va(p),0,C.byref(out));rows=[(out[i].address,out[i].mnemonic.decode(),out[i].op_str.decode()) for i in range(size)];dll.cs_free(out,size);return rows
fields=[(16,'快攻'),(17,'快法'),(18,'物避'),(19,'魔避'),(20,'准确'),(21,'冰封'),(22,'引燃'),(23,'中毒'),(24,'麻痹'),(25,'吸血'),(26,'伤反'),(27,'幸运'),(31,'等级需求'),(32,'攻击需求'),(33,'道术需求'),(34,'魔法需求')]
records=[]
for index,label in fields:
 pos=b.find(label.encode('utf-16le'));assert pos>=0
 needle=struct.pack('<I',va(pos));refs=[];at=b.find(needle)
 while at>=0:
  if at>100000:
   f=b.rfind(b'\x55\x8b\xec',max(0,at-30000),at)
   if va(f)==0x7ac570:
    rows=instructions(f,at-f+8);assignment=next(((a,m,o) for a,m,o in reversed(rows[-35:]) if m=='mov' and o==f'eax, {hex(index+2)}'),None)
    assert assignment,(index,label)
    refs.append({'literalRefVA':hex(va(at)),'columnAssignmentVA':hex(assignment[0]),'column':index+2,'instructions':[f'{a:08x} {m} {o}' for a,m,o in rows[-20:]]})
  at=b.find(needle,at+4)
 assert refs,label
 records.append({'rawWordIndex':index,'label':label,'refs':refs})
report={'passed':True,'source':str(source.relative_to(ROOT)),'sourceSha256':hashlib.sha256(b).hexdigest(),'editorHeaderVA':'0x7ac570','mapping':records,'help':'Help/Mod_2_1.htm','notes':['Editor columns 16–27 and 31–34 are verified here. The shipped loader additionally maps raw30 to attached skill, raw35 to forge, raw36 to use count and raw37 to sale-price factor. Raw28/29 both load into 6c; fusion grade is separate 68. See native-refining-source.json.','Actual modified instance fields are used by display, requirements, combat, carry weight, forge/merge, prices and persistence.']}
(ROOT/'reports/native-item-fields.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'passed':True,'verifiedFields':len(records)},ensure_ascii=False))
