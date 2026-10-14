from source import load
from UnityPy.helpers import TypeTreeHelper as h
from UnityPy.helpers.Tpk import get_typetree_node
e=load();h.read_typetree_boost=None
def norm(node):
 for n in node.traverse():
  if n.m_Children and n.m_Children[0].m_Type=='Array' and n.m_Type in h.FUNCTION_READ_MAP and not(n.m_Type=='string' and n.m_Children[0].m_Children[1].m_Type=='char'):n.m_Type='vector'
 return node
def ref(r,af):
 t=r['type']; print('REF',r['rid'],t,flush=True)
 if not t['class']:return None
 n=norm(e.typetree_generator.get_nodes_up(t['asm'],t['ns']+'.'+t['class']))
 if n.m_Children and n.m_Children[0].m_Name=='m_GameObject':n.m_Children=n.m_Children[4:]
 if t['class'] in ['VisualElementAsset','TemplateAsset','UxmlObjectAsset'] and not any(x.m_Name=='m_Parent' for x in n.m_Children):
  from UnityPy.helpers.TypeTreeNode import TypeTreeNode
  n.m_Children.insert(3,TypeTreeNode(m_Level=1,m_Type='managedReference',m_Name='m_Parent',m_ByteSize=8,m_Version=1,m_Children=[TypeTreeNode(m_Level=2,m_Type='SInt64',m_Name='rid',m_ByteSize=8,m_Version=1)]))
 print([(x.m_Name,x.m_Type,x.m_MetaFlag)for x in n.m_Children],flush=True)
 return n
h.get_ref_type_node=ref
orig=h.read_value
def read(n,r,c):
 p=r.Position
 try:
  v=orig(n,r,c)
  if n.m_Name in ['m_FullTypeName','m_XmlNamespace','m_Id','prefix','resolvedNamespace','rid']:print('VAL',n.m_Name,p,r.Position,v,flush=True)
  return v
 except Exception:
  print('FAIL',n.m_Name,n.m_Type,p,r.Position,flush=True);raise
h.read_value=read
for o in e.objects:
 if o.type.name!='MonoBehaviour' or o.path_id!=184 or o.assets_file.name!='sharedassets0.assets':continue
 n=norm(o.generate_monobehaviour_node());n.m_Children=get_typetree_node(114,o.version).m_Children+n.m_Children[4:]
 try:print(o.read_typetree(nodes=n))
 except Exception:pass
