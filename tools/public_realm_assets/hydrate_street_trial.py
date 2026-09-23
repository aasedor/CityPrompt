"""Hydrate the ten accepted streets into the local DEV review layer.

Source GLBs stay external/ignored. Registry rows contain exact hashes and
surface ownership; no student catalogue IDs or published picker entries change.
"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--public-root', type=Path, required=True)
    parser.add_argument('--registry', type=Path, required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    data = json.loads(args.manifest.read_text(encoding='utf-8'))
    assert len(data['candidates']) == 10
    registry = json.loads(args.registry.read_text(encoding='utf-8'))
    ids = {entry['id'] for entry in registry}
    rows = []
    for candidate in data['candidates']:
        assert candidate['id'] not in ids, f"Registry already includes {candidate['id']}"
        assert candidate['verification']['status'] == 'PASS_OFFLINE_GEOMETRY'
        root = Path(candidate['package'])
        recipe = json.loads((root / 'recipe.json').read_text(encoding='utf-8'))
        assert recipe['id'] == candidate['id'] and recipe['runtime_approved'] is False
        # Native junctions inherit the authored long-section finish. Requiring
        # this at hydration keeps future street batches in the shared crossing
        # contract rather than silently falling back to a blank paving square.
        finish = recipe.get('junction_surface') or {
            'deck': 'timber', 'cobble': 'cobble', 'brick': 'brick', 'stone': 'pavers'
        }.get(recipe.get('pattern'))
        assert finish in {'pavers', 'brick', 'cobble', 'timber'}, f"Register junction finish for {candidate['id']}"
        assembly = recipe['assembly']
        source = root / assembly['path']
        content = source.read_bytes()
        assert len(content) == assembly['bytes']
        assert hashlib.sha256(content).hexdigest() == assembly['sha256']
        filename = f"{recipe['id']}-{assembly['sha256'][:8]}.glb"
        relative = Path('public-realm-trials/ten-streets-2026-09-23') / filename
        target = args.public_root / relative
        assert not target.exists(), f'Preserve existing local asset: {target}'
        row = dict(
            id=recipe['id'], title=recipe['title'], kind='street',
            dimensions=recipe['dimensions_m'], sha256=assembly['sha256'],
            junctionSurface=finish,
            surfaceRegions=recipe['surface_regions'],
            url='/' + relative.as_posix(), treeWells=recipe['tree_wells'],
        )
        rows.append((source, target, row))
    if args.dry_run:
        print('DRY_RUN_PASS', len(rows))
        return
    for source, target, _ in rows:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    args.registry.write_text(json.dumps(registry + [row for _, _, row in rows], indent=2) + '\n', encoding='utf-8')
    print('HYDRATED', len(rows), str(args.public_root))


if __name__ == '__main__':
    main()
