"""Validate source archive and original owner mapping; no image modification."""
from pathlib import Path
import argparse, hashlib, json
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--repo',required=True);a=p.parse_args()
R=Path(a.repo).resolve();P=Path(__file__).resolve().parent
H=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for name,sha in json.loads((P/'SHA256.json').read_text()).items():assert H(P/name)==sha,name
m=json.loads((P/'ARCHIVE.json').read_text());atlas=m['source_atlas'];assert H(R/atlas['repo_path'])==atlas['sha256'];src=Image.open(R/atlas['repo_path']).convert('RGBA')
results=[]
for asset in m['assets']:
 D=P/asset['name'];reg=json.loads((D/'REGISTRATION_CANDIDATE.json').read_text());audit=json.loads((D/'RAW_AUDIT.json').read_text());raw=P/asset['raw'];assert H(raw)==reg['raw_sha256'];im=Image.open(raw);assert im.mode=='RGBA' and im.size==(1536,1024)
 assert im.getchannel('A').histogram()==audit['alpha_histogram']
 x,y,w,h=reg['source_atlas_rect'];assert hashlib.sha256(src.crop((x,y,x+w,y+h)).tobytes()).hexdigest()==reg['source_rgba_sha256']
 for owner in reg['owners']:
  cx,cy=owner['map_cell'];assert owner['world_top_left']==[cx*48,cy*32];assert owner['world_bounds']==[cx*48,cy*32,cx*48+96,cy*32+64]
 for i,ref in enumerate(asset['actual_refs'],1):
  f=R/ref['repo_path'] if 'repo_path' in ref else P/ref['package_path'];assert ref['order']==i and H(f)==ref['sha256'] and f.stat().st_size==ref['bytes']
 results.append({'asset':asset['name'],'raw_sha256':H(raw),'refs_exact':5,'owner_count':len(reg['owners']),'source_crop_rgba_exact':True,'alpha_histogram_exact':True,'mapping':'entire1536x1024 at uniform1/16, offset0'})
print(json.dumps({'status':'PASS source validation only; no imagegen, renderer or artistic acceptance replay','results':results},indent=2))
