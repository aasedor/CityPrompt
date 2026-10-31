"""Locked native-source and finite-topology contracts for three curved bridges."""
from importlib import import_module
import hashlib
import json
from pathlib import Path
import struct

import numpy as np
import pytest
import trimesh


ROOT = Path(__file__).resolve().parents[2]


def builder():
    assert (ROOT / 'tools/drawn_bridge_routes/topology_build.py').exists(), 'topology extractor is missing'
    return import_module('tools.drawn_bridge_routes.topology_build')


@pytest.mark.parametrize('style', ['ring', 'flyover', 'weathering'])
def test_source_gate_rejects_changed_original_before_geometry_loading(style, tmp_path):
    b = builder()
    bad = tmp_path / 'bad.glb'
    bad.write_bytes(b.source_path(style).read_bytes() + b'changed')
    with pytest.raises(ValueError, match='source hash'):
        b.extract(style, bad)


@pytest.mark.parametrize('style', ['ring', 'flyover', 'weathering'])
def test_bridge_owned_extraction_keeps_native_structure_and_excludes_scene(style):
    scenes, record = builder().extract(style)
    assert record['ownership']['excludedTriangles'] > 0
    assert record['sourceSha256'] == hashlib.sha256(builder().source_path(style).read_bytes()).hexdigest()
    all_meshes = [m for s in scenes.values() for m in s.geometry.values()]
    materials = {m.visual.material.name for m in all_meshes}
    assert not materials & {'CLAY_ASPHALT', 'CLAY_SAND', 'CLAY_TREE', 'CLAY_TIMBER', 'CLAY_PLANTING', 'CLAY_INTERIOR'}
    assert min(s.bounds[0, 1] for s in scenes.values()) >= -1e-5
    assert record['topology']['centerlines']
    assert record['topology']['gradeEndpointsM'][0][2] == pytest.approx(.0, abs=.11)
    assert record['topology']['gradeEndpointsM'][1][2] == pytest.approx(.0, abs=.11)
    if style == 'ring':
        assert set(scenes) == {'ring_core', 'ring_ramp_left', 'ring_ramp_right'}
        assert {'CLAY_RED', 'CLAY_CABLE', 'CLAY_STEEL'} <= materials
        assert scenes['ring_core'].bounds[1, 1] == pytest.approx(60)
        for kind in ('ring_ramp_left','ring_ramp_right'):
            assert np.max(np.abs(scenes[kind].bounds[:,2])) <= 32.070
            assert np.max(np.abs(scenes[kind].bounds[:,0])) <= 2.301
    elif style == 'flyover':
        assert {'CLAY_ORANGE', 'CLAY_UNDER', 'CLAY_DECK', 'CLAY_CONCRETE'} <= materials
        assert scenes['bridge_topology'].extents[2] < 380
        path = np.array(record['topology']['centerlines'][0]['pointsM'])
        assert np.ptp(path[:, 0]) > 30
        assert path[:, 2].max() == pytest.approx(6.2)
    else:
        assert {'CLAY_RUST', 'CLAY_MESH', 'CLAY_BRICK', 'CLAY_HARDWARE'} <= materials
        assert record['access']['towerCount'] == 2
        assert record['access']['risersPerTower'] == 40
        assert record['access']['minStairClearWidthM'] >= 1.2
        assert record['access']['solidTowerBodiesRemoved'] == 2


@pytest.mark.parametrize('style', ['flyover', 'weathering'])
def test_bounded_span_mapping_preserves_heights_curved_profile_and_rigid_ends(style):
    b = builder()
    _, record = b.extract(style)
    descriptor = record['deformation']
    native = descriptor['nativeLengthM']
    positions = np.array([[1, 7, -native / 2], [2, 6.2, 0], [3, 0, native / 2]])
    stretched = b.deform_longitudinal(positions, native * 1.1, descriptor)
    assert stretched[:, :2] == pytest.approx(positions[:, :2])
    assert stretched[:, 2] == pytest.approx([-native * .55, 0, native * .55])
    with pytest.raises(ValueError, match='supported length'):
        b.deform_longitudinal(positions, native * 2, descriptor)


def test_ring_radius_mapping_retains_metric_deck_width_and_keeps_mast_rigid():
    b = builder()
    _, record = b.extract('ring')
    d = record['deformation']
    cx = d['centerAcrossM']
    points = np.array([[cx + 30.6, 6.6, 0], [cx + 36, 6.6, 0], [cx, 60, 0]])
    grown = b.deform_ring(points[:2], 1.2, d, 'ring')
    assert grown[1, 0] - grown[0, 0] == pytest.approx(5.4)
    assert b.deform_ring(points[2:], 1.2, d, 'pylon')[0] == pytest.approx([cx * 1.2, 60, 0])


def vertical_hits(scene, across, along, material=None):
    hits=[]
    for mesh in scene.geometry.values():
        if material is not None and mesh.visual.material.name != material:
            continue
        tri=mesh.triangles[:, :, [0,2,1]].copy()
        tri[:,:,1]*=-1
        a=tri[:,0,:2]; v0=tri[:,1,:2]-a; v1=tri[:,2,:2]-a
        v2=np.array([across,along])-a
        det=v0[:,0]*v1[:,1]-v0[:,1]*v1[:,0]
        valid=np.abs(det)>1e-10
        u=np.divide(v2[:,0]*v1[:,1]-v2[:,1]*v1[:,0],det,out=np.zeros_like(det),where=valid)
        v=np.divide(v0[:,0]*v2[:,1]-v0[:,1]*v2[:,0],det,out=np.zeros_like(det),where=valid)
        valid &= (u>=-1e-6)&(v>=-1e-6)&(u+v<=1+1e-6)
        heights=tri[:,0,2]+u*(tri[:,1,2]-tri[:,0,2])+v*(tri[:,2,2]-tri[:,0,2])
        hits.extend(heights[valid])
    return np.array(hits)


