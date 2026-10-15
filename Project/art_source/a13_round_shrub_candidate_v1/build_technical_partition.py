"""Lossless, common-transform four-owner partition. No raw image editing or runtime changes."""
from pathlib import Path
import hashlib
import json
import numpy as np
import scipy
from scipy.ndimage import distance_transform_edt
from PIL import Image, ImageDraw, ImageFont

P = Path(__file__).resolve().parents[2]
D = Path(__file__).resolve().parent
S = P / 'art_source/a13_round_shrub_source'
O = D / 'technical_v1'
Q = P / 'diagnostics/art_source/a13-round-shrub'
O.mkdir(exist_ok=True)
Q.mkdir(parents=True, exist_ok=True)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def box(mask):
    yy, xx = np.where(mask)
    return [int(xx.min()), int(yy.min()), int(xx.max() + 1), int(yy.max() + 1)]

def resource(path):
    return 'res://' + str(path.relative_to(P))

raw_path = D / 'raw.png'
raw_hash = 'b093644c662a8d42f8beee8160b4fe2b4c200257bfb7d3ac5589683069f8b469'
assert sha(raw_path) == raw_hash
contract_path = S / 'source-group-contract.json'
source = json.loads(contract_path.read_text())
group = next(g for g in source['groups'] if g['center_owner_cell'] == [57, 38])
geometry = json.loads((D / 'geometry-diagnostic.json').read_text())
scale = geometry['common_transform']['scale']
translation = np.array(geometry['common_transform']['translation_to_source_composite'])
assert scale == 0.09442870632672333
assert np.array_equal(translation, [-4.022662889518415, -4.15486307837584])
world_origin = np.array(source['selected_composite']['world_origin']) + translation
raw_image = Image.open(raw_path).convert('RGBA')
raw = np.asarray(raw_image)
h, w = raw.shape[:2]
stored = np.any(raw != 0, axis=2)
visible = raw[:, :, 3] > 0

# Populate ORIGINAL owner provenance from spatial alpha only, no RGB classification.
# Padding includes every candidate texel-center mapped to the source pixel grid.
grid_min = np.floor(translation).astype(int)
grid_max = np.ceil(translation + np.array([w, h]) * scale).astype(int)
grid_min = np.minimum(grid_min, [0, 0])
grid_max = np.maximum(grid_max, [124, 105])
gw, gh = grid_max - grid_min
labels = np.zeros((gh, gw), dtype=np.uint8)
source_overlap = 0
for index, owner in enumerate(group['owners_in_draw_order'], 1):
    frame = next(f for f in source['frames'] if f['id'] == owner['frame_id'])
    path = S / frame['extracted_full_canvas']
    assert sha(path) == frame['png_sha256']
    image = np.asarray(Image.open(path).convert('RGBA'))
    cx, cy = owner['crop']
    wx, wy, ww, hh = owner['world_rect']
    ox, oy = np.array([wx, wy]) - source['selected_composite']['world_origin'] - grid_min
    mask = image[cy:cy + hh, cx:cx + ww, 3] > 0
    target = labels[oy:oy + hh, ox:ox + ww]
    source_overlap += int(np.count_nonzero((target > 0) & mask))
    target[mask] = index
assert source_overlap == 0
# Deterministic pixel-grid nearest-provenance extrapolation into source gaps.
# This assigns draw ownership only; it does not create a physical depth model.
_, indices = distance_transform_edt(labels == 0, return_indices=True)
filled = labels[indices[0], indices[1]]
x = np.floor(translation[0] + (np.arange(w) + .5) * scale).astype(int) - grid_min[0]
y = np.floor(translation[1] + (np.arange(h) + .5) * scale).astype(int) - grid_min[1]
assignment = filled[y[:, None], x[None, :]]
direct = labels[y[:, None], x[None, :]] > 0
assert np.all((assignment >= 1) & (assignment <= 4))
# Palette-independent uint8 owner labels are retained as an auditable derivation.
Image.fromarray(assignment, 'L').save(O / 'owner-index.png')

