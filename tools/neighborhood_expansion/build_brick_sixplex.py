"""Source-locked three-storey walk-up, central stacked stair and exactly six flats."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import delivery as D
from delivery import C,B,R,bpy
import build_corner_fourplex as P  # Atomic walls, bed and bathroom fixtures only.

Z=.28
RISE=3.1
PALETTE=dict(B.PALETTE,wall=(.52,.22,.12),trim=(.12,.105,.085),roof=(.17,.18,.18),
    timber=(.48,.28,.12),interior=(.76,.75,.69),floor=(.47,.37,.25),furniture=(.30,.38,.31),
    ceiling=(.84,.82,.76),lamp=(.96,.87,.70),leaf=(.24,.33,.13),flower=(.67,.60,.33),grass=(.26,.34,.14))


def windows():
    original=C.Face.window
    def source_window(self,ident,u,z,w,h,cols=2,rows=1,frame='trim',inset=.14,bar=.045,sill=True,curtain=False,depth=.27,kind='window'):
        if cols!=3:return original(self,ident,u,z,w,h,cols,rows,frame,inset,bar,sill,curtain,depth,kind)
        original(self,ident,u,z,w,h,1,rows,frame,inset,bar,sill,curtain,depth,kind)
        for o in list(C.objects()):
            if o.name.startswith(ident+' optical pane'):bpy.data.objects.remove(o,do_unlink=True)
        C.OPENINGS[-1]['cols']=3
        for f in (.21,.79):self.part(ident+' sash',u+w*(f-.5),inset,z+h/2,bar,.09,h-.12,frame)
        for a,b in ((0,.21),(.21,.79),(.79,1)):
            self.part(ident+' clear pane',u+w*((a+b)/2-.5),inset+.037,z+h/2,w*(b-a)-.06,.009,h-.13,'glass',soft=0)
    C.Face.window=source_window


def partition(face,a,b,z,doors=(),flat=False):P.wall(face,a,b,z,z+2.96,doors,'interior',.13,flat_door=flat)


def kitchen(side,z):
    x=-.48 if side<0 else .35;y=.45
    base=C.box('kitchen base',(x,y,z+.44),(.68,2.65,.88),'timber','furniture')
    C.cut_box(base,'basin cabinet cavity',(x,y-.55,z+.85),(.48,.64,.40))
    top=C.box('kitchen counter',(x,y,z+.91),(.73,2.71,.06),'stone','furniture')
    C.cut_box(top,'sink cut',(x,y-.55,z+.91),(.43,.59,.19))
    bowl=C.box('sink bowl',(x,y-.55,z+.80),(.46,.62,.23),'hardware','furniture')
    C.cut_box(bowl,'sink recess',(x,y-.55,z+.87),(.40,.56,.25))
    C.rod('sink tap',(x-side*.20,y-.55,z+.95),(x-side*.20,y-.55,z+1.20),.02,'hardware','furniture')
    C.rod('sink spout',(x-side*.20,y-.55,z+1.20),(x,y-.55,z+1.20),.02,'hardware','furniture')
    C.box('hob',(x,y+.55,z+.955),(.53,.62,.035),'hardware','furniture')
    for dx in (-.14,.14):
        for dy in (.38,.73):C.rod('hob ring',(x+dx,y+dy,z+.98),(x+dx,y+dy,z+.986),.085,'trim','furniture',16)
    C.box('upper cabinets',(-.32 if side<0 else .19,y+.30,z+1.95),(.38,1.8,.68),'timber','furniture')
    C.box('fridge',(-.57 if side<0 else .44,2.33,z+.95),(.86,.83,1.9),'ceiling','furniture')
    for dy in (-.85,0,.85):C.box('cabinet pull',(x+side*.36,y+dy,z+.68),(.025,.24,.025),'hardware','furniture')


def dining(side,z):
    x=side*4.8;y=-2.0
    C.box('dining table',(x,y,z+.75),(1.6,.95,.08),'timber','furniture')
    for dx in (-.62,.62):
        for dy in (-.32,.32):C.box('table leg',(x+dx,y+dy,z+.35),(.065,.065,.70),'hardware','furniture')
    for dx,dy in ((-1.07,0),(1.07,0),(0,-.83),(0,.83)):
        cx=x+dx;cy=y+dy
        C.box('dining chair seat',(cx,cy,z+.45),(.46,.44,.07),'furniture','furniture')
        C.box('dining chair back',(cx,cy+.20,z+.70),(.46,.065,.48),'furniture','furniture')
        for a in (-.17,.17):
            for b in (-.15,.15):C.box('dining chair leg',(cx+a,cy+b,z+.215),(.035,.035,.43),'timber','furniture')


def furnishings(side,z,level):
    B.sofa(side*4.9,-4.85,z);dining(side,z);kitchen(side,z)
    P.bed(side*5.15,5.35,z)
    C.box('bedside cabinet',(side*6.62,5.45,z+.28),(.52,.58,.56),'timber','furniture')
    C.box('bedroom wardrobe',(side*1.05,6.78,z+1.10),(1.60,.74,2.2),'timber','furniture')
    cx=side*2.005
    C.box('bookcase back',(cx,-2.4,z+.95),(.42,1.1,1.9),'timber','furniture')
    for j in range(3):
        C.box('bookcase shelf',(cx+side*.06,-2.4,z+.40+j*.5),(.43,1.06,.045),'stone','furniture')
        for k in range(5):C.box('book',(cx+side*.25,-2.78+k*.18,z+.57+j*.5),(.10,.095,.28),'furniture','furniture')
    before=set(C.objects());P.bathroom(-6.85,1.6,z)
    if side>0:
        for o in set(C.objects())-before:
            for v in o.data.vertices:v.co.x=-v.co.x
            C.normalise(o.data)
    # Bounded domestic dressing, no objects placed in the authored aisles.
    C.box('living rug',(side*4.9,-4.75,z+.003),(3.25,2.2,.006),'interior','decor',0)
    for x,y in ((side*4.8,-4.4),(side*4.8,-1.5),(side*5.2,5.4),(side*6.85,1.6)):
        C.qa_room_light('sixplex occupied',(x,y,z+2.70),120 if abs(y)>2 else 95,1.8)
        R.lamp(x,y,z+2.82,.70)


def stair_guards(z):
    r=RISE/22
    for side in (-1,1):
        x=side*.0625;pts=[]
        for j in range(11):pts.append((x,-5.35+j*.25,z+(j+1)*r if side<0 else z+RISE-j*r))
        pts=[(x,-5.475,pts[0][2])]+pts+[(x,-2.725,pts[-1][2])]
        for p in pts:C.rod('inner guard post',p,(p[0],p[1],p[2]+1.02),.018,'trim','stair guard')
        for a,b in zip(pts,pts[1:]):
            mid=((a[0]+b[0])/2,(a[1]+b[1])/2,(a[2]+b[2])/2)
            C.rod('inner guard picket',(mid[0],mid[1],max(a[2],b[2])),(mid[0],mid[1],mid[2]+1.02),.016,'trim','stair guard')
            for rise,width in ((1.02,.04),(.10,.025)):C.beam('inner stair rail',(a[0],a[1],a[2]+rise),(b[0],b[1],b[2]+rise),width,width,'trim','stair guard')


def roof():
    C.box('roof deck',(0,0,9.50),(16.4,14.4,.16),'roof','roof',0)
    for y in (-7.35,7.35):
        C.box('parapet long',(0,y,9.68),(17,.30,.40),'wall','roof',0)
        C.box('stone cornice',(0,y,9.80),(17.10,.40,.22),'stone','roof',0)
        C.box('parapet cap',(0,y,9.925),(17.14,.44,.03),'roof','roof',0)
    for x in (-8.35,8.35):
        C.box('parapet end',(x,0,9.68),(.30,14.4,.40),'wall','roof',0)
        C.box('stone cornice',(x,0,9.80),(.40,14.4,.22),'stone','roof',0)
        C.box('parapet cap',(x,0,9.925),(.44,14.4,.03),'roof','roof',0)
    for x in range(-7,8):C.box('membrane lap',(x,0,9.584),(.009,14.35,.008),'roof','roof',0)
    for y in (-5,-2,1,4):C.box('membrane cross seam',(0,y,9.584),(16.35,.008,.008),'roof','roof',0)
    C.box('service hatch curb',(.5,3.0,9.71),(1.35,1.10,.26),'roof','roof')
    C.box('service hatch cap',(.5,3.0,9.86),(1.43,1.18,.055),'hardware','roof')
    for x in (-2.7,2.7):
        C.rod('vent flashing',(x,.3,9.58),(x,.3,9.62),.20,'roof','roof',20)
        C.rod('plumbing vent',(x,.3,9.6),(x,.3,10.05),.09,'roof','roof',20)
    for x in (-8.52,8.52):C.rod('rear rainwater downpipe',(x,7.35,.12),(x,7.35,9.7),.047,'roof','site')


def build():
    P.OBS.clear();windows()
    C.box('plot base',(0,0,.02),(23,25,.04),'paving','site',0)
    for x in (-4.8,4.8):
        C.box('front lawn',(x,-10.4,.065),(6.6,2.6,.05),'grass','landscape',0)
        R.plantbed(x,-8.22,6.1,1.05)
    C.box('rear lawn',(-2.0,10.4,.065),(12.4,3.3,.05),'grass','landscape',0)
    C.box('entry first step',(0,-7.95,.09),(2.7,.40,.10),'stone','site',0)
    C.box('entry upper landing',(0,-7.425,.16),(2.7,.65,.24),'stone','site',0)
    for level in range(3):
        z=Z+level*RISE;lo=0 if level==0 else z;hi=Z+(level+1)*RISE if level<2 else 9.82
        front=C.Face((0,-7.5,0),(1,0,0),(0,1,0),'sixplex front '+str(level))
        hs=[P.h('living window '+str(level)+' '+str(s),s*4.9,z+.60,4.8,1.95) for s in (-1,1)]
        hs.append(P.h('shared entry',0,Z,1.8,2.45,True) if level==0 else P.h('stair light '+str(level),0,z+.55,1.10,2.0))
        P.wall(front,-8.5,8.5,lo,hi,hs,glazed=True)
        for side in (-1,1):
            f=C.Face((side*8.5,0,0),(0,1,0),(-side,0,0),'sixplex side '+str(side)+' '+str(level))
            P.wall(f,-7.2,7.2,lo,hi,[P.h('side light '+str(side)+' '+str(level)+' '+str(j),y,z+(1.25 if j==2 else .8),1.05,1.4 if j==2 else 1.9) for j,y in enumerate((-4.8,-1.7,1.6,5.2))])
        f=C.Face((0,7.5,0),(1,0,0),(0,-1,0),'sixplex rear '+str(level))
        P.wall(f,-8.5,8.5,lo,hi,[P.h('rear bed '+str(level)+' '+str(s),s*5.1,z+.75,2.6,1.9) for s in (-1,1)])
        floor=C.box('occupied slab',(0,0,z-.07),(16.4,14.4,.14),'floor','floors',0)
        ceiling=C.box('occupied ceiling',(0,0,z+2.90),(16.4,14.4,.12),'ceiling','ceiling',0)
        if level:C.cut_box(floor,'stacked stair void',(0,-3.5375,z),(2.96,3.875,.7))
        if level<2:C.cut_box(ceiling,'stacked stair headroom',(0,-3.5375,z+2.90),(2.96,3.875,.7))
        for side in (-1,1):
            f=C.Face((side*1.65,0,0),(0,1,0),(side,0,0),'core wall '+str(side)+' '+str(level))
            partition(f,-7.2,-1.4,z,[P.h('flat entry '+str(side)+' '+str(level),-6.2,z,1.2,2.30,True)])
            f=C.Face((side*4.1,3.4,0),(1,0,0),(0,1,0),'bedroom wall '+str(side)+' '+str(level))
            partition(f,-4.1,4.1,z,[P.h('bedroom door '+str(side)+' '+str(level),side*-1.7,z,1.15,2.25,True)])
            cx=side*6.85;cy=1.6
            partition(C.Face((cx,.4,0),(1,0,0),(0,1,0),'bath front '+str(side)+' '+str(level)),-1.35,1.35,z,[P.h('bath door '+str(side)+' '+str(level),side*-.4,z,1.05,2.25,True)],True)
            partition(C.Face((side*5.5,cy,0),(0,1,0),(side,0,0),'bath inner '+str(side)+' '+str(level)),-1.2,1.2,z)
            partition(C.Face((cx,2.8,0),(1,0,0),(0,-1,0),'bath back '+str(side)+' '+str(level)),-1.35,1.35,z)
            furnishings(side,z,level)
        partition(C.Face((0,-1.4,0),(1,0,0),(0,-1,0),'core back '+str(level)),-1.65,1.65,z)
        partition(C.Face((0,0,0),(0,1,0),(-1,0,0),'rear party '+str(level)),-1.4,7.2,z)
        if level<2:R.stair(0,-5.35,z,RISE,1.25);stair_guards(z)
        if level:
            for x in (-1.48,1.48):C.railing('upper perimeter guard',(x,-5.475,z),(x,-1.60,z),spacing=.10,bottom=0)
            C.railing('upper back guard',(-1.48,-1.60,z),(1.48,-1.60,z),spacing=.10,bottom=0)
        if level==2:C.railing('top lower-flight lip guard',(-1.48,-5.49,z),(0,-5.49,z),spacing=.10,bottom=0)
        C.qa_room_light('common stair',(0,-4.0,z+2.7),140,1.6)
    for x in (-1.22,1.22):C.box('cedar entry surround',(x,-7.56,1.57),(.45,.20,2.58),'timber','structure')
    for x in (-1.4,-1.25,-1.1,1.1,1.25,1.4):C.box('cedar entry joint',(x,-7.667,1.57),(.018,.009,2.58),'trim','structure',0)
    C.box('entrance canopy',(0,-7.90,2.99),(3.5,1.0,.20),'roof','structure')
    roof()
    for x in (-7,0,5.0):R.plantbed(x,12.1,3.5,.6)
    C.box('bicycle paving',(9.7,10.05,.045),(2.5,3.1,.01),'paving','site',0)
    B.bikehoop(9.7,9.3);B.bikehoop(9.7,10.8);B.bench(5.5,10.5)
    C.box('garden table',(5.5,9.35,.73),(1.5,.85,.08),'timber','site')
    for x in (4.95,6.05):C.box('garden table support',(x,9.35,.38),(.10,.60,.70),'hardware','site')
    R.tree(-9.7,-9.3,301);R.tree(-9.5,10.6,307)
    for o in bpy.context.scene.objects:
        if o.type=='LIGHT':
            o.visible_camera=False;o.visible_glossy=False;o.visible_transmission=False
            o.data.specular_factor=0;o.data.transmission_factor=0


def network():
    tris=[];routes=[];obs=P.OBS
    def rect(a,b,c,d,z):
        p=[a,b,z];q=[c,b,z];r=[c,d,z];s=[a,d,z];tris.extend([[p,q,r],[p,r,s]])
    for level in range(3):
        z=Z+level*RISE
        rect(-8.18,-7.18,-1.48,7.18,z);rect(1.48,-7.18,8.18,7.18,z)
        rect(-1.48,-7.18,1.48,-5.475,z);rect(-1.48,-1.60,1.48,7.18,z)
        if level<2:
            for j in range(11):
                rect(-1.3125,-5.475+j*.25,-.0625,-5.225+j*.25,z+(j+1)*RISE/22)
                rect(.0625,-5.475+j*.25,1.3125,-5.225+j*.25,z+RISE-j*RISE/22)
            rect(-1.3125,-2.725,1.3125,-1.675,z+RISE/2)
            pts=[[-.6875,-5.75,z],[-.6875,-2.2,z+RISE/2],[.6875,-2.2,z+RISE/2],[.6875,-5.75,z+RISE]]
            routes.extend([dict(name='Stair '+str(level)+' ascent',points=pts),dict(name='Stair '+str(level)+' descent',points=list(reversed(pts)))])
        for side in (-1,1):
            def route(label,xy):routes.append(dict(name=('Left' if side<0 else 'Right')+' flat '+str(level)+' '+label,points=[[side*x,y,z] for x,y in xy]))
            route('entry',[(.70,-6.2),(2.70,-6.2),(2.70,0),(2.50,0)])
            route('bedroom',[(2.5,0),(2.5,3.0),(2.4,3.0),(2.4,4.25)])
            route('bathroom',[(2.5,0),(6.45,0),(6.45,.95)])
    rect(-1.2,-12.3,1.2,-8.15,.04);rect(-1.35,-8.15,1.35,-7.75,.14);rect(-1.35,-7.75,1.35,-7.1,.28)
    rect(-1.2,-12.3,10.8,-11.7,.04);rect(8.6,-12.3,10.8,11.8,.04);rect(3.8,7.5,10.8,11.8,.04)
    routes.extend([
        dict(name='Shared front entrance',points=[[0,-12,.04],[0,-6.2,Z]]),
        dict(name='Rear seating approach',points=[[0,-12,.04],[9.2,-12,.04],[9.2,8.0,.04],[7.4,8.0,.04],[7.4,10.5,.04],[6.9,10.5,.04]]),
        dict(name='Bicycle approach',points=[[7.4,8.0,.04],[8.4,8.0,.04],[8.4,10.1,.04]])])
    for o in C.objects():
        mod=o.get('cityprompt_lego_module','');role=o.get('cityprompt_semantic_role','')
        eligible=mod in ('furniture','interior','site','structure') or 'guard' in mod or 'open leaf' in o.name or o.name.startswith('bike rack')
        if role in ('paving','soil','leaf','plant','flower','roof','grass') or o.name.startswith('entry first step') or o.name.startswith('entry upper landing'):eligible=False
        if not eligible or any(w in o.name for w in ('ceiling','diffuser','luminaire')):continue
        lo,hi=C.bounds([o]);obs.append([lo[0],hi[0],lo[1],hi[1],lo[2],hi[2]])
    probes=[dict(name=n,point=p) for n,p in [('bench',[5.5,10.5,.04]),('table',[5.5,9.35,.04]),('bike1',[9.7,9.3,.04]),('bike2',[9.7,10.8,.04])]]
    return dict(version=2,footprint=[23,25],entrance=[0,-12,.04],maxStepM=.18,triangles=tris,obstacles=obs,portals=[[-1.2,1.2,-12.5,-11.7]],routes=routes,gardenExclusionProbes=probes)


def cameras():
    cams=[]
    for name,loc in [('front',(0,-43,10)),('front_corner',(30,-36,25)),('aerial',(27,-30,39)),('left_side',(-40,0,13)),('right_side',(40,0,13)),('rear',(0,42,13)),('rear_side',(-29,32,25))]:cams.append(dict(name=name,location=loc,target=(0,0,4.7),whole=True,lens=52))
    def add(n,loc,target,lens):cams.append(dict(name=n,location=loc,target=target,whole=False,lens=lens))
    add('facade_close',(-12,-19,8),(-4,-7.5,4.6),40);add('architecture_close',(4,-14,3.2),(0,-7.4,1.7),34)
    add('glass_close',(-6.6,-12,2.0),(-4.9,-7.2,1.8),40);add('roof_contact',(15,-16,21),(0,0,9.7),44)
    add('rear_garden',(15,18,9),(5,9,1.5),32)
    for level in range(3):
        z=Z+level*RISE
        for side in (-1,1):
            label=('left' if side<0 else 'right')
            add(label+'_living_'+str(level),(side*7,-6.7,z+1.65),(side*3,-2.2,z+1.2),20)
            add(label+'_bedroom_'+str(level),(side*1.0,4.9,z+1.7),(side*5.15,5.7,z+.9),23)
            add(label+'_bathroom_'+str(level),(side*5.8,.65,z+1.8),(side*6.85,2.1,z+.75),14)
            add(label+'_shower_'+str(level),(side*5.88,2.45,z+1.7),(side*7.57,1.1,z+1.18),18)
            if level==0:add(label+'_kitchen',(side*2.7,-.8,z+1.85),(side*.43,.4,z+1.0),27)
        if level<2:
            add('stair_'+str(level),(0,-6.8,z+2.0),(0,-2.4,z+2.1),18)
            add('upper_landing_'+str(level),(0,-6.6,z+RISE+1.6),(0,-3.0,z+1.8),18)
    return cams


if __name__=='__main__':D.run(__file__,'sixplex-prework.json','sixplex-brick',PALETTE,cameras,build,network,'sixplex-russet-brick.png',[2.16,2.08],extra_scripts=[P.__file__])
