"""Exact-source RLASM architectural-clay candidates; no catalogue installation.

Blender 5.2 --background --python build.py -- --kind office --source-root ...
  --output C:/dev-artifacts/CityPrompt/.../office-v001 [--dry-run]
"""
import argparse
import math
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.append(str(HERE.parent/'catalogue_services_batch'))
import clay_core as C
sys.path.append(str(HERE.parent/'catalogue_runtime_preparation'))
from guards import seated_guard
from plan import SPECS, source_entry

PALETTE=dict(wall=(.40,.21,.14),buff=(.55,.45,.31),trim=(.68,.61,.47),
    timber=(.45,.26,.12),roof=(.29,.31,.31),foundation=(.45,.43,.38),
    glass=(.34,.39,.40),hardware=(.08,.095,.095),interior=(.64,.59,.49),
    floor=(.49,.42,.31),joint=(.29,.18,.13),copper=(.43,.28,.17),
    planting=(.19,.25,.12),dark=(.10,.12,.13))

def cameras(kind):
    h=8 if kind in ('office','school') else 5.5
    roster=[('front',(0,-65,12),(0,0,h)),('front_corner',(43,-55,29),(0,0,h)),
        ('aerial',(41,-49,61),(0,0,5)),('top',(0,0,90),(0,.001,0)),
        ('left_side',(-65,0,13),(0,0,h)),('right_side',(65,0,13),(0,0,h)),
        ('rear',(0,65,13),(0,0,h)),('rear_side',(-45,53,31),(0,0,h))]
    if kind=='office':
        detail=[('facade_close',(25,-39,17),(4,-14,6)),
            ('architecture_close',(10,-25,6),(0,-15,4)),('glass_close',(12,-19,4),(10.2,-14,3)),
            ('roof_contact',(23,-23,23),(1,-4,15)),('side_projection',(27,-10,11),(14,-4,7)),
            ('cupola_close',(8,-9,20),(0,0,17.7)),('interior',(0,-11,2.1),(0,8,2.5)),
            ('stair_contact',(-5,0,4),(0,4.5,3.2)),
            ('stair_top',(0,-.5,8),(.6,2.3,5.5))]
    elif kind=='row':
        roster=[(n,tuple(v*.72 for v in loc),tar) for n,loc,tar in roster]
        detail=[('facade_close',(21,-23,12),(5,-6.5,5)),
            ('architecture_close',(1,-14,3),(-1.8,-7,1.5)),('glass_close',(11,-12,5),(9,-6.5,5.2)),
            ('roof_contact',(18,-13,18),(8,0,11)),('side_projection',(22,-4,10),(12,0,6)),
            ('roof_stair',(8.9,3.85,11.7),(7.9,-.7,9.5)),('roof_exit',(9.05,1.7,11.2),(8.1,-2.65,10.6)),
            ('roof_arrival',(8.65,.5,11.2),(7.5,3.0,9.8)),
            ('interior',(8,-5.9,2),(8,4,2))]
    elif kind=='school':
        roster=[(n,tuple(v*1.15 for v in loc),tar) for n,loc,tar in roster]
        detail=[('facade_close',(29,-41,19),(2,-20,6)),
            ('architecture_close',(9,-30,6),(0,-20,4)),('glass_close',(18,-26,8),(12.5,-20,7)),
            ('roof_contact',(24,-27,21),(12.5,-18,13)),('side_projection',(31,-5,16),(16,0,8)),
            ('courtyard',(0,-12.5,6),(0,9.8,6)),('clock_close',(8,-27,22),(0,-17,17)),
            ('classroom',(14,-17,2),(13,-8,2)),
            ('school_stair',(15,9.5,2.8),(12.5,14.8,3.6)),
            ('school_stair_top',(14,11,9.7),(12.5,13.3,7.9)),
            ('rear_roof_contact',(24,28,23),(10,15,13))]
    else: raise ValueError(kind)
    return [dict(name=n,location=l,target=t,**({'ortho_scale':42} if n=='top' else {})) for n,l,t in roster]+[
        dict(name=n,location=l,target=t,whole=False,lens=24 if n in ('stair_contact','roof_stair','roof_arrival','school_stair','school_stair_top') else 42) for n,l,t in detail]

def manifest(kind,version):
    s=SPECS[kind];cams=cameras(kind)
    return dict(candidate=f'{s["title"]}-clay-v{version:03d}',method=C.METHOD,
        representation_kind='architectural_clay',archetype_id=s['parent'],variant_id=s['variant'],
        state='prework',keeper_claimed=False,runtime_seed_allowed=False,
        measurement_contract=dict(dimensions_m=s['dimensions'],observed_storeys=s['floors'],
            source_measurements=s['measurements'],hidden_assumptions=s['assumptions']),
        roof_contract=dict(authority='top for plan; front/oblique for vertical datums; closed physical roof surfaces'),
        identity_contract=dict(owner='physical envelope, bays, cornices, openings, stairs and railings',bitmap_stickers='none in clay stage'),
        material_contract=dict(profile='source-palette semantic architectural clay, no textures',
            limitations='Not source-conditioned PBR or textured keeper approval.'),
        programme_contract=dict(storeys=s['floors'],interiors='Conceptual occupied rooms and connected circulation; not surveyed'),
        contact_contract=['Foundations at grade zero.', 'Real carrier openings, inset frames and rooms.',
            'Roof surfaces, cupola, canopies and stairs physically seated.'],
        runtime_contract=dict(scale='fixed_native_only',translation=True,rotation=True,resizing=False,
            terrain='not tested',installation='not installed',review='not tested'),
        camera_roster=cams,mandatory_review_views=[c['name'] for c in cams])

def cleanup():
    for obj in C.objects():
        bm=C.bmesh.new();bm.from_mesh(obj.data);C.bmesh.ops.triangulate(bm,faces=list(bm.faces))
        C.bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<=1e-10],context='FACES_ONLY')
        bm.to_mesh(obj.data);bm.free();obj.data.update()

def cylinder(name,x,y,z,r,h,role='trim',sides=24,r2=None):
    r2=r if r2 is None else r2
    vs=[(x+rr*math.cos(i*math.tau/sides),y+rr*math.sin(i*math.tau/sides),zz)
        for rr,zz in ((r,z),(r2,z+h)) for i in range(sides)]
    fs=[tuple(range(sides-1,-1,-1)),tuple(range(sides,sides*2))]+[
        (i,(i+1)%sides,(i+1)%sides+sides,i+sides) for i in range(sides)]
    return C.mesh(name,vs,fs,role,'turned construction')

def dome(name,x,y,z,r,h,role='copper',sides=48,rings=12):
    vs=[]
    for j in range(rings):
        a=j/rings*math.pi/2
        vs.extend((x+r*math.cos(a)*math.cos(i*math.tau/sides),y+r*math.cos(a)*math.sin(i*math.tau/sides),z+h*math.sin(a)) for i in range(sides))
    vs.append((x,y,z+h));top=len(vs)-1
    fs=[tuple(range(sides-1,-1,-1))]
    for j in range(rings-1):
        for i in range(sides):fs.append((j*sides+i,j*sides+(i+1)%sides,(j+1)*sides+(i+1)%sides,(j+1)*sides+i))
    fs.extend(((rings-1)*sides+i,(rings-1)*sides+(i+1)%sides,top) for i in range(sides))
    return C.mesh(name,vs,fs,role,'cupola dome')

