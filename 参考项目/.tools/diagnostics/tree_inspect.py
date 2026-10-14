import json
c=json.load(open('public/assets/catalog.json'))
for k,v in c['components'].items():
 if v['type']=='VisualTreeAsset' and v['data']['m_Name'] in ['FarmWindow','LootReviewInventoryWindow','ToolbarButton','ManagementWindowTemplate','PlayerStatus']:
  d=v['data'];print('TREE',k,d['m_Name'],{n:d[n]for n in d if n!='references'})
  rs=d['references']['RefIds']
  for r in rs:
   if r['type']['class'] in ['VisualElementAsset','TemplateAsset']:
    print(r['rid'],r['type']['class'],r['data'])
