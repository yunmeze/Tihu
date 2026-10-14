"""Verify the shipped ring activation, possession query and cooldown clock."""
from pathlib import Path
from importlib import import_module
import json,hashlib
n=import_module('native-code').NativeCode();root=Path(__file__).resolve().parent.parent
files=[]
for name,ranges in [
 ('native-ring-use.txt',[(0x5e65c0,0x5e6de6)]),
 ('native-ring-key.txt',[(0x56d2e5,0x56d548)]),
 ('native-ring-possession.txt',[(0x5fe650,0x5fe69c)]),
 ('native-ring-clock.txt',[(0x618fb2,0x619050)]),
 ('native-ring-invisibility.txt',[(0x62d6a0,0x62d71f)]),
]:
 rows=n.dump(name,ranges);p=root/'reports'/name;files.append({'file':'reports/'+name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
assert n.string(0x40f4b8)=='传送戒指' and n.string(0x40f49c)=='隐身戒指'
rows=n.disasm(0x5e65c0,0x5e6de6)
assert any(a==0x5e6c02 and '0x3c' in o for a,m,o in rows)
assert any(a==0x5e6d21 and '0x78' in o for a,m,o in rows)
assert any(a==0x5e6dd3 and '0x3e8' in o for a,m,o in rows)
clock=n.disasm(0x618fb2,0x619050);assert sum(m=='idiv' and o=='ebx' for a,m,o in clock)==2
query=n.disasm(0x5fe650,0x5fe69c);assert any(m=='mov' and o=='edi, 0x38' for a,m,o in query)
report={'passed':True,'sourceSha256':hashlib.sha256(n.data).hexdigest(),'helpFile':'reference/LP传奇单机版-重生v1.2.2E/Help/Game_Index.htm','evidenceFiles':files,
 'rules':{'teleportCooldownSeconds':60,'invisibilityCooldownSeconds':120,'invisibilityFrames':1000,'sourceFps':50,'possessionQuerySlots':56,'ringsConsumed':False,'teleportTown':'remembered town prefix + 00, original home','invisibilityShortcut':'Y','equipmentRequired':False,'cooldownClock':'one second, native frame count modulo 50'},
 'port':{'touchAndMouseDoubleTap':True,'explicitUseButtons':True,'bagAndEquipmentUse':True,'cooldownsPerCharacterSaved':True,'failedTeleportRestoresWorldAndCooldown':True},'fullNativeItemUseEquivalent':False}
(root/'reports/native-ring-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print({'passed':True,'rings':2,'invisibilitySeconds':20,'evidenceFiles':len(files)})
