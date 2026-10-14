from pathlib import Path
import sys,json,statistics
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'.tools/python'))
from PIL import Image
out={'passed':True,'checks':[]}
for name in ['battle-375.png','bag-375.png','character-375.png','skills-375.png','tasks-375.png','maps-375.png','portrait-750.png','forest-375.png','wechat-shim.png']:
 im=Image.open(ROOT/'reports'/name).convert('RGB');colors=len(im.getcolors(im.width*im.height) or [])
 assert colors>1000,(name,'blank/near-blank image',colors)
 out['checks'].append({'image':name,'uniqueColors':colors})
for width in [375,750]:
 im=Image.open(ROOT/'reports'/f'tile-seam-{width}.png').convert('RGB');pixels=im.load();rows=[statistics.mean(sum(pixels[x,y])/3 for x in range(im.width)) for y in range(im.height)];cols=[statistics.mean(sum(pixels[x,y])/3 for y in range(im.height)) for x in range(im.width)]
 ratios=[]
 for profiles,step,origin in [(cols,96*1.6*width/750,.37*width/750),(rows,64*1.6*width/750,.19*width/750)]:
  for i in range(1,int((len(profiles)-3)/step)):
   p=int(origin+i*step);boundary=min(profiles[p-1:p+2]);neighbors=statistics.mean(profiles[p-3:p-1]+profiles[p+2:p+4]);ratios.append(boundary/neighbors)
 assert min(ratios)>.99 and min(rows+cols)>250,('transparent seam detected',width,min(ratios),min(rows+cols))
 out['checks'].append({'image':f'tile-seam-{width}.png','minBoundaryToNeighborLuminance':min(ratios),'boundaries':len(ratios)})
(ROOT/'reports/visual-qa.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(out))
