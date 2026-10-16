"""Replay fixed source geometry and candidate mapping. Does not rerun generation."""
import argparse,hashlib,json,pathlib
from PIL import Image
P=pathlib.Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=argparse.ArgumentParser();a.add_argument('--project',type=pathlib.Path,default=P.parents[1]);a.add_argument('--out',type=pathlib.Path,required=True);args=a.parse_args();args.out.mkdir(parents=True,exist_ok=True)
meta=json.loads((P/'ARCHIVE.json').read_text());contract=json.loads((P/'contract-before-generation.json').read_text())
for name,digest in json.loads((P/'SHA256.json').read_text()).items():assert sha(P/name)==digest,name
for pin in meta['dependencies']:assert sha(args.project/pin['path'])==pin['sha256'],pin['path']
manifest=json.loads((args.project/'assets/original/manifest.json').read_text());source=json.loads((args.project/'data/maps/A13.json').read_text());record=meta['source_npc_record'];assert source['npcs'][record['record']]==record['npc']
pack=manifest['packs']['Npc'];page=Image.open(args.project/'assets/original/Npc/0.png').convert('RGBA');equivalence=json.loads((P/'four-id-equivalence.json').read_text());first=None
for e in equivalence:
 f=pack['frames'][str(e['id'])]
 for key in ['original','offset','crop','rect','page']:assert f[key]==e['metadata'][key]
 x,y,w,h=f['rect'];im=page.crop((x,y,x+w,y+h));assert hashlib.sha256(im.tobytes()).hexdigest()==e['rgba_sha256'];im.save(args.out/f'source-{e["id"]}.png');assert sha(args.out/f'source-{e["id"]}.png')==e['png_sha256']
 if first is None:first=im
 else:assert im.tobytes()==first.tobytes()
primary=Image.new('RGBA',(640,640));primary.alpha_composite(first.resize((384,512),Image.Resampling.NEAREST),(112,56));primary.save(args.out/'primary-source.png');assert (args.out/'primary-source.png').read_bytes()==(P/'references/primary-source.png').read_bytes()
for old,new in zip(contract['actual_refs_order'],meta['actual_generation']['references_in_order']):assert sha(P/new)==contract['actual_ref_sha256'][old]
assert sha(P/'prompt_actual.txt')==contract['prompt_sha256'];raw=Image.open(P/'raw.png').convert('RGBA');assert list(raw.size)==meta['mapping']['raw_size'];im=raw.convert('RGBa').resize((640,640),Image.Resampling.LANCZOS).convert('RGBA');im.save(args.out/'candidate837-density4.png');assert sha(args.out/'candidate837-density4.png')==meta['candidate_png_sha256'];assert hashlib.sha256(im.tobytes()).hexdigest()==meta['candidate_rgba_sha256'];print('PASS exact source4 static equivalence,actualrefs and candidate PNG/RGBA')
