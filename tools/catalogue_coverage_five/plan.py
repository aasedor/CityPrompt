"""Original-design reference locks; generated pixels, never invented source claims."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DESIGNS = json.loads((HERE / 'designs.json').read_text(encoding='utf-8'))
SPECS = {s['kind']: s for s in DESIGNS['candidates']}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_entry(kind, source_root):
    spec = SPECS[kind]
    root = Path(source_root).resolve() / 'frontend/public/archetypes/buildings' / spec['slug']
    provenance = json.loads((root / 'generation-provenance.json').read_text(encoding='utf-8'))
    assert provenance['origin'] == 'original_generated_design'
    records = provenance['records']
    if {s['role'] for s in records} != {'front', 'oblique', 'top'}:
        raise ValueError('Three compatible original reference roles are required')
    entry = dict(archetype_id=spec['id'], variant_id=spec['variant'],
                 source_origin='original_generated_design', _reference_root=str(root), sources=[])
    for s in records:
        p = root / s['file']
        raw = p.read_bytes()
        if raw.startswith(b'version https://git-lfs.github.com/spec/v1'):
            raise ValueError('Unhydrated image: ' + str(p))
        if len(raw) != s['bytes'] or digest(p) != s['sha256']:
            raise ValueError('Generated reference changed: ' + str(p))
        try:
            from PIL import Image
        except ModuleNotFoundError:
            import bpy
            im = bpy.data.images.load(str(p), check_existing=False)
            size = list(im.size)
            bpy.data.images.remove(im)
        else:
            with Image.open(p) as im:
                size = list(im.size)
                im.verify()
        if size != s['dimensions_px'] or min(size) < 512:
            raise ValueError('Invalid reference resolution: ' + str(p))
        entry['sources'].append(dict(archetype_id=spec['id'], variant_id=spec['variant'],
            role=s['role'], original_path=str(p), path='sources/' + p.name,
            bytes=len(raw), sha256=s['sha256'], dimensions_px=size))
    enrolled = {Path(s['original_path']).name for s in entry['sources']}
    extras = [p.name for p in root.glob('variant_0*') if p.suffix.lower() in ('.png', '.jpg', '.jpeg') and p.name not in enrolled]
    if extras:
        raise ValueError('Additional reference views require review: ' + ', '.join(extras))
    return entry


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--kind', choices=list(SPECS), required=True)
    parser.add_argument('--source-root', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(source_entry(args.kind, args.source_root), indent=2))
