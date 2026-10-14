"""Recover skill records from executable users, never constant-pool ordering."""
import json,re,hashlib
from pathlib import Path
from importlib import import_module
n=import_module('native-code').NativeCode()
ROOT=Path(__file__).resolve().parent.parent
NAMES=['基本剑术','剑气斩','火龙斩','半月斩','烈火斩','冰封斩','自然之力','灵魂火符','回生术','治愈术','隐身术','召唤骷髅','召唤神兽','施毒术','侵蚀术','火球术','爆裂火球','雷电术','火墙','魔法盾','御冰术','强冰术','冰咆哮','诱惑之光','地狱雷光','炼尸咒']
def recover():
 starts=[n.number(0x5facc0+i*4,'<I') for i in range(26)]
 records=[];evidence=[]
 handler=n.disasm(0x573760,0x577224)
 clicks=[n.number(0x577228+i*4,'<I') for i in range(26)]
 for index,(name,start) in enumerate(zip(NAMES,starts)):
  end=min([a for a in starts if a>start]+[0x5fa663]);rows=n.disasm(start,end);literals=[];costs=[]
  for i,(a,m,o) in enumerate(rows):
   match=re.search(r'0x[0-9a-f]+$',o)
   if m not in ('push','mov') or not match:continue
   v=int(match[0],16)
   if not 0x40d000<v<0x420000:continue
   try:s=n.string(v)
   except:continue
   if not s.isprintable() or not s:continue
   literals.append({'instructionVA':hex(a),'literalVA':hex(v),'sourceOffset':n.offset(v)-4,'text':s})
   if '需要技能点' in s:
    cost=next(int(o2,0) for _,m2,o2 in rows[i+1:i+12] if m2=='push' and (o2.isdigit() or o2.startswith('0x')))
    costs.append(cost)
  if index==0:costs*=5
  assert len(costs)==(0 if index in (23,25) else 5),(name,costs)
  # Cross-check UI prices against each native click-handler level jump table.
  clickEnd=min([a for a in clicks if a>clicks[index]]+[0x577185])
  clickRows=[row for row in handler if clicks[index]<=row[0]<clickEnd]
  classGuards=[]
  for a,m,o in clickRows:
   if m!='push' or not re.match(r'0x[0-9a-f]+$',o):continue
   try:label=n.string(int(o,16))
   except:continue
   if label in ['战士','道士','法师']:classGuards.append({'instructionVA':hex(a),'class':label})
  assert len(classGuards)<=1,(name,classGuards)
  classes=[classGuards[0]['class']] if classGuards else ['战士','道士','法师']
  checks=[(a,o) for a,m,o in clickRows if m=='cmp' and '0x1ff4]' in o]
  displayedCosts=costs[:]
  if costs:
   table=next(int(re.search(r'0x[0-9a-f]+',o)[0],16) for _,m,o in clickRows if m=='jmp' and 'ecx*4' in o)
   prices=[]
   for level in range(5):
    at=n.number(table+4*level,'<I')
    op=next(o for a,m,o in handler if a==at and m=='cmp')
    assert '0x1ff4]' in op
    prices.append(int(op.split(', ')[-1],0))
   # The shipped panel says 2 at Ice Storm level 2, but the click handler
   # charges 1. Show the actual transaction price in the web port.
   assert prices==costs or (name=='冰咆哮' and prices==[2,2,1,1,1] and costs==[2,2,2,1,1])
   costs=prices
   assert n.number(table+20,'<I') not in [n.number(table+i*4,'<I') for i in range(5)]
  prereq=next((s['text'] for s in literals if s['text'].startswith('学习'+name+'需要')),'')
  parts=list(dict.fromkeys(s['text'] for s in literals if (len(s['text'])>8 or '%' in s['text'] or 'MP消耗' in s['text']) and not s['text'].startswith(('学习','下一级','，下一级')) and not s['text'].strip()==name))
  # Native panel interpolates these values. Preserve literals and fill the holes.
  dynamic={'剑气斩':['proc8'],'火龙斩':['proc4','bonus10'],'烈火斩':['proc10','bonus10'],'冰封斩':['proc10','bonus10'],'召唤骷髅':['level'],'召唤神兽':['level'],'炼尸咒':['refine']}.get(name,[])
  template=''.join(part+('{'+dynamic[i]+'}' if i<len(dynamic) else '') for i,part in enumerate(parts))
  description=template
  for key in dynamic:description=description.replace('{'+key+'}','（随技能等级提高）')
  mp=re.search(r'MP消耗[：:](\d+)',template)
  record={'name':name,'nativeIndex':index,'description':description,'descriptionTemplate':template,'text':parts,'sourceOffsets':[s['sourceOffset'] for s in literals],'mpCost':int(mp[1]) if mp else None,'prerequisites':re.findall(r'\[([^\]]+)\]\s*(\d+)级',prereq),'prerequisiteText':prereq,'pointCosts':costs,'maxLevel':5 if costs else None,'learningMethod':'points' if costs else 'special','learningVerified':True,'formulasVerified':False}
  record['classes']=classes
  records.append(record);evidence.append({'name':name,'nativeIndex':index,'classes':classes,'classGuards':classGuards,'panelCaseVA':hex(start),'clickCaseVA':hex(clicks[index]),'pointCosts':costs,'nativeDisplayedCosts':displayedCosts,'costCheckVAs':[hex(a) for a,_ in checks],'literals':literals})
 acquisition=import_module('inspect-npc-quests').recover_acquisition()[0]
 for record in records:
  if record['name'] in acquisition:record['acquisition']=acquisition[record['name']]
 return records,evidence
