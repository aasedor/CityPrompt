"""Hydrated, immutable candidate-byte checks; no database or paid services."""
import hashlib
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[2]
ROWS = json.loads((ROOT / 'frontend/src/features/parks/calgarySafetyCatalogue.json').read_text())


def test_exact_bounded_batch_and_no_source_collisions():
    existing = json.loads((ROOT / 'frontend/src/features/parks/trafficSafetyCatalogue.json').read_text())
    assert len(ROWS) == len({r['id'] for r in ROWS}) == 10
    assert len({r['safety']['family'] for r in ROWS}) == 8
    assert not ({r['id'] for r in ROWS} & {r['id'] for r in existing})
    assert sum(r['bytes'] for r in ROWS) < 1_000_000


def test_glbs_and_model_captures_match_reviewed_bytes():
    for row in ROWS:
        blob = (ROOT / 'frontend/public' / row['url'].lstrip('/')).read_bytes()
        assert hashlib.sha256(blob).hexdigest() == row['sha256'] == row['safety']['sha256']
        assert len(blob) == row['bytes']
        assert struct.unpack_from('<4sII', blob) == (b'glTF', 2, len(blob))
        length, kind = struct.unpack_from('<I4s', blob, 12)
        assert kind == b'JSON'
        gltf = json.loads(blob[20:20+length])
        assert not gltf.get('textures') and not gltf.get('images')
        assert not gltf.get('animations')
        assert all('uri' not in b for b in gltf['buffers'])
        assert all(n.get('scale', [1, 1, 1]) == [1, 1, 1] for n in gltf['nodes'])
        primitives = [p for m in gltf['meshes'] for p in m['primitives']]
        assert 1 <= len(primitives) <= 9
        assert sum(gltf['accessors'][p['indices']]['count']//3 for p in primitives) <= 6000
        assert all(m.get('doubleSided') for m in gltf['materials'])
        image = (ROOT / 'frontend/public' / row['thumbnailUrl'].lstrip('/')).read_bytes()
        assert hashlib.sha256(image).hexdigest() == row['thumbnailSha256']
        assert row['runtimeApproved'] is True
        assert row['datumLift'] == 0
        assert row['safety']['transforms'] == ['translation', 'yaw']
