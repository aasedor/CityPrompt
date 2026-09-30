"""Finite source-locked architectural-clay buildings; no generation API calls."""
import argparse
import importlib.util
import json
import math
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('showcase_primitives', HERE.parent/'showcase_building_trio/build.py')
B = importlib.util.module_from_spec(spec); sys.modules[spec.name] = B; spec.loader.exec_module(B)
C = B.C
SPECS = {
    'timber': dict(title='Nordic Roof-Garden Apartments', width=20, depth=18, height=22.8, floors=6,
        signature='Five-bay six-storey timber frame, alternating full-depth loggias, narrow glazed slots and planted roof with offset pavilion.'),
    'villa': dict(title='Tuscan Arcade Villa', width=18, depth=13, height=11.8, floors=3,
        signature='Three inhabited levels including low attic, three-bay stone entrance arcade, green shutters, corner quoins and canal-tile gable.'),
    'cinema': dict(title='Grand Deco Cinema', width=24, depth=38, height=22, floors=3,
        signature='Stepped terracotta movie-palace frontage, large arch windows, suspended blade sign, lit marquee, deep lobby and auditorium.'),
}

def box(name, loc, size, role='wall', module='envelope'):
    return C.box(name, loc, size, role, module, 0)

VEGETATION = {}

def load_vegetation(path):
    """Use the same metre-scale leaf/branch geometry as the native park kit."""
    material=C.bpy.data.materials.new('native botanical vertex colour');material.use_nodes=True
    attr=material.node_tree.nodes.new('ShaderNodeVertexColor');attr.layer_name='Color'
    material.node_tree.links.new(attr.outputs['Color'],material.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
    material.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.9
    C.MATS['native_plant']=material
    payload=json.loads(Path(path).read_text())
    for kind in ('silver_shrub','flowering_perennial','ornamental_tree'):
        VEGETATION[kind]=[]
        for part,g in payload[kind].items():
            vs=list(zip(*[iter(g['position'])]*3));ids=g['index'] or list(range(len(vs)))
            mesh=C.bpy.data.meshes.new(kind+' '+part);mesh.from_pydata(vs,[],list(zip(*[iter(ids)]*3)));mesh.update()
            colors=mesh.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='POINT')
            colors.data.foreach_set('color',[v for rgb in zip(*[iter(g['color'])]*3) for v in (*rgb,1)])
            mesh.materials.append(material);VEGETATION[kind].append(mesh)

def plant(x, y, z, radius=.4, height=.65, role='leaf'):
    kind='ornamental_tree' if height>1.2 else ('silver_shrub' if radius>.24 else 'flowering_perennial')
    scale=height/({'ornamental_tree':4.77,'silver_shrub':1.066,'flowering_perennial':.699}[kind])
    for data in VEGETATION[kind]:
        o=C.bpy.data.objects.new(kind,data);C.bpy.context.collection.objects.link(o)
        o.location=(x,y,z);o.scale=(scale,)*3;o.rotation_euler.z=(x*7+y*3)%math.tau
        C.tag(o,'native_plant','source-composed native botanical planting')

def planter(x,y,z,w,d):
    box('roof planter',(x,y,z+.2),(w,d,.4),'stone','roof landscape')
    box('rooted planting soil',(x,y,z+.406),(w-.12,d-.12,.018),'soil','roof landscape')
    rng=random.Random(round((x+y)*1000))
    # Continuous low groundcover under the specimen shrubs, with individually
    # modelled leaves instead of costly duplicated high-poly bush crowns.
    for tone in ('leaf','leaf_light'):
        vs=[];fs=[]
        for i in range(int(w*d*90)):
            xx=x+rng.uniform(-w/2+.10,w/2-.10);yy=y+rng.uniform(-d/2+.10,d/2-.10)
            zz=z+.46+rng.uniform(.02,.20);angle=rng.random()*math.tau
            a=rng.uniform(.055,.10);b=a*.48;dx,dy=math.cos(angle),math.sin(angle);k=len(vs)
            vs.extend([(xx-a*dx,yy-a*dy,zz),(xx-b*dy,yy+b*dx,zz+.035),(xx+a*dx,yy+a*dy,zz+.045),(xx+b*dy,yy-b*dx,zz+.02)])
            fs.extend([(k,k+1,k+2),(k,k+2,k+3)])
        C.mesh('continuous roof groundcover',vs,fs,tone,'roof landscape')
    for i in range(max(4,int(w*d*1.4))):
        plant(x+rng.uniform(-w*.42,w*.42),y+rng.uniform(-d*.42,d*.42),z+.42,
              rng.uniform(.17,.3),rng.uniform(.28,.65),'leaf' if i%3 else 'leaf_light')

