"""Four distinct exact-reference compositions for the bounded community batch."""
import math
import clay_core as C
import assemblies as A


def table(x,y,z=.16,w=2.4):
    C.box('Activity table',(x,y,z+.75),(w,1,.07),'timber','activity furniture')
    for xx in (x-w*.40,x+w*.40):
        for yy in (y-.38,y+.38):C.box('Grounded table leg',(xx,yy,z+.36),(.06,.06,.72),'hardware','activity furniture')
    for xx in (x-w*.3,x+w*.3):
        for yy in (y-1,y+1):A.garden_chair(xx,yy,z)


def palette(kind,base):
    p=dict(base)
    p.update({
        'hall':dict(wall=(.76,.75,.69),trim=(.14,.15,.14),roof=(.24,.26,.25),joint=(.15,.13,.12),timber=(.38,.25,.13),floor=(.51,.48,.41)),
        'cabin':dict(wall=(.42,.28,.16),trim=(.30,.20,.12),roof=(.32,.27,.19),joint=(.66,.61,.50),timber=(.42,.28,.16),foundation=(.35,.34,.30)),
        'inglewood':dict(wall=(.40,.18,.11),trim=(.13,.15,.14),roof=(.26,.28,.26),foundation=(.48,.46,.39),timber=(.35,.25,.15)),
        'shops':dict(wall=(.64,.57,.42),trim=(.44,.44,.37),roof=(.29,.24,.17),joint=(.22,.19,.14),timber=(.46,.38,.25),floor=(.49,.48,.43)),
    }[kind]);return p


def detail_cameras(kind):
    return {
        'hall':[
            ('facade_close',(23,-29,11),(1,-10,4)),('architecture_close',(-9,-15,3.4),(-8.6,-6.2,1.7)),
            ('glass_close',(3,-14,6),(3,-10,5.9)),('roof_contact',(20,-17,11),(11,-11.5,6.5)),
            ('side_projection',(24,1,6),(13,1,4)),('interior',(9,-7,1.8),(-2,3,2)),
            ('entry_connection',(-9,-4,1.8),(-3,-4,1.8)),('support_room',(-10,9,1.8),(2,10,1.8))],
        'cabin':[
            ('facade_close',(12,-16,7),(0,-4,2.6)),('architecture_close',(2.8,-8.2,2),(0,-4,1.9)),
            ('glass_close',(-3,-7,2.7),(-3,-4,2.1)),('roof_contact',(11,-9,8),(5.6,-3.7,3.9)),
            ('side_projection',(12,-1,5),(6,0,2.7)),('interior',(3,-2.8,2.1),(-3,2,2.4)),
            ('entry_steps',(4,-10,2.3),(0,-6.5,.5)),('hearth',(-2,1,2),(-5,-1.15,1.7))],
        'inglewood':[
            ('facade_close',(16,-26,13),(0,-8,5)),('architecture_close',(5,-15,3.4),(0,-8,2.1)),
            ('glass_close',(4.7,-12,2.6),(4.7,-8,2)),('roof_contact',(16,-17,16),(4,-3,8.8)),
            ('side_projection',(17,-1,10),(7,0,6)),('interior',(4,-5.9,1.8),(-3,4,1.7)),
            ('stair_arrival',(-2,6,5.9),(-4.5,2.8,4.3)),('upper_room',(4,-5,5.9),(-1,3,5.7)),
            ('roof_stair',(.7,1.94,10.3),(.5,5.4,7.6)),
            ('roof_half_landing',(-1.15,6.45,8.15),(0,5.3,6.2)),
            ('roof_exit',(4.5,.8,10.3),(.7,1.7,9.7))],
        'shops':[
            ('facade_close',(26,-32,10),(1,-11,3.7)),('architecture_close',(-9,-18,2.8),(-12,-11,1.6)),
            ('glass_close',(-13,-14,2.1),(-13,-11,1.7)),('roof_contact',(24,-20,12),(12,-9,5)),
            ('side_projection',(29,0,7),(15,0,3)),('interior',(-12,-8,1.8),(-12,2,1.7)),
            ('hardware_interior',(-4.3,-8,1.8),(-4,3,1.7)),('roof_services',(12,15,16),(1,1,5))],
    }[kind]


