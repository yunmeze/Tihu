"""Read-only numeric evidence from the shipped executable and save, not Help guesses."""
import json, hashlib, struct
from pathlib import Path
from importlib import import_module
n=import_module('native-code').NativeCode()
ROOT=Path(__file__).resolve().parent.parent
save=ROOT/'reference/LP传奇单机版-重生v1.2.2E/Save/ddoo.lpSave'
b=save.read_bytes(); key=b[3]; pos=10
def text():
 global pos
 size=struct.unpack_from('<I',b,pos)[0]^key;pos+=4
 value=bytes(v^key for v in b[pos:pos+size]).decode('gb18030');pos+=size
 return value
def integer(size):
 global pos
 value=int.from_bytes(b[pos:pos+size],'little')^key;pos+=size
 return value
headers=[text() for _ in range(7)];mode=integer(2);strings=[text() for _ in range(5)]
rows=n.disasm(0x5ad540,0x5adff0);reads=[]
for i,(a,m,o) in enumerate(rows):
 if 0x5ad831<=a<=0x5addfd and m=='call' and o=='esi':
  size=next(int(oo,0) for aa,mm,oo in reversed(rows[max(0,i-4):i]) if mm=='push' and oo in ['1','2','4'])
  start=pos;reads.append({'readerVA':hex(a),'offset':start,'size':size,'value':integer(size)})
speed=reads[-1]['value'];assert speed==2
update=n.disasm(0x618ce0,0x61e654)
states={str(i):hex(n.number(0x61e688+n.number(0x61e6a8+i-1,'<B')*4,'<I')) for i in [1,33,81,129,177,225,249]}
assert states['33']=='0x61c40e' and states['81']=='0x61c5cc'
sections=[('movement branches',update,0x61c40e,0x61c68e),('attack step',update,0x61c7ee,0x61c870),('cast step',update,0x61daa0,0x61dbcd),('growth',n.disasm(0x61f2f0,0x61ff20),0x61f8e0,0x61fcd0),('offense and set bonus',n.disasm(0x624eb0,0x625180),0x624eb0,0x625180),('equipment set',n.disasm(0x5f27e0,0x5f3680),0x5f27e0,0x5f3680)]
report={'passed':True,'sourceSha256':hashlib.sha256(n.data).hexdigest(),'movement':{'sourceFps':50,'observedSaveSpeed':speed,'saveSha256':hashlib.sha256(b).hexdigest(),'speedRead':reads[-1],'speedField':'0x1f6c','stateJumpMap':states,'walk':{'state':33,'pixelsPerTick':speed/2,'animationTicks':7,'tilesPerSecond':speed/2*50/32},'run':{'state':81,'pixelsPerTick':speed,'animationTicks':5,'tilesPerSecond':speed*50/32},'horizontalPixelMultiplier':n.number(0x401f30,'<d'),'freezeMovementMultiplier':.5,'freezeAnimationExtraTicks':1,'diagonals':'Both grid axes receive the full step; no Euclidean normalization.','portScope':'Portrait destinations use native walk/run speed and frames. Left click/tap walks; right click and touch double tap run. Held mouse movement and Space continuous autorun are not yet ported.'},'attack':{'phaseTicks':'8 - fastAttack + frozen','phases':6,'normalSeconds':.96},'cast':{'phaseTicks':'8 - fastCast + frozen','phases':6,'normalSeconds':.96},'growth':{'attributePoints':'one per promotion','skillPoints':'one at even resulting levels','capacity':'2 per promotion; warrior additional 1 per promotion and per tenth level','mageHP':'2 at odd levels, 1 at even levels'},'equipmentSet':{'field':'0x2004','meaning':'computed set bonus, not forge or durability','bonus':'CInt(setLevel * matchingRingStatMax / 3) + setLevel','offenseRoll':'CInt(min + Rnd*(max-min) + setBonus)'},'remaining':['Native special challenge drop-bonus triggers','Expert/hell entry, exact native geometry and every special-attack release offset'],'fullNativeNumericEquivalent':False,'evidence':[{'meaning':name,'instructions':[f'{a:08x} {m} {o}' for a,m,o in r if lo<=a<hi]} for name,r,lo,hi in sections]}
report['monsterMovement']={'sourceFps':50,'pixelsPerSecond':{'horizontal':'75 * DB speed','vertical':'50 * DB speed'},'diagonals':'full step on both axes','freezeMultiplier':.5,'walkAnimationSeconds':.48,'frozenWalkAnimationSeconds':.6,'sourceFunctions':['5cafe5..5cb044','5d28c0..5d3028']}
report['equipmentReport']='reports/native-refining-source.json'
report['implemented']=['native normal creation without web gifts','level and capacity growth','point allocation','actual equipment instance properties and requirements','set bonus and offense rolls','luck MP queue and HP/MP recovery pools','fast attack/cast and half-speed frozen movement','user-requested fixed class stack slots (50/30/40), excluding belt/equipment and disabling native load gating','reachable reward overflow','attached weapon spells','weapon use damage counter','forge/merge and actual sale valuation','ordinary drops, per-item random affixes and native GIVE equipment rewards']
(ROOT/'reports/native-numeric-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':True,'movement':report['movement'],'fullNativeNumericEquivalent':False},ensure_ascii=False))
