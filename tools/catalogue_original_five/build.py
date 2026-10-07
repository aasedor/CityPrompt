"""Five original buildings: new geometry, locked generated references, clay delivery."""
import argparse
import math
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.append(str(HERE.parent / 'catalogue_services_batch'))
import clay_core as C
from plan import SPECS, source_entry

PALETTE = dict(wall=(.12,.14,.14), trim=(.075,.085,.083), roof=(.13,.16,.19),
    foundation=(.25,.26,.24), glass=(.32,.39,.39), hardware=(.08,.085,.09),
    interior=(.73,.69,.59), floor=(.46,.38,.26), timber=(.52,.32,.15),
    pale=(.64,.62,.53), copper=(.40,.19,.09), planting=(.23,.29,.12),
    blue=(.09,.27,.32), yellow=(.74,.48,.09), red=(.52,.19,.11), joint=(.07,.08,.08))


def hole(ident,u,z,w,h):
    return dict(id=ident,u=u,z=z,w=w,h=h)


def faces(w,d,cx=0,cy=0,label=''):
    return [C.Face((cx,cy-d/2,0),(1,0,0),(0,1,0),label+'front'),
            C.Face((cx+w/2,cy,0),(0,1,0),(-1,0,0),label+'right'),
            C.Face((cx,cy+d/2,0),(-1,0,0),(0,-1,0),label+'rear'),
            C.Face((cx-w/2,cy,0),(0,-1,0),(1,0,0),label+'left')]


def glazing(f,h,door=False,cols=2):
    f.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=cols,rows=1,
             frame='trim',depth=.23,sill=not door,kind='glazed door' if door else 'window')
    if door:
        for du in ((-.1,.1) if cols==2 else (h['w']*.32,)):
            C.rod(h['id']+' door pull',f.p(h['u']+du,.01,h['z']+.9),
                  f.p(h['u']+du,.01,h['z']+1.4),.018,'hardware','door hardware')


def cladding(f,lo,hi,z0,z1,holes,step=.18,role='joint'):
    count=math.ceil((hi-lo)/step)
    for i in range(count):
        u=lo+(i+.5)*(hi-lo)/count
        spans=[(z0,z1)]
        for h in holes:
            if abs(u-h['u']) < h['w']/2+.025:
                spans=[p for a,b in spans for p in ((a,min(b,h['z'])),(max(a,h['z']+h['h']),b)) if p[1]>p[0]]
        for a,b in spans:
            f.part('Standing cladding seam',u,-.012,(a+b)/2,.014,.027,b-a,role,'cladding',0)


def gable_x(name,cx,cy,w,d,eave,ridge,role='roof',over=.22):
    xmin,xmax=cx-w/2-over,cx+w/2+over
    ymin,ymax=cy-d/2-over,cy+d/2+over
    for yy in (ymin,ymax):
        C.solid_surface(name+' closed roof plane',[(xmin,cy,ridge),(xmax,cy,ridge),
            (xmax,yy,eave),(xmin,yy,eave)],.14,role,name)
        count=math.ceil((xmax-xmin)/.42)
        for i in range(count+1):
            xx=xmin+(xmax-xmin)*i/count
            C.beam(name+' standing roof seam',(xx,cy,ridge+.018),(xx,yy,eave+.018),.026,.027,role,name)
    C.beam(name+' ridge cap',(xmin,cy,ridge+.02),(xmax,cy,ridge+.02),.13,.08,role,name)
    wall_edge=ridge-(ridge-eave)*(d/2)/(d/2+over)-.12
    for sign in (-1,1):
        xx=cx+sign*w/2
        C.prism(name+' enclosed end gable',[(cy-d/2,eave-.15),(cy+d/2,eave-.15),
                (cy+d/2,wall_edge),(cy,ridge-.12),(cy-d/2,wall_edge)],
                'x',xx-.11,xx+.11,'wall',name)
        # End cladding runs continuously up to the actual underside of the roof.
        count=math.ceil(d/.2)
        for i in range(count):
            yy=cy-d/2+(i+.5)*d/count
            top=ridge-(ridge-eave)*abs(yy-cy)/(d/2+over)-.14
            C.box(name+' end gable seam',(xx+sign*.12,yy,(eave+top)/2),(.027,.014,top-eave),'joint',name)


def steps(name,cx,wall_y,width,top,n=3,run=.28,role='timber'):
    for i in range(n):
        height=top*(i+1)/n
        y=wall_y-(n-i-.5)*run
        C.box(name+str(i),(cx,y,height/2),(width,run+.006,height),role,'entry steps')


def sofa(x,y,z):
    C.box('Sofa plinth',(x,y,z+.19),(2.4,.88,.22),'timber','living furniture')
    C.box('Sofa seat',(x,y-.03,z+.4),(2.25,.86,.24),'interior','living furniture')
    C.box('Sofa back',(x,y+.39,z+.68),(2.4,.16,.72),'interior','living furniture')
    for xx in (x-1.12,x+1.12):C.box('Sofa arm',(xx,y,z+.53),(.2,.9,.5),'interior','living furniture')
    C.box('Coffee table',(x,y-1.25,z+.42),(1.15,.62,.1),'timber','living furniture')
    for xx in (x-.43,x+.43):
        for yy in (y-1.44,y-1.06):C.box('Coffee table leg',(xx,yy,z+.2),(.045,.045,.4),'trim','living furniture')


def bed(x,y,z):
    C.box('Bed frame',(x,y,z+.22),(1.6,2,.32),'timber','bedroom furniture')
    C.box('Mattress',(x,y,z+.48),(1.53,1.93,.21),'interior','bedroom furniture')
    C.box('Duvet',(x,y-.2,z+.61),(1.52,1.35,.06),'pale','bedroom furniture')
    C.box('Headboard',(x,y+.99,z+.6),(1.67,.09,1.0),'timber','bedroom furniture')
    for xx in (x-.39,x+.39):C.box('Pillow',(xx,y+.60,z+.63),(.61,.36,.13),'interior','bedroom furniture')


