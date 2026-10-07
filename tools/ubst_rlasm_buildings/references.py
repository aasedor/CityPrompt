"""Capture unchanged generated originals and fail closed if their lock changes."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

SLUG = 'ubst-live-work-row'
ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def image_size(path):
    try:
        from PIL import Image
    except ModuleNotFoundError:
        import bpy
        image = bpy.data.images.load(str(path), check_existing=False)
        result = list(image.size)
        bpy.data.images.remove(image)
        return result
    with Image.open(path) as image:
        size = list(image.size)
        image.verify()
        return size


def capture(root=ROOT):
    source = json.loads(Path(__file__).with_name('reference-capture.json').read_text())
    target = Path(root) / 'frontend/public/archetypes/buildings' / SLUG
    target.mkdir(parents=True, exist_ok=False)
    for record in source['records']:
        src = Path(record['generated_path'])
        dst = target / record['file']
        shutil.copy2(src, dst)
        record.update(sha256=digest(dst), bytes=dst.stat().st_size,
                      dimensions_px=image_size(dst))
    (target / 'generation-provenance.json').write_text(
        json.dumps(source, indent=2), encoding='utf-8')
    return target


def source_entry(root=ROOT, slug=SLUG):
    if Path(slug).name != slug or slug in {'.', '..'}:
        raise ValueError('Invalid family slug')
    target = Path(root) / 'frontend/public/archetypes/buildings' / slug
    provenance = json.loads((target / 'generation-provenance.json').read_text(encoding='utf-8'))
    if provenance['origin'] != 'original_generated_design':
        raise ValueError('Original design provenance is required')
    records = provenance['records']
    if len(records) != 3 or {s['role'] for s in records} != {'front', 'oblique', 'top'}:
        raise ValueError('Exactly three compatible reference roles required')
    sources = []
    for record in records:
        if Path(record['file']).name != record['file']:
            raise ValueError('Reference path escapes its family')
        path = target / record['file']
        if (path.stat().st_size != record['bytes'] or digest(path) != record['sha256']):
            raise ValueError('Reference bytes changed: ' + str(path))
        size = image_size(path)
        if size != record['dimensions_px'] or min(size) < 512:
            raise ValueError('Reference image dimensions invalid')
        sources.append(dict(role=record['role'], original_path=str(path),
            path='sources/' + path.name, bytes=record['bytes'],
            sha256=record['sha256'], dimensions_px=size))
    enrolled = {s['file'] for s in records}
    extras = [p.name for p in target.glob('variant_0*')
              if p.suffix.lower() in {'.png', '.jpg', '.jpeg'} and p.name not in enrolled]
    if extras:
        raise ValueError('Unreviewed additional references: ' + ', '.join(extras))
    return dict(archetype_id=slug, variant_id=slug + '-v0',
                source_origin='original_generated_design',
                _reference_root=str(target), sources=sources)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--capture', action='store_true')
    args = parser.parse_args()
    if args.capture:
        capture()
    print(json.dumps(source_entry(), indent=2))