def timber():
    w,d,h=20,18,19.4
    box('stone ground plinth',(0,0,.10),(w,d,.20),'foundation')
    fronts=B.faces(w,d)
    for level in range(6):
        z=.20 if level==0 else 3.4+(level-1)*3.2
        top=3.4 if level==0 else z+3.2
        box('authored floor plate',(0,0,z),(w,d,.20),'timber','floor structure')
        # The complete facade grid continues around all four sides.
        for fi,face in enumerate(fronts):
            length=w if fi%2==0 else d
            bays=5 if fi%2==0 else 4; bw=length/bays
            for j in range(bays):
                u=(j+.5)*bw
                loggia=level>0 and ((fi==0 and j in (0,3,4)) or (fi==2 and j in (1,4)))
                inset=1.65 if loggia else .20
                carrier=C.Face(face.p(0,inset,0),tuple(face.t),tuple(face.n),face.label+f' level{level} bay{j}')
                holew=bw-.8 if loggia or level==0 else 1.20
                hole=dict(id=f'opening-{fi}-{level}-{j}',u=u,z=z+.2,w=holew,h=top-z-.45,
                          cols=2 if holew>2 else 1,frame='hardware')
                if fi==0 and level==0 and j==2:
                    hole.update(id='public-entrance',z=.20,h=2.86,door=True)
                # Only one bay carrier, with a physical opening and timber finish.
                local=C.Face(carrier.p(j*bw+.16,0,0),tuple(face.t),tuple(face.n),carrier.label)
                local_hole=dict(hole,u=bw/2-.16)
                B.open_wall(local,bw-.32,z+.1,top-.1,[local_hole],role='wall',depth=.22)
                # Thin vertical board relief stops at the actual opening.
                for k in range(int((bw-.32)/.16)):
                    uu=j*bw+.23+k*.16
                    if abs(uu-u)<holew/2+.04: continue
                    face.part('vertical timber board joint',uu,inset-.014,(z+top)/2,.012,.025,top-z-.24,'timber_dark','cladding',0)
                if loggia:
                    # Full-depth side returns separate balconies and carry the upper slab.
                    for side in (-1,1):
                        face.part('loggia side return',u+side*(bw/2-.19),.9,(z+top)/2,.16,1.7,top-z-.2,'wall','loggias',0)
                    a=face.p(j*bw+.25,.10,z+.1);b=face.p((j+1)*bw-.25,.10,z+.1)
                    C.railing('inset loggia guard',a,b,role='hardware',spacing=.13)
                    if j==3:
                        for k in range(8):face.part('partial timber privacy screen',u+1.1-k*.12,.16,(z+top)/2,.045,.09,top-z-.26,'timber','screens',0)
                    # Bench and small table visibly occupy the sheltered balcony.
                    face.part('balcony bench seat',u,.92,z+.54,1.15,.40,.09,'timber','balcony furniture',0)
                    for uu in (u-.45,u+.45):face.part('bench leg',uu,.92,z+.31,.07,.32,.45,'hardware','balcony furniture',0)
                else:
                    # Rooms have visible depth, return partitions and furnishings.
                    # Corner rooms are open plan: orthogonal partitions must not
                    # cross the adjacent elevation's windows or loggia recess.
                    if j not in (0,bays-1):
                        face.part('room partition',u+bw/2-.25,2.15,(z+top)/2,.12,3.2,top-z-.25,'interior','interior',0)
                        face.part('room rear wall',u,3.7,(z+top)/2,bw-.45,.12,top-z-.25,'interior','interior',0)
                    face.part('interior desk',u,1.75,z+.86,1.05,.55,.08,'timber','interior',0)
                    for uu in (u-.43,u+.43):face.part('desk leg',uu,1.75,z+.44,.05,.43,.8,'hardware','interior',0)
            for j in range(bays+1):
                face.part('continuous expressed timber post',j*bw,.075,(z+top)/2,.30,.42,top-z,'timber','frame',0)
            face.part('expressed floor edge',length/2,.06,top-.11,length,.42,.26,'timber','frame',0)
    box('weatherproof roof deck',(0,0,h),(20.35,18.35,.24),'roof','roof')
    for face in fronts:
        length=w if face.label in ('front','rear') else d
        C.railing('roof garden guard',face.p(.15,.02,h+.12),face.p(length-.15,.02,h+.12),role='hardware',spacing=.15)
    # Reference: continuous outer planting ring, offset front pavilion, service
    # core behind it and an unobstructed circulation loop.
    for x in (-8.7,8.7):planter(x,0,h+.13,1.2,15.1)
    for y in (-7.65,7.65):planter(0,y,h+.13,16.5,1.2)
    planter(5,0,h+.13,2.7,9.4)
    box('roof pavilion terrace',(-2,-2.1,h+.19),(10.5,8.6,.14),'timber','pavilion')
    for x in [-6.6,-2.3,2]:
        for y in (-5.9,1.5):box('pavilion timber column',(x,y,h+1.65),(.22,.22,3.0),'timber','pavilion')
    box('pavilion flat roof',(-2.3,-2.1,h+3.18),(9.8,8.4,.24),'timber','pavilion')
    box('pavilion dark edge',(-2.3,-2.1,h+3.32),(9.95,8.55,.08),'roof','pavilion')
    # Closed stair core, with real opening, contiguous with pavilion.
    core=C.Face((-3,2,0),(1,0,0),(0,1,0),'roof core')
    B.open_wall(core,6,h+.2,h+2.7,[dict(id='roof-access',u=3,z=h+.2,w=1.2,h=2.25,cols=1,door=True)])
    for x in (-2.89,2.89):box('core side',(x,3.9,h+1.45),(.22,3.8,2.5),'wall','roof core')
    box('core rear',(0,5.8,h+1.45),(6,.22,2.5),'wall','roof core')
    box('core weather roof',(0,3.9,h+2.8),(6.1,4.05,.20),'roof','roof core')
    for x in (-5,0):B.table(x,-2.2,h+.28)
    for x in (-8.4,8.4):
        for y in (-7.3,7.3):
            plant(x,y,h+.55,.75,2.15)
    # A readable glazed entrance, with a short seated stoop and door hardware.
    box('entry lower step',(0,-9.65,.05),(3.8,1.3,.10),'stone','public entrance')
    box('entry upper step',(0,-9.30,.15),(3.6,.60,.10),'stone','public entrance')
    box('entry canopy',(0,-9.25,3.10),(3.8,1.15,.12),'timber','public entrance')
    for x in (-.18,.18):C.rod('entry pull handle',(x,-8.76,1.0),(x,-8.76,1.65),.018,'hardware','public entrance')
    B.label('NORDIC',(0,-9.85,2.78),.20,'hardware')
    box('lobby reception',(0,-5.6,.65),(1.9,.6,.9),'timber','occupied lobby')
    # Double-height lobby visible through ground-floor glazing.
    for i in range(19):box('lobby stair tread',(-7, -4.8+i*.16,.25+i*.16),(1.3,.18,.12),'timber','lobby stair')
    C.railing('lobby stair rail',(-7.68,-4.8,.25),(-7.68,-1.92,3.13),role='hardware')
    C.CONTACTS.append(dict(id='timber-frame',relationship='Continuous ground-to-roof posts, connected floor beams and fixed loggia returns'))

