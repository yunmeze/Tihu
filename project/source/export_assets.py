"""Export the saved authored source and install a validated vertex-AO GLB.

Run with ordinary Python, not inside Blender. Requires Blender on PATH.
No new visible geometry is generated; evaluated modifier results are exported.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--blender', default='blender', help='Blender executable')
    parser.add_argument('--samples', type=int, default=32)
    args = parser.parse_args()
    if args.samples < 1:
        parser.error('--samples must be positive')
    root = Path(__file__).resolve().parents[1]
    source = root / 'source' / 'pelican_coast.blend'
    asset = root / 'assets' / 'coastal_ride.glb'
    if not source.is_file():
        parser.error(f'Missing saved source: {source}')
    with tempfile.TemporaryDirectory(prefix='pelican-ao-export-') as staging:
        candidate = Path(staging) / 'coastal_ride.glb'
        subprocess.run([args.blender, '--background', str(source), '--python-exit-code', '1',
                        '--python', str(root / 'source' / 'materials_export.py'), '--',
                        '--output', str(Path(staging) / 'unbaked.glb')], check=True)
        subprocess.run([args.blender, '--background', str(source), '--python-exit-code', '1',
                        '--python', str(root / 'source' / 'bake_vertex_ao.py'), '--',
                        '--output', str(candidate), '--samples', str(args.samples),
                        '--radius', '0.15'], check=True)
        report = json.loads(candidate.with_suffix('.validation.json').read_text())
        required = ('passed', 'source_file_unchanged', 'source_filename_unchanged',
                    'glb_non_color_data_identical')
        if not all(report.get(key) is True for key in required):
            raise RuntimeError('AO validation did not pass; production candidate was not installed.')
        card = Path(staging) / 'foliage_card.glb'
        subprocess.run([args.blender, '--background', str(source), '--python-exit-code', '1',
                        '--python', str(root / 'source' / 'export_foliage_card.py'), '--',
                        '--output', str(card)], check=True)
        card_replacement = (asset.parent / 'foliage_card.glb.pending')
        shutil.copy2(card, card_replacement)
        card_replacement.replace(asset.parent / 'foliage_card.glb')
        replacement = asset.with_suffix('.glb.pending')
        shutil.copy2(candidate, replacement)
        replacement.replace(asset)
    print(f'Installed validated authored GLB: {asset} ({asset.stat().st_size:,} bytes)')


if __name__ == '__main__':
    main()
