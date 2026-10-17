#!/usr/bin/env python3
"""Read two pinned rasters; write numerical analysis only. Never saves an image."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import label


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def bbox(mask):
    yy, xx = np.where(mask)
    return [int(xx.min()), int(yy.min()), int(xx.max()+1), int(yy.max()+1)]


def lower(mask, roi, seed=None):
    x0, y0, x1, y1 = roi
    crop = mask[y0:y1, x0:x1]
    if seed is not None:
        labels, _ = label(crop)
        component = labels[seed[1]-y0, seed[0]-x0]
        assert component != 0
        crop = labels == component
    yy, xx = np.where(crop)
    yy, xx = yy+y0, xx+x0
    y = int(yy.max())
    xs = xx[yy == y]
    return {"row_center": [float((xs.min()+xs.max())/2), y],
            "bottom_edge_center": [float((xs.min()+xs.max())/2), y+1],
            "bottom_row_x_extent_half_open": [int(xs.min()), int(xs.max()+1)],
            "roi": roi, "seed": seed}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source125', type=Path, required=True)
    ap.add_argument('--v2', type=Path, required=True)
    ap.add_argument('--contract', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    annotations_path = Path(__file__).resolve().parent.parent/'surface-proxy-annotations.json'
    annotations = json.loads(annotations_path.read_text())
    contract = json.loads(args.contract.read_text())
    pins = {str(args.source125): '701aab9ce8fda25b0dd10b479a5f8f2553552687a3b4a9b9f68e635056343aa0',
            str(args.v2): '2c4095424ab187ed601448347ecc33920928e97c6cdbe1e5931a50193f40eedf'}
    for p, expected in pins.items():
        assert digest(Path(p)) == expected, f'Input hash mismatch: {p}'
    source = np.array(Image.open(args.source125).convert('RGBA'))
    candidate = np.array(Image.open(args.v2).convert('RGBA'))
    smask = (source[:, :, 3] > 0) & np.any(source[:, :, :3] != [16, 8, 8], axis=2)
    assert bbox(smask) == [0, 0, 49, 67]
    assert contract['frames'][0]['source_id'] == 125
    assert contract['frames'][0]['body_palette_proxy_bbox_local'] == bbox(smask)
    rois = annotations['machine_roi_definitions']
    source_points = {}
    for side in ['left', 'right']:
        d = rois['source_hand_'+side]
        source_points['hand_'+side] = lower(smask, d['roi'], d['seed'])
    for side, roi in [('left', [11, 63, 23, 70]), ('right', [28, 63, 39, 70])]:
        source_points['shoe_'+side] = lower(smask, roi)
    source_crown_x = float(np.where(smask[0])[0].mean())
    source_mid_x = sum(source_points['shoe_'+s]['row_center'][0] for s in ['left', 'right'])/2

    runs = []
    for threshold in rois['v2_threshold_sensitivity']:
        mask = candidate[:, :, 3] > threshold
        bb = bbox(mask)
        points = {}
        for side in ['left', 'right']:
            d = rois['v2_hand_'+side]
            points['hand_'+side] = lower(mask, d['roi'], d['seed'])
            d = rois['v2_shoe_'+side]
            points['shoe_'+side] = lower(mask, d['roi'])
        height = bb[3]-bb[1]
        scale = 67/height
        mid_x = sum(points['shoe_'+s]['row_center'][0] for s in ['left', 'right'])/2
        tx, ty = source_mid_x-scale*mid_x, -scale*bb[1]
        transform = lambda p: [scale*p[0]+tx, scale*p[1]+ty]
        transformed = {}
        for key, p in points.items():
            transformed[key] = {}
            for convention in ['row_center', 'bottom_edge_center']:
                registered = transform(p[convention])
                expected = source_points[key][convention]
                transformed[key][convention] = {
                    'v2_raw': p[convention], 'source125': expected,
                    'registered_v2': registered,
                    'residual_v2_minus_source125': list(np.subtract(registered, expected)),
                    'v2_y_fraction_of_body_height': (p[convention][1]-bb[1])/height,
                    'source125_y_fraction_of_body_height': expected[1]/67}
        crown_x = float(np.where(mask[bb[1]])[0].mean())
        crown_registered = transform([crown_x, bb[1]])
        runs.append({'alpha_gt': threshold, 'candidate_bbox': bb, 'candidate_height': height,
                     'uniform_scale': scale, 'translation': [tx, ty],
                     'candidate_lower_surface_points': points,
                     'registered_proxies': transformed,
                     'crown_top': {'source125': [source_crown_x, 0], 'v2_raw': [crown_x, bb[1]],
                                   'registered_v2': crown_registered,
                                   'residual': [crown_registered[0]-source_crown_x, crown_registered[1]]},
                     'body_width_over_height': (bb[2]-bb[0])/height,
                     'registered_body_width': (bb[2]-bb[0])*scale})
    fixed = next(r for r in runs if r['alpha_gt'] == 128)
    s = fixed['uniform_scale']
    tx, ty = fixed['translation']
    transform = lambda p: [s*p[0]+tx, s*p[1]+ty]
    manual = []
    for p in annotations['manual_points']:
        item = dict(p)
        item['registered_v2'] = transform(p['v2'])
        item['residual_v2_minus_source125'] = list(np.subtract(item['registered_v2'], p['source']))
        vi, si = p['v2_interval'], p['source_interval']
        item['residual_interval'] = [[s*vi[i][0]+[tx,ty][i]-si[i][1],
                                      s*vi[i][1]+[tx,ty][i]-si[i][0]] for i in range(2)]
        item['source_y_fraction_interval'] = [n/67 for n in si[1]]
        item['registered_v2_y_fraction_interval'] = [(s*n+ty)/67 for n in vi[1]]
        manual.append(item)
    envelope, hem = annotations['manual_ranges']
    cb = envelope['v2_nominal_bbox']
    sb = envelope['source_nominal_bbox']
    envelope = dict(envelope)
    envelope['registered_v2_size'] = [s*(cb[2]-cb[0]), s*(cb[3]-cb[1])]
    envelope['source125_size'] = [sb[2]-sb[0], sb[3]-sb[1]]
    envelope['nominal_v2_over_source_size_ratio'] = [envelope['registered_v2_size'][i]/envelope['source125_size'][i] for i in range(2)]
    envelope['size_ratio_intervals'] = [[s*envelope['v2_'+d+'_interval'][0]/envelope['source_'+d+'_interval'][1],
                                          s*envelope['v2_'+d+'_interval'][1]/envelope['source_'+d+'_interval'][0]]
                                         for d in ['width', 'height']]
    hem = dict(hem)
    hem['registered_v2_y'] = s*hem['v2_nominal_y']+ty
    hem['residual_y'] = hem['registered_v2_y']-hem['source_nominal_y']
    hem['residual_y_interval'] = [s*hem['v2_y_interval'][0]+ty-hem['source_y_interval'][1],
                                  s*hem['v2_y_interval'][1]+ty-hem['source_y_interval'][0]]
    hand_span = (fixed['candidate_lower_surface_points']['hand_right']['row_center'][0]-fixed['candidate_lower_surface_points']['hand_left']['row_center'][0])*s
    shoe_span = (fixed['candidate_lower_surface_points']['shoe_right']['row_center'][0]-fixed['candidate_lower_surface_points']['shoe_left']['row_center'][0])*s
    data = {
        'schema': 'chief-pose-analysis-v1',
        'status': 'ANALYSIS_ONLY; v1 and v2 NOT_ACCEPTED; no animation/art acceptance',
        'source_inputs': [{'path': p, 'sha256': h} for p,h in pins.items()]+[{'path': str(args.contract), 'sha256': digest(args.contract)}],
        'actual_visual_inspection': ['untouched source125', 'existing source125-128 registered 5x contact sheet', 'untouched v2 raw'],
        'registration': {
            'method': 'ONE isotropic whole-figure scale, crown/top boundary to y0 and lowest shoe/body bottom boundary to y67; horizontal translation aligns the midpoint of both lowest shoe-material row centers to source125 x24.5. No rotation, shear, per-part transform, image resampling, or image output.',
            'formula': 'p_source_local = uniform_scale * p_v2_raw + translation',
            'primary_alpha_gt': 128, 'uniform_scale': s, 'translation': [tx, ty],
            'source_frame_offset': [-1,-47], 'source_world_cell_origin':[3600,1728],
            'to_world_relative': 'registered source-local + (-1,-47)',
            'normalization': 'Source body-palette proxy H=67, excluding contract shadow RGB(16,8,8). V2 alpha>128 H=1147; alpha0 haze is not a body extent.',
            'coordinate_caution': 'Lowest occupied pixel row and its lower boundary differ by one pixel. Contract row-index convention gives source hand36/67=53.73%; continuous lower-edge convention gives37/67=55.22%. Never subtract quantities with mixed conventions.'},
        'source125_machine_proxies': source_points,
        'primary_registration': fixed,
        'alpha_threshold_sensitivity': runs,
        'manual_surface_proxies': manual,
        'manual_surface_ranges': [envelope,hem],
        'ratios': {'source125_body_width_over_height':49/67, 'v2_body_width_over_height':fixed['body_width_over_height'],
                   'source125_hand_lowest_row_center_span':46, 'registered_v2_hand_lowest_row_center_span':hand_span,
                   'v2_over_source_hand_span_ratio':hand_span/46,
                   'source125_shoe_lowest_row_center_span':17, 'registered_v2_shoe_lowest_row_center_span':shoe_span,
                   'v2_over_source_shoe_span_ratio':shoe_span/17},
        'interpretation': {
            'robust_failure': 'Hands are much too low and too close to the center. Lowest-row vertical residuals are approximately+10.8 logical pixels; true bottom-edge residuals approximately+9.8. Registered hand span is~19.5% narrower than source125.',
            'lower_confidence_findings': 'Elbow-region sleeve folds tend lower; shoulder-top ridge tends wider. Neither is a recovered skeleton joint. Crown/hair envelope is nominally~9% wider and~29% taller; interval uncertainty means this is not a precise whole-head resize instruction.',
            'relative_strengths_to_preserve': 'Matte woven brown-gray long work coat, closed stand collar and central zipper, restrained light work panels, near-shoe hem, small shoe tips and nearly level shoe-bottom material.',
            'projection': 'Redraw high-angle compact projection and relaxed arms using source125 as geometry reference; do not infer a numerical 3D camera angle, pose joints, toe anatomy or support-foot identity from these pixels.'},
        'not_performed': ['image generation','image edits','image warp','Godot','main-repository writes','Git commands or publication'],
        'next_step': 'A new single base may be generated only by the separately authorized owner. Reassess the new raw under the same whole-figure registration; no animation/art acceptance follows from these measurements.'
    }
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out/'pose-analysis.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'scale': s, 'translation':[tx,ty], 'hand_span':hand_span,'shoe_span':shoe_span,
                      'hand_left':fixed['registered_proxies']['hand_left'],
                      'hand_right':fixed['registered_proxies']['hand_right'],
                      'head_envelope':envelope,'hem':hem},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
