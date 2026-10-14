"""Read-only native scroll destination, town memory and six-item package evidence."""
import hashlib,json
from pathlib import Path
from importlib import import_module
n=import_module('native-code').NativeCode();root=Path(__file__).resolve().parent.parent
files=[]
for name,ranges in [
 ('native-consumable-scrolls.txt',[(0x5e756d,0x5e79cd)]),
 ('native-consumable-packages.txt',[(0x5e7300,0x5e756d)]),
 ('native-consumable-town.txt',[(0x59dfc0,0x59e1a8)]),
]:
 rows=n.dump(name,ranges);p=root/'reports'/name
 files.append({'file':'reports/'+name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'instructions':len(rows)})
assert n.string(0x411738)=='回城卷'
assert n.string(0x410b60)=='00'
assert n.string(0x40f488)=='00 0 0'
assert n.string(0x414b28)=='无法传送到未到过的地图'
assert n.string(0x414af8)=='三清观符'
assert n.string(0x414ad8)=='背包没有足够的空间用来解包'
items=json.loads((root/'public/assets/data/items.json').read_text(encoding='utf8'))
names={i['name']:i for i in items if i['name']!='0'}
scrolls=[{'id':i['id'],'name':i['name'],'map':i['name'].split()[-1] if ' 'in i['name'] else None,'position':i['rawFields'][2:4],'icon':i['icon']} for i in items if i['type']==5]
packages=[{'id':i['id'],'name':i['name'],'child':names[i['name'][:-1]]['id'],'quantity':6} for i in items if i['type']==6 and i['name']!='0']
assert len(scrolls)==12 and len(packages)==17
report={'passed':True,'sourceSha256':hashlib.sha256(n.data).hexdigest(),'evidenceFiles':files,'scrolls':scrolls,'packages':packages,
 'rules':{'returnScroll':'remembered town prefix + 00; map home for 0/0','townMemory':'update prefix on entering a map ending in 00; latest entered town, not geographic distance','townMemoryWrite':'0x59e0a0','scrollCoordinates':'runtime +0x34/+0x36, rawFields[2]/[3]','visitedMapRequired':True,'sanqingQuestEventIndex':0,'sanqingMinimumEvent':3,'packageContents':6},
 'port':{'beltAndBagSharedDispatcher':True,'saveAfterUseAndMapTransition':True,'failedUseKeepsItem':True,'deadUseBlocked':True,'oldSaveTownFallback':'latest unlocked xx00 town; A00 when absent','packageCapacity':'check resulting class slots (warrior 50, mage 30, daoist 40), matching stacks and belt; weight disabled by user request; native six contents retained'},
 'remaining':['Type 4 人参包/特级人参包/千年人参包 have zero HP/MP and no type-6 unpack branch; remain unsupported rather than inventing an effect.','Other special non-consumable item and equipment activation flows remain separate.'],'fullNativeItemUseEquivalent':False}
(root/'reports/native-consumable-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'passed':True,'scrolls':len(scrolls),'packages':len(packages),'sourceSha256':report['sourceSha256']}))
