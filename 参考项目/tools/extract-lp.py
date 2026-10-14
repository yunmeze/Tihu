"""Read LP's shipped bytes. Source inputs are never modified."""
from pathlib import Path
import sys, struct, json, hashlib, re, io, time, shutil
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / '.tools/python'))
from PIL import Image, ImageSequence, ImageChops
SOURCE = ROOT / 'reference/LP传奇单机版-重生v1.2.2E'
OUT = ROOT / 'public/assets'
REPORT = ROOT / 'reports'

def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

class Reader:
    def __init__(self, data, kind, start=10): self.data, self.key, self.pos = data, data[3] ^ kind, start
    def number(self, fmt):
        size = struct.calcsize(fmt)
        if self.pos + size > len(self.data): raise ValueError('Unexpected EOF at '+str(self.pos))
        value = struct.unpack_from(fmt, self.data, self.pos)[0]; self.pos += size
        if fmt in ('<f', '<d'): return value
        value ^= self.key
        if fmt == '<H' and value & 0x8000: value -= 0x10000
        return value
    def short(self): return self.number('<H')
    def long(self): return self.number('<I')
    def string(self):
        length = self.long()
        if length > 2000000 or self.pos+length > len(self.data): raise ValueError('Invalid string length '+str(length)+' at '+str(self.pos-4))
        value = bytes(x ^ self.key for x in self.data[self.pos:self.pos+length]).decode('gb18030', errors='strict')
        self.pos += length
        return value

def items():
    data=(SOURCE/'Data/Item0.lpRes').read_bytes(); r=Reader(data,0); result=[]; error=None
    while r.pos < len(data):
        start=r.pos
        try:
            name=r.string()
            if not name or any(ord(c)<32 for c in name): raise ValueError('Item table end')
            fields=[r.short() for _ in range(39)]; price=r.long(); reserved=r.short()
            if not -1 <= fields[0] <= 100: raise ValueError('Invalid item type '+str(fields[0])+' '+name)
            result.append(dict(id=len(result),name=name,type=fields[0],icon=fields[1],appearance=[fields[2],fields[3]],hp=fields[4],mp=fields[5],attack=fields[6:8],tao=fields[8:10],magic=fields[10:12],defense=fields[12:14],magicDefense=fields[14:16],weight=fields[38],price=price,rawFields=fields,reserved=reserved,sourceOffset=start))
        except Exception as e:
            error={'offset':start,'bytes':len(data)-start,'reason':str(e)};break
    write(OUT/'data/items.json',result)
    return {'records':len(result),'parsedBytes':r.pos,'totalBytes':len(data),'tail':error}

def monsters():
    data=(SOURCE/'Data/Mon/0.lpRes').read_bytes();r=Reader(data,6);result=[];error=None
    while r.pos<len(data):
        start=r.pos
        try:
            name=r.string();sound=r.string()
            if not name or any(ord(c)<32 for c in name): raise ValueError('Monster table end')
            fields=[r.short() for _ in range(11)];speed=r.number('<f');extra=[r.short() for _ in range(11)];drops=r.string();color=[r.short() for _ in range(4)];experience=r.short();event=r.string();description=''
            if not 0<=fields[0]<1000 or fields[3]<0 or not 0<=speed<50:raise ValueError('Invalid monster record')
            dropRules=[]
            for token in drops.split():
                match=re.match(r'^(.*?)(\d+)/(\d+)$',token)
                if match:dropRules.append({'item':match[1],'quantity':int(match[2]),'denominator':int(match[3])})
            result.append(dict(id=len(result),name=name,sound=sound,appearance=fields[0],death=fields[1],attackKind=fields[2],hp=fields[3],regenFrames=fields[4],attack=fields[5],defense=fields[6],magicDefense=fields[7],physicalEvade=fields[8],magicEvade=fields[9],vision=fields[10],speed=speed,attackFrames=extra[0],paralysis=extra[1],poison=extra[2],freeze=extra[3],burn=extra[4],behavior=extra[7],rawExtra=extra,event=event,drops=drops,dropRules=dropRules,color=color,experience=experience,description=description,sourceOffset=start))
        except Exception as e:error={'offset':start,'bytes':len(data)-start,'reason':str(e)};break
    write(OUT/'data/monsters.json',result)
    return {'records':len(result),'parsedBytes':r.pos,'totalBytes':len(data),'tail':error}

