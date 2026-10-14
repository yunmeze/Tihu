"""Read-only single-strip flight rotation evidence from the shipped EXE."""
import hashlib,json
from pathlib import Path
from importlib import import_module
n=import_module('native-code').NativeCode();root=Path(__file__).resolve().parent.parent
blocks={14:(0x5bba44,0x5bbbbb),15:(0x5bbd38,0x5bbeae),16:(0x5bc02b,0x5bc1a1),17:(0x5bc31e,0x5bc494),6:(0x5bd28b,0x5bd3fc),41:(0x5bed42,0x5beebf),42:(0x5beebf,0x5bf03c),43:(0x5bf03c,0x5bf1b9),44:(0x5bf1b9,0x5bf375),45:(0x5bf375,0x5bf4f2),46:(0x5bf4f2,0x5bf66f),47:(0x5bf66f,0x5bf7ec),48:(0x5bf7ec,0x5bf969),49:(0x5bf969,0x5bfae6),38:(0x5c035b,0x5c04a3),39:(0x5c04a3,0x5c0620)}
randomSpin=blocks.pop(44) # Native 5bf27a..5bf29d random spin, not a heading.
allrows=n.disasm(0x5bb270,0x5c0620);branchProof=[]
for type,(lo,hi) in blocks.items():
 rows=[r for r in allrows if lo<=r[0]<hi]
 assert rows[0][1:] == ('cmp',f'cl, {hex(type) if type>9 else type}')
 angles=[a for a,m,o in rows if (m=='add' and o.endswith(', 0x18')) or (m=='lea' and o.endswith('+ 0x18]'))]
 jumps=[a for a,m,o in rows if (m=='jmp' and o in ['0x5c061a','0x5c061b','0x5c05e6']) or (m=='call' and o=='0x6326b0')]
 if any(m=='jmp' and o=='0x5c05e6' for a,m,o in rows):angles.append(0x5c05e9)
 assert angles and jumps,(type,angles,jumps)
 branchProof.append({'type':type,'branch':hex(lo),'anglePointer':hex(angles[-1]),'commonDrawJump':hex(jumps[-1])})
files=[]
for name,ranges in [('flight-branches',list(blocks.values())+[randomSpin,(0x5c05e6,0x5c0620)]),('heading',[(0x5a31b6,0x5a3533),(0x634000,0x634142)]),('rotated-draw',[(0x6326b0,0x632819)])]:
 n.dump('native-projectile-orientation-'+name+'.txt',ranges)
 path=root/'reports'/('native-projectile-orientation-'+name+'.txt');files.append({'file':'reports/'+path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
assert n.number(0x402148,'<f')==360
assert n.string(0x411fb0)=='6.lpRes'
assert any(a==0x5a3495 and m=='fstp' and o=='dword ptr [ecx + eax*4 + 0x18]' for a,m,o in n.disasm(0x5a31b6,0x5a3533))
assert any(a==0x5c061b and m=='call' and o=='0x6326b0' for a,m,o in n.disasm(0x5c061a,0x5c0620))
assert any(a==0x63279a and m=='mov' and o=='eax, dword ptr [ebp + 0x14]' for a,m,o in n.disasm(0x6326b0,0x632819))
packs={6:'18',14:'6',15:'8',16:'10',17:'12',38:'38',39:'38',41:'51',42:'52',43:'53',45:'55',46:'6',47:'8',48:'10',49:'12'}
sprites=[]
for type,id in packs.items():
 p=root/'public/assets/sprites/Mgc'/id/'index.json';pack=json.loads(p.read_text('utf8'))
 assert all(f['offset']==[0,0] for f in pack['frames'][1:])
 sprites.append({'type':type,'pack':'Mgc/'+id,'sourceSha256':pack['sha256'],'frames':len(pack['frames'])-1})
report={'passed':True,'sourceSha256':hashlib.sha256(n.data).hexdigest(),'evidenceFiles':files,'flightBranches':branchProof,'sprites':sprites,
 'rules':{'rotatedProjectileTypes':sorted(blocks),'sourceAngleField':'effect float +0x18; written at5a3495','sourceDraw':'5c061b calls6326b0, rotation argument at63279a..6327aa','originalSheetForward':'up','screenGridPixels':[48,32],'webClockwiseAngle':'atan2(vx*48,-vy*32)','pivot':'original uncropped canvas center, at projected cell center +24/-20; preserve transparent crop position','eightDirectionSheets':'keep original direction-specific frames; no additional rotation','stationaryImpacts':'retain original offset/animation and do not inherit moving-projectile rotation'},
 'limits':['This verifies visual orientation and source rotation routes. Native special collision/speed/timing equivalence remains partial.','Type44 Mgc/54 has random per-draw spin (5bf27a..5bf29d), not heading rotation; its existing ball rendering is retained in this repair.','No WeChat device validation.']}
(root/'reports/native-projectile-orientation-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print({'passed':True,'rotatedFlightTypes':len(blocks)})
