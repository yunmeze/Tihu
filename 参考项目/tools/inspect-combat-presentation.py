"""Read-only original effect/animation anchors for the presentation repair."""
import sys,json,hashlib
from pathlib import Path
from importlib import import_module
sys.path.insert(0,'tools')
n=import_module('native-code').NativeCode()
ranges=[(0x5b97e0,0x5bb270),(0x5bb270,0x5c1180),(0x5c2b4e,0x5c2dbe),(0x628590,0x6286e0)]
rows=n.dump('native-combat-presentation-assembly.txt',ranges)
by_address={a:(m,o)for a,m,o in rows}
for address,expected in {
 0x5b9977:('imul','dx, dx, 6'),
 0x5b9984:('lea','ecx, [ecx + edx + 1]'),
 0x5ba004:('imul','cx, cx, 0x11'),
 0x5bc78a:('cmp','word ptr [ecx + eax*4 + 0x20b4], 5'),
 0x5bc66b:('cmp','edx, 4'),
 0x5bcdf1:('call','0x629510'),
 0x5bd077:('cmp','dword ptr [edx + 0x24], 4'),
 0x5bcac7:('cmp','dword ptr [edx + 0x24], 2'),
 0x5c2b53:('mov','edi, 5'),
 0x5c2b84:('cmp','edx, 0xe'),
 0x5c2bb1:('cmp','edx, 0x11'),
}.items():assert by_address[address]==expected,(hex(address),by_address.get(address))
assert n.number(0x401ac0,'<d')==10
assert n.string(0x412060)=='14-2.lpRes'
assert n.string(0x41207c)=='14.lpRes'
report={
 'passed':True,'sourceSha256':hashlib.sha256(n.data).hexdigest(),'assemblyInstructions':len(rows),
 'ranges':[[hex(a),hex(b)]for a,b in ranges],
 'swordLights':{'packs':['Mgc/1-1','Mgc/2-1','Mgc/3-1'],'directions':8,'framesPerDirection':6,'source':'5b995d..5b9984, 5b9b47..5b9b6e: follow current hero attack phase'},
 'fireAndIceSlash':{'packs':['Mgc/4','Mgc/5'],'directions':8,'framesPerDirection':17,'source':'5ba004, 5ba28a'},
 'lightning':{'source':'5bc611..5bcd99, 628590..6286e0','normalPack':'Mgc/14','level5Pack':'Mgc/14-2','primaryHitFrame':4,'frameSeconds':.1,'visiblePrimaryFrames':4,'aftershockPack':'Mgc/56','aftershockHitFrame':2,'aftershockCycles':'learnedLevel-1','aftershockPower':'CInt(magicRoll/10+2*learnedLevel)'},
 'iceStorm':{'pack':'Mgc/16','hitFrame':6,'frameSeconds':.08,'frames':17,'source':'5bcdea, 5bcfd9..5bd00a'},
 'hellLightning':{'pack':'Mgc/90','hitFrame':4,'frameSeconds':.08,'visibleFrames':7,'source':'5bd077, 5bd270..5bd286'},
 'shield':{'pack':'Mgc/17','frameSeconds':.1,'unfold':[1,10],'hold':[11,13],'hit':[13,16],'source':'5c2b4e..5c2bc8'},
 'coverageReport':'reports/combat-presentation-tests.json',
 'adaptations':['Portrait attack duration remains .96 seconds; physical contact is aligned to visible landed-blade phase 4 instead of recovery phase 5','Native effect rendering was tied partly to global frame counts and drawing passes; web playback uses actor/effect-local clocks','Primary thunder follows its selected target until impact; subsequent shocks and area spells use fixed ground cells','Original sprite offsets are retained; heading-driven zero-offset projectile sheets rotate around the original canvas center in 48:32 screen projection (see native-projectile-orientation-source.json)','Combat text is drawn after scene scaling at final display resolution, with outlined Song-style glyphs; continuous ground damage is displayed as a rolling total'],
 'remaining':['Exact native phased sword AOE geometry and all monster special attack frame phases/offsets','Native low-time shield flashing','Luck, fast attack, weapon durability and full native pre-cast UI restrictions','WeChat device testing'],
 'fullNativeCombatEquivalent':False,
}
Path('reports/native-combat-presentation-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print({'verified':True,'instructions':len(rows),'fullNativeCombatEquivalent':False})
