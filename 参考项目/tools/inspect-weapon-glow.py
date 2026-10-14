"""Read-only evidence for the shipped merged-weapon rendering passes."""
from pathlib import Path
from importlib import import_module
import hashlib,json
n=import_module('native-code').NativeCode()
all_rows=n.disasm(0x5c1180,0x5c2b40)
rows=[r for r in all_rows if 0x5c1a50<=r[0]<0x5c1ad7 or 0x5c1bfa<=r[0]<0x5c1ebc or 0x5c25cd<=r[0]<0x5c2894]
at={a:(m,o) for a,m,o in rows}
assert at[0x5c1a5f]==('mov','ax, word ptr [ecx + 0x554]')
assert at[0x5c1a6d]==('imul','ax, ax, 0x32')
assert at[0x5c1a75]==('add','eax, 0x37')
assert at[0x5c1a83]==('mov','word ptr [0x63f006], 0x32')
assert at[0x5c1a71]==('add','cx, 5') and at[0x5c1aab]==('add','ax, 0xfffb')
assert at[0x5c1a78]==('cmp','cx, 0xff') and at[0x5c1aaf]==('cmp','ax, 0x32')
assert at[0x5c1c08]==('cmp','word ptr [esi + 0x1f78], 0')
assert at[0x5c25db]==('cmp','word ptr [esi + 0x1f78], 4')
assert n.number(0x401624)==2
calls=[hex(a) for a,m,o in rows if m=='call' and o=='0x6323b0']
assert len(calls)==8
root=Path(__file__).resolve().parent.parent;target=root/'reports/audit-fixes-20261012/native-weapon-glow.txt'
target.write_text('\n'.join(f'{a:08x} {m:8s} {o}' for a,m,o in rows),encoding='utf8')
report={'passed':True,'sourceExeSha256':hashlib.sha256(n.data).hexdigest(),'evidenceSha256':hashlib.sha256(target.read_bytes()).hexdigest(),'rules':{'gradeField':'+0x554','condition':'merge grade > 0','rgb':['grade*50+55',50,0],'alphaStep':5,'turnWhenAscendingAbove':255,'turnWhenDescendingBelow':50,'offsetSourcePixels':2,'withoutHorizontalPassDirections':[0,4],'passOrder':'Displaced glow copies before ordinary tinted weapon, retaining normal body/weapon depth order','nativeDrawCalls':calls},'adaptations':['Use elapsed time at the native 50-Hz rhythm rather than browser render count.','Scene, role portrait and saved-character preview share one assembly function.','Browser opacity clamps the native pulse overshoot to 0..255.']}
(target.with_suffix('.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print({'passed':True,'glowPasses':len(calls),'offsetPixels':2})
