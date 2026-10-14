from source import load,ROOT
import json,collections
e=load(); counts=collections.Counter(); samples={}
for o in e.objects:
    if o.type.name!='MonoBehaviour': continue
    try:
        d=o.read(check_read=False)
        s=d.m_Script.deref().read(); name=s.m_ClassName;counts[name]+=1
        if name not in samples and (s.m_AssemblyName=='Assembly-CSharp.dll' or name in ['Image','TextMeshProUGUI','CanvasScaler']):
            samples[name]=o.read_typetree()
    except Exception as ex: samples.setdefault('errors',[]).append(str(ex))
(ROOT/'reports/component-samples.json').write_text(json.dumps(samples,default=str,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(counts,ensure_ascii=False));print('samples',list(samples))
