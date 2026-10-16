"""Reproduce bounded phase48 research composition; never modify source assets."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
from PIL import Image,ImageDraw
O=Path(__file__).resolve().parent
A=O.parent

def load(p):return Image.open(p).convert('RGBA')
def mask(p):return np.array(Image.open(p))>0

def reproduce(output):
    provenance=json.loads((O/'ARCHIVE_PROVENANCE.json').read_text())
    for path,digest in provenance['input_sha256'].items():
        assert hashlib.sha256((A/path).read_bytes()).hexdigest()==digest,path
    # Rebuild original no-right fixed stack from tracked source and pants registration.
    left=load(A/'earth_e_four_phase_rigid_study_v1/48-left-rigid-HD4.png')
    right=load(A/'earth_e_four_phase_rigid_study_v1/48-right-rigid-HD4.png')
    upper=load(A/'earth_e_four_phase_rigid_study_v1/48-using-arm49-CORE-ONLY-RESEARCH.png')
    cloth=load(A/'earth_e_47_48_50_context_plan_v1/48-old-upper-WITH-HAND-HOLE.png')
    fixed_union=mask(A/'earth_e_47_48_context_edits_v1/48/fixed-union-mask.png')
    pants_registration=json.loads((A/'earth_e_47_48_similarity_audit_v1/MEASUREMENTS.json').read_text())['48']
    pants_raw=load(A/'earth_e_47_48_context_edits_v1/48/raw.png')
    s=pants_registration['uniform_scale_source_to_mapped_raw']
    tx,ty=pants_registration['translation_source_to_mapped_raw'];q=512/pants_raw.width
    pants=np.array(pants_raw.transform((512,512),Image.Transform.AFFINE,(s/q,0,tx/q,0,s/q,ty/q),resample=Image.Resampling.BICUBIC))
    pants[~fixed_union,3]=0;pants=Image.fromarray(pants.copy())
    protect=Image.new('RGBA',(512,512))
    for layer in [left,upper]:protect.alpha_composite(layer)
    context=cloth.copy();context.alpha_composite(protect)
    base=np.array(context);over=np.array(Image.alpha_composite(pants,protect));base[fixed_union]=over[fixed_union]
    assert np.array_equal(base,np.array(load(O/'references/ref1-context-missing-right.png')))
    # The five upper-body fit and two held-out rear-leg measurements were frozen independently.
    reg=json.loads((O/'GLOBAL_REGISTRATION.json').read_text())
    rows=reg['evidence']['rows'];fit=[r for r in rows if r['role']=='fit']
    src=np.array([r['source_center'] for r in fit]);dst=np.array([r['matched_center'] for r in fit])
    centered=src-src.mean(0);scale=float(np.sum(centered*(dst-dst.mean(0)))/np.sum(centered**2))
    translation=dst.mean(0)-scale*src.mean(0)
    assert abs(scale-reg['scale_reference_to_fixedmap'])<1e-12
    assert np.allclose(translation,reg['translation_reference_to_fixedmap_HD4'],atol=1e-10)
    assert [r['name'] for r in fit]==['head','shoulder','chest','forearm','hand']
    assert {r['name'] for r in rows if r['role']=='held_out'}=={'rear_shin','rear_boot'}
    raw=load(O/'raw.png')
    registered=raw.transform((512,512),Image.Transform.AFFINE,reg['output_HD4_to_raw_affine'],resample=Image.Resampling.BICUBIC)
    assert np.array_equal(np.array(registered),np.array(load(O/'attempt2-rejected/references/ref1-registered-context-EDIT.png')))
    # Separate explicit donor translation, not a fit or further scale/rotation.
    contract=json.loads((O/'BEFORE_COMPOSITE_CONTRACT.json').read_text())
    window=Image.new('L',(512,512));ImageDraw.Draw(window).polygon([tuple(p) for p in contract['source_polygon_HD4']],fill=255)
    selected=mask(O/'FROZEN-source-donor-window.png');assert np.array_equal(np.array(window)>0,selected)
    donor=np.array(registered);owned=selected&(donor[:,:,3]>0)
    knots=json.loads((O/'RIGID_TRANSLATION_MEASUREMENTS.json').read_text())['provisional_material_boundary_knots_HD4']
    yy,xx=np.indices((512,512));boundary=np.interp(xx,[v[0] for v in knots],[v[1] for v in knots])
    provisional=(xx>=188)&(xx<=260)&(yy>=boundary)&(yy<324)&(donor[:,:,3]>0)
    underlap=owned&~provisional
    assert underlap.sum()==377 and np.array_equal(underlap,mask(O/'FROZEN-proximal-underlap-source.png'))
    donor[~selected,3]=0;shifted=Image.new('RGBA',(512,512))
    assert contract['whole_donor_translation_HD4']==[-10,0]
    shifted.alpha_composite(Image.fromarray(donor.copy()),(-10,0))
    alpha=np.array(shifted)[:,:,3]>0
    assert not (alpha&~mask(O/'FROZEN-newpart-support.png')).any()
    old_owned=np.array(right)[:,:,3]>0
    assert np.array_equal(old_owned,mask(O/'FROZEN-old-right-ownership.png'))
    domain=old_owned|alpha
    frozen=np.array(load(A/'earth_e_walk_layered_research_v1/48-HD4-RESEARCH.png'))
    result=np.array(Image.alpha_composite(shifted,Image.fromarray(base.copy())))
    result[~domain]=frozen[~domain]
    assert np.array_equal(result[base[:,:,3]==255],base[base[:,:,3]==255])
    assert np.array_equal(result,np.array(load(O/'48-HD4-BOUNDED-DONOR-DIAGNOSTIC.png')))
    output=Path(output).resolve();assert not output.exists(),'Refusing to overwrite output';output.mkdir(parents=True)
    Image.fromarray(result.copy()).save(output/'48-HD4-BOUNDED-DONOR-DIAGNOSTIC.png')
    registered.save(output/'REGISTERED-WHOLE-RAW-UNEXTRACTED.png')
    digest=hashlib.sha256((output/'48-HD4-BOUNDED-DONOR-DIAGNOSTIC.png').read_bytes()).hexdigest()
    print(json.dumps({'RGBA_different_pixels':0,'sha256':digest,'byte_identical':digest==provenance['final_sha256'],'underlap_alpha_pixels':int(underlap.sum()),'changed_vs_frozen':int(np.any(result!=frozen,axis=2).sum())}))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    reproduce(parser.parse_args().output)
