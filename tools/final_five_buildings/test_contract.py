import hashlib
import json
from pathlib import Path

import pytest

from tools.final_five_buildings.contract import source_entry, subtract_openings


def test_brick_courses_do_not_bridge_openings():
    holes = [dict(u=0, w=2, z=0, h=3), dict(u=3, w=1, z=1, h=1)]
    assert subtract_openings(-5, 5, 1.5, 1.57, holes) == [(-5, -1), (1, 2.5), (3.5, 5)]
    assert subtract_openings(-5, 5, 3.1, 3.17, holes) == [(-5, 5)]
    assert subtract_openings(-.5, .5, 1, 1.07, holes) == []


def test_source_lock_rejects_modified_reference_and_unapproved_set(tmp_path):
    records = []
    for role in ('front', 'oblique', 'top'):
        path = tmp_path / (role + '.png')
        path.write_bytes(b'locked original ' + role.encode())
        records.append(dict(role=role, file=path.name, bytes=path.stat().st_size,
                            sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    provenance = dict(origin='original_generated_design', records=records)
    (tmp_path / 'generation-provenance.json').write_text(json.dumps(provenance))
    with pytest.raises(ValueError, match='review'):
        source_entry(tmp_path, 'test', dict(compatible=False))
    review = dict(compatible=True, inspected_sha256=[r['sha256'] for r in records])
    assert len(source_entry(tmp_path, 'test', review)['sources']) == 3
    (tmp_path / 'top.png').write_bytes(b'changed')
    with pytest.raises(ValueError, match='changed'):
        source_entry(tmp_path, 'test', review)