def arch_ring(face,name,u,z,r,thickness,depth,role='stone'):
    for i in range(24):
        a=i*math.pi/24;b=(i+1)*math.pi/24
        poly=[(u+rr*math.cos(t),z+rr*math.sin(t)) for rr,t in [(r,a),(r,b),(r+thickness,b),(r+thickness,a)]]
        face.panel(name,poly,-.08,depth,role,'arch voussoirs')

def arch_carrier(face,length,top,centres,r,spring,depth=.40,role='wall'):
    # Construct around each opening rather than overlaying an arch on solid wall.
    cuts=sorted([0,length,*[x for c in centres for x in (c-r,c+r)]])
    for a,b in zip(cuts,cuts[1:]):
        centre=next((c for c in centres if c-r< (a+b)/2 < c+r),None)
        if centre is None:
            face.part('arch pier',(a+b)/2,depth/2,top/2,b-a,depth,top,role,'arcade',0)
        else:
            for i in range(24):
                aa=math.pi-i*math.pi/24;bb=math.pi-(i+1)*math.pi/24
                x1=centre+r*math.cos(aa);x2=centre+r*math.cos(bb)
                face.panel('arch closed spandrel',[(x1,spring+r*math.sin(aa)),(x2,spring+r*math.sin(bb)),(x2,top),(x1,top)],0,depth,role,'arcade')
            arch_ring(face,'radial stone arch',centre,spring,r,.24,depth+.035)

