#!/usr/bin/env python3
"""Build fail-closed Earth sample receiver and common SE cast envelope.
Offline-only inputs may live in art_source; emitted runtime dependencies never do.
Requires Pillow and numpy. Raster cells are conservative area coverage, not centers.
"""
from pathlib import Path
import hashlib, json
import numpy as np
from PIL import Image
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/earth/shadows/se_flat_v1'
D = 2
SAMPLE = [2496, 960, 768, 512]
HALL_SHA = '57072cc60ed9e33aa9afaeb0c7310733216e2884e0b042b043077551473e273c'
inputs = {}
def path(p): return ROOT / p.removeprefix('res://')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def track(p):
    p=path(p); inputs[str(p.relative_to(ROOT))]=sha(p); return p
def read(p): return json.loads(track(p).read_text())
def alpha(p): return np.array(Image.open(track(p)).convert('RGBA'))[:,:,3] > 0

def raster(rects, origin, size):
    """Every cell intersecting an AABB is covered; exact boundary is excluded."""
    w,h=map(int,size); diff=np.zeros((h+1,w+1),dtype=np.int32)
    if len(rects):
        r=np.asarray(rects,dtype=float).reshape(-1,4)
        lo=np.floor((r[:,:2]-origin)*D).astype(int)
        hi=np.ceil((r[:,2:]-origin)*D).astype(int)
        lo=np.maximum(lo,0); hi=np.minimum(hi,[w,h])
        valid=np.all(hi>lo,axis=1);lo=lo[valid];hi=hi[valid]
        for xx,yy,v in [(lo[:,0],lo[:,1],1),(hi[:,0],lo[:,1],-1),(lo[:,0],hi[:,1],-1),(hi[:,0],hi[:,1],1)]:
            np.add.at(diff,(yy,xx),v)
    return diff.cumsum(0).cumsum(1)[:h,:w]>0

def verify_coverage(mask, rects, origin):
    """Independent summed-area proof: every intersected cell of each box is set."""
    h,w=mask.shape
    r=np.asarray(rects,dtype=float).reshape(-1,4)
    lo=np.maximum(np.floor((r[:,:2]-origin)*D).astype(int),0)
    hi=np.minimum(np.ceil((r[:,2:]-origin)*D).astype(int),[w,h])
    valid=np.all(hi>lo,axis=1);lo=lo[valid];hi=hi[valid]
    table=np.pad(mask.astype(np.int64),((1,0),(1,0))).cumsum(0).cumsum(1)
    counts=table[hi[:,1],hi[:,0]]-table[lo[:,1],hi[:,0]]-table[hi[:,1],lo[:,0]]+table[lo[:,1],lo[:,0]]
    areas=(hi[:,0]-lo[:,0])*(hi[:,1]-lo[:,1])
    assert np.array_equal(counts,areas), 'A covered footprint was omitted'

def rects_for(a,origin,scale,pad=0):
    y,x=np.nonzero(a); p=np.stack((x,y),axis=1)*scale+origin
    return np.concatenate((p-pad,p+scale+pad),axis=1)

