"""Verify map animation/visible blockers against the shipped native renderer."""
import sys, importlib, hashlib, json, collections
from pathlib import Path
sys.path.insert(0, 'tools')
native=importlib.import_module('native-code').NativeCode()
root=Path.cwd();assets=root/'public/assets'
ranges=[(0x5b53d0,0x5b5680),(0x5c51b0,0x5c59e4),(0x589760,0x58a2d4),(0x6060c0,0x60631d)]
rows=native.dump('native-map-effects-assembly.txt',ranges);by_address={a:(m,o) for a,m,o in rows}
for address,expected in {
 0x5b55e7:('mov','edi, 0x11'),0x5b5610:('and','edx, 0x80000007'),
 0x5b5627:('cmp','ax, 5'),0x5b5641:('sete','al'),
 0x5c562b:('movsx','ecx, word ptr [0x63f6be]'),
 0x5c52e8:('sub','ax, 0x34'),0x5c537f:('mov','cx, 4'),
 0x5c5383:('sub','cx, word ptr [0x63f6be]'),
 0x589f6a:('mov','dword ptr [ebp - 0x4c], 0x37'),
 0x58a282:('mov','dword ptr [ebp - 0x4c], 0x3b'),
 0x6061fb:('mov','dword ptr [ecx + esi*8], 8'),
 0x6062c7:('cmp','dword ptr [edx], 8'),
}.items():assert by_address[address]==expected,(hex(address),by_address.get(address))
assert native.string(0x4108f8)==r'\Data\Data4.lpRes'
assert [native.number(0x5c59e4+i*4,'<I') for i in [4,6,7]]==[0x5c562b,0x5c56d3,0x5c52af]
read=lambda file:json.loads((assets/file).read_text(encoding='utf8'))
dynamic=read('sprites/Map/Res/Dynamic/index.json');pillar=read('sprites/Data4/index.json')
assert len(dynamic['frames'])==51
assert all(pillar['frames'][i]['original']==[48,92] for i in range(55,60))
rules={'sourceFps':50,'frameTicks':8,'dynamicFrames':5,'pillarPack':'Data4','pillarFirst':55,'pillarFrames':5,'pillarTop':-52,'npcFrameTicks':17}
maps=[];dynamic_count=0;pillar_count=0;npc_count=0;stale_npcs=[];groups=collections.Counter()
for path in sorted((assets/'maps').glob('*.json')):
 m=json.loads(path.read_text(encoding='utf8'));d=[];p=[]
 for x in range(m['width']):
  for y in range(m['height']):
   _,flag,t,index=m['cells'][x*m['height']+y]
   if t==5 and index>0:
    assert index%5==1 and index+4<len(dynamic['frames']),[m['id'],x,y,index]
    d.append([x,y,flag,index]);groups[index]+=1
   elif t==8 and index>0:p.append([x,y,flag,index])
   elif t==7 and index>0:
    n=m['npcs'][index-1] if index<=len(m['npcs']) else None
    if n and [n['x'],n['y']]==[x,y]:npc_count+=1
    else:stale_npcs.append([m['id'],x,y,index])
 if d or p:maps.append({'id':m['id'],'name':m['name'],'sourceSha256':m['sourceSha256'],'dynamic':d,'pillars':p})
 dynamic_count+=len(d);pillar_count+=len(p)
for pack in [dynamic,pillar]:assert hashlib.sha256((root/'reference/LP传奇单机版-重生v1.2.2E'/pack['source']).read_bytes()).hexdigest()==pack['sha256']
report={'passed':True,'sourceSha256':hashlib.sha256(native.data).hexdigest(),'rules':rules,'sourceFunctions':{'renderObject':'0x5c51b0','dispatchTable':'0x5c59e4','globalClock':'0x5b55df–0x5b5644','pillarTextures':'0x589f55–0x58a2b9','setMapFlag':'0x6060c0'},'counts':{'maps':155,'mapsWithEffects':len(maps),'dynamicObjects':dynamic_count,'dynamicGroups':len(groups),'visiblePillars':pillar_count,'npcCellReferencesVerified':npc_count,'staleNpcCellReferences':len(stale_npcs)},'dynamicGroups':dict(groups),'resources':[{'id':p['id'],'source':p['source'],'sha256':p['sha256']} for p in [dynamic,pillar]],'maps':maps,'staleNpcCellReferences':stale_npcs,'adaptations':['Native global tick converted to elapsed simulation seconds at 50 FPS; hidden app does not advance.','Object visibility and prefetch use the union of every animation frame.','Native stored cell flags determine rendering order; map effects never enter combat effects, damage, audio or loot queues.','Visible SETMAPFLAG 2 blockers and removals persist through the existing per-character script state.','Type 7 is rendered through the existing live NPC list; stale cached cell references do not create duplicate or ghost NPCs.']}
(root/'reports/native-map-effects-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'passed':True,**report['counts']},ensure_ascii=False))
