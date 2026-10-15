#!/usr/bin/env python3
"""Deterministic Hero/2 + Hero/Head/0 extraction; no source writes or art edits."""
import hashlib, json, sys
from pathlib import Path
from PIL import Image, ImageDraw
PROJECT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(PROJECT/'tools'))
from lp_original import read_pack, decode_frame

def sha(b): return hashlib.sha256(b).hexdigest()
def dump(path,value): path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
    assets=PROJECT/'assets/original/hero'; assets.mkdir(parents=True,exist_ok=True)
    out=PROJECT/'data/hero'; out.mkdir(parents=True,exist_ok=True)
    diagnostics=PROJECT/'diagnostics/hero'; diagnostics.mkdir(parents=True,exist_ok=True)
    packs={}; decoded={}; checks=[]
    for part,pack in [('body','Hero/2'),('head','Hero/Head/0')]:
        source=PROJECT.parent/'原版游戏/Data'/f'{pack}.lpRes'
        data,records,animated,key=read_pack(source)
        assert animated and len(records)>=129
        atlas=Image.new('RGBA',(16*128,8*128))
        frames={}; decoded[part]={}
        for index in range(1,129):
            im,meta=decode_frame(data,records[index],pack,animated)
            assert im.width<=126 and im.height<=126
            x=((index-1)%16)*128+1; y=((index-1)//16)*128+1
            atlas.paste(im,(x,y)) # no mask: preserves every RGBA byte, including alpha-zero RGB
            frames[str(index)]={**meta,'rect':[x,y,im.width,im.height]}
            decoded[part][index]=im
        file=assets/f'{part}-movement.png'; atlas.save(file)
        reread=Image.open(file).convert('RGBA')
        for key_id,meta in frames.items():
            x,y,w,h=meta['rect']; assert sha(reread.crop((x,y,x+w,y+h)).tobytes())==meta['rgba_sha256']
        assert source.read_bytes()==data
        packs[part]={'pack':pack,'source':str(source.relative_to(PROJECT.parent)),
          'source_sha256':sha(data),'source_records':len(records),'metadata_record_0':list(records[0]),
          'atlas':'res://'+str(file.relative_to(PROJECT)),'atlas_sha256':sha(file.read_bytes()),
          'atlas_size':list(atlas.size),'frames':frames}
        checks.append({'part':part,'decoded_frames':128,'atlas_rgba_roundtrip':True,'source_unchanged':True})
    actions={'idle':{'base':1,'phases':4,'actor_ticks_per_phase':12},
      'walk':{'base':33,'phases':6,'actor_ticks_per_phase':7},
      'run':{'base':81,'phases':6,'actor_ticks_per_phase':5}}
    manifest={'schema':'original-hero-movement-v1','appearance':{'body':2,'head':0,'weapon':None},
      'directions':['N','NE','E','SE','S','SW','W','NW'],'actions':actions,
      'index_formula':'base + direction * phases + phase; phase starts at 0',
      'source_record_zero_is_not_animation':True,
      'draw_order':['body','head'],'placement':'layer_top_left = actor_draw_origin + frame.offset; no centering, scaling or crop offset',
      'anchor':{'kind':'native_draw_origin','coordinate':[0,0],'note':'Use shared actor draw origin for both layers. This is not measured boot contact. No inferred foot recentering.'},
      'transparency':'Only exact RGB 0,0,0 is transparent for these animated BMPs. All nonblack pixels, including RGB16,8,8 native checker shadow and body/head colors, are retained.',
      'timing_scope':'Clip frame cadence from reference animation.js. Transition/state clock semantics and original movement speed are outside this extraction.',
      'reference_files':['参考项目/tools/extract-lp.py','参考项目/src/animation.js','参考项目/src/appearance.js','参考项目/src/batch.js'],
      'layers':packs}
    dump(out/'movement.json',manifest)
    dump(diagnostics/'extraction-validation.json',{'passed':True,'frames':128,'layers':256,'checks':checks,
      'manifest_sha256':sha((out/'movement.json').read_bytes()),'extractor_sha256':sha(Path(__file__).read_bytes())})
    board=Image.new('RGBA',(8*128,3*144),(85,85,85,255)); d=ImageDraw.Draw(board)
    for row,(action,clip) in enumerate(actions.items()):
        for direction in range(8):
            idx=clip['base']+direction*clip['phases']; tile=Image.new('RGBA',(128,128))
            for part in ['body','head']:
                ox,oy=packs[part]['frames'][str(idx)]['offset']; tile.alpha_composite(decoded[part][idx],(16+ox,64+oy))
            board.alpha_composite(tile,(direction*128,row*144+16))
            d.text((direction*128+3,row*144+2),f'{action} {manifest["directions"][direction]} #{idx}',fill='white')
    board.convert('RGB').save(diagnostics/'movement-source-contact-sheet.jpg',quality=92)
    for action,clip in actions.items():
        phases=clip['phases']; grid=Image.new('RGBA',(8*128,phases*144),(85,85,85,255)); label=ImageDraw.Draw(grid)
        for direction in range(8):
            for phase in range(phases):
                idx=clip['base']+direction*phases+phase; tile=Image.new('RGBA',(128,128))
                for part in ['body','head']:
                    ox,oy=packs[part]['frames'][str(idx)]['offset']; im=decoded[part][idx]
                    assert 0<=16+ox and 0<=64+oy and 16+ox+im.width<=128 and 64+oy+im.height<=128
                    tile.alpha_composite(im,(16+ox,64+oy))
                grid.alpha_composite(tile,(direction*128,phase*144+16))
                label.text((direction*128+3,phase*144+2),f'{action} {manifest["directions"][direction]} #{idx}',fill='white')
        grid.convert('RGB').save(diagnostics/f'{action}-all-phases.jpg',quality=92)
    print(json.dumps({'passed':True,'manifest':str(out/'movement.json'),'frames':128,'layers':256,'atlas_sha256':{p:v['atlas_sha256'] for p,v in packs.items()}},indent=2))
if __name__=='__main__': main()
