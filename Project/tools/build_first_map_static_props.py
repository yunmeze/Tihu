#!/usr/bin/env python3
"""Reproduce the optional first-map static-prop registration. Never modifies art."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from PIL import Image

PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT / 'assets/earth/first_map_review/static_props_registration.json'
CLUMP_SUPPORT = [[20.5,176,162,375.5],[162,104.5,354,402.5],[354,105.5,490,356]]
MASTER_SHA = {'pool':'55a2ac86f1d7e5274e89c155439eaa38d5b880d6396e5b327b29780abe0433ea','clump':'56fe91ccc0e9b1909f48cde77ff8219b8845d1d31cb6844fbc535cbfc7c56980'}

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def res(path: Path) -> str:
    return 'res://' + path.relative_to(PROJECT).as_posix()

def pin(path: Path, role: str) -> dict:
    entry={'path':res(path),'sha256':sha(path),'bytes':path.stat().st_size,'type':path.suffix[1:],'role':role}
    if path.suffix=='.png':
        with Image.open(path) as im: entry.update(width=im.width,height=im.height)
    return entry

def build() -> dict:
    source_map=PROJECT/'data/maps/A13.json'; source_manifest=PROJECT/'assets/original/manifest.json'
    map_data=json.loads(source_map.read_text()); packs=json.loads(source_manifest.read_text())['packs']
    assert (map_data['id'],map_data['width'],map_data['height'])==('A13',100,100)
    assert sha(source_map)=='d09549838963c8157307cc5406d3118baf69259d82459bcba0a3a8be5b34aa27'
    runtime={res(source_map):pin(source_map,'source-map'),res(source_manifest):pin(source_manifest,'source-atlas-manifest')}
    result={'schema':'earth-first-map-static-props-v1','status':'Selected bounded static-prop research integration in optional first_map_review only; not whole-map art acceptance; Windows not validated.','source_map':pin(source_map,'source-map'),'source_manifest':pin(source_manifest,'source-atlas-manifest'),'groups':{},'provenance':[]}
    for name,dirname,filename,source_file,member_key,density,origin,size in [
        ('pool','earth_pool_research_v1','pool-registered-research-2x.png','SOURCE_GROUP.json','members',2,[3086,1800],[640,496]),
        ('clump','earth_fine_clump_research_v1','candidate-density4-fullcanvas.png','SOURCE_AND_FIRST_CONTRACT.json','owner_contract',4,[3031.5,1744],[512,512])]:
        base=PROJECT/'art_source'/dirname; master=base/filename
        assert sha(master)==MASTER_SHA[name]
        image=Image.open(master).convert('RGBA'); assert list(image.size)==size
        source=json.loads((base/source_file).read_text()); owners=[]; dependencies=[runtime[res(source_map)],runtime[res(source_manifest)],pin(master,'texture')]
        for i,old in enumerate(source[member_key]):
            order=old['stable_source_order'];sf=old['source_frame'];pack=packs[old['pack']];frame=pack['frames'][str(old['index'])]
            assert map_data['cells'][order]==old['source_cell']
            assert all(frame[k]==sf[v] for k,v in [('original','original'),('crop','crop'),('offset','offset'),('rect','atlas_rect')])
            atlas=PROJECT/sf['atlas'].removeprefix('res://'); assert pack['pages'][frame['page']]['file']==res(atlas)
            atlas_pin=pin(atlas,'source-atlas');runtime[res(atlas)]=atlas_pin
            if atlas_pin not in dependencies:dependencies.append(atlas_pin)
            x,y,w,h=frame['rect']; cropped=Image.open(atlas).convert('RGBA').crop((x,y,x+w,y+h))
            assert hashlib.sha256(cropped.tobytes()).hexdigest()==sf['rgba_sha256']
            wb=old['all_frame_bounds_xyxy']; original=[(wb[k]-origin[k%2])*density for k in range(4)]
            support=original if name=='pool' else CLUMP_SUPPORT[i]
            owners.append({'index':old['index'],'pack':old['pack'],'cell':old['cell'],'source_cell':old['source_cell'],'layer':old['layer'],'sort_y':old['sort_y'],'stable_source_order':order,'source_world_bounds':wb,'source_frame':{'original':frame['original'],'crop':frame['crop'],'offset':frame['offset'],'page':frame['page'],'rect':frame['rect'],'atlas':res(atlas)},'support_px_half_open':support})
        for i,a in enumerate(owners):
            x0,y0,x1,y1=a['support_px_half_open'];assert 0<=x0<x1<=size[0] and 0<=y0<y1<=size[1]
            for b in owners[:i]:
                l,t,r,d=b['support_px_half_open'];assert not(max(x0,l)<min(x1,r) and max(y0,t)<min(y1,d))
        omitted=[]
        for y in range(size[1]):
            for x in range(size[0]):
                alpha=image.getpixel((x,y))[3]
                if alpha and not any(r[0]<=x+.5<r[2] and r[1]<=y+.5<r[3] for r in (o['support_px_half_open'] for o in owners)):omitted.append(alpha)
        expected=(12,1) if name=='pool' else (551,2);assert(len(omitted),max(omitted))==expected
        runtime[res(master)]=pin(master,'texture')
        result['groups'][name]={'owner_count':len(owners),'master':pin(master,'texture'),'density':density,'world_origin':origin,'logical_size':[size[0]/density,size[1]/density],'sampling':'One unchanged shared full-master CanvasTexture, LINEAR, draw_texture_rect_region clip_uv=false. Half-open geometry; no per-owner texture/mask or alpha threshold.','support_selection':'original seven source rectangles' if name=='pool' else 'bounded half-texel outer filtering halo; internal x seams unchanged','omitted_texel_centers':{'alpha_positive':len(omitted),'max_alpha':max(omitted),'alpha_histogram':{str(a):omitted.count(a) for a in sorted(set(omitted))},'alpha8plus':sum(a>=8 for a in omitted),'alpha128plus':sum(a>=128 for a in omitted)},'outside_finite_master':{'nonzero_samples':36,'max_alpha':1,'note':'Existing finite pool master excludes these larger raw-mapped-view samples; runtime does not additionally discard them.'} if name=='pool' else None,'source_dependencies':dependencies,'owners':owners}
        provenance_files=[base/source_file,base/('OWNER_PARTITION_PROPOSAL.json' if name=='pool' else 'OWNER_EXTENSION_PROPOSAL.json'),base/'README.md']
        result['provenance'].extend(pin(f,'provenance-only-not-runtime') for f in provenance_files)
    result['runtime_files']=sorted(runtime.values(),key=lambda v:v['path'])
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=DEFAULT_OUTPUT);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    document=build();payload=json.dumps(document,ensure_ascii=False,indent=2)+'\n'
    if args.check:
        assert args.output.is_file() and args.output.read_text()==payload, 'Registration differs from deterministic frozen build'
    else:
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(payload)
    print(f'{args.output}\nsha256={sha(args.output)}\nruntime_files={len(document["runtime_files"])}')