def hall():
    z=.16; eave=6.8
    # Main hall x[-6,13], y[-10,7]; the low L wing occupies left and rear.
    C.box('Connected ground slab',(0,1.5,z/2),(26,27,z),'foundation','foundation')
    C.box('Common occupied floor',(0,1.5,z+.01),(25.5,26.5,.02),'floor','floor')
    front,right,rear,left=A.faces(19,17,3.5,-1.5,'hall ')
    for f,span in ((front,19),(right,17),(rear,19),(left,17)):
        high=[A.hole(f.label+' clerestory',0,5.25,span-.7,1.22)]
        low=[]
        if f==front:low=[A.hole('Hall entrance-side tall window',-7.0,z,.95,2.55)]
        elif f==right:low=[A.hole('Hall side window '+str(i),u,1.05,1.4,1.5) for i,u in enumerate((-5,0,5))]
        elif f==left:low=[A.hole('Entry to activity hall',3, z,2.2,2.6)] # left u=-y-1.5 -> y=-4.5
        else:low=[A.hole('Hall to rear rooms',0,z,2.2,2.6)]
        f.wall(f.label+' enclosure',-span/2,span/2,z,eave-.18,holes=low+high)
        for h in high:f.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=round(span/1.1),rows=1)
        for h in low:
            if 'window' in h['id']:f.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=1 if f==front else 2,rows=2 if f==front else 1)
            else:
                # Internal passage is genuinely open; only physical jambs/head.
                for u in (h['u']-h['w']/2,h['u']+h['w']/2):f.part('Passage jamb',u,.12,z+1.3,.08,.28,2.6,'trim','internal passage')
                f.part('Passage head',h['u'],.12,z+2.6,2.28,.28,.08,'trim','internal passage')
    # Outer perimeter of connected low L; no opaque duplicate shared walls.
    wingfront=C.Face((-9.5,-6,0),(1,0,0),(0,1,0),'low wing front')
    h=A.hole('Main glazed lobby entrance',0,z,3.8,2.9)
    wingfront.wall('Entry dark-brick wall',-3.5,3.5,z,3.65,role='joint',holes=[h]);A.glazing(wingfront,h,door=True,cols=4)
    wingfront.part('Lobby transom',0,.12,2.60,3.70,.10,.065,'trim','lobby glazing')
    wingfront.part('Entry canopy',0,-.65,3.40,5.1,1.65,.16,'trim','entry canopy')
    outerleft=C.Face((-13,4.5,0),(0,-1,0),(1,0,0),'low west')
    hs=[A.hole('Low-wing window '+str(i),u,1.0,2.3,1.4) for i,u in enumerate((-7,-2,3,8))]
    outerleft.wall('Low west brick',-10.5,10.5,z,3.65,role='joint',holes=hs)
    for h in hs:A.glazing(outerleft,h)
    back=C.Face((0,15,0),(-1,0,0),(0,-1,0),'low north')
    hs=[A.hole('Rear exit',0,z,1.5,2.6)]+[A.hole('Rear room '+str(i),u,1,2.6,1.4) for i,u in enumerate((-9,-4,4,9))]
    back.wall('Rear low brick',-13,13,z,3.65,role='joint',holes=hs)
    for h in hs:A.glazing(back,h,door='exit' in h['id'])
    east=C.Face((13,11,0),(0,1,0),(-1,0,0),'low east')
    h=A.hole('Side meeting window',0,1,3.8,1.4);east.wall('Low east brick',-4,4,z,3.65,role='joint',holes=[h]);A.glazing(east,h)
    # Fill exposed side below front-left re-entrant corner (y -10 to -6 stays main hall).
    C.box('Rear wing roof',(0,11,3.65),(26.4,8.4,.22),'roof','low wing roof')
    C.box('West wing roof',(-9.5,.5,3.65),(7.4,13,.22),'roof','low wing roof')
    # Shallow hipped junction visible in the locked top reference.
    C.solid_surface('Low west roof field',[(-13.2,-6,3.78),(-6,-6,3.78),(-6,7,4.05),(-13.2,15.2,3.78)],.06,'roof','wing roof junction')
    C.solid_surface('Low rear roof field',[(-13.2,15.2,3.78),(-6,7,4.05),(13.2,7,3.78),(13.2,15.2,3.78)],.06,'roof','wing roof junction')
    C.beam('Diagonal wing roof seam',(-13.2,15.2,3.80),(-6,7,4.07),.06,.045,'trim','wing roof junction')
    for a,b in [((-13.1,-6,3.86),(-13.1,15.1,3.86)),((-13.1,15.1,3.86),(13.1,15.1,3.86)),((13.1,15.1,3.86),(13.1,7.1,3.86))]:
        C.beam('Low roof perimeter upstand',a,b,.14,.24,'joint','low roof upstand')
    C.box('Hall timber soffit',(3.5,-1.5,eave),(22.8,20.8,.20),'timber','soffit')
    C.box('Hall metal roof',(3.5,-1.5,eave+.15),(22.9,20.9,.12),'roof','roof')
    for x in (-6.6,-1.8,3,7.8,12.6):
        C.beam('Inclined front column',(x,-11.65,z),(x+.5,-11.25,eave-.10),.14,.14,'hardware','inclined columns')
        C.box('Seated column plate',(x,-11.65,z+.035),(.38,.38,.07),'trim','column feet')
        C.beam('Soffit front rafter',(x+.5,-11.85,eave-.14),(x+.5,8.6,eave-.14),.14,.28,'timber','soffit rafters')
    for y in (-6.5,-1.5,3.5,7.5):
        C.beam('Inclined side column',(14.1,y,z),(13.75,y+.4,eave-.1),.14,.14,'hardware','inclined columns')
        # side feet sit on their own grade-zero concrete piers outside main slab
        C.box('Side column pier',(14.1,y,z/2),(.5,.5,z),'foundation','foundation')
        C.box('Side column plate',(14.1,y,z+.03),(.35,.35,.06),'trim','column feet')
    for x in (-1,5):
        for y in (-4,2):table(x,y,z+.02,3)
    for x in (-8,0,8):table(x,11,z+.02)
    C.box('Reception counter',(-10,-1,z+.52),(2.8,.8,1.04),'timber','lobby')
    for x in (-1,6):
        for y in (-4,3):A.light_fixture(x,y,5.9,length=3,ceiling=6.70,qa_size=5,qa_power=400)
    for x,y in ((-9,-2),(-9,7),(1,11),(9,11)):C.qa_room_light('Low community rooms',(x,y,3.2),220,4)
    C.CONTACTS.append(dict(name='Main hall entrance',door_centre=[-9.5,-6,z],clear_width=3.8,entry_direction=[0,-1],ground_floor=z))


