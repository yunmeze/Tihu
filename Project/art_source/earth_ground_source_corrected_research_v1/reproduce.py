"""Reproduce the frozen research patch; write only to a caller-selected output path."""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
from PIL import Image
O = Path(__file__).resolve().parent
D = O.parent

def rgba(path):
    return np.array(Image.open(path).convert('RGBA'))
def mask(path):
    return np.array(Image.open(path).convert('L')) > 0

def reproduce(output):
    provenance = json.loads((O / 'provenance.json').read_text())
    for rel, digest in provenance['reproduction_inputs_sha256'].items():
        assert hashlib.sha256((D / rel).read_bytes()).hexdigest() == digest, rel
    M = D / 'earth_ground_material_layers_plan_v1'
    V = D / 'earth_ground_cross_seam_revision_plan_v3'
    C = rgba(D / 'earth_ground_concrete_material_c_v1/raw.png')
    G = rgba(D / 'earth_grass_two_segment_composite_v1/03_outer_8raw.png')
    base = rgba(D / 'earth_ground_concrete_material_c_v1/RESEARCH_G_frozen_plus_C.png')
    fixed = mask(V / 'PROPOSED_fixed_replace_mask.png')
    old = mask(M / 'DOMAIN_curb_BINARY.png')
    poly = json.loads((V / 'PLAN.json').read_text())['source_center_polyline_localraw']
    y, x = np.indices(fixed.shape, dtype=float)
    x += .5
    y += .5
    u = np.clip((y - 72) / 28, 0, 1)
    h = 1 - u * u * (3 - 2 * u)
    dx = 4.5 * h
    dw = -3 * h
    d = np.full(x.shape, np.inf)
    for aa, bb in zip(poly, poly[1:]):
        vx, vy = bb[0] - aa[0], bb[1] - aa[1]
        t = np.clip(((x-dx-aa[0])*vx + (y-aa[1])*vy)/(vx*vx+vy*vy), 0, 1)
        d = np.minimum(d, np.hypot(x-dx-aa[0]-t*vx, y-aa[1]-t*vy))
    width = np.where(y < 100, 18 - 10*u, 8) + dw
    new = np.where((y >= 72) & (y < 100), fixed & (d <= width / 2), old)
    add, remove = new & ~old, old & ~new
    assert add.sum() == 42 and remove.sum() == 84
    geo = base.copy()
    geo[remove] = G[remove]
    iy, ix = np.where(add)
    geo[iy, ix] = C[iy-64, ix]
    seam, lip, grass = [mask(O / (n + '_support.png')) for n in ('seam', 'lip', 'grass_contact')]
    union = seam | lip | grass
    assert union.sum() == 7617 and not (union & ~fixed).any()
    assert not ((seam.astype(int) + lip.astype(int) + grass.astype(int)) > 1).any()
    donor = geo.copy()
    iy, ix = np.where(seam | lip)
    donor[iy, ix] = C[iy-64, ix]
    donor[grass] = G[grass]
    cfg = json.loads((O / 'FROZEN_PARAMETERS_UNCHANGED.json').read_text())
    v = donor[:, :, :3] / 255.
    linear = np.where(v <= .04045, v/12.92, ((v+.055)/1.055)**2.4)
    result_linear = linear.copy()
    result_linear[seam] *= cfg['deep_seam']['k']
    result_linear[grass] *= cfg['grass_contact']['k']
    alpha = cfg['lip']['alpha']
    result_linear[lip] = (1-alpha)*linear[lip] + alpha
    assert result_linear.min() >= 0 and result_linear.max() <= 1
    encoded = np.where(result_linear <= .0031308, result_linear*12.92, 1.055*result_linear**(1/2.4)-.055)
    result = geo.copy()
    result[:, :, :3][union] = np.floor(255*encoded[union]+.5).astype(np.uint8)
    reference = rgba(O / '03_source_corrected_contact.png')
    assert np.array_equal(result, reference), 'Frozen patch pixel mismatch'
    assert not np.any((result != base)[~fixed]) and (result[:, :, 3] == 255).all()
    output = Path(output).resolve()
    assert not output.exists(), 'Refusing to overwrite an existing file'
    output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(result).save(output)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    print(json.dumps({'RGBA_different_pixels': 0, 'sha256': digest, 'byte_identical': digest == provenance['patch_sha256']}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    reproduce(parser.parse_args().output)
