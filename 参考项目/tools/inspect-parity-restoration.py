"""Verify shipped EXE anchors; write only this restoration round's evidence."""
from pathlib import Path
from importlib import import_module
import hashlib,json,os
n=import_module('native-code').NativeCode()
root=Path(__file__).resolve().parent.parent
out=root/'reports/restoration-parity-20261013'
assert hashlib.sha256(n.data).hexdigest()=='21dc753d3aa828fb29dc171e595857be234833edc43a1d80833540ae7e355b84'
clips=[]
for name,lo,hi in [('boss-refresh',0x5c968b,0x5c9902),('shield-start',0x61dc4b,0x61dcc0),('shield-update-draw',0x5c2b4e,0x5c2dbe),('shield-hit',0x61e43e,0x61e490)]:
 rows=n.disasm(lo,hi)
 file=out/(name+'.txt')
 file.write_text('\n'.join(f'{a:08x} {m:8} {o}' for a,m,o in rows),encoding='utf8')
 clips.append({'name':name,'from':hex(lo),'to':hex(hi),'file':str(file.relative_to(root)).replace('\\','/'),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'instructions':len(rows)})
 if name=='boss-refresh':
  assert any(a==0x5c9698 and o=='word ptr [esi + 0x9a], 0xa' for a,m,o in rows)
  assert any(a==0x5c96a6 and o=='eax, 0x1d' for a,m,o in rows)
  assert n.string(0x411178)=='设置'
  assert n.number(0x401ee4)==10
 if name=='shield-start':
  assert any(a==0x61dca7 and o=='cx, cx, 0x50' for a,m,o in rows)
  assert any(a==0x61dcb0 and o=='edx, [eax + eax*4]' for a,m,o in rows)
 if name=='shield-update-draw':
  assert any(a==0x5c2b53 and o=='edi, 5' for a,m,o in rows)
  assert any(a==0x5c2b99 and m=='dec' and o=='eax' for a,m,o in rows)
  assert any(a==0x5c2c9f and o=='dword ptr [0x63f784], 0x32' for a,m,o in rows)
  assert any(a==0x5c2cad and o=='ecx, 0xc' for a,m,o in rows)
 if name=='shield-hit':
  assert any(a==0x61e475 and o=='byte ptr [0x63f774], 3' for a,m,o in rows)
  assert any(a==0x61e47c and o=='dword ptr [0x63f77c], 0xd' for a,m,o in rows)
report={'passed':True,'sourceSha256':hashlib.sha256(n.data).hexdigest(),'evidenceFiles':clips,'bossRefresh':{'highestEligibleIndex':29,'skipBehavior':10,'skipTimedSurvivalChallenge':True,'settingsName':'设置','seconds':'CInt(Rnd*10)+5','accumulatorReset':'only when subtraction < 0'},'shield':{'nativeCount':'5*(magicRoll+80*level)','tickUnitsPerCount':5,'unfold':[1,10],'hold':[11,13],'hit':[13,16],'lifetimeCountsOnlyHolding':True,'warningCountLessThan':50,'drawPhases':[1,7],'periodTicks':12},'pid':os.getpid(),'fullOriginalEquivalent':False}
(out/'native-evidence.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print({'passed':True,'sections':len(clips),'pid':os.getpid()})
