"""Read-only, bounded evidence for the remaining original gameplay routes."""
from pathlib import Path
from importlib import import_module
import json,hashlib

root=Path(__file__).resolve().parent.parent
n=import_module('native-code').NativeCode()
out=root/'reports/restoration-20261013'
out.mkdir(exist_ok=True)
groups={
 'native-particle-pool':[(0x5c5b00,0x5c7910)],
 'native-weather-emission':[(0x5b53d0,0x5b5f18)],
 'native-rotation':[(0x6325c0,0x632820)],
 'native-guard-rebirth':[(0x5c8470,0x5c9930)],
 'native-ground-glow':[(n.prolog(0x5b7765),0x5b8686)],
 'native-particle-sprites':[(0x5999d0,0x59a2c2)],
}
files=[];code={}
for name,ranges in groups.items():
 rows=n.dump('restoration-20261013/'+name+'.txt',ranges)
 code[name]={a:(m,o) for a,m,o in rows}
 file=out/(name+'.txt')
 files.append({'file':file.relative_to(root).as_posix(),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'instructions':len(rows)})
assert code['native-guard-rebirth'][0x5c8577]==('add','eax, -3')
assert code['native-guard-rebirth'][0x5c8583]==('add','edx, 3')
assert n.string(0x411f58)=='明阳守卫'
assert n.string(0x411e44)=='天界-天路'
assert n.string(0x411e60)=='天界-三明界'
assert n.string(0x411e74)=='天界-轮回'
assert code['native-guard-rebirth'][0x5c9207]==('mov','word ptr [esi + 0x32], 0x16')
assert code['native-guard-rebirth'][0x5c91de]==('add','word ptr [esi + 0x6c], 0xa')
constants={hex(a):n.number(a,fmt) for a,fmt in [(0x4020e0,'<d'),(0x401798,'<d'),(0x4017a0,'<d'),(0x402450,'<f'),(0x40159c,'<f'),(0x401ec4,'<f'),(0x402148,'<f')]}
assert list(constants.values())==[.3,.7,.2,18.,20.,120.,360.]
report={'passed':True,'source':n.source.relative_to(root).as_posix(),'sourceSha256':hashlib.sha256(n.data).hexdigest(),'evidenceFiles':files,'constants':constants,
 'guard':{'name':'明阳守卫','currentHpFraction':.3,'recoveryPoolFraction':.7,'recoveryPerTick':3,'retainOriginalMaxHp':True,'speedAdd':.2,'attackAdd':-15,'defenseAdd':10,'magicDefenseAdd':5,'vision':5,'attackKind':22,'particle':7,'sound':n.string(0x4125cc),'rewardsAfterFinalDeathOnly':True},
 'ambient':{'天界-天路':{'type':9,'period':2},'天界-三明界':{'type':20,'period':3},'天界-轮回':{'type':20,'period':3}},
 'ground':{'insight':4,'itemTypes':[7,14],'crossPriceRange':[10,15],'rainbowPriceMinimum':15,'mergeGradeAlsoRainbow':True,'crossPeriod':20,'rainbowPeriod':10,'paralysisParticle':22},
 'limits':['Weather types10..16 entry flag still unresolved.','Particle6 emitter not connected in this change.','Special collision and conditional drop multiplier are not claimed complete.','Native random distribution and constants are retained; browser floating point is not bitwise VB6 equivalence.']}
(out/'native-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'passed':True,'evidenceFiles':len(files),'guard':report['guard']},ensure_ascii=False))
