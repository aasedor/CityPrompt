"""Small deterministic contracts for the final finite RLASM building batch."""
import hashlib
import json
from pathlib import Path


def subtract_openings(left, right, bottom, top, holes):
    spans = [(left, right)]
    for h in holes:
        if top <= h['z'] or bottom >= h['z'] + h['h']:
            continue
        a, b = h['u'] - h['w'] / 2, h['u'] + h['w'] / 2
        spans = [s for x, y in spans for s in ((x, min(y, a)), (max(x, b), y))
                 if s[1] - s[0] > 1e-6]
    return spans


def source_entry(directory, slug, review):
    directory = Path(directory)
    if review.get('compatible') is not True:
        raise ValueError('Independent compatible source review required')
    provenance = json.loads((directory / 'generation-provenance.json').read_text(encoding='utf-8'))
    if provenance['origin'] != 'original_generated_design':
        raise ValueError('Original design provenance required')
    records = provenance['records']
    if len(records) != 3 or {r['role'] for r in records} != {'front', 'oblique', 'top'}:
        raise ValueError('Exactly front, oblique and top references required')
    sources = []
    for r in records:
        p = directory / r['file']
        if not p.resolve().is_relative_to(directory.resolve()):
            raise ValueError('Reference path escapes family')
        raw = p.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if len(raw) != r['bytes'] or digest != r['sha256']:
            raise ValueError('Reference bytes changed: ' + str(p))
        if digest not in review.get('inspected_sha256', []):
            raise ValueError('Reference missing from independent review')
        sources.append(dict(role=r['role'], original_path=str(p.resolve()),
                            path='sources/' + p.name, bytes=len(raw), sha256=digest))
    return dict(archetype_id=slug, variant_id=slug + '-v1',
                source_origin='original_generated_design', _reference_root=str(directory.resolve()),
                sources=sources)
