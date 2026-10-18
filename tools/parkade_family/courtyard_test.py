"""Spatial regression checks for fixed courtyard reserves and physical contacts."""
import math
import sys
from . import family_courtyard as F


class Recorder:
    def __init__(self):
        self.parts=[];self.OPENINGS=[]

    def box(self,name,loc,size,role,module,soft=0):
        assert min(size)>0
        self.parts.append(dict(name=name,kind='box',lo=tuple(a-b/2 for a,b in zip(loc,size)),
                               hi=tuple(a+b/2 for a,b in zip(loc,size)),role=role,module=module))

    def beam(self,name,a,b,width,depth=None,role='steel',module='detail'):
        assert math.dist(a,b)>0
        self.parts.append(dict(name=name,kind='linear',a=a,b=b,width=width,role=role,module=module))

    def rod(self,name,a,b,r,role,module,sides=12):
        assert math.dist(a,b)>0
        self.parts.append(dict(name=name,kind='linear',a=a,b=b,width=2*r,role=role,module=module))

    def mesh(self,name,vertices,faces,role,module):
        assert all(len(f)>=3 and max(f)<len(vertices) for f in faces)
        self.parts.append(dict(name=name,kind='mesh',vertices=vertices,faces=faces,role=role,module=module))


def recorded(monkeypatch):
    r=Recorder();monkeypatch.setitem(sys.modules,'clay_core',r)
    F.extra_geometry(dict(width=64,depth=48,levels=4,datums=(.15,3.45,6.75,10.05),top=10.05,
                         towerHeight=12.8,frontY=-24,rearY=24,rampY=(17.55,23.95),rampX=(-25,25)))
    return r


def test_fixed_native_contract_and_unstriped_ground_program():
    assert (F.SPEC['width'],F.SPEC['depth'],F.SPEC['levels'])==(64,48,4)
    assert F.SPEC['courtyard']==(-8,8,-7,7)
    assert F.CAFE in F.SPEC['marking_exclusions'] and F.BIKE_HUB in F.SPEC['marking_exclusions']
    assert not any(a<-21<b and c<-23<d for a,b,c,d in F.SPEC['marking_exclusions'])


def test_court_has_real_root_openings_and_full_ground_partition():
    panels=F.court_paving_panels()
    assert sum((b-a)*(d-c) for a,b,c,d in panels)+sum((b-a)*(d-c) for a,b,c,d in F.SOIL_WELLS)==16*14
    for a,b,c,d in F.SOIL_WELLS:
        x,y=(a+b)/2,(c+d)/2
        assert not any(p<x<q and r<y<s for p,q,r,s in panels)
    # Two independent, four metre wide through walking axes remain paved.
    for x,y in ((0,-6.5),(0,6.5),(-7.5,0),(7.5,0),(0,0)):
        assert any(a<x<b and c<y<d for a,b,c,d in panels)


def test_extra_geometry_stays_inside_native_envelope_and_rear_lane(monkeypatch):
    r=recorded(monkeypatch)
    for p in r.parts:
        if p['kind']=='box':points=(p['lo'],p['hi'])
        elif p['kind']=='mesh':points=p['vertices']
        else:points=(p['a'],p['b'])
        for x,y,z in points:
            assert -32<=x<=32 and -24<=y<=24 and 0<=z<=12.8,p['name']
            assert y<17.5,p['name']


def test_court_upper_void_and_root_contacts(monkeypatch):
    r=recorded(monkeypatch)
    for p in r.parts:
        if p['kind']=='box' and p['module']!='courtyard planting' and p['hi'][2]>.151:
            a,c,_=p['lo'];b,d,_=p['hi']
            assert not (a<7.999 and b>-7.999 and c<6.999 and d>-6.999),p['name']
    trunks=[p for p in r.parts if p['name']=='Tree trunk rooted in soil']
    assert len(trunks)==4
    for p in trunks:
        x,y,z=p['a'];assert z<.15
        assert any(a<x<b and c<y<d for a,b,c,d in F.SOIL_WELLS)
    for p in r.parts:
        if p['name']=='Court corner ground-bearing column':assert abs(p['lo'][2]-.15)<1e-9


def test_cafe_has_actual_clear_door_and_no_glass_over_structural_piers(monkeypatch):
    r=recorded(monkeypatch)
    assert r.OPENINGS[0]['width']>=1.5
    assert r.OPENINGS[0]['u']==0 and r.OPENINGS[0]['z']==.15
    assert r.OPENINGS[0]['face_origin']==[-1.4,-23.83,0]
    for p in r.parts:
        if p['name']=='Cafe recessed optical storefront':
            assert p['hi'][2]<=2.8
            assert not any(p['lo'][0]<x+.25 and p['hi'][0]>x-.25 for x in (-12,-6,0))
        if p['kind']=='box' and p['module']=='cafe glazing':
            assert not (p['lo'][0]<-1.5 and p['hi'][0]>-1.3 and p['lo'][2]<2.7),p['name']
    assert any(p['name']=='Cafe service counter body' for p in r.parts)
    assert len([p for p in r.parts if p['name']=='Cafe chair seat'])==4


def test_cycle_hoops_have_ground_contacts_and_bikes_have_open_wheels(monkeypatch):
    r=recorded(monkeypatch)
    roof=next(p for p in r.parts if p['name']=='Bicycle hub shelter roof')
    for p in r.parts:
        if p['name']=='Bicycle canopy seated post':
            assert abs(p['lo'][2]-.15)<1e-8
            assert abs(p['hi'][2]-roof['lo'][2])<1e-8
    feet=[p for p in r.parts if p['name']=='Grounded inverted U cycle hoop' and min(p['a'][2],p['b'][2])==.15]
    assert len(feet)==14
    assert len([p for p in r.parts if p['name']=='Bicycle open wheel tyre'])==72
    assert len([p for p in r.parts if p['name']=='Bicycle physical triangle frame'])==18


def test_screen_fins_have_clear_gaps_and_supported_ends(monkeypatch):
    r=recorded(monkeypatch)
    fins=[p for p in r.parts if p['name']=='Permeable front coloured fin']
    assert len(fins)==3*len(F.front_fins())
    assert set(p['role'] for p in fins)==set(F.SCREEN_ROLES)
    for p in fins:
        assert abs(p['hi'][0]-p['lo'][0]-.15)<1e-8
        assert abs(p['lo'][1]+23.92)<1e-8
        assert p['hi'][2]<=11.65+1e-8
    for z in (3.45,6.75,10.05):
        xs=sorted(p['lo'][0] for p in fins if abs(p['lo'][2]-z-.18)<1e-8)
        assert min(b-a for a,b in zip(xs,xs[1:]))>.6
