"""Shared opening, furniture and contact primitives; no inherited building geometry."""
import clay_core as C
import math

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

def steps(name,cx,wall_y,width,top,n=3,run=.28,role='timber'):
    for i in range(n):
        height=top*(i+1)/n
        y=wall_y-(n-i-.5)*run
        C.box(name+str(i),(cx,y,height/2),(width,run+.006,height),role,'entry steps')

def sofa(x,y,z):
    for xx in (x-.98,x+.98):
        for yy in (y-.31,y+.31):C.box('Sofa grounded foot',(xx,yy,z+.045),(.12,.12,.09),'timber','living furniture')
    C.box('Sofa plinth',(x,y,z+.19),(2.4,.88,.22),'timber','living furniture')
    C.box('Sofa seat',(x,y-.03,z+.4),(2.25,.86,.24),'interior','living furniture')
    C.box('Sofa back',(x,y+.39,z+.68),(2.4,.16,.72),'interior','living furniture')
    for xx in (x-1.12,x+1.12):C.box('Sofa arm',(xx,y,z+.53),(.2,.9,.5),'interior','living furniture')
    C.box('Coffee table',(x,y-1.25,z+.42),(1.15,.62,.1),'timber','living furniture')
    for xx in (x-.43,x+.43):
        for yy in (y-1.44,y-1.06):C.box('Coffee table leg',(xx,yy,z+.2),(.045,.045,.4),'trim','living furniture')

def bed(x,y,z):
    for xx in (x-.64,x+.64):
        for yy in (y-.82,y+.82):C.box('Bed grounded foot',(xx,yy,z+.035),(.13,.13,.07),'timber','bedroom furniture')
    C.box('Bed frame',(x,y,z+.22),(1.6,2,.32),'timber','bedroom furniture')
    C.box('Mattress',(x,y,z+.48),(1.53,1.93,.21),'interior','bedroom furniture')
    C.box('Duvet',(x,y-.2,z+.61),(1.52,1.35,.06),'pale','bedroom furniture')
    C.box('Headboard',(x,y+.99,z+.6),(1.67,.09,1.0),'timber','bedroom furniture')
    for xx in (x-.39,x+.39):C.box('Pillow',(xx,y+.60,z+.63),(.61,.36,.13),'interior','bedroom furniture')

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

def light_fixture(x,y,z,length=2,*,ceiling,qa_size=3,qa_power=180):
    C.box('Linear light housing',(x,y,z),(length,.15,.12),'trim','interior lights')
    C.box('Linear light diffuser',(x,y,z-.065),(length-.08,.11,.012),'interior','interior lights')
    for xx in (x-length*.35,x+length*.35):
        top=ceiling(xx) if callable(ceiling) else ceiling
        C.rod('Light suspension',(xx,y,z+.045),(xx,y,top),.013,'hardware','interior lights',sides=8)
        C.box('Light ceiling fixing',(xx,y,top-.014),(.09,.09,.028),'trim','interior lights')
    C.qa_room_light('Room illumination',(x,y,z-.20),qa_power,qa_size)

def straight_stair(name,x,y,lower,upper,width=1.0,run=.27,count=18):
    """Supported stair, ascending +y; caller provides the upper-floor opening."""
    rise=(upper-lower)/count
    for i in range(count):
        h=rise*(i+1)
        C.box(name+' riser '+str(i),(x,y+(i+.5)*run,lower+h/2),(width,run+.003,h),'timber','stairs')
    for side in (-1,1):
        xx=x+side*(width/2-.025)
        C.beam(name+' sloped handrail',(xx,y+run*.5,lower+rise+1.02),(xx,y+(count-.5)*run,upper+1.02),.045,.045,'hardware','stairs')
        for i in range(count):
            C.box(name+' stair baluster',(xx,y+(i+.5)*run,lower+rise*(i+1)+.51),(.025,.025,1.02),'hardware','stairs')
    return dict(x=x,y=y,width=width,length=run*count,lower=lower,upper=upper,rise=rise,run=run)


def seated_guard(name,a,b,height=1.02,role='hardware',spacing=.12,end_anchors=True):
    """Guard infill supported by explicit floor-seated posts and anchor plates."""
    C.railing(name,a,b,height=height,role=role,spacing=spacing,end_posts=False)
    count=max(1,math.ceil(math.dist(a,b)/1.2))
    for i in range(count+1):
        if not end_anchors and i in (0,count):continue
        x,y,z=(a[j]+(b[j]-a[j])*i/count for j in range(3))
        C.box(name+' seated anchor plate',(x,y,z+.009),(.14,.14,.018),role,'guard anchors')
        C.beam(name+' grounded structural post',(x,y,z+.014),(x,y,z+height+.02),.04,.04,role,'guard anchors')
        for dx in (-.045,.045):
            for dy in (-.045,.045):C.rod(name+' anchor bolt',(x+dx,y+dy,z+.013),(x+dx,y+dy,z+.026),.009,role,'guard anchors',sides=6)

