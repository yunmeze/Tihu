from pathlib import Path
import argparse,hashlib,json
import numpy as np
from PIL import Image
O=Path(__file__).resolve().parent
P=O.parents[1]
def js(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return Image.open(p).convert('RGBA')
def verify_inputs():
    provenance=js(O/'ARCHIVE_PROVENANCE.json')
    for path,digest in provenance['input_sha256'].items():assert sha(P/path)==digest,path
    return provenance

def source_group(members,bounds):
    manifest=js(P/'assets/original/manifest.json');source_map=js(P/'data/maps/A13.json')
    source=Image.new('RGBA',(bounds[2]-bounds[0],bounds[3]-bounds[1]));pages={}
    for item in sorted(members,key=lambda v:(v['layer'],v['sort_y'],v['stable_source_order'])):
        cx,cy=item['cell'];order=cx*source_map['height']+cy
        assert order==item['stable_source_order'] and source_map['cells'][order]==item['source_cell']
        pack=manifest['packs'][item['pack']];frame=pack['frames'][str(item['index'])]
        assert frame['rect']==item['source_frame']['atlas_rect']
        page=P/pack['pages'][frame['page']]['file'][6:]
        if page not in pages:pages[page]=load(page)
        x,y,w,h=frame['rect'];tile=pages[page].crop((x,y,x+w,y+h))
        assert hashlib.sha256(tile.tobytes()).hexdigest()==item['source_frame']['rgba_sha256']
        b=item['all_frame_bounds_xyxy'];assert [w,h]==[b[2]-b[0],b[3]-b[1]]
        source.alpha_composite(tile,(b[0]-bounds[0],b[1]-bounds[1]))
    return source

def reproduce(output):
    provenance=verify_inputs();output=Path(output).resolve();assert not output.exists();output.mkdir(parents=True)
    group=js(O/'SOURCE_GROUP.json');source=source_group(group['members'],group['bounds_xyxy'])
    padded=Image.new('RGBA',(1024,1024));padded.alpha_composite(source.resize((640,496),Image.Resampling.NEAREST),(192,264))
    assert np.array_equal(np.array(padded),np.array(load(O/'references/source-padded-reference.png')))
    padded.save(output/'source-padded-reference.png');assert sha(output/'source-padded-reference.png')==sha(O/'references/source-padded-reference.png')
    reg=js(O/'LANDMARK_REGISTRATION.json');rows=reg['training']
    x=np.array([r['source_logical_xy'] for r in rows]);y=np.array([r['raw_xy'] for r in rows]);xc=x-x.mean(0)
    density=float(np.sum(xc*(y-y.mean(0)))/np.sum(xc*xc));translation=y.mean(0)-density*x.mean(0)
    assert abs(density-reg['density_raw_pixels_per_source_logical_unit'])<1e-12
    assert np.allclose(translation,reg['raw_translation_for_source_group_origin_xy'],atol=1e-10)
    raw=load(O/'raw.png');d=reg['density_raw_pixels_per_source_logical_unit'];tx,ty=reg['raw_translation_for_source_group_origin_xy']
    result=raw.transform((640,496),Image.Transform.AFFINE,(d/2,0,tx,0,d/2,ty),Image.Resampling.BILINEAR)
    assert np.array_equal(np.array(result),np.array(load(O/'pool-registered-research-2x.png')))
    result.save(output/'pool-registered-research-2x.png');digest=sha(output/'pool-registered-research-2x.png');assert digest==provenance['final_sha256']
    # Evidence only: no owner textures exported and no alpha discarded.
    owner=js(O/'OWNER_PARTITION_PROPOSAL.json');coverage=np.zeros((496,640),np.uint8)
    for item in owner['owners']:
        x0,y0,x1,y1=item['local_2x_bounds'];coverage[y0:y1,x0:x1]+=1
    alpha=np.array(result)[:,:,3];assert not (coverage>1).any()
    for threshold,count in owner['candidate_outside_original_owner_rect_union'].items():assert int(((alpha>int(threshold))&(coverage==0)).sum())==count
    print(json.dumps({'byte_identical':True,'RGBA_different_pixels':0,'sha256':digest,'source_reference_byte_identical':True,'owner_partition':'proposal only','owners':7}))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Reproduce research-only candidate; no cleanup or runtime change.')
    parser.add_argument('--output',type=Path,required=True);reproduce(parser.parse_args().output)
