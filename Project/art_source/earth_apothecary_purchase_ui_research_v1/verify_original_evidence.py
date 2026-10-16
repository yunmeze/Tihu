"""Read-only source-byte proof. Never executes the original game."""
from pathlib import Path
import argparse,json,hashlib,io
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--repo',required=True);a=p.parse_args();R=Path(a.repo);P=Path(__file__).resolve().parent;sha=lambda b:hashlib.sha256(b).hexdigest();n=json.loads((P/'original-evidence/NATIVE_EVIDENCE.json').read_text());b=(R/n['binary']).read_bytes();assert sha(b)==n['sha256'];count=0
for r in n['ranges']+n['literals']:
 chunk=b[r['file_offset']:r['file_offset']+r['bytes']];assert sha(chunk)==r['sha256'];count+=1
u=json.loads((P/'ui-evidence/UI_EVIDENCE.json').read_text());assert sha(b)==u['binary']['sha256']
for r in u['resources']:
 if 'file_offset' in r:
  raw=b[r['file_offset']:r['file_offset']+r['bytes']];assert sha(raw)==r['sha256'];assert raw==(P/'ui-evidence'/r['gif']).read_bytes()
for r in u['event_metadata_chain']+[r for values in u['controls'].values() for r in values]:assert sha(b[r['file_offset']:r['file_offset']+r['bytes']])==r['sha256']
pack=(R/'原版游戏/Data/Item1.lpRes').read_bytes()
for r in json.loads((P/'isolated/data/resource_sources.json').read_text()):
 raw=pack[r['sourceOffset']:r['sourceOffset']+r['sourceBytes']];assert sha(raw)==r['sha256'];im=Image.open(io.BytesIO(raw)).convert('RGBA');out=Image.open(P/'isolated/assets'/('item_'+str(r['id'])+'.png')).convert('RGBA');assert im.size==out.size and im.tobytes()==out.tobytes()
assert Image.open(P/'ui-evidence/ScriptBuy.gif').convert('RGBA').tobytes()==Image.open(P/'isolated/assets/panel.png').convert('RGBA').tobytes()
assert Image.open(R/'原版游戏/Data/Button/Buy.gif').convert('RGBA').tobytes()==Image.open(P/'isolated/assets/buy.png').convert('RGBA').tobytes()
print('PASS EXE SHA, native ranges/literals',count,'UI resource/control/event bytes,12 original item image RGBA,panel/button RGBA; no game execution')