def home():
    w,d,floor,eave=16,4.6,.45,3.2
    # Permanent transport chassis and supported floor, concealed by a removable skirt.
    for yy in (-1.3,1.3):
        C.box('Permanent chassis lower flange',(0,yy,.18),(15.6,.17,.045),'hardware','permanent chassis')
        C.box('Permanent chassis web',(0,yy,.255),(15.6,.035,.15),'hardware','permanent chassis')
        C.box('Permanent chassis upper flange',(0,yy,.33),(15.6,.17,.045),'hardware','permanent chassis')
        for xx in (-6.8,-3.4,0,3.4,6.8):
            C.box('Chassis bearing pier',(xx,yy,.0825),(.34,.34,.165),'foundation','chassis support')
    for xx in range(-7,8):C.box('Floor cross bearer',(xx,0,.34),(.075,4.35,.1),'hardware','permanent chassis')
    C.box('Insulated floor deck',(0,0,.405),(16,4.6,.09),'floor','floor')
    ff=faces(w,d)
    hs=[hole('Living window',-5.7,.83,2.65,1.85),hole('Front entrance',-.5,floor,1.05,2.3),
        hole('Bedroom one',2.5,1.02,1.6,1.65),hole('Bedroom two',5.8,1.02,1.6,1.65)]
    ff[0].wall('Front charcoal carrier',-8,8,floor,eave,depth=.23,holes=hs)
    cedar=C.Face((0,-2.325,0),(1,0,0),(0,1,0),'Cedar front facing')
    cedar.wall('Central cedar facing',-3.65,3.95,floor,eave,depth=.05,holes=hs,role='timber')
    for h in hs:glazing(ff[0],h,door=h['id']=='Front entrance',cols=1 if h['id']=='Front entrance' else 2)
    cladding(ff[0],-8,-3.65,floor,eave,hs,.20)
    cladding(ff[0],3.95,8,floor,eave,hs,.20)
    cladding(cedar,-3.65,3.95,floor,eave,hs,.14,'copper')
    for f,span in [(ff[1],4.6),(ff[2],16),(ff[3],4.6)]:
        openings=[hole(f.label+' window',0,1.12,1.1,1.15)] if span==4.6 else [hole('Rear kitchen',4.6,1.25,1.8,1.2),hole('Rear hall',-3.2,1.55,1.2,.85)]
        f.wall(f.label+' closed carrier',-span/2,span/2,floor,eave,depth=.23,holes=openings)
        for h in openings:glazing(f,h)
        cladding(f,-span/2,span/2,floor,eave,openings,.20)
    for f,span in zip(ff,[w,d,w,d]):
        f.part('Ventilated chassis skirt',0,.035,.225,span,.1,.45,'wall','skirt')
        f.part('Skirt bottom rail',0,-.025,.025,span,.045,.05,'trim','skirt')
    gable_x('Home gable',0,0,16,4.6,3.2,4.35)
    # Complete ceiling closes the unoccupied roof void.
    C.box('Room ceiling',(0,0,3.15),(15.6,4.2,.10),'interior','ceiling')
    C.box('Front deck skirt',(0,-2.88,.205),(14.4,1.16,.41),'wall','porch')
    C.box('Front cedar deck',(0,-2.88,.432),(14.4,1.16,.036),'timber','porch')
    for i in range(7):C.box('Deck board groove',(0,-2.33-i*.16,.453),(14.4,.009,.006),'copper','porch')
    steps('Central entry tread',-.5,-3.46,2.5,.45)
    C.solid_surface('Shallow porch canopy',[(-4.25,-2.32,3.21),(4.25,-2.32,3.21),
        (4.25,-3.58,3.04),(-4.25,-3.58,3.04)],.12,'roof','porch roof')
    for i in range(21):
        xx=-4.2+i*.42
        C.beam('Porch standing seam',(xx,-2.32,3.225),(xx,-3.58,3.055),.022,.024,'roof','porch roof')
    C.box('Porch front beam',(0,-3.45,2.94),(8.5,.16,.22),'timber','porch support')
    for xx in (-4.05,-2.2,1.2,4.05):
        C.box('Porch post foot',(xx,-3.4,.09),(.29,.29,.18),'foundation','porch support')
        C.box('Porch timber post',(xx,-3.4,1.63),(.15,.15,2.42),'timber','porch support')
        C.box('Post bracket',(xx,-3.4,.48),(.17,.17,.11),'hardware','porch support')
    # Two separate bedrooms opening to a shared rear hall; living/kitchen to left.
    for xx in (1.0,4.0):C.box('Bedroom division',(xx,-.685,1.79),(.12,2.77,2.68),'interior','room partitions')
    partition=C.Face((0,.70,0),(1,0,0),(0,1,0),'Bedroom hall')
    doors=[hole('Bedroom access '+str(x),x,floor,.85,2.12) for x in (3.35,6.8)]
    partition.wall('Bedroom hall wall',1.0,7.8,floor,3.13,depth=.12,role='interior',holes=doors)
    for h in doors:partition.door(h['id'],h['u'],h['z'],h['w'],h['h'],role='timber',panels=1)
    sofa(-5.4,-.1,floor)
    for x in (2.03,5.32):bed(x,-.85,floor)
    C.box('Kitchen base cabinets',(-4.8,1.70,.91),(4.0,.65,.92),'timber','kitchen')
    C.box('Kitchen counter',(-4.8,1.69,1.40),(4.10,.70,.06),'pale','kitchen')
    C.box('Sink inset',(-4.2,1.63,1.437),(.62,.43,.014),'hardware','kitchen')
    for xx in (-6.2,-5.93):
        for yy in (1.57,1.82):C.rod('Induction hob',(xx,yy,1.44),(xx,yy,1.448),.10,'trim','kitchen',20)
    C.rod('Sink tap',(-4.2,1.88,1.42),(-4.2,1.88,1.77),.018,'hardware','kitchen')
    C.rod('Tap spout',(-4.2,1.88,1.77),(-4.2,1.68,1.77),.018,'hardware','kitchen')
    for x in (-5,0,2.5,5.8):C.qa_room_light('Home room '+str(x),(x,0,2.95),75,1.7)
    for x in (-5,0,5):C.qa_room_light('Chassis inspection '+str(x),(x,0,.315),5,.7)
    for i,p in enumerate(((-3,-.3,.21),(-4,1.05,.22),(1,0,.20))):
        light=C.bpy.data.lights.new('QA chassis bearing '+str(i),'POINT');light.energy=8;light.shadow_soft_size=.03
        obj=C.bpy.data.objects.new(light.name,light);C.bpy.context.collection.objects.link(obj);obj.location=p
    C.CONTACTS.append(dict(name='Permanent chassis',program='Authored manufactured-home teaching design; certification and transport not verified.',floor_m=.45,storeys=1))


def flat_roof(name,cx,cy,w,d,z,role='roof',parapet=.20):
    C.box(name+' closed roof',(cx,cy,z-.10),(w,d,.20),role,'roof')
    for yy in (cy-d/2+.09,cy+d/2-.09):
        C.box(name+' parapet',(cx,yy,z+parapet/2),(w,.18,parapet),'wall','parapet')
        C.box(name+' coping',(cx,yy,z+parapet+.025),(w+.08,.26,.05),'trim','parapet')
    for xx in (cx-w/2+.09,cx+w/2-.09):
        C.box(name+' parapet',(xx,cy,z+parapet/2),(.18,d,parapet),'wall','parapet')
        C.box(name+' coping',(xx,cy,z+parapet+.025),(.26,d,.05),'trim','parapet')
    for yy in range(math.ceil(cy-d/2+1),math.floor(cy+d/2),2):
        C.box(name+' membrane joint',(cx,yy,z+.002),(w-.36,.015,.004),'joint','roof')


def sectional(f,ident,u,z,w,h,role='trim',glazed=False):
    # A real hole in the enclosing carrier; physical sectional leaf/frames.
    if glazed:
        f.window(ident+' glazing',u,z+.7,w,h-.7,cols=3,rows=5,frame='trim',sill=False,kind='glazed sectional door')
        f.part(ident+' lower solid panel',u,.16,z+.35,w-.13,.09,.7,role,'sectional door')
        for side in (-1,1):f.part(ident+' full height jamb',u+side*(w/2-.035),.14,z+h/2,.07,.12,h,'trim','sectional door')
    else:
        f.door(ident,u,z,w,h,role=role,panels=max(4,round(h/.4)))
    for side in (-1,1):
        C.rod(ident+' safety bollard',f.p(u+side*(w/2+.25),-.45,0),f.p(u+side*(w/2+.25),-.45,1.1),.055,'yellow','bollard',12)


def desk(x,y,z=.12):
    C.box('Desk surface',(x,y,z+.75),(2.1,.85,.07),'timber','office furniture')
    for xx in (x-.85,x+.85):
        for yy in (y-.30,y+.30):C.box('Desk leg',(xx,yy,z+.37),(.045,.045,.74),'trim','office furniture')
    C.box('Monitor base',(x,y+.10,z+.80),(.32,.22,.04),'trim','office furniture')
    C.box('Monitor stem',(x,y+.12,z+.98),(.055,.055,.32),'trim','office furniture')
    C.box('Monitor',(x,y+.14,z+1.15),(.65,.06,.40),'trim','office furniture')
    C.box('Chair seat',(x,y-.9,z+.47),(.48,.48,.08),'blue','office furniture')
    C.box('Chair back',(x,y-1.1,z+.72),(.48,.07,.5),'blue','office furniture')
    for xx in (x-.2,x+.2):
        for yy in (y-1.1,y-.7):C.box('Chair leg',(xx,yy,z+.22),(.04,.04,.44),'trim','office furniture')


def workbench(x,y,z=.12,w=3):
    C.box('Workbench top',(x,y,z+.94),(w,.9,.1),'timber','workshop fixtures')
    for xx in (x-w/2+.15,x+w/2-.15):
        for yy in (y-.33,y+.33):C.box('Workbench leg',(xx,yy,z+.44),(.08,.08,.88),'trim','workshop fixtures')
    C.box('Workbench lower shelf',(x,y,z+.26),(w-.15,.78,.07),'trim','workshop fixtures')
    for xx in (x-.7,x+.7):C.box('Stored tool case',(xx,y,z+1.15),(.75,.42,.32),'blue','workshop fixtures')