def villa():
    w,d=18,13;front,right,rear,left=B.faces(w,d)
    box('villa foundation',(0,0,.08),(w,d,.16),'foundation')
    # Open portico at the front, complete inhabited envelope behind it.
    arch_carrier(front,w,3.8,[3,9,15],2.35,1.3,.43,'wall')
    inner=C.Face((-9,-3.5,0),(1,0,0),(0,1,0),'portico inner wall')
    arch_carrier(inner,6,3.8,[3],.775,2.05,.38,'wall')
    inner.window('villa-entry',3,.16,1.55,1.89,2,1,'shutter',.16,sill=False,kind='arched glazed entrance')
    fan=[(3-.775,2.05),(3+.775,2.05)]+[(3+.775*math.cos(i*math.pi/24),2.05+.775*math.sin(i*math.pi/24)) for i in range(25)]
    inner.panel('entrance arched fanlight',fan,.205,.009,'glass','entrance')
    arch_ring(inner,'green arched frame',3,2.05,.72,.055,.13,'shutter')
    for u in (3-.88,3+.88):inner.part('stone entry jamb',u,.1,1.05,.21,.45,2.10,'stone','entrance',0)
    for x in (-6.12,-5.88):C.rod('entry pull',(x,-3.37,.95),(x,-3.37,1.35),.018,'hardware','entrance')
    remainder=C.Face((-3,-3.5,0),(1,0,0),(0,1,0),'portico window wall')
    B.open_wall(remainder,12,.16,3.8,[dict(id='portico-window-middle',u=3,z=1.1,w=1.45,h=1.8),dict(id='portico-window-right',u=9,z=1.1,w=1.45,h=1.8)],role='wall')
    for face in (right,rear,left):
        length=w if face==rear else d
        us=[length*(i+.5)/3 for i in range(3)]
        B.open_wall(face,length,.16,3.8,[dict(id=f'{face.label}-ground-{i}',u=u,z=1.0,w=1.35,h=1.85) for i,u in enumerate(us)],role='wall')
    for z in (3.8,7.1,9.3):box('villa floor or eaves deck',(0,0,z),(w,d,.18),'floor','floors')
    for face in (front,right,rear,left):
        length=w if face in (front,rear) else d
        us=[length*(i+.5)/3 for i in range(3)]
        for level,z,top,wh,ww in [(1,3.89,7.1,1.7,1.55),(2,7.19,9.3,.88,1.25)]:
            holes=[dict(id=f'{face.label}-floor-{level}-{i}',u=u,z=z+.60,w=ww,h=wh,frame='shutter') for i,u in enumerate(us)]
            B.open_wall(face,length,z,top,holes,role='wall',depth=.38)
            for i,u in enumerate(us):
                # Stone window surrounds are aligned with the actual wall opening.
                for s in (-1,1):face.part('stone jamb',u+s*(ww/2+.095),-.055,z+.60+wh/2,.19,.16,wh+.28,'stone','window surround',0)
                for zz in (z+.51,z+.69+wh):face.part('stone lintel sill',u,-.06,zz,ww+.38,.19,.18,'stone','window surround',0)
                if level==1:
                    for s in (-1,1):
                        uu=u+s*(ww*.78+.12)
                        face.part('open shutter leaf',uu,-.14,z+.60+wh/2,ww*.44,.075,wh,'shutter','shutters',0)
                        for k in range(11):face.part('shutter louvre',uu,-.19,z+.67+k*(wh-.16)/10,ww*.40,.025,.065,'shutter_light','shutters',0)
                face.part('enclosed room back',u,2.5,z+1.4,3,.15,2.6 if level==1 else 1.7,'interior','rooms',0)
                face.part('occupied cabinet',u,1.4,z+.7,1.2,.6,1.1,'timber','rooms',0)
        # Continuous rough stone base and corner quoins share one stone authority.
        for u in (.20,length-.20):
            for i in range(19):face.part('alternating stone quoin',u,.02,.25+i*.48,.52 if i%2 else .75,.52,.44,'stone','quoins',0)
        if face != front:
            face.part('continuous stone base',length/2,-.025,.37,length,.16,.52,'stone','foundation edge',0)
    # Gable roof with weather-tight deck, raised clay canal rows and seated ridge.
    eave=9.45;rise=2.1;half=7.0
    for side in (-1,1):
        C.solid_surface('closed terracotta roof',[(-9.65,0,eave+rise),(9.65,0,eave+rise),(9.65,side*half,eave),(-9.65,side*half,eave)],.18,'roof','roof')
        for i in range(58):
            x=-9.5+i*19/57
            for j in range(15):
                y0=side*j*half/15;y1=side*(j+1)*half/15
                z0=eave+rise*(1-abs(y0)/half)+.07;z1=eave+rise*(1-abs(y1)/half)+.07
                axis=C.Vector((0,y1-y0,z1-z0)).normalized();across=C.Vector((1,0,0));normal=across.cross(axis)
                if normal.z<0:normal=-normal
                vs=[]
                for point,radius in ((C.Vector((x,y0,z0)),.095),(C.Vector((x,y1,z1)),.12)):
                    vs.extend(tuple(point+across*(radius*math.cos(k*math.pi/8))+normal*(radius*math.sin(k*math.pi/8))) for k in range(9))
                C.mesh('overlapping tapered canal tile',vs,[(k,k+1,k+10,k+9) for k in range(8)],'roof','roof tile')
        C.beam('continuous eaves gutter',(-9.6,side*half,eave-.08),(9.6,side*half,eave-.08),.13,.16,'hardware','drainage')
    C.rod('seated ridge tile',(-9.65,0,eave+rise+.08),(9.65,0,eave+rise+.08),.15,'roof','roof tile',12)
    edge=eave+rise*(1-6.5/half)-.18
    for x in (-9,9):C.prism('closed roof gable',[(-6.5,9.3),(6.5,9.3),(6.5,edge),(0,eave+rise-.18),(-6.5,edge)],'x',x-.18,x+.18,'wall')
    for x in (-9.1,9.1):
        for y in (-6.45,6.45):C.rod('connected downpipe',(x,y,.2),(x,y,9.4),.055,'hardware','drainage')
    for x in (-6,0,6):
        box('terracotta arcade floor',(x,-5,.175),(5.5,2.8,.025),'roof','portico')
    B.table(6,-5,.19)
    C.CONTACTS.append(dict(id='villa-arcade',relationship='Open stone arches bear on full-height piers; occupied rooms recessed behind a continuous portico.'))

