"""Independent spatial checks for ramp headroom and open circulation zones."""
import hashlib
import json
from pathlib import Path
import pytest
from . import specs as S


def test_rear_ramps_reach_successive_decks_without_crossing_each_other():
    for level in range(3):
        assert S.ramp_height(level, -23) == pytest.approx(S.LEVELS[level])
        assert S.ramp_height(level, 23) == pytest.approx(S.LEVELS[level + 1])
    for x in (-23, -12, 0, 12, 23):
        for lower in (0, 1):
            clearance = S.ramp_height(lower + 1, x) - S.RAMP_THICKNESS - S.ramp_height(lower, x)
            assert clearance >= 2.4
    assert S.RAMP_Y[1] - S.RAMP_Y[0] - 2*(.06+.055/2) >= S.RAMP_CLEAR_WIDTH


def test_upper_main_deck_has_open_stair_wells_and_no_rear_ramp_cover():
    for x0, x1, y0, y1 in S.CORE_HOLES:
        for x, y in ((x0+.01, y0+.01), ((x0+x1)/2, (y0+y1)/2), (x1-.01, y1-.01)):
            assert not any(a < x < b and c < y < d for a,b,c,d in S.main_deck_panels())
    assert not any(a < 0 < b and c < 15 < d for a,b,c,d in S.main_deck_panels())


def test_finite_brief_retains_two_conventional_and_three_innovative_models():
    assert [d['style'] for d in S.DESIGNS.values()].count('conventional') == 2
    assert [d['style'] for d in S.DESIGNS.values()].count('innovative') == 3
    assert len({d['slug'] for d in S.DESIGNS.values()}) == 5


@pytest.mark.parametrize('origin',['original_generated_design','original_authored_design'])
def test_source_lock_rejects_modified_bytes(tmp_path: Path,origin: str):
    records=[]
    for role in ('front','oblique','top'):
        raw=('original-'+role).encode();(tmp_path/(role+'.png')).write_bytes(raw)
        records.append(dict(role=role,file=role+'.png',bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
    (tmp_path/'generation-provenance.json').write_text(json.dumps(dict(origin=origin,records=records)))
    with pytest.raises(ValueError, match='ramp_section'):
        S.source_entry(tmp_path)
    section=b'authoritative ramp section'
    (tmp_path/'ramp_section.png').write_bytes(section)
    records.append(dict(role='ramp_section',file='ramp_section.png',bytes=len(section),sha256=hashlib.sha256(section).hexdigest()))
    (tmp_path/'generation-provenance.json').write_text(json.dumps(dict(origin=origin,records=records)))
    assert len(S.source_entry(tmp_path)['sources']) == 4
    (tmp_path/'front.png').write_bytes(b'changed')
    with pytest.raises(ValueError, match='Locked source changed'):
        S.source_entry(tmp_path)