def cabin():
    z=.54; walltop=3.45; ridge=5.8
    C.box('Stone foundation',(0,0,z/2),(12,8,z),'foundation','foundation')
    C.box('Porch stone base',(0,-5.25,z/2),(12,2.5,z),'foundation','foundation')
    C.box('Cabin floor',(0,0,z),(11.5,7.5,.06),'floor','floor')
    C.box('Porch deck',(0,-5.25,z),(12,2.5,.07),'timber','porch')
    ff=A.faces(12,8)
    for f,span in zip(ff,(12,8,12,8)):
        hs=([A.hole('Main cabin door',0,z+.035,1.12,2.25)]+[A.hole('Front window '+str(i),u,1.22,1.35,1.45) for i,u in enumerate((-3.2,3.2))]) if f==ff[0] else [A.hole(f.label+' window '+str(i),u,1.22,1.28,1.45) for i,u in enumerate((-2.1,2.1))]
        if f==ff[2]:hs.append(A.hole('Rear cabin exit',0,z+.035,1.05,2.25))
        f.wall(f.label+' log carrier',-span/2,span/2,z,walltop,depth=.30,role='joint',holes=hs)
        # Individually constructed hewn log courses, split around every opening.
        for j in range(10):
            low=z+j*(walltop-z)/10;high=low+(walltop-z)/10-.035
            parts=[(-span/2-.10,span/2+.10)]
            for h in hs:
                if low<h['z']+h['h'] and high>h['z']:
                    a,b=h['u']-h['w']/2-.035,h['u']+h['w']/2+.035
                    parts=[p for l,r in parts for p in ((l,min(r,a)),(max(l,b),r)) if p[1]-p[0]>.01]
            for a,b in parts:f.part('Hewn log course',(a+b)/2,.08,(low+high)/2,b-a,.36,high-low,'wall','log wall courses')
        for h in hs:
            if 'door' in h['id'].lower() or 'exit' in h['id']:f.door(h['id'],h['u'],h['z'],h['w'],h['h'],panels=1)
            else:
                f.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=2,rows=2,frame='trim',depth=.30)
                for side in (-1,1):
                    su=h['u']+side*(h['w']/2+.27)
                    f.part('Timber shutter',su,-.13,h['z']+h['h']/2,.43,.08,h['h']+.12,'timber','shutters')
                    for zz in (h['z']+.19,h['z']+h['h']-.19):f.part('Shutter cross brace',su,-.18,zz,.46,.06,.095,'trim','shutters')
    # True gable ends, across-front ridge, kick in the front roof over the porch.
    for x in (-6,5.72):C.prism('Closed timber gable',[(-4,walltop),(0,ridge-.16),(4,walltop)],'x',x,x+.28,'timber','gable')
    segments=[(-6.9,3.2,-4,3.63),(-4,3.63,0,ridge),(0,ridge,4.45,3.43)]
    for a,za,b,zb in segments:
        C.solid_surface('Closed pitched roof',[(-6.45,a,za),(6.45,a,za),(6.45,b,zb),(-6.45,b,zb)],.17,'roof','roof')
        for x in (-6.4,-4.8,-3.2,-1.6,0,1.6,3.2,4.8,6.4):C.beam('Supported exposed rafter',(x,a,za-.15),(x,b,zb-.15),.12,.18,'timber','rafters')
        for i in range(1,math.ceil((b-a)/.30)):
            y=a+i*(b-a)/math.ceil((b-a)/.30);zz=za+(zb-za)*(y-a)/(b-a)
            C.box('Shingle course edge',(0,y,zz+.01),(12.88,.015,.022),'joint','roof courses')
    for x in (-5.7,-1.9,1.9,5.7):
        C.rod('Porch log post',(x,-6.25,z+.035),(x,-6.25,3.13),.13,'timber','porch posts')
    C.beam('Continuous porch bearing beam',(-6.3,-6.25,3.11),(6.3,-6.25,3.11),.22,.24,'timber','porch beam')
    A.steps('Front porch step',0,-6.5,2.0,z+.035,n=3,run=.31,role='foundation')
    C.box('Rear exit landing',(0,4.6,(z+.035)/2),(1.7,1.2,z+.035),'foundation','rear entry landing')
    before=set(C.bpy.data.objects);opening_start=len(C.OPENINGS)
    A.steps('Rear exit step',0,-5.2,1.7,z+.035,n=3,run=.31,role='foundation')
    A.rotate_new(before,opening_start,0,0,math.pi)
    # Masonry fireplace/chimney with roof-contact flashing; no unsupported stack.
    C.box('Grounded chimney',(-5.0,-1.15,3.05),(1.05,1.12,6.10),'foundation','chimney')
    C.box('Chimney cap',(-5,-1.15,6.14),(1.23,1.3,.13),'trim','chimney')
    C.box('Unlit firebox',(-4.445,-1.15,1.2),(.07,.72,1.05),'hardware','hearth')
    C.box('Hearth slab',(-4.7,-1.15,z+.07),(1.8,1.6,.14),'foundation','hearth')
    for x in (-2.0,2.1):table(x,1.4,z+.035,2.4)
    for x in (-3.2,3.2):
        C.box('Recreation bench',(x,-2,z+.46),(2.6,.46,.12),'timber','bench')
        for xx in (x-1,x+1):C.box('Bench foot',(xx,-2,z+.21),(.10,.38,.42),'timber','bench')
    for x in (-3,3):A.light_fixture(x,0,4.6,length=1.5,ceiling=5.63,qa_size=4,qa_power=220)
    C.CONTACTS.append(dict(name='Porch connected steps',door_centre=[0,-4,z+.035],clear_width=1.12,ground_floor=z+.035,entry_direction=[0,-1]))