def cinema():
    w,d=24,38;front,right,rear,left=B.faces(w,d)
    C.prism('theatre stepped foundation',[(-12,-19),(12,-19),(12,19),(-10,19),(-10,3),(-12,3)],'z',0,.20,'foundation')
    box('lobby floor',(0,-14,.22),(23.4,9.5,.12),'floor','lobby')
    # Ground doors occupy real wall cuts; side poster bays have solid backing.
    B.open_wall(front,w,.2,4.7,[dict(id='lobby-door-'+str(i),u=7+i*2,z=.2,w=1.75,h=3.25,cols=2,door=True,frame='bronze') for i in range(6)])
    box('lobby entrance step',(0,-19.35,.05),(12.2,.7,.10),'foundation','entrance')
    box('lobby entrance landing',(0,-19.15,.15),(12,.3,.10),'foundation','entrance')
    for i in range(6):
        for dx in (-.12,.12):C.rod('lobby door pull',(-5+i*2+dx,-18.92,1.1),(-5+i*2+dx,-18.92,1.6),.018,'bronze','entrance')
    for u in (1.65,4,20,22.35):
        front.part('poster cabinet',u,-.12,1.8,1.62,.12,2.35,'bronze','poster bays',0)
        front.part('poster inset',u,-.20,1.8,1.43,.05,2.16,'roof','poster bays',0)
    # Two arched upper windows. Carrier spandrels and glass share the same arc.
    for ox in (-12,4):
        wing=C.Face((ox,-19,4.7),(1,0,0),(0,1,0),'arched theatre wing')
        arch_carrier(wing,8,9.5,[4],2.05,4.0,.40)
        box('arched window sill',(ox+4,-19.03,4.73),(4.4,.58,.12),'bronze','arched windows')
        pts=[(4-2.05,0),(4+2.05,0)]+[(4+2.05*math.cos(a),4+2.05*math.sin(a)) for a in [i*math.pi/32 for i in range(33)]]
        wing.panel('recessed arched optical glass',pts,.20,.009,'glass','arched windows')
        for i in range(9):
            xx=-2.0+i*.5;top=4+math.sqrt(max(0,2.05**2-xx**2))
            wing.part('arch vertical lattice',4+xx,.12,top/2,.035,.07,top,'bronze','arched windows',0)
        for zz in (.3,1.05,1.8,2.55,3.3,4.0,4.75,5.5):
            half=2.05 if zz<=4 else math.sqrt(2.05**2-(zz-4)**2)
            wing.part('arch horizontal lattice',4,.12,zz,half*2,.07,.035,'bronze','arched windows',0)
        # Visible gallery depth and low furniture, never a blank card at glass.
        box('gallery occupied floor',(ox+4,-16,4.67),(7.6,5.6,.18),'floor','gallery')
        box('gallery rear wall',(ox+4,-12.2,8.6),(7.8,.25,7.8),'interior','gallery')
        B.table(ox+4,-16,4.76)
    central=C.Face((-4,-19,0),(1,0,0),(0,1,0),'central stepped frontage')
    holes=[dict(id=f'central-window-{i}-{j}',u=1.55+i*4.9,z=zz,w=1.7,h=hh,frame='bronze') for i in range(2) for j,(zz,hh) in enumerate(((4.9,4.7),(10,5.3)))]
    B.open_wall(central,8,4.7,16.2,holes)
    for x in (-3.9,0,3.9):box('central vertical pier',(x,-19.15,10.5),(.46,.65,11.6),'wall','deco frontage')
    for x in (-3.3,3.3):box('gilded flute',(x,-19.5,14.8),(.16,.12,3.2),'bronze','deco frontage')
    for x,width,height in ((0,7.8,.45),(0,6.5,.45),(0,5.2,.45)):
        zz=16.2+(7.8-width)/1.3*.45
        box('stepped crown',(x,-18.75,zz+height/2),(width,1.0,height),'wall','deco crown')
    # Ornament is relief geometry with bounded repetitive motifs.
    for ox in (-12,4):
        for zz in (12.1,12.65,13.55):box('wing frieze band',(ox+4,-19.12,zz),(7.9,.24,.16),'stone','deco frieze')
        for i in range(16):
            x=ox+.3+i*.49
            box('frieze inset panel',(x,-19.18,13.03),(.32,.08,.36),'wall','deco frieze')
            box('gilded frieze tile',(x,-19.23,13.55),(.30,.045,.12),'bronze','deco frieze')
            for k in range(3):box('stepped ornament',(x+(k-1)*.085,-19.2,12.05+k*.075),(.045,.10,.18),'bronze','deco frieze')
    # Enclosed auditorium and side exits, above-grade floor and closed roof.
    stepped_left=C.Face((-10,19,0),(0,-1,0),(1,0,0),'rear stepped left')
    front_left=C.Face((-12,3,0),(0,-1,0),(1,0,0),'front left')
    for face,length,exits in ((right,38,(9,29)),(front_left,22,(13,)),(stepped_left,16,(8,))):
        B.open_wall(face,length,.2,14.2,[dict(id=face.label+'-exit-'+str(i),u=u,z=.2,w=1.7,h=2.65,door=True) for i,u in enumerate(exits)])
        for u in range(2,int(length),4):face.part('auditorium buttress',u,-.10,7.1,.48,.44,14.2,'wall','auditorium',0)
    box('left plan return',(-11,2.82,7.1),(2,.36,14.2),'wall','stepped plan')
    B.open_wall(rear,22,.2,18,[dict(id='rear-service',u=11,z=.2,w=3.4,h=3.5,door=True)])
    box('auditorium opaque rear division',(1,12,7),(21.6,.3,13.7),'interior','auditorium')
    box('auditorium ceiling',(0,-1,14),(24,36,.25),'roof','roof')
    box('right continuous parapet',(11.8,0,14.5),(.4,38,1),'wall','roof')
    for x,y,length in ((-11.8,-8,22),(-9.8,11,16)):box('left stepped parapet',(x,y,14.5),(.4,length,1),'wall','roof')
    box('left parapet return',(-11,2.8,14.5),(2,.4,1),'wall','roof')
    box('rear fly-tower mass',(1,15,16.1),(22,8,4.2),'wall','fly tower')
    box('fly-tower weather roof',(1,15,18.24),(21.5,7.5,.16),'roof','roof')
    # Raised glazed roof lantern, physically seated over a real roof opening.
    # Partition ceiling so the lantern owns its aperture.
    ceiling=C.bpy.data.objects.get('auditorium ceiling')
    C.bpy.data.objects.remove(ceiling,do_unlink=True)
    box('right roof side deck',(7.5,-4,14),(9,30,.25),'roof','roof')
    box('front left roof deck',(-7.5,-8,14),(9,22,.25),'roof','roof')
    box('stepped left roof deck',(-6.5,7,14),(7,8,.25),'roof','roof')
    for yy,dd in ((-15,8),(7,8)):box('roof cross deck',(0,yy,14),(6,dd,.25),'roof','roof')
    for x in (-3,3):box('lantern curb',(x,-4,14.3),(.2,14,.6),'stone','roof lantern')
    for y in (-11,3):box('lantern curb',(0,y,14.3),(6,.2,.6),'stone','roof lantern')
    for side in (-1,1):
        C.solid_surface('lantern glazed pitch',[(0,-11,16),(0,3,16),(side*3,3,14.6),(side*3,-11,14.6)],.014,'glass','roof lantern')
        for y in range(-11,4):C.beam('lantern rafter',(0,y,16.04),(side*3,y,14.63),.055,.065,'bronze','roof lantern')
        C.beam('lantern eaves',(side*3,-11,14.63),(side*3,3,14.63),.07,.08,'bronze','roof lantern')
    for y in (-11,3):C.prism('lantern closed gable',[(-3,14.6),(3,14.6),(0,16)],'y',y-.02,y+.02,'glass','roof lantern')
    # Roof plant sits on bearing pads, with visible fans and connected ducts.
    for x,y in ((-8,-6),(8,-3),(-6,7),(5,7)):
        box('plant bearing pad',(x,y,14.22),(2.9,3.3,.18),'stone','roof services')
        box('roof air handler',(x,y,14.95),(2.5,2.9,1.3),'stone','roof services')
        for dx in (-.6,.6):
            C.rod('fan grille',(x+dx,y,15.61),(x+dx,y,15.64),.48,'hardware','roof services',24)
            for n in range(5):box('fan guard',(x+dx,y-.36+n*.18,15.66),(.80,.025,.025),'stone','roof services')
        box('seated service duct',(x,y+2.0,14.55),(.75,1.8,.65),'hardware','roof services')
    # Marquee, suspended by visible stays; perimeter fascia and warm lamps.
    box('marquee canopy',(0,-21,4.25),(20,4,.30),'roof','marquee')
    for yy in (-23,-19.1):box('marquee fascia',(0,yy,4.9),(20,.2,1.2),'bronze','marquee')
    for x in (-10,10):box('marquee return',(x,-21,4.9),(.20,4,1.2),'bronze','marquee')
    for z in (4.4,4.65,4.9,5.15,5.4):
        box('marquee horizontal gold fillet',(0,-23.14,z),(20,.055,.035),'white','marquee detail')
        for x in (-10.14,10.14):box('marquee return fillet',(x,-21,z),(.055,4,.035),'white','marquee detail')
    for side in (-1,1):
        C.rod('marquee suspension stay',(side*9.7,-22.8,4.3),(side*10.8,-19.06,8.2),.035,'hardware','marquee')
        box('stay masonry anchor plate',(side*10.8,-19.04,8.2),(.28,.16,.32),'hardware','marquee')
    for x in range(-9,10):
        for y in (-19.7,-21,-22.4):
            C.bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=.07,location=(x,y,4.06))
            o=C.bpy.context.object;o.data.materials.append(C.MATS['light']);C.tag(o,'light','marquee lamps')
    for x in range(-9,10,2):
        f=C.Face((x,-23.15,0),(1,0,0),(0,1,0),'marquee fan')
        arch_ring(f,'gold fan',0,5.52,.22,.055,.06,'bronze')
    for x in (-9.75,0,9.75):
        box('marquee stepped finial',(x,-23.12,5.35),(.86,.22,1.75),'wall','marquee ornament')
        for dx in (-.30,-.15,0,.15,.30):
            box('marquee finial gold reed',(x+dx,-23.26,5.3),(.035,.06,1.2+(1-abs(dx)/.3)*.4),'bronze','marquee ornament')
    # Blade is perpendicular to frontage, with gold letters on BOTH long faces.
    box('deco blade',(0,-21,13.75),(.46,3.0,13.5),'wall','blade sign')
    for x in (-.26,.26):
        box('blade black enamel',(x,-21,13.75),(.05,2.55,12.9),'roof','blade sign')
        for y in (-22.33,-19.67):box('blade gold border',(x,y,13.75),(.09,.05,12.95),'bronze','blade sign')
        for z in (7.3,20.2):box('blade gold border',(x,-21,z),(.09,2.65,.05),'bronze','blade sign')
        for i,char in enumerate('CINEMA'):
            C.bpy.ops.object.text_add(location=(x*1.15,-21,18.65-i*1.8))
            o=C.bpy.context.object;o.data.body=char;o.data.align_x='CENTER';o.data.size=1.30;o.data.extrude=.016
            o.rotation_euler=(math.pi/2,0,math.pi/2 if x>0 else -math.pi/2)
            C.bpy.ops.object.convert(target='MESH');o=C.bpy.context.object;o.data.materials.append(C.MATS['bronze']);C.tag(o,'bronze','blade lettering')
    for z in (8,12,16):C.beam('blade steel attachment',(0,-20,z),(0,-18.5,z+.65),.13,.13,'hardware','blade support')
    for i,width in enumerate((3.4,2.5,1.65)):
        box('stepped blade crown',(0,-21,20.62+i*.32),(.52,width,.32),'wall','blade crown')
    for x in (-.285,.285):
        for i in range(7):
            yy=(i-3)*.34
            C.beam('blade sunburst ray',(x,-21,20.28),(x,-21+yy,21.40-abs(yy)*.3),.042,.042,'bronze','blade crown')
    B.label('GRAND',(-4,-23.20,4.68),.45,'hardware');B.label('CINEMA',(4,-23.20,4.68),.45,'hardware')
    # Lobby details visible behind the doors.
    box('ticket counter',(0,-14.5,.8),(4,.8,1.25),'bronze','lobby')
    for x in (-8,8):B.table(x,-16,.28)
    for i in range(6):box('lobby wall light',(-11.7,-18+i*1.1,2.5),(.08,.20,.65),'light','lobby')
    C.CONTACTS.append(dict(id='cinema-assembly',relationship='Cut arched glazing, occupied lobby and galleries, seated roof lantern, supported marquee and double-sided attached blade.'))

