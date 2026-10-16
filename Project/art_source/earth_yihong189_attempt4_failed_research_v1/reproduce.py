from pathlib import Path
import argparse,json,hashlib
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--repo',required=True);p.add_argument('--output',required=True);a=p.parse_args();R=Path(a.repo);P=Path(__file__).resolve().parent;H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m=json.loads((P/'ARCHIVE.json').read_text());metrics=json.loads((P/'measurements.json').read_text())
for r in m['references']:
 f=R/r['repo_path'] if 'repo_path' in r else P/r['package_path'];assert H(f)==r['sha256']
assert H(P/'RAW.png')==m['raw_sha256'];im=Image.open(P/'RAW.png').convert('RGBA');assert im.size==(1254,1254);out=Path(a.output);assert not out.exists();out.parent.mkdir(parents=True,exist_ok=True);im.convert('RGBa').resize((384,384),Image.Resampling.LANCZOS).convert('RGBA').save(out);assert H(out)==metrics['candidate_SHA256'];print('PASS exact fixed-canvas PNG; original FAIL retained',H(out))