def trim_opening(f,h):
    u,z,w,hh=h['u'],h['z'],h['w'],h['h']
    for side in (-1,1):f.part('Stone reveal',u+side*(w/2+.07),-.025,z+hh/2,.14,.19,hh+.25,'trim','stone surrounds')
    f.part('Stone lintel',u,-.03,z+hh+.08,w+.3,.2,.16,'trim','stone surrounds')
    f.part('Stone keystone',u,-.075,z+hh+.16,.24,.25,.32,'trim','stone surrounds')

def desk(x,y,z,role='office'):
    C.box('Desk top',(x,y,z+.79),(1.65,.78,.08),'timber',role)
    for dx in (-.70,.70):C.box('Desk support',(x+dx,y,z+.39),(.08,.70,.74),'hardware',role)
    C.box('Desk monitor',(x,y+.15,z+1.05),(.55,.045,.34),'dark',role)
    C.box('Desk monitor foot',(x,y+.15,z+.85),(.24,.18,.04),'hardware',role)
    C.box('Seat',(x,y-.8,z+.45),(.49,.48,.07),'timber',role)
    C.box('Chair back',(x,y-1,z+.69),(.49,.055,.48),'timber',role)
    for dx in (-.18,.18):
        for dy in (-.98,-.62):C.box('Chair leg',(x+dx,y+dy,z+.21),(.045,.045,.42),'hardware',role,0)