def cameras(kind):
    s=SPECS[kind];w,d,h=s['width'],s['depth'],s['height'];target=(0,0,h*.45);r=max(w,d,h)*1.8
    roster=[dict(name=n,location=p,target=target,ortho_scale=max(w,d,h)*1.45) for n,p in
        [('front',(0,-r,h*.45)),('left_side',(-r,0,h*.45)),('right_side',(r,0,h*.45)),('rear',(0,r,h*.45))]]
    roster += [dict(name='front_corner',location=(w*1.6,-d*1.8,h*1.1),target=target),
        dict(name='aerial',location=(w*1.5,-d*1.5,max(w,d,h)*1.9),target=target),
        dict(name='top',location=(0,0,h+150),target=(0,.001,0),ortho_scale=max(w,d)*1.4),
        dict(name='rear_side',location=(-w*1.6,d*1.8,h*1.1),target=target)]
    close=[('facade_close',(6,-23,13),(2,-8,11)),('architecture_close',(19,-20,22),(4,-5,17)),
           ('glass_close',(2,-15,2),(-.3,-7,1.6)),('walk',(17,-32,1.65),(0,0,10)),
           ('roof_garden',(18,-22,30),(-1,0,20.5))]
    if kind=='villa':
        close=[('facade_close',(8,-19,7),(1,-6,5)),('architecture_close',(19,-17,13),(0,0,7)),
            ('glass_close',(0,-10,5.8),(0,-6.2,5.6)),('walk',(19,-28,1.65),(0,0,5)),
            ('arcade_access',(-4,-10,1.7),(-6,-3.5,1.7))]
    elif kind=='cinema':
        close=[('facade_close',(17,-38,13),(5,-20,9)),('architecture_close',(15,-30,24),(0,-19,15)),
            ('glass_close',(-6,-26,2),(-2,-15,1.7)),('walk',(25,-43,1.65),(0,-19,9)),
            ('roof_lantern',(24,-18,30),(0,-3,14.5)),('arched_glazing',(-8,-24,8),(-8,-17,8))]
    roster += [dict(name=n,location=p,target=t,whole=False,lens=38) for n,p,t in close]
    return roster

