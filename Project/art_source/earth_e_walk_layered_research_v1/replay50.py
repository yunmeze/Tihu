"""Deterministic replay into an explicitly supplied output directory; no generation, no production writes.
Usage: python replay50.py --output /path/to/replay
Requires Pillow and numpy. Frozen aliases are never overwritten.
"""
from pathlib import Path
import argparse,hashlib,json
from PIL import Image
import numpy as np
P=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();O=Path(args.output).resolve()
assert O!=P and P not in O.parents,'Use output outside frozen package';O.mkdir(parents=True,exist_ok=True)
load=lambda p:Image.open(p).convert('RGBA');C=P/'source/50_context';K=P/'source/50_knee';old=load(C/'input-context.png');pr=load(C/'protected-original-layers.png');raw=load(C/'raw.png');m=np.array(Image.open(C/'proposed-fixed-union-mask.png'))>0;q=raw.width/512
mapped=raw.transform((512,512),Image.Transform.AFFINE,(q,0,0,0,q,0),resample=Image.Resampling.BICUBIC);d=np.array(mapped);d[~m,3]=0;a=np.array(old);a[m]=np.array(Image.alpha_composite(Image.fromarray(d),pr))[m];first=Image.fromarray(a);first.save(O/'50-context-replay.png')
raw=load(K/'raw.png');assert raw.width==raw.height;crop=raw.resize((96,96),Image.Resampling.LANCZOS);d=Image.new('RGBA',(512,512));d.alpha_composite(crop,(136,232));m=np.array(Image.open(K/'frozen-full512-mask.png'))>0;da=np.array(d);da[~m,3]=0;a[m]=np.array(Image.alpha_composite(Image.fromarray(da),pr))[m];out=Image.fromarray(a);out.save(O/'50-local-knee-replay.png');expected=np.array(load(P/'50-HD4-RESEARCH.png'));assert np.array_equal(a,expected),'Replay pixel mismatch';print('50 replay pixel-identical to frozen alias; original input hashes in manifest')
