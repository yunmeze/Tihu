"""Read-only native defense switch-table extraction; never runs the EXE."""
import sys,re,json,hashlib
from importlib.machinery import SourceFileLoader
N=SourceFileLoader('native',str(__file__).replace('inspect-defense.py','native-code.py')).load_module()
n=N.NativeCode();rows=n.disasm(0x5cd230,0x5d082c)
code={a:(m,o) for a,m,o in rows};following={rows[i][0]:rows[i+1][0] for i in range(len(rows)-1)}
def event(t):
 regs=dict(eax=t,ecx=0,edx=0,esi=0,edi=0);mem={'0x6400ac':t,'0x63ecd0':0};pc=0x5cd290;diff=0;pending=None;commands=[];messages=[]
 def value(s):
  if s in regs:return regs[s]
  if re.fullmatch(r'-?(?:0x[0-9a-f]+|\d+)',s):return int(s,0)
  m=re.fullmatch(r'(?:dword|word) ptr \[(0x[0-9a-f]+)\]',s)
  if m:return mem.get(m[1],0)
  return 0
 for _ in range(1400):
  if pc==0x5d0818 or pc>=0x5d082c:break
  m,o=code[pc];args=o.split(', ');dest=following[pc]
  if m=='cmp':diff=value(args[0])-value(args[1])
  elif m=='test':diff=value(args[0])&value(args[1])
  elif m in ['je','jne','jg','jge','jl','jle','ja','jae','jb','jbe']:
   if {'je':diff==0,'jne':diff!=0,'jg':diff>0,'jge':diff>=0,'jl':diff<0,'jle':diff<=0,'ja':diff>0,'jae':diff>=0,'jb':diff<0,'jbe':diff<=0}[m]:dest=int(o,0)
  elif m=='jmp':
   if o.startswith('0x'):dest=int(o,0)
   else:
    a=re.fullmatch(r'dword ptr \[(\w+)\*4 \+ (0x[0-9a-f]+)\]',o);assert a,o
    dest=n.number(int(a[2],0)+regs[a[1]]*4,'<I')
  elif m=='mov':
   d,s=args
   if d in regs:regs[d]=value(s)
   elif d in ['al','cl','dl']:
    a=re.fullmatch(r'byte ptr \[(\w+) \+ (0x[0-9a-f]+)\]',s)
    if a:regs[{'al':'eax','cl':'ecx','dl':'edx'}[d]]=n.number(int(a[2],0)+regs[a[1]],'<B')
   else:
    a=re.fullmatch(r'(?:dword|word) ptr \[(0x6400ac|0x63ecd0)\]',d)
    if a:mem[a[1]]=value(s)
   if d=='edx' and s.startswith('0x'):
    try:pending=n.string(int(s,0))
    except (AssertionError,UnicodeError,StopIteration):pass
  elif m=='xor' and args[0]==args[1] and args[0] in regs:regs[args[0]]=0
  elif m in ['add','sub'] and args[0] in regs:regs[args[0]]=(regs[args[0]]+(1 if m=='add' else -1)*value(args[1]))&0xffffffff
  elif m=='inc':
   if o in regs:regs[o]+=1
   else:
    a=re.fullmatch(r'dword ptr \[(0x6400ac)\]',o)
    if a:mem[a[1]]+=1
  elif m=='call' and o=='0x6047d0':
   assert pending and pending.startswith('# '),(t,pc,pending);commands.append(pending)
  elif m=='call' and o=='0x5a7590':messages.append(pending)
  pc=dest
 else:raise AssertionError(('trace limit',t,hex(pc)))
 return dict(time=t,commands=commands,messages=messages,nextTime=mem['0x6400ac'],waitForClear=bool(mem['0x63ecd0']))
events=[e for t in range(5,2201) if (e:=event(t))['commands']]
mon=json.loads((N.ROOT/'public/assets/data/monsters.json').read_text('utf8'));names={m['name'] for m in mon}
for e in events:
 e['spawns']=[]
 for line in e.pop('commands'):
  _,x,y,name=line.split();assert name in names,name
  e['spawns'].append(dict(x=int(x),y=int(y),name=name))
