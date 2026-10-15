"""Read-only native LP resource decoding, R1 recovery.
Reader/container/signature definitions copied verbatim from the checked-in reference extractor.
No original EXE is executed. Source files are never written.
"""
import struct, io, hashlib
from pathlib import Path
from PIL import Image, ImageChops
REFERENCE_PARSER_SHA256 = "8e12bfebe9a8b026011275d84a2b06e8bb8ed255c25fadce7000654f8e065cd4"

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

def decode_frame(data, record, pack_name, animated=False):
    """Return full native RGBA and metadata; offsets remain separate from pixels."""
    offset, length, ox, oy = record
    source = Image.open(io.BytesIO(data[offset:offset+length]))
    rgba = source.convert('RGBA')
    # Same explicit BMP color-key policy as reference pack(); no semantic masking.
    if source.format == 'BMP' and (animated or (pack_name.startswith('Map/Res/') and 'Floor' not in pack_name)):
        rr, gg, bb, aa = rgba.split()
        mask = ImageChops.lighter(ImageChops.lighter(rr, gg), bb).point(lambda v:255 if v else 0)
        rgba.putalpha(ImageChops.multiply(aa, mask))
    elif source.format == 'BMP':
        if source.mode == 'P':
            rgba.putalpha(source.point(lambda index:0 if index == 0 else 255, 'L'))
        else:
            rr, gg, bb, aa = rgba.split()
            mask = ImageChops.lighter(ImageChops.lighter(rr, gg), bb).point(lambda v:255 if v else 0)
            rgba.putalpha(ImageChops.multiply(aa, mask))
    extraction_bounds = list(rgba.getbbox() or (0,0,1,1))
    # Reference tools/native-color-key.py normalizes animated/map-object PNG too.
    if animated or (pack_name.startswith('Map/Res/') and 'Floor' not in pack_name):
        rr, gg, bb, aa = rgba.split()
        mask = ImageChops.lighter(ImageChops.lighter(rr, gg), bb).point(lambda v:255 if v else 0)
        rgba.putalpha(ImageChops.multiply(aa, mask))
    return rgba, {'original':list(rgba.size),'offset':[ox,oy], 'sourceOffset':offset,
                  'sourceBytes':length,'format':source.format,'reference_extraction_bounds':extraction_bounds,'gifFrames':getattr(source,'n_frames',1),
                  'rgba_sha256':hashlib.sha256(rgba.tobytes()).hexdigest()}

def read_pack(path):
    data = Path(path).read_bytes()
    records, animated, key = container(data)
    return data, records, animated, key
