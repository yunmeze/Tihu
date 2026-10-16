from pathlib import Path
import numpy as np,json
from PIL import Image
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
O=Path(__file__).parent;R=O.parent;a=np.array(Image.open(R/'south-walk-mesh-correction-v1/raw/58.png'))[:,:,3];c=np.maximum(*[np.array(Image.open(R/f'south-walk-arm5861-proposal-v1/revision3/58-{k}-classes.png')) for k in ['L','R']]);y,x=np.where(a>0);idx=np.full(a.shape,-1,int);idx[y,x]=np.arange(len(x));edges=[]
for dx,dy in [(1,0),(0,1)]:
 ok=(x+dx<512)&(y+dy<512);s=idx[y[ok],x[ok]];t=idx[y[ok]+dy,x[ok]+dx];v=t>=0;edges.append(np.stack([s[v],t[v]],1))
e=np.concatenate(edges);s,t=e.T;G=coo_matrix((np.ones(2*len(e)),(np.r_[s,t],np.r_[t,s])),shape=(len(x),len(x))).tocsr();moving=np.where((a[y,x]>=64)&(c[y,x]==2))[0];body=np.where((a[y,x]>=64)&(c[y,x]==0))[0];dm=dijkstra(G,directed=False,indices=moving,min_only=True);db=dijkstra(G,directed=False,indices=body,min_only=True);points=[]
for xx,yy in [(135,158),(285,230),(286,232),(286,233)]:
 k=idx[yy,xx];points.append({'raw_pixel':[xx,yy],'alpha':int(a[yy,xx]),'steps_to_visible_gauntlet_core':float(dm[k]),'steps_to_fixed_visible_material':float(db[k]),'nearest_core':'moving_arm' if dm[k]<db[k] else 'fixed_material' if db[k]<dm[k] else 'tie'})
oldrig=(c[y,x]==2)&(a[y,x]<64);result={'graph':'4-neighbor occupied alpha>0 pixel graph, no path across alpha0; distance is topology proxy not anatomical attachment','limiting_points':points,'old_rigid_weak_alpha_pixels':int(oldrig.sum()),'old_rigid_weak_pixels_closer_fixed_core':int((oldrig&(db<dm)).sum()),'proposal':'rigid translation seeds only complete visible alpha>=64 gauntlet core; weak-alpha is extension, never automatically same rigid patch; preserve fixed visible material and approved whole fixed head/legs; freeze ownership ambiguity separately before any solve'};(O/'SUPPORT_ATTACHMENT_EVIDENCE.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