def bathroom(x,y,z):
    """Simple seated fixtures, never a certification of sanitary layout."""
    C.box('Vanity cabinet',(x-.45,y,z+.42),(.7,.48,.84),'timber','sanitary fittings')
    C.box('Vanity basin',(x-.45,y,z+.87),(.68,.46,.06),'pale','sanitary fittings')
    C.rod('Basin tap',(x-.45,y+.15,z+.90),(x-.45,y+.15,z+1.12),.015,'hardware','sanitary fittings')
    C.box('Toilet pedestal',(x+.4,y-.05,z+.18),(.28,.38,.36),'pale','sanitary fittings')
    C.box('Toilet bowl',(x+.4,y-.14,z+.36),(.43,.57,.20),'pale','sanitary fittings')
    C.box('Toilet cistern',(x+.4,y+.12,z+.61),(.43,.19,.54),'pale','sanitary fittings')

def vertical_cladding(f,span,z0,z1,holes,spacing=.15,role='timber'):
    for i in range(math.ceil(span/spacing)):
        u=-span/2+(i+.5)*span/math.ceil(span/spacing)
        spans=[(z0,z1)]
        for h in holes:
            if h['u']-h['w']/2-.01<u<h['u']+h['w']/2+.01:
                spans=[s for a,b in spans for s in ((a,min(b,h['z'])),(max(a,h['z']+h['h']),b)) if s[1]-s[0]>.001]
        for a,b in spans:f.part('Vertical cladding seam',u,-.012,(a+b)/2,.014,.028,b-a,role,'cladding',0)

def rotate_new(before,opening_start,cx,cy,angle):
    """Rigid placement preserves physical dimensions and world-space aperture evidence."""
    from mathutils import Matrix,Vector
    rotation=Matrix.Rotation(angle,4,'Z')
    transform=Matrix.Translation((cx,cy,0))@rotation
    C.bpy.context.view_layer.update()
    for obj in set(C.bpy.data.objects)-before:obj.matrix_world=transform@obj.matrix_world
    for h in C.OPENINGS[opening_start:]:
        h['face_origin']=list(transform@Vector(h['face_origin']))
        h['face_tangent']=list(rotation.to_3x3()@Vector(h['face_tangent']))
        h['face_inward']=list(rotation.to_3x3()@Vector(h['face_inward']))

def foliage(name,centre,size,role='planting',detail=1):
    C.bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=detail,radius=1,location=centre)
    obj=C.bpy.context.object;obj.name=name;obj.scale=size
    obj.data.materials.append(C.MATS[role]);C.tag(obj,role,'garden planting')
    return obj

def shrub(x,y,z=.15,height=.65):
    C.rod('Shrub rooted stem',(x,y,z),(x,y,z+height*.65),.025,'timber','garden planting')
    for i,(dx,dy) in enumerate(((-.16,0),(.16,.05),(0,-.13),(0,.16))):
        foliage('Leafy shrub crown',(x+dx,y+dy,z+height*.55),(.24,.24,height*.50),detail=1)

def small_tree(x,y,z=.15,height=3.8,spread=1.0):
    for i,(dx,dy) in enumerate(((-.6,-.2),(.5,-.1),(.1,.55))):
        base=(x+(i-1)*.09,y,z)
        tip=(x+dx*spread,y+dy*spread,z+height*.76)
        C.rod('Serviceberry rooted trunk',base,tip,.046,'timber','garden planting')
        for j in range(3):
            end=(tip[0]+math.cos(i*2+j*2)*.60*spread,tip[1]+math.sin(i*2+j*2)*.6*spread,z+height*(.72+j*.09))
            C.rod('Serviceberry branch',tip,end,.022,'timber','garden planting')
            foliage('Serviceberry leafy crown',end,(.70*spread,.65*spread,.75),detail=2)

def garden_chair(x,y,z=.15):
    C.box('Garden chair seat',(x,y,z+.44),(.48,.49,.06),'timber','garden furniture')
    C.box('Garden chair back',(x,y+.23,z+.69),(.48,.055,.46),'timber','garden furniture')
    for xx in (x-.20,x+.20):
        for yy in (y-.20,y+.20):C.box('Garden chair leg',(xx,yy,z+.21),(.035,.035,.42),'hardware','garden furniture')