def light_fixture(x,y,z,length=2,*,ceiling,qa_size=3,qa_power=180):
    C.box('Linear light housing',(x,y,z),(length,.15,.12),'trim','interior lights')
    C.box('Linear light diffuser',(x,y,z-.065),(length-.08,.11,.012),'interior','interior lights')
    for xx in (x-length*.35,x+length*.35):
        top=ceiling(xx) if callable(ceiling) else ceiling
        C.rod('Light suspension',(xx,y,z+.045),(xx,y,top),.013,'hardware','interior lights',sides=8)
        C.box('Light ceiling fixing',(xx,y,top-.014),(.09,.09,.028),'trim','interior lights')
    C.qa_room_light('Room illumination',(x,y,z-.20),qa_power,qa_size)


def depot():
    floor=.12;w,d,cx=30,22,7.75
    ff=faces(w,d,cx,0,'Hall ')
    C.box('Hall slab',(cx,0,.06),(w,d,.12),'foundation','floor')
    bays=[hole('Vehicle bay '+str(i+1),u,floor,5.4,5.25) for i,u in enumerate((-11.25,-3.75,3.75,11.25))]
    ff[0].wall('Four bay front carrier',-15,15,floor,7.40,depth=.30,holes=bays)
    for h in bays:sectional(ff[0],h['id'],h['u'],floor,h['w'],h['h'],glazed=True)
    rh=[hole('Right clerestory',-1,4.9,16,1.02),hole('Right service door',9,.12,1.05,2.2)]
    ff[1].wall('Right carrier',-11,11,floor,7.4,depth=.30,holes=rh)
    glazing(ff[1],rh[0],cols=10);ff[1].door(rh[1]['id'],rh[1]['u'],floor,1.05,2.2,role='trim',panels=1)
    bh=[hole('Rear personnel access',-10,floor,1.15,2.2),hole('Rear daylight',3,4.9,16,1.0)]
    ff[2].wall('Rear carrier',-15,15,floor,7.4,depth=.30,holes=bh)
    ff[2].door(bh[0]['id'],-10,floor,1.15,2.2,role='trim',panels=1);glazing(ff[2],bh[1],cols=10)
    # Shared opening connects the office and hall; never two closed overlapping carriers.
    link=hole('Staff hall connection',5,floor,1.2,2.25)
    ff[3].wall('Left and shared wall',-11,11,floor,7.4,depth=.30,holes=[link])
    ff[3].door(link['id'],5,floor,1.2,2.25,role='trim',panels=1)
    for f,span,apertures in zip(ff,[30,22,30,22],[bays,rh,bh,[link]]):
        band=C.Face(f.p(0,-.045,0),tuple(f.t),tuple(f.n),f.label+' copper')
        band.wall('Copper upper fascia',-span/2,span/2,6.0,7.6,depth=.05,role='copper')
        cladding(band,-span/2,span/2,6,7.6,[],.28,'timber')
        cladding(f,-span/2,span/2,.12,6,apertures,3,'foundation')
    flat_roof('Hall',cx,0,30,22,7.40)
    # Low left office wing, whose width is reconciled from the three references.
    ow,od,ox,oy=15.5,12,-15,-5
    of=faces(ow,od,ox,oy,'Office ')
    C.box('Office slab',(ox,oy,.06),(ow,od,.12),'foundation','floor')
    oh=[hole('Dispatch glazing',-3.6,.12,6.6,3.25),hole('Staff entrance',4.6,.12,3.4,3.25)]
    of[0].wall('Office front carrier',-ow/2,ow/2,.12,3.88,holes=oh)
    glazing(of[0],oh[0],cols=4);glazing(of[0],oh[1],door=True,cols=2)
    cedar=C.Face((ox,-11.04,0),(1,0,0),(0,1,0),'Office entry timber')
    cedar.wall('Entry timber pier',.15,2.85,.12,3.34,depth=.06,role='timber')
    cladding(cedar,.15,2.85,.12,3.34,[],.14,'copper')
    # Office right boundary is the existing hall wall. Other two elevations complete the envelope.
    for idx,span in ((2,ow),(3,od)):
        holes=[hole(of[idx].label+' daylight',0,1.1,span*.62,1.75)]
        of[idx].wall(of[idx].label+' carrier',-span/2,span/2,.12,3.88,holes=holes)
        glazing(of[idx],holes[0],cols=5)
    flat_roof('Office',ox,oy,ow,od,3.88,parapet=.17)
    C.box('Office canopy',(ox,-12.15,3.44),(14.5,2.65,.20),'trim','entry canopy')
    C.box('Cedar canopy soffit',(ox,-12.15,3.327),(14.36,2.56,.026),'timber','entry canopy')
    for xx in (-21.6,-8.5):
        C.box('Office canopy post',(xx,-13.2,1.70),(.12,.12,3.4),'trim','entry support')
        C.box('Post bearing plate',(xx,-13.2,.035),(.24,.24,.07),'trim','entry support')
    C.box('Office entry landing',(ox,-12.3,.06),(15.5,2.6,.12),'foundation','entry')
    for xx in (-19,-14):desk(xx,-7.5)
    C.box('Staff rear partition',(-15,-1.5,1.55),(14.9,.14,2.86),'interior','staff rooms')
    staff=C.Face((-15,-1.5,0),(1,0,0),(0,1,0),'Staff room partition')
    # Cut the authored staff door through the existing partition.
    partition=C.bpy.data.objects.get('Staff rear partition')
    staff.cut(partition,'Staff room door hole',0,.12,1.0,2.2,.14);staff.door('Staff room door',0,.12,1,2.2,panels=1)
    for xx in (-11,0,11,21):
        if xx==-11:continue
        C.box('Service hall roof column',(xx,8,3.7),(.18,.18,7.16),'trim','hall structure')
    for yy in (-6,1,8):
        C.box('Hall roof beam',(7.75,yy,7.16),(29.4,.20,.40),'trim','hall structure')
        for xx in (-3.5,4,11.5,19):light_fixture(xx,yy,6.8,ceiling=6.98)
    for xx in (-3.5,4,11.5,19):
        workbench(xx,8.8)
        for side in (-1,1):
            C.box('Two-post maintenance lift',(xx+side*1.8,1.5,1.67),(.28,.30,3.10),'yellow','vehicle service lift')
            C.box('Lift footing',(xx+side*1.8,1.5,.19),(.66,.66,.14),'trim','vehicle service lift')
            C.box('Lift arm',(xx+side*.94,1.5,.61),(1.7,.12,.12),'trim','vehicle service lift')
    for xx in (-19,-12):light_fixture(xx,-6,3.5,ceiling=3.73)
    C.CONTACTS.append(dict(name='Municipal depot programme',storeys=1,bays=4,operator='government',office_to_hall_connection='one shared cut doorway',roof='one high hall and one low office; physically seated complete roofs'))


def conveyor(x,y,length=7):
    C.box('Conveyor belt',(x,y,1.18),(1.5,length,.12),'trim','enclosed sorting line')
    for side in (-1,1):
        C.box('Conveyor side rail',(x+side*.81,y,1.27),(.10,length,.30),'blue','enclosed sorting line')
        for yy in (y-length/2+.25,y,y+length/2-.25):
            C.box('Conveyor supported leg',(x+side*.70,yy,.62),(.09,.09,1.0),'trim','enclosed sorting line')
    for yy in (y-length/2,y+length/2):C.rod('Conveyor end roller',(x-.76,yy,1.17),(x+.76,yy,1.17),.12,'hardware','enclosed sorting line')
    for yy in (y-2,y,y+2):
        C.box('Sorted paper bundle',(x,yy,1.38),(.75,.85,.27),'pale','dry recyclables')
    for yy in (y-1.7,y+1.7):
        for side in (-1,1):
            bx=x+side*1.75
            C.box('Sort bin floor',(bx,yy,.19),(1.05,1.15,.14),'blue','dry sorting bins')
            for xx in (bx-.5,bx+.5):C.box('Sort bin side',(xx,yy,.60),(.06,1.15,.82),'blue','dry sorting bins')
            for by in (yy-.54,yy+.54):C.box('Sort bin end',(bx,by,.60),(1.05,.06,.82),'blue','dry sorting bins')


