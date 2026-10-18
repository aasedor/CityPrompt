"""Green Terraces signature on the native shared four-level parking frame.

Original CAD source authority lives in green_sources.py and the reviewed
external green-cad-sources package. No frame stretching or source rendering.
"""
from __future__ import annotations
import math
try:
    from .green_sources import DESIGN, garden_beds, terrace_segments
except ImportError:
    from green_sources import DESIGN, garden_beds, terrace_segments

SPEC = dict(key='green', slug='parkade-green-terraces', label='Green Terraces Parkade',
    width=60, depth=40, frameDepth=36, levels=4, height=12.8, courtyard=None,
    description='Stepped planted front ledges, rooted climbing screens and a separate protected rooftop garden.',
    marking_exclusions=[dict(rect=[-10.8,10.8,-5.5,5.5],levels=[3])],
    garden_reserves=[dict(rect=[-10.8,10.8,-5.5,5.5],levels=[3],
        programme='pedestrian roof garden; open north/south gates; no vehicle bays')],
    source_directory='green-cad-sources-v002',
    source_authority='Original metric CAD front/top/section; schematic oblique/foliage symbols',
    palette=dict(planter=(.33,.40,.28),foliage=(.20,.34,.19),soil=(.22,.19,.12),timber=(.40,.31,.20)))


def _leaf(C, name, base, angle, length=.27, rise=.07):
    """A closed eight-triangle leaf; no alpha cards or spherical crown proxies."""
    x,y,z=base;c,s=math.cos(angle),math.sin(angle)
    along=(length*c,length*s,rise)
    side=(-s*length*.24,c*length*.24,0)
    tip=(x+along[0],y+along[1],z+along[2])
    mid=(x+along[0]*.5,y+along[1]*.5,z+rise*.5)
    vertices=[base,(mid[0]+side[0],mid[1]+side[1],mid[2]),tip,
        (mid[0]-side[0],mid[1]-side[1],mid[2]),
        (mid[0],mid[1],mid[2]+.014),(mid[0],mid[1],mid[2]-.008)]
    faces=[(i,(i+1)%4,4) for i in range(4)]+[((i+1)%4,i,5) for i in range(4)]
    C.mesh(name,vertices,faces,'foliage','rooted vegetation')


def _shrub(C, name, x, y, soil, seed=0):
    """Rooted branching shrub, kept inside the planter's reserved silhouette."""
    C.rod(name+' rooted stem',(x,y,soil-.03),(x,y,soil+.53),.017,'timber','rooted vegetation',6)
    for i in range(3):
        angle=seed*.37+i*math.tau/3
        start=(x,y,soil+.14+i*.11)
        tip=(x+.16*math.cos(angle),y+.16*math.sin(angle),soil+.38+i*.07)
        C.rod(name+' branch',start,tip,.011,'timber','rooted vegetation',6)
        for j in range(4):
            a=angle+(j-1.5)*.9
            root=(x+.06*math.cos(angle),y+.06*math.sin(angle),soil+.26+i*.12+j*.012)
            _leaf(C,name+' physical leaf',root,a,.22+.025*((seed+i+j)%3),.05+.012*j)


def _trough(C, name, rect, z, plant=True, seed=0):
    a,b,c,d=rect;w=b-a;depth=d-c
    C.box(name+' bearing tray',((a+b)/2,(c+d)/2,z-.05),(w,depth,.14),'planter','planted ledges',0)
    for y in (c+.06,d-.06):
        C.box(name+' long planter wall',((a+b)/2,y,z+.27),(w,.12,.5),'planter','planted ledges',0)
    for x in (a+.06,b-.06):
        C.box(name+' returned planter end',(x,(c+d)/2,z+.27),(.12,depth-.24,.5),'planter','planted ledges',0)
    C.box(name+' contained soil',((a+b)/2,(c+d)/2,z+.30),(w-.25,depth-.25,.20),'soil','rooted vegetation',0)
    if plant:
        columns=max(1,int((w-.4)/.75));rows=max(1,int((depth-.4)/.85))
        for i in range(columns):
            for j in range(rows):
                x=a+.35+(w-.7)*(i+.5)/columns
                y=c+.32+(depth-.64)*(j+.5)/rows
                _shrub(C,name,x,y,z+.40,seed+i*3+j)


def _rail(C,name,a,b,height=1.1):
    for rise in (.35,.7,height):
        C.beam(name+' horizontal',(a[0],a[1],a[2]+rise),(b[0],b[1],b[2]+rise),.04,.04,'steel','garden separation')
    n=max(1,math.ceil(math.dist(a,b)/1.5))
    for i in range(n+1):
        p=tuple(a[k]+(b[k]-a[k])*i/n for k in range(3))
        C.beam(name+' post',p,(p[0],p[1],p[2]+height),.05,.05,'steel','garden separation')