def office():
    C.box('Building foundation',(0,0,.20),(28,28,.40),'foundation','foundation',0)
    faces=[C.Face((0,-14,0),(1,0,0),(0,1,0),'front'),C.Face((0,14,0),(-1,0,0),(0,-1,0),'rear'),
        C.Face((-14,0,0),(0,-1,0),(1,0,0),'left'),C.Face((14,0,0),(0,1,0),(-1,0,0),'right')]
    for f in faces:
        cols=[-11.65,-8.95,-6.25,6.25,8.95,11.65] if f.label=='front' else [-11,-6.6,-2.2,2.2,6.6,11]
        holes=[dict(id=f'{f.label} {floor} {i}',u=u,z=z,w=1.35,h=3.1) for floor,z in enumerate((.95,6.2)) for i,u in enumerate(cols)]
        if f.label=='front':
            holes += [dict(id='Entrance',u=0,z=.4,w=2.6,h=3.65)]
            holes += [dict(id=f'Portico upper {u}',u=u,z=6.2,w=1.2,h=3.1) for u in (-2.6,0,2.6)]
        if f.label=='rear':holes += [dict(id='Rear service door',u=0,z=.4,w=1.1,h=2.35)]
        f.wall(f.label+' brick carrier',-14,14,.4,10.75,depth=.32,holes=holes)
        for h in holes:
            if 'Entrance' in h['id']:
                f.door(h['id'],h['u'],h['z'],h['w'],2.82,panels=4,panel_cols=2)
                f.window('Entrance transom',0,3.22,2.6,.83,cols=4,rows=1,frame='trim',bar=.025,sill=False)
            elif 'service' in h['id']:f.door(h['id'],h['u'],h['z'],h['w'],h['h'])
            else:f.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=3,rows=5,frame='trim',bar=.025,depth=.32)
            trim_opening(f,h)
        for z,ht,thick in [(.60,.32,.20),(5.42,.23,.19),(10.12,.26,.25),(10.53,.38,.32),(10.88,.18,.5),(11.04,.16,.62)]:
            f.part('Continuous limestone course',0,-thick/2,z,28+.12,thick,ht,'trim','cornices')
        for u in (-13.60,13.60):
            for i in range(19):f.part('Alternating corner quoin',u,-.07,.7+i*.52,.8 if i%2==0 else .55,.18,.43,'trim','corner quoins')
        for i in range(70):f.part('Cornice dentil',-13.65+i*.395,-.30,10.66,.13,.22,.18,'trim','cornice dentils',0)
    # Floor plates remain distinct and open at the actual stairwell.
    for z in (.4,5.6):
        slab=C.box('Occupied floor',(0,0,z+.09),(27.36,27.36,.18),'floor','floors',0)
        if z>1:C.cut_box(slab,'Stair opening',(0,5,z),(3.4,6.8,1))
    C.box('Top floor ceiling',(0,0,10.74),(27.36,27.36,.12),'interior','ceiling',0)
    for level in (0,1):
        C.qa_room_light(f'office floor {level}',(0,-3,4.9+level*5.2),1100,9)
        C.qa_room_light(f'office stair {level}',(0,6,4.8+level*5.2),450,4)
        for x in (-10,-6,6,10):
            for y in (-10,-5,1,7):desk(x,y,.58+level*5.2)
    # Connected two-flight internal stair, clear landing, no plate through the route.
    for i in range(13):
        C.box('Stair first flight',(-.9,2+i*.26,.51+(i+1)*.20),(1.3,.30,.14),'trim','internal stair')
        C.box('Stair return flight',(.9,5.12-i*.26,3.11+(i+1)*.20),(1.3,.30,.14),'trim','internal stair')
    C.box('Stair landing',(0,5.6,3.11),(3.2,1,.14),'trim','internal stair')
    C.box('Upper floor stair landing',(.9,1.75,5.69),(1.3,.50,.18),'floor','internal stair',0)
    for x in (-1.49,-.31):C.beam('First stair stringer',(x,1.85,.57),(x,5.3,3.10),.12,.22,'trim','internal stair support')
    for x in (.31,1.49):C.beam('Return stair stringer',(x,5.27,3.12),(x,1.85,5.70),.12,.22,'trim','internal stair support')
    for x in (-1.49,1.49):C.box('Stair landing support',(x,5.6,1.76),(.14,.14,2.36),'trim','internal stair support')
    for x,ys,zs,ye,ze in [(-1.52,1.85,.58,5.3,3.18),(-.28,1.85,.58,5.3,3.18),
            (1.52,5.3,3.18,1.85,5.78),(.28,5.3,3.18,1.85,5.78)]:
        C.beam('Stair handrail',(x,ys,zs+.95),(x,ye,ze+.95),.045,.045,'hardware','stair rails')
        for t in (0,.33,.66,1):
            y=ys+(ye-ys)*t;z=zs+(ze-zs)*t
            C.rod('Stair rail post',(x,y,z),(x,y,z+.95),.022,'hardware','stair rails',10)
    for x in (-1.79,1.79):seated_guard('Stairwell guard',(x,1.51,5.78),(x,8.49,5.78),role='hardware')
    seated_guard('Landing rear guard',(-1.52,6.02,3.18),(1.52,6.02,3.18),role='hardware')
    seated_guard('Upper well back guard',(-1.79,8.49,5.78),(1.79,8.49,5.78),role='hardware')
    seated_guard('Upper well front guard',(-1.79,1.51,5.78),(.20,1.51,5.78),role='hardware')
    # Four full-height columns, seated bases, conservative Corinthian capital relief.
    C.box('Portico landing',(0,-15.4,.2),(10.2,2.8,.4),'trim','portico',0)
    for i in range(3):C.box('Entrance step',(0,-17.08+i*.30,.067*(i+1)),(9.6,.64,.134*(i+1)),'trim','entrance steps')
    for x in (-4.15,-1.38,1.38,4.15):
        C.box('Column plinth',(x,-15.7,.55),(.9,.9,.30),'trim','columns')
        cylinder('Column base',x,-15.7,.70,.48,.20)
        cylinder('Tapered column shaft',x,-15.7,.90,.35,8.5,r2=.30)
        for a in range(16):
            ang=a*math.tau/16
            C.rod('Column flute',(x+.347*math.cos(ang),-15.7+.347*math.sin(ang),1.1),
                (x+.30*math.cos(ang),-15.7+.30*math.sin(ang),9.27),.018,'trim','column flutes',8)
        cylinder('Capital neck',x,-15.7,9.4,.34,.16)
        cylinder('Capital bell',x,-15.7,9.56,.37,.4,r2=.48)
        for a in range(8):
            ang=a*math.tau/8
            C.rod('Capital leaf',(x+.32*math.cos(ang),-15.7+.32*math.sin(ang),9.5),
                (x+.49*math.cos(ang),-15.7+.49*math.sin(ang),9.85),.085,'trim','capital relief',8)
        C.box('Capital abacus',(x,-15.7,10.02),(1.0,1.0,.20),'trim','columns')
    C.box('Portico entablature',(0,-15.25,10.55),(10.0,2.6,.86),'trim','portico')
    f=faces[0]
    for x in (-1.57,1.57):f.part('Entrance pilaster',x,-.20,2.42,.40,.42,4.04,'trim','door surround')
    f.part('Entrance entablature',0,-.20,4.47,3.65,.44,.32,'trim','door surround')
    f.panel('Entrance small pediment',[(-1.95,4.63),(1.95,4.63),(0,5.76)],-.48,-.12,'trim','door pediment')
    for x in (-1.95,1.95):C.beam('Entrance pediment moulding',f.p(x,-.5,4.64),f.p(0,-.5,5.78),.13,.14,'trim','door pediment')
    C.prism('Pediment tympanum',[(-5,10.98),(5,10.98),(0,14.0)],'y',-16.58,-16.22,'trim','pediment')
    for x in (-1,1):
        C.beam('Pediment raking cornice',(x*5.1,-16.66,10.96),(0,-16.66,14.05),.25,.28,'trim','pediment')
    valley_y=-14.4+(14.13-11.16)/(14.25-11.16)*5.8
    C.solid_surface('Portico left roof',[(-5.1,-16.65,11.16),(0,-16.65,14.13),(0,valley_y,14.13),(-5.1,-14.4,11.16)],.18)
    C.solid_surface('Portico right roof',[(0,-16.65,14.13),(5.1,-16.65,11.16),(5.1,-14.4,11.16),(0,valley_y,14.13)],.18)
    # Single truncated hip surrounding a flat terrace; corners meet without overlap.
    outside=[(-14.4,-14.4,11.16),(14.4,-14.4,11.16),(14.4,14.4,11.16),(-14.4,14.4,11.16)]
    inside=[(-8.6,-8.6,14.25),(8.6,-8.6,14.25),(8.6,8.6,14.25),(-8.6,8.6,14.25)]
    for i in range(4):
        outline=[outside[i],outside[(i+1)%4],inside[(i+1)%4],inside[i]]
        if i==0:outline=[outside[0],(-5.1,-14.4,11.16),(0,valley_y,14.13),(5.1,-14.4,11.16),outside[1],inside[1],inside[0]]
        C.solid_surface('Main hip slope '+str(i),outline,.18)
    for x in (-5.1,5.1):C.beam('Portico bounded valley flashing',(x,-14.4,11.18),(0,valley_y,14.15),.06,.035,'roof','roof junction')
    C.box('Roof terrace',(0,0,14.16),(17.3,17.3,.18),'trim','roof terrace',0)
    for a,b in zip(inside,inside[1:]+inside[:1]):
        aa=C.Vector(a);bb=C.Vector(b)
        C.beam('Terrace balustrade base',aa+C.Vector((0,0,.13)),bb+C.Vector((0,0,.13)),.36,.26,'trim','terrace parapet')
        C.beam('Terrace balustrade handrail',aa+C.Vector((0,0,.98)),bb+C.Vector((0,0,.98)),.34,.18,'trim','terrace parapet')
        for i in range(5):
            p=aa.lerp(bb,i/4)
            C.box('Stone balustrade pier',(p.x,p.y,p.z+.58),(.44,.44,1.08),'trim','terrace piers')
            C.box('Stone pier cap',(p.x,p.y,p.z+1.15),(.54,.54,.12),'trim','terrace piers')
        for i in range(1,54):
            t=i/54
            if min(abs(t-j/4) for j in range(5))*17.2<.30:continue
            p=aa.lerp(bb,t);profile=[(.24,.075),(.30,.095),(.43,.075),(.56,.049),(.78,.045),(.88,.075)]
            vs=[(p.x+r*math.cos(k*math.tau/8),p.y+r*math.sin(k*math.tau/8),p.z+z) for z,r in profile for k in range(8)]
            fs=[tuple(range(7,-1,-1)),tuple(range(40,48))]+[(j*8+k,j*8+(k+1)%8,(j+1)*8+(k+1)%8,(j+1)*8+k) for j in range(5) for k in range(8)]
            C.mesh('Turned stone baluster',vs,fs,'trim','terrace balusters')
    # Octagonal lantern with cut glazing, supported on a closed plinth.
    cylinder('Cupola brick plinth',0,0,14.25,2.0,.72,'wall',8)
    cylinder('Cupola lower moulding',0,0,14.95,2.08,.18,'trim',8)
    r=1.90; side=2*r*math.sin(math.pi/8);apothem=r*math.cos(math.pi/8)
    for i in range(8):
        a=(i+.5)*math.tau/8;n=(math.cos(a),math.sin(a));t=(-n[1],n[0])
        f=C.Face((n[0]*apothem,n[1]*apothem,0),(t[0],t[1],0),(-n[0],-n[1],0),'cupola '+str(i))
        hh=dict(id='Lantern sash '+str(i),u=0,z=15.45,w=.77,h=2.2)
        f.wall('Lantern pier wall',-side/2,side/2,15.08,18.05,depth=.22,role='trim',holes=[hh])
        arched_sash(f,hh['id'],0,15.45,.77,2.2,'trim',.22)
    cylinder('Cupola cornice',0,0,18.03,2.02,.25,'trim',8)
    dome('Copper dome',0,0,18.27,2.04,1.64)
    for i in range(12):
        a=i*math.tau/12
        for j in range(10):
            p=j/10*math.pi/2;q=(j+1)/10*math.pi/2
            C.beam('Dome raised seam',(2.05*math.cos(p)*math.cos(a),2.05*math.cos(p)*math.sin(a),18.27+1.65*math.sin(p)),
                (2.05*math.cos(q)*math.cos(a),2.05*math.cos(q)*math.sin(a),18.27+1.65*math.sin(q)),.026,.025,'copper','dome seams')
    cylinder('Finial stem',0,0,19.85,.055,1.0,'copper',16)
    dome('Finial ball',0,0,20.23,.17,.22,'copper',24,8)
    # Bounded planting beds, not a private terrain-covering slab.
    for x in (-8.4,8.4):
        C.box('Garden retaining bed',(x,-16.35,.17),(6.5,3.1,.34),'wall','front garden')
        C.box('Clipped garden surface',(x,-16.35,.40),(6.15,2.75,.32),'planting','front garden')
    C.CONTACTS.extend([dict(name='Portico',foundation_z=0,landing_z=.4,column_start_z=.4,column_top_z=10.12),
        dict(name='Cupola',carrier='roof terrace',base_z=14.25),dict(name='Entrances',front=[0,-17.4,0],rear=[0,14,.4])])