def main():
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=SPECS,required=True);p.add_argument('--lock',type=Path,required=True)
    p.add_argument('--output',required=True);p.add_argument('--version',type=int,default=1);p.add_argument('--dry-run',action='store_true');p.add_argument('--kit',type=Path,required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);s=SPECS[a.kind]
    source=next(e for e in json.loads(a.lock.read_text())['entries'] if e['kind']==a.kind)
    entry=dict(archetype_id=source['archetype_id'],variant_id=source['variant_id'],directory='.',
        _reference_root=str(Path(source['sources'][0]['path']).parent),
        sources=[dict(v,original_path=v['path'],path='sources/'+Path(v['path']).name) for v in source['sources']])
    roster=cameras(a.kind)
    manifest=dict(candidate=f'autumn-{a.kind}-clay-v{a.version:03d}',method=C.METHOD,representation_kind='architectural_clay',
        archetype_id=entry['archetype_id'],variant_id=entry['variant_id'],camera_roster=roster,state='prework',keeper_claimed=False,runtime_seed_allowed=False,
        measurement_contract=dict(dimensions_m={k:s[k] for k in ('width','depth','height')},floors=s['floors'],front='-Y',bottom_datum_m=0,
            measurement_basis='Exact source-view ratios and plausible metric modules; conceptual dimensions, not surveyed.'),
        identity_contract=[s['signature']],hidden_view_assumptions=['Unseen rear/interior room arrangements inferred; visible source topology retained.'],
        limitations=['Fixed native geometry; runtime/browser acceptance pending.','Architectural-clay tier; no textured keeper or construction claim.'])
    manifest['native_vegetation_kit']=dict(path=str(a.kit.resolve()),sha256=C.digest(a.kit))
    out=C.prepare_candidate(a,entry,manifest,__file__,[HERE.parent/'showcase_building_trio/build.py'])
    if out is None:return
    palette=dict(B.PALETTE,wall=(.49,.31,.15),timber=(.57,.37,.18),timber_dark=(.25,.14,.06),leaf=(.16,.25,.07),leaf_light=(.31,.36,.10),roof=(.17,.17,.14))
    if a.kind=='villa':palette.update(wall=(.64,.46,.25),stone=(.46,.44,.34),roof=(.40,.17,.075),trim=(.26,.32,.14),shutter=(.10,.19,.085),shutter_light=(.16,.24,.11))
    if a.kind=='cinema':palette.update(wall=(.36,.11,.068),stone=(.43,.22,.12),roof=(.12,.13,.13),light=(1,.76,.28),bronze=(.65,.42,.13))
    cams=C.setup(palette,roster,1440);C.fit=B.efficient_fit;C.bevel=lambda *args,**kwargs:None
    load_vegetation(a.kit)
    if a.kind=='cinema':
        # The inherited small-house QA rig intersects this deep auditorium.
        # Keep inspection lights outside its complete occupied envelope.
        for label,location in [('key',(-32,-46,50)),('fill',(38,-8,35)),('rear',(-24,40,45))]:
            light=C.bpy.data.objects['QA '+label];light.location=location;light.data.energy*=5
            C.look_at(light,(0,0,8))
        bs=C.MATS['light'].node_tree.nodes['Principled BSDF'];bs.inputs['Emission Color'].default_value=(1,.70,.20,1);bs.inputs['Emission Strength'].default_value=.8
    C.bpy.context.scene.cycles.samples=24
    C.bpy.ops.object.light_add(type='SUN');sun=C.bpy.context.object;sun.rotation_euler=(.45,-.5,-.45);sun.data.energy=2;sun.data.angle=.16
    globals()[a.kind]()
    C.deliver(out,manifest,cams)

if __name__=='__main__':main()
