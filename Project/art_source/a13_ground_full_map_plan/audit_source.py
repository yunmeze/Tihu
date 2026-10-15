"""Read-only A13 atlas/map audit; all outputs stay in the ignored full-map audit directory."""
from pathlib import Path
from collections import Counter,defaultdict
import hashlib,json,csv
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[2];D=P/'diagnostics/art_source/a13-ground/full-map-source-audit';D.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
 mp=P/'data/maps/A13.json';mf=P/'assets/original/manifest.json';cp=P/'art_source/a13_ground_source/source-group-contract.json'
 m=json.loads(mp.read_text());packs=json.loads(mf.read_text())['packs'];verified=set(json.loads(cp.read_text())['minimum_first_screen_group']['unique_signed_ids']);pages={};ims={};rows={};owners=[]
 def tile(name,k):
  pk=packs[name];f=pk['frames'][str(k)];page=pk['pages'][f['page']]['file'];a,b,w,h=f['rect']
  if page not in pages:pages[page]=Image.open(P/page[6:]).convert('RGBA')
  return pages[page].crop((a,b,a+w,b+h)),f,page
 special={118,129,133,136,141,142,144,154,156,157,159,160}
 grass={-406,-399,-591};soil={-2,-394,-395,-402,-403,-586,-587,-594,-595}
 curb={-577,-579,-580,-581,-582,-585,-588,-593,-597,-598,-601,-602,-604,-607,-608}
 for i,c in enumerate(m['cells']):
  k=c[0]
  if not k:continue
  x,y=divmod(i,m['height']);name='Map/Res/FloorBig'if k<0 else'Map/Res/FloorSmall';im,f,page=tile(name,abs(k))
  o={'key':f'{k}@{x},{y}','signed_id':k,'cell':[x,y],'world_rect':[x*48+f['crop'][0],y*32+f['crop'][1],*im.size],'order':i};owners.append(o)
  if k in rows:continue
  ims[k]=im
  category='grass-earth-transition-or-grass-variant'
  if k in special:category='coarse-rock-around-stairwell-formation'
  elif k==-426:category='special-grass-dark-linear-mark-unknown'
  elif k in grass:category='grass-base'
  elif k in soil:category='tan-earth-gravel-base'
  elif k in curb:category='narrow-stone-curb-road-edge'
  rows[k]={'signed_id':k,'pack':name,'frame_index':abs(k),'original':f['original'],'crop':f['crop'],'offset_ignored':f['offset'],'atlas_page':page,'rect':f['rect'],'rgba_sha256':hashlib.sha256(im.tobytes()).hexdigest(),'alpha_extrema':im.getchannel('A').getextrema(),'nonopaque_pixel_count':sum(im.getchannel('A').histogram()[:255]),'classification':category,'in_initial_15':k in verified,'classification_basis':'Manual visual reading of original atlas and actual map context; no name/color-only automatic inference.'}
 counts=Counter(o['signed_id']for o in owners);hs=defaultdict(list)
 for k,r in rows.items():r['placements']=counts[k];r['cells']=[o['cell']for o in owners if o['signed_id']==k];hs[(tuple(ims[k].size),r['rgba_sha256'])].append(k)
 aliases=[sorted(v)for v in hs.values()if len(v)>1];alias_extensions=set()
 for group in aliases:
  if verified.intersection(group):alias_extensions.update(set(group)-verified)
 # Exact full-frame aliases only; signed keys retained. Explicitly test half-size quadrant matches too.
 quadrant_aliases=[]
 for k,im in ims.items():
  if k<0:continue
  for j,b in ims.items():
   if j>0:continue
   for x,y in [(0,0),(48,0),(0,32),(48,32)]:
    if im.tobytes()==b.crop((x,y,x+48,y+32)).tobytes():quadrant_aliases.append([k,j,x,y])
 # Shared real rectangle edges, interval overlap supports 48x32 next to 96x64 half edges.
 left=defaultdict(list);top=defaultdict(list)
 for o in owners:
  x,y,w,h=o['world_rect'];left[x].append(o);top[y].append(o)
 edges=[]
 for a in owners:
  x,y,w,h=a['world_rect']
  for b in left[x+w]:
   X,Y,W,H=b['world_rect'];lo,hi=max(y,Y),min(y+h,Y+H)
   if hi>lo:edges.append({'axis':'vertical','line':[x+w,lo,x+w,hi],'length_px':hi-lo,'before':a['key'],'after':b['key'],'ids':[a['signed_id'],b['signed_id']]})
  for b in top[y+h]:
   X,Y,W,H=b['world_rect'];lo,hi=max(x,X),min(x+w,X+W)
   if hi>lo:edges.append({'axis':'horizontal','line':[lo,y+h,hi,y+h],'length_px':hi-lo,'before':a['key'],'after':b['key'],'ids':[a['signed_id'],b['signed_id']]})
 pairs=defaultdict(lambda:{'contacts':0,'length_px':0,'vertical':0,'horizontal':0})
 for e in edges:
  a,b=sorted(e['ids']);v=pairs[(a,b)];v['contacts']+=1;v['length_px']+=e['length_px'];v[e['axis']]+=1
 pair_rows=[{'ids':list(k),**v}for k,v in sorted(pairs.items())]
 crossing=[r for r in pair_rows if (r['ids'][0]in verified)!=(r['ids'][1]in verified)]
 def board(name,keys,scale=1):
  cw,ch=224,170;out=Image.new('RGB',(cw*5,ch*((len(keys)+4)//5)),(40,40,40));dr=ImageDraw.Draw(out)
  for i,k in enumerate(keys):
   x,y=i%5*cw,i//5*ch;im=ims[k];factor=2 if k<0 else 4
   out.paste(im.resize((im.width*factor,im.height*factor),Image.Resampling.NEAREST),(x,y+36));dr.text((x+2,y+2),f'{k}  n={counts[k]}  {im.width}x{im.height}',fill='white');dr.text((x+2,y+18),rows[k]['classification'][:30],fill='white')
  out.save(D/name)
 board('all-70-original-contact-board.png',sorted(rows));board('difference-55-original-contact-board.png',sorted(set(rows)-verified));board('special-original-contact-board.png',sorted(special|{-426}))
 def context(slug,b):
  out=Image.new('RGBA',(b[2]-b[0],b[3]-b[1]));used=[]
  for o in owners:
   x,y,w,h=o['world_rect']
   if x<b[2]and y<b[3]and x+w>b[0]and y+h>b[1]:out.alpha_composite(ims[o['signed_id']],(x-b[0],y-b[1]));used.append(o)
  out.save(D/f'{slug}-floor.png');with_objects=out.copy();obs=[]
  for i,c in enumerate(m['cells']):
   if c[2]not in [1,2,3,4]or c[3]<=0:continue
   x,y=divmod(i,m['height']);name={1:'Map/Res/Debris',2:'Map/Res/Plant',3:'Map/Res/Wall',4:'Map/Res/Building'}[c[2]];im,f,_=tile(name,c[3]);wx=x*48+f['crop'][0];wy=y*32+32-f['original'][1]+f['crop'][1]
   if wx<b[2]and wy<b[3]and wx+im.width>b[0]and wy+im.height>b[1]:obs.append((0 if c[1]in[1,-2]else 2 if c[1]==2 else 1,y,i,im,wx,wy,name,c[3]))
  for layer,y,i,im,wx,wy,name,k in sorted(obs,key=lambda o:o[:3]):with_objects.alpha_composite(im,(wx-b[0],wy-b[1]))
  with_objects.save(D/f'{slug}-static-scenery-context.png');save(f'{slug}-context.json',{'world_bounds':b,'floor_owners':used,'static_scenery': [{'pack':o[6],'frame':o[7],'order':o[2]}for o in obs],'note':'Original static kinds1-4 only; not a runtime screenshot; transparent floor gaps are not a semantic claim of water/hole.'})
 context('coarse-rock-formation',[75*48,17*32,85*48,28*32]);context('unknown-minus426',[86*48,20*32,92*48,26*32]);context('expanded-curb-junction',[44*48,44*32,60*48,58*32])
 # Actual original pair contexts for all 71 changed/unchanged interface types.
 by_key={o['key']:o for o in owners}; ranked=sorted(crossing,key=lambda r:-r['contacts'])
 for start in range(0,len(ranked),20):
  subset=ranked[start:start+20];out=Image.new('RGB',(5*244,((len(subset)+4)//5)*184),(45,45,45));dr=ImageDraw.Draw(out)
  for n,r in enumerate(subset):
   e=next(e for e in edges if sorted(e['ids'])==r['ids']);a,b=by_key[e['before']],by_key[e['after']];rs=[a['world_rect'],b['world_rect']];box=[min(q[0]for q in rs),min(q[1]for q in rs),max(q[0]+q[2]for q in rs),max(q[1]+q[3]for q in rs)];im=Image.new('RGBA',(box[2]-box[0],box[3]-box[1]))
   for o in owners:
    x,y,w,h=o['world_rect']
    if x<box[2]and y<box[3]and x+w>box[0]and y+h>box[1]:im.alpha_composite(ims[o['signed_id']],(x-box[0],y-box[1]))
   x,y=n%5*244,n//5*184;out.paste(im,(x,y+42),im);dr.text((x,y),str(r['ids'])+' n='+str(r['contacts']),fill='white');dr.text((x,y+18),e['before']+' | '+e['after'],fill='white')
  out.save(D/f'cross-boundary-context-{start//20+1}.png')
 categories=defaultdict(list)
 for k,r in rows.items():categories[r['classification']].append(k)
 protected=set(rows)-grass-soil
 report={'source_sha256':{'map':sha(mp),'manifest':sha(mf),'frozen_contract':sha(cp)},'scope':'Only ignored outputs. No generated materials, runtime edits or source-contract modifications.',
  'totals':{'placements':len(owners),'unique_signed_ids':len(rows),'initial15_global_placements':sum(counts[k]for k in verified),'difference55_global_placements':sum(counts[k]for k in set(rows)-verified)},
  'dimensions':{'FloorBig':'47 IDs, 96x64 actual source canvases','FloorSmall':'23 IDs, 48x32 actual source canvases'},
  'classifications':{c:{'ids':sorted(ks),'placements':sum(counts[k]for k in ks)}for c,ks in categories.items()},
  'ids':[rows[k]for k in sorted(rows)],'initial15':sorted(verified),'difference55':sorted(set(rows)-verified),
  'exact_rgba_alias_groups':aliases,'exact_small_to_big_quadrant_aliases':quadrant_aliases,'exact_alias_extensions_from_initial15':sorted(alias_extensions),
  'recommendation':{'material_family_shareable_without_special_geometry':sorted(grass|soil),'meaning':'Can share grass or earth material basis, but not evidence that existing candidate is seam-safe or all patterns should be identical. Maintain world origin 0 and assembled-map QA.',
   'must_preserve_source_structure_or_source_pixels_until_validated':sorted(protected),'unknown_preserve_source_pixels':[-426],
   'coarse_rock_preserve_source_pixels':sorted(special),'curb_note':'15 curb IDs include previously unseen orientations and corners; existing narrow-stone material is not proof of shape coverage. Exact aliases may reuse geometry evidence but all external contacts still need validation.',
   'transition_note':'Grass/earth transitions and grass-only variation tiles are conservatively grouped together; they need per-ID source masks and shared global materials, not rectangular scope masks. No new classifier/mask has been implemented or validated here.',
   'special_semantics':'No unambiguous water or water-surface, regular silver-brick paving, or floor-painted black pit was established in these 70 atlas frames. Coarse-rock tiles surround a stairwell entrance in original static scenery context. The central stairs/pit are a separate scenery object, not painted into these floor frames. Transparent map gaps alone do not establish a hole. -426 dark mark remains unknown.'},
  'adjacency':{'method':'Full source world rectangles; right/left and bottom/top exact shared coordinate, positive interval overlap. Each physical contact once, half-edges supported; floor-only pre-occlusion.', 'contacts':len(edges),'pair_types':len(pair_rows),'initial15_to_difference55_contacts':sum(r['contacts']for r in crossing),'initial15_to_difference55_pair_types':len(crossing),'initial15_to_difference55_pairs':crossing},
  'limits':['Visual semantics are manually read, not authoritative game labels.','No replacement export or whole-map boundary pass completed.','Full-frame alias is exact RGBA including dimensions; never collapse signed ownership keys.','Adjacency records touch interfaces, not overdraw intersections or rendered object occlusion.']}
 save('id-placement-report.json',report);save('all-owner-adjacency.json',{'owners':owners,'edges':edges,'pair_counts':pair_rows});save('initial15-to-difference55-boundaries.json',crossing)
 with (D/'id-placement-report.csv').open('w')as f:
  w=csv.writer(f);w.writerow(['signed_id','placements','category','initial15','original','crop','offset_ignored','rgba_sha256'])
  for k in sorted(rows):r=rows[k];w.writerow([k,counts[k],r['classification'],r['in_initial_15'],r['original'],r['crop'],r['offset_ignored'],r['rgba_sha256']])
 print(json.dumps({'totals':report['totals'],'classes':report['classifications'],'aliases':aliases,'alias_extensions':sorted(alias_extensions),'adjacency':{k:v for k,v in report['adjacency'].items()if k!='initial15_to_difference55_pairs'}},indent=2))
if __name__=='__main__':main()