def row():
    # The top photograph bounds exactly four foreground units; no background rows.
    C.box('Four-home foundation',(0,0,.22),(24,13,.44),'foundation','foundation',0)
    for i,x in enumerate((-9,-3,3,9)):
        role='wall' if i%2 else 'buff'
        front=C.Face((0,-6.5,0),(1,0,0),(0,1,0),f'home {i+1} front')
        holes=[dict(id='Front door',u=x-1.9,z=.55,w=1.02,h=2.25),
            dict(id='Ground living',u=x+.75,z=1.02,w=2.8,h=1.65),
            dict(id='Middle living',u=x+.35,z=4.05,w=3.15,h=1.75),
            dict(id='Upper living',u=x+.35,z=7.08,w=3.15,h=1.92)]
        if i==3:
            holes[1].update(u=x+1.47,z=.55,h=2.25,w=3.0)
            holes[3].update(u=x+1.47,w=3.0)
        front.wall('Ground unit frontage',x-3,x+3,.44,3.35,depth=.27,role=role,holes=holes)
        front.wall('Projecting middle brick bay',x-1.55,x+3,3.35,6.48,depth=.27,role=role,holes=holes)
        front.wall('Timber upper frontage',x-1.55,x+3,6.48,9.6,depth=.27,role='timber',holes=holes)
        slot=C.Face((0,-6.20,0),(1,0,0),(0,1,0),f'home {i+1} recessed stair slot')
        sh=[dict(id=f'Stair sash {j}',u=x-2.3,z=z,w=.62,h=1.7) for j,z in enumerate((4.15,7.22))]
        slot.wall('Recessed charcoal stair carrier',x-3,x-1.55,3.35,9.6,role='dark',holes=sh)
        for h in sh:slot.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=1,frame='hardware')
        C.box('Stair slot reveal',(x-1.56,-6.35,6.475),(.10,.30,6.25),role,'slot return',0)
        for h in holes:
            if h['id']=='Front door':front.door(h['id'],h['u'],h['z'],h['w'],h['h'],panels=1)
            else:front.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=3,rows=1,frame='hardware',bar=.04)
        # One depth owner for the upper white surround; no frame over glazing.
        for u in ((x-1.58,) if i==3 else (x-1.58,x+2.28)):front.part('Upper pale surround jamb',u,-.12,8.02,.19,.25,2.55,'trim','upper surrounds')
        front.part('Upper pale surround head',x+(.7425 if i==3 else .35),-.12,9.3,4.835 if i==3 else 4.05,.25,.20,'trim','upper surrounds')
        front.part('Upper pale sill',x+(.7425 if i==3 else .35),-.12,6.75,4.835 if i==3 else 4.05,.30,.15,'trim','upper surrounds')
        if i==3:
            C.box('Corner ground canopy front',(10.1,-6.63,3.06),(4.1,.58,.16),'dark','corner canopy')
            C.box('Corner ground canopy return',(12.14,-5.32,3.06),(.58,2.62,.16),'dark','corner canopy')
        front.part('Unit charcoal divider',x-2.95,-.035,1.9,.10,.11,3.0,'dark','vertical joints',0)
        for u in (x-2.62,x-1.18):front.part('Projecting brick entry jamb',u,-.18,1.76,.22,.52,2.42,role,'entry portal')
        front.part('Projecting brick entry head',x-1.9,-.18,3.04,1.66,.52,.24,role,'entry portal')
        front.part('Entry portal coping',x-1.9,-.18,3.2,1.8,.59,.09,'dark','entry portal')
        # Individual stoop with physically connected risers and open rails.
        for j in range(3):C.box('Unit entrance step',(x-1.9,-7.15-j*.30,.092*(3-j)),(1.55,.67,.184*(3-j)),'trim','entrance steps')
        for sign in (-1,1):
            a=(x-1.9+sign*.74,-7.9,.18);b=(x-1.9+sign*.74,-6.7,.55)
            C.beam('Stoop handrail',(a[0],a[1],a[2]+.90),(b[0],b[1],b[2]+.90),.035,.035,'hardware','stoop rails')
            for p in (a,b):C.rod('Stoop rail post',p,(p[0],p[1],p[2]+.90),.021,'hardware','stoop rails',10)
        # Three occupied floors and roof with a real continuous stair void.
        for level,z in enumerate((.44,3.48,6.52,9.56)):
            slab=C.box('Home floor',(x,0,z+.09),(5.96,12.5,.18),'floor' if level<3 else 'roof','floor plates',0)
            if level>0:C.cut_box(slab,'Home stairwell',(x-1.65,.65,z),(1.26,4.5,1))
            if level<3:
                for j in range(20):
                    yy=-1.5+j*.22
                    C.box('Home stair tread',(x-1.65,yy,z+.13+(j+1)*.152),(1.08,.25,.10),'timber','internal stair')
                C.box('Home stair arrival bridge',(x-1.65,2.9,z+3.13),(1.08,.44,.18),'floor','internal stair',0)
                for xx in (x-2.12,x-1.18):C.beam('Stair stringer',(xx,-1.6,z+.27),(xx,2.75,z+3.19),.07,.16,'timber','internal stair')
                for xx in (x-2.17,x-1.13):
                    C.beam('Home stair handrail',(xx,-1.5,z+1.15),(xx,2.72,z+4.10),.035,.04,'hardware','home stair rails')
                    for q in (0,.25,.5,.75,1):
                        yy=-1.5+q*4.22;zz=z+.32+q*2.90
                        C.rod('Home stair rail upright',(xx,yy,zz),(xx,yy,zz+.92),.017,'hardware','home stair rails',10)
                # Furnished front living space and rear kitchen support occupation.
                C.box('Sofa base',(x+.9,-3.85,z+.42),(2.4,.88,.46),'interior','residential rooms')
                C.box('Sofa back',(x+.9,-3.47,z+.72),(2.4,.16,.57),'interior','residential rooms')
                C.box('Living table',(x+.9,-5,z+.56),(1.3,.58,.09),'timber','residential rooms')
                for dx in (-.48,.48):C.box('Table leg',(x+.9+dx,-5,z+.29),(.065,.45,.53),'timber','residential rooms')
                desk(x+.9,3.6,z+.18,'residential rooms')
                C.qa_room_light(f'home {i} floor {level}',(x,-2,z+2.65),80,2)
        # Party walls, no phantom extra exterior bays.
        if i<3:C.box('Party wall',(x+3,0,5.0),(.14,12.48,9.12),'interior','party walls',0)
        rear=C.Face((0,6.5,0),(-1,0,0),(0,-1,0),f'home {i+1} rear')
        hs=[dict(id=f'Rear window {j}',u=-x+.35,z=z,w=2.8,h=1.8) for j,z in enumerate((1.0,4.05,7.1))]
        hs.append(dict(id='Rear door',u=-x-1.9,z=.55,w=.95,h=2.25))
        rear.wall('Rear quiet brick wall',-x-3,-x+3,.44,9.6,holes=hs,role=role)
        for h in hs:
            if h['id']=='Rear door':rear.door(h['id'],h['u'],h['z'],h['w'],h['h'])
            else:rear.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=3,frame='hardware')
        C.box('Rear doorstep',(x+1.9,6.72,.275),(1.3,.75,.55),'trim','rear access')
        # Each rooftop stair pavilion is a separate closed, occupied volume.
        px=x-1.0;py=.85;w=2.9;d=7.0;z0=9.74;zt=12.25
        for label,origin,tangent,inward,span in [
            ('front',(px,py-d/2,0),(1,0,0),(0,1,0),w),
            ('rear',(px,py+d/2,0),(-1,0,0),(0,-1,0),w),
            ('left',(px-w/2,py,0),(0,-1,0),(1,0,0),d),
            ('right',(px+w/2,py,0),(0,1,0),(-1,0,0),d)]:
            f=C.Face(origin,tangent,inward,f'home {i} pavilion {label}')
            hs=[dict(id='Roof access door',u=.1,z=z0,w=.90,h=2.14)] if label=='front' else []
            if label=='right':hs=[dict(id='Roof access sidelight',u=-1.65,z=z0+.4,w=.65,h=1.6)]
            f.wall('Pavilion timber carrier',-span/2,span/2,z0,zt,depth=.18,role='timber',holes=hs)
            for h in hs:
                if label=='front':f.door(h['id'],h['u'],h['z'],h['w'],h['h'],glazed=True,role='hardware')
                else:f.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=1,rows=1,frame='hardware',depth=.18)
        C.box('Pavilion flat roof',(px,py,12.31),(3.15,7.25,.16),'roof','pavilion roof',0)
        C.qa_room_light(f'roof access {i}',(px+.4,py,12.0),180,2)
        for level,z in enumerate((3.66,6.70,9.74)):
            # Rails guard the long well edges; both flight ends stay open.
            for xx in (x-2.37,x-.93):seated_guard('Stairwell edge guard',(xx,-1.6,z),(xx,2.9,z),height=.94,spacing=.14,role='hardware')
        for yy in (-6.2,6.2):seated_guard('Roof deck rail',(x-2.94,yy,9.76),(x+2.94,yy,9.76),height=.98,role='hardware')
        if i<3:
            for a,b in [(-6.2,-2.7),(3.4,6.2)]:C.box('Private deck divider',(x+3,(a+b)/2,10.38),(.11,b-a,1.26),'timber','privacy screens')
        C.CONTACTS.append(dict(name=f'Unit {i+1} entrance',door=[x-1.9,-6.5,.55],approach=[x-1.9,-8.2,0],roof_access=True))
    # Two end elevations; right has source-visible wraparound corner glazing.
    for sign in (-1,1):
        f=C.Face((sign*12,0,0),(0,sign,0),(-sign,0,0),'right end' if sign>0 else 'left end')
        hs=[dict(id=f'End window {j}-{k}',u=u,z=z,w=1.65,h=1.8) for j,z in enumerate((1.0,4.05,7.1)) for k,u in enumerate((-4.9,0,4.5))]
        if sign>0:
            for h in hs:
                if h['u']==-4.9:
                    h.update(u=-5.32,w=1.98)
                    if h['z']<2:h.update(z=.55,h=2.25)
                    if h['z']>7:h.update(z=7.08,h=1.92)
        f.wall('End brick carrier',-6.5,6.5,.44,9.6,holes=hs,role='wall' if sign>0 else 'buff')
        if sign>0:
            ret=C.Face((12.045,0,0),(0,1,0),(-1,0,0),'corner timber return')
            ret.wall('Corner upper timber return',-6.5,-4.02,6.48,9.6,depth=.08,holes=hs,role='timber')
            for z,ht in ((9.3,.20),(6.75,.15)):ret.part('Corner pale horizontal return',-5.33,-.10,z,2.62,.25,ht,'trim','upper surrounds')
            ret.part('Corner pale side jamb',-4.05,-.10,8.02,.19,.25,2.55,'trim','upper surrounds')
        for h in hs:f.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=2,frame='hardware')
        seated_guard('End roof deck rail',(-12 if sign<0 else 12,-6.2,9.76),(-12 if sign<0 else 12,6.2,9.76),height=.98,role='hardware')
    for y in (-6.5,6.5):C.box('Continuous roof coping',(0,y,9.66),(24.15,.24,.18),'dark','parapet cap')

