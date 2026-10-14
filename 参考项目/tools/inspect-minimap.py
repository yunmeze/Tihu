from pathlib import Path
import struct,json,io,sys
root=Path.cwd();sys.path.insert(0,str(root/'.tools/python'))
from PIL import Image
s=root/'reference/LP传奇单机版-重生v1.2.2E/Data/Map';b=(s/'miniIndex.lpRes').read_bytes();data=(s/'miniData.lpRes').read_bytes();n=struct.unpack_from('<H',b,0)[0];pos=2;records=[]
for i in range(n):
 size=struct.unpack_from('<I',b,pos)[0];pos+=4;name=b[pos:pos+size].decode('gb18030');pos+=size;offset,length=struct.unpack_from('<II',b,pos);pos+=8;image=Image.open(io.BytesIO(data[offset:offset+length]));records.append((name,offset,length,image.size))
 if name in ['A00.lpMap','A02.lpMap','A05.lpMap']:(root/'reports'/('native-mini-'+Path(name).stem+'.jpg')).write_bytes(data[offset:offset+length])
print('records',n,'parsed',pos,len(b),'examples',records[:8]);maps={p.stem for p in (root/'public/assets/maps').glob('*.json')};print('missing',maps-{Path(r[0]).stem for r in records});print('tailData',len(data)-max(r[1]+r[2] for r in records))
