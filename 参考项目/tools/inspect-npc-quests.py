"""Recover special-skill recipes from the extracted, unchanged native scripts."""
import json,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def recover_acquisition():
 out={};evidence=[]
 for skill,map_id,npc_name in [('炼尸咒','C03','蛙林老人'),('诱惑之光','D02','隐士')]:
  m=json.loads((ROOT/f'public/assets/maps/{map_id}.json').read_text(encoding='utf8'));npc=next(n for n in m['npcs'] if n['name']==npc_name);script=npc['script'];steps=[]
  for match in re.finditer(r'#sub\s+(\S+)\s*([\s\S]*?)(?=#sub\b|\Z)',script,re.I):
   page,body=match.groups();level=re.search(r'#change\s+'+skill+r'\s*=\s*(\d+)',body,re.I)
   if level:
    materials=[{'name':name.strip(),'quantity':int(quantity)} for name,quantity in re.findall(r'#take\s+([^\r\n]+?)\s+(\d+)\s*(?:\r?\n|$)',body,re.I)]
    steps.append({'level':int(level[1]),'page':page.upper(),'materials':materials})
  steps.sort(key=lambda s:s['level']);assert [s['level'] for s in steps]==list(range(1,(3 if skill=='炼尸咒' else 5)+1)),(skill,steps)
  out[skill]={'map':map_id,'mapName':m['name'],'npc':npc_name,'maxLevel':len(steps),'steps':steps,'sourceSha256':m['sourceSha256']}
  evidence.append({'skill':skill,**out[skill],'scriptSha256':hashlib.sha256(script.encode('utf8')).hexdigest(),'script':script})
 return out,evidence
if __name__=='__main__':
 acquisition,evidence=recover_acquisition();report={'source':'Unchanged NPC/map/monster script strings extracted from LP传奇重生 v1.2.2E','specialSkills':evidence,'nativeFunctions':{'query':'0x606de0','change':'0x608b20','give':'0x6041c0','setMapData':'0x606330'},'evidenceFiles':['native-npc-query.txt','native-npc-change.txt','native-npc-give.txt','native-mapdata-mutation.txt','native-npc-field-source.json'],'adaptations':['Portrait dialogue pages and choice pagination retain the native text and branch targets.','#LABEL START is accepted as an alias used in the supplied NPC scripts.','NPC coordinates/removal and object changes are saved per character; transient monster removals are not persisted across map visits.','Unsupported active instructions abort the whole exchange instead of granting a partial reward.','42 physical inventory slots and worn/bag carry weight are enforced; quest reward overflow retains its exact instance attributes on the ground.']}
 report['sourceSha256']=hashlib.sha256((ROOT/'reference/LP传奇单机版-重生v1.2.2E/LP传奇单机版_重生.exe').read_bytes()).hexdigest()
 report['nativeFunctions']['setMapFlag']='0x6060c0';report['evidenceFiles'].append('native-mapflag-mutation.txt')
 (ROOT/'reports/native-quest-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:{'map':v['map'],'npc':v['npc'],'levels':v['maxLevel']} for k,v in acquisition.items()},ensure_ascii=False))