def test_v_stair_treads_are_supported_with_clear_headroom_in_both_towers():
    b=builder()
    scenes,record=b.extract('weathering')
    scene=scenes['bridge_topology']
    frame=record['_info']['frame']
    for q,u in [(b.QA,(b.QA-b.APEX)/30),(b.QB,(b.QB-b.APEX)/32)]:
        for flight in range(4):
            start,end=(.9,3.7) if flight%2==0 else (3.7,.9)
            lane=.85 if flight%2==0 else -.85
            for step in (2,6,9):
                s=start+(end-start)*(step+.5)/10
                height=flight*1.75+(step+1)*.175
                for lateral in (-.5,0,.5):
                    p=b._point([q[0]+u[0]*s-u[1]*(lane+lateral),q[1]+u[1]*s+u[0]*(lane+lateral),height],frame)
                    hits=vertical_hits(scene,p[0],p[1])
                    assert np.any(np.isclose(hits,height,atol=1e-5)), (flight,step,lateral,'missing tread')
                    assert not np.any((hits>height+.01)&(hits<height+2.0)), (flight,step,lateral,'blocked headroom')


def test_v_drawing_interval_contains_all_towers_and_every_stair_station():
    scenes,record=builder().extract('weathering')
    length=record['deformation']['nativeLengthM']
    assert length > 54
    bounds=scenes['bridge_topology'].bounds
    assert np.max(np.abs(bounds[:,2])) <= length/2+1e-5
    for path in record['topology']['walkingPaths']:
        assert all(-length/2 <= p[1] <= length/2 for p in path['pointsM'])


def test_s_drawing_interval_contains_full_skewed_ramp_end_sections():
    scenes,record=builder().extract('flyover')
    length=record['deformation']['nativeLengthM']
    bounds=scenes['bridge_topology'].bounds
    assert np.max(np.abs(bounds[:,2])) <= length/2+1e-5


def test_ring_cable_anchor_meets_metric_ring_when_radius_changes():
    b=builder()
    _,record=b.extract('ring')
    d=record['deformation']
    cx=d['centerAcrossM']
    anchor=np.array([[cx+30.65,6.3,0]])
    cable=b.deform_ring(anchor,1.2,d,'cables')
    ring=b.deform_ring(anchor,1.2,d,'ring')
    assert cable == pytest.approx(ring,abs=1e-6)


def test_ring_ramp_throats_meet_full_ring_and_native_grade_feet():
    scenes,record=builder().extract('ring')
    throat=record['deformation']['throatAlongM']
    for side,sign in [('left',1),('right',-1)]:
        for across in (-1.9,0,1.9):
            core=vertical_hits(scenes['ring_core'],across,-sign*throat,'CLAY_RED')
            assert np.any(np.isclose(core,6.6,atol=1e-4))
            ramp=vertical_hits(scenes['ring_ramp_'+side],across,sign*32.068,'CLAY_RAMPDECK')
            assert np.max(ramp) == pytest.approx(6.59,abs=.002)
            foot=vertical_hits(scenes['ring_ramp_'+side],across,-sign*32.068,'CLAY_RAMPDECK')
            assert np.max(foot) == pytest.approx(.1,abs=.002)


def test_export_is_deterministic_material_exact_and_source_unchanged(tmp_path):
    b = builder()
    for style in ('ring', 'flyover', 'weathering'):
        first = tmp_path / style
        row, provenance = b.build(style, first)
        locks = {p.name: p.read_bytes() for p in first.iterdir()}
        b.build(style, first)
        assert locks == {p.name: p.read_bytes() for p in first.iterdir()}
        source = b.source_path(style).read_bytes()
        n = struct.unpack_from('<I', source, 12)[0]
        originals = {m['name']: m for m in json.loads(source[20:20+n])['materials']}
        for kind, lock in row['modules'].items():
            data = (first / (kind + '.glb')).read_bytes()
            assert hashlib.sha256(data).hexdigest() == lock['sha256']
            n = struct.unpack_from('<I', data, 12)[0]
            doc = json.loads(data[20:20+n])
            assert all(m == originals[m['name']] for m in doc['materials'])
            assert all('uri' not in buffer for buffer in doc['buffers'])
        assert row['program']['adapter'] == 'source-span-bridge-v1'
        edges=sorted((s['x']-s['width']/2,s['x']+s['width']/2) for s in row['sections'])
        assert edges[0][0] == pytest.approx(-row['widthM']/2)
        assert edges[-1][-1] == pytest.approx(row['widthM']/2)
        assert all(a[1] == pytest.approx(b[0]) for a,b in zip(edges,edges[1:]))
        assert row['program']['bridge']['parts']
        assert provenance['review']['runtime'] == 'NOT TESTED'
        assert hashlib.sha256(source).hexdigest() == provenance['sourceSha256']