def shops(lettering,shelf):
    w,d,z,roof=30,22,.15,5.0
    C.box('Continuous shop foundation',(0,0,z/2),(w,d,z),'foundation','foundation')
    C.box('Retail floor',(0,0,z+.01),(w-.4,d-.4,.02),'floor','floor')
    front,right,rear,left=A.faces(w,d)
    centres=(-11.25,-3.75,3.75,11.25);hs=[]
    for i,cx in enumerate(centres):
        hs.extend([A.hole('Shop '+str(i)+' door',cx+.9,z,1.0,2.65),A.hole('Shop '+str(i)+' display',cx-1.3,.65,2.6,2.0)])
    front.wall('Front shop enclosure',-15,15,z,3.85,holes=hs)
    for h in hs:A.glazing(front,h,door='door' in h['id'],cols=1 if 'door' in h['id'] else 2)
    for f in (right,left):
        ranges=((-11,-8.65,3.85),(-8.65,11,roof)) if f==right else ((-11,8.65,roof),(8.65,11,3.85))
        for a,b,top in ranges:
            f.wall(f.label+' metal enclosure',a,b,z,top,role='pale')
            section=C.Face(f.p((a+b)/2,0,0),f.t,f.n,f.label+' cladding section')
            A.vertical_cladding(section,b-a,z,top,[],spacing=.20,role='trim')
    rh=[A.hole('Service door '+str(i),-cx,z,1.1,2.5) for i,cx in enumerate(centres)]
    rear.wall('Rear service enclosure',-15,15,z,roof,role='pale',holes=rh)
    A.vertical_cladding(rear,30,z,roof,rh,spacing=.20,role='trim')
    for h in rh:rear.door(h['id'],h['u'],h['z'],h['w'],h['h'],role='trim',panels=1)
    for x in (-7.5,0,7.5):C.box('Tenant separation',(x,0,(roof+z)/2),(.18,21.6,roof-z),'pale','tenant partition')
    # Flat roof and shallow false mansard have full side returns and sealed ends.
    roofslab=C.box('Closed main roof',(0,1.225,roof),(30.2,19.75,.2),'foundation','roof')
    for x in (-15,15):C.box('Side roof upstand',(x,1.30,5.2),(.20,19.6,.4),'wall','parapet')
    C.box('Rear roof upstand',(0,11,5.2),(30.2,.20,.4),'wall','parapet')
    front.part('Timber sign band',0,-.10,3.40,30.3,.18,.78,'timber','sign band')
    A.vertical_cladding(front,30.3,3.03,3.80,[],spacing=.16,role='pale')
    C.solid_surface('Front mansard',[(-15.35,-11.65,3.88),(15.35,-11.65,3.88),(14.35,-10.65,5.64),(-14.35,-10.65,5.64)],.15,'roof','mansard')
    C.box('Mansard underside',(0,-10.15,3.80),(30.7,3,.14),'timber','mansard soffit')
    for side in (-1,1):
        x=side*15.35
        C.solid_surface('Mansard side return',[(x,-11.65,3.88),(x, -8.65,3.88),(side*14.35,-8.65,5.64),(side*14.35,-10.65,5.64)],.15,'roof','mansard')
        C.prism('Mansard end closure',[(side*14.35,5.64),(x,3.88),(x,3.78),(side*14.35,3.78)],'y',-8.68,-8.60,'roof','mansard closure')
    C.box('Mansard top closure',(0,-9.65,5.58),(28.7,2,.12),'roof','mansard closure')
    C.box('Mansard rear closure',(0,-8.65,5.31),(28.7,.10,.66),'roof','mansard closure')
    for i in range(1,10):
        y=-11.65+i/10;zz=3.88+1.76*i/10
        C.box('Mansard course',(0,y,zz+.007),(30.7-2*i/10,.016,.014),'joint','roof courses')
    for name,cx in zip(('PRAIRIE DELI','HARDWARE SUPPLY','LIQUOR STORE','GIFTS & MORE'),centres):
        front.part('Tenant sign',cx,-.25,3.42,5.1,.08,.59,'pale','tenant signage')
        lettering(front,name,cx,3.42,4.8,.36,depth=-.31)
    right.part('Right sign return',-10.0,-.10,3.40,2.7,.18,.78,'timber','sign band')
    right.part('Right tenant sign',-10.0,-.25,3.42,2.5,.08,.59,'pale','tenant signage')
    lettering(right,'GIFTS & MORE',-10.0,3.42,2.3,.32,depth=-.31)
    for x,y in ((-9,-3),(1,6)):
        C.box('HVAC curb',(x,y,5.22),(2.5,2.1,.24),'trim','mechanical curb')
        C.box('Rooftop air unit',(x,y,5.75),(2.4,2, .84),'pale','roof plant')
        for dy in (-.6,-.2,.2,.6):C.box('Air intake louvre',(x+1.21,y+dy,5.75),(.035,.08,.60),'trim','roof plant')
    for x in (-10,0,10):
        C.rod('Vent riser',(x,7,5.1),(x,7,5.85),.15,'trim','roof vents');C.box('Vent cap',(x,7,5.85),(.45,.45,.10),'trim','roof vents')
    C.cut_box(roofslab,'Small rooflight aperture',(1,-4,5),(1.25,1.25,1))
    pts=[(.37,-4.73,5.23),(1.73,-4.73,5.23),(1.73,-3.37,5.23),(.37,-3.37,5.23)]
    apex=(1.05,-4.05,5.85)
    for i,a in enumerate(pts):
        b=pts[(i+1)%4];C.beam('Rooflight curb',a,b,.12,.26,'trim','rooflight')
        C.solid_surface('Rooflight pane',[a,b,apex],.014,'glass','rooflight');C.beam('Rooflight hip',a,apex,.045,.045,'trim','rooflight')
    for a,b in [((-9,-1.8,5.19),(10,-1.8,5.19)),((10,-1.8,5.19),(10,7,5.19)),((1,5,5.19),(1,-1.8,5.19))]:
        C.rod('Seated services conduit',a,b,.045,'hardware','roof services')
    for cx in centres:
        for y in (-2,2,6):shelf(cx-1,y,z+.02)
        C.box('Tenant checkout',(cx+1.4,-6,z+.5),(1.8,.8,1),'timber','shop counter')
        for y in (-6,1,7):A.light_fixture(cx,y,4.2,ceiling=4.90,length=2,qa_power=220,qa_size=4)
    C.CONTACTS.append(dict(name='Four level shop entrances',door_centres=[[cx+.9,-11,z] for cx in centres],ground_floor=z,clear_width=1.0))


