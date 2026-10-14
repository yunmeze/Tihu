"""Read original input only; write fresh parity evidence, never edit game assets."""
from pathlib import Path
from importlib import import_module
import json,re,hashlib
n=import_module('native-code').NativeCode()
root=Path(__file__).resolve().parent.parent
out=root/'reports/parity-audit-20261013'
out.mkdir(parents=True,exist_ok=True)
assert hashlib.sha256(n.data).hexdigest()=='21dc753d3aa828fb29dc171e595857be234833edc43a1d80833540ae7e355b84'
records=[]
for label,lo,hi in [('monster-update-drop',0x5c8470,0x5cd03a),('hero-death',0x61e4e5,0x61e654),('conditional-drop',0x5d5af0,0x5d6546),('shield-expiry-flash',0x5c2b4e,0x5c2dbe)]:
 rows=n.disasm(lo,hi)
 strings=[]
 lines=[]
 for a,m,o in rows:
  annotation=[]
  for value in re.findall(r'0x[0-9a-f]+',o):
   address=int(value,16)
   if not 0x403000<address<0x430000:continue
   try:
    s=n.string(address)
    if s and len(s)<500 and all(c.isprintable() or c in '\r\n\t' for c in s):
     annotation.append(s);strings.append({'instruction':hex(a),'address':value,'text':s})
   except (ValueError,StopIteration,AssertionError,UnicodeError):pass
  lines.append(f'{a:08x} {m:8} {o}'+(' ; '+repr(annotation) if annotation else ''))
 file=out/(label+'.txt');file.write_text('\n'.join(lines),encoding='utf8')
 records.append({'name':label,'file':str(file.relative_to(root)).replace('\\','/'),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'instructions':len(rows),'strings':strings})
report={'source':str(n.source.relative_to(root)).replace('\\','/'),'sha256':hashlib.sha256(n.data).hexdigest(),'sections':records,'bossTimerReductionRandomScale':n.number(0x401ee4)}
(out/'native-evidence.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
for row in records:print(json.dumps({'name':row['name'],'strings':row['strings']},ensure_ascii=False))
print('boss timer random scale:',report['bossTimerReductionRandomScale'])
