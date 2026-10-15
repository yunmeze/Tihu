#!/usr/bin/env python3
"""Decode the fixed original Config opening record and verify reference reflow inputs."""
import hashlib,json,pathlib,re,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from lp_original import Reader
ROOT=pathlib.Path(__file__).resolve().parents[3]
source=ROOT/'参考项目/public/assets/data/story.json'
record=json.loads(source.read_text())
raw=(ROOT/'原版游戏/Config.dat').read_bytes()
source_sha=hashlib.sha256(raw).hexdigest()
assert source_sha=='53adb0ec6983a0a3cb15fe544f4f138dcdcbd6cae707322910727a6805f9c54d', 'Unexpected Config source revision'
reader=Reader(raw,8,start=96)
script=reader.string()
assert reader.pos-96==850, 'Unexpected opening record length'
assert hashlib.sha256(script.encode()).hexdigest()=='11e2e7b4a02001b25a2b145dcd441c1bb8c873e1bf0fc94b1717aa4ae79a7c89'
assert record['sourceSha256']==source_sha and record['opening']['offset']==96 and record['opening']['bytes']==850
assert script==record['opening']['script'], 'Reference opening differs from original Config bytes' 
pages=[]
for line in script.splitlines():
    match=re.fullmatch(r'#P\s+(\S+)(?:\s+(\S+))?(?:\s+(\d+))?\s*',line,re.I)
    if match: pages.append({'color':match[1],'secondary':match[2] or '黑','lines':[]})
    elif pages and not line.startswith('#'):pages[-1]['lines'].append(line)
for page in pages:
    out=[]
    for line in page.pop('lines'):
        if not line.strip():
            if out and out[-1]!='\n':out.append('\n')
            continue
        if out and out[-1]!='\n' and line.startswith('　'):out.append('\n')
        out.append(line.rstrip())
    page['text']=''.join(out).strip('\n')
dest=re.search(r'^#To\s+(\S+)\s+(\d+)\s+(\d+)\s*$',script,re.I|re.M)
assert len(pages)==5 and dest and dest.groups() == ('A13','61','39')
result={'schema':'original-opening-pages-v1','source':record['source'],'source_sha256':source_sha,'offset':record['opening']['offset'],'bytes':record['opening']['bytes'],'script':script,'script_sha256':hashlib.sha256(script.encode()).hexdigest(),'pages':pages,'destination':{'map':'A13','x':61,'y':39},'reflow_reference':'参考项目/src/ending.js storyPages/reflow'}
out=ROOT/'Project/data/story/opening.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('OPENING_EXTRACT_PASS',len(pages),result['script_sha256'])