result=dict(version=1,map='J30',entry=[30,19],initialClock=5,endClock=2199,minimumFlags=4,events=events)
assert len(events)==147 and sum(len(e['spawns']) for e in events)==573
assert sum(bool(e['messages']) for e in events)==21 and sum(e['waitForClear'] for e in events)==21
assert events[0]['time']==10 and events[-1]['nextTime']==2199
assert all(e['nextTime']>e['time'] and e['spawns'] for e in events)
assert all(e['nextTime']<events[i+1]['time'] for i,e in enumerate(events[:-1]))
result['sourceSha256']=hashlib.sha256(n.data).hexdigest()
(N.ROOT/'reports/native-defense-events.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
files=[]
for name,ranges in {'native-defense-waves.txt':[(0x5cd230,0x5d082c)],'native-defense-start.txt':[(0x617915,0x617bad)],'native-defense-upgrades.txt':[(0x612fc0,0x613560)],'native-defense-continue.txt':[(0x56a0c0,0x56a180)],'native-defense-outcomes.txt':[(0x5c7a60,0x5c82a0)],'native-defense-mercenary.txt':[(0x604b60,0x604d40)],'native-defense-growth-full.txt':[(0x5d15d0,0x5d1b90)],'native-defense-siege-ai.txt':[(0x5caeb9,0x5cafda)]}.items():
 n.dump(name,ranges);files.append({'file':'reports/'+name,'sha256':hashlib.sha256((N.ROOT/'reports'/name).read_bytes()).hexdigest()})
start=n.disasm(0x617915,0x617bad)
assert any(m=='mov' and o=='dword ptr [0x6400ac], 5' for a,m,o in start)
assert not any('0x640040' in o for a,m,o in start)
up=n.disasm(0x612fc0,0x613560)
assert sum(m=='add' and o.endswith(', 0x12c') for a,m,o in up)>=2
assert n.string(0x4174f4)==' -1' and n.string(0x41210c)=='战旗'
flag=next(m for m in mon if m['name']=='战旗');assert flag['hp']==1500 and flag['behavior']==-2
sourceMap=N.ROOT/'public/assets/maps/J30.json';map=json.loads(sourceMap.read_text('utf8'));npc=next(row for row in map['npcs'] if row['name']=='守卫升级')
report={'passed':True,'sourceSha256':result['sourceSha256'],'mapSourceSha256':map['sourceSha256'],'npcScriptSha256':hashlib.sha256(npc['script'].encode()).hexdigest(),'eventTableSha256':hashlib.sha256((N.ROOT/'reports/native-defense-events.json').read_bytes()).hexdigest(),'evidenceFiles':files,'rules':{'waves':21,'events':147,'enemies':573,'initialClock':5,'finalClock':2199,'flags':8,'minimumRemainingFlags':4,'flagHp':1500,'flagHpPerUpgrade':300,'flagDefensePerUpgrade':5,'maxHpUpgrades':5,'maxPhysicalUpgrades':6,'maxMagicUpgrades':6,'initialMercenaryLevel':6,'recruitCountThreshold':12},'nativeBehavior':['DEFSTART marks eight flags friendly without incrementing FRIENDCOUNT; flags cannot attack.','Waiting gate is cleared by original button handler 56a0c0. The clock increments once every 50 native frames only while the gate is clear.','Boss event moves clock to stage*100-1 and sets waiting; must clear enemies before the continue button appears.','Fewer than four flags loses; exactly four survives. Final clock2199 and no enemies announces completion. No separate gold/XP victory reward.','Mercenary wrapper 604b60 appends one -1 (owner), following pet wrapper604d40 additionally marks 0x36=-1. Mercenaries chase enemies, do not follow across maps and cannot receive pet healing.','Generic growth5d15d0 branches on tracked-pet marker but both branches increment kill-based growth; fixed mercenaries therefore also grow.','Siege idle movement fallback5caeb9 searches a living flag when no ordinary target is acquired.'],'adaptations':['Defense HUD and paginated flag/mercenary inspection reuse original HUD slices/icons and fit the portrait canvas.','Explicit return to J00 uses original carriage destination126,74; failure freezes the encounter while allowing return.','Web per-character active defense snapshot resumes wave cursor/clock, remaining flags, living enemies and mercenaries after reload. Leaving and reentering starts a fresh encounter; flags/mercenaries are not following pets.','Source J30 home19,80 is outside50x50; use actual original carriage entry30,19.','Validate recruitment/upgrade caps and source region spawn space before fees; stalled full spawn pool retries without skipping wave events.'],'remaining':['Original desktop defense UI/pause/visibility implementation is adapted to portrait; full native combat/quest equivalence remains false.'],'fullNativeCombatEquivalent':False}
(N.ROOT/'reports/native-defense-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
(N.ROOT/'public/assets/data/defense.json').write_bytes((N.ROOT/'reports/native-defense-events.json').read_bytes())
print({'passed':True,'waves':21,'events':147,'enemies':573,'sourceUnchanged':True})
