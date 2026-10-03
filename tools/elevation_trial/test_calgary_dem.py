from pathlib import Path

import pytest

from tools.elevation_trial.calgary_dem import AsciiDem


def raster(tmp_path: Path, values: str) -> AsciiDem:
    path = tmp_path/'ground.asc'
    path.write_text('ncols 3\nnrows 3\nxllcorner 100\nyllcorner 200\ncellsize 2\nNODATA_value -9999\n'+values)
    return AsciiDem(path)


def test_cell_centres_and_north_first_rows(tmp_path):
    dem = raster(tmp_path, '5 7 9\n3 5 7\n1 3 5\n')
    assert dem.sample(101, 205) == 5
    assert dem.sample(103, 203) == 5
    assert dem.sample(102, 204) == 5
    assert dem.sample(102, 202) == 3


def test_missing_ground_is_never_bridged(tmp_path):
    dem = raster(tmp_path, '5 7 9\n3 -9999 7\n1 3 5\n')
    with pytest.raises(ValueError, match='Missing ground'):
        dem.sample(102, 204)


def test_outside_support_is_not_clamped(tmp_path):
    dem = raster(tmp_path, '5 7 9\n3 5 7\n1 3 5\n')
    with pytest.raises(ValueError, match='outside'):
        dem.sample(100, 205)