owners, pieces = [], []
reassembled = np.zeros_like(raw)
coverage = np.zeros((h, w), dtype=np.uint8)
for index, src_owner in enumerate(group['owners_in_draw_order'], 1):
    selected = assignment == index
    support = selected & stored
    support_box = box(support)
    # Full-canvas owner textures share identical UV origin/extent. This avoids
    # independent crop rounding at exact nearest-texel boundaries.
    x0, y0, x1, y1 = 0, 0, w, h
    piece = np.where(selected[y0:y1, x0:x1, None], raw[y0:y1, x0:x1], 0).astype(np.uint8)
    filename = f"owner-{src_owner['frame_id']}.png"
    Image.fromarray(piece, 'RGBA').save(O / filename)
    readback = np.asarray(Image.open(O / filename).convert('RGBA'))
    assert np.array_equal(piece, readback)
    active = np.any(readback != 0, axis=2)
    coverage[y0:y1, x0:x1] += active
    reassembled[y0:y1, x0:x1] += readback
    p0 = world_origin + np.array([x0, y0]) * scale
    owners.append({
        'key': src_owner['key'], 'frame_id': src_owner['frame_id'],
        'cell': src_owner['cell'], 'source_cell': src_owner['source_cell'],
        'flag': src_owner['flag'], 'layer': src_owner['layer'],
        'sort_y': src_owner['sort_y'], 'stable_source_order': src_owner['stable_source_order'],
        'sort_tuple': src_owner['sort_tuple'],
        'texture': resource(O / filename), 'texture_sha256': sha(O / filename),
        'raw_rect_xywh': [x0, y0, x1-x0, y1-y0],
        'stored_support_bbox_xyxy': support_box,
        'world_rect_xywh': [*p0.tolist(), (x1-x0)*scale, (y1-y0)*scale],
        'world_origin': p0.tolist(), 'scale': scale,
        'stored_rgba_pixels': int(support.sum()), 'nonzero_alpha_pixels': int((selected & visible).sum()),
        'direct_source_provenance_alpha_pixels': int((selected & visible & direct).sum()),
        'extrapolated_source_provenance_alpha_pixels': int((selected & visible & ~direct).sum()),
        'alpha96_raw_bbox_xyxy': box(selected & (raw[:, :, 3] >= 96)),
    })
    pieces.append((readback, x0, y0))
assert np.array_equal(reassembled, raw)
assert np.all(coverage[stored] == 1) and np.all(coverage[~stored] == 0)

# Independent screen-center nearest sampling of each full-canvas owner vs raw. Exercise
# native pixels, fractional camera offsets and clipped viewport-edge rectangles.
def sample(image, origin, size):
    yy, xx = np.indices((size[1], size[0]))
    u = np.floor((xx + .5 - origin[0]) / scale).astype(int)
    v = np.floor((yy + .5 - origin[1]) / scale).astype(int)
    good = (u >= 0) & (u < image.shape[1]) & (v >= 0) & (v < image.shape[0])
    result = np.zeros((*good.shape, 4), dtype=np.uint8)
    result[good] = image[v[good], u[good]]
    return result

sampling_cases = []
for ox in [8.0, 8.25, 8.5, 8.75, -40.0]:
    for oy in [8.0, 8.28, 8.5, 8.72, -70.0]:
        origin = translation + [ox, oy]
        whole = sample(raw, origin, (140, 121))
        joined = np.zeros_like(whole, dtype=np.uint16)
        for piece, px, py in pieces:
            joined += sample(piece, origin + np.array([px, py])*scale, (140, 121))
        difference = int(np.count_nonzero(np.any(joined != whole, axis=2)))
        assert difference == 0
        sampling_cases.append({'source_canvas_offset': [ox, oy], 'different_rgba_pixels': difference})

