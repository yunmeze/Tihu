import sys, json, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'Threejs-33Days/.tools/python'))
import UnityPy
root=Path(__file__).resolve().parents[1]
env=UnityPy.load(str(root/'reference/Desktop Hellfarmer/Desktop Hellfarmer_Data'))
counts=collections.Counter(o.type.name for o in env.objects)
entries=[]
for o in env.objects:
    try:
        name=o.peek_name() or ''
        tree=None
        if o.type.name in ['Shader','MonoScript']: tree=o.read_typetree()
        if o.type.name=='Shader': name=tree.get('m_ParsedForm',{}).get('m_Name',name)
        entries.append(dict(type=o.type.name,id=str(o.path_id),source=o.assets_file.name,name=name))
    except Exception as e: entries.append(dict(type=o.type.name,id=str(o.path_id),error=str(e)))
out=root/'reports';out.mkdir(exist_ok=True)
(out/'source-inventory.json').write_text(json.dumps(dict(counts=counts,entries=entries),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(counts))
for kind in ['Shader','GameObject','MonoScript','AnimationClip','Mesh','Texture2D']:
    print(kind, json.dumps([e['name'] for e in entries if e['type']==kind and e.get('name')][:180]))
for kind in ['Mesh','AnimationClip','MonoBehaviour','SkinnedMeshRenderer','ParticleSystem','Sprite']:
    ob=next(o for o in env.objects if o.type.name==kind)
    try:
        tree=ob.read_typetree()
        (out/(kind+'-sample.json')).write_text(json.dumps(tree,default=str,indent=2),encoding='utf-8')
        print(kind, list(tree))
    except Exception as ex: print(kind,str(ex))
