"""Green Terraces reservations and immutable original-source contract."""
import importlib
import importlib.util
import json
from pathlib import Path

import pytest


def sources():
    name = 'tools.parkade_family.green_sources'
    assert importlib.util.find_spec(name), 'Green source authority is not implemented'
    return importlib.import_module(name)


def test_garden_reserves_only_roof_bays_and_preserves_both_motor_aisles():
    s = sources()
    assert s.DESIGN['width'] == 60 and s.DESIGN['depth'] == 40
    assert s.DESIGN['frame_depth'] == 36 and s.DESIGN['levels'] == 4
    x0, x1, y0, y1 = s.DESIGN['garden']
    assert (x0, x1, y0, y1) == (-10.8, 10.8, -5.5, 5.5)
    assert y0 > -11.5 and y1 < 11.5
    assert all(not (a < 0 < b and c < 0 < d) for a, b, c, d in s.garden_beds())
    assert all(not (a < 0 < b) for a, b, _, _ in s.garden_beds())


def test_terraces_and_screens_do_not_cover_portal_or_core_openings():
    s = sources()
    terraces = s.terrace_segments()
    assert sorted({p['projection'] for p in terraces}) == [.8, 1.4, 2.0]
    assert all(-16 <= p['x0'] < p['x1'] <= 16 for p in terraces)
    assert all(-20 <= p['y0'] < p['y1'] <= -18 for p in terraces)
    assert s.DESIGN['garden_max_height'] < 12.8


def test_source_package_is_four_role_hash_locked_and_refuses_overwrite(tmp_path: Path):
    s = sources()
    package = tmp_path / 'sources'
    s.write_sources(package)
    provenance = json.loads((package / 'generation-provenance.json').read_text())
    assert provenance['origin'] == 'original_authored_design'
    assert {r['role'] for r in provenance['records']} == {'front', 'top', 'oblique', 'ramp_section'}
    import hashlib
    for record in provenance['records']:
        raw = (package / record['file']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == record['sha256']
        assert len(raw) == record['bytes']
    before = (package / 'front.png').read_bytes()
    with pytest.raises(FileExistsError):
        s.write_sources(package)
    assert (package / 'front.png').read_bytes() == before


def test_actual_extra_geometry_keeps_motor_aisles_and_front_portal_clear():
    name = 'tools.parkade_family.family_green'
    assert importlib.util.find_spec(name), 'Green geometry is not implemented'
    family = importlib.import_module(name)
    class RecordingCore:
        def __init__(self):self.boxes=[];self.meshes=[]
        def box(self, name, loc, size, *args):self.boxes.append((name,loc,size))
        def mesh(self, name, vertices, faces, *args):self.meshes.append((name,vertices,faces))
        def beam(self, *args):pass
        def rod(self, *args):pass
    core=RecordingCore()
    family.extra_geometry(dict(datums=[.15+i*3.3 for i in range(4)],top=10.05,
        towerHeight=12.8,frontY=-18,rearY=18,width=60,depth=36,levels=4),core=core)
    assert len(core.boxes)>30 and len(core.meshes)>30
    for name,(x,y,z),(w,d,h) in core.boxes:
        assert -30.001 <= x-w/2 <= x+w/2 <= 30.001, name
        assert -20.001 <= y-d/2 <= y+d/2 <= 20.001, name
        assert z-h/2 >= -.001 and z+h/2 <= 12.8, name
        assert not (x-w/2 < -18.4 and x+w/2 > -23.6 and y-d/2 < -17.7 and z-h/2 < 2.6), name
        for lo,hi in [(-11.5,-5.5),(5.5,11.5)]:
            assert not (y-d/2 < hi-.01 and y+d/2 > lo+.01), name
        if ('Climber root planter' in name or 'Rear ground planter' in name) and 'bearing tray' in name:
            assert z-h/2 == pytest.approx(0), name
    all_vertices=[v for _,verts,_ in core.meshes for v in verts]
    assert all(-30 <= x <= 30 and -20.001 <= y <= 20.001 and 0 <= z <= 12.8 for x,y,z in all_vertices)


def test_terrace_diagonal_lower_anchors_have_physical_mounts_to_the_ledger():
    from . import family_green as family
    class ContactRecorder:
        def __init__(self):self.boxes=[];self.beams=[]
        def box(self,name,loc,size,*args):self.boxes.append((name,loc,size))
        def beam(self,name,a,b,*args):self.beams.append((name,a,b))
        def rod(self,*args):pass
        def mesh(self,*args):pass
    core=ContactRecorder()
    family.extra_geometry(dict(datums=[.15+i*3.3 for i in range(4)],top=10.05,
        towerHeight=12.8,frontY=-18,rearY=18,width=60,depth=36,levels=4),core=core)
    def bounds(part):
        _,loc,size=part
        return tuple(p-s/2 for p,s in zip(loc,size)),tuple(p+s/2 for p,s in zip(loc,size))
    mounts=[part for part in core.boxes if 'vertical mounting plate' in part[0]]
    ledgers=[part for part in core.boxes if 'seated back ledger' in part[0]]
    diagonals=[part for part in core.beams if 'bracket diagonal' in part[0]]
    assert len(diagonals)>=18
    for name,anchor,_ in diagonals:
        connected=[part for part in mounts if all(lo-1e-8<=p<=hi+1e-8
            for p,lo,hi in zip(anchor,*bounds(part)))]
        assert connected, f'Unsupported lower diagonal anchor: {name} at {anchor}'
        for plate in connected:
            low,high=bounds(plate)
            assert any(all(a<d and b>c for a,b,c,d in zip(low,high,*bounds(ledger)))
                for ledger in ledgers), 'Mount must penetrate its physical seated ledger'