def extra_geometry(ctx, *, core=None):
    """Called after standard_frame; all positions are fixed author-space metres."""
    if core is None:
        import clay_core as core
    C=core
    assert ctx['width']==60 and ctx['depth']==36 and ctx['levels']==4
    assert all(math.isclose(a,b,abs_tol=1e-7) for a,b in zip(ctx['datums'],DESIGN['datums']))
    roof=ctx['top']
    # Cantilevered ledges have a concrete-frame ledger, diagonal brackets,
    # returned soil-containing troughs and genuinely rooted leaf geometry.
    for index,p in enumerate(terrace_segments()):
        rect=(p['x0'],p['x1'],p['y0'],p['y1']);z=ctx['datums'][p['level']]
        name=f'Green terrace L{p["level"]+1} segment {index%3+1}'
        _trough(C,name,rect,z,seed=index)
        C.box(name+' seated back ledger',((p['x0']+p['x1'])/2,-17.83,z-.26),
            (p['x1']-p['x0'],.18,.22),'steel','terrace support',0)
        count=max(2,math.ceil((p['x1']-p['x0'])/3))
        for i in range(count):
            x=p['x0']+.35+(p['x1']-p['x0']-.7)*i/(count-1)
            # The lower diagonal anchor is below the concrete beam soffit.
            # Its steel mounting plate rises through the back ledger and
            # overlaps the real beam, giving that anchor a continuous owner.
            C.box(name+' vertical mounting plate',(x,-17.8,z-.55),
                (.22,.16,.90),'steel','terrace support',0)
            C.beam(name+' bracket diagonal',(x,-17.8,z-.9),(x,p['y0']+.12,z-.12),.095,.095,'steel','terrace support')
            C.beam(name+' horizontal bearing',(x,p['y0']+.12,z-.12),(x,-17.65,z-.12),.10,.10,'steel','terrace support')
    # Root beds and steel climbing mesh stand outside the structural frontage.
    # Their three positions avoid the entrance bay and both stair-tower doors.
    for index,cx in enumerate(DESIGN['screen_centres']):
        _trough(C,f'Climber root planter {index+1}',(cx-1.1,cx+1.1,-18.65,-18.10),.12,plant=False)
        for x in (cx-1.,cx+1.):
            C.box('Grounded climbing screen post',(x,-18.18,5.55),(.07,.07,10.8),'steel','climbing screen',0)
        for i in range(20):
            z=.7+i*.51
            C.beam('Open climbing mesh horizontal',(cx-1.,-18.18,z),(cx+1.,-18.18,z),.018,.018,'steel','climbing screen')
        for dx in (-.5,0,.5):
            C.beam('Open climbing mesh vertical',(cx+dx,-18.18,.7),(cx+dx,-18.18,10.9),.018,.018,'steel','climbing screen')
        for z in ctx['datums'][1:]:
            for dx in (-1.,1.):
                C.beam('Climbing mesh frame anchor',(cx+dx,-17.7,z-.3),(cx+dx,-18.18,z-.3),.055,.055,'steel','climbing screen')
        for stem in (-.42,.42):
            previous=(cx+stem,-18.34,.53)
            for i in range(22):
                z=.65+i*.46;x=cx+stem+math.sin(i*.87)*.24;y=-18.25-.03*math.cos(i)
                tip=(x,y,z)
                C.rod('Rooted climbing woody vine',previous,tip,.014,'timber','climbing plants',6)
                for j in range(2):_leaf(C,'Climbing leaf',(x,y,z),math.pi*(j+.18)+i*.29,.25,.09)
                previous=tip
    # Rear planted grade edges complete the full 40 m occupied depth without
    # occupying either ramp end landing or the continuous six-metre ramp lane.
    for index,rect in enumerate(DESIGN['ground_rear_planters']):
        _trough(C,f'Rear ground planter {index+1}',rect,.12,seed=30+index)

    # Distinct pedestrian roof garden: level finish, protected vehicle edges,
    # real soil beds, open north/south gates and a cross-shaped clear route.
    a,b,c,d=DESIGN['garden']
    C.box('Separate roof garden level finish',((a+b)/2,(c+d)/2,roof+.0125),
        (b-a,d-c,.025),'accent','roof garden floor',0)
    for x in (a,b):_rail(C,'Garden motor separation',(x,c,roof),(x,d,roof))
    for y in (c,d):
        for x0,x1 in [(a,-1.5),(1.5,b)]:_rail(C,'Garden motor separation',(x0,y,roof),(x1,y,roof))
    for index,rect in enumerate(garden_beds()):
        _trough(C,f'Roof garden bed {index+1}',rect,roof,seed=50+index)
    for x in (-3.3,3.3):
        for y in (-1.7,1.7):
            C.box('Garden timber bench seat',(x,y,roof+.47),(2.2,.5,.09),'timber','roof garden furniture',0)
            C.box('Garden timber bench back',(x,y+(.23 if y>0 else -.23),roof+.76),
                (2.2,.055,.55),'timber','roof garden furniture',0)
            for dx in (-.8,.8):
                C.box('Bench seated steel leg',(x+dx,y,roof+.22),(.065,.38,.44),'steel','roof garden furniture',0)
    # Timber pergola sits below the 12.8 m tower caps and keeps the full
    # 3 m north/south path plus 2.4 m east/west route free of posts or furniture.
    for x in (-5.,5.):
        for y in (-1.7,1.7):
            C.box('Pergola seated post',(x,y,(roof+12.4)/2),(.12,.12,12.4-roof),'timber','garden pergola',0)
            C.box('Pergola steel base shoe',(x,y,roof+.04),(.16,.16,.08),'steel','garden pergola',0)
    for y in (-1.7,1.7):C.box('Pergola longitudinal bearing',(0,y,12.35),(10.2,.14,.18),'timber','garden pergola',0)
    for i in range(11):C.box('Pergola open slat',(-5+i,0,12.475),(.08,3.6,.15),'timber','garden pergola',0)