def arch_ring(face,name,u,z,r,width,d0,d1,role='trim',segments=24):
    for i in range(segments):
        a=i*math.pi/segments;b=(i+1)*math.pi/segments
        poly=[(u+rr*math.cos(t),z+rr*math.sin(t)) for rr,t in [(r,a),(r,b),(r+width,b),(r+width,a)]]
        face.panel(name,poly,d0,d1,role,'arched construction')

def arched_corners(f,name,u,z,w,h,role='trim',depth=.27):
    r=w/2;spring=z+h-r
    for sign in (-1,1):
        poly=[(u+sign*r,z+h),(u+sign*r,spring)]+[(u+sign*r*math.cos(j*math.pi/32),spring+r*math.sin(j*math.pi/32)) for j in range(1,17)]
        f.panel(name+' arched carrier spandrel',poly,0,depth,role,'arched carrier')

def arched_sash(f,name,u,z,w,h,role='trim',depth=.27):
    r=w/2;spring=z+h-r
    f.window(name,u,z,w,h-r,cols=2,rows=3,frame=role,bar=.022,depth=depth)
    # Fill only the two upper carrier corners; the fanlight has physical depth.
    arched_corners(f,name,u,z,w,h,role,depth)
    arch_ring(f,name+' curved sash',u,spring,r-.045,.045,.10,.20,role)
    poly=[(u+(r-.045)*math.cos(j*math.pi/24),spring+(r-.045)*math.sin(j*math.pi/24)) for j in range(25)]
    f.panel(name+' optical fanlight',poly,.177,.186,'glass','fanlight')
    f.part(name+' fanlight central bar',u,.135,spring+r/2,.022,.075,r-.03,role,'fanlight')

