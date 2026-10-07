import json
from pathlib import Path

import pytest
from PIL import Image

from tools.ubst_rlasm_buildings.references import SLUG, digest, source_entry


@pytest.fixture
def locked(tmp_path):
    target = tmp_path / 'frontend/public/archetypes/buildings' / SLUG
    target.mkdir(parents=True)
    records = []
    for role in ['front', 'oblique', 'top']:
        path = target / f'variant_0_{role}.png'
        Image.new('RGB', (512, 512)).save(path)
        records.append(dict(role=role, file=path.name, sha256=digest(path),
                            bytes=path.stat().st_size, dimensions_px=[512, 512]))
    (target / 'generation-provenance.json').write_text(json.dumps(
        dict(origin='original_generated_design', records=records)))
    return tmp_path, target


def test_locked_originals_are_enrolled(locked):
    assert len(source_entry(locked[0])['sources']) == 3


def test_changed_image_is_rejected(locked):
    (locked[1] / 'variant_0_front.png').write_bytes(b'changed')
    with pytest.raises(ValueError, match='bytes changed'):
        source_entry(locked[0])


def test_unreviewed_extra_view_is_rejected(locked):
    Image.new('RGB', (512, 512)).save(locked[1] / 'variant_0_rear.png')
    with pytest.raises(ValueError, match='Unreviewed additional'):
        source_entry(locked[0])


def test_wrong_role_and_escaping_path_are_rejected(locked):
    path = locked[1] / 'generation-provenance.json'
    data = json.loads(path.read_text())
    data['records'][2]['role'] = 'front'
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match='three compatible'):
        source_entry(locked[0])
    data['records'][2]['role'] = 'top'
    data['records'][2]['file'] = '../outside.png'
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match='escapes'):
        source_entry(locked[0])
