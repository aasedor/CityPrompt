import pytest
from pyproj import Geod
from tools.elevation_trial.calgary_corridor import LocalFrame


@pytest.mark.parametrize('heading,azimuth',[(0,0),(90,90)])
def test_viewer_frame_preserves_heading_and_metric_distance(heading,azimuth):
    frame = LocalFrame(-114.12,51.016,1100,heading)
    lon,lat,height = frame.geographic(0,0)
    assert (lon,lat) == pytest.approx((-114.12,51.016),abs=1e-10)
    assert height == pytest.approx(1100,abs=1e-6)
    assert frame.local_height(lon,lat,1101)==pytest.approx(1,abs=1e-6)
    end_lon,end_lat,_ = frame.geographic(100,0)
    bearing,_,distance = Geod(ellps='WGS84').inv(lon,lat,end_lon,end_lat)
    assert bearing == pytest.approx(azimuth,abs=1e-5)
    # Geodesic distance is on the ellipsoid, 1100 m below the local frame.
    assert distance == pytest.approx(100,abs=.02)


def test_cross_road_axis_is_left_of_heading():
    frame = LocalFrame(-114.12,51.016,1100,90)
    lon,lat,_ = frame.geographic(0,10)
    assert lat>51.016
    assert lon==pytest.approx(-114.12,abs=1e-10)
