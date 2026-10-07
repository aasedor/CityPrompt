"""Source-locked vaulted reading pavilion, with a real open clerestory dormer."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import delivery as D
from delivery import C,B,R,bpy
import build_corner_fourplex as P  # Atomic wall/open-leaf helpers only.

Z=.14
PALETTE=dict(B.PALETTE,wall=(.57,.31,.20),trim=(.11,.12,.11),roof=(.44,.48,.50),
 timber=(.56,.38,.21),interior=(.80,.78,.70),floor=(.58,.52,.42),furniture=(.30,.40,.34),
 ceiling=(.85,.82,.72),lamp=(.96,.88,.70),leaf=(.24,.32,.15),flower=(.67,.60,.42),grass=(.29,.37,.17))

def roofz(y):return 4.34+(y+12)*2.66/16 if y<=4 else 7-(y-4)*2.66/8

def pane_schedule():
    original=C.Face.window
    def window(self,ident,u,z,w,h,cols=2,rows=1,frame='trim',inset=.14,bar=.045,sill=True,curtain=False,depth=.27,kind='window'):
        if ident in ('reading frontage','clerestory lights'):cols=14
        return original(self,ident,u,z,w,h,cols,rows,frame,inset,bar,sill,curtain,depth,kind)
    C.Face.window=window

def wall(face,a,b,holes=(),height=4.17,role='wall',depth=.30,glazed=False):
    P.wall(face,a,b,0,height,holes,role,depth,glazed,flat_door=role=='interior')

def partition_y(y,a,b):wall(C.Face((0,y,0),(1,0,0),(0,1,0),'service divider '+str(y)),a,b,height=3.62,role='interior',depth=.13)

def table(x,y,w=2.2,d=1.0,child=False):
    ht=.58 if child else .76;seat=.33 if child else .46;cw=.35 if child else .46
    C.box('reading table',(x,y,Z+ht),(w,d,.07),'timber','furniture')
    for dx in (-w/2+.16,w/2-.16):
        for dy in (-d/2+.14,d/2-.14):C.box('table leg',(x+dx,y+dy,Z+ht/2),(.065,.065,ht),'trim','furniture')
    for dx in (-w*.27,w*.27):
        for sign in (-1,1):
            cy=y+sign*(d/2+.49)
            C.box('reading chair',(x+dx,cy,Z+seat),(cw,cw,.065),'furniture','furniture')
            C.box('chair back',(x+dx,cy+sign*cw*.42,Z+seat+.23),(cw,.055,.45),'timber','furniture')
            for a in (-cw*.35,cw*.35):
                for b in (-cw*.35,cw*.35):C.box('chair leg',(x+dx+a,cy+b,Z+seat/2),(.035,.035,seat),'trim','furniture')
    for dx in (-.42,.25):C.box('reading book',(x+dx,y,Z+ht+.065),(.23,.32,.04),'furniture','decor')

def shelf(x,y,length=3.6,height=1.8,axis='y',name='book stacks'):
    def box(label,u,v,z,a,b,h,role='timber'):
        pos=(x+v,y+u,Z+z) if axis=='y' else (x+u,y+v,Z+z)
        size=(b,a,h) if axis=='y' else (a,b,h)
        return C.box(name+' '+label,pos,size,role,'furniture')
    box('spine',0,0,height/2,length,.065,height)
    for u in (-length/2,length/2):box('end',u,0,height/2,.065,.60,height)
    rows=4 if height>1.3 else 2
    for j in range(rows):
        zz=.18+j*.41;box('shelf',0,0,zz,length,.62,.055)
        for side in (-1,1):
            for k in range(int(length/.14)-1):
                box('book',-length/2+.15+k*.14,side*.18,zz+.19,.085,.23,.28+.03*(k%3),'furniture' if k%3 else 'interior')

def basin(x,y):
    base=C.box('sink cabinet',(x,y,Z+.42),(1.60,.68,.84),'timber','furniture')
    C.cut_box(base,'cabinet bowl clearance',(x-.28,y,Z+.83),(.60,.49,.40))
    top=C.box('sink worktop',(x,y,Z+.88),(1.66,.73,.08),'stone','furniture')
    C.cut_box(top,'counter aperture',(x-.28,y,Z+.89),(.53,.43,.22))
    bowl=C.box('sink bowl',(x-.28,y,Z+.77),(.57,.47,.25),'hardware','furniture')
    C.cut_box(bowl,'bowl interior',(x-.28,y,Z+.86),(.50,.40,.27))
    C.rod('basin tap',(x-.28,y+.26,Z+.90),(x-.28,y+.26,Z+1.20),.02,'hardware','furniture')
    C.rod('basin spout',(x-.28,y+.26,Z+1.20),(x-.28,y+.02,Z+1.20),.02,'hardware','furniture')

def toilet(x,y):
    C.box('WC pedestal',(x,y,Z+.21),(.36,.48,.42),'ceiling','furniture')
    bowl=C.box('WC ceramic bowl',(x,y-.05,Z+.46),(.50,.68,.18),'ceiling','furniture')
    C.cut_box(bowl,'WC bowl recess',(x,y-.12,Z+.52),(.27,.39,.25))
    C.box('WC cistern',(x,y+.27,Z+.69),(.48,.20,.78),'ceiling','furniture')

def roof():
    # Four front-plane rectangles surround an actual dormer opening.
    for a,b,c,d in [(-16.5,16.5,-12.7,-3),(-16.5,-11.8,-3,2.8),(9.2,16.5,-3,2.8),(-16.5,16.5,2.8,4)]:
        C.solid_surface('main front zinc plane',[(a,c,roofz(c)),(b,c,roofz(c)),(b,d,roofz(d)),(a,d,roofz(d))],.12)
        C.solid_surface('timber roof lining',[(a,c,roofz(c)-.12),(b,c,roofz(c)-.12),(b,d,roofz(d)-.12),(a,d,roofz(d)-.12)],.055,'timber','roof')
    C.solid_surface('rear zinc plane',[(-16.5,4,7),(16.5,4,7),(16.5,12.5,roofz(12.5)),(-16.5,12.5,roofz(12.5))],.12)
    C.solid_surface('rear timber lining',[(-16.5,4,6.88),(16.5,4,6.88),(16.5,12.5,roofz(12.5)-.12),(-16.5,12.5,roofz(12.5)-.12)],.055,'timber','roof')
    face=C.Face((0,-3,0),(1,0,0),(0,1,0),'clerestory front')
    face.wall('clerestory aperture carrier',-11.8,9.2,roofz(-3)-.025,6.61,.12,'trim',[P.h('clerestory lights',-1.3,5.93,20.76,.60)])
    face.window('clerestory lights',-1.3,5.93,20.76,.60,14,1,'trim',.055,.045,False,False,.12)
    for a,b in [(-11.8,-11.68),(9.08,9.2)]:C.prism('dormer zinc cheek',[(-3,roofz(-3)-.025),(-3,6.61),(2.8,6.8205),(2.8,roofz(2.8)-.025)],'x',a,b,'roof','roof')
    C.solid_surface('dormer zinc cap',[(-11.87,-3.08,6.607), (9.27,-3.08,6.607),(9.27,2.82,6.8212),(-11.87,2.82,6.8212)],.055)
    C.beam('dormer rear flashing',(-11.90,2.85,6.835),(9.30,2.85,6.835),.18,.04,'roof','roof')
    for xx in (-11.84,9.24):C.beam('dormer side flashing',(xx,-3.03,roofz(-3.03)+.025),(xx,2.85,roofz(2.85)+.025),.14,.04,'roof','roof')
    for i in range(56):
        x=-16.45+i*.59
        ranges=[(-12.68,-3.04),(2.83,4)] if -11.9<x<9.3 else [(-12.68,4)]
        for a,b in ranges:C.beam('main standing seam',(x,a,roofz(a)+.02),(x,b,roofz(b)+.02),.018,.024,'roof','roof')
        C.beam('rear standing seam',(x,4,7.02),(x,12.48,roofz(12.48)+.02),.018,.024,'roof','roof')
        if -11.8<x<9.2:C.beam('dormer cap seam',(x,-3.06,6.629),(x,2.8,6.843),.016,.022,'roof','roof')
    C.rod('continuous ridge cap',(-16.52,4,7.025),(16.52,4,7.025),.06,'roof','roof')
    for x in (-16.52,16.52):
        for a,b in [(-12.72,4),(4,12.52)]:C.beam('gable fascia',(x,a,roofz(a)-.08),(x,b,roofz(b)-.08),.18,.17,'timber','roof')
    for y in (-12.71,12.51):C.beam('eave fascia',(-16.52,y,roofz(y)-.1),(16.52,y,roofz(y)-.1),.18,.20,'timber','roof')
    for x in (-14,-9,-4,1,6,11,15.5):
        for a,b in [(-12.2,4),(4,12.1)]:C.beam('glulam rafter',(x,a,roofz(a)-.36),(x,b,roofz(b)-.36),.19,.38,'timber','structure')

def build():
    P.OBS.clear();pane_schedule()
    C.box('site base',(0,-1,.02),(42,36,.04),'paving','site',0)
    C.box('occupied floor',(0,0,Z-.06),(32,24,.12),'floor','floors',0)
    front=C.Face((0,-12,0),(1,0,0),(0,1,0),'reading front')
    wall(front,-16,10.2,[P.h('reading frontage',-3.15,.24,23.90,3.57)])
    # Recessed entrance under the continuous overhanging source roof.
    wall(C.Face((10.2,-11.25,0),(0,1,0),(1,0,0),'entry brick return'),-.75,.75)
    wall(C.Face((0,-10.5,0),(1,0,0),(0,1,0),'entry facade'),10.2,15.7,[P.h('public door',12.4,Z,1.65,2.73,True),P.h('entry left light',10.98,.24,1.20,3.55),P.h('entry right light',14.52,.24,2.18,3.55),P.h('entry transom',12.4,3.02,1.65,.77)],glazed=True)
    for side in (-1,1):
        f=C.Face((side*16,0,0),(0,1,0),(-side,0,0),'side '+str(side))
        windows=[P.h('narrow side '+str(j),y,.74,1.0,2.65) for j,y in enumerate((-7.5,-3.5,.5,4.5,8.5))] if side>0 else [P.h('left reading '+str(j),y,.74,2.6,2.65) for j,y in enumerate((-8,-3,2,7))]
        wall(f,-12,12,windows)
        C.prism('brick asymmetric gable',[(-12,4.17),(4,6.83),(12,4.17)],'x',-16 if side<0 else 15.7,-15.7 if side<0 else 16,'wall')
    wall(C.Face((0,12,0),(1,0,0),(0,-1,0),'rear facade'),-15.7,15.7,[P.h('rear quiet '+str(j),x,.74,3.4,2.65) for j,x in enumerate((-11,-4,3))]+[P.h('meeting rear',12.3,.84,2.2,2.5)])
    roof()
    wall(C.Face((8.6,0,0),(0,1,0),(1,0,0),'service corridor'),-5.5,11.7,[P.h('WC doorway',-2.8,Z,1.3,2.35,True),P.h('staff doorway',3.0,Z,1.3,2.35,True),P.h('meeting doorway',8.4,Z,1.4,2.35,True)],3.62,'interior',.13)
    for y in (-5.5,1.7,6.5):partition_y(y,8.6,15.7)
    C.box('service rooms ceiling',(12.15,3.10,3.68),(7.1,17.2,.12),'ceiling','ceiling',0)
    for x,y in [(-5.5,-8.4),(1,-8.4),(-5.5,-3.3),(1,-3.3)]:table(x,y)
    table(-12,-7.8,1.7,.85,True)
    shelf(-12,-3.3,3.4,1.05,'x','children books')
    C.box('children rug',(-12,-5.4,Z+.008),(4.1,2.4,.016),'interior','decor',0)
    for x,y in [(-13.2,-5.5),(-11.1,-5.4)]:C.box('reading cushion',(x,y,Z+.16),(.75,.70,.32),'furniture','furniture')
    for x in (-11.5,-6.5,-1.5,3.5):shelf(x,2.8)
    for x in (-11,-4,3):table(x,9.35,2.4,1)
    C.box('reception counter',(12.9,-7.45,Z+.52),(3.1,.80,1.04),'timber','furniture')
    C.box('reception worktop',(12.9,-7.45,Z+1.06),(3.2,.88,.08),'stone','furniture')
    C.box('reception terminal',(12.65,-7.4,Z+1.40),(.55,.055,.46),'hardware','furniture')
    C.box('terminal stand',(12.65,-7.4,Z+1.16),(.10,.12,.18),'hardware','furniture')
    C.box('terminal foot',(12.65,-7.4,Z+1.115),(.32,.24,.035),'hardware','furniture')
    basin(10.7,1.32);toilet(13.3,1.18)
    C.rod('WC grab rail',(14.05,.5,Z+.75),(14.05,1.53,Z+.75),.035,'hardware','furniture')
    for y in (.55,1.48):C.rod('WC rail bracket',(14.05,y,Z+.75),(14.05,y,Z),.025,'hardware','furniture')
    C.box('washroom mirror',(10.7,1.685,Z+1.55),(1.1,.035,.70),'glass','furniture')
    basin(14.5,6.12);C.box('staff fridge',(15.12,2.8,Z+.98),(.9,.85,1.96),'ceiling','furniture')
    table(11.65,4.4,1.65,.75)
    table(12.4,9.2,2.3,1.0)
    C.box('meeting display',(15.69,10.8,1.75),(.04,1.65,1.0),'hardware','furniture')
    # Source entry columns and forecourt. No planter crosses the public route.
    for x in (-13.7,9.65):C.box('front glulam column',(x,-12.2,2.10),(.18,.18,4.20),'trim','structure')
    for x,y,power in [(-12,-7,260),(-5,-7,280),(2,-7,280),(-11,2,270),(-4,2,270),(3,2,260),(-10,9,230),(-2,9,250),(12,-8,170),(12,-1,160),(12,4,160),(12,9,160)]:
        z=3.2 if x>8.6 and y>-5.5 else 3.85
        C.qa_room_light('library',(x,y,z),power,2.5);R.lamp(x,y,z+.15,.85)
        if x<8.6:
            support=6.61+(y+3)*.2105/5.8-.05 if -11.8<x<9.2 and -3<y<2.8 else roofz(y)-.17
            C.rod('pendant suspension',(x,y,z+.19),(x,y,support),.014,'hardware','structure')
    C.box('entry apron',(12.4,-13.75,.09),(5.8,6.5,.10),'paving','site',0)
    C.prism('public approach slope',[(-18.5,0),(-18.5,.04),(-17,.14),(-17,0)],'x',9.5,15.3,'paving','site')
    C.box('front crossing',(-1,-14.1,.09),(32.6,1.5,.10),'paving','site',0)
    C.box('bike pad',(-9.2,-16.1,.09),(4.0,2.6,.10),'paving','site',0)
    C.box('bench pad',(.2,-16,.09),(4.8,2.8,.10),'paving','site',0)
    for x in (-13,-5,4.7):R.plantbed(x,-12.9,4.6,.95)
    for x in (-10.4,-9.2,-8.0):B.bikehoop(x,-16.1)
    B.bench(.2,-16.0)
    for x in (-17.2,17.2):R.plantbed(x,0,1.4,21)
    for x,y,seed in [(-19,-14,601),(19,-14,602),(-19,12,603),(19,12,604)]:R.tree(x,y,seed)
    for x in (-9,0,8):C.box('front lawn',(x,-18.15,.065),(2.6 if x==8 else 6.8,1.35,.05),'grass','landscape',0)
    for o in bpy.context.scene.objects:
        if o.type=='LIGHT':o.visible_camera=False;o.visible_glossy=False;o.visible_transmission=False;o.data.specular_factor=0;o.data.transmission_factor=0

def network():
    tris=[];routes=[];obs=P.OBS
    def rect(a,b,c,d,z):
        p=[a,b,z];q=[c,b,z];r=[c,d,z];s=[a,d,z];tris.extend([[p,q,r],[p,r,s]])
    rect(-15.68,-11.68,15.68,11.68,Z)
    rect(9.5,-18.9,15.3,-18.5,.04)
    a=[9.5,-18.5,.04];b=[15.3,-18.5,.04];c=[15.3,-17,Z];d=[9.5,-17,Z];tris.extend([[a,b,c],[a,c,d]])
    rect(9.5,-17,15.3,-10.2,Z);rect(-17.3,-14.85,15.3,-13.35,Z)
    rect(-11.2,-17.3,-7.2,-13.35,Z);rect(-2.2,-17.4,2.6,-13.35,Z)
    def route(name,xy):routes.append(dict(name=name,points=[[x,y,Z] for x,y in xy]))
    routes.append(dict(name='Public entrance',points=[[12.4,-18.8,.04],[12.4,-18.5,.04],[12.4,-17,Z],[12.4,-9.7,Z],[7.2,-9.7,Z]]))
    route('Reception approach',[(12.4,-9.7),(12.4,-8.2)])
    route('Children reading area',[(7.2,-9.7),(7.2,-10.5),(-14.5,-10.5),(-14.5,-5.2)])
    route('Adult reading table',[(7.2,-9.7),(4.5,-9.7),(4.5,-8.4),(2.6,-8.4)])
    route('Main hall to quiet reading',[(7.2,-9.7),(7.2,7.3),(-13.4,7.3),(-13.4,9.35)])
    for x in (-14,-9,-4,1):route('Stack aisle '+str(x),[(7.2,-.4),(x,-.4),(x,5.4)])
    route('Washroom',[(7.2,-2.8),(10,-2.8),(10,-.5)])
    route('Staff room',[(7.2,3),(10.1,3),(10.1,5.8),(12.8,5.8)])
    route('Meeting room',[(7.2,8.4),(10.2,8.4)])
    route('Forecourt bench',[(12.4,-17),(12.4,-14.1),(2.5,-14.1),(2.5,-16)])
    route('Bicycle approach',[(2.5,-14.1),(-9.2,-14.1),(-9.2,-15.0)])
    for o in C.objects():
        mod=o.get('cityprompt_lego_module','');role=o.get('cityprompt_semantic_role','')
        eligible=mod in ('furniture','interior','site','structure') or 'open leaf' in o.name or o.name.startswith('bike rack')
        if role in ('paving','soil','leaf','plant','flower','roof','grass') or any(s in o.name for s in ('ceiling','luminaire','diffuser','rafter','suspension')):eligible=False
        if eligible:
            lo,hi=C.bounds([o]);obs.append([lo[0],hi[0],lo[1],hi[1],lo[2],hi[2]])
    return dict(version=2,footprint=[42,36],entrance=[12.4,-18.8,.04],maxStepM=.18,triangles=tris,obstacles=obs,portals=[[9.5,15.3,-19,-17.5]],routes=routes,gardenExclusionProbes=[dict(name='bench',point=[.2,-16,Z])]+[dict(name='bike'+str(i),point=[x,-16.1,Z]) for i,x in enumerate((-10.4,-9.2,-8))])

def cameras():
    cams=[]
    for name,loc in [('front',(0,-60,8)),('front_corner',(42,-48,27)),('aerial',(38,-42,53)),('left_side',(-58,0,12)),('right_side',(58,0,12)),('rear',(0,56,15)),('rear_side',(-42,40,29))]:cams.append(dict(name=name,location=loc,target=(0,0,3),whole=True,lens=52))
    for n,loc,target,lens in [
      ('facade_close',(-13,-22,6),(-4,-12,2.7),34),('architecture_close',(16,-20,4),(12,-10.5,2),32),('glass_close',(-6,-16,2.1),(-5,-9,1.5),32),
      ('roof_contact',(20,-22,20),(0,0,6),38),('dormer_contact',(10,-6,10),(-1,0,6.6),28),('dormer_rear',(-10,8,11),(-2,2.8,6.8),32),
      ('clerestory_interior',(-1,1.8,3.4),(-1,-3,6.2),24),('reading_hall',(6.8,-10.6,1.8),(-6,-4,1.2),22),('children',(-14.7,-10,1.7),(-11.5,-5.7,1.0),24),
      ('stacks',(6.8,-.3,1.8),(-7,3,1.1),24),('quiet_reading',(-14.3,6.5,1.8),(-3,9.4,1.1),24),('reception',(8,-9.5,1.8),(12.8,-7.5,1.1),28),
      ('washroom',(9,-3.8,1.85),(12.5,1.0,.9),23),('washroom_sink',(10,-.3,1.7),(10.7,1.3,.9),28),('washroom_toilet',(12,-.3,1.7),(13.4,1.2,.7),28),
      ('staff_room',(9.2,2.2,1.85),(13.4,5.7,1.0),22),('staff_kitchen',(13.2,4.8,1.75),(14.3,6.1,1.0),25),('meeting',(9.1,7,1.8),(13,9.6,1.1),23),
      ('forecourt',(13,-24,7),(-4,-14,1.1),30),('public_approach',(17,-20.5,1.1),(12.4,-17,.14),30)]:cams.append(dict(name=n,location=loc,target=target,whole=False,lens=lens))
    return cams

if __name__=='__main__':D.run(__file__,'library-prework.json','library-pavilion',PALETTE,cameras,build,network,'library-warm-brick.png',[1.968,2.0],extra_scripts=[P.__file__])
