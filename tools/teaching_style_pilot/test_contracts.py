import pytest

from tools.teaching_style_pilot.contracts import lock_sources, verify_evidence, unobstructed_spans


def test_source_lock_detects_a_changed_source(tmp_path):
    source = tmp_path / 'board.png'
    source.write_bytes(b'original-reference')
    roles = {r: source for r in ('front', 'oblique', 'top', 'rear_side')}
    record = lock_sources('house', 'exact', roles)
    source.write_bytes(b'replacement')
    with pytest.raises(ValueError, match='changed'):
        verify_evidence(record, tmp_path)


def test_source_lock_refuses_missing_top_view(tmp_path):
    source = tmp_path / 'front.png'
    source.write_bytes(b'reference')
    with pytest.raises(ValueError, match='top'):
        lock_sources('house', 'exact', {'front': source, 'oblique': source})


def test_evidence_refuses_missing_mandatory_render(tmp_path):
    source = tmp_path / 'board.png'
    source.write_bytes(b'reference')
    record = lock_sources('house', 'exact', {r: source for r in ('front', 'oblique', 'top')})
    with pytest.raises(ValueError, match='renders/front.png'):
        verify_evidence(record, tmp_path, require_renders=True)


def test_stone_belt_leaves_garden_door_clear():
    spans=unobstructed_spans(-8,8,[(4.38,5.42)])
    assert spans==[(-8,4.38),(5.42,8)]
    assert all(end<=4.38 or start>=5.42 for start,end in spans)
