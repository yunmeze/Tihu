from pathlib import Path
import numpy as np,json,hashlib
from PIL import Image,ImageDraw
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
O=Path(__file__).parent;R=O.parent;im=Image.open(R/'south-walk-mesh-correction-v1/raw/58.png').convert('RGBA');a=np.array(im)[:,:,3];old=[np.array(Image.open(R/f'south-walk-arm5861-proposal-v1/revision3/58-{k}-classes.png')) for k in ['L','R']];c=np.maximum(*old);y,x=np.where(a>0);idx=np.full(a.shape,-1,int);idx[y,x]=np.arange(len(x));edges=[]
for dx,dy in [(1,0),(0,1)]:
 ok=(x+dx<512)&(y+dy<512);s=idx[y[ok],x[ok]];t=idx[y[ok]+dy,x[ok]+dx];v=t>=0;edges.append(np.stack([s[v],t[v]],1))
e=np.concatenate(edges);s,t=e.T;G=coo_matrix((np.ones(2*len(e)),(np.r_[s,t],np.r_[t,s])),shape=(len(x),len(x))).tocsr();body=np.where((a[y,x]>=64)&(c[y,x]==0))[0];db=dijkstra(G,directed=False,indices=body,min_only=True);ds=[]
for m in old:ds.append(dijkstra(G,directed=False,indices=np.where((a[y,x]>=64)&(m[y,x]==2))[0],min_only=True))
dm=np.minimum(*ds);weak=a[y,x]<64;gap=np.full_like(dm,np.inf);finite=np.isfinite(dm)&np.isfinite(db);gap[finite]=abs(dm[finite]-db[finite]);uncertain=weak&(gap<=2);eligible=weak&np.isfinite(dm)&(dm<=db+2)&(y>143)&(y<270);owner=(ds[1]<ds[0]).astype(int);merged=np.zeros(a.shape,np.uint8);result=[]
for n,side in enumerate(['L','R']):
 m=np.zeros(a.shape,np.uint8);m[(old[n]==1)&(a>=64)]=1;m[(old[n]==2)&(a>=64)]=2;sel=eligible&(owner==n);m[y[sel],x[sel]]=3;Image.fromarray(m).save(O/f'58-{side}-classes.png');merged=np.maximum(merged,m);result.append({'side':side,'visible_rigid_cells':int((m==2).sum()),'visible_cloth_cells':int((m==1).sum()),'weak_extension_cells':int((m==3).sum())})
# Validate incident vertex classes without changing geometry.
corners=np.stack([np.stack([x,y],1),np.stack([x+1,y],1),np.stack([x+1,y+1],1),np.stack([x,y+1],1)],1);uv,inv=np.unique(corners.reshape(-1,2),axis=0,return_inverse=True);cl=np.repeat(merged[y,x],4);f=np.zeros(len(uv),bool);g=np.zeros(len(uv),bool);f[inv[cl==0]]=True;g[inv[cl==2]]=True
z={'status':'partition only, no deformation','classes':{'0':'fixed','1':'visible cloth ARAP','2':'visible gauntlet translation','3':'weak-alpha connected extension'},'sides':result,'uncertain_weak_cells_within_two_graph_steps':int(uncertain.sum()),'eligible_uncertain_cells':int((uncertain&eligible).sum()),'fixed_rigid_vertex_conflicts':int((f&g).sum()),'protected_head_shoulder_rows_le138_any_nonfixed':int(((merged>0)&(np.indices(a.shape)[0]<=138)).sum()),'protected_legs_rows_ge270_any_nonfixed':int(((merged>0)&(np.indices(a.shape)[0]>=270)).sum()),'all_nonarm_visible_material_fixed':bool(np.all(merged[(c==0)&(a>=64)]==0)),'limiting_cells_new_classes':{f'{xx},{yy}':int(merged[yy,xx]) for xx,yy in [(135,158),(285,230),(286,232),(286,233)]},'raw_sha256':hashlib.sha256((R/'south-walk-mesh-correction-v1/raw/58.png').read_bytes()).hexdigest(),'whole_alpha_retained':True,'ownership_caution':'graph-nearest support proxy only, not physical/anatomical attribution; <=2step difference explicitly ambiguous'}
(O/'PARTITION_PREFLIGHT.json').write_text(json.dumps(z,indent=2));v=np.array(im)
for cls,color in [(1,[30,150,255]),(2,[255,180,30]),(3,[255,40,180])]:v[merged==cls,:3]=(.5*v[merged==cls,:3]+.5*np.array(color)).astype(np.uint8)
b=Image.new('RGBA',im.size,(70,75,80,255));b.alpha_composite(Image.fromarray(v));b.crop((120,90,350,270)).resize((920,720),Image.Resampling.NEAREST).save(O/'PARTITION_REVIEW_4X.png');np.savez_compressed(O/'support_distances.npz',xy=np.stack([x,y],1),distance_arm=dm,distance_fixed=db,uncertain=uncertain,eligible=eligible);print(json.dumps(z,indent=2))