def recovery():
    w,d,floor,low,high=36,24,.12,6.2,9
    ff=faces(w,d,label='Recovery ')
    C.box('Recovery hall slab',(0,0,.06),(w,d,.12),'foundation','floor')
    hs=[hole('Enclosed receiving',-12,floor,6,5),hole('Staff entrance',0,floor,5.8,3.2),hole('Enclosed shipping',12,floor,6,5)]
    ff[0].wall('Recovery front carrier',-18,18,floor,low,holes=hs)
    for h in (hs[0],hs[2]):sectional(ff[0],h['id'],h['u'],floor,h['w'],h['h'],role='blue')
    # Central paired doors sit between sidelights and below a full-width transom.
    for u in (-2.1,2.1):ff[0].window('Entry sidelight '+str(u),u,.12,1.6,2.45,cols=1,frame='trim',sill=False)
    ff[0].window('Entry paired doors',0,.12,2.6,2.45,cols=2,frame='trim',sill=False,kind='paired glazed doors')
    ff[0].window('Entry transom',0,2.57,5.8,.75,cols=4,frame='trim',sill=False)
    for u in (-.12,.12):C.rod('Entry pull',ff[0].p(u,.015,1.03),ff[0].p(u,.015,1.57),.018,'hardware','door hardware')
    rear=[hole('Rear escape door',u,floor,1.15,2.2) for u in (-14,14)]
    ff[2].wall('Recovery rear carrier',-18,18,floor,low,holes=rear)
    for h in rear:ff[2].door(h['id']+str(h['u']),h['u'],floor,1.15,2.2,role='trim',panels=1)
    for i in (1,3):
        h=hole(ff[i].label+' escape',10,floor,1.15,2.2)
        ff[i].wall(ff[i].label+' carrier',-12,12,floor,low,holes=[h])
        ff[i].door(h['id'],10,floor,1.15,2.2,role='trim',panels=1)
    for idx,span,holes in ((0,36,hs),(1,24,[hole('escape',10,floor,1.15,2.2)]),(2,36,rear),(3,24,[hole('escape',10,floor,1.15,2.2)])):
        f=ff[idx];cladding(f,-span/2,span/2,1.1,low,holes,.28,'pale')
        f.wall('Concrete plinth',-span/2,span/2,floor,1.1,depth=.29,role='foundation',holes=holes)
    # Three closed single-slope roofs; the drop is a real glazed clerestory.
    for module,lo in enumerate((-18,-6,6)):
        hi=lo+12
        C.solid_surface('Single-slope roof '+str(module),[(lo,-12.22,low),(hi,-12.22,high),(hi,12.22,high),(lo,12.22,low)],.16,'pale','sawtooth roof')
        for yy in [i*.42 for i in range(-29,30)]:
            C.beam('Down-slope standing seam',(lo,yy,low+.018),(hi,yy,high+.018),.024,.028,'trim','sawtooth seams')
        for yy in (-12.22,12.22):C.beam('Sawtooth edge flashing',(lo,yy,low),(hi,yy,high),.12,.14,'trim','roof flashing')
        for yy in (-12,12):
            near,far=(yy,yy+.27) if yy<0 else (yy-.27,yy)
            C.prism('Closed tooth end',[(lo,6.0),(hi,6.0),(hi,8.88),(lo,6.08)],'y',near,far,'wall','roof enclosure')
            for j in range(43):
                xx=lo+(j+.5)*12/43;top=low+(high-low)*(xx-lo)/12-.17
                if top>low:
                    C.box('Tooth end rib',(xx,yy+(-.016 if yy<0 else .016),(low+top)/2),(.02,.032,top-low),'pale','cladding')
        cler=C.Face((hi,0,0),(0,1,0),(-1,0,0),'Roof tooth '+str(module))
        C.box('Clerestory base',(hi-.06,0,6.23),(.18,24,.16),'trim','roof structure')
        cler.window('Northlight glazing '+str(module),0,6.25,24,2.60,cols=16,rows=1,frame='trim',depth=.16,sill=False)
        C.box('Clerestory high header',(hi-.06,0,8.84),(.18,24,.18),'trim','roof structure')
        for yy in (-10,-4,2,8):
            C.box('Roof line column',(hi-.16,yy,4.46),(.20,.20,8.68),'trim','roof supports')
            C.beam('Sloped roof beam',(lo-.16 if module else lo+.12,yy,5.96),(hi-.12,yy,8.78),.16,.22,'trim','roof supports')
        for yy in (-5,5):light_fixture((lo+hi)/2,yy,6.2,ceiling=lambda x:6.05+(x-lo)*2.8/12)
    C.box('Entry canopy',(0,-12.75,3.65),(6.5,1.6,.20),'trim','staff entry')
    C.box('Canopy timber fascia',(0,-13.53,3.54),(6.5,.09,.22),'timber','staff entry')
    for xx in (-3.1,3.1):C.box('Entry timber post',(xx,-13.30,1.86),(.18,.18,3.48),'timber','staff entry')
    C.box('Staff landing',(0,-12.85,.06),(6.7,1.7,.12),'foundation','staff entry')
    # A contained lobby, enclosed process hall, conveyor, baler and strapped paper bales.
    for xx in (-3.7,3.7):C.box('Lobby side',(xx,-9,1.68),(.14,5.73,3.12),'interior','lobby')
    lobby=C.Face((0,-6.2,0),(1,0,0),(0,1,0),'Lobby internal')
    dh=hole('Hall access',0,.12,1.8,2.3)
    lobby.wall('Lobby rear',-3.7,3.7,.12,3.24,depth=.14,role='interior',holes=[dh]);glazing(lobby,dh,door=True)
    C.box('Lobby ceiling',(0,-9,3.22),(7.4,5.6,.12),'interior','lobby')
    desk(-1.8,-9.8);light_fixture(0,-9,2.95,ceiling=3.18)
    for xx in (-9,5):conveyor(xx,1.5,8)
    C.box('Enclosed baler base',(13,7,.32),(3.8,3.0,.4),'trim','baling equipment')
    for xx in (11.3,14.7):C.box('Baler side frame',(xx,7,1.65),(.35,3,2.66),'blue','baling equipment')
    C.box('Baler header',(13,7,3),(3.8,3,.4),'blue','baling equipment')
    C.box('Hydraulic ram',(13,7.6,2.2),(.7,.7,1.25),'trim','baling equipment')
    C.box('Compressed paper bale',(13,7,1.02),(2.7,2.3,1.0),'pale','baling equipment')
    for x in (-14,-10,-6):
        for y in (8,10):
            C.box('Stored dry paper bale',(x,y,.87),(2.4,1.6,1.5),'pale','indoor product storage')
            for xx in (x-.7,x+.7):C.box('Bale strap',(xx,y,.875),(.035,1.62,1.52),'trim','indoor product storage')
    C.CONTACTS.append(dict(name='Enclosed dry-recyclables process',storeys=1,roof_teeth=3,all_processing='indoors',roof_void='occupied high bay; no artificial floor',operator_impacts='dust and vibration conditions require separate review'))


def fence(name,ax,ay,bx,by,height=2.2,base=.85,role='timber',step=.14):
    length=math.hypot(bx-ax,by-ay);tx,ty=(bx-ax)/length,(by-ay)/length
    f=C.Face((ax,ay,0),(tx,ty,0),(-ty,tx,0),name)
    if base>0:f.part(name+' solid screen',length/2,0,base/2,length,.09,base,'copper','fence',0)
    for z in (base+.1,height-.15):f.part(name+' continuous rail',length/2,0,z,length,.075,.08,role,'fence',0)
    for i in range(math.ceil(length/step)):
        u=(i+.5)*length/math.ceil(length/step)
        f.part(name+' picket',u,-.05,(base+height)/2,.075,.07,height-base,role,'fence',0)
    count=math.ceil(length/2.5)
    for i in range(count+1):f.part(name+' post',length*i/count,0,height/2,.13,.13,height,role,'fence',0)


