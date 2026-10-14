"""Read-only native status-particle emitters, sprite slots and lifetime rules."""
from pathlib import Path
from importlib import import_module
import hashlib,json
n=import_module('native-code').NativeCode();root=Path(__file__).resolve().parent.parent
ranges=[(0x5c5b00,0x5c6310),(0x5c6c10,0x5c707e),(0x5c72b3,0x5c7363),(0x5c8924,0x5c8b41),(0x5c8f3c,0x5c9009),(0x5999d0,0x599cdb),(0x6325c0,0x632696)]
name='audit-fixes-20261012/native-status-particles-source.txt';rows=n.dump(name,ranges);at={a:(m,o) for a,m,o in rows}
assert at[0x5c5b48]==('mov','edi, 0x400')
for a,field in [(0x5c8924,'0xb2'),(0x5c8a6e,'0xae'),(0x5c8f3c,'0xa6')]:assert at[a]==('cmp',f'word ptr [esi + {field}], bx')
for a in [0x5c8946,0x5c8a90,0x5c8f5e]:assert at[a]==('mov','cx, 0x1e')
for a,value in [(0x5c89ec,'ebx'),(0x5c8b32,'1'),(0x5c8ffa,'2')]:assert at[a]==('mov',f'dword ptr [ebp - 0x118], {value}')
assert at[0x5c6de4]==('add','word ptr [esi + ecx + 0x20], -0x14')
assert at[0x5c6e14]==('add','word ptr [esi + ecx + 0x1c], -0x14')
assert at[0x5c6e45]==('add','word ptr [esi + ecx + 0x22], -0xa')
for a in [0x5c6f7a,0x5c72bd]:assert at[a]==('add','word ptr [esi + ecx + 0x22], -0x14')
for a in [0x5c6cb2,0x5c6ef5,0x5c6fff]:assert at[a]==('add','word ptr [esi + ecx + 0x22], -5')
for a,value in [(0x5999e1,'0x19'),(0x599aa8,'0x1f'),(0x599b6f,'0x20'),(0x599c36,'0x21')]:assert at[a]==('mov',f'dword ptr [ebp - 0x2c], {value}')
assert at[0x599a08]==('add','ecx, 4') and at[0x599acf]==('add','ecx, 8') and at[0x599b96]==('add','ecx, 0xc') and at[0x599c5d]==('add','ecx, 0x10')
assert n.string(0x4108b8)=='\\Data\\Data1.lpRes'
assert n.number(0x4015a0)==40 and n.number(0x4020ec)==50 and n.number(0x401598)==15 and n.number(0x4023d8)==16
assert n.number(0x401f18,'<d')==.5 and n.number(0x4020b0,'<d')==1.8
pack=json.loads((root/'public/assets/sprites/Data1/index.json').read_text(encoding='utf8'))
evidence=root/'reports'/name
report={'passed':True,'sourceExeSha256':hashlib.sha256(n.data).hexdigest(),'evidenceFile':str(evidence.relative_to(root)).replace('\\','/'),'evidenceSha256':hashlib.sha256(evidence.read_bytes()).hexdigest(),'spriteSourceSha256':pack['sha256'],
 'rules':{'fps':50,'capacity':1024,'monsterStatusEmitters':{'freeze':{'field':'+b2','type':0},'burn':{'field':'+ae','type':1},'poison':{'field':'+a6','type':2}},'emitPeriod':30,'emitPhase':'remaining status ticks modulo 30, before decrement','rgbWordLayout':{'r':'+1c','g':'+20','b':'+1e'},'sprites':{'0':[32,33],'1':[25],'2':[31],'3':[31],'4':[31],'8':[31]},'alphaDecayPerTick':{'0':5,'2':5,'3':20,'4':5,'8':20},'burnColorStages':['green -20 until zero','red -20 until zero','alpha -10 until zero'],'burnInitialRgb':[255,255,0],'poisonInitialRgb':[0,255,0],'drawPivot':'top-left of original canvas; common native 6325c0 uses zero rotation center'},
 'limits':['Other particle types, weather and teleport/death emitters remain separate work.','This verifies monster/friendly-unit status emitters, not a guessed identical player emitter.','Native numeric/gameplay randomness is not reseeded by the visual tests.']}
(root/'reports/audit-fixes-20261012/native-status-particles-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print({'passed':True,'statusTypes':[0,1,2],'restorationFadePerTick':20,'originalSprites':[25,31,32,33]})
