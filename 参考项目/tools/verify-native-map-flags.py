"""Read the original editor's control captions and matching signed flag stores."""
from pathlib import Path
import struct,re,json,hashlib
ROOT=Path(__file__).resolve().parent.parent
source=ROOT/'reference/LP传奇单机版-重生v1.2.2E/Module/Tool/MOD编辑器.exe'
b=source.read_bytes();pe=struct.unpack_from('<I',b,60)[0];base=struct.unpack_from('<I',b,pe+52)[0]
count=struct.unpack_from('<H',b,pe+6)[0];start=pe+24+struct.unpack_from('<H',b,pe+20)[0]
sections=[struct.unpack_from('<8sIIII',b,start+i*40) for i in range(count)]
def offset(va):
 for _,_,rva,size,raw in sections:
  if rva<=va-base<rva+size:return raw+va-base-rva
 raise ValueError('Address outside section')
controls={}
for m in re.finditer(rb'\x11(..)\x06\x00o_Flag\x00\x06\x01(..)',b,re.S):
 index=struct.unpack('<H',m[1])[0];length=struct.unpack('<H',m[2])[0]
 controls[index]={'caption':b[m.end():m.end()+length].decode('gb18030'),'captionOffset':m.end()}
# Each branch queries o_Flag.Item(index).Value, then passes this integer to the
# same map-flag setter (vtable +0x70c). Addresses are in the original PE image.
branches=[(0,0x7c3e19,0x7c3e7e,-2),(1,0x7c3ea4,0x7c3f09,-1),(2,0x7c3f2f,0x7c3f94,1),(3,0x7c3fba,0x7c401f,2),(4,0x7c4045,0x7c40aa,-3),(5,0x7c40e5,0x7c4151,-4)]
expected=['底端禁行','中层禁行','底端','顶端','玩家禁止','怪物禁止'];records=[]
for index,selector,store,value in branches:
 assert controls[index]['caption']==expected[index]
 selectBytes=b[offset(selector):offset(selector)+2];assert selectBytes==bytes([0x6a,index])
 storeBytes=b[offset(store):offset(store)+7];assert storeBytes[:3]==b'\xc7\x45\x9c'
 assert struct.unpack('<i',storeBytes[3:])[0]==value
 records.append({'index':index,**controls[index],'flag':value,'selectorVA':hex(selector),'selectorBytes':selectBytes.hex(),'storeVA':hex(store),'storeBytes':storeBytes.hex()})
out={'passed':True,'source':str(source.relative_to(ROOT)),'sourceSha256':hashlib.sha256(b).hexdigest(),'imageBase':hex(base),'mapping':records,'setterVA':'vtable+0x70c','renderMeaningSource':'Help/Mod_4_2.htm'}
(ROOT/'reports/native-map-flags.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(out,ensure_ascii=False))