registration = {
    'schema': 'a13-round-shrub-four-owner-registration-v1',
    'status': 'whole/native art accepted as working candidate; technical CPU parity passed; native GPU/depth pending',
    'source_contract': resource(contract_path), 'source_contract_sha256': sha(contract_path),
    'selected_group_center': [57, 38],
    'whole_shrub_registration': {
        'texture': resource(raw_path), 'sha256': raw_hash, 'size': [w, h],
        'scale': scale, 'translation_to_source_composite': translation.tolist(),
        'source_composite_world_origin': source['selected_composite']['world_origin'],
        'world_origin': world_origin.tolist(), 'rotation': 0, 'shear': 0,
        'actual_woody_root': None, 'ground_reference': None,
        'alignment_meaning': 'visible foliage envelope, not a physical root/contact or receiver plane',
    },
    'suppress_source_keys': [o['key'] for o in owners],
    'owners': owners,
    'partition_method': {
        'rule': 'source-alpha owner provenance; raw texel center mapped to source integer grid; nearest nonzero original owner fills gaps by scipy.ndimage.distance_transform_edt',
        'owner_index_texture': resource(O / 'owner-index.png'), 'owner_index_sha256': sha(O / 'owner-index.png'),
        'owner_index_values': {str(i): o['key'] for i, o in enumerate(owners, 1)},
        'source_grid_bounds_xyxy': [*grid_min.tolist(), *grid_max.tolist()],
        'source_alpha_owner_overlap_pixels': source_overlap,
        'source_gap_extrapolation_is_draw_ownership_only': True,
        'scipy_version': scipy.__version__,
        'source_color_filtering': False,
        'all_raw_rgba_preserved_including_invisible_rgb': True,
    },
    'sampling': {'body_filter': 'nearest', 'mipmaps': False, 'independent_linear_cutouts_accepted': False,
                 'shared_canvas_required': True,
                 'shared_canvas_reason': 'All four owner textures keep the exact full-raw size and origin to avoid independent cropped-quad rounding at nearest-texel ties.',
                 'rgba8_gpu_bytes_four_textures_without_mipmaps': int(raw.size*4),
                 'gpu_requirement': 'whole vs four-owner exact same-phase native render parity before promotion'},
    'validation': {'raw_rgba_byte_exact_reassembly': True, 'nonzero_alpha_pixels': int(visible.sum()),
                   'stored_rgba_pixels': int(stored.sum()), 'coverage_min_stored': int(coverage[stored].min()),
                   'coverage_max_stored': int(coverage[stored].max()),
                   'native_nearest_cpu_cases': len(sampling_cases), 'native_nearest_cpu_differing_pixels': 0,
                   'gpu_parity': 'pending', 'runtime_depth': 'pending'},
    'activation_contract': {
        'authorized_instance_only': [57, 38], 'automatically_replace_other_seven_groups': False,
        'atomic_group': 'Use all four new bodies and suppress all four original owners together; invalid resource restores all four source owners.',
        'sorting': 'Preserve original layer/sort_y/stable_source_order. Do not merge body into one sorted object.',
        'shadow': 'No new cast in this stage. Source checker disappears only with atomic suppression of the four entire source bodies.',
        'default_entry': 'unchanged; isolated review only',
    },
    'first_screen_context': source['first_screen'],
    'limits': ['Actual woody root remains unknown/null.',
               'Nearest source ownership in changed crown gaps is a technical approximation, not verified botanical depth.',
               'Four full-canvas RGBA8 textures use 25,166,432 uncompressed bytes before runtime overhead; do not silently crop them or enable linear filtering.',
               'White opaque points and alpha1..15 green fringe are retained from approved raw.',
               'No shadow/receiver or actor front/back acceptance follows from byte-exact reassembly.',
               'Other seven instances are not automatically approved; inspect original remaining first-screen shrubs as context.'],
}
(O / 'registration.json').write_text(json.dumps(registration, indent=2) + '\n')
report = {'status': 'PASS', 'raw_sha256': sha(raw_path), 'registration_sha256': sha(O / 'registration.json'),
          'rgba_bytes_compared': int(raw.size), 'raw_rgba_different_bytes': int(np.count_nonzero(raw != reassembled)),
          'stored_overlap_or_loss_pixels': int(np.count_nonzero(coverage[stored] != 1)),
          'source_sort_tuples_preserved': [o['sort_tuple'] for o in owners], 'native_cpu_sampling_cases': sampling_cases,
          'note': 'No GUI or GPU test. Not a physical root/shadow/depth proof.'}
(Q / 'technical-headless-report.json').write_text(json.dumps(report, indent=2) + '\n')

# Diagnostic board: exact raw/assembled images and ownership visualization.
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 17)
board = Image.new('RGB', (1120, 640), (232, 236, 239))
draw = ImageDraw.Draw(board)
draw.text((16, 12), 'Round shrub: approved raw / lossless four-owner assembly / draw-ownership labels', fill=(20,25,30), font=font)
palette = np.array([[0,0,0], [233,157,54], [69,160,209], [193,89,149], [90,175,100]], dtype=np.uint8)
owner_rgba = np.concatenate((palette[assignment], raw[:, :, 3, None]), axis=2)
for index, array in enumerate([raw, reassembled, owner_rgba]):
    layer = Image.fromarray(array, 'RGBA').resize((352, 298), Image.Resampling.NEAREST)
    bg = Image.new('RGBA', layer.size, (81,98,83,255)); bg.alpha_composite(layer)
    board.paste(bg.convert('RGB'), (16 + index*368, 46))
for index, owner in enumerate(owners):
    piece, px, py = pieces[index]
    out = sample(piece, translation + [8,8] + np.array([px,py])*scale, (140,121))
    bg = Image.new('RGBA', (140,121), (81,98,83,255)); bg.alpha_composite(Image.fromarray(out,'RGBA'))
    bx = 16 + index*272
    board.paste(bg.resize((252,218),Image.Resampling.NEAREST).convert('RGB'),(bx,389))
    draw.text((bx,357), f"{owner['frame_id']} sort {owner['sort_y']} / {owner['stable_source_order']}",fill=(20,25,30),font=font)
draw.text((16,614),'All RGBA preserved once. Root unknown. Whole/cutout GPU parity and actor depth still required.',fill=(20,25,30),font=font)
board.save(Q/'technical-partition-board.png')
print('SHRUB_TECHNICAL_PASS', json.dumps({'raw_rgba_bytes': int(raw.size), 'stored_pixels':int(stored.sum()),'cpu_sampling_cases':len(sampling_cases),'owners':len(owners),'raw_sha256':sha(raw_path)}))
