"""Validate shipped atlas samples against raw original frames, without rewriting assets."""
from pathlib import Path
import hashlib,json,argparse
from PIL import Image
from lp_original import read_pack,decode_frame
P=Path(__file__).resolve().parents[1];R=P.parent
ap=argparse.ArgumentParser();ap.add_argument('--manifest',default='assets/original/manifest.json');args=ap.parse_args();manifest=json.load(open(P/args.manifest));map_id=manifest.get('map',manifest.get('r1_map','A13'));count=0;pages=0
for name,pack in manifest['packs'].items():
 source=R/pack['source'];assert hashlib.sha256(source.read_bytes()).hexdigest()==pack['source_sha256']
 data,records,animated,key=read_pack(source);assert len(records)==pack['total_source_records'];atlas=[]
 for page in pack['pages']:
  path=P/page['file'].removeprefix('res://');assert hashlib.sha256(path.read_bytes()).hexdigest()==page['sha256'];im=Image.open(path).convert('RGBA');assert list(im.size)==page['size'];atlas.append(im);pages+=1
 for index,f in pack['frames'].items():
  x,y,w,h=f['rect'];a=atlas[f['page']];assert x>=0 and y>=0 and x+w<=a.width and y+h<=a.height
  raw,meta=decode_frame(data,records[int(index)],name,animated);cx,cy=f['crop'];expected=raw.crop((cx,cy,cx+w,cy+h));actual=a.crop((x,y,x+w,y+h));assert actual.tobytes()==expected.tobytes(),(name,index,'RGBA')
  assert f['original']==meta['original']and f['offset']==meta['offset']and f['rgba_sha256']==meta['rgba_sha256'];count+=1
out={'status':'PASS','frames_redecoded_and_compared':count,'atlas_pages_checked':pages,'sample_bounds_violations':0,'source_files_hash_verified':len(manifest['packs']),'assets_rewritten':False};dest=P/'diagnostics/maps'/f'{map_id}-raw-atlas-verification.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
