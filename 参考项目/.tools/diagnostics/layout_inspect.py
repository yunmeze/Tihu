import json
c=json.load(open('public/assets/catalog.json'))
print('STRUCTURE',list(c))
for k,v in c['sprites'].items():
 if k.startswith('sharedassets0.assets:') and int(k.split(':')[-1]) in [77,85,95,98]:print(k,v)
for k,v in c['components'].items():
 if v['type'] in ['UiToolkitManagementWindowLayout','DesktopManagementModeRegistry','DesktopManagementModeSettings']:print('BOUNDS',k,str(v)[:1500])
r=json.load(open('public/assets/ui/layout.json'))
for n in ['ManagementWindow','LootReviewInventoryWindow','SkillTreeWindow','ZoneWindow','SettingsWindow']:
 print(n)
 for rule in r[n]:
  p=rule['properties']
  if 'hover' in str(rule['selectors']) or 'disabled' in str(rule['selectors']):continue
  print(','.join(rule['selectors']),'; '.join(k+'='+str(v) for k,v in p.items() if k in ['Width','Height','PaddingLeft','PaddingRight','PaddingTop','PaddingBottom','MarginLeft','MarginRight','MarginTop','MarginBottom','FontSize','BackgroundImage','Left','Right','Top','Bottom','FlexDirection','FlexGrow','MinHeight','Position','UnityFontDefinition']))