def segmental_bay(f,ident,u,z,width,height,door=False,rise=.42,cols=None):
    """Glazed rectangle plus real curved masonry infill above, in a cut carrier."""
    spring=z+height-rise
    f.window(ident,u,z,width,height,cols=cols or 3,rows=1,frame='trim',sill=not door,kind='glazed door with sidelights' if door else 'window')
    # Infill closes the corners above the shallow arch while leaving its centre open.
    curve=[(u-width/2+width*i/24,spring+rise*math.sin(math.pi*i/24)) for i in range(25)]
    f.panel(ident+' arch spandrel',[(u-width/2,z+height),(u+width/2,z+height)]+list(reversed(curve)),0,.29,'wall','segmental masonry arch')
    for i in range(24):
        a,b=curve[i],curve[i+1]
        f.panel(ident+' arch voussoir',[(a[0],a[1]),(b[0],b[1]),(b[0],b[1]+.16),(a[0],a[1]+.16)],-.025,.05,'wall','arch ring')
    f.part(ident+' transom',u,.13,z+height-.88,width-.10,.10,.07,'trim','storefront transom')
    if door:
        for du in ((-.10,.10) if cols==2 else (.37,)):
            C.rod(ident+' active leaf pull',f.p(u+du,.02,z+.85),f.p(u+du,.02,z+1.35),.018,'hardware','door hardware')