def tuft(x,y,z=.12,h=.45,seed=0):
    # Small honest leaf meshes, retained in the exported asset.
    for i in range(9):
        angle=i*2.399+seed;dx,dy=math.cos(angle),math.sin(angle)
        side=(-dy*.045,dx*.045);r=.12+(i%3)*.055;hh=h*(.65+(i%4)*.10)
        vs=[(x+side[0],y+side[1],z),(x-side[0],y-side[1],z),
            (x+dx*r-side[0]*.5,y+dy*r-side[1]*.5,z+hh*.55),
            (x+dx*r+side[0]*.5,y+dy*r+side[1]*.5,z+hh*.55),
            (x+dx*r*1.65,y+dy*r*1.65,z+hh)]
        C.mesh('Prairie planting leaf',vs,[(0,1,2,3),(3,2,4)],'planting','planted edge',0)


def tube(name,a,b,r=.13,t=.022):
    a,b=C.Vector(a),C.Vector(b);axis=(b-a).normalized();side=axis.cross(C.Vector((0,0,1))).normalized();up=axis.cross(side).normalized()
    vs=[];n=12
    for p in (a,b):
        for radius in (r,r-t):
            vs.extend(tuple(p+radius*(math.cos(i*math.tau/n)*side+math.sin(i*math.tau/n)*up)) for i in range(n))
    fs=[]
    for i in range(n):
        j=(i+1)%n
        fs.extend([(i,j,2*n+j,2*n+i),(n+j,n+i,3*n+i,3*n+j),(i,n+i,n+j,j),(2*n+j,3*n+j,3*n+i,2*n+i)])
    C.mesh(name,vs,fs,'hardware','stored usable pipe',0)


def storage_rack(x,y,w=2.4,length=4,role='copper',pipes=True):
    for xx in (x-w/2,x+w/2):
        for yy in (y-length/2,y+length/2):C.box('Rack upright',(xx,yy,1.44),(.1,.1,2.76),'trim','storage rack')
    for z in (.4,1.4,2.4):
        for xx in (x-w/2,x+w/2):C.box('Rack bearer',(xx,y,z),(.12,length,.12),role,'storage rack')
        for yy in (y-length/2,y+length/2):C.box('Rack crossbeam',(x,yy,z),(w,.12,.12),role,'storage rack')
        C.box('Load-bearing rack shelf',(x,y,z+.05),(w,length,.06),role,'storage rack')
        if pipes:
            for j in range(6):
                xx=x-.87+j*.34
                tube('Open stored pipe',(xx,y-length/2+.14,z+.21),(xx,y+length/2-.14,z+.21),.14)
        else:
            for j in range(5):
                for k in range(3):C.box('Usable timber stack',(x-.85+j*.42,y,z+.12+k*.085),(.36,length-.25,.085),'timber','stored usable lumber')


def mono_shed(name,cx,cy,w,d,front_h,rear_h,holes):
    ff=faces(w,d,cx,cy,name+' ')
    C.box(name+' slab',(cx,cy,.06),(w,d,.12),'foundation','floor')
    ff[0].wall(name+' front carrier',-w/2,w/2,.12,front_h,holes=holes)
    ff[2].wall(name+' rear carrier',-w/2,w/2,.12,rear_h-.10)
    for idx in (1,3):
        f=ff[idx];f.wall(name+' side carrier',-d/2,d/2,.12,front_h)
        xx=cx+(-w/2 if idx==3 else w/2)
        C.prism(name+' side wedge',[(cy-d/2,front_h-.2),(cy+d/2,front_h-.2),(cy+d/2,rear_h-.1),(cy-d/2,front_h-.1)],'x',xx-.10,xx+.10,'copper','roof closure')
    C.solid_surface(name+' pitched roof',[(cx-w/2-.2,cy-d/2-.2,front_h),(cx+w/2+.2,cy-d/2-.2,front_h),
        (cx+w/2+.2,cy+d/2+.2,rear_h),(cx-w/2-.2,cy+d/2+.2,rear_h)],.16,'roof','roof')
    for i in range(math.ceil(w/.42)+1):
        xx=cx-w/2+i*w/math.ceil(w/.42)
        C.beam(name+' roof standing seam',(xx,cy-d/2-.2,front_h+.02),(xx,cy+d/2+.2,rear_h+.02),.025,.028,'trim','roof seam')
    for idx,span,top in ((0,w,front_h),(1,d,front_h),(2,w,rear_h),(3,d,front_h)):
        f=ff[idx];openings=holes if idx==0 else []
        # One outer skin: the former d=0 siding duplicated the structural wall
        # face and flickered in Cesium. Seat a 60mm facing 35mm proud, with
        # its rear 25mm buried in the carrier and its joints on the same face.
        siding=C.Face(f.p(0,-.035,0),f.t,f.n,f.label+' siding')
        siding.wall(name+' corten siding',-span/2,span/2,2.35,top-.12,depth=.06,role='copper',holes=openings)
        cladding(siding,-span/2,span/2,2.35,top-.12,openings,.35,'timber')
    return ff


def yard():
    C.box('Compound grade pad',(0,0,.03),(38,30,.06),'foundation','compound')
    # The open gateway and pedestrian gateway remain separate and unobstructed.
    for args in [('Front left',-19,-15,-12.7,-15),('Front middle',-11.3,-15,-4,-15),('Front right',4,-15,19,-15),
                 ('Left edge',-19,-15,-19,15),('Right edge',19,-15,19,15),('Rear edge',-19,15,19,15)]:fence(*args)
    for x in (-4,4):fence('Open vehicle gate',x,-15,x,-11,height=2.2)
    # Pedestrian gate is closed, with a visible handle and physical hinges.
    fence('Office pedestrian gate',-12.7,-15,-11.3,-15,height=2.2,base=0,role='trim')
    C.rod('Gate handle',(-11.55,-15.12,1.0),(-11.55,-15.12,1.3),.018,'hardware','gate')
    C.box('Office path',(-12,-13.4,.075),(1.6,3.2,.03),'pale','pedestrian path')
    C.box('Service apron',(2,6.3,.09),(23,3.4,.06),'pale','vehicle apron')
    hs=[hole('Stored equipment bay '+str(i+1),u,.12,5.7,4.15) for i,u in enumerate((-5.5,2.5))]+[hole('Shed personnel door',9,.12,1.0,2.15)]
    sf=mono_shed('Equipment shed',2,11,22,6,5.4,6.3,hs)
    for h in hs[:2]:
        f=sf[0];u=h['u'];w=h['w'];z=.12
        for side in (-1,1):f.part('Shed sectional jamb',u+side*(w/2-.04),.14,z+2.075,.08,.12,4.15,'trim','bay')
        for i in range(11):
            a=z+i*4.15/11;b=z+(i+1)*4.15/11
            for lo,hi in ((a,min(b,1.65)),(max(a,1.95),b)):
                if hi>lo:f.part('Shed sectional leaf',u,.18,(lo+hi)/2,w-.16,.07,hi-lo-.004,'trim','bay',0)
        f.window(h['id']+' light strip',u,1.65,w-.2,.30,cols=4,rows=1,frame='hardware',sill=False,kind='garage vision strip')
        for sign in (-1,1):C.rod('Garage bollard',f.p(u+sign*(w/2+.20),-.3,.06),f.p(u+sign*(w/2+.2),-.3,1.0),.045,'yellow','bollard')
    sf[0].door('Shed personnel door',9,.12,1,2.15,role='trim',panels=1)
    for xx in (-4,5):workbench(xx,12.7);light_fixture(xx,11,4.8,ceiling=5.70)
    # Small dispatch office at front left.
    of=faces(8,6,-12,-9,'Yard office ')
    C.box('Dispatch slab',(-12,-9,.09),(8,6,.06),'foundation','floor')
    front=[hole('Dispatch entrance',0,.12,2.6,2.7)]
    for idx,span in ((0,8),(1,6),(2,8),(3,6)):
        hh=front if idx==0 else ([hole('Office side daylight',0,1.0,2.1,1.5)] if idx==1 else [])
        of[idx].wall(of[idx].label+' carrier',-span/2,span/2,.12,3.45,role='timber',holes=hh)
        cladding(of[idx],-span/2,span/2,.12,3.45,hh,.18,'copper')
        for h in hh:glazing(of[idx],h,door=idx==0,cols=2)
    flat_roof('Dispatch office',-12,-9,8,6,3.45,parapet=.20)
    desk(-12,-7.5);light_fixture(-12,-9,3.1,ceiling=3.30)
    # Open timber lean-to with actual seated posts, roof and stocked racks.
    C.solid_surface('Rack lean-to roof',[(-17.8,-5.3,4.6),(-12.3,-5.3,3.8),(-12.3,13.5,3.8),(-17.8,13.5,4.6)],.15,'roof','open rack canopy')
    for yy in (-5,0,5,10,13.2):
        for xx,hh in ((-17.6,4.48),(-12.5,3.72)):
            C.box('Rack canopy post',(xx,yy,(hh+.06)/2),(.16,.16,hh-.06),'timber','rack canopy support')
        C.beam('Canopy cross rafter',(-17.6,yy,4.40),(-12.5,yy,3.64),.13,.18,'timber','rack canopy support')
    for xx,zz in ((-17.6,4.35),(-12.5,3.62)):C.box('Canopy longitudinal beam',(xx,4.1,zz),(.16,18.6,.18),'timber','rack canopy support')
    for j in range(45):
        yy=-5.2+j*.42;C.beam('Lean-to standing seam',(-17.8,yy,4.62),(-12.3,yy,3.82),.024,.03,'trim','rack canopy')
    for i,yy in enumerate((-2,2.5,7,11.3)):storage_rack(-15.2,yy,w=3.5,length=3.7,role='timber',pipes=i%2==1)
    for i,yy in enumerate((-10,-5.5,-1,3.5)):storage_rack(16,yy,w=2.8,length=3.7,pipes=i%2==0)
    for yy in (-13,-8,-3,2,7,12):tuft(-18.2,yy,.065,.8,yy);tuft(18.1,yy,.065,.8,yy+1)
    for xx in (-17,-14,-9,-6,7,10,13,16):tuft(xx,-14.3,.065,.45,xx)
    C.CONTACTS.append(dict(name='Screened outdoor storage programme',compound_area_m2=1140,parcel_requirement='I-O minimum parcel 16000m2; asset is not parcel approval',circulation='central8mvehiclegateway and separate1.4mpedestrianentry',storeys=1))


