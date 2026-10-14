from source import ROOT,load
from extract_assets import key,write_json
from UnityPy.helpers.Tpk import get_typetree_node
import json
e=load();c=json.loads((ROOT/'public/assets/catalog.json').read_text(encoding='utf8'))
for o in e.objects:
    if o.type.name!='MonoBehaviour':continue
    try:
        h=o.parse_monobehaviour_head();s=h.m_Script.deref().read()
        if s.m_ClassName!='VisualTreeAsset':continue
        node=o.generate_monobehaviour_node();node.m_Children=get_typetree_node(114,o.version).m_Children+node.m_Children[4:]
        node.m_Children=[x for x in node.m_Children if x.m_Name!='references']
        d=o.read_typetree(nodes=node,check_read=False);c['components'][key(o)]={'type':'VisualTreeAsset','data':d}
        print(o.peek_name(),len(d.get('m_VisualElementAssets',[])),list(d))
    except Exception as ex:print('UI',o.path_id,str(ex))
write_json(ROOT/'public/assets/catalog.json',c)
