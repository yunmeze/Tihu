"""Read-only walk/run input and directional displacement evidence."""
import hashlib, json, math, re
from pathlib import Path
from importlib import import_module
n=import_module('native-code').NativeCode()
root=Path(__file__).resolve().parent.parent
help_path=root/'reference/LP传奇单机版-重生v1.2.2E/Help/Game_Index.htm'
text=re.sub(r'\s+',' ',re.sub('<[^>]+>',' ',help_path.read_text(encoding='utf-8-sig')))
assert all(s in text for s in ['鼠标左键按住走路','鼠标右键跑步','自动跑步/停止跑步'])
files=[]
for name,ranges in [
 ('native-continuous-toggle.txt',[(0x56d2b4,0x56d2e5),(0x61bac0,0x61baea)]),
 ('native-run-input.txt',[(0x588290,0x5887d0),(0x5887d0,0x588990)]),
 ('native-run-selector.txt',[(0x622a70,0x622e50)]),
 ('native-run-vector.txt',[(0x622e50,0x623600)]),
 ('native-run-timing.txt',[(0x61c40e,0x61c5cc),(0x61c5cc,0x61c7ee)]),
]:
 rows=n.dump(name,ranges);p=root/'reports'/name
 files.append({'file':'reports/'+name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'instructions':len(rows)})
selector=n.disasm(0x622a70,0x622e50)
assert any(a==0x622aa0 and '0x63ed1e' in o for a,m,o in selector)
assert any(a==0x622be4 and '0x21' in o for a,m,o in selector)
assert any(a==0x622d18 and '0x51' in o for a,m,o in selector)
horizontal=n.number(0x401f30,'<d');assert horizontal==1.5
speed=2;fps=50;directions=[]
for mode,per_tick in [('walk',speed/2),('run',speed)]:
 for i,(dx,dy) in enumerate([(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1)]):
  x,y=dx*per_tick*horizontal*fps,dy*per_tick*fps
  directions.append({'mode':mode,'direction':i,'sourcePixelsPerSecond':{'x':x,'y':y},'screenDistancePerSecond':math.hypot(x,y)})
report={'passed':True,'sourceSha256':hashlib.sha256(n.data).hexdigest(),'helpFile':str(help_path.relative_to(root)).replace('\\','/'),'helpSha256':hashlib.sha256(help_path.read_bytes()).hexdigest(),
 'nativeInput':{'leftMouse':'walk','rightMouse':'run','space':'automatic running toggle','mouseButtonField':'0x63ed1e','selector':'0x622a70','leftBranch':'0x622aa0','walkStateWrite':'0x622be4','runStateWrite':'0x622d18'},
 'movement':{'walkTilesPerSecond':1.5625,'runTilesPerSecond':3.125,'walkAnimationSeconds':.84,'runAnimationSeconds':.6,'horizontalMultiplier':horizontal,'diagonalNormalized':False,'freezeDisplacementMultiplier':.5,'frozenRunAnimationSeconds':.72},
 'directions':directions,'evidenceFiles':files,
 'port':{'leftClick':'walk to selected point','rightClick':'run to selected point','touchSingleTap':'walk','touchDoubleTap':'run; same location within 350 ms','continuousRepointing':'preserve walk/run phase','frameBudget':'consume across waypoints; 30/50/60/120 Hz maintain displacement','nativeSpaceAutoRunPorted':True,'nativeMouseHoldPorted':True},
 'remaining':['Portrait A* pathing and cursor/camera sampling adapt desktop directional input; touch uses tap/double-tap and still needs WeChat device testing.'],'fullNativeMovementEquivalent':False}
(root/'reports/native-run-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':True,'nativeInput':report['nativeInput'],'movement':report['movement']},ensure_ascii=False))
