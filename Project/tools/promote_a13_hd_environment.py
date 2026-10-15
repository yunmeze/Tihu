"""Rebuild and promote bounded A13 HD environment assets; never modifies runtime/map."""
from pathlib import Path
import json,hashlib,shutil,subprocess,sys
from PIL import Image
P=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def dump(p,a):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(a,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def copy(src,dst):dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);assert sha(src)==sha(dst);return 'res://'+str(dst.relative_to(P))
for script in ['art_source/a13_upright_tree_candidate_v1/build_partition.py','art_source/a13_grass_clumps_candidate_v1/build_partition.py','art_source/a13_ground_hd2x_sampling/export_probe.py','art_source/a13_second_tree_reuse/export_candidate.py']:
 subprocess.run([sys.executable,str(P/script)],check=True)
base=P/'assets/scifi/environment';T=P/'art_source/a13_upright_tree_candidate_v1';tr=read(T/'technical_v1/registration.json');dest=base/'a13_upright_tree_v1';mapping={}
for o in tr['owners']:
 src=P/o['texture'][6:];mapping[o['texture']]=copy(src,dest/src.name)
whole=copy(T/'raw.png',dest/'whole_tree.png');owners=[];instances=[]
for inst in tr['instances']:
 oo=[]
 for o in inst['owners']:
  o=dict(o);o['texture']=mapping[o['texture']];oo.append(o);owners.append(o)
 instances.append({**inst,'status':'bounded first-screen working reuse; source flags preserved','owners':oo})
r={**tr,'schema':'a13-upright-tree-selected-hd-v1','status':'parent-approved bounded HD working composition','owners':owners,'instances':instances,'suppress_source_keys':[o['key']for o in owners],'whole_alpha_texture':whole,'raw_provenance_sha256':tr['raw_sha256'],'acceptance':{'samepose_only_cells':[[61,50],[61,54],[61,56]],'blocked_fixture_cell':[61,50],'actual_astar_route':[[61,39],[61,54]],'actual_ticks':480,'whole_split_gpu_max_rgb':1,'whole_split_gpu_changed_pixels':26,'cpu_reassembly_byte_exact':True,'cast':'single ground cast per instance on/off visually reviewed','scope':'three exact source-family instances; no other source-family instances changed'},'guard_contract':{'unit':'complete6-owner instance','check_actual_png_sha256_in_source_project':True,'invalid':'restore all6 original keys and hide that instance cast','fields':['cell','source_cell','layer','sort_y','stable_source_order','texture','texture_sha256','texture_size','world_top_left','scale'],'exported_build_note':'Raw file SHA proof is source-project verification; exported imported resources need explicit supported validation, not a claimed filesystem hash.'}}
r.pop('raw_texture',None);r['limits']=[v for v in r['limits']if 'No new cast'not in v and 'First61'not in v];dump(dest/'registration.json',r)
shadow=read(T/'technical_v1/shadow.json');shadow['texture']=whole;shadow['status']='parent-approved bounded HD working flat-ground cast';shadow['limits']=[v for v in shadow['limits']if 'First61'not in v];dump(dest/'shadow.json',shadow)
G=P/'art_source/a13_grass_clumps_candidate_v1';gr=read(G/'technical_v1/registration.json');dest=base/'a13_grass_clumps_v1';groups=[];flat=[]
for g in gr['groups']:
 mapping={}
 for o in g['owners']:
  src=P/o['texture'][6:];mapping[o['texture']]=copy(src,dest/src.name)
 instances=[]
 for i in g['instances']:
  oo=[]
  for o in i['owners']:
   o=dict(o);o['texture']=mapping[o['texture']];oo.append(o);flat.append(o)
  instances.append({**i,'owners':oo})
 gg={**g,'owners':[{**o,'texture':mapping[o['texture']]}for o in g['owners']],'instances':instances};gg.pop('whole_texture',None);gg['whole_texture_provenance_sha256']=gg.pop('whole_texture_sha256');groups.append(gg)
r={**gr,'schema':'a13-grass-clumps-selected-hd-v1','status':'parent-approved bounded HD working body; no standalone new grass cast','groups':groups,'owners':flat,'suppress_source_keys':[o['key']for o in flat],'acceptance':{'whole_split_gpu':{'239-240':{'max_rgb':0,'changed':0},'241-242':{'max_rgb':1,'changed':4}},'source_instances':3,'actual2x_composition_reviewed':True},'guard_contract':{'unit':'complete2-owner instance','invalid':'restore both source keys; no new grass cast present','actual_sha_scope':'source-project PNG files; do not claim exported Texture2D byte hash without separate implementation'}};dump(dest/'registration.json',r)
# Only these143 original floor placements are included; outside remains source.
src=base/'a13_ground_hd2x_probe';dest=base/'a13_ground_hd2x_v1';r=read(src/'registration.json')
for o in r['placements']:
 p=P/o['texture'][6:];o['texture']=copy(p,dest/p.name)
r['schema']='a13-ground-first-screen-hd2x-v1';r['status']='parent-approved first-screen working HD material scope; mirror pattern residual remains';r['guard_contract']={'unit':'all143 exact floor keys','invalid':'restore entire source floor scope','actual_sha_scope':'source-project PNG bytes; exported imported resources need separate validation'};r['limits']=['World period256,2texels/world unit,512world mirror superperiod; not a doubled world layout.','First143 only, outside source; not fullA13 completion.','Mirror symmetric dark motifs remain.','No independent terrain shadow; receive existing scene shadows.'];dump(dest/'registration.json',r)
# The second tree shares all first-tree PNGs and has no new generated image.
dest=base/'a13_second_tree_reuse_v1';r=read(dest/'registration.json');r['status']='parent-approved second exact-source-family instance in bounded HD composition';r['acceptance_scope']['native_second_instance']='actual2048 first-screen composition reviewed'
for o in r['owners']:
 o['texture_sha256']=sha(P/o['texture'][6:]);o['texture_size']=list(Image.open(P/o['texture'][6:]).size)
dump(dest/'registration.json',r);s=read(dest/'shadow.json');s['status']='parent-approved translated second-instance single cast in HD composition';s['reuse_native_acceptance']='second-instance root/cast visible in reviewed actual2048 first-screen composition; original first-instance routes remain historical';dump(dest/'shadow.json',s)
# Verify every emitted runtime texture from actual files, not only declared strings.
checks=[]
for name in ['a13_upright_tree_v1','a13_grass_clumps_v1','a13_second_tree_reuse_v1']:
 r=read(base/name/'registration.json');keys=[o['key']for o in r['owners']];assert len(keys)==len(set(keys))
 for o in r['owners']:
  path=P/o['texture'][6:];expected=o.get('texture_sha256',o.get('sha256'));assert sha(path)==expected
 checks.append({'group':name,'keys':len(keys),'actual_source_project_png_sha_pass':True})
r=read(base/'a13_ground_hd2x_v1/registration.json')
for o in r['placements']:assert sha(P/o['texture'][6:])==o['texture_sha256']
checks.append({'group':'a13_ground_hd2x_v1','keys':len(r['placements']),'actual_source_project_png_sha_pass':True});out=P/'diagnostics/art_source/a13-ground/hd-production-verification.json';dump(out,{'checks':checks,'runtime_modified':False});print(checks)