def child_table(x,y):
    C.box('Activity table top',(x,y,.67),(1.5,.85,.08),'timber','classroom furniture')
    for xx in (x-.62,x+.62):
        for yy in (y-.29,y+.29):C.box('Child table leg',(xx,yy,.395),(.06,.06,.49),'timber','classroom furniture')
    for xx in (x-.43,x+.43):
        for sign in (-1,1):
            yy=y+sign*.72
            C.box('Child chair seat',(xx,yy,.43),(.38,.38,.05),'timber','classroom furniture')
            C.box('Child chair back',(xx,yy+sign*.17,.61),(.38,.05,.35),'timber','classroom furniture')
            for dx in (-.14,.14):
                for dy in (-.14,.14):C.box('Child chair leg',(xx+dx,yy+dy,.28),(.04,.04,.26),'timber','classroom furniture')


def child_gable(cx):
    # Three joined front-to-back gables; internal valleys are shared, not overlapping overhangs.
    for sign in (-1,1):
        outer=abs(cx+sign*3.75)>11
        xx=cx+sign*(3.75+(.18 if outer else 0))
        zz=3.82-(.18*2.38/3.75 if outer else 0)
        C.solid_surface('Sage standing-seam roof',[(cx,-2.18,6.2),(cx,10.15,6.2),
            (xx,10.15,zz),(xx,-2.18,zz)],.14,'roof','gable roof')
        for i in range(31):
            yy=-2.15+i*12.27/30
            C.beam('Roof standing seam',(cx,yy,6.215),(xx,yy,zz+.015),.025,.027,'roof','roof seam')
    C.beam('Continuous ridge cap',(cx,-2.18,6.23),(cx,10.15,6.23),.12,.06,'roof','roof')
    # Four solid pieces form a timber triangle around an actual triangular glass aperture.
    outer=[(cx-3.75,3.68),(cx,6.06),(cx+3.75,3.68)]
    inner=[(cx-2.8,3.82),(cx,5.44),(cx+2.8,3.82)]
    for p in ([outer[0],outer[1],inner[1],inner[0]],
              [outer[1],outer[2],inner[2],inner[1]],
              [outer[2],outer[0],inner[0],inner[2]]):
        C.prism('Clerestory timber surround',p,'y',-2.04,-1.81,'timber','front gable')
    C.prism('Triangular clerestory pane',inner,'y',-1.925,-1.90,'glass','clerestory')
    for a,b in zip(inner,inner[1:]+inner[:1]):
        C.beam('Triangular window frame',(a[0],-1.98,a[1]),(b[0],-1.98,b[1]),.08,.10,'timber','clerestory')
    for dx in (-1.25,0,1.25):
        top=5.44-abs(dx)*1.62/2.8
        C.box('Clerestory mullion',(cx+dx,-1.98,(3.82+top)/2),(.045,.09,top-3.82),'timber','clerestory')
    # Fine timber joints stop at the aperture and the sloping roof underside.
    for i in range(38):
        dx=-3.75+(i+.5)*7.5/38;top=6.06-abs(dx)*2.38/3.75
        low=5.44-abs(dx)*1.62/2.8 if abs(dx)<2.8 else 3.68
        if top>low:C.box('Gable timber joint',(cx+dx,-2.051,(low+top)/2),(.009,.012,top-low),'pale','timber joints')
    C.prism('Closed rear gable',outer,'y',9.81,10.02,'wall','rear gable')
    for yy in (1.8,5.8,9.6):
        for sign in (-1,1):C.beam('Seated classroom roof rafter',(cx+sign*3.65,yy,3.69),(cx,yy,6.00),.10,.15,'timber','roof structure')
    C.CONTACTS.append(dict(name='Triangular clerestory',centre_x=cx,opening='Physical triangular aperture with frames and thin glass; no carrier behind it',source='front and oblique references'))