def school():
    # U-shaped occupied wings plus an unoccupied high front roof bridge.
    for x in (-12.5,12.5):C.box('Teaching wing foundation',(x,0,.18),(7,40,.36),'foundation','foundation',0)
    C.box('Rear teaching foundation',(0,13.5,.18),(18,7,.36),'foundation','foundation',0)
    C.box('Courtyard paving',(0,-1.5,.08),(18,23,.16),'foundation','courtyard',0)
    zfloors=(.36,4.0,7.64);top=11.28
    for x in (-12.5,12.5):
        for level,z in enumerate(zfloors):
            for light_y in (-13,0,9):
                C.qa_room_light(f'school wing {x} floor {level}',(x,light_y,z+3.25),300,4.5)
            slab=C.box('Teaching floor',(x,0,z+.08),(6.48,39.48,.16),'floor','school floors',0)
            if level>0:C.cut_box(slab,'Teaching stairwell',(x,15,z),(2.9,5.4,1))
        C.box('Teaching ceiling',(x,0,11.18),(6.48,39.48,.20),'interior','ceiling',0)
        C.box('Teaching wing closed eaves crown',(x,0,11.43),(7.06,40.06,.36),'trim','roof bearing',0)
        for sign in (-1,1):
            xx=x+sign*3.5;f=C.Face((xx,0,0),(0,sign,0),(-sign,0,0),f'wing {x} side {sign}')
            hs=[dict(id=f'Class window {level} {bay}',u=u,z=z+1.0,w=3.65,h=2.15)
                for level,z in enumerate(zfloors) for bay,u in enumerate((-16,-10.6,-5.2,.2,5.6,11,16.4))]
            if x*sign>0:
                for h in hs:
                    if h['z']<2:h.update(z=1.78,h=1.18)
            if x*sign<0:
                # The rear cross wing joins here: no exterior windows buried
                # in its wall intersections. Real passages connect the wings.
                hs=[h for h in hs if sign*h['u']+h['w']/2<9.7 or sign*h['u']-h['w']/2>17.3]
                for level,z in enumerate(zfloors):
                    hs.append(dict(id=f'Wing connecting passage {level}',u=sign*13.5,z=z+.16,w=1.7,h=2.5))
            f.wall('Brick teaching elevation',-20,20,.36,top,holes=hs,role='buff')
            for h in hs:
                if not h['id'].startswith('Wing connecting'):
                    f.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=4,frame='trim',bar=.045)
            for z in (.5,4.0,7.64,11.15):f.part('Continuous school floor course',0,-.06,z,40,.19,.22,'trim','school courses')
            for u in (-19,-13.3,-7.9,-2.5,2.9,8.3,13.7,19):f.part('School vertical pier',u,-.04,5.8,.23,.16,10.9,'trim','school piers')
        for sign in (-1,1):
            f=C.Face((x,sign*20,0),(sign,0,0),(0,-sign,0),f'wing {x} end {sign}')
            hs=[dict(id=f'Pavilion glazing {level}',u=0,z=z+(1.4 if level==0 else .55),w=5.3,h=1.2 if level==0 else 2.55) for level,z in enumerate(zfloors)]
            f.wall('Pavilion brick carrier',-3.5,3.5,.36,top,holes=hs,role='buff')
            for h in hs:f.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=6,frame='trim',bar=.04)
            for u in (-3.25,3.25):f.part('Pavilion corner pier',u,-.07,5.8,.38,.23,10.9,'trim','pavilion piers')
            for z in (.8,4,7.64,11.15):f.part('Pavilion pale course',0,-.09,z,7.12,.26,.30,'trim','pavilion courses')
        # Inferred classrooms visibly occupied behind real glazing, rear stairs.
        for level,z in enumerate(zfloors):
            for y in (-14,-7,0,7):
                for dx in (-1.5,1.1):
                    for dy in (-1,1):desk(x+dx,y+dy,z+.16,'classroom desks')
            if level<2:
                for j in range(10):
                    C.box('School stair flight',(x-.77,13+j*.25,z+.10+(j+1)*.182),(1.25,.28,.12),'trim','school stairs')
                    C.box('School stair return',(x+.77,15.25-j*.25,z+1.92+(j+1)*.182),(1.25,.28,.12),'trim','school stairs')
                C.box('School stair landing',(x,15.85,z+1.91),(2.85,1.0,.14),'trim','school stairs')
                C.qa_room_light(f'school stair {x} level {level}',(x,14.8,z+3.2),170,2)
                for dx in (-1.32,-.22):C.beam('School first stringer',(x+dx,12.87,z+.16),(x+dx,15.42,z+1.92),.11,.20,'trim','school stairs')
                for dx in (.22,1.32):C.beam('School return stringer',(x+dx,15.42,z+1.98),(x+dx,12.87,z+3.74),.11,.20,'trim','school stairs')
                for dx in (-1.36,-.18,.18,1.36):
                    lo,hi=(z+.34,z+1.98) if dx<0 else (z+3.8,z+2.16)
                    C.beam('School stair handrail',(x+dx,13,lo+.95),(x+dx,15.25,hi+.95),.045,.045,'hardware','school rails')
                    for q in (0,.25,.5,.75,1):
                        yy=13+q*2.25;zz=lo+q*(hi-lo)
                        C.rod('School stair upright',(x+dx,yy,zz),(x+dx,yy,zz+.95),.019,'hardware','school rails',10)
                for dx in (-1.30,1.30):C.box('School landing support',(x+dx,16.1,z+1.0),(.12,.12,1.84),'trim','school stairs')
                seated_guard('School landing guard',(x-1.35,16.30,z+1.98),(x+1.35,16.30,z+1.98),height=.95,role='hardware')
            if level>0:
                C.box('School continuous arrival landing',(x,12.57,z+.08),(2.9,.72,.16),'floor','school stairs',0)
                for dx in (-1.54,1.54):seated_guard('School well edge',(x+dx,12.21,z+.16),(x+dx,17.79,z+.16),height=1.02,role='hardware')
                seated_guard('School well rear edge',(x-1.54,17.79,z+.16),(x+1.54,17.79,z+.16),height=1.02,role='hardware')
    # Rear cross wing, retaining the clear courtyard in front of it.
    for z in zfloors:C.box('Rear classroom floor',(0,13.5,z+.08),(18,6.5,.16),'floor','rear wing',0)
    C.box('Rear classroom ceiling',(0,13.5,11.2),(18,6.5,.16),'interior','rear wing',0)
    C.box('Rear wing closed eaves crown',(0,13.5,11.43),(18,7.06,.36),'trim','roof bearing',0)
    # Both exterior doors meet their occupied floor through grounded approaches.
    for wall_y, direction, grade, count in ((10,-1,.16,2),(17,1,0,3)):
        C.box('School doorway landing',(0,wall_y+direction*.58,(grade+.52)/2),(3.1,1.20,.52-grade),'foundation','door approaches',0)
        for step in range(count):
            height=(.52-grade)*(count-step)/count
            C.box('School grounded approach step',(0,wall_y+direction*(1.20+(step+.5)*.35),grade+height/2),(3.1,.356,height),'foundation','door approaches',0)
    for y,normal in ((10,1),(17,-1)):
        f=C.Face((0,y,0),(1,0,0),(0,normal,0),'rear cross wing '+str(y))
        hs=[dict(id=f'Rear wing window {j} {u}',u=u,z=z+1,w=3.2,h=2.1) for j,z in enumerate(zfloors) for u in (-6,0,6)]
        hs=[h for h in hs if not(h['u']==0 and h['z']<2)]
        hs.append(dict(id='Courtyard double door',u=0,z=.52,w=2.6,h=3.25 if y==10 else 2.7))
        if y==10:
            for h in hs:
                if h['id']!='Courtyard double door' and h['z']<2:h.update(z=.85,h=2.9)
        f.wall('Cross wing brick',-9,9,.36,top,holes=hs,role='buff')
        for h in hs:
            if y==10:
                if h['id']=='Courtyard double door':
                    arched_corners(f,'Court portal',0,.52,2.6,3.25)
                    f.door(h['id'],0,.52,2.6,1.95,glazed=True,role='hardware')
                    arc=[(1.27*math.cos(j*math.pi/24),2.47+1.27*math.sin(j*math.pi/24)) for j in range(25)]
                    f.panel('Court door fanlight',arc,.18,.19,'glass','court portal')
                    arch_ring(f,'Court portal archivolt',0,2.47,1.30,.22,-.12,.22)
                elif h['z']<2:
                    arched_sash(f,h['id'],h['u'],h['z'],h['w'],h['h'])
                    arch_ring(f,'Court window archivolt',h['u'],h['z']+h['h']-h['w']/2,h['w']/2,.18,-.12,.22)
                else:f.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=4)
            elif h['id']=='Courtyard double door':f.door(h['id'],0,.52,2.6,2.7,glazed=True,role='hardware')
            else:f.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=4)
        for z in (4,7.64,11.15):f.part('Cross wing course',0,-.07,z,18,.2,.26,'trim','cross wing courses')
    # Low independent entry wall: four open iron grilles and one walkable arch.
    gate=C.Face((0,-20,0),(1,0,0),(0,1,0),'street gate')
    for a,b in [(-9,-7.7),(-5.7,-5.2),(-3.2,-2.2),(2.2,3.2),(5.2,5.7),(7.7,9)]:
        gate.wall('Street gate pier',a,b,0,4.0,role='trim')
    for a,b in [(-9,-2.2),(2.2,9)]:gate.part('Low gate lintel',(a+b)/2,.20,4.02,b-a,.5,.28,'trim','gate lintel')
    arch_ring(gate,'Main gateway barrel',0,3.25,2.2,.36,-.10,2.55)
    arch_ring(gate,'Main gateway curved roof',0,3.25,2.56,.12,-.22,2.65,'copper')
    for a,b in [(-9,-2.38),(2.38,9)]:
        C.solid_surface('Low entry sloping roof',[(a,-20.2,4.2),(b,-20.2,4.2),(b,-17.4,4.82),(a,-17.4,4.82)],.13,'roof')
        for yy,zz in ((-19.85,4.06),(-17.55,4.54)):C.box('Low entry roof beam',((a+b)/2,yy,zz),(b-a,.22,.3),'trim','entry roof support')
        for xx in (a,b):C.box('Entry rear roof pier',(xx,-17.55,2.25),(.35,.35,4.5),'trim','entry roof support')
    for u in (-2.38,2.38):gate.part('Main arch pier',u,.25,1.625,.36,.7,3.25,'trim','gateway')
    for a,b in [(-7.7,-5.7),(-5.2,-3.2),(3.2,5.2),(5.7,7.7)]:
        C.box('Street grille grounded sill',((a+b)/2,-19.82,.09),(b-a,.42,.18),'trim','gate foundation',0)
        seated_guard('Street grille',(a,-19.82,.18),(b,-19.82,.18),height=3.65,spacing=.13,role='hardware')
    # Roof envelope from explicitly joined outer/ridge/inner contours.
    outer=[(-16.45,-20.45,11.45),(16.45,-20.45,11.45),(16.45,17.45,11.45),(-16.45,17.45,11.45)]
    ridges=[(-12.5,-16.5,14),(12.5,-16.5,14),(12.5,13.5,14),(-12.5,13.5,14)]
    inner=[(-8.75,-12.75,11.45),(8.75,-12.75,11.45),(8.75,9.75,11.45),(-8.75,9.75,11.45)]
    roofowners=[]
    for i in range(4):
        j=(i+1)%4
        if i==0:outerpoly=[outer[i],outer[j],ridges[j],ridges[i]]
        elif i==1:outerpoly=[outer[1],(16.45,20.4,11.45),(12.5,20.4,14),ridges[1]]
        elif i==2:outerpoly=[(-8.55,17.45,11.45),(8.55,17.45,11.45),ridges[2],ridges[3]]
        else:outerpoly=[(-16.45,20.4,11.45),outer[0],ridges[0],(-12.5,20.4,14)]
        roofowners.append(C.solid_surface('Outer roof slope '+str(i),outerpoly,.18))
        roofowners.append(C.solid_surface('Inner roof slope '+str(i),[ridges[i],ridges[j],inner[j],inner[i]],.18))
        C.beam('Bounded main ridge',ridges[i],ridges[j],.13,.15,'copper','roof ridges')
    # High bridge edge sits on the side wings, with empty courtyard below.
    C.box('High front bridge beam',(0,-20.0,11.12),(18.2,.45,.62),'trim','roof bridge')
    C.box('High courtyard bridge beam',(0,-12.95,11.12),(18.2,.45,.62),'trim','roof bridge')
    for x in (-12.5,12.5):
        inward=1 if x<0 else -1
        roofowners.append(C.solid_surface('Rear wing joined inner slope',[(x,13.5,14),(x,20.4,14),
            (x+inward*3.95,20.4,11.45),(x+inward*3.95,17.45,11.45)],.18))
        C.beam('Rear continuing ridge',(x,13.5,14),(x,20.4,14),.13,.15,'copper','roof ridges')
        C.beam('Rear bounded valley',(x,13.5,14),(x+inward*3.95,17.45,11.45),.12,.10,'copper','roof valleys')
        C.prism('Closed rear gable',[(x-3.53,11.1),(x+3.53,11.1),(x+3.53,11.62),
            (x,13.96),(x-3.53,11.62)],'y',19.74,20.03,'buff','rear gable')
    # Front dormers use the hero's curved heads; through-roof cuts are physical.
    for x in (-12.5,12.5):
        for owner in roofowners:C.cut_box(owner,'Dormer through roof cut',(x,-18.2,13),(1.25,1.9,4))
        f=C.Face((x,-19.1,0),(1,0,0),(0,1,0),'front dormer '+str(x))
        hs=[dict(id='Dormer clear sash',u=0,z=12.10,w=.86,h=1.3)]
        f.wall('Dormer front body',-.70,.70,11.65,13.55,role='trim',holes=hs)
        f.window('Dormer clear sash',0,12.1,.86,1.3,cols=1,rows=1,frame='hardware')
        arch_ring(f,'Curved dormer head',0,13.15,.70,.16,-.04,1.95,'trim')
        for xx in (-.62,.62):C.box('Dormer cheek',(x+xx,-18.15,12.73),(.16,1.9,2.16),'trim','dormer cheeks')
        C.box('Dormer back',(x,-17.2,12.80),(1.4,.18,2.3),'trim','dormer back')
        # Curved solid cap owns its weathering crown and joins both cheeks.
        for i in range(20):
            a=i*math.pi/20;b=(i+1)*math.pi/20
            poly=[(rr*math.cos(t),13.15+rr*math.sin(t)) for rr,t in [(.72,a),(.72,b),(.86,b),(.86,a)]]
            C.prism('Dormer curved cap',[(x+u,z) for u,z in poly],'y',-19.2,-17.08,'copper','dormer cap')
    # Side dormer cadence follows the top photograph, with the same curved head
    # chosen from the hero. Cut all roof owners, never hide an intact roof behind glass.
    for sign in (-1,1):
        for yy in (-11,-2,7,16):
            for owner in roofowners:C.cut_box(owner,'Side dormer roof cut',(sign*14.55,yy,13),(1.95,1.0,4))
            f=C.Face((sign*15.55,yy,0),(0,sign,0),(-sign,0,0),f'Side dormer {sign} {yy}')
            hs=[dict(id='Side dormer sash',u=0,z=12.25,w=.66,h=1.05)]
            f.wall('Side dormer face',-.58,.58,11.7,13.42,role='trim',holes=hs)
            f.window('Side dormer sash',0,12.25,.66,1.05,cols=1,rows=1,frame='hardware')
            for u in (-.51,.51):f.part('Side dormer cheek',u,1.02,12.62,.14,2.14,1.9,'trim','dormer cheeks')
            f.part('Side dormer back',0,2.02,12.85,1.15,.16,2.35,'trim','dormer back')
            for j in range(20):
                a=j*math.pi/20;b=(j+1)*math.pi/20
                poly=[(rr*math.cos(t),13.13+rr*math.sin(t)) for rr,t in [(.59,a),(.59,b),(.73,b),(.73,a)]]
                f.panel('Side dormer curved cap',poly,-.10,2.15,'copper','dormer cap')
    # Three courtyard-facing dormers from the top reference. Their rear walls
    # penetrate the actual inner roof slopes; the cuts stay inside the cheeks.
    for label,origin,tangent,inward in [
        ('left court',(-9.4,-8,0),(0,-1,0),(-1,0,0)),
        ('right court',(9.4,-8,0),(0,1,0),(1,0,0)),
        ('rear court',(0,10.35,0),(1,0,0),(0,1,0))]:
        f=C.Face(origin,tangent,inward,label+' dormer')
        cutcenter=f.p(0,.9,13)
        cutsize=(1.1,1.7,4) if label=='rear court' else (1.7,1.1,4)
        for owner in roofowners:C.cut_box(owner,'Court dormer roof aperture',cutcenter,cutsize)
        hs=[dict(id=label+' dormer sash',u=0,z=12.1,w=.86,h=1.25)]
        f.wall('Court dormer front',-.70,.70,11.45,13.48,role='trim',holes=hs)
        f.window(hs[0]['id'],0,12.1,.86,1.25,cols=1,rows=1,frame='hardware')
        for u in (-.62,.62):f.part('Court dormer cheek',u,.98,12.62,.16,2.1,2.34,'trim','court dormer')
        f.part('Court dormer back',0,2.0,12.7,1.4,.18,2.5,'trim','court dormer')
        arch_ring(f,'Court dormer curved cap',0,13.1,.71,.15,-.10,2.12,'copper')
    # Physically small standing seams from the front-view finish authority.
    # Bounded central runs stop before dormer footprints and hip junctions.
    for i in range(-21,22):
        x=i*.55
        if min(abs(x-12.5),abs(x+12.5))>1.0:
            C.beam('Front standing seam',(x,-20.44,11.49),(x,-16.52,14.03),.023,.035,'copper','roof seams')
            if abs(x)>1.6:C.beam('Front inner standing seam',(x,-16.48,14.03),(x,-12.77,11.49),.023,.035,'copper','roof seams')
    for sign in (-1,1):
        for i in range(-27,24):
            y=i*.55
            if all(abs(y-d)>1.0 for d in (-11,-2,7,16)):
                C.beam('Side standing seam',(sign*16.44,y,11.49),(sign*12.52,y,14.03),.023,.035,'copper','roof seams')
    # Seated clock tower: opaque plinth, four clock faces and open bell stage.
    C.box('Clock tower plinth',(0,-16.5,14.95),(2.8,2.8,3.6),'copper','clock tower')
    for label,origin,tan,norm in [('front',(0,-17.91,0),(1,0,0),(0,1,0)),('rear',(0,-15.09,0),(-1,0,0),(0,-1,0)),
        ('left',(-1.41,-16.5,0),(0,-1,0),(1,0,0)),('right',(1.41,-16.5,0),(0,1,0),(-1,0,0))]:
        f=C.Face(origin,tan,norm,'clock '+label)
        poly=[(.95*math.cos(i*math.tau/64),15.65+.95*math.sin(i*math.tau/64)) for i in range(64)]
        f.panel('Clock dial',poly,-.07,-.015,'trim','clock faces')
        for i in range(12):
            a=i*math.tau/12
            C.beam('Clock hour mark',f.p(.79*math.sin(a),-.082,15.65+.79*math.cos(a)),f.p(.87*math.sin(a),-.082,15.65+.87*math.cos(a)),.027,.024,'hardware','clock marks')
        C.beam('Clock minute hand',f.p(0,-.10,15.65),f.p(.32,-.10,16.26),.035,.025,'hardware','clock hands')
        C.beam('Clock hour hand',f.p(0,-.11,15.65),f.p(-.41,-.11,15.89),.04,.025,'hardware','clock hands')
    C.box('Clock cap',(0,-16.5,16.83),(3.1,3.1,.18),'trim','clock cap')
    for i in range(8):
        a=(i+.5)*math.tau/8
        f=C.Face((1.08*math.cos(a),-16.5+1.08*math.sin(a),0),(-math.sin(a),math.cos(a),0),
            (-math.cos(a),-math.sin(a),0),f'bell lantern {i}')
        hs=[dict(id='Bell arch',u=0,z=17.04,w=.62,h=1.48)]
        f.wall('Arched bell lantern',-.448,.448,16.94,18.73,depth=.15,holes=hs,role='trim')
        arched_corners(f,'Bell arch',0,17.04,.62,1.48,'trim',.15)
        arch_ring(f,'Bell archivolt',0,18.21,.31,.08,-.035,.15,'trim')
    cylinder('Bell shoulder',0,-16.5,17.65,.31,.35,'copper',24,r2=.20)
    cylinder('Bell flared mouth',0,-16.5,17.35,.54,.31,'copper',24,r2=.31)
    cylinder('Bell lip',0,-16.5,17.32,.56,.07,'copper',24)
    cylinder('Bell hanger',0,-16.5,18.0,.045,.68,'hardware',12)
    cylinder('Bell clapper',0,-16.5,17.13,.065,.26,'hardware',12)
    cylinder('Bell stage base',0,-16.5,16.9,1.15,.18,'trim',8)
    cylinder('Bell stage crown',0,-16.5,18.7,1.22,.17,'trim',8)
    dome('Bell cupola',0,-16.5,18.85,1.22,1.0,'copper')
    cylinder('Bell finial',0,-16.5,19.8,.04,.86,'copper',12)
    C.CONTACTS.extend([dict(name='Open front court',entry=[0,-20,0],roof_bridge_underside=10.81,occupied_floor_beneath=False),
        dict(name='Tower seat',roof_ridge_z=14,tower_bottom=13.15),dict(name='Source reconciliation',front_dormers='curved',roof_finish='front metal; aerial slate conflict retained')])