def map_file(p):
    data=p.read_bytes();r=Reader(data,3);name=r.string();home=[r.short(),r.short()];width=r.short();height=r.short()
    if not 1<=width<=2000 or not 1<=height<=2000:raise ValueError('Invalid map dimensions')
    start=r.pos
    # Four native Integer fields per cell. Their meanings are kept explicit until checked against native drawing.
    cells=[];spawns=[]
    for x in range(width):
        for y in range(height):
            cell=[r.short() for _ in range(4)];cells.append(cell)
            if cell[2]==6:
                monster=r.string();spawns.append({'x':x,'y':y,'monsterId':cell[3],'name':monster})
    tailStart=r.pos;tail=data[tailStart:];tailText=bytes(x^r.key for x in tail).decode('gb18030',errors='replace')
    # Preserve every native script and its exact location, even before the surrounding entity record is decoded.
    scripts=[]
    for pos in range(max(0,tailStart-1000),len(data)-4):
        length=struct.unpack_from('<I',data,pos)[0]^r.key
        if not 8<=length<=100000 or pos+4+length>len(data):continue
        bb=data[pos+4:pos+4+length]
        txt=bytes(x^r.key for x in bb).decode('gb18030',errors='replace')
        if txt.lstrip().lower().startswith(('#sub ','#buy','#notui','#p ')) and '\ufffd' not in txt:
            scripts.append({'offset':pos,'text':txt})
    portalCount=r.short();portals=[]
    if not 0<=portalCount<=10000:raise ValueError('Invalid portal count '+str(portalCount))
    for _ in range(portalCount):
        x,y,tx,ty=[r.short() for _ in range(4)];target=r.string();portals.append({'x':x,'y':y,'targetX':tx,'targetY':ty,'target':target})
    npcCount=r.short();npcs=[]
    if not 0<=npcCount<=10000:raise ValueError('Invalid NPC count '+str(npcCount))
    for _ in range(npcCount):
        x,y,appearance,direction=[r.short() for _ in range(4)];npcName=r.string();script=r.string();npcs.append({'x':x,'y':y,'appearance':appearance,'direction':direction,'name':npcName,'script':script})
    loadScript=r.string() if r.pos+4<=len(data) else ''
    result={'id':p.stem,'name':name,'home':home,'width':width,'height':height,'cells':cells,'cellOrder':'x-major','spawns':spawns,'portals':portals,'npcs':npcs,'loadScript':loadScript,'scripts':scripts,'nativeTail':tail.hex(),'source':str(p.relative_to(SOURCE)).replace('\\','/'),'sourceSha256':hashlib.sha256(data).hexdigest(),'gridOffset':start,'tailOffset':tailStart,'unmappedTail':data[r.pos:].hex(),'entitySchemaVerified':True}
    write(OUT/'maps'/f'{p.stem}.json',result)
    return {k:result[k] for k in ('id','name','home','width','height','source','sourceSha256','entitySchemaVerified')}

def image_signature(data,pos):return data[pos:pos+2]==b'BM' or data[pos:pos+8]==b'\x89PNG\r\n\x1a\n' or data[pos:pos+6] in (b'GIF89a',b'GIF87a') or data[pos:pos+3]==b'\xff\xd8\xff'

