"""Phase A: lock the exact catalogue views of one archetype variant as RLASM sources.

Catalogue reference nomination (not a generated design). Pixels govern geometry;
metric dimensions in the family module are authored teaching assumptions.
"""
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ARCHETYPE = 'barcelona_corner_chamfer'
DIRECTORY = 'frontend/public/archetypes/buildings/barcelona-corner-chamfer'
VARIANT = 'variant_0'
VARIANT_ID = 'chamfer_classic'
ROLES = {'front': 'variant_0.png', 'oblique': 'variant_0_angle_60.jpg', 'top': 'variant_0_angle_90.jpg'}
MANIFEST = Path(__file__).resolve().parent / 'sources.json'


def lock():
    directory = ROOT / DIRECTORY
    records = []
    for role, name in ROLES.items():
        path = directory / name
        raw = path.read_bytes()
        if raw.startswith(b'version https://git-lfs'):
            raise ValueError('LFS pointer, not pixels: ' + str(path))
        with Image.open(path) as img:
            img.load(); size = list(img.size)
        records.append(dict(archetype_id=ARCHETYPE, variant_id=VARIANT, catalogue_variant_id=VARIANT_ID, role=role,
                            path=str(path.relative_to(ROOT)).replace('\\', '/'), file=name,
                            bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(), dimensions_px=size))
    sibling = sorted(p.name for p in directory.iterdir() if p.name.startswith('variant_') and not p.name.startswith(VARIANT))
    manifest = dict(schema='cityprompt.rlasm.source-lock@1', method='RLASM v6.1', archetype_id=ARCHETYPE,
                    variant_id=VARIANT, catalogue_variant_id=VARIANT_ID, source_origin='catalogue_reference_nomination',
                    sibling_variant_mixing_allowed=False, excluded_sibling_files=sibling,
                    excluded_duplicate='hero.png (LFS pointer locally; composite hero, not a locked view)',
                    records=records)
    MANIFEST.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest


def verify():
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    for r in manifest['records']:
        raw = (ROOT / r['path']).read_bytes()
        if len(raw) != r['bytes'] or hashlib.sha256(raw).hexdigest() != r['sha256']:
            raise ValueError('Locked source changed: ' + r['path'])
    return manifest


if __name__ == '__main__':
    m = lock()
    for r in m['records']:
        print(r['role'], r['file'], r['bytes'], r['sha256'][:16], r['dimensions_px'])