def main():
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=['office','row','school'],required=True)
    p.add_argument('--source-root',type=Path,required=True);p.add_argument('--output',required=True)
    p.add_argument('--version',type=int,default=1);p.add_argument('--resolution',type=int,default=1440)
    p.add_argument('--dry-run',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    entry=source_entry(a.kind,a.source_root);m=manifest(a.kind,a.version)
    out=C.prepare_candidate(a,entry,m,__file__,extra_scripts=[HERE/'plan.py',HERE.parent/'catalogue_runtime_preparation/guards.py'])
    if out is None:return
    cams=C.setup(PALETTE,m['camera_roster'],a.resolution)
    # Fine edge microbevels are outside this clay scope. Applying thousands of
    # object operators while constructing the scene causes quadratic dependency
    # work. Silhouette, reveals, profiles and contacts remain physical geometry.
    C.bevel=lambda obj,width=.012,segments=1: None
    old_mesh=C.mesh
    count=[0]
    def measured_mesh(*args,**kwargs):
        obj=old_mesh(*args,**kwargs);count[0]+=1
        if count[0]%200==0:print(f'CONSTRUCTION_COMPONENTS {count[0]}',flush=True)
        return obj
    C.mesh=measured_mesh
    for obj in C.bpy.context.scene.objects:
        if obj.type=='LIGHT':obj.location*=2.2;obj.data.energy*=4.84;obj.data.size*=2.2
    print('CONSTRUCTION_STARTED '+a.kind,flush=True)
    {'office':office,'row':row,'school':school}[a.kind]()
    print('CONSTRUCTION_FINISHED '+a.kind,flush=True)
    cleanup();C.deliver(out,m,cams)

if __name__=='__main__':main()