def inglewood(lettering,shelf):
    w,d,z,upper,roof=14,16,.17,4.4,8.9
    C.box('Masonry foundation',(0,0,z/2),(w,d,z),'foundation','foundation')
    C.box('Ground retail floor',(0,0,z+.01),(w-.5,d-.5,.02),'floor','floor')
    ff=A.faces(w,d)
    for f,span in zip(ff,(14,16,14,16)):
        street=f in ff[:2]
        us=(-4.5,0,4.5) if f==ff[0] else (-5,0,5)
        hs=[A.hole(f.label+' shop bay '+str(i),u,z if i==1 else .48,3.3,3.35 if i==1 else 3.04) for i,u in enumerate(us)] if street else [A.hole(f.label+' service exit',0,z,1.25,2.6)]+[A.hole(f.label+' back window '+str(i),u,1,1.6,2) for i,u in enumerate((-4.5,4.5))]
        f.wall(f.label+' lower masonry',-span/2,span/2,z,upper-.18,holes=hs,depth=.29)
        for i,h in enumerate(hs):
            if street:segmental_bay(f,h['id'],h['u'],h['z'],h['w'],h['h'],door=i==1)
            else:A.glazing(f,h,door=i==0,cols=1 if i==0 else 2)
        uh=([A.hole(f.label+' balcony door',0,upper,2.75,3.10)]+[A.hole(f.label+' upper sash '+str(i),u,5.05,1.15,2.45) for i,u in enumerate((-5,-3.2,3.2,5))]) if street else [A.hole(f.label+' rear office sash '+str(i),u,5.05,1.35,2.45) for i,u in enumerate((-4.3,0,4.3))]
        f.wall(f.label+' upper masonry',-span/2,span/2,upper-.18,roof,holes=uh,depth=.29)
        for h in uh:
            if street:segmental_bay(f,h['id'],h['u'],h['z'],h['w'],h['h'],door='door' in h['id'],rise=.12,cols=2 if 'door' in h['id'] else 1)
            else:f.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=1,rows=2)
        if street:
            # Shallow brick bay frames belong to the facade geometry.
            for a,b in ((-span/2+.55,-2.45),(-2.20,2.20),(2.45,span/2-.55)):
                for u in (a,b):f.part('Upper bay brick jamb',u,-.035,6.35,.13,.07,3.52,'wall','street bay surround')
                f.part('Upper bay brick header',(a+b)/2,-.035,8.08,b-a+.13,.07,.14,'wall','street bay surround')
            slab=f.part('Supported balcony',0,-.78,upper-.10,3.8,1.6,.2,'trim','balcony')
            for u in (-1.45,1.45):
                C.beam('Balcony bearing bracket',f.p(u,.1,upper-1.0),f.p(u,-1.45,upper-.2),.14,.16,'trim','balcony structure')
            A.seated_guard('Balcony front',f.p(-1.85,-1.55,upper),f.p(1.85,-1.55,upper))
            for u in (-1.85,1.85):A.seated_guard('Balcony return',f.p(u,-1.55,upper),f.p(u,.01,upper))
        # Cornice is assembled from seated continuous moulding bands and dentils.
        for zz,t,h in ((8.46,.26,.12),(8.66,.48,.16),(8.84,.62,.12)):
            f.part('Cornice moulding',0,-t/2+.01,zz,span+.40,t,h,'trim','cornice')
        for i in range(round(span/.55)):
            u=-span/2+(i+.5)*span/round(span/.55)
            f.part('Cornice dentil',u,-.17,8.56,.16,.27,.15,'foundation','cornice')
        f.wall(f.label+' parapet',-span/2,span/2,roof,9.42,depth=.29)
        f.part('Parapet coping',0,.12,9.45,span+.10,.40,.10,'foundation','parapet')
        for u in ((-span/2+.14,span/2-.14) if f==ff[0] else (-span/2+.14,0,span/2-.14)):
            f.part('Parapet brick pier',u,.12,9.46,.44,.45,.85,'wall','parapet')
            f.part('Parapet pier cap',u,.12,9.91,.54,.55,.10,'foundation','parapet')
    f=ff[0]
    pediment=[(-2.7,9.40),(-1.8,10.05),(1.8,10.05),(2.7,9.40)]
    f.panel('Raised central brick parapet',pediment,0,.29,'wall','front parapet')
    for a,b in zip(pediment[:3],pediment[1:]):C.beam('Pediment coping',f.p(a[0],.13,a[1]+.04),f.p(b[0],.13,b[1]+.04),.13,.42,'foundation','front parapet')
    f=ff[0];f.part('Merchants sign fascia',0,-.07,3.94,12.3,.13,.47,'trim','signage')
    lettering(f,'INGLEWOOD MERCHANDISE CO.',0,3.94,11.9,.30,depth=-.15)
    C.box('Projecting merchants sign',(1.9,-8.75,3.18),(.075,1.25,.78),'trim','shop blade sign')
    for zz in (2.83,3.54):C.beam('Blade wall bracket',(1.9,-7.95,zz),(1.9,-9.35,zz),.04,.04,'trim','shop blade sign')
    # Connected ground-to-office flight and a separate compact roof-service stair.
    floor=C.box('Upper offices floor',(0,0,upper-.09),(13.42,15.42,.18),'floor','floor',0)
    roofobj=C.box('Closed membrane roof',(0,0,roof-.1),(14,16,.2),'roof','roof',0)
    sx,sy,run,count=-4.5,-1.5,.25,22;end=sy+run*count
    C.cut_box(floor,'Stair opening',(sx,(sy-.2+end)/2,upper),(1.7,end-sy+.2,1))
    for lo,hi in ((z+.02,upper),):
        stair=A.straight_stair('Connected stair',sx,sy,lo,hi,width=1.35,run=run,count=count)
        for x in (sx-.89,sx+.89):A.seated_guard('Floor aperture guard',(x,sy-.2,hi),(x,end,hi))
        A.seated_guard('Aperture end guard',(sx-.89,sy-.2,hi),(sx+.89,sy-.2,hi))
        C.CONTACTS.append(dict(name='Continuous stair flight',**stair))
    mid=(upper+roof)/2
    A.straight_stair('Roof service lower flight',-.7,3,upper,mid,width=1.15,run=.25,count=11)
    C.box('Roof stair half landing',(0,6.23,mid-.09),(2.7,.96,.18),'floor','roof stair landing')
    A.seated_guard('Half landing rear',(-1.32,6.68,mid),(1.32,6.68,mid))
    for x in (-1.32,1.32):A.seated_guard('Half landing side',(x,5.78,mid),(x,6.68,mid))
    for x in (-1.2,1.2):C.box('Landing bearing post',(x,6.45,(upper+mid)/2),(.12,.12,mid-upper),'trim','roof stair support')
    before=set(C.bpy.data.objects);opening_start=len(C.OPENINGS)
    A.straight_stair('Roof service upper flight',-.7,-5.75,mid,roof,width=1.15,run=.25,count=11)
    A.rotate_new(before,opening_start,0,0,math.pi)
    C.cut_box(roofobj,'Roof stair aperture',(0,4.855,roof),(2.7,3.71,1))
    # Door opens onto the roof at the head of the return flight, facing forward.
    room=A.faces(3.2,6.3,0,4.85,'roof access ')
    for f,span in zip(room,(3.2,6.3,3.2,6.3)):
        hs=[A.hole('Roof maintenance door',.7,roof,1.0,2.1)] if f==room[0] else []
        inset=.20 if f in (room[1],room[3]) else 0
        f.wall('Roof stairhead enclosure',-span/2+inset,span/2-inset,roof,roof+2.35,depth=.20,role='pale',holes=hs)
        for h in hs:f.door(h['id'],h['u'],h['z'],h['w'],h['h'],role='trim',panels=1)
    C.box('Stairhead cap',(0,4.85,roof+2.40),(3.5,6.6,.14),'roof','roof access')
    # True roof aperture beneath four-sided glazed pyramidal skylight.
    C.cut_box(roofobj,'Skylight aperture',(1.1,-1.6,roof),(3,3,1))
    for x in (-.48,2.68):C.box('Skylight curb',(x,-1.6,roof+.17),(.16,3.32,.34),'trim','skylight')
    for y in (-3.18,-.02):C.box('Skylight curb',(1.1,y,roof+.17),(3.32,.16,.34),'trim','skylight')
    pts=[(-.56,-3.26,roof+.34),(2.76,-3.26,roof+.34),(2.76,.06,roof+.34),(-.56,.06,roof+.34)]
    tip=(1.1,-1.6,roof+1.15)
    for i,a in enumerate(pts):
        b=pts[(i+1)%4];C.solid_surface('Skylight pane',[a,b,tip],.016,'glass','skylight');C.beam('Skylight hip',a,tip,.06,.06,'trim','skylight')
    for x,y in ((.5,-3),(3.8,2),(1.5,5)):shelf(x,y,z+.02)
    for x,y in ((1,-4),(4,2),(4,5)):A.desk(x,y,upper)
    C.qa_room_light('Roof stair proof',(0,5.2,10.5),180,2)
    for zz in (3.75,8.15):
        for x,y in ((1,-4),(2,3),(-4,5)):C.qa_room_light('Occupied level',(x,y,zz),240,4)
    C.CONTACTS.append(dict(name='Retail main entrance',door_centre=[0,-8,z],clear_width=3.3,ground_floor=z,entry_direction=[0,-1]))
