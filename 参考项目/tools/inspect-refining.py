"""Trace the shipped numeric equipment rules and their DB-to-runtime mapping."""
import json,hashlib,re
from pathlib import Path
from importlib import import_module
n=import_module('native-code').NativeCode();ROOT=Path(__file__).resolve().parent.parent
ores=['铁矿石','铜矿石','银矿石','金矿石'];costs=[];evidence=[]
for level in range(9):
 start=n.number(0x5e6088+4*level,'<I')
 end=min([n.number(0x5e6088+4*i,'<I') for i in range(9) if n.number(0x5e6088+4*i,'<I')>start]+[0x5e602c])
 rows=n.disasm(start,end);gold=next(int(o.split(', ')[-1],0) for a,m,o in rows if m=='cmp' and '0x1fe0]' in o)
 requirements={}
 for i,(a,m,o) in enumerate(rows):
  if m!='mov' or not re.match(r'edx, 0x[0-9a-f]+$',o):continue
  try:label=n.string(int(o.split(', ')[-1],16))
  except:continue
  if label not in ores or label in requirements:continue
  requirement=next((int(oo.split(', ')[-1],0) for aa,mm,oo in rows[i+1:] if mm=='cmp' and re.match(r'eax, (?:0x[0-9a-f]+|\d+)$',oo)),None)
  if requirement is not None:requirements[label]=requirement
 costs.append([gold]+[requirements.get(ore,0) for ore in ores]);evidence.append({'level':level,'startVA':hex(start),'gold':gold,'oreChecks':requirements})
assert costs==[[200,1,0,0,0],[500,2,0,0,0],[800,1,1,0,0],[1000,2,1,0,0],[1200,3,1,0,0],[1500,4,1,0,0],[1800,4,1,1,0],[2000,4,2,1,0],[2500,4,1,1,1]],costs
rates=[]
for level in range(4):
 start=n.number(0x566fc4+4*level,'<I');rows=n.disasm(start,start+10);rates.append(next(int(o.split(', ')[-1],0)for a,m,o in rows if m=='mov' and o.startswith('esi, ')))
assert rates==[70,50,30,10]
files=[]
for name,ranges in [
 ('native-numeric-item-loader.txt',[(0x5a8660,0x5a8d50)]),
 ('native-numeric-forge-transaction.txt',[(0x583d80,0x584ac0)]),
 ('native-numeric-forge-cost.txt',[(0x5e5230,0x5e6088)]),
 ('native-numeric-merge-transaction.txt',[(0x563040,0x565780)]),
 ('native-numeric-merge-rate-cost.txt',[(0x566e30,0x566fc4),(0x566fe0,0x567220)]),
 ('native-numeric-random-equipment.txt',[(0x5fcc20,0x5fd794),(0x5fd7c0,0x5fe645)]),
 ('native-numeric-weapon-usage.txt',[(0x625180,0x625eb0)]),
 ('native-numeric-drop-event.txt',[(0x5d5af0,0x5d6546)]),
 ('native-attached-weapon-skill.txt',[(0x618ce0,0x61e654)]),
 ('native-numeric-sale-price.txt',[(0x584a20,0x584f30)]),
]:
 n.dump(name,ranges);files.append({'file':'reports/'+name,'sha256':hashlib.sha256((ROOT/'reports'/name).read_bytes()).hexdigest(),'ranges':[[hex(lo),hex(hi)]for lo,hi in ranges]})
report={'passed':True,'sourceSha256':hashlib.sha256(n.data).hexdigest(),
 'dbMapping':{'raw0through27':'runtime offset 0x30 + 2 * index','raw28and29':'both load into 0x6c; second overwrites first','raw30':'0x70 attached skill','raw31through34':'0x72..0x78 requirements','raw35':'0x7a forge level','raw36':'0x7c usage counter','raw37':'0x7e sale-price factor','raw38':'0x80 weight','mergeGrade':'runtime 0x68, independent saved instance metadata; NOT DB raw28'},
 'forge':{'costs':costs,'ores':ores,'costEvidence':evidence,'maximum':9,'failure':'Rnd*100 < oldForgeLevel*10: paid ores/gold and weapon lost','success':'dominant max of attack/magic/tao += max(1,CInt(max/20)); actual field and forge grade increment','sixthPlus':'five independent rolls for accuracy/freeze/burn/poison/vampire, capped at 2'},
 'merge':{'baseRates':rates,'costs':[2000,5000,8000,10000],'oreRateBonuses':[4,6,9,12],'oreCatalystBonuses':[3,5,8,12],'maximum':4,'sameNameAndGrade':True,'failure':'consume both inputs, selected ores/catalysts and fee; keep one chosen base weapon','success':'CInt(signed-word sum/2), raw6..26; increment positive minima by 1 and positive maxima by new grade; luck inherits chosen input','finalConflicts':'preserve native asymmetric physical/magic evade decrements'},
 'sale':'CLng(basePrice * priceBonus / 10 + trunc(basePrice/5)) + 1',
 'usage':{'limit':1500,'damageBonus':'integer usage count / 500, before status amplification/defense','counterField':36,'persists':'individual weapon; empty weapon slot counted separately until replaced'},
 'affixes':{'baseAttempts':3,'perAttemptChance':.2,'clearCountExtra':'min(2,clearCount)','modeExtra':'expert 4 / hell 8','collectionReward':'claimed stage 10 gives one additional 30-percent attempt','levelAttempts':[20,30,40,50,50,60,60,70,80],'levelAttemptChance':.2,'entryPoints':['native monster drop 5d648f','native script GIVE 6042d8 / 604327'],'persisted':['actual raw fields','price factor','random tint']},
 'drops':{'chance':'CInt(Rnd*denominator), zero becomes 1; drop only on 1','gold':'trunc(max/3) + CInt(Rnd*(max-trunc(max/3))); zero becomes 1','ordering':'chance, each equipment affix generation or gold roll, then next record','unmappedConditionalBoost':{'condition':'native player 2262 == 83 and 226a - 2 == 22f0','denominatorDivisors':{'2':2,'5':5,'10':10}}},
 'remaining':['Native collection completion/claiming UI and challenge-state production flow','Random tint rendering (stored per equipment instance)','Native cast selection/class UI gates and every special geometry/timing branch','Native walk/run input selection and expert/hell entry flows'],
 'fullNativeNumericEquivalent':False,'evidenceFiles':files}
# Read the actual constants rather than inferring divisors from their addresses.
report['drops']['unmappedConditionalBoost']['denominatorDivisors']={'2':n.number(0x401558,'<d'),'5':n.number(0x4020a0,'<d'),'10':n.number(0x401ac0,'<d')}
(ROOT/'reports/native-refining-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'passed':True,'forgeCostTiers':len(costs),'mergeRates':rates,'evidenceFiles':len(files)},ensure_ascii=False))
