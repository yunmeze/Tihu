"""Copy the approved candidate bytes to ordinary assets; no runtime/source changes."""
from pathlib import Path
import json,hashlib,shutil
from PIL import Image
HERE=Path(__file__).resolve().parent;P=HERE.parents[1];OUT=P/'assets/earth/environment/training_hall_v1'
APPROVED_SOURCE_REGISTRATION_SHA='0b086e70162f6f79de76f311b662c7b66bb54ee6a3b4d7cf9a9cd806459a4c6c'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 source=HERE/'registration.json';assert sha(source)==APPROVED_SOURCE_REGISTRATION_SHA,'Source changed; request review before packaging'
 reg=json.loads(source.read_text());assert reg['validation']['full_rgba_reassembly_exact'];OUT.mkdir(parents=True,exist_ok=True)
 raw=P/reg['raw_texture'][6:];dst=OUT/'whole-review.png';shutil.copyfile(raw,dst);assert sha(dst)==reg['raw_sha256'];reg['raw_texture']='res://'+str(dst.relative_to(P));reg['raw_texture_size']=list(Image.open(dst).size);reg['raw_texture_sha256']=sha(dst);reg['raw_usage']='Parity/evidence only. Never draw as the normal whole-building sprite over actors.'
 entries=[]
 for e in reg['owners']:
  if e['texture']is not None:
   src=P/e['texture'][6:];dst=OUT/src.name;shutil.copyfile(src,dst);assert sha(dst)==e['sha256'];e['texture']='res://'+str(dst.relative_to(P));e['texture_size']=list(Image.open(dst).size);e['texture_sha256']=sha(dst)
  else:
   assert e['frame_index']in[3966,3978] and e['layer']==1 and e['visible_pixel_count']==0
   binding={k:e[k]for k in ['key','pack','frame_index','cell','source_cell','flag','layer','sort_y','stable_source_order']};binding['whole_raw_sha256']=reg['raw_sha256'];binding['source_registration_sha256']=APPROVED_SOURCE_REGISTRATION_SHA;encoded=json.dumps(binding,sort_keys=True,separators=(',',':')).encode();e['empty_identity_binding_sha256']=hashlib.sha256(encoded).hexdigest();entries.append({'key':e['key'],'frame_index':e['frame_index'],'binding':binding,'binding_sha256':e['empty_identity_binding_sha256']})
 reg['source_registration_sha256']=APPROVED_SOURCE_REGISTRATION_SHA;reg['packaging']='Byte-identical copies to ordinary assets; source registration remains independent evidence.';reg['empty_owner_contracts']=entries;reg['runtime_integration']='Hall-specific validator must preserve all30 identities atomically, permit only these2 hash-bound empty upper owners, suppress their original art, and retain original ordering. Do not weaken shared asset_guard.'
 out=OUT/'registration.json';out.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n')
 files=[]
 for f in sorted(OUT.glob('*')):
  if f.is_file() and f.name!='PACKAGE_FILES.json':files.append({'path':str(f.relative_to(P)),'bytes':f.stat().st_size,'sha256':sha(f)})
 report={'status':'ordinary candidate package only; native integration/acceptance owned by runner','source_registration_sha256':APPROVED_SOURCE_REGISTRATION_SHA,'ordinary_registration_sha256':sha(out),'owner_count':30,'layer_counts':{'0':12,'1':18},'owner_texture_count':28,'empty_owner_ids':[3966,3978],'whole_rgba_sha256':reg['raw_sha256'],'byte_identical_copies':True,'files':files,'count':len(files),'bytes':sum(f['bytes']for f in files),'reproduce':'python Project/art_source/earth_training_hall_registration_v1/package_candidate.py'}
 (OUT/'PACKAGE_FILES.json').write_text(json.dumps(report,indent=2)+'\n');(HERE/'production-package.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='files'}))
if __name__=='__main__':main()
