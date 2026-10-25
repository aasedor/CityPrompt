"""Small fail-closed source/evidence checks for the finite teaching batch."""
from hashlib import sha256
from pathlib import Path

BASELINE = ('front', 'front_corner', 'aerial', 'left_side', 'right_side',
            'rear', 'rear_side', 'facade_close', 'architecture_close', 'glass_close')


def unobstructed_spans(start, end, openings):
    spans=[];cursor=start
    for lo,hi in sorted(openings):
        lo=max(start,lo);hi=min(end,hi)
        if hi<=cursor:continue
        if lo>cursor:spans.append((cursor,lo))
        cursor=max(cursor,hi)
    if cursor<end:spans.append((cursor,end))
    return spans


def lock_sources(archetype_id, variant_id, roles):
    for role in ('front', 'oblique', 'top'):
        if role not in roles:
            raise ValueError(f'missing source role: {role}')
    return [dict(archetype_id=archetype_id, variant_id=variant_id, role=role,
                 path='sources/' + Path(path).name, original_path=str(Path(path).resolve()),
                 bytes=Path(path).stat().st_size, sha256=sha256(Path(path).read_bytes()).hexdigest())
            for role, path in roles.items()]


def verify_evidence(sources, root, require_renders=False):
    root = Path(root)
    for source in sources:
        path = root / source['path']
        if not path.is_file():
            path = Path(source['original_path'])
        if (not path.is_file() or path.stat().st_size != source['bytes']
                or sha256(path.read_bytes()).hexdigest() != source['sha256']):
            raise ValueError(f'source changed: {source["role"]}')
    if require_renders:
        for name in BASELINE:
            path = root / 'renders' / (name + '.png')
            if not path.is_file() or path.stat().st_size < 1000:
                raise ValueError(f'missing render: renders/{name}.png')
    return True
