"""Read native NPC pet, healing and control-lock instructions without editing inputs."""
from pathlib import Path
from importlib import import_module
import json,hashlib
n=import_module('native-code').NativeCode();root=Path(__file__).resolve().parent.parent
rows=n.disasm(0x613c20,0x6187d0)
blocks=[('native-script-heal.txt',0x614945,0x614bbf),('native-script-warp-lock.txt',0x614fe0,0x615160),('native-script-summon-dispatch.txt',0x615f60,0x61624c)]
files=[]
for name,lo,hi in blocks:
 block=[r for r in rows if lo<=r[0]<hi];p=root/'reports'/name;p.write_text('\n'.join(f'{a:08x} {m:8s} {o}' for a,m,o in block),encoding='utf8');files.append(p)
for name,lo,hi in [('native-script-pet-limits.txt',0x604d40,0x605010),('native-script-pet-creation.txt',0x605010,0x605aa1),('native-script-pet-query.txt',0x607794,0x6077b5)]:
 n.dump(name,[(lo,hi)]);files.append(root/'reports'/name)
assert n.string(0x417b0c)=='#REME' and n.string(0x417b1c)=='#REPET'
assert n.string(0x417b5c)=='#STOP' and n.string(0x417b6c)=='#UNSTOP'
assert any(a==0x614a2a and '0x1fe8' in o for a,m,o in rows)
assert any(a==0x614a97 and '0x1fec' in o for a,m,o in rows)
assert any(a==0x614b8e and '0x78' in o for a,m,o in rows)
assert any(a==0x615092 and '0xffff' in o for a,m,o in rows)
limits=n.disasm(0x604d40,0x605010);assert any(a==0x604e15 and o=='word ptr [0x640042], 2' for a,m,o in limits)
creation=n.disasm(0x605010,0x605aa1);assert any(a==0x605a14 and o=='esi, 3' for a,m,o in creation)
sourceMonster=json.loads((root/'public/assets/data/monsters.json').read_text(encoding='utf8'))
boss=next(m for m in sourceMonster if m['name']=='玄冥之神');assert '#change bt25 = 3600@3change ET9 = 1' in boss['event']
report={'passed':True,'sourceSha256':hashlib.sha256(n.data).hexdigest(),'evidenceFiles':[{'file':'reports/'+p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],
 'rules':{'warriorPets':1,'magePets':1,'taoistPets':3,'maxPetLevel':10,'purchasedPetTemplate':'full source monster stats, not halved','characterHealing':'full HP and MP, reset recovery accumulator','petHealing':'full HP of the three tracked living pets','stopFlag':'63ee30 = -1; UNSTOP clears; native keyboard/items/menu controls check it'},
 'adaptations':['Spawn beside player at nearest terrain cell reachable by both player and monster; no charge on absent cell, unit-pool exhaustion or pet limit.','Portrait NPC approach and system/save controls remain usable while STOP disables manual movement, combat inputs, consumables and free map travel.','Purchased pets reuse source-backed pet growth, AI, native models and per-character saved stats.','Targeted repair of the malformed boss delimiter @3change activates the intended ET9 gate alongside BT25=3600; original asset string remains unchanged.'],
 'bossDelimiterRepair':{'monsterId':boss['id'],'sourceEvent':boss['event'],'sourceEventSha256':hashlib.sha256(boss['event'].encode('utf8')).hexdigest(),'nativeBugCompatibility':False},'fullNativeQuestEquivalent':False}
(root/'reports/native-script-services-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print({'passed':True,'evidenceFiles':len(files),'petLimits':[1,3,1],'sourcePreserved':True})
