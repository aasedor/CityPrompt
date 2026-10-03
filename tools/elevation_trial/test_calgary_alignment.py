import json
import os
from pathlib import Path

import pytest

from tools.elevation_trial.calgary_alignment import CalgaryAlignment, align_trial


def test_unknown_grid_is_rejected(tmp_path):
    path = tmp_path/'bad.dac'
    path.write_bytes(b'wrong grid')
    with pytest.raises(ValueError, match='Unrecognized Alberta grid'):
        CalgaryAlignment(path)


def test_missing_grid_never_falls_back(tmp_path):
    with pytest.raises(FileNotFoundError):
        CalgaryAlignment(tmp_path/'missing.dac')


@pytest.mark.parametrize('point', [(51, -114, 1100), (0, 0, 1100),
                                 (-114, 51, float('nan')), (-114, 51, 0)])
def test_invalid_coordinates_are_rejected(point):
    with pytest.raises(ValueError):
        CalgaryAlignment._validate(*point)


def test_already_aligned_or_unknown_baseline_is_rejected(tmp_path):
    with pytest.raises(ValueError, match='original 4 m'):
        align_trial({'horizontalAccuracyM': None}, None, tmp_path)


def test_unsupported_grid_shape_is_rejected(tmp_path):
    with pytest.raises(ValueError, match='31 by 31'):
        align_trial({'horizontalAccuracyM': 4,
                     'horizontalOperation': 'NAD83 to WGS 84 (1)',
                     'sites': [{'columns': 30}]}, None, tmp_path)


@pytest.fixture
def alignment():
    path = os.environ.get('CALGARY_ALIGNMENT_GRID')
    if not path:
        pytest.skip('Set CALGARY_ALIGNMENT_GRID for official-grid integration checks')
    return CalgaryAlignment(Path(path))


@pytest.mark.parametrize('source', [(-114.12, 51.016), (-114.1265, 51.0245)])
def test_real_grid_roundtrip_and_expected_direction(alignment, source):
    # The grid and frame operation move these locations west and north. A
    # missing grid, wrong Helmert direction, or omitted epoch changes the result.
    lng, lat = alignment.display_lonlat(*source, 1100)
    assert lng < source[0] and lat > source[1]
    assert lng - source[0] == pytest.approx(-0.00001854, abs=1e-7)
    assert lat - source[1] == pytest.approx(0.00000532, abs=1e-7)
    assert alignment.source_lonlat(lng, lat, 1100) == pytest.approx(source, abs=1e-10)
    assert alignment.provenance()['horizontalAccuracyM'] is None


def test_source_heights_preserved_and_geoid_applied_once(alignment, tmp_path, monkeypatch):
    import tools.elevation_trial.calgary_alignment as module
    queries = []
    def mock_geoid(lat, lng, out, tag, epoch):
        queries.append((lat, lng, epoch))
        return -16.025
    monkeypatch.setattr(module, 'geoid', mock_geoid)
    source = [-114.12, 51.016, 1120, 1104]
    site = dict(name='test', center=source[:2], columns=31, rows=31,
                boundary=[source[:2] for _ in range(4)], points=[source[:] for _ in range(961)],
                connection=dict(profile=[source[:] for _ in range(31)],
                                edges=[[source[:], source[:]] for _ in range(31)]))
    baseline = dict(horizontalAccuracyM=4, horizontalOperation='NAD83 to WGS 84 (1)', sites=[site])
    before = json.dumps(baseline)
    result = align_trial(baseline, alignment, tmp_path)
    assert json.dumps(baseline) == before
    updated = result['sites'][0]
    for p in updated['points'] + updated['connection']['profile'] + updated['connection']['edges'][0]:
        assert p[2] == 1120
        assert p[3] == pytest.approx(1103.975)
        assert alignment.source_lonlat(*p[:2], p[3]) == pytest.approx(source[:2], abs=1e-10)
    assert all(q[2] == '2010-01-01' for q in queries)
    assert len(queries) == 6
