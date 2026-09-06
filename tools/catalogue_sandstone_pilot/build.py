"""Source-locked sandstone Romanesque courtyard civic building, clay first."""
import sys, math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import support as S
C=S.C; bpy=S.bpy
SLUG='calgary-sandstone-heritage';PARENT='calgary_sandstone_heritage';VARIANT='sandstone_romanesque_revival';INDEX=0
TITLE='Sandstone courtyard civic hall';WIDTH=57;DEPTH=59;HEIGHT=44;STOREYS=3
PALETTE=dict(wall=(.56,.405,.235),mortar=(.39,.30,.20),trim=(.67,.51,.31),coping=(.60,.46,.28),roof=(.22,.245,.235),foundation=(.48,.36,.23),glass=(.23,.29,.265),hardware=(.10,.085,.065),timber=(.25,.15,.075),interior=(.64,.57,.44),floor=(.38,.31,.22),copper=(.43,.275,.16),clock=(.76,.70,.56))

def manifest(v):
    m=S.prework(sys.modules[__name__],v,dict(width=WIDTH,depth=DEPTH,height=HEIGHT),
      dict(front='Sandstone Romanesque civic institution: three principal gabled facade pavilions, tall paired arches, recessed arched entrance and right-side clock tower.',
           oblique='Square open courtyard with four enclosed wings, steep grey slate roof ring, corner and central gables, copper conical tower roof and four pinnacles.',
           top='Open square courtyard inside a continuous roof ring; clock tower rises from centre of right wing, not courtyard.',
           roof='Closed mitred ring roof with real courtyard void; pavilion hips unioned into ring; tower cuts ring before insertion. Separate conical copper crown seats on octagonal belfry.',
           programme='Three occupied institutional storeys, enclosed wing rooms, courtyard, ground entries, clock chamber and open arched belfry.'),
      ['Conceptual 54 m square plan, 18 m courtyard, three storeys and 44 m tower inferred from source proportions; not a survey of a named historic property.',
       'Hidden rear continues the observed sandstone opening grammar; room subdivisions and clock mechanism inferred.',
       'Fine stone ornament simplified to constructed voussoirs, courses, buttresses, gable relief and finials; no perspective texture cards.',
       'Street, trees and surrounding buildings excluded. Grade is native zero; courtyard paving belongs to this building.'],
      ['Continuous masonry wing foundations meet grade.','Window and door arches are true carrier apertures with recessed optical or timber layers.',
       'Roof ring is a closed manifold solid with open courtyard; roof solids unioned at pavilion joints.',
       'Clock shaft passes through a full roof cut and supports the belfry, copper cone and pinnacles.'],[
        dict(name='facade_close',location=(36,-70,23),target=(0,-27,9),whole=False),
        dict(name='architecture_close',location=(7,-43,9),target=(0,-29,4.5),whole=False),
        dict(name='glass_close',location=(24,-42,14),target=(21,-27,9),whole=False,lens=60),
        dict(name='roof_contact',location=(57,-27,44),target=(26,0,24),whole=False),
        dict(name='courtyard_tower',location=(42,30,53),target=(4,1,20),whole=False)])
    for c in m['camera_roster']:
        if c['name'] in ('front_corner','aerial'):c['location']=(-c['location'][0],*c['location'][1:])
    return m

def arch_poly(u,z,w,h,n=16):
    r=w/2; spring=z+h-r
    return [(u-r,z),(u+r,z)]+[(u+r*math.cos(i*math.pi/n),spring+r*math.sin(i*math.pi/n)) for i in range(n+1)]