def save(name,a):
    p=OUT/name; Image.fromarray(a.astype(np.uint8)*255,'L').save(p)
    b=np.array(Image.open(p));assert np.array_equal(b,a.astype(np.uint8)*255)
    assert set(np.unique(b)).issubset({0,255})
    return {'texture':'res://'+str(p.relative_to(ROOT)), 'texture_size':[a.shape[1],a.shape[0]], 'sha256':sha(p), 'set_pixel_count':int(a.sum())}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    source=read('data/maps/A13.json'); scope=read('data/earth/a13_hall_source_scope.json')
    assert inputs['data/maps/A13.json']==scope['source_map_sha256']
    assert source['id']=='A13' and source['width']==source['height']==100
    manifest=read(source.get('texture_manifest','res://assets/original/manifest.json'))
    pack=manifest['packs']['Map/Res/Building']
    hall=read('assets/earth/environment/training_hall_v1/registration.json')
    assert inputs['assets/earth/environment/training_hall_v1/registration.json']==HALL_SHA
    assert len(scope['owners'])==len(hall['owners'])==30
    assert {o['frame_index'] for o in scope['owners']}==set(range(3966,3996))
    original_rects=[];new_rects=[];owner_records=[];pages={}
    for o in scope['owners']:
        assert source['cells'][o['stable_source_order']]==o['source_cell']
        assert o['source_cell'][2]==4
        f=pack['frames'][str(o['frame_index'])]; page=pack['pages'][f['page']]
        if page['file'] not in pages:
            pages[page['file']]=alpha(page['file']);assert inputs[page['file'].removeprefix('res://')]==page['sha256']
        x,y,w,h=f['rect'];a=pages[page['file']][y:y+h,x:x+w]
        # world_view.gd lines 115-129: kind 4 uses 32-original.y, NOT frame.offset.
        origin=np.array(o['cell'])*[48,32]+f['crop']+[0,32-f['original'][1]]
        original_rects.append(rects_for(a,origin,1,4))
        owner_records.append({'key':o['key'],'original_world_top_left':origin.tolist(),'original_alpha_pixels':int(a.sum()),'source_offset_not_applied':f['offset']})
    expected={o['key']:o for o in scope['owners']};empty=0
    for o in hall['owners']:
        assert o['key'] in expected and o['source_cell']==expected[o['key']]['source_cell']
        if o['empty']:
            assert o['texture'] is None;empty+=1;continue
        a=alpha(o['texture']);assert inputs[o['texture'].removeprefix('res://')]==o['texture_sha256']
        assert list(a.shape[::-1])==o['texture_size']
        new_rects.append(rects_for(a,o['world_top_left'],o['scale'],4))
    assert empty==2
    size=np.array(SAMPLE[2:])*D;origin=np.array(SAMPLE[:2])
    old=raster(np.concatenate(original_rects),origin,size)
    new=raster(np.concatenate(new_rects),origin,size)
    forbidden=old|new; allowed=~forbidden
    verify_coverage(forbidden,np.concatenate(original_rects+new_rects),origin)
    assert not np.any(allowed & old) and not np.any(allowed & new)
    assert np.all(allowed|forbidden) and not np.any(allowed&forbidden)
    allowed_info=save('allowed.png',allowed); forbidden_info=save('forbidden.png',forbidden)
    track('scripts/world_view.gd');track('scripts/art/hero_alpha_ground_shadow.gd');track('shaders/hero_alpha_ground_shadow.gdshader');track('scripts/art/density_alpha_ground_shadow.gd');track('shaders/density_alpha_ground_shadow.gdshader')
    reference=np.array([40,85.2463]);slope=-.342818;cast=np.array([1.2,.55])
    intercept=reference[1]-slope*reference[0]
    affine=np.array([[1+cast[0]*slope,-cast[0]],[slope*(1+cast[1]),-cast[1]]])
    translation=np.array([cast[0]*intercept,(1+cast[1])*intercept])
    all_rects=[];boots=[];frames=[]
    for group,ids in [('idle',list(range(13,17))),('walk',list(range(51,57)))]:
        m=read(f'assets/earth/hero/se_{group}_v1/manifest.json');assert m['source_ids']==ids and m['texture_density']==4
        atlas=alpha(m['texture']);assert inputs[m['texture'].removeprefix('res://')]==m['texture_sha256']
        registration=read(f'art_source/earth_hero_se_{group}_v1/registration-v1.json')
        assert registration['atlas_sha256']==m['texture_sha256']
        for r in m['records']:
            x,y,w,h=r['region_px'];a=atlas[y:y+h,x:x+w]; yy,xx=np.nonzero(a)
            # Full raw texel footprints plus half-texel linear filtering support.
            lo=np.stack((xx,yy),axis=1)/4-.125; hi=lo+.5
            corners=np.stack([lo,np.stack((hi[:,0],lo[:,1]),1),hi,np.stack((lo[:,0],hi[:,1]),1)],axis=1)
            corners=corners@affine.T+translation
            bounds=np.concatenate((corners.min(1)-1.8,corners.max(1)+1.8),axis=1)
            all_rects.append(bounds);frames.append({'group':group,'source_id':r['source_id'],'alpha_texels':int(a.sum())})
        for r in registration['records']:
            if group=='idle': points=[v for k,v in r['mapped_points'].items() if 'boot' in k]
            else: points=[v['mapped'] for k,v in r['points'].items() if 'boot' in k and v['mapped'] is not None]
            for p in points:boots.append({'group':group,'source_id':r['source_id'],'point':p})
    r=np.concatenate(all_rects)
    # Include visible boot proxies themselves, not a guessed planted/contact state.
    bp=np.array([b['point'] for b in boots]);br=np.concatenate((bp-1.8,bp+1.8),1)
    rr=np.concatenate((r,br)); offset=np.floor(rr[:,:2].min(0)*D)/D
    end=np.ceil(rr[:,2:].max(0)*D)/D; esize=np.rint((end-offset)*D).astype(int)
    projected=raster(r,offset,esize); bootmask=raster(br,offset,esize); envelope=projected|bootmask
    assert np.all(envelope[projected]) and np.all(envelope[bootmask])
    verify_coverage(envelope,rr,offset)
    track('tools/earth/build_flat_shadow_gate.py')
    env_info=save('envelope.png',envelope)
    report={'schema':'earth-se-flat-shadow-gate-v1','status':'bounded conservative candidate; no platform receiver inference',
      'sample_world_rect':SAMPLE,'mask_density':D,'outside_sample_allowed':False,
      'allowed':allowed_info,'forbidden':forbidden_info,'forbidden_dilation_logical':4,
      'forbidden_method':'union of alpha>0 texel footprints of all original and replacement hall owners; square/L-infinity 4 logical pixel expansion; conservative cell-area raster',
      'original_owner_count':30,'replacement_owner_count':30,'replacement_nonempty_count':28,
      'envelope':dict(env_info,offset_logical=offset.tolist(),size_logical=(end-offset).tolist(),density=D),
      'actor_body_frame_origin':'actor_cell * (48,32) + (-16,-64)',
      'actor_body_offset_logical':[-16,-64],'actor_cell_size_logical':[48,32],
      'projection':{'reference_logical':reference.tolist(),'slope':slope,'cast':cast.tolist(),'matrix_rows':affine.tolist(),'translation_logical':translation.tolist(),'blur_logical':.8,'helper_padding_logical':1,'linear_support_half_texel_logical':.125},
      'envelope_method':'union of projected per-texel AABBs with bilinear support plus 1.8 logical pixel square expansion; common across all 10 frames, union visible boot proxies with same padding',
      'runtime_gate':'Entire translated envelope must be inside allowed mask. Any out-of-bounds, intersected forbidden raster cell, invalid input or unsupported hero frame disables whole shadow. Use area overlap, never center-only sampling.',
      'boot_proxies':boots,'hidden_boot_policy':'walk52 B_boot has no visible mapped proxy; never infer a contact','boot_added_pixel_count':int((bootmask & ~projected).sum()),'frames':frames,'original_owners':owner_records,
      'verification':{'binary_lossless_roundtrip':True,'all_source_texel_and_envelope_AABBs_covered':True,'full_sample_partition':True,'forbidden_pixels_admitted':0,'original_forbidden_pixel_count':int(old.sum()),'replacement_forbidden_pixel_count':int(new.sum()),'sample_pixel_count':int(allowed.size)},
      'input_sha256':dict(sorted(inputs.items())),
      'runtime_input_sha256':{k:v for k,v in sorted(inputs.items()) if k.startswith(('assets/','data/','scripts/','shaders/'))},
      'runtime_dependencies':[allowed_info['texture'],forbidden_info['texture'],env_info['texture']]}
    p=OUT/'manifest.json';p.write_text(json.dumps(report,indent=2)+'\n')
    hashes={q.name:sha(q) for q in sorted(OUT.iterdir()) if q.name in ['allowed.png','forbidden.png','envelope.png','manifest.json']}
    (OUT/'SHA256SUMS.json').write_text(json.dumps(hashes,indent=2)+'\n')
    print(json.dumps({'outputs':hashes,'envelope':report['envelope'],'verification':report['verification'],'allowed_pixels':int(allowed.sum()),'boot_added_pixels':report['boot_added_pixel_count']},indent=2))
if __name__=='__main__':main()
