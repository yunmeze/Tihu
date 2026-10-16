from pathlib import Path
import argparse,json,hashlib
import numpy as np
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=Path(__file__).resolve().parent;c=json.loads((r/'ARCHIVE.json').read_text())
for n,v in c['inputs'].items():assert hashlib.sha256((r/n).read_bytes()).hexdigest()==v['sha256'],n
out={}
if c['mode']=='wall':
 owners=json.loads((r/'SOURCE_NINE_OWNERS.json').read_text())['owners']
 for call in c['calls']:
  im=Image.open(r/call['raw']).convert('RGBA');ar=np.asarray(im)[:,:,3];d=im.width/384;assert im.width==im.height;x=(np.arange(im.width)+.5)/d+840;y=(np.arange(im.height)+.5)/d+221;u=np.zeros(ar.shape,bool)
  for o in owners:
   l,t,rr,b=o['all_frame_bounds_xyxy'];u|=(x[None,:]>=l)&(x[None,:]<rr)&(y[:,None]>=t)&(y[:,None]<b)
  counts={str(t):int(((ar>=t)&~u).sum()) for t in [1,8,32,128,250]};expected=json.loads((r/call['phase']/'measurements.json').read_text())['outside_original_owner_rectangle_union'];assert counts==expected
  out[call['phase']]={'outside_original_owner_rectangle_union':counts,'raw_rgba_sha256':hashlib.sha256(im.tobytes()).hexdigest()}
else:
 im=Image.open(r/'RAW.png').convert('RGBA');assert im.size==(1536,1024);arr=np.asarray(im);layout=json.loads((r/'INPUT_LAYOUT.json').read_text());board=Image.new('RGBA',(1536,1024))
 for s in layout['source_tiles']:
  q=Image.open(r/'references'/s['reference_file']).convert('RGBA');assert hashlib.sha256(q.tobytes()).hexdigest()==s['source_rgba_sha256'];z=s['output_slot_xyxy_density8'];board.paste(q.resize((768,512),Image.Resampling.NEAREST),(z[0],z[1]))
 assert board.tobytes()==Image.open(r/'references/SOURCE_SLOT_REFERENCE_D8.png').convert('RGBA').tobytes()
 for i,n in enumerate(['G2','G3','F413','UNUSED']):
  al=arr[i//2*512:(i//2+1)*512,i%2*768:(i%2+1)*768,3];out[n]={'alpha_histogram':np.bincount(al.ravel(),minlength=256).tolist(),'nonzero':int((al>0).sum())}
 assert out['UNUSED']['nonzero']==5081
 out['application']='none: no normalization, extraction, placement, alpha modification or catalog application'
a.output.mkdir(parents=True,exist_ok=True);(a.output/'REPLAY.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS exact inputs and technical layout/support replay; no art modification')