def arch(face,wall,ident,u,z,w,h,door=False,open_air=False):
    poly=arch_poly(u,z,w,h)
    cutter=face.panel(ident+' cutter',poly,-.4,.8,'wall','construction cutter')
    bpy.context.view_layer.objects.active=wall
    mod=wall.modifiers.new(ident+' aperture','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name);C.remove_cutter(cutter);C.normalise(wall.data)
    r=w/2; spring=z+h-r; modname=face.label+'.'+ident
    for side in (-1,1):
        face.part(ident+' stone jamb',u+side*(r+.13),-.055,(z+spring)/2,.26,.32,spring-z+.03,'trim',modname,0)
        face.part(ident+' recessed return',u+side*(r-.045),.20,(z+spring)/2,.09,.25,spring-z,'trim',modname,0)
    for i in range(14):
        a=i*math.pi/14+.014;b=(i+1)*math.pi/14-.014
        wedge=[(u+rr*math.cos(t),spring+rr*math.sin(t)) for rr,t in [(r,a),(r+.28,a),(r+.28,b),(r,b)]]
        face.panel(ident+' voussoir',wedge,-.20,.16,'trim',modname)
    if not open_air:
        face.panel(ident+' recessed optical layer',arch_poly(u,z+.035,w-.11,h-.065),.235,.245,'timber' if door else 'glass',modname)
        if door:
            face.part(ident+' double door stile',u,.18,z+h*.43,.075,.10,h*.86,'trim',modname,0)
            for dx in (-w*.26,w*.26):face.part(ident+' door raised panel',u+dx,.16,z+h*.38,w*.38,.08,h*.60,'timber',modname,0)
        else:
            face.part(ident+' central mullion',u,.17,z+h/2,.065,.10,h-.1,'hardware',modname,0)
            for frac in (.32,.66):face.part(ident+' transom',u,.17,z+h*frac,w-.08,.10,.065,'hardware',modname,0)
    C.OPENINGS.append(dict(id=ident,face=face.label,u=u,z=z,width=w,height=h,kind='arched entry' if door else 'arched belfry' if open_air else 'arched window',clear_wall_cut=True,carrier_depth_m=.38,frame_inset_m=.17,pane_inset_m=None if open_air else .24,face_origin=list(face.o),face_tangent=list(face.t),face_inward=list(face.n),occupied_space='enclosed wing room or open belfry; no painted wall'))

def facade(face,length,inner=False,us=None,pavilion=False,entry=None):
    top=18.5 if pavilion else 16
    wall=face.wall(face.label,0,length,.9,top,depth=.38)
    if us is None:us=[3+i*4.0 for i in range(13)] if not inner else [2.6,6.8,11.0,15.2]
    hs=[]
    for i,u in enumerate(us):
        if not inner and face.label=='right' and 22<u<32:continue # clock tower occupies these bays
        is_entry=(i==entry) if entry is not None else ((i==6 and not inner) or (inner and i==1))
        if is_entry:
            arch(face,wall,face.label+' entry',u,.9,2.5,3.5,door=True)
        else:
            h=dict(id=face.label+f' lower {i}',u=u,z=1.8,w=1.5,h=2.8)
            face.cut(wall,h['id'],u,h['z'],h['w'],h['h'],.38);face.window(h['id'],u,h['z'],h['w'],h['h'],2,2,depth=.38)
        arch(face,wall,face.label+f' principal {i}',u,6.0,1.65,5.0)
        upper_h=4.2 if pavilion else 2.2
        arch(face,wall,face.label+f' upper {i}',u,12.7,1.4,upper_h)
        hs.extend([dict(u=u,z=.9,w=2.6,h=4),dict(u=u,z=5.9,w=2,h=5.4),dict(u=u,z=12.6,w=1.8,h=upper_h+.4)])
    # Thin real course relief; clipped around the opening bounds, never across glazing.
    S.courses(face,length,.9,top-.05,hs,pitch=.48)
    vs=[];fs=[]
    for row in range(math.floor((top-.9)/.48)):
        z=.9+(row+.5)*.48
        for i in range(math.ceil(length/.90)):
            u=(i+.5*(row%2))*.90
            if not .02<u<length-.02 or any(h['u']-h['w']/2-.03<u<h['u']+h['w']/2+.03 and h['z']-.03<z<h['z']+h['h']+.03 for h in hs):continue
            n=len(vs)
            vs.extend(face.p(uu,dd,zz) for uu,dd,zz in [(u-.007,-.007,z-.22),(u+.007,-.007,z-.22),(u+.007,.001,z-.22),(u-.007,.001,z-.22),(u-.007,-.007,z+.22),(u+.007,-.007,z+.22),(u+.007,.001,z+.22),(u-.007,.001,z+.22)])
            fs.extend(tuple(n+j for j in f) for f in C.BOX_FACES)
    if vs:C.mesh('Staggered sandstone block joints',vs,fs,'mortar','stone bonding')
    for z in (5.3,11.8,top-.3):face.part('Continuous sandstone string course',length/2,-.08,z,length,.25,.21,'trim','stone cornice',0)
    return wall

def roof_ring():
    rings=[(27.65,16.10),(19.1,22.0),(8.65,16.10)]
    vs=[]
    for radius,z in rings:vs.extend([(-radius,-radius,z),(radius,-radius,z),(radius,radius,z),(-radius,radius,z)])
    for radius in (27.65,8.65):vs.extend([(-radius,-radius,15.85),(radius,-radius,15.85),(radius,radius,15.85),(-radius,radius,15.85)])
    fs=[]
    for i in range(4):
        j=(i+1)%4
        fs.extend([(i,j,4+j,4+i),(4+i,4+j,8+j,8+i),(i,12+i,12+j,j),(8+i,8+j,16+j,16+i),(12+i,16+i,16+j,12+j)])
    return C.mesh('Continuous mitred courtyard roof',vs,fs,'roof','roof ring')

def cone(name,x,y,z,r,h,role='copper',segments=40):
    vs=[(x+r*math.cos(i*2*math.pi/segments),y+r*math.sin(i*2*math.pi/segments),z) for i in range(segments)]+[(x,y,z+h)]
    return C.mesh(name,vs,[tuple(range(segments-1,-1,-1))]+[(i,(i+1)%segments,segments) for i in range(segments)],role,'tower crown')

def clock(face,u,z):
    r=1.58
    disk=[(u+r*math.cos(i*math.tau/48),z+r*math.sin(i*math.tau/48)) for i in range(48)]
    face.panel('Clock dial',disk,-.12,-.04,'clock','clock')
    for i in range(12):
        a=i*math.tau/12
        C.beam('Hour marker',face.p(u+1.26*math.sin(a),-.16,z+1.26*math.cos(a)),face.p(u+1.43*math.sin(a),-.16,z+1.43*math.cos(a)),.06,.055,'hardware','clock',0)
    for a,length in [(math.pi/3,.90),(math.pi*1.42,1.22)]:C.beam('Clock hand',face.p(u,-.19,z),face.p(u+length*math.sin(a),-.19,z+length*math.cos(a)),.07,.06,'hardware','clock',0)
    for i in range(48):
        a=i*math.tau/48;b=(i+1)*math.tau/48
        C.beam('Dial stone surround',face.p(u+1.71*math.cos(a),-.15,z+1.71*math.sin(a)),face.p(u+1.71*math.cos(b),-.15,z+1.71*math.sin(b)),.16,.18,'trim','clock',0)

def build():
    gable_caps=[]
    # Ring foundations and floors leave the actual courtyard empty.
    wings=[(0,-18,54,18),(0,18,54,18),(-18,0,18,18),(18,0,18,18)]
    for x,y,w,d in wings:
        C.box('Wing foundation',(x,y,.45),(w,d,.90),'foundation','ground contact',0)
        for z in (.9,5.5,11.6):S.room(x,y,z,w-.85,d-.85,4.10)
    C.box('Courtyard paving',(0,0,.06),(18,18,.12),'foundation','courtyard',0)
    for label,o,t,n in [('front',(-27,-27,0),(1,0,0),(0,1,0)),('right',(27,-27,0),(0,1,0),(-1,0,0)),('rear',(27,27,0),(-1,0,0),(0,-1,0)),('left',(-27,27,0),(0,-1,0),(1,0,0))]:
        f=C.Face(o,t,n,label)
        if label=='front':
            # Raised, projecting masonry pavilions own their openings and interrupt
            # the low wing eave. No duplicate wall remains behind their glazing.
            for start,end,raised in [(0,10,True),(10,22,False),(22,32,True),(32,44,False),(44,54,True)]:
                x=-27+start;length=end-start;y=-28.2 if raised else -27
                pf=C.Face((x,y,0),(1,0,0),(0,1,0),f'front section {start}')
                facade(pf,length,us=[2,5,8] if raised else [2,6,10],pavilion=raised,entry=1 if start==22 else -1)
                if raised:
                    C.box('Pavilion projecting foundation',(x+5,-27.55,.45),(10,1.3,.9),'foundation','pavilion',0)
                    for edge in (x+.19,x+9.81):C.box('Pavilion stone return',(edge,-27.45,9.7),(.38,1.5,17.6),'wall','pavilion',0)
                    for z in (.9,5.5,11.6,18.4):C.box('Pavilion floor continuation',(x+5,-27.5,z),(9.6,1.8,.15),'floor','pavilion',0)
                    for u in (.45,9.55):pf.part('Pavilion edge pilaster',u,-.16,9.7,.5,.44,17.6,'wall','pavilion',0)
        else:facade(f,54)
        # Buttresses and facade gables: geometry owns relief and silhouette.
        if label!='front':
            for u in (.35,9,21,33,45,53.65):f.part('Masonry buttress',u,-.22,8.55,.58,.63,15.3,'wall','buttresses',0)
        for u in (5.5,27,48.5):
            if label=='right' and u==27:continue
            raised=label=='front';lift=2.8 if raised else 0
            gf=f
            if raised:
                u={5.5:5,27:27,48.5:49}[u]
                gf=C.Face((-27,-28.2,0),(1,0,0),(0,1,0),'front pavilion gable')
                # Close both triangular cheeks below the raised cap. The roof
                # aperture must never leave daylight beside a masonry pavilion.
                for side in (-1,1):
                    x0=-27+u+side*4.8;x1=-27+u+side*4.5
                    C.mesh('Solid pavilion roof cheek',[(x+dx,y,z) for dx in (-.16,.16) for x,y,z in [(x0,-28.04,15.7),(x1,-16.2,15.7),(x1,-16.2,16.08),(x0,-28.04,18.82)]],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'wall','pavilion roof cheeks')
            gf.panel('Fronted sandstone gable',[(u-4.6,15.7+lift),(u+4.6,15.7+lift),(u,21.8+lift)],-.18,.4,'wall','gable')
            for a,b in [((u-4.72,15.8+lift),(u,22+lift)),((u,22+lift),(u+4.72,15.8+lift))]:C.beam('Gable coping',gf.p(a[0],-.22,a[1]),gf.p(b[0],-.22,b[1]),.29,.29,'trim','gable',0)
            # Front cap sits behind the stone gable. Rear ridge sinks into the
            # main hip, avoiding exposed vertical ends above the roof carrier.
            gable_caps.append(C.mesh('Gable weathering cap',[gf.p(u-4.9,.16,15.9+lift),gf.p(u+4.9,.16,15.9+lift),gf.p(u,.16,22.12+lift),gf.p(u-4.6,12 if raised else 10,15.9),gf.p(u+4.6,12 if raised else 10,15.9),gf.p(u,12 if raised else 10,21.7 if raised else 20.0)],[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],'roof','gable roof'))
            # Inset decorative gable slots, intentionally blind stone ornament.
            for dx in (-1.45,0,1.45):gf.part('Gable blind lancet',u+dx,-.205,17.65+lift,.6,.04,1.35,'mortar','gable relief',0)
            p=gf.p(u,0,22.02+lift);cone('Gable pinnacle',p[0],p[1],p[2],.22,1.2,'trim',12)
    for label,o,t,n in [('court north',(-9,9,0),(1,0,0),(0,1,0)),('court east',(9,9,0),(0,-1,0),(1,0,0)),('court south',(9,-9,0),(-1,0,0),(0,-1,0)),('court west',(-9,-9,0),(0,1,0),(-1,0,0))]:facade(C.Face(o,t,n,label),18,True)
    roof=roof_ring()
    for x in (-21.5,21.5):
        for y in (-21.5,21.5):S.union(roof,S.hip('Corner pavilion hip',x-6,x+6,y-6,y+6,16.1,6.2))
    for y in (-21,21):S.union(roof,S.hip('Central entrance hip',-5.1,5.1,y-6.6,y+6.6,16.1,6.3))
    for x in (-21,21):S.union(roof,S.hip('Side pavilion hip',x-6.6,x+6.6,-5.1,5.1,16.1,6.3))
    for x in (-22,0,22):C.cut_box(roof,'Raised pavilion eave opening',(x,-26.1,19),(9.65,5.0,8))
    for cap in gable_caps:S.union(roof,cap)
    # Deep entrance porch with an actual arched portal and unobstructed stairs.
    porch=C.Face((-4.1,-30.0,0),(1,0,0),(0,1,0),'entrance porch')
    pw=porch.wall('Portal',0,8.2,.9,5.7,depth=.6)
    arch(porch,pw,'grand entrance passage',4.1,.9,3.8,4.25,open_air=True)
    for x in (-3.8,3.8):C.box('Portal return',(x,-28.65,3.3),(.6,2.7,4.8),'wall','entrance porch',0)
    C.box('Portal roof',(0,-28.6,5.75),(8.7,3.5,.35),'trim','entrance porch',0)
    C.box('Portal floor',(0,-28.5,.45),(8.2,3.0,.9),'foundation','entrance porch',0)
    S.stairs(0,-30.1,.9,width=4,count=5)
    S.stairs(0,27,.9,width=2.6,count=5,direction=1)
    for label,o,t,n in [('court north',(-9,9,0),(1,0,0),(0,1,0)),('court east',(9,9,0),(0,-1,0),(1,0,0)),('court south',(9,-9,0),(-1,0,0),(0,-1,0)),('court west',(-9,-9,0),(0,1,0),(-1,0,0)),('left',(-27,27,0),(0,-1,0),(1,0,0))]:
        sf=C.Face(o,t,n,label);u=27 if label=='left' else 6.8
        for i in range(5):sf.part('Entry stair',u,-(i+.5)*.29,.9*(5-i)/10,2.6,.30,.9*(5-i)/5,'foundation','entrance stairs',0)
    # Clock tower on the right street wing. It never occupies the courtyard.
    C.cut_box(roof,'Full tower roof aperture',(25.5,0,21),(7.6,7.6,13))
    for label,o,t,n in [('tower front',(21.5,-4,0),(1,0,0),(0,1,0)),('tower right',(29.5,-4,0),(0,1,0),(-1,0,0)),('tower rear',(29.5,4,0),(-1,0,0),(0,-1,0)),('tower left',(21.5,4,0),(0,-1,0),(1,0,0))]:
        f=C.Face(o,t,n,label);wall=f.wall(label,0,8,.9,35.1,depth=.38)
        for u in (1.9,4,6.1):
            for z,h in [(2.0,3.0),(7.0,4.5),(13.0,2.5)]:
                if label=='tower right' and z==2.0:continue
                arch(f,wall,label+' lower '+str(u)+' '+str(z),u,z,1.1,h)
        if label=='tower right':
            arch(f,wall,'tower side entrance',4,.9,3.2,4.6,door=True)
            for i in range(5):f.part('Tower entry stair',4,-(i+.5)*.29,.9*(5-i)/10,3.6,.30,.9*(5-i)/5,'foundation','entrance stairs',0)
        for u in (1.9,4,6.1):arch(f,wall,label+' shaft '+str(u),u,21.5,1.1,5.1)
        for u in (1.2,2.6,4,5.4,6.8):arch(f,wall,label+' belfry '+str(u),u,32.1,.76,2.1,open_air=True)
        clock(f,4,29.3)
        for z in (16,20.8,27.2,31.3,35):f.part('Tower string course',4,-.1,z,8.35,.3,.25,'trim','tower cornice',0)
        for u in (.35,7.65):f.part('Tower corner pier',u,-.13,18,.50,.35,34.2,'wall','tower pier',0)
    C.box('Tower foundation',(25.5,0,.45),(8,8,.9),'foundation','tower base',0)
    for z in (.9,5.5,11.6,20.2,27.3,31.6):C.box('Tower interior floor',(25.5,0,z),(7.2,7.2,.16),'floor','tower floors',0)
    cone('Copper spire',25.5,0,35.1,4.6,8.3)
    C.rod('Spire finial',(25.5,0,43.25),(25.5,0,44),.08,'trim','tower crown')
    for x in (21.5,29.5):
        for y in (-4,4):
            C.rod('Pinnacle shaft',(x,y,30.8),(x,y,35.5),.40,'wall','tower pinnacles',16)
            cone('Pinnacle cap',x,y,35.5,.58,2.3,'trim',16)
    # Bounded source-specific copper seams follow the actual conical carrier.
    for i in range(24):
        a=i*math.tau/24
        C.beam('Spire standing seam',(25.5+4.60*math.cos(a),4.60*math.sin(a),35.12),(25.5+.055*math.cos(a),.055*math.sin(a),43.31),.045,.045,'trim','tower crown',0)

if __name__=='__main__':S.run(sys.modules[__name__])
