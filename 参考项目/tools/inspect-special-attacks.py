"""Read-only native evidence for mixed, spread and cyclic boss attacks."""
from pathlib import Path
from importlib import import_module
import hashlib,json,struct
n=import_module('native-code').NativeCode();root=Path(__file__).resolve().parent.parent
ranges=[(0x5cbade,0x5ccca7),(0x5a37fb,0x5a3ab3),(0x5c8470,0x5c85e4),(0x633f50,0x634142)]
rows=n.dump('audit-fixes-20261012/native-special-attack-source.txt',ranges)
at={a:(m,o) for a,m,o in rows}
assert at[0x5c8554]==('inc','word ptr [esi + 0x3a]')
assert at[0x5c855c]==('cmp','ax, 0x2710')
assert at[0x5cbfce]==('cmp','word ptr [esi + 0x3a], 0x1f4')
assert at[0x5cc2e4]==('cmp','word ptr [esi + 0x3a], 0x1f4')
assert at[0x5cc0c6]==('mov','word ptr [esi + 0x3a], 0')
assert at[0x5cc4c8]==('mov','word ptr [esi + 0x3a], 0')
assert n.number(0x401f38)==3 and n.number(0x4016f8)==30
assert n.number(0x402fb8)==180 and abs(n.number(0x402fbc)-3.14159265)<1e-6
radial=[]
for a,m,o in rows:
 if 0x5cc0bf<=a<0x5cc2e4 and m=='push' and (o=='0' or o.startswith('0x4')):
  value=struct.unpack('<f',struct.pack('<I',int(o,0)))[0]
  if value!=5:radial.append(round(value))
assert radial==list(range(0,360,30)),radial
evidence=root/'reports/audit-fixes-20261012/native-special-attack-source.txt'
report={'passed':True,'sourceExeSha256':hashlib.sha256(n.data).hexdigest(),'evidenceFile':'reports/audit-fixes-20261012/native-special-attack-source.txt','evidenceSha256':hashlib.sha256(evidence.read_bytes()).hexdigest(),
 'rules':{'actorTimer':{'field':'+0x3a','fps':50,'threshold':500,'cap':10000,'scope':'per alive monster, not one global boss timer'},
 '23':{'types':[48,48],'nativePixelOrigins':[[-26,-62],[74,-62]]},
 '24':{'types':[47,46,46],'nativePixelOrigins':[[24,-32],[-26,-72],[74,-72]]},
 '26':{'type':38,'nativeAngleOffsets':[-3,0,3,-30,30],'pixelsPerTick':[5.6,6.5,5.6,5,5],'angleFromMonsterPixel':[-20,-37],'angleToPlayerPixel':[24,-16],'nativePixelOrigin':[0,-32]},
 '27':{'before500':'twin explosive fire from [-26,-62] / [74,-62]','burstType':39,'burstAngles':radial,'burstPixelsPerTick':5,'burstOrigin':[0,-32],'resetActorTimer':True},
 '28':{'before500':'Rnd < .5: explosive fire and ice, otherwise one persistent cell at target','after500':'three persistent cells, each orientation branch uses a new Rnd < .25','hazardFrames':4000,'resetActorTimer':True}},
 'webLimits':['Projectile cell/actor collision remains swept web collision rather than every native occupancy query.','Non-burst projectile velocity and all native lifetimes are not fully traced.','No complete original-client frame-by-frame replay or WeChat device verification.']}
(root/'reports/audit-fixes-20261012/native-special-attack-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print({'passed':True,'attackKinds':[23,24,26,27,28],'burstAngles':len(radial),'timer':'per actor'})