def main():
 records,evidence=recover();p=ROOT/'public/assets/data/skills.json';skills=json.loads(p.read_text(encoding='utf8'));skills['records']=records;skills['recordSource']='native-panel-and-click-v1';p.write_text(json.dumps(skills,ensure_ascii=False,separators=(',',':')),encoding='utf8')
 ranges=[(0x573760,0x577224),(0x5f5800,0x5fa663),(0x55c570,0x55c8a0),(0x55c8d0,0x55cc00),(0x55cc30,0x55cf60),(0x55cf90,0x55d2d4),(0x55d320,0x55d696),(0x5ef940,0x5f06d1)]
 rows=n.dump('native-growth-assembly.txt',ranges)
 report={'passed':True,'source':str(n.source.relative_to(ROOT)),'sourceSha256':hashlib.sha256(n.data).hexdigest(),'skills':evidence,'attributes':{'pointField':'0x1ff2','functions':{'attack':'0x55c570','tao':'0x55c8d0','magic':'0x55cc30','defense':'0x55cf90','magicDefense':'0x55d320'},'cost':1,'rangeRule':'Compare Rnd() against current total min/max; below ratio increases max, otherwise min. Apply delta to base so equipped bonuses are not duplicated.','bonus':{'attack':{'hp':1},'tao':{'mp':2},'magic':{'mp':3},'defense':{'hp':2,'capacity':1},'magicDefense':{'hp':1,'mp':2,'capacity':1}},'zeroMaxAdaptation':'Legacy web saves can have a 0–0 range: raise max instead of dividing by zero.'},'equipment':{'functionVA':'0x5ef940','comparisons':[['0x5ef9cf','level',31],['0x5ef9e9','attackMax',32],['0x5efa03','taoMax',33],['0x5efa1d','magicMax',34]],'uses':'Current totals before replacing the worn item, including its bonuses.'},'instructions':len(rows),'adaptations':['Point controls are repositioned into portrait native HUD surfaces.','Special skills are hidden until learned through their original NPC acquisition scripts; learned ranks retain native acquisition restrictions. See native-quest-source.json and hidden-skills-design.json.','User-requested fixed stack slots: warrior 50, mage 30, daoist 40; belt/worn equipment excluded, native weight disabled. Raw growth/capacity fields are retained for legacy/source compatibility only. Purchases/withdrawals are atomic and reward overflow is placed on the ground.']}
 report['adaptations'][1]='Special skills use the original NPC acquisition scripts; see native-quest-source.json.'
 (ROOT/'reports/native-growth-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps({'passed':True,'skills':len(records),'pointSkills':sum(bool(r['pointCosts']) for r in records),'sourceSha256':report['sourceSha256']},ensure_ascii=False))
if __name__=='__main__':main()
