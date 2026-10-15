from pathlib import Path
import json,numpy as np
from PIL import Image
p=Path(__file__).resolve().parent;g=json.loads((p/'geometry-diagnostic.json').read_text());sp=np.array([r['source_xy']for r in g['points']]);cp=np.array([r['candidate_xy']for r in g['points']]);out={}
for name,ix in [('support',list(range(5))),('roof',list(range(5,8)))]:
 s=sp[ix];c=cp[ix];scale=float(((c-c.mean(0))*(s-s.mean(0))).sum()/((c-c.mean(0))**2).sum());t=s.mean(0)-scale*c.mean(0);e=scale*cp+t-sp;out[name]={'scale':scale,'translation':t.tolist(),'fitted_group_rms':float(np.sqrt((e[ix]**2).sum(1).mean())),'all8_errors':e.tolist(),'not_applied_to_asset':True}
a=np.array(Image.open(p/'raw.png').getchannel('A'));y,x=np.where(a>32);out['alpha32_measurement_only']={'bounds':[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)],'margins':[int(x.min()),int(y.min()),int(a.shape[1]-x.max()-1),int(a.shape[0]-y.max()-1)],'alpha_was_not_modified':True};(p/'independent-support-roof-check.json').write_text(json.dumps(out,indent=2)+'\n');print(out['alpha32_measurement_only'])
