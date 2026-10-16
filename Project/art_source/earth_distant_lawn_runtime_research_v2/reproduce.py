"""Deterministic mapping and purecore composition; generation itself is stochastic."""
import argparse,pathlib,hashlib,json
import numpy as np
from PIL import Image
p=pathlib.Path(__file__).parent;a=argparse.ArgumentParser();a.add_argument('project');a.add_argument('output');args=a.parse_args();root=pathlib.Path(args.project);out=pathlib.Path(args.output);out.mkdir(parents=True,exist_ok=True)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
B=root/'art_source/earth_coherent_grass_research_v1/coherent-grass-union-RESEARCH.png';M=root/'art_source/earth_coherent_grass_research_v1/grass-core-conservative.png'
assert sha(B)=='d6bf26a3bd518798ca1ecdde9ebc3be9e722f64034acc42303bc87128a72a4c4';assert sha(M)=='d40582eddfc1b8b86c57aabcdf420c954e7f96cc7e2b1c53b2493f8674b9cb84';assert sha(p/'RAW.png')=='7b016af52b7e82b71de562a7683089429abf2bd679cae01062c3a0f9c906db11'
request=json.loads((p/'REQUEST_FROZEN.json').read_text());assert request['actual_references']==[] and request['transparent_background'] is False and sha(p/'PROMPT.txt')==request['prompt_sha256']
im=Image.open(p/'RAW.png').convert('RGBA');assert im.size==(1254,1254) and im.getchannel('A').getextrema()==(255,255)
im=im.resize((768,768),Image.Resampling.LANCZOS);im.save(out/'tile.png');t=np.array(im);b=np.array(Image.open(B).convert('RGBA'));m=np.array(Image.open(M))>0;y,x=np.indices(m.shape);z=b.copy();z[m,:3]=t[(1920+y)%768,(4800+x)%768,:3][m]
assert m.sum()==2373576 and np.array_equal(z[~m],b[~m]) and np.array_equal(z[:,:,3],b[:,:,3]);Image.fromarray(z).save(out/'new121-core-union.png')
assert sha(out/'tile.png')=='470f2866b30b0901999e915c51cde7124c3e6532b5b4c8fa4c3d9edbfcf02b8b'
assert (out/'new121-core-union.png').read_bytes()==(p/'new121-core-union.png').read_bytes()
print('PASS exact tile and121corePNG; alpha/outside unchanged')
