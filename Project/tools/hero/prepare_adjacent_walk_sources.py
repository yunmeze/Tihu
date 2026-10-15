"""Prepare exact original E/S six-phase walking references, without editing source pixels.
This is source preparation only; it does not generate art or alter runtime manifests.
"""
from pathlib import Path
from PIL import Image
import json, hashlib
ROOT=Path(__file__).resolve().parents[2]
M=ROOT/'data/hero/movement.json'
m=json.loads(M.read_text())
H=lambda data:hashlib.sha256(data).hexdigest()
for direction, ids in [('E',list(range(45,51))),('S',list(range(57,63)))]:
    out=ROOT/'art_source'/f'hero_{direction.lower()}_walk_source_r8'
    out.mkdir(exist_ok=True)
    board=Image.new('RGBA',(384,256)); strip=Image.new('RGBA',(768,128)); frames=[]; records=[]
    for i,fid in enumerate(ids):
        composite=Image.new('RGBA',(128,128)); record={'source_id':fid,'layers':{}}
        for name in ['body','head']:
            layer=m['layers'][name]; f=layer['frames'][str(fid)]
            atlas=Image.open(ROOT/layer['atlas'].removeprefix('res://')).convert('RGBA')
            x,y,w,h=f['rect']; tile=atlas.crop((x,y,x+w,y+h))
            assert H(tile.tobytes())==f['rgba_sha256']
            ox,oy=f['offset']; composite.alpha_composite(tile,(16+ox,64+oy))
            record['layers'][name]={k:f[k] for k in ['original','offset','rgba_sha256','sourceOffset','sourceBytes']}
        composite.save(out/f'source-{fid}.png'); frames.append(composite)
        record['composite_rgba_sha256']=H(composite.tobytes()); records.append(record)
        strip.paste(composite,(i*128,0)); board.paste(composite,((i%3)*128,(i//3)*128))
    strip.save(out/'original-six-native-strip.png')
    board.resize((2304,1536),Image.Resampling.NEAREST).save(out/'original-six-complete-canvas-6x.png')
    pairs=[{'source_ids':[ids[a],ids[b]],'changed_pixel_count':sum(x!=y for x,y in zip(frames[a].getdata(),frames[b].getdata()))} for a in range(6) for b in range(a+1,6)]
    info={'status':'source_preparation_only_no_generation','direction':direction,'source_ids':ids,'native_canvas':[128,128],'native_root':[16,64],'main_grid':[3,2],'main_magnification':6,'crop':None,'frame_ticks':7,'timing_boundary':'Current/reference walk clip cadence; not independent EXE transition or movement-speed proof.','transparency':'Audited exact-black transparency only. All remaining body/head RGBA including RGB16,8,8 checker and clothing retained.','original_manifest_sha256':H(M.read_bytes()),'records':records,'pairwise_comparison':pairs}
    (out/'source-provenance.json').write_text(json.dumps(info,indent=2)+'\n')
    assert all(p['changed_pixel_count']>0 for p in pairs)
print('Prepared original E45-50 and S57-62 full source canvases; all six frames differ in each group.')
