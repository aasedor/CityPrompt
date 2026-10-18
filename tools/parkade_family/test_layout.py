import pytest
from .layout import frame_plan,partition


def area(rect):return (rect[1]-rect[0])*(rect[3]-rect[2])


def test_floor_partition_really_removes_courtyard_and_core_wells():
    parts=partition((-32,32,-24,17.5),[(-8,8,-7,7),(-32,-27.1,-24,-17.4),(27.1,32,-24,-17.4)])
    assert sum(map(area,parts)) == pytest.approx(64*41.5-16*14-2*4.9*6.6)
    for x,y in [(0,0),(-30,-20),(30,-20)]:
        assert not any(a<x<b and c<y<d for a,b,c,d in parts)


@pytest.mark.parametrize('w,d,n',[(54,36,5),(66,36,5),(60,36,4),(64,48,4)])
def test_authored_frame_preserves_native_levels_and_clear_vehicle_portal(w,d,n):
    f=frame_plan(w,d,n)
    assert len(f['datums'])==n
    assert f['datums'][-1]==pytest.approx(.15+3.3*(n-1))
    assert all(abs(x-f['entryX'])>=3 for x in f['frontColumns'])
    assert f['rampX'][1]-f['rampX'][0]==w-14
    assert f['towerHeight']==pytest.approx(.15+3.3*(n-1)+2.75)