def container(data):
    # The native files encode each numeric field, not every byte of the whole file.
    for numberSize,kind in ((2,2),(4,1)):
        for countOffset in (10,11,9,12):
            if len(data)<countOffset+numberSize+8:continue
            base=countOffset+numberSize
            keys=[data[3]^kind]+[k for k in range(256) if k!=data[3]^kind]
            for key in keys:
                count=int.from_bytes(data[countOffset:base],'little')^key
                if not 1<=count<=20000 or base+count*8>len(data):continue
                pos=(struct.unpack_from('<I',data,base)[0]^key)-1
                length=struct.unpack_from('<I',data,base+4)[0]^key
                prefix=4 if numberSize==2 else 0
                if pos!=base+count*8 or length<12 or pos+prefix+length>len(data) or not image_signature(data,pos+prefix):continue
                records=[];valid=True
                for i in range(count):
                    p=(struct.unpack_from('<I',data,base+i*8)[0]^key)-1;l=struct.unpack_from('<I',data,base+i*8+4)[0]^key
                    if p<base+count*8 or p+prefix+l>len(data) or not image_signature(data,p+prefix):valid=False;break
                    x=y=0
                    if prefix:
                        x,y=(struct.unpack_from('<H',data,p+j*2)[0]^key for j in range(2));x=x-65536 if x&32768 else x;y=y-65536 if y&32768 else y
                    records.append((p+prefix,l,x,y))
                if valid:return records,numberSize==2,key
    raise ValueError('No validated native image table')

def pack(p):
    data=p.read_bytes();records,animated,key=container(data);relative=p.relative_to(SOURCE/'Data').with_suffix('');name=str(relative).replace('\\','/');directory=OUT/'sprites'/relative;directory.mkdir(parents=True,exist_ok=True)
    pageSize=2048;pages=[];frames=[];image=Image.new('RGBA',(pageSize,pageSize));x=y=row=0;page=0;used=False
    def finish():
        nonlocal image,x,y,row,page,used
        if used:
            file=f'{page}.png';image.save(directory/file,compress_level=6);pages.append({'file':f'sprites/{name}/{file}','width':pageSize,'height':pageSize});page+=1
        image=Image.new('RGBA',(pageSize,pageSize));x=y=row=0;used=False
    for i,(offset,length,ox,oy) in enumerate(records):
        source=Image.open(io.BytesIO(data[offset:offset+length]));rgba=source.convert('RGBA')
        if source.format=='BMP' and (animated or (name.startswith('Map/Res/') and 'Floor' not in name)):
            rr,gg,bb,aa=rgba.split();mask=ImageChops.lighter(ImageChops.lighter(rr,gg),bb).point(lambda v:255 if v else 0);rgba.putalpha(ImageChops.multiply(aa,mask))
        elif source.format=='BMP':
            if source.mode=='P':
                mask=source.point(lambda index:0 if index==0 else 255,'L');rgba.putalpha(mask)
            else:
                pixels=rgba.load()
                for yy in range(rgba.height):
                    for xx in range(rgba.width):
                        if pixels[xx,yy][:3]==(0,0,0):pixels[xx,yy]=(0,0,0,0)
        original=[rgba.width,rgba.height];bounds=rgba.getbbox() or (0,0,1,1);cropped=rgba.crop(bounds);w,h=cropped.size
        if w+2>pageSize or h+2>pageSize:raise ValueError('Image exceeds atlas size')
        if x+w+2>pageSize:x=0;y+=row;row=0
        if y+h+2>pageSize:finish()
        image.paste(cropped,(x+1,y+1));frames.append({'page':page,'rect':[x+1,y+1,w,h],'original':original,'crop':[bounds[0],bounds[1]],'offset':[ox,oy],'sourceOffset':offset,'sourceBytes':length,'gifFrames':getattr(source,'n_frames',1)});x+=w+2;row=max(row,h+2);used=True
    finish();value={'id':name,'source':str(p.relative_to(SOURCE)).replace('\\','/'),'sha256':hashlib.sha256(data).hexdigest(),'nativeAnimation':animated,'key':key,'pages':pages,'frames':frames,'firstFrameMetadata':frames[0]['offset'] if animated else None,'actionSchemaVerified':False}
    write(directory/'index.json',value)
    return {'id':name,'file':f'sprites/{name}/index.json','frames':len(frames),'pages':len(pages),'nativeAnimation':animated,'sha256':value['sha256']}

