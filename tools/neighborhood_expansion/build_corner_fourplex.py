"""Four separate homes, two independent street-facing cores, intersecting roofs."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import delivery as D
from delivery import C,B,R,bpy

Z=.14
RISE=3.45
OBS=[]
PALETTE=dict(B.PALETTE,wall=(.57,.55,.49),trim=(.095,.105,.10),roof=(.12,.15,.18),
    timber=(.50,.30,.14),interior=(.78,.76,.68),floor=(.53,.42,.28),furniture=(.31,.39,.33),
    glass=(.96,.98,.98),ceiling=(.82,.81,.76),lamp=(.96,.85,.66),leaf=(.22,.31,.11),flower=(.6,.54,.30))


def h(name,u,z,w,ht,door=False):return dict(id=name,u=u,z=z,w=w,h=ht,door=door)


def wall(face,a,b,z0,z1,holes=(),role='wall',depth=.30,glazed=False,flat_door=False):
    face.wall(face.label,a,b,z0,z1,depth,role,holes)
    cuts=sorted([v for v in holes if v.get('door')],key=lambda v:v['u'])
    edges=[a]
    for v in cuts:edges.extend([v['u']-v['w']/2,v['u']+v['w']/2])
    edges.append(b)
    for lo,hi in zip(edges[::2],edges[1::2]):
        pts=[face.p(u,d,0) for u in (lo,hi) for d in (0,depth)]
        OBS.append([min(v[0] for v in pts),max(v[0] for v in pts),min(v[1] for v in pts),max(v[1] for v in pts),z0,z1])
    for v in holes:
        if v.get('door'):
            u,z,w,ht=v['u'],v['z'],v['w'],v['h']
            if glazed:
                for s in (-1,1):face.part(v['id']+' door jamb',u+s*(w/2-.03),.20,z+ht/2,.06,.16,ht,'trim')
                face.part(v['id']+' lintel',u,.20,z+ht,w,.16,.06,'trim')
                leaf=C.Face(face.p(u-w/2+.07,-.05,0),tuple(-n for n in face.n),face.t,v['id']+' open leaf')
                leaf.window(v['id']+' open leaf',(w-.14)/2,z,w-.14,ht-.06,1,1,'trim',.03,sill=False,depth=.1)
                for s in (-1,1):face.part(v['id']+' cedar reveal',u+s*(w/2-.025),.13,z+ht/2,.055,.30,ht,'timber')
                face.part(v['id']+' cedar soffit',u,.13,z+ht-.025,w,.30,.06,'timber')
            elif flat_door:
                for s in (-1,1):face.part(v['id']+' jamb',u+s*(w/2-.025),.07,z+ht/2,.05,.14,ht,'trim')
                face.part(v['id']+' lintel',u,.07,z+ht,w,.14,.06,'trim')
                face.part(v['id']+' open leaf',u-w+.09,-.05,z+ht/2,w-.09,.06,ht-.06,'timber','interior')
            else:R.open_door(face,v['id'],u,z,w,ht)
        else:
            face.window(v['id'],v['u'],v['z'],v['w'],v['h'],3 if v['w']>2 else 1,1,'trim',.16,.045,False,False,depth)
            face.part(v['id']+' stone sill',v['u'],.01,v['z']-.04,v['w']+.15,.39,.08,'stone')


def lamp(name,x,y,z,power=180):
    obj=C.qa_room_light(name,(x,y,z+2.94),power,2.1)
    if hasattr(obj.data,'specular_factor'):obj.data.specular_factor=0
    R.lamp(x,y,z+3.10,.65)


def kitchen(x,y,z):
    C.box('kitchen base',(x,y,z+.44),(.65,2.8,.88),'timber','furniture')
    top=C.box('kitchen stone counter',(x,y,z+.905),(.72,2.85,.06),'stone','furniture')
    C.cut_box(top,'real counter sink cut',(x,y-.50,z+.905),(.44,.64,.20))
    bowl=C.box('kitchen sink body',(x,y-.50,z+.79),(.47,.67,.24),'hardware','furniture')
    C.cut_box(bowl,'sink recess',(x,y-.50,z+.88),(.40,.60,.32))
    C.rod('kitchen tap',(x+.23,y-.50,z+.93),(x+.23,y-.50,z+1.22),.02,'hardware','furniture')
    C.rod('kitchen tap spout',(x+.23,y-.50,z+1.22),(x+.01,y-.50,z+1.22),.02,'hardware','furniture')
    C.box('cooktop',(x,y+.58,z+.945),(.54,.70,.035),'hardware','furniture')
    for dx in (-.15,.15):
        for dy in (.39,.76):C.rod('hob ring',(x+dx,y+dy,z+.966),(x+dx,y+dy,z+.972),.10,'trim','furniture',16)
    C.box('upper cupboard',(-.315 if x<0 else .185,y+.5,z+1.97),(.37,1.7,.75),'timber','furniture')
    C.box('refrigerator',(x,y+1.92,z+.97),(.80,.80,1.94),'ceiling','furniture')
    for dy in (-.9,0,.9):C.box('cabinet pull',(x+.36,y+dy,z+.72),(.026,.25,.025),'hardware','furniture')


def bed(x,y,z):
    C.box('bed frame',(x,y,z+.22),(1.9,2.1,.44),'timber','furniture')
    C.box('bed mattress',(x,y,z+.52),(1.85,2.05,.17),'interior','furniture')
    C.box('bed headboard',(x,y+.99,z+.65),(1.94,.12,1.15),'timber','furniture')
    for dx in (-.45,.45):C.box('bed pillow',(x+dx,y+.65,z+.65),(.68,.43,.16),'ceiling','furniture')
    C.box('bed throw',(x,y-.55,z+.625),(1.87,.82,.025),'furniture','furniture')


def bathroom(cx,cy,z):
    # Compact real fixtures, with a clear offset doorway aisle.
    tx=cx+.55;ty=cy+.72
    C.box('toilet pedestal',(tx,ty,z+.22),(.34,.47,.44),'ceiling','furniture')
    rim=C.box('toilet bowl rim',(tx,ty-.06,z+.46),(.48,.66,.14),'ceiling','furniture')
    C.cut_box(rim,'toilet bowl opening',(tx,ty-.12,z+.50),(.25,.37,.22))
    C.box('toilet cistern',(tx,ty+.24,z+.65),(.43,.20,.72),'ceiling','furniture')
    sx=cx-.73;sy=cy+.61
    C.box('bath vanity',(sx,sy,z+.40),(.66,.65,.80),'timber','furniture')
    rim=C.box('bath basin',(sx,sy,z+.86),(.70,.68,.13),'ceiling','furniture')
    C.cut_box(rim,'basin recess',(sx,sy-.03,z+.92),(.45,.44,.14))
    C.rod('bath tap',(sx,sy+.22,z+.93),(sx,sy+.22,z+1.12),.02,'hardware','furniture')
    C.rod('bath spout',(sx,sy+.22,z+1.12),(sx,sy+.08,z+1.12),.02,'hardware','furniture')
    C.box('bath mirror',(sx,cy+1.10,z+1.51),(.65,.025,.70),'glass','furniture')
    sx=cx-.73;sy=cy-.57
    C.box('shower tray',(sx,sy,z+.065),(.92,.95,.13),'stone','furniture')
    C.box('shower back screen',(sx-.44,sy,z+1.06),(.012,.95,1.96),'glass','furniture')
    C.rod('shower riser',(sx-.40,sy,z+.85),(sx-.40,sy,z+2.13),.018,'hardware','furniture')
    C.rod('shower head',(sx-.40,sy,z+2.13),(sx-.17,sy,z+2.13),.05,'hardware','furniture')
    wall_x=cx-1.35 if cx<0 else cx-1.45+.13
    for zz in (1.05,1.90):C.rod('shower wall bracket',(wall_x,sy,z+zz),(sx-.40,sy,z+zz),.025,'hardware','furniture')


def partition(face,a,b,z,doors,flat_door=False):wall(face,a,b,z,z+3.31,doors,'interior',.13,flat_door=flat_door)


def inner_stair_guard(sx,sg,side):
    x=sx+side*.0525;r=RISE/22;points=[]
    for j in range(11):
        zz=Z+(j+1)*r if side<0 else Z+RISE-j*r
        points.append((x,sg*(-5.5+j*.25),zz))
    points=[(x,sg*-5.625,points[0][2])]+points+[(x,sg*-2.875,points[-1][2])]
    for p in points:C.rod('inner stair guard post',p,(p[0],p[1],p[2]+1.02),.018,'trim','stair guard')
    for a,b in zip(points,points[1:]):
        mid=((a[0]+b[0])/2,(a[1]+b[1])/2,(a[2]+b[2])/2)
        C.rod('inner stair intermediate picket',(mid[0],mid[1],max(a[2],b[2])),(mid[0],mid[1],mid[2]+1.02),.016,'trim','stair guard')
        C.beam('inner stair handrail',(a[0],a[1],a[2]+1.02),(b[0],b[1],b[2]+1.02),.042,.038,'trim','stair guard')
        C.beam('inner stair lower rail',(a[0],a[1],a[2]+.10),(b[0],b[1],b[2]+.10),.025,.025,'trim','stair guard')


def roof():
    a=2.6/4.25;b=2.05/7.5;yb=7.75;edge=9.05-b*yb
    junction=-4.25+(9.6-9.05)/a;val=-4.25+(9.6-edge)/a
    C.solid_surface('left outer roof',[(-8.75,-yb,7-.25*a),(-4.25,-yb,9.6),(-4.25,yb,9.6),(-8.75,yb,7-.25*a)],.12)
    for sign in (-1,1):
        yy=sign*yb
        C.solid_surface('left inner clipped roof',[(-4.25,yy,9.6),(val,yy,edge),(junction,0,9.05),(-4.25,0,9.6)],.12)
        C.solid_surface('right cross roof',[(val,yy,edge),(8.75,yy,edge),(8.75,0,9.05),(junction,0,9.05)],.12)
        C.beam('roof valley flashing',(val,yy,edge+.018),(junction,0,9.068),.16,.028,'roof','roof')
    for j in range(30):
        y=-7.5+j*.515;v=-4.25+(9.6-(9.05-b*abs(y)))/a
        C.beam('left outer standing seam',(-8.75,y,7-.25*a+.026),(-4.25,y,9.626),.018,.026,'roof','roof')
        C.beam('left inner standing seam',(-4.25,y,9.626),(v,y,9.05-b*abs(y)+.026),.018,.026,'roof','roof')
    for j in range(24):
        x=junction+.25+j*.51
        if x>8.7:continue
        reach=min(yb,(x-junction)/(b/a))
        for sign in (-1,1):C.beam('right standing seam',(x,0,9.076),(x,sign*reach,9.05-b*reach+.026),.018,.026,'roof','roof')
    C.rod('left ridge cap',(-4.25,-7.8,9.63),(-4.25,7.8,9.63),.055,'roof','roof')
    C.rod('right ridge cap',(junction,0,9.08),(8.8,0,9.08),.055,'roof','roof')
    for y in (-7.5,7.2):C.prism('left end gable',[(-8.5,7),(-4.25,9.6),(0,7)],'y',y,y+.30,'wall')
    C.prism('right side gable',[(-7.5,7),(0,9.05),(7.5,7)],'x',8.2,8.5,'wall')
    for y in (-7.76,7.76):
        C.beam('gable fascia',(-8.75,y,6.82),(-4.25,y,9.53),.14,.14,'timber','roof')
        C.beam('gable fascia',(-4.25,y,9.53),(val,y,edge-.07),.14,.14,'timber','roof')
        C.rod('front rear gutter',(val,y,edge-.06),(8.75,y,edge-.06),.055,'roof','roof')
    for x,y in ((.1,-7.77),(8.65,7.70),(-8.65,7.70)):
        C.rod('rainwater pipe',(x,y,.13),(x,y,6.94),.05,'roof','site')


def build():
    C.box('site base',(0,0,.02),(23,23,.04),'paving','site',0)
    C.box('front approach',(-6.7,-9.5,.09),(2.2,4,.10),'paving','site',0)
    C.box('side approach',(10,6.2,.09),(3,2.2,.10),'paving','site',0)
    for level in range(2):
        z=Z+level*RISE;lo=level*RISE;hi=(level+1)*RISE if not level else 7
        front=C.Face((0,-7.5,0),(1,0,0),(0,1,0),'front '+str(level))
        holes=[h('front living '+str(level)+' '+str(x),x,z+.70,3.6,2.1) for x in (-2.7,4.25)]
        holes.append(h('front stair window',-6.7,z+.80,1.05,1.85) if level else h('front shared entrance',-6.7,Z,1.8,2.72,True))
        wall(front,-8.5,8.5,lo,hi,holes,glazed=True)
        east=C.Face((8.5,0,0),(0,1,0),(-1,0,0),'east '+str(level))
        holes=[h('east window '+str(level)+' '+str(y),y,z+1.05,1.2,1.8) for y in (-4.7,-.2,3.3) if level or y!=3.3]
        if not level:holes.append(h('side shared entrance',6.2,Z,1.8,2.72,True))
        wall(east,-7.2,7.2,lo,hi,holes,glazed=True)
        west=C.Face((-8.5,0,0),(0,1,0),(1,0,0),'west '+str(level))
        wall(west,-7.2,7.2,lo,hi,[h('west stair '+str(level),-3,z+1.2,1.3,1.5),h('west bath '+str(level),2.1,z+1.6,.9,1),h('west bed '+str(level),5.5,z+.9,1.8,1.9)])
        rear=C.Face((0,7.5,0),(1,0,0),(0,-1,0),'rear '+str(level))
        wall(rear,-8.5,8.5,lo,hi,[h('rear bedroom '+str(level)+' '+str(x),x,z+.9,2.4,1.9) for x in (-4.8,1.9)]+[h('rear stair '+str(level),6.7,z+1.1,1.1,1.5)])
        floor=C.box('occupied floor',(0,0,z-.07),(16.4,14.4,.14),'floor','floors',0)
        ceiling=C.box('interior ceiling',(0,0,z+3.255),(16.4,14.4,.10),'ceiling','ceiling',0)
        for sx,mirror in [(-6.7,False),(6.7,True)]:
            cy=3.6875 if mirror else -3.6875
            if level:C.cut_box(floor,'stairwell floor opening',(sx,cy,z),(2.68,3.875,.6))
            if not level:C.cut_box(ceiling,'stairwell ceiling opening',(sx,cy,z+3.255),(2.68,3.875,.6))
        partition(C.Face((0,0,0),(0,1,0),(-1,0,0),'party wall '+str(level)),-7.2,7.2,z,[])
        partition(C.Face((-5.2,0,0),(0,1,0),(1,0,0),'left core '+str(level)),-7.2,-1.45,z,[h('left flat '+str(level),-6.2,z,1.2,2.30,True)])
        partition(C.Face((-6.7,-1.45,0),(1,0,0),(0,-1,0),'left core back '+str(level)),-1.5,1.5,z,[])
        partition(C.Face((5.2,0,0),(0,-1,0),(-1,0,0),'right core '+str(level)),-7.2,-1.45,z,[h('right flat '+str(level),-6.2,z,1.2,2.30,True)])
        partition(C.Face((6.7,1.45,0),(1,0,0),(0,1,0),'right core back '+str(level)),-1.5,1.5,z,[])
        # Left apartment: living front, independent bath, full bedroom at rear.
        partition(C.Face((-4.2,3.3,0),(1,0,0),(0,1,0),'left bedroom '+str(level)),-4,4.2,z,[h('left bedroom door '+str(level),1,z,1.15,2.25,True)])
        # Right apartment: entry corridor reaches all rooms without crossing bedroom.
        partition(C.Face((3.65,5.15,0),(0,1,0),(-1,0,0),'right bedroom '+str(level)),-1.85,2.05,z,[h('right bedroom door '+str(level),-.95,z,1.1,2.25,True)])
        partition(C.Face((1.9,3.3,0),(1,0,0),(0,1,0),'right bedroom front '+str(level)),-1.9,1.75,z,[])
        for label,cx,cy,w,d in [('left',-6.85,2.1,2.7,2.4),('right',6.75,-.35,2.9,2.5)]:
            face=C.Face((cx,cy-d/2,0),(1,0,0),(0,1,0),label+' bathroom front '+str(level))
            partition(face,-w/2,w/2,z,[h(label+' bath door '+str(level),.4,z,1.05,2.25,True)],flat_door=True)
            if label=='right':partition(C.Face((cx-w/2,cy,0),(0,1,0),(1,0,0),label+' bath left '+str(level)),-d/2,d/2,z,[])
            if label=='left':partition(C.Face((cx+w/2,cy,0),(0,1,0),(-1,0,0),label+' bath right '+str(level)),-d/2,d/2,z,[])
            partition(C.Face((cx,cy+d/2,0),(1,0,0),(0,-1,0),label+' bath back '+str(level)),-w/2,w/2,z,[])
            bathroom(cx,cy,z);lamp(label+' bath',cx,cy,z,90)
        B.sofa(-2.65,-4.6,z);B.desk(-3.0,-.45,z,False);kitchen(-.65,.05,z);bed(-6.0,5.5,z)
        B.sofa(3.2,-5.3,z);B.desk(5.2,-3.8,z,False);kitchen(.70,-.15,z);bed(1.8,5.6,z)
        for x,y in [(-2.9,-4.1),(-3.5,.1),(-5.3,5.5),(3.4,-5),(2,-.2),(1.8,5.5)]:lamp('occupied apartment',x,y,z,130)
    # Two proven U stairs; right is reflected to face the rear-side entrance.
    R.stair(-6.7,-5.5,Z,RISE,1.05)
    before=set(C.objects());R.stair(6.7,-5.5,Z,RISE,1.05)
    for o in set(C.objects())-before:
        for v in o.data.vertices:v.co.y=-v.co.y
        C.normalise(o.data)
    for sx,mirror in [(-6.7,False),(6.7,True)]:
        sg=-1 if mirror else 1
        for x in (sx-1.34,sx+1.34):C.railing('upper stair guard',(x,sg*-5.60,Z+RISE),(x,sg*-1.75,Z+RISE),height=1.02,spacing=.12)
        C.railing('upper stair back guard',(sx-1.34,sg*-1.75,Z+RISE),(sx+1.34,sg*-1.75,Z+RISE),height=1.02,spacing=.12)
        C.railing('upper stair lower-flight guard',(sx-1.34,sg*-5.645,Z+RISE),(sx,sg*-5.645,Z+RISE),height=1.02,spacing=.10,bottom=0)
        for side in (-1,1):inner_stair_guard(sx,sg,side)
        lamp('shared stair',sx,sg*-4.1,Z+RISE,150)
    roof()
    C.box('front entry canopy',(-6.7,-7.72,3.05),(2.1,.68,.15),'roof','structure')
    C.box('side entry canopy',(8.72,6.2,3.05),(.68,2.1,.15),'roof','structure')
    for x in (-2.7,4.25):R.plantbed(x,-8.65,4,1.1)
    R.plantbed(9.5,-1.0,1.0,10)
    for x in (-6,0,6):R.plantbed(x,9.35,3,1.2)
    B.bench(2.5,8.7)
    C.box('clear paved bicycle bay',(-9.7,8.8,.045),(2.2,2.5,.01),'paving','site',0)
    B.bikehoop(-9.7,8.2);B.bikehoop(-9.7,9.45)
    for x,y,seed in [(-10,5,101),(10,-8.5,203)]:R.tree(x,y,seed)


def network():
    tris=[];routes=[]
    def rect(a,b,c,d,z):
        p=[a,b,z];q=[c,b,z];r=[c,d,z];s=[a,d,z];tris.extend([[p,q,r],[p,r,s]])
    holes=[[-8.04,-5.36,-5.625,-1.75],[5.36,8.04,1.75,5.625]]
    xs=sorted({-8.18,8.18,*[h[j] for h in holes for j in (0,1)]})
    ys=sorted({-7.18,7.18,*[h[j] for h in holes for j in (2,3)]})
    for level in range(2):
        z=Z+level*RISE
        for a,c in zip(xs,xs[1:]):
            for b,d in zip(ys,ys[1:]):
                if any(h[0]<(a+c)/2<h[1] and h[2]<(b+d)/2<h[3] for h in holes):continue
                rect(a,b,c,d,z)
        for side in (-1,1):
            sx=side*6.7;sg=1 if side<0 else -1;sy=-5.5;w=1.05
            if level:rect(sx-1.34,min(sg*-6.05,sg*-5.625),sx+1.34,max(sg*-6.05,sg*-5.625),z)
            if not level:
                for j in range(11):
                    a=sg*(sy+j*.25-.125);b=sg*(sy+j*.25+.125)
                    rect(sx-w*1.05,min(a,b),sx-w*.05,max(a,b),z+(j+1)*RISE/22)
                    rect(sx+w*.05,min(a,b),sx+w*1.05,max(a,b),z+RISE-j*RISE/22)
                rect(sx-w*1.05,min(sg*(sy+2.625),sg*(sy+3.675)),sx+w*1.05,max(sg*(sy+2.625),sg*(sy+3.675)),z+RISE/2)
                pts=[[sx-w*.55,sg*(sy-.35),z],[sx-w*.55,sg*(sy+3.1),z+RISE/2],[sx+w*.55,sg*(sy+3.1),z+RISE/2],[sx+w*.55,sg*(sy-.35),z+RISE]]
                routes.extend([dict(name=('Left' if side<0 else 'Right')+' stair ascent',points=pts),dict(name=('Left' if side<0 else 'Right')+' stair descent',points=list(reversed(pts)))])
        def route(name,pts):routes.append(dict(name=name,points=[[x,y,z] for x,y in pts]))
        route('Left flat '+str(level)+' entry',[(-6.1,-6.2),(-4.5,-6.2),(-4.5,-2)])
        route('Left flat '+str(level)+' bedroom',[(-4.5,-2),(-4.5,2.7),(-3.2,2.7),(-3.2,4.2)])
        route('Left flat '+str(level)+' bathroom',[(-4.5,0),(-6.45,0),(-6.45,1.35)])
        route('Right flat '+str(level)+' entry',[(6.7,6.2),(4.4,6.2),(4.4,-2.5),(3.7,-2.5)])
        route('Right flat '+str(level)+' bedroom',[(4.4,6.2),(4.4,4.2),(3.0,4.2)])
        route('Right flat '+str(level)+' bathroom',[(4.4,-2.5),(7.15,-2.5),(7.15,-1.15)])
    rect(-7.78,-11.3,-5.62,-7.1,Z);rect(8.1,5.15,11.4,7.15,Z)
    rect(10.25,6.5,11.4,7.5,.04);rect(8.5,7.15,11.4,11.3,.04);rect(-11.3,7.5,11.4,11.3,.04)
    routes.extend([dict(name='Front public entrance',points=[[-6.7,-11,Z],[-6.7,-6.2,Z]]),dict(name='Side public entrance',points=[[11,6.2,Z],[6.7,6.2,Z]])])
    routes.extend([
        dict(name='Shared rear garden bench',points=[[10.8,6.2,Z],[10.8,10.6,.04],[3.9,10.6,.04],[3.9,8.1,.04],[2.5,8.1,.04]]),
        dict(name='Shared bicycle bay',points=[[10.8,10.6,.04],[-8.65,10.6,.04],[-8.65,8.2,.04]])])
    for o in C.objects():
        mod=o.get('cityprompt_lego_module','');role=o.get('cityprompt_semantic_role','')
        eligible=mod in ('furniture','interior','site','structure') or 'guard' in mod or 'open leaf' in o.name or o.name.startswith('bike rack')
        if role in ('paving','soil','leaf','plant','flower','roof'):eligible=False
        if not eligible or any(w in o.name for w in ('ceiling','diffuser','luminaire')):continue
        lo,hi=C.bounds([o]);OBS.append([lo[0],hi[0],lo[1],hi[1],lo[2],hi[2]])
    probes=[dict(name='rear bench',point=[2.5,8.7,.04]),dict(name='bike rack1',point=[-9.7,8.2,.04]),dict(name='bike rack2',point=[-9.7,9.45,.04])]
    return dict(version=2,footprint=[23,23],entrance=[-6.7,-11,Z],maxStepM=.18,triangles=tris,obstacles=OBS,portals=[[-7.8,-5.6,-11.6,-10.7],[10.8,11.7,5.1,7.2]],routes=routes,gardenExclusionProbes=probes)


def cameras():
    result=[]
    for name,loc in [('front',(0,-42,9)),('front_corner',(30,-35,23)),('aerial',(28,-29,38)),('left_side',(-40,0,12)),('right_side',(40,0,12)),('rear',(0,42,12)),('rear_side',(-29,32,24))]:
        result.append(dict(name=name,location=loc,target=(0,0,4),whole=True,lens=52))
    def add(name,loc,target,lens):result.append(dict(name=name,location=loc,target=target,whole=False,lens=lens))
    add('facade_close',(-10,-18,8),(-4,-7.5,4.5),44);add('architecture_close',(-10,-14,3.1),(-6.7,-7.3,1.8),38)
    add('glass_close',(2.6,-12,2.0),(4.2,-7.2,1.8),42);add('roof_contact',(12,-15,15),(-1.5,-2,8.5),40)
    add('side_entry',(13,8,3),(8.2,6.2,1.5),30);add('rear_garden',(10,16,7),(0,8,2.5),35)
    for level in range(2):
        z=Z+level*RISE
        add('left_living_'+str(level),(-4.7,-6.7,z+1.7),(-1.6,-2.5,z+1.3),20)
        add('right_living_'+str(level),(7,-6.5,z+1.7),(2.8,-3.5,z+1.3),24)
        add('left_bedroom_'+str(level),(-1.1,4.7,z+1.7),(-6,5.7,z+.9),24)
        add('right_bedroom_'+str(level),(3.3,3.8,z+1.65),(1.7,5.7,z+.9),20)
        add('left_bathroom_'+str(level),(-6.3,1.2,z+1.8),(-6.85,2.55,z+.75),14)
        add('right_bathroom_'+str(level),(7.25,-1.3,z+1.8),(6.7,.2,z+.75),14)
        for label,cx,cy in [('left',-6.85,2.1),('right',6.75,-.35)]:
            add(label+'_shower_'+str(level),(cx+.97,cy+.85,z+1.7),(cx-.72,cy-.50,z+1.18),18)
    for side in (-1,1):
        sx=side*6.7;sg=1 if side<0 else -1
        add(('left' if side<0 else 'right')+'_stair',(sx,sg*-6.7,2.6),(sx,sg*-2.3,2.4),18)
        add(('left' if side<0 else 'right')+'_upper_landing',(sx,sg*-6.7,5.2),(sx,sg*-3.1,2.5),18)
    return result


if __name__=='__main__':
    D.run(__file__,'corner-prework.json','fourplex-corner',PALETTE,cameras,build,network,'corner-grey-brick.png',[1.92,2.0])
