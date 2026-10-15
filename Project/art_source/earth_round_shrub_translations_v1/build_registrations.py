from pathlib import Path
import json,hashlib,copy
P=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
basepath=P/'art_source/earth_round_shrub_registration_v1/registration.json';base=read(basepath)
assert sha(basepath)=='a4633ce2be29f8296439032ab9f291b04f9cf2ead4047e338bb4d01f2332b9dc'
s=read(P/'art_source/earth_vegetation_input_plan_v1/source_contract.json');groups={g['id']:g for g in s['groups']};m=read(P/'data/maps/A13.json')
instances=[]
for name,delta in [('round_shrub_51_44',[-288,192]),('round_shrub_64_45',[336,224])]:
 g=groups[name];r=copy.deepcopy(base);r['status']='Translated static candidate; independent runtime diagnostic pending; not ordinary promoted';r['approval_scope']=f'Only {name}; four exact original owner identities; independent all-or-nothing fallback'
 r['translation_from_center_world']=delta;r['center_registration_sha256']=sha(basepath);r['whole_shrub_registration']['world_top_left']=[base['whole_shrub_registration']['world_top_left'][i]+delta[i] for i in range(2)]
 for a,b in zip(r['owners'],g['owners_in_draw_order']):
  assert a['frame_index']==b['frame_index'];x,y=b['cell'];assert m['cells'][x*m['height']+y]==b['source_cell']
  for k in ['pack','key','cell','source_cell','flag','layer','sort_y','stable_source_order','frame_index']:a[k]=b[k]
  a['world_top_left']=r['whole_shrub_registration']['world_top_left'][:]
  assert sha(P/a['texture'][6:])==a['texture_sha256']
 r['suppress_source_keys']=[o['key'] for o in r['owners']]
 r['fallback_contract']='Validate all four exact native source_cell arrays and textures before suppressing any source. Any failure falls back only this complete group; other shrubs remain independent.'
 filename='registration_'+name.removeprefix('round_shrub_')+'.json';write(D/filename,r);instances.append({'instance':name,'registration':'res://'+str((D/filename).relative_to(P)),'sha256':sha(D/filename),'world_top_left':r['whole_shrub_registration']['world_top_left'],'delta':delta})
write(D/'instances.json',{'status':'three-instance bounded candidate closure; only center already ordinary approved','center':{'registration':'res://assets/earth/environment/round_shrub_v1/registration.json','sha256':sha(P/'assets/earth/environment/round_shrub_v1/registration.json')},'pending_diag':instances,'shared_textures':[{'path':o['texture'],'sha256':o['texture_sha256']} for o in base['owners']],'raw':{'path':base['raw_texture'],'sha256':base['raw_sha256']},'partition':base['partition'],'all_rgba_ownership_unchanged':True,'new_generation':False})
print(json.dumps(instances,indent=2))
