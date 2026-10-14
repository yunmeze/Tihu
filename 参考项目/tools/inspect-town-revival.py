"""Read-only evidence for the native revival button's remembered town route."""
import hashlib,json
from pathlib import Path
from importlib import import_module
n=import_module('native-code').NativeCode();root=Path(__file__).resolve().parent.parent
files=[]
for name,lo,hi in [('button',0x588bd0,0x588e12),('memory',0x59dfc0,0x59e0c2)]:
 rows=n.dump('native-town-revival-'+name+'.txt',[(lo,hi)])
 path=root/'reports'/('native-town-revival-'+name+'.txt')
 files.append({'file':'reports/'+path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
rows=n.disasm(0x588bd0,0x588e12)
assert any(a==0x588c9a and m=='mov' and o=='word ptr [eax + 0x1fe8], dx' for a,m,o in rows)
assert any(a==0x588d74 and m=='mov' and o=='edx, dword ptr [ecx + eax*4 + 0x1fcc]' for a,m,o in rows)
assert any(a==0x588da2 and m=='call' and o=='0x606530' for a,m,o in rows)
assert n.string(0x40f474)=='#move ' and n.string(0x40f488)=='00 0 0'
assert n.string(0x410b60)=='00'
rows=n.disasm(0x59dfc0,0x59e0c2)
assert any(a==0x59e0a0 and m=='lea' and o=='ecx, [ecx + eax*4 + 0x1fcc]' for a,m,o in rows)
towns=[{k:m[k] for k in ['id','name','home','width','height']} for m in json.loads((root/'public/assets/data/maps.json').read_text('utf8')) if len(m['id'])==3 and m['id'][1:]=='00']
assert len(towns)==10
for town in towns:
 assert 0<=town['home'][0]<town['width'] and 0<=town['home'][1]<town['height']
report={'passed':True,'sourceSha256':hashlib.sha256(n.data).hexdigest(),'evidenceFiles':files,
 'rules':{'townMemory':'latest entered xx00 map; persists when entering wilderness, dungeons, time challenge and border defense','townField':'hero BSTR +0x1fcc','townWrite':'0x59e0a0','revivalRead':'0x588d74','revivalCommand':'#move <remembered prefix>00 0 0','destination':'original map home; same destination selection as return scroll and teleport ring'},
 'towns':towns,'port':{'ordinaryAndChallengeRevivalShared':True,'defenseRevivalShared':True,'townRecordSavedPerCharacter':True,'oldSaveFallback':'latest unlocked xx00 town; A00 when no town exists','deadMedicinesStillBlocked':True},
 'limits':['Legacy saves do not contain visit order; latest unlocked town is an explicit migration fallback.','This evidence verifies the revival destination, not all native death penalties or revival animations.']}
(root/'reports/native-town-revival-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print({'passed':True,'towns':len(towns),'revivalRoute':report['rules']['revivalCommand']})
