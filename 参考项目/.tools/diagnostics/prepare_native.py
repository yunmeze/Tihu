from source import ROOT,load
import sys,json,re
def dump(obj,level=0):
    pad=' '*level;lines=[]
    for k,v in obj.items():
        if isinstance(v,dict):lines.append(pad+k+':\n'+dump(v,level+2))
        elif isinstance(v,list) and v and isinstance(v[0],dict):
            lines.append(pad+k+':')
            for item in v:
                text=dump(item,level+2).splitlines();lines.append(pad+'- '+text[0].lstrip());lines.extend(text[1:])
        else:lines.append(pad+k+': '+json.dumps(v,ensure_ascii=False,separators=(',',':')))
    return '\n'.join(lines)
e=load();out=ROOT/'.tools/unity/Assets/Original';out.mkdir(parents=True,exist_ok=True)
for o in e.objects:
    if o.type.name not in ['AnimationClip','Avatar']:continue
    d=o.read_typetree();filename=str(o.path_id)+('.anim' if o.type.name=='AnimationClip' else '.asset');name=o.type.name
    text='%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!'+str(o.class_id)+' &'+str(o.path_id)+'\n'+dump({name:d})+'\n'
    (out/filename).write_text(text,encoding='utf-8')
print('Prepared original native clips and avatars')
