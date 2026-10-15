#!/usr/bin/env python3
"""Reproducible original Hero2/Head0 action layers, separate from movement interface."""
import hashlib, io, json, sys
from pathlib import Path
from PIL import Image,ImageDraw
PROJECT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(PROJECT/'tools'))
from lp_original import read_pack,decode_frame
sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
    assets=PROJECT/'assets/original/hero';out=PROJECT/'data/hero';diag=PROJECT/'diagnostics/hero/actions'
    for p in [assets,out,diag]:p.mkdir(parents=True,exist_ok=True)
    actions={'attack':{'base':129,'phases':6},'cast':{'base':177,'phases':6},'hurt':{'base':225,'phases':3},'death':{'base':249,'phases':4}}
    dirs=['N','NE','E','SE','S','SW','W','NW']; layers={};decoded={};checks=[]
    for part,pack in [('body','Hero/2'),('head','Hero/Head/0')]:
        path=PROJECT.parent/'原版游戏/Data'/f'{pack}.lpRes';data,records,animated,key=read_pack(path)
        assert len(records)==281 and animated
        atlas=Image.new('RGBA',(2048,1280));frames={};decoded[part]={};nonblack_checked=0;dark_subject_or_shadow=0
        for i in range(129,281):
            im,m=decode_frame(data,records[i],pack,animated);assert im.width<=126 and im.height<=126
            original=Image.open(io.BytesIO(data[m['sourceOffset']:m['sourceOffset']+m['sourceBytes']])).convert('RGBA')
            for before,after in zip(original.getdata(),im.getdata()):
                assert before[:3]==after[:3]
                if before[:3]!=(0,0,0): assert before==after;nonblack_checked+=1
                if before[:3]==(16,8,8):assert before==after;dark_subject_or_shadow+=1
            x=((i-129)%16)*128+1;y=((i-129)//16)*128+1;atlas.paste(im,(x,y))
            frames[str(i)]={**m,'rect':[x,y,im.width,im.height]};decoded[part][i]=im
        file=assets/f'{part}-actions.png';atlas.save(file);back=Image.open(file).convert('RGBA')
        for m in frames.values():
            x,y,w,h=m['rect'];assert sha(back.crop((x,y,x+w,y+h)).tobytes())==m['rgba_sha256']
        assert path.read_bytes()==data
        layers[part]={'pack':pack,'source':str(path.relative_to(PROJECT.parent)),'source_sha256':sha(data),'source_records':281,'atlas':'res://'+str(file.relative_to(PROJECT)),'atlas_size':list(atlas.size),'atlas_sha256':sha(file.read_bytes()),'frames':frames}
        checks.append({'part':part,'full_rgba_atlas_roundtrip':True,'source_unchanged':True,'nonblack_rgba_preserved_count':nonblack_checked,'rgb_16_8_8_preserved_count':dark_subject_or_shadow})
    manifest={'schema':'original-hero-actions-v1','appearance':{'body':2,'head':0,'weapon':None},'directions':dirs,'actions':actions,'index_formula':'base + direction * phases + phase (phase starts at zero)','draw_order':['body','head'],'placement':'actor_draw_origin + native frame.offset; no bbox normalization','transparency':'Only exact RGB0,0,0 becomes alpha0. All nonblack RGBA retained, including native checker and dark body/head.','timing_evidence':'docs/HERO_ACTION_TIMING_EVIDENCE.md; no runtime timing/event authorization from this asset manifest','runtime_status':'source-assets-only; not automatically wired into R1','layers':layers}
    dump(out/'actions.json',manifest)
    observations=[]
    for action,clip in actions.items():
        for d,name in enumerate(dirs):
            sheet=Image.new('RGBA',(clip['phases']*192,208),(84,84,84,255));label=ImageDraw.Draw(sheet)
            for phase in range(clip['phases']):
                idx=clip['base']+d*clip['phases']+phase;tile=Image.new('RGBA',(192,192));layer_boxes={}
                for part in ['body','head']:
                    m=layers[part]['frames'][str(idx)];ox,oy=m['offset'];im=decoded[part][idx]
                    assert 0<=48+ox and 0<=80+oy and 48+ox+im.width<=192 and 80+oy+im.height<=192
                    tile.alpha_composite(im,(48+ox,80+oy));layer_boxes[part]={'native_offset':m['offset'],'alpha_bbox_local':im.getbbox()}
                sheet.alpha_composite(tile,(phase*192,16));label.text((phase*192+3,2),f'{action} {name} #{idx}',fill='white')
                observations.append({'source_id':idx,'action':action,'direction':name,'phase':phase,'layer_bounds':layer_boxes,'joint_annotations':'not measured; no fabricated hidden joints'})
            sheet.convert('RGB').save(diag/f'{action}-{name}-source.jpg',quality=94)
    for action in actions:
        for first in (0,4):
            strips=[Image.open(diag/f'{action}-{d}-source.jpg') for d in dirs[first:first+4]]
            board=Image.new('RGB',(strips[0].width,832))
            for row,im in enumerate(strips): board.paste(im,(0,row*208))
            board.save(diag/f'{action}-directions-{first}-{first+3}.jpg',quality=94)
    dump(out/'action-frame-index.json',{'frames':observations,'preview_only_origin':[48,80],'preview_canvas':[192,192],'note':'bounds include checker shadow; not inferred body joints or physical contact'})
    dump(diag/'extraction-validation.json',{'passed':True,'source_frames':152,'layer_frames':304,'checks':checks,'manifest_sha256':sha((out/'actions.json').read_bytes()),'script_sha256':sha(Path(__file__).read_bytes())})
    print(json.dumps({'passed':True,'phases':152,'layers':304,'atlas_hashes':{p:v['atlas_sha256'] for p,v in layers.items()}},indent=2))
if __name__=='__main__':main()
