"""Verify native anchors and keep the reconstruction's remaining limits explicit."""
import sys,json,hashlib
from importlib import import_module
sys.path.insert(0,'tools')
n=import_module('native-code').NativeCode()
ranges=[(0x624eb0,0x625180),(0x625180,0x625eb0),(0x6286e0,0x629510),(0x62bb60,0x62c940),(0x5d3b70,0x5d5370),(0x605010,0x605a64),(0x5fe7c0,0x5fe800),(0x619979,0x61a400),(0x5c8924,0x5c9020),(0x5a0b24,0x5a0b68),(0x5ca1f1,0x5ca2b3),(0x5a3cd0,0x5a529b),(0x5bb270,0x5bdfa0)]
rows=n.dump('native-combat-rules-assembly.txt',ranges)
constants={'flightPixelsPerFrame':(0x402138,7),'spellFireMultiplier':(0x402d60,.75),'spellIceMultiplier':(0x401798,.7),'spellStrongIceMultiplier':(0x401758,.9),'summonHpMultiplier':(0x4020b8,1.1),'statusPowerDivisor':(0x401c50,20),'paralysisMultiplier':(0x402570,2.8)}
for key,(address,value)in constants.items():assert n.number(address,'<d')==value,key
assert n.string(0x411698)=='#addFriend '
assert n.string(0x4116b4)==' 召唤骷髅 '
assert n.string(0x4145d8)=='护身戒指'
assert any(a==0x5fe7ee and o=='ax, 0x258' for a,m,o in rows)
for address,helper in [(0x5a4356,'0x6286e0'),(0x5a4691,'0x6289b0'),(0x5a499c,'0x628dd0'),(0x5a4ce3,'0x6290a0'),(0x5a5094,'0x62bb60')]:assert any(a==address and m=='call' and o==helper for a,m,o in rows)
report={
 'exeSha256':hashlib.sha256(n.data).hexdigest(),'verifiedAgainstShippedExecutable':True,
 'sourceRanges':[[hex(lo),hex(hi)]for lo,hi in ranges],
 'constants':{key:{'address':hex(a),'value':v}for key,(a,v)in constants.items()},
 'flightEffectIds':{'火球术':14,'爆裂火球':15,'御冰术':16,'强冰术':17,'灵魂火符':6},'flightPacks':{'14':'Mgc/6','15':'Mgc/8','16':'Mgc/10','17':'Mgc/12','6':'Mgc/18'},'impactPacks':{'24':'Mgc/7','25':'Mgc/9','26':'Mgc/11','27':'Mgc/13','28':'Mgc/19'},
 'damage':{'random':'VB CInt interpolation; tie to even','minimum':1,'heroToMonsterEvadeMultiplier':3,'monsterEvadeMultiplier':5,'magicShieldDefensePerLevel':{'physical':6,'magic':5},'protectionRing':'MP cost 2 * damage; exhausted mana also loses full HP damage','monsterMeleeKinds':[0,1,2,3,4,5,6,7],'physicalFlightKinds':[11,12,13,14,15],'magicFlightKinds':[16,17,18,19]},
 'statuses':{'freezeAndBurnMutuallyExclusive':True,'freezeFrames':500,'burnFrames':500,'monsterPoisonFrames':1000,'monsterParalysisFrames':250,'playerParalysisFrames':150,'monsterDot':'CInt(Rnd * power) + 1 on remaining-frame multiples of 100','playerDot':'max(1,CInt(Rnd*5 + 1 - matching equipment attribute)) on remaining-frame multiples of 100','weaponStatusPriority':['paralysis','freeze','burn','poison'],'monsterStatusPriority':['freeze','burn','poison','paralysis'],'corrosion':'Subtract defense and magic defense; restore on expiry'},
 'skills':{'fire':'CInt(magicRoll * .75 + 2*(level-1) + 1)','explosiveFire':'magicRoll + 4*level - 3','ice':'CInt(magicRoll * .7 + 2*(level-1))','strongIce':'CInt(magicRoll * .9 + 4*(level-1))','talisman':'CInt(taoRoll * .9 + 3*(level-1))','poison':{'frames':'10*(taoRoll+30*level)','power':'CInt(taoRoll/10+2*level)'},'corrosion':{'frames':'10*(taoRoll+10*level)','power':'CInt(taoRoll/10+4*level+1)'}},
 'egg':{'init':'CLng(Rnd*100000)','countsOnlyWhileIdle':True,'oneEggPerInitialization':True,'preferredOffset':[1,-1],'item':'鸡蛋','sourceAddresses':['0x5a0b24','0x5ca1f1']},
 'parents':{'behaviors':[-3,-4],'periodFrames':200,'probabilities':[.6,.2,.2],'offspring':[['暗月飞蛾','暗月飞蛾-火焰','暗月飞蛾-精英'],['暗月蜘蛛','暗月天狼','暗月黑鄂']],'maximumNativeUnitSlots':600,'nativeCapacityAddress':'0x5fe7ee'},
 'summons':{'costs':{'召唤骷髅':50,'召唤神兽':100},'limits':{'skeletonLevel1':1,'skeletonLevel2Plus':2,'beast':1,'allFriends':3},'statScalingSource':'0x605478..0x605896','level5Appearances':{'skeleton':200,'beast':174}},
 'adaptations':['A* and swept projectile collision replace native occupancy / directional routing','Hero attack/cast cycle uses native (8-fast)/50 per phase; contact/cast release phase and six-tile spell auto-attack range remain portrait adaptations','Source-backed heading rotation is connected for 15 single-strip projectile types (see native-projectile-orientation-source.json); exact native speeds, offsets and special collisions remain partial','Parent cadence is actor-local rather than native global frame modulo','Friendly follow/acquisition uses portrait A*; pets are stored as web JSON rather than native binary saves','Reachable egg/drop placement overrides inaccessible native placements; blocked parent or summon cells skip creation','Native corrosion restoration writes are applied to the affected actor rather than an unrelated array slot'],
 'extendedRulesReport':'reports/native-extended-combat-source.json',
 'remaining':['Native collection/challenge acquisition flow; luck/fast modifiers, weapon use counter and computed set bonus 0x2004 are connected','Exact phased sword AOE and all native special attack geometry, speeds, collision and timing','Full native pre-cast class/UI restrictions; native point allocation is connected'],
 'fullNativeCombatEquivalent':False}
(n.source.parents[2]/'reports/native-combat-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print({'verified':True,'assemblyInstructions':len(rows),'fullNativeCombatEquivalent':False})
