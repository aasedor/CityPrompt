"""Inspect emitted metric constructor boxes without a Blender installation.

These tests execute the actual frame recipe, not a second copy of its column
schedule. Blender primitives are recorded at their supplied native dimensions.
Visual joins, vehicles and engineering remain independent review duties.
"""
import importlib.util
from pathlib import Path
import sys
from types import ModuleType

import pytest

from . import layout

VARIANTS = [(54,36,5,None),(60,36,4,None),(66,36,5,None),(64,48,4,(-8,8,-7,7))]
EPS=1e-8


class Recorder(ModuleType):
    def __init__(self):
        super().__init__('clay_core')
        self.boxes=[]

    def box(self,name,loc,size,role='concrete',module='frame',soft=0):
        assert len(loc)==len(size)==3 and min(size)>0
        part=dict(name=name,lo=tuple(p-s/2 for p,s in zip(loc,size)),
            hi=tuple(p+s/2 for p,s in zip(loc,size)),role=role,module=module)
        self.boxes.append(part)
        return part

    def solid_surface(self,*args):pass
    def prism(self,*args):pass
    def rod(self,*args):pass


def record_frame(monkeypatch,width,depth,levels,courtyard=None,source=None):
    recorder=Recorder();primitives=ModuleType('build')
    def plate(name,rect,z,thick=.25,role='deck'):
        a,b,c,d=rect
        return recorder.box(name,((a+b)/2,(c+d)/2,z-thick/2),(b-a,d-c,thick),role,'floor structure')
    primitives.plate=plate
    primitives.guard=lambda *args:None
    primitives.flight=lambda *args:None
    primitives.text=lambda *args:None
    monkeypatch.setitem(sys.modules,'clay_core',recorder)
    monkeypatch.setitem(sys.modules,'build',primitives)
    monkeypatch.setitem(sys.modules,'layout',layout)
    path=Path(__file__).with_name('frame.py')
    spec=importlib.util.spec_from_file_location('_recorded_parkade_frame',path)
    module=importlib.util.module_from_spec(spec)
    if source is None:spec.loader.exec_module(module)
    else:exec(compile(source,str(path),'exec'),module.__dict__)
    frame=module.standard_frame(width,depth,levels,courtyard=courtyard)
    return frame,recorder.boxes


def overlaps(part,rect):
    a,b,c,d=rect;lo,hi=part['lo'],part['hi']
    return lo[0]<b-EPS and hi[0]>a+EPS and lo[1]<d-EPS and hi[1]>c+EPS


def columns(parts):
    result=[p for p in parts if p['name'] in
        {'Ground-bearing frame column','Rear landing column','Core structural corner'}]
    assert len(result)>20, 'The geometry recorder must contain the real constructor columns'
    return result


def assert_transverse_clear(frame,parts):
    h=frame['width']/2
    # Transverse parking span joins the two side routes. Core-occupied end
    # strips are separately checked behind the actual 6.55 m deep towers.
    corridors=[(-h+6.5,h-6.5,-11.5,-5.5),(-h+6.5,h-6.5,5.5,11.5)] if frame['depth']==36 else [
        (-h+6.5,h-6.5,-17.5,-11.5),(-h+6.5,h-6.5,11.5,17.5)]
    for rect in corridors:
        assert rect[3]-rect[2]==6
        for p in columns(parts):assert not overlaps(p,rect),(frame['width'],frame['depth'],rect,p)


def assert_portal_unstriped(frame,parts):
    front=frame['frontY'];entry=frame['entryX']
    corridor=(entry-3,entry+3,front,front+6.5)
    markings=[p for p in parts if p['name'] in {'Fixed parking stall stripe','Parking row head'}]
    assert len(markings)>100
    ground=[p for p in markings if p['lo'][2]<frame['datums'][0]+.02]
    assert len(ground)>20, 'Keep actual ground parking outside the entrance reserve'
    for p in ground:assert not overlaps(p,corridor),(frame['width'],corridor,p)
    assert any(overlaps(p,corridor) for p in markings if p not in ground), 'The reserve is ground-only'


@pytest.mark.parametrize('width,depth,levels,courtyard',VARIANTS)
def test_actual_columns_preserve_six_metre_transverse_routes(monkeypatch,width,depth,levels,courtyard):
    frame,parts=record_frame(monkeypatch,width,depth,levels,courtyard)
    assert_transverse_clear(frame,parts)


@pytest.mark.parametrize('width,depth,levels,courtyard',VARIANTS)
def test_actual_columns_and_stripes_leave_both_six_metre_side_routes(monkeypatch,width,depth,levels,courtyard):
    frame,parts=record_frame(monkeypatch,width,depth,levels,courtyard)
    h=width/2
    obstacles=columns(parts)+[p for p in parts if p['name'] in {'Fixed parking stall stripe','Parking row head'}]
    for a,b in [(-h+.5,-h+6.5),(h-6.5,h-.5)]:
        rect=(a,b,frame['frontY']+6.7,frame['rearY']-.5)
        assert b-a==6
        for p in obstacles:assert not overlaps(p,rect),(width,depth,rect,p)


@pytest.mark.parametrize('width,depth,levels,courtyard',VARIANTS)
def test_actual_ground_portal_has_no_backing_parking_bay(monkeypatch,width,depth,levels,courtyard):
    frame,parts=record_frame(monkeypatch,width,depth,levels,courtyard)
    assert_portal_unstriped(frame,parts)


def test_actual_courtyard_decks_and_columns_leave_a_real_open_court(monkeypatch):
    frame,parts=record_frame(monkeypatch,64,48,4,(-8,8,-7,7))
    for p in parts:
        if p['name'] in {'Ground slab','Open-well parking deck'} or p in columns(parts):
            assert not overlaps(p,(-8,8,-7,7)),p
    for z in frame['datums'][1:]:
        floors=[p for p in parts if p['module']=='floor structure' and abs(p['hi'][2]-z)<EPS]
        for sign in (-1,1):
            for x in (26.9,27.1,27.2,27.3):
                assert any(p['lo'][0]-EPS<=sign*x<=p['hi'][0]+EPS and
                    p['lo'][1]<frame['frontY']+1<p['hi'][1] for p in floors),(z,sign*x)