def childcare():
    C.box('Courtyard grade pad',(0,0,.04),(28,26,.08),'foundation','compound')
    C.box('Three classroom slab',(0,4,.115),(22.5,12,.07),'floor','floor')
    C.box('Rear service spine slab',(0,11,.115),(22.5,2,.07),'floor','floor')
    ff=faces(22.5,12,0,4,'Childcare ')
    hs=[hole('Classroom '+str(i+1)+' glazed frontage',cx,.15,5.9,3.15) for i,cx in enumerate((-7.5,0,7.5))]
    ff[0].wall('Pale brick front carrier',-11.25,11.25,.15,3.70,holes=hs)
    for h in hs:
        ff[0].window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=4,frame='timber',sill=False,kind='classroom glazing with right door')
        u=h['u']+2.05
        C.rod('Classroom door pull',ff[0].p(u,.01,1.10),ff[0].p(u,.01,1.55),.018,'hardware','door hardware')
    for idx in (1,3):
        side=[hole(ff[idx].label+' daylight '+str(i),u,.9,1.6,2.05) for i,u in enumerate((-3.7,0,3.7))]
        ff[idx].wall('Pale brick side carrier',-6,6,.15,3.70,holes=side)
        for h in side:ff[idx].window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=2,frame='timber')
    # Rear connection is open through real doorways into a low flat service spine.
    rear=C.Face((0,10,0),(1,0,0),(0,1,0),'Service spine connection')
    access=[hole('Room to service spine '+str(cx),cx,.15,1.05,2.3) for cx in (-7.5,0,7.5)]
    rear.wall('Rear classroom service wall',-11.25,11.25,.15,3.70,depth=.15,role='interior',holes=access)
    for h in access:rear.door(h['id'],h['u'],h['z'],h['w'],h['h'],role='timber',panels=1)
    sf=faces(22.5,2,0,11,'Rear spine ')
    for idx,span in ((1,2),(2,22.5),(3,2)):
        openings=([hole('Rear staff exit',8,.15,1.05,2.3),hole('Staff daylight',-4,1.3,5,1.1)] if idx==2 else [])
        sf[idx].wall('Rear spine enclosure',-span/2,span/2,.15,3.65,holes=openings)
        for h in openings:
            if h['id']=='Rear staff exit':sf[idx].door(h['id'],h['u'],h['z'],h['w'],h['h'],role='timber',panels=1)
            else:sf[idx].window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=4,frame='timber')
    flat_roof('Low service spine',0,11,22.5,2,3.65,parapet=.20)
    for cx in (-7.5,0,7.5):child_gable(cx)
    # Interior partitions run up to the common valleys, preserving single-storey tall rooms.
    for xx in (-3.75,3.75):
        pf=C.Face((xx,4,0),(0,1,0),(-1,0,0),'Classroom connection '+str(xx))
        ph=[hole('Connecting door',2.5,.15,1.05,2.3)]
        pf.wall('Classroom partition',-5.75,6.02,.15,3.68,depth=.12,role='interior',holes=ph)
        pf.door('Connecting door',2.5,.15,1.05,2.3,role='timber',panels=1)
    for cx in (-7.5,0,7.5):
        child_table(cx-1.3,1.3);child_table(cx+1.3,4.1)
        # Low open cubbies have actual shelves and dividers, not painted rectangles.
        cabinet_x=cx+2.15
        C.box('Cubbies back',(cabinet_x,9.7,.73),(2.6,.05,1.16),'timber','classroom storage')
        C.box('Cubbies seated plinth',(cabinet_x,9.48,.20),(2.6,.48,.10),'timber','classroom storage')
        for z in (.25,.76,1.28):C.box('Cubbies shelf',(cabinet_x,9.48,z),(2.6,.48,.045),'timber','classroom storage')
        for k in range(6):C.box('Cubbies division',(cabinet_x-1.28+k*.512,9.48,.74),(.04,.48,1.12),'timber','classroom storage')
        C.box('Quiet play mat',(cx-1.4,6.9,.16),(2.2,1.6,.02),'blue','classroom furniture')
        light_fixture(cx,4,4.7,ceiling=lambda x:6.07-abs(x-cx)*2.38/3.75)
        C.qa_room_light('Classroom daylight',(cx,2,3.3),230,3.5)
    # Keep inspection emitters inside the 2m-wide spine; a 3m disk crossed its walls.
    for xx in (-8,0,8):light_fixture(xx,11,3.2,ceiling=3.46,qa_size=.9,qa_power=75)
    C.box('Staff service counter',(9.8,11.45,1.03),(2.1,.55,.08),'timber','staff service area')
    C.box('Staff service cabinet',(9.8,11.45,.60),(2.1,.50,.9),'interior','staff service area')
    # Full-length veranda with the six supports evidenced by front and oblique sources.
    C.box('Timber veranda',(0,-3,.115),(22.8,2,.07),'timber','veranda')
    for i in range(13):C.box('Veranda board seam',(0,-3.96+i*.16,.153),(22.8,.009,.006),'pale','veranda')
    C.solid_surface('Veranda canopy',[(-11.50,-1.95,3.69),(11.50,-1.95,3.69),(11.50,-4.16,3.47),(-11.50,-4.16,3.47)],.12,'pale','veranda canopy')
    C.box('Continuous veranda beam',(0,-4.01,3.30),(23,.15,.20),'timber','veranda structure')
    for xx in (-11.15,-4.1,.4,3.2,7.3,11.15):
        C.box('Veranda post shoe',(xx,-3.96,.19),(.18,.18,.08),'hardware','veranda structure')
        C.rod('Six veranda timber posts',(xx,-3.96,.15),(xx,-3.96,3.4),.095,'timber','veranda structure',sides=16)
    # Court: a continuous accessible pedestrian approach, sand and timber nature play.
    C.box('Courtyard lawn',(0,-8,.095),(22.8,8,.03),'planting','courtyard')
    C.box('Courtyard pedestrian path',(-12,-7.5,.105),(1.4,11,.05),'pale','pedestrian approach')
    C.box('Sandbox sand',(-6.8,-8.4,.16),(3.3,2.7,.14),'sand','sandbox')
    for xx in (-8.55,-5.05):C.box('Sandbox side',(xx,-8.4,.25),(.2,3.1,.34),'timber','sandbox')
    for yy in (-9.85,-6.95):C.box('Sandbox end',(-6.8,yy,.25),(3.3,.2,.34),'timber','sandbox')
    for i,(xx,yy) in enumerate(((.1,-6.7),(.7,-7.0),(1.25,-7.4),(1.75,-7.85),(2.2,-8.35),(2.65,-8.8),(-8.6,-10.4),(-5.4,-10.6))):
        C.rod('Nature play stump',(xx,yy,.11),(xx,yy,.11+.25+(i%3)*.07),.18,'timber','nature play',sides=12)
    C.rod('Horizontal balance log',(3.15,-9.15,.31),(5.3,-10.05,.31),.2,'timber','nature play',sides=14)
    # Front pickets and tall side screens. The teaching model keeps its pedestrian gate closed.
    fence('Childcare front left',-14,-13,-12.7,-13,height=1.25,base=0,role='timber',step=.12)
    fence('Childcare front right',-11.3,-13,14,-13,height=1.25,base=0,role='timber',step=.12)
    fence('Secure pedestrian gate',-12.7,-13,-11.3,-13,height=1.25,base=0,role='timber',step=.12)
    C.rod('Gate latch',(-11.52,-13.12,.9),(-11.52,-13.12,1.06),.025,'hardware','gate hardware')
    for side in (-1,1):fence('Courtyard side screen',side*14,-13,side*14,13,height=1.9,base=0,role='timber',step=.10)
    fence('Rear secure screen',-14,13,14,13,height=1.9,base=0,role='timber',step=.10)
    for yy in range(-11,13,2):tuft(-13.4,yy,.08,.65,yy);tuft(13.2,yy,.08,.8,yy+3)
    for xx in range(-10,13,2):tuft(xx,-12.2,.11,.45,xx)
    for xx,yy in ((11.8,-9),(12.2,-4),(-13,2)):
        C.rod('Young courtyard tree',(xx,yy,.08),(xx,yy,2.7),.045,'timber','planting')
        for z in (1.35,1.9,2.4):tuft(xx,yy,z,.9,z*xx)
    C.CONTACTS.append(dict(name='Childcare programme',children=30,age_range='3-5 years',storeys=1,
        veranda_posts=6,gate_pose='Closed for secure-courtyard teaching state; reference gate is slightly open',
        dropoff='Three stalls must be provided separately in project site design; not part of this compound asset'))


