from pathlib import Path

import pytest

from tools.teaching_style_wave2.contracts import candidate_path, source_lock


def test_output_refuses_a_previous_candidate_without_touching_it(tmp_path):
    root = tmp_path / 'batch'
    previous = root / 'workshop-v001'
    previous.mkdir(parents=True)
    marker = previous / 'review.json'
    marker.write_text('preserved rejection')
    with pytest.raises(FileExistsError):
        candidate_path(previous, root)
    assert marker.read_text() == 'preserved rejection'


def test_output_cannot_escape_the_named_batch(tmp_path):
    root = tmp_path / 'batch'
    with pytest.raises(ValueError, match='batch'):
        candidate_path(root / '..' / 'elsewhere', root)
    with pytest.raises(ValueError, match='batch'):
        candidate_path(root, root)
    assert not root.exists()


def test_source_lock_refuses_a_non_authoritative_image_root(tmp_path):
    canonical = tmp_path / 'frontend/public/archetypes/buildings'
    canonical.mkdir(parents=True)
    source = canonical / 'front.png'
    source.write_bytes(b'locked source')
    outside = tmp_path / 'legacy' / 'top.png'
    outside.parent.mkdir()
    outside.write_bytes(b'different root')
    with pytest.raises(ValueError, match='authoritative'):
        source_lock('workshop', 'exact', {'front': source, 'oblique': source, 'top': outside}, canonical)


def test_source_lock_enrolls_every_supplied_compatible_view(tmp_path):
    sources = {}
    for role in ('front', 'oblique', 'top', 'oblique_high'):
        path = tmp_path / f'{role}.png'
        path.write_bytes(role.encode())
        sources[role] = path
    locked = source_lock('workshop', 'exact', sources, tmp_path)
    assert {item['role'] for item in locked} == set(sources)
    assert all(item['bytes'] and len(item['sha256']) == 64 for item in locked)
