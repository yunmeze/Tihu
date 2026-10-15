from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;repo=P.parents[2];A=P.parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
folders=['earth_hero_s_input_plan_v1','earth_hero_s_idle_v1','earth_hero_s_idle_edit_plan_v1','earth_hero_s_idle_edit_v1'];files=[]
for name in folders:
 q=A/name;manifest=q/'MINIMAL_SHA_MANIFEST.json';m=json.loads(manifest.read_text())
 for f in m['files']:
  x=q/f['path'];assert sha(x)==f['sha256'];files.append({'path':str(x.relative_to(repo)),'sha256':sha(x)})
 files.append({'path':str(manifest.relative_to(repo)),'sha256':sha(manifest)})
m={'purpose':'explicit archive/staging allowlist for parent; no Git run by worker','files':files,'self':'Project/art_source/earth_hero_s_idle_edit_v1/ARCHIVE_ALLOWLIST.json','frozen_versions':['original S source input','first full S raw and original registration','edit plan and independent phase proxy measurements','edited raw and frozen registration copy'],'exclude':['Project/diagnostics/**','**/*.import','runtime assets and scripts','other workers files','old courtyard generated identities'],'read_only_dependencies':'See each MINIMAL_SHA_MANIFEST.json; do not blindly stage dependency paths.'}
(P/'ARCHIVE_ALLOWLIST.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print('Archive allowlist verified',len(files),'files plus this allowlist itself; no Git.')
