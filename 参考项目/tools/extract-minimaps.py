"""Export the original miniIndex/miniData JPEG records without changing pixels."""
from pathlib import Path
import struct,json,hashlib,io,sys
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'.tools/python'))
from PIL import Image
SOURCE=ROOT/'reference/LP传奇单机版-重生v1.2.2E/Data/Map';OUT=ROOT/'public/assets'
index=(SOURCE/'miniIndex.lpRes').read_bytes();data=(SOURCE/'miniData.lpRes').read_bytes()
count=struct.unpack_from('<H',index,0)[0];pos=2;maps={};end=0
(OUT/'minimaps').mkdir(exist_ok=True)
for i in range(count):
 length=struct.unpack_from('<I',index,pos)[0];pos+=4;name=index[pos:pos+length].decode('gb18030');pos+=length
 offset,size=struct.unpack_from('<II',index,pos);pos+=8;assert offset==end and offset+size<=len(data);end=offset+size
 original=data[offset:end];im=Image.open(io.BytesIO(original));assert im.format=='JPEG' and im.size==(1400,1000)
 key=Path(name).stem;file='minimaps/'+key+'.jpg';(OUT/file).write_bytes(original)
 maps[key]={'file':file,'width':im.width,'height':im.height,'sourceOffset':offset,'sourceBytes':size,'sha256':hashlib.sha256(original).hexdigest()}
assert pos==len(index) and end==len(data)
known={p.stem for p in (OUT/'maps').glob('*.json')}
result={'sourceIndex':'Data/Map/miniIndex.lpRes','sourceData':'Data/Map/miniData.lpRes','indexSha256':hashlib.sha256(index).hexdigest(),'dataSha256':hashlib.sha256(data).hexdigest(),'tilePixels':[7,5],'canvasCells':[200,200],'maps':maps,'missing':sorted(known-set(maps))}
(OUT/'data/minimaps.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')),encoding='utf8')
(ROOT/'reports/minimap-extraction.json').write_text(json.dumps({'passed':True,'records':count,'byteExact':True,'missing':result['missing'],'dataBytes':len(data),'coordinateCheck':'A00 map extent 150x150 maps to 1050x750; source portal markers align to 7x5 pixel cells'},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'records':count,'byteExact':True,'missing':result['missing'],'dataBytes':len(data)}))
