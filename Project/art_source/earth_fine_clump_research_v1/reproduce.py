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
    first=js(O/'SOURCE_AND_FIRST_CONTRACT.json');source=source_group(first['owner_contract'],[3037,1772,3154,1844])
    padded=Image.new('RGBA',(1024,1024));padded.alpha_composite(source.resize((936,576),Image.Resampling.NEAREST),(44,224))
    assert np.array_equal(np.array(padded),np.array(load(O/'references/source-padded-density8.png')))
    padded.save(output/'source-padded-density8.png');assert sha(output/'source-padded-density8.png')==sha(O/'references/source-padded-density8.png')
    raw=load(O/'raw.png');assert raw.size==(1254,1254)
    result=raw.resize((512,512),Image.Resampling.LANCZOS)
    assert np.array_equal(np.array(result),np.array(load(O/'candidate-density4-fullcanvas.png')))
    result.save(output/'candidate-density4-fullcanvas.png');digest=sha(output/'candidate-density4-fullcanvas.png');assert digest==provenance['final_sha256']
    proposal=js(O/'OWNER_EXTENSION_PROPOSAL.json');a=np.array(result);yy,xx=np.indices(a.shape[:2]);x=(xx+.5)/4-5.5;y=(yy+.5)/4-28
    union=np.zeros(x.shape,bool);original=np.zeros(x.shape,bool);counts=np.zeros(x.shape,np.uint8);full=np.zeros_like(a);fullcounts=np.zeros(x.shape,np.uint8)
    for item,strip in zip(proposal['members'],[x<35,(x>=35)&(x<83),x>=83]):
        def rect(b):return (x>=b[0])&(y>=b[1])&(x<b[2])&(y<b[3])
        old=rect(item['original_bounds']);new=rect(item['proposed_support_bounds']);original|=old;union|=new;counts+=new;fullcounts+=strip;full[strip]=a[strip]
        assert int(((a[:,:,3]>=128)&new&~old).sum())==item['added_strong_pixels']
    assert not (counts>1).any() and fullcounts.min()==fullcounts.max()==1 and np.array_equal(full,a)
    assert int(((a[:,:,3]>=128)&~original).sum())==proposal['density4_strong_spill_pixels']==68
    assert int(((a[:,:,3]>0)&~union).sum())==proposal['unassigned_nonzero_alpha_pixels']==560
    assert int(a[:,:,3][~union].max())==proposal['unassigned_alpha_max']==2
    assert not ((a[:,:,3]>=8)&~union).any()
    print(json.dumps({'byte_identical':True,'RGBA_different_pixels':0,'sha256':digest,'source_reference_byte_identical':True,'strong_spill_pixels':68,'lowalpha_unassigned_pixels':560,'lowalpha_max':2,'owner_extension':'proposal only; no split exports'}))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Reproduce research-only candidate; no cleanup or runtime change.')
    parser.add_argument('--output',type=Path,required=True);reproduce(parser.parse_args().output)