DETAILS={
 'home': [('facade_close',(5,-12,5),(0,-3,1.9)),('architecture_close',(2,-8,2.2),(-.5,-3.6,1.3)),
    ('glass_close',(-5,-6,1.9),(-5.7,-2,1.55)),('roof_contact',(9,-7,6),(3,-2.9,3.1)),
    ('side_projection',(13,-4,3),(8,0,1.8)),('interior',(-6.5,-1.7,1.85),(-3,1.6,1.55)),
    ('bedroom',(3.7,-1.9,1.8),(2.8,.6,1.3)),('entry_approach',(-1,-8,1.7),(-.5,-3,1.4)),
    ('chassis',(-6,0,.23),(4,1.55,.23)),('bearing_contact',(-3.1,.45,.23),(-3.4,1.3,.21))],
 'depot':[('facade_close',(28,-37,12),(7.5,-11,3.8)),('architecture_close',(-11,-24,5),(-15,-11,2)),
    ('glass_close',(-3,-17,3),(-3.5,-8,2.4)),('roof_contact',(31,-20,15),(19,-8,7)),
    ('side_projection',(37,0,8),(22,0,4.8)),('interior',(17,-7,1.8),(4,5,3)),
    ('office',(-20,-9,1.8),(-13,-4,1.5)),('staff_connection',(-11,-6,1.8),(-7.2,-5,1.3)),
    ('service_lift',(.5,-5,3.5),(4,1.5,1.7))],
 'recovery':[('facade_close',(24,-36,12),(0,-12,4)),('architecture_close',(5,-24,4),(0,-12.8,2)),
    ('glass_close',(23,-6,8),(17,0,7.4)),('roof_contact',(25,-20,14),(6,-7,7.3)),
    ('side_projection',(34,1,9),(18,0,5)),('interior',(-14,-6,2),(-4,4,2.5)),
    ('sorting_line',(-13,-3,2),(-9,3,1.2)),('baler',(6,1,3),(13,7,1.8)),
    ('roof_structure',(0,0,4),(7,9,8))],
 'yard':[('facade_close',(7,-12,9),(2,8,3)),('architecture_close',(-7,-19,5),(-12,-12,1.8)),
    ('glass_close',(-7,-14.3,2.5),(-12,-11.8,1.4)),('roof_contact',(-9,-6,7),(-14,0,3.9)),
    ('side_projection',(29,6,11),(16,0,2)),('interior',(8,9.1,1.8),(0,12.5,1.8)),
    ('gate_approach',(0,-24,2.1),(0,-6,1.8)),('stored_materials',(11,-9,4),(16,-5.5,1.4)),
    ('canopy_bearing',(-10,-3,4.3),(-12.5,0,3.65)),('dispatch_office',(-14.8,-11,1.8),(-10,-7.4,1.9))],
 'childcare':[('facade_close',(15,-26,11),(0,-2,3.2)),('architecture_close',(1,-11,3),(0,-3,1.7)),
    ('glass_close',(1,-10,6),(0,-2,4.6)),('roof_contact',(19,-10,13),(6,0,5)),
    ('side_projection',(23,2,7),(11,3,2.2)),('interior',(-9.6,-.5,1.7),(-6.7,5,2.3)),
    ('courtyard',(10,-15,5),(-3,-8,.7)),('rear_spine',(-6,10.6,1.8),(5,11.4,1.6)),
    ('veranda_contact',(-8,-8,2.8),(-4.1,-3.96,1.7))],
}


def cameras(kind):
    d=SPECS[kind]['dimensions_m'];scale=max(d['width'],d['depth'])/34
    basic=[('front',(0,-64,12)),('front_corner',(46,-58,32)),('aerial',(39,-49,69)),('top',(0,0,90)),
        ('left_side',(-64,0,12)),('right_side',(64,0,12)),('rear',(0,64,12)),('rear_side',(-46,58,32))]
    out=[dict(name=n,location=tuple(v*scale for v in loc),target=(0,.001 if n=='top' else 0,0 if n=='top' else d['height']*.4),
        **({'ortho_scale':d['width']*1.2} if n=='top' else {})) for n,loc in basic]
    return out+[dict(name=n,location=loc,target=target,whole=False,lens=24 if n in ('interior','bedroom','chassis','bearing_contact','dispatch_office') else 42)
                for n,loc,target in DETAILS[kind]]


def manifest(kind,version):
    s=SPECS[kind];cams=cameras(kind)
    return dict(candidate=f'{s["slug"]}-clay-v{version:03d}',method=C.METHOD,representation_kind='architectural_clay',
        archetype_id=s['id'],variant_id=s['variant'],state='prework',keeper_claimed=False,runtime_seed_allowed=False,
        measurement_contract=dict(dimensions_m=s['dimensions_m'],observed_storeys=s['storeys'],
            reference_reconciliation=s.get('reference_reconciliation','No topology reconciliation required.'),
            source_measurements=['Original designed building; generated references govern visible topology and cadence.'],
            hidden_assumptions=['Metric dimensions are authored, not surveyed.','Unseen rear rooms and structural details are inferred.',
                'Reference top view is overhead design evidence, not a georeferenced or survey orthophoto.']),
        roof_contract=dict(authority='Locked generated pixels; seated complete roofs with physical gable closures.'),
        identity_contract=dict(owner='New physical geometry for silhouette, openings, joinery and circulation.',bitmap_stickers='None in architectural clay.'),
        material_contract=dict(profile='Source-palette semantic architectural clay',limitations='Final source-conditioned texture work is separate.'),
        programme_contract=dict(storeys=s['storeys'],description=s['program'],uses=s['uses'],legal_approval=False),
        contact_contract=['Grade-zero foundation.','Physical through-carrier windows.','Supported roof, porch and entry.'],
        runtime_contract=dict(scale='fixed_native_only',resizing=False,installation='not installed',review='not tested'),
        camera_roster=cams,mandatory_review_views=[c['name'] for c in cams])


def prepare(a,entry,m):
    out=Path(a.output).resolve()
    external=Path('C:/dev-artifacts/CityPrompt').resolve()
    if not out.is_relative_to(external):raise ValueError('Build output must be external')
    if a.dry_run:
        print('DRY_RUN_PASS '+m['candidate']+' '+str(len(entry['sources']))+' source views')
        return None
    out.mkdir(parents=True,exist_ok=False)
    for name in ('sources','scripts','renders','review','evidence','boards'):(out/name).mkdir()
    for s in entry['sources']:
        shutil.copy2(s['original_path'],out/s['path'])
        assert C.digest(out/s['path'])==s['sha256']
    for name in ('generation-provenance.json',):shutil.copy2(Path(entry['_reference_root'])/name,out/'sources'/name)
    scripts=[Path(C.__file__),Path(__file__),HERE/'plan.py',HERE/'designs.json']
    for p in scripts:shutil.copy2(p,out/'scripts'/p.name)
    C.write_json(out/'source-entry.json',{k:v for k,v in entry.items() if not k.startswith('_')})
    m['source_contract']=dict(sources=entry['sources'],exact_variant_only=True,
        origin='original_generated_design',generated_references_explicitly_requested=True,
        substitute_for_existing_archetype=False,not_surveyed=True)
    m['provenance']=dict(scripts=[dict(path='scripts/'+p.name,sha256=C.digest(out/'scripts'/p.name)) for p in scripts],
        blender_version=C.bpy.app.version_string,python_version=sys.version,
        generation_api_calls_during_build=0,reference_generation='built-in image_gen, prompts and source chain in sources/generation-provenance.json',
        build_started_utc=C.utc(),render_source='actual optimized GLB reimport only')
    C.write_json(out/'prework-manifest.json',m)
    return out


def main():
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=list(SPECS),required=True)
    p.add_argument('--source-root',type=Path,required=True);p.add_argument('--output',required=True)
    p.add_argument('--version',type=int,default=1);p.add_argument('--resolution',type=int,default=1440);p.add_argument('--dry-run',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);m=manifest(a.kind,a.version)
    out=prepare(a,source_entry(a.kind,a.source_root),m)
    if out is None:return
    palette=dict(PALETTE)
    if a.kind=='depot':palette.update(wall=(.62,.60,.55),floor=(.42,.44,.43),roof=(.22,.23,.24),foundation=(.42,.43,.40))
    if a.kind=='recovery':palette.update(wall=(.65,.64,.57),pale=(.60,.63,.63),floor=(.46,.47,.44),foundation=(.40,.42,.40),trim=(.22,.25,.25))
    if a.kind=='yard':palette.update(wall=(.59,.58,.53),roof=(.26,.28,.29),foundation=(.35,.36,.34),hardware=(.32,.35,.36))
    if a.kind=='childcare':palette.update(wall=(.70,.68,.60),roof=(.30,.38,.36),timber=(.67,.49,.29),pale=(.60,.60,.54),floor=(.53,.45,.33),foundation=(.33,.35,.29),planting=(.30,.36,.17),sand=(.68,.60,.43))
    cams=C.setup(palette,m['camera_roster'],a.resolution);C.bevel=lambda *args,**kwargs:None
    for obj in C.bpy.context.scene.objects:
        q=2 if a.kind=='home' else 4
        if obj.type=='LIGHT':obj.location*=q;obj.data.energy*=q*q;obj.data.size*=q
        if obj.name=='QA ground - excluded':obj.scale*=6
    globals()[a.kind]()
    for obj in C.objects():
        bm=C.bmesh.new();bm.from_mesh(obj.data);C.bmesh.ops.triangulate(bm,faces=list(bm.faces))
        C.bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<=1e-10],context='FACES_ONLY')
        bm.to_mesh(obj.data);bm.free();obj.data.update()
    C.deliver(out,m,cams)


if __name__=='__main__':main()
