"""Immutable GH, aura drawing/damage/save evidence and ending investigation."""
from pathlib import Path
from importlib import import_module
import json,hashlib
n=import_module('native-code').NativeCode();e=import_module('extract-lp');root=e.ROOT
blocks=[('native-dark-aura-code.txt',[(0x5c1180,0x5c1a50),(0x5c2fc0,0x5c3070),(0x5c3e10,0x5c4520),(0x632160,0x6323b0)]),
 ('native-dark-aura-fields.txt',[(0x606de0,0x608ab9),(0x608b20,0x60eb00)]),
 ('native-dark-aura-save.txt',[(0x5a9910,0x5ac470),(0x5acee0,0x5ad350),(0x5ad540,0x5b0240)])]
files=[]
for name,ranges in blocks:
 rows=[]
 for lo,hi in ranges:
  allrows=n.disasm(lo,hi)
  if name.endswith('fields.txt'):
   ranges_of_interest=[(0x6072b0,0x607310),(0x608700,0x6087e0),(0x6097e0,0x6098c0),(0x60e8d0,0x60ea10)]
   allrows=[r for r in allrows if any(a<=r[0]<b for a,b in ranges_of_interest)]
  elif name.endswith('save.txt'):
   ranges_of_interest=[(0x5aa8b0,0x5aa930),(0x5ac3a0,0x5ac470),(0x5ad190,0x5ad230),(0x5ad300,0x5ad350),(0x5ae290,0x5ae350),(0x5b0190,0x5b0240)]
   allrows=[r for r in allrows if any(a<=r[0]<b for a,b in ranges_of_interest)]
  rows+=allrows
 p=root/'reports'/name;p.write_text('\n'.join(f'{a:08x} {m:8s} {o}' for a,m,o in rows),encoding='utf8');files.append(p)
assert n.string(0x4175e8)=='GH' and n.string(0x4108f8)=='\\Data\\Data4.lpRes'
assert n.number(0x402360)==4 and n.number(0x401780,'<d')==.01
code=n.disasm(0x5c3e10,0x5c4520)
assert any(a==0x5c41d8 and o=='edi, 0x78' for a,m,o in code)
assert any(a==0x5c4292 and o=='dword ptr [eax], ebx' for a,m,o in code)
map=json.loads((e.OUT/'maps/A20.json').read_text(encoding='utf8'));npc=next(row for row in map['npcs'] if row['name']=='牛岛屠夫')
pack=json.loads((e.OUT/'sprites/Data4/index.json').read_text(encoding='utf8'))
report={'passed':True,'sourceSha256':hashlib.sha256(n.data).hexdigest(),'evidenceFiles':[{'file':'reports/'+p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],
 'fields':{'GH':'hero word 200e','GH2':'unlock word 2016'},
 'rules':{'kind':2,'frames':[67,68,69],'enemyFrame':67,'period':120,'randomScale':4,'minimumHp':1,'rotationPerTick':.01,'scaleX':.7,'scaleY':.5},
 'spriteSource':{'source':pack['source'],'sha256':pack['sha256']},
 'acquisition':{'map':'A20','npc':npc['name'],'sourceSha256':map['sourceSha256'],'scriptSha256':hashlib.sha256(npc['script'].encode()).hexdigest(),'items':['银环吊坠','翠玉吊坠'],'gold':5000,'renewGold':500},
 'nativeBehavior':['Active while a living enemy has target index -1 (hero), positive aggro timer and hero HP >0.','Global 120-tick cadence; CInt(Rnd * 4) + 1 is 1..5 with banker rounding, not uniform 1..6.','Damage bypasses armor and evasion, clamps enemy HP to one, grants no kill/experience/loot.','Native shared rotation .01 radians/tick, ellipse scale .7/.5 and pulse +1 to200, -2 to60.','Three hero layers and one enemy layer are static images from Data4, not Mgc animations.','GH and unlock flags are separate saved fields; no invented expiry or death-clearing.'],
 'adaptations':['Uses existing nearby combat range for target processing; full native visibility culling equivalence is not claimed.','Actual clamped loss is displayed, not native rolled damage when HP reaches one.','Ground layers protect actor sprites; original aura image also supplies the persistent status icon.','Exact native B1 #good2 typo repaired to #goto GOOD2 only when its matching 500-gold/GH destination is present; inputs unchanged.'],
 'remainingVisuals':['Native emitter 5c4103 checks the monster timer modulo 40 and creates type-4 black general particles via 5c5b00/5c61f9. The generic particle pool/renderer is not yet ported; current aura visuals are the three native ring layers and attacker ring.'],
 'fullNativeCombatEquivalent':False}
(root/'reports/native-dark-aura-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
# Keep the discovered ending source reviewable; this is NOT a runtime completion.
raw=(e.SOURCE/'Config.dat').read_bytes();stories=[]
for name,offset in [('opening',96),('ending',946)]:
 r=e.Reader(raw,8,start=offset);script=r.string();assert script.startswith('#P 黄')
 stories.append({'name':name,'offset':offset,'bytes':r.pos-offset,'script':script,'sha256':hashlib.sha256(script.encode()).hexdigest()})
(root/'reports/native-story-investigation.json').write_text(json.dumps({'source':'Config.dat','sourceSha256':hashlib.sha256(raw).hexdigest(),'stories':stories,'runtimeEndingComplete':False,'investigationOnly':True,'runtimeStatusReport':'reports/native-ending-source.json','notes':['62e418 increments clear count.','62e5d9 clears thirty boss timers to -1; 62e651 clears task/event arrays.','Source ending destination A00 138 12; retains growth/items.','Higher-mode selection and enemy scaling must be verified before wiring GAMEOVER into a complete transition.']},ensure_ascii=False,indent=2),encoding='utf8')
print({'passed':True,'auraFrames':3,'sourcePreserved':True,'endingRuntimeComplete':False})
