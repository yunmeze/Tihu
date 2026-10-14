"""Recover permanent interfaces from the shipped config, buttons and EXE."""
from pathlib import Path
import sys,struct,json,hashlib,importlib,re
sys.path.insert(0,str(Path(__file__).resolve().parent))
e=importlib.import_module('extract-lp');n=importlib.import_module('native-code').NativeCode()
b=(e.SOURCE/'Config.dat').read_bytes();r=e.Reader(b,8,start=1895);script=r.string()
assert script.startswith('//版本占位') and '#change kw12 = 1' in script
sections=dict((m.group(1),m.group(2)) for m in re.finditer(r'#Sub (\w+)\r?\n(.*?)(?=\r?\n#Sub |\Z)',script,re.S|re.I))
insights=[]
for page in ['B1','B2','C1','C2','C3','C4','D1','D2','E1','E2','E3','E4','E5']:
 s=sections[page];id=int(re.search(r'#if kw(\d+) = -1',s,re.I).group(1));desc=re.search(r'开悟(.+?)，(.+?)\r?\n',s).groups();price=int(re.search(r'支付(\d+)金币',s).group(1))
 insights.append({'id':id,'name':desc[0],'description':desc[1],'price':price,'page':page})
monsters=json.loads((e.OUT/'data/monsters.json').read_text(encoding='utf8'))
pool=[{'id':m['id'],'drops':m['dropRules']} for m in monsters if m['id']>=4 and m['name'] not in ('','0')]
rewards={
 'monsters':[{'stage':1,'gold':500},{'stage':2,'gold':1000},{'stage':4,'gold':2000},{'stage':6,'items':[['铜色栗子',1],['银色栗子',1],['金色栗子',1]]},{'stage':8,'items':[['铜矿石',3],['银矿石',2],['金矿石',1]]},{'stage':10,'attributes':1}],
 'drops':[{'stage':1,'capacity':10},{'stage':2,'defense':1},{'stage':4,'magicDefense':1},{'stage':6,'offense':1},{'stage':8,'attributes':1},{'stage':10,'affixBonus':True}]
}
value={'source':'LP传奇单机版_重生.exe / Config.dat','exeSha256':hashlib.sha256(n.data).hexdigest(),'configSha256':hashlib.sha256(b).hexdigest(),'insightScript':script,'insights':insights,'collectionPool':pool,'rewards':rewards}
e.write(e.OUT/'data/permanent.json',value)
e.write(e.REPORT/'native-permanent-source.json',{'passed':True,'exeSha256':value['exeSha256'],'configSha256':value['configSha256'],'configScript':{'offset':1895,'bytes':r.pos-1895,'kind':8,'sha256':hashlib.sha256(script.encode()).hexdigest()},'insightCount':len(insights),'monsterCount':len(pool),'dropEntries':sum(len(m['drops']) for m in pool),'rewards':rewards,'nativeFunctions':{'collectionPool':'5ff270','deathRegistration':'5ffea0','dropRegistration':'6002f0','monsterRewards':'567bd0','dropRewards':'568130','collectionUI':'600460','insightSwitch':'56fbc0','insightThresholdUI':'5ddca0'},'nativeDiscrepancies':['Drop reward 10% says capacity +15 in the original label, but 568246 adds 10. Use executed value 10.','HP insight acquisition text says default 40%, acquired text says 60%; web starts at 40% and offers explicit controls.'],'evidenceFiles':[{'file':'reports/'+f,'sha256':hashlib.sha256((e.REPORT/f).read_bytes()).hexdigest()} for f in ['native-collection-counts.txt','native-collection-drop-register.txt','native-collection-rewards.txt','native-insight-ui.txt']]})
print({'insights':len(insights),'monsterPool':len(pool),'dropEntries':sum(len(m['drops']) for m in pool)})