def main():
    OUT.mkdir(parents=True,exist_ok=True);REPORT.mkdir(parents=True,exist_ok=True)
    report={'source':str(SOURCE),'startedAt':time.strftime('%Y-%m-%dT%H:%M:%S'),'items':items(),'monsters':monsters(),'errors':[]}
    maps=[]
    for p in sorted((SOURCE/'Data/Map').glob('*.lpMap')):
        try:maps.append(map_file(p))
        except Exception as e:report['errors'].append({'source':str(p.relative_to(SOURCE)),'error':str(e)})
    write(OUT/'data/maps.json',maps);report['maps']=len(maps)
    tasks=(SOURCE/'Mstm.dat').read_bytes().decode('gb18030');write(OUT/'data/tasks.json',{'source':'Mstm.dat','text':tasks})
    helpDocs={}
    for p in (SOURCE/'Help').glob('*.htm'):
        text=p.read_text(encoding='utf-8',errors='replace');text=re.sub(r'<script\b.*?</script>|<style\b.*?</style>','',text,flags=re.S|re.I);text=re.sub(r'<[^>]+>',' ',text);text=re.sub(r'\s+',' ',text).replace('&nbsp;',' ')
        helpDocs[p.stem]=text
    write(OUT/'data/help.json',helpDocs)
    exe=(SOURCE/'LP传奇单机版_重生.exe').read_bytes();start=exe.find('基本剑术'.encode('utf-16le'));end=exe.find('地狱雷光'.encode('utf-16le'),start)+8;native=exe[start:end].decode('utf-16le');names=[s for s in re.split(r'[\x00-\x1f]+',native) if s and s not in ('级','战士','道士','法师')];write(OUT/'data/skills.json',{'source':'LP传奇单机版_重生.exe','offset':start,'names':names,'nativeText':native,'formulasVerified':False})
    # Native configuration bytes and decoded text are retained alongside mapped tables.
    for name,kind in (('Config.dat',8),('Cil.dat',8)):
        b=(SOURCE/name).read_bytes();write(OUT/'data'/f'{name}.json',{'source':name,'sha256':hashlib.sha256(b).hexdigest(),'nativeHex':b.hex(),'decodedText':bytes(x^(b[3]^kind) for x in b[10:]).decode('gb18030',errors='replace'),'schemaVerified':False})
    packs=json.loads((OUT/'data/packs.json').read_text(encoding='utf8')) if '--config-only' in sys.argv and (OUT/'data/packs.json').exists() else []
    if '--config-only' in sys.argv:
        exported={p['id'] for p in packs}
        for p in sorted((SOURCE/'Data').rglob('*.lpRes')):
            if p.name=='Item0.lpRes' or p==SOURCE/'Data/Mon/0.lpRes':continue
            if str(p.relative_to(SOURCE/'Data').with_suffix('')).replace('\\','/') not in exported:
                report['errors'].append({'source':str(p.relative_to(SOURCE)).replace('\\','/'),'error':'No exported image pack; preserve original bytes and investigate special/truncated format'})
    if '--config-only' not in sys.argv:
        files=sorted((SOURCE/'Data').rglob('*.lpRes'));last=time.monotonic()
        for i,p in enumerate(files):
            if p.name=='Item0.lpRes' or p==SOURCE/'Data/Mon/0.lpRes':continue
            try:packs.append(pack(p))
            except Exception as e:report['errors'].append({'source':str(p.relative_to(SOURCE)),'error':str(e)})
            if time.monotonic()-last>5:print(json.dumps({'phase':'sprites','done':i+1,'total':len(files),'packs':len(packs),'errors':len(report['errors'])}),flush=True);last=time.monotonic()
        sounds=[]
        for p in (SOURCE/'Data/Sound').rglob('*.wav'):
            relative=p.relative_to(SOURCE/'Data');target=OUT/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target);sounds.append({'id':str(relative).replace('\\','/'),'name':p.stem,'bytes':p.stat().st_size})
        write(OUT/'data/sounds.json',sounds)
        ui=OUT/'ui';ui.mkdir(exist_ok=True)
        for p in (SOURCE/'Data/Button').glob('*.gif'):Image.open(p).convert('RGBA').save(ui/(p.stem+'.png'))
        write(OUT/'data/packs.json',packs)
    report['packs']=len(packs);report['frames']=sum(p['frames'] for p in packs);report['finishedAt']=time.strftime('%Y-%m-%dT%H:%M:%S');write(REPORT/'lp-extraction.json',report);print(json.dumps(report,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
