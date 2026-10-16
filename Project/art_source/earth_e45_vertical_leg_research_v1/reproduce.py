"""Rebuild phase45 research candidate without modifying source or runtime assets."""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
from PIL import Image
O=Path(__file__).resolve().parent
A=O.parent

def load(p): return Image.open(p).convert('RGBA')
def mask(p): return np.array(Image.open(p))>0

def reproduce(output):
    provenance=json.loads((O/'ARCHIVE_PROVENANCE.json').read_text())
    for path,digest in provenance['input_sha256'].items():
        assert hashlib.sha256((A/path).read_bytes()).hexdigest()==digest,path
    # Rebuild the original split core directly from archived source, not diagnostic layers.
    core=load(A/'earth_e_layered_parts_v1/raw.png').crop((0,0,512,512))
    a=np.array(core)
    bg=Image.open(A/'earth_e_parts_density_review_v1/background-only-proposed-keep-mask.png').crop((0,0,512,512))
    a[np.array(bg)==0,3]=0
    core=Image.fromarray(a.copy())
    scale=33/387
    translation=[39-292*scale,16-29*scale]
    affine=(1/(4*scale),0,-translation[0]/scale,0,1/(4*scale),-translation[1]/scale)
    core=core.transform((512,512),Image.Transform.AFFINE,affine,resample=Image.Resampling.BICUBIC)
    fm=Image.open(A/'earth_e_49_cloth_patch_v1/core-shoulder-front-mask.png').transform((512,512),Image.Transform.AFFINE,affine,resample=Image.Resampling.NEAREST)
    back=np.array(core);front=back.copy()
    back[np.array(fm)>0,3]=0;front[np.array(fm)==0,3]=0
    layers=[load(A/'earth_e_four_phase_rigid_study_v1/45-left-rigid-HD4.png')]
    for part in [back,front]:
        shifted=Image.new('RGBA',(512,512));shifted.alpha_composite(Image.fromarray(part.copy()),(4,0));layers.append(shifted)
    layers.insert(2,load(A/'earth_e_upper45_context_edit_plan_v1/arm45-context-rigid.png'))
    context=load(A/'earth_e_upper45_context_edit_plan_v1/old45-upper-REPLACEMENT-CONTEXT.png')
    protect=Image.new('RGBA',(512,512))
    for layer in layers:context.alpha_composite(layer);protect.alpha_composite(layer)
    cloth=load(A/'earth_e_upper45_context_edit_v1/mapped-whole-image-UNMASKED.png')
    union=mask(A/'earth_e_upper45_context_edit_v1/actual-fixed-union-mask.png')
    waist=mask(A/'earth_e_45_underlap_bridge_v1/waist89-actual-mask.png')
    bridge=mask(A/'earth_e_45_underlap_bridge_v1/knee178-actual-mask.png')
    plate=np.array(context);plate[union]=np.array(cloth)[union]
    over=cloth.copy();over.alpha_composite(protect);plate[waist]=np.array(over)[waist]
    # Crucial independent copy: the obsolete knee bridge stage is never applied.
    corrected=Image.fromarray(plate.copy())
    assert np.array_equal(plate,np.array(load(O/'corrected-replay-NO-FRONT-NO-BRIDGE.png')))
    actual_reference=np.array(load(O/'references/ref1-full-context-front-removed-512.png'))
    delta=np.any(plate!=actual_reference,axis=2)
    assert delta.sum()==178 and not (delta&~bridge).any()
    remove=mask(O/'FROZEN-OLD-CLOTH-RESIDUE-REMOVAL-mask.png')
    assert remove.sum()==96 and not (remove&~union).any()
    assert np.array_equal(plate[remove],np.array(cloth)[remove])
    revised=plate.copy();revised[remove,3]=0
    support0=mask(O/'new-part-max-support.png')
    added=mask(O/'approved-21px-instep-addition.png')
    support=support0|added
    assert support0.sum()==5253 and added.sum()==21 and support.sum()==5274
    owned=(np.array(load(A/'earth_e_four_phase_rigid_study_v1/45-right-rigid-HD4.png'))[:,:,3]>0)|bridge
    domain=owned|support|remove
    raw=load(O/'raw.png');assert raw.size==(1254,1254)
    donor=np.array(raw.resize((512,512),Image.Resampling.BICUBIC));donor[~support,3]=0
    result=Image.fromarray(donor.copy());result.alpha_composite(Image.fromarray(revised.copy()))
    result=np.array(result);frozen=np.array(load(A/'earth_e_walk_layered_research_v1/45-HD4-RESEARCH.png'))
    result[~domain]=frozen[~domain]
    opaque=(plate[:,:,3]==255)&~remove
    assert np.array_equal(result[opaque],plate[opaque])
    assert np.array_equal(result,np.array(load(O/'45-HD4-CLOTH-CLEANED-RESEARCH.png')))
    output=Path(output).resolve();assert not output.exists(),'Refusing to overwrite output'
    output.mkdir(parents=True)
    Image.fromarray(result.copy()).save(output/'45-HD4-CLOTH-CLEANED-RESEARCH.png')
    Image.fromarray(result.copy()).resize((128,128),Image.Resampling.LANCZOS).save(output/'45-128-CLOTH-CLEANED-RESEARCH.png')
    corrected.save(output/'corrected-replay-NO-FRONT-NO-BRIDGE.png')
    digest=hashlib.sha256((output/'45-HD4-CLOTH-CLEANED-RESEARCH.png').read_bytes()).hexdigest()
    print(json.dumps({'RGBA_different_pixels':0,'sha256':digest,'byte_identical':digest==provenance['final_sha256'],'bridge_correction_pixels':178,'cloth_removal_pixels':96,'support_pixels':5274,'changed_vs_frozen':int(np.any(result!=frozen,axis=2).sum())}))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    reproduce(parser.parse_args().output)
