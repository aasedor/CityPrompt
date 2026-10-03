"""Two exact-reference interior pilots; immutable offline RLASM clay packages."""
import argparse, hashlib, importlib.util, json, math, shutil, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE.parent/'catalogue_duplex_pilot'))
import clay_core as C
spec=importlib.util.spec_from_file_location('interior_navigation',HERE.parent/'station_interior/build.py')
S=importlib.util.module_from_spec(spec);spec.loader.exec_module(S);B=S.B
box=S.box;floor=S.floor;obstacle=S.obstacle;beam=S.beam
G=.12;H=3.6
SPECS={
 'school':dict(archetype='university_academic_complex',variant='biophilic_mass_timber_campus',directory='university-academic-complex',index=2,title='Timber Art & Design School',width=36,depth=30,height=17,floors=4,group='civic'),
 'hotel':dict(archetype='boutique_hotel',variant='mediterranean_resort_courtyard',directory='boutique-hotel',index=1,title='Mediterranean Courtyard Hotel',width=40,depth=36,height=14,floors=3,group='hotels'),
}
PALETTE=dict(S.PALETTE,wall=(.72,.68,.57),stone=(.50,.44,.34),timber=(.48,.29,.13),trim=(.14,.12,.085),
 floor=(.57,.51,.39),walk_floor=(.57,.51,.39),roof=(.40,.17,.085),blackwood=(.055,.065,.065),
 leaf=(.19,.29,.075),leaf_light=(.29,.37,.09),flower=(.42,.06,.22),canvas=(.81,.77,.65),
 pigment_blue=(.06,.20,.30),pigment_red=(.43,.10,.055),pigment_gold=(.67,.42,.07),water=(.025,.38,.37))

def solid(name,p,size,role='timber',module='furniture'):
    o=box(name,p,size,role,module);x,y,z=p;w,d,h=size
    obstacle(x-w/2,x+w/2,y-d/2,y+d/2,z-h/2,z+h/2);return o

def ellipsoid(name,p,r,role='leaf'):
    vs=[];fs=[];n=10;m=6
    for j in range(m+1):
        t=math.pi*j/m
        for i in range(n):
            a=i*math.tau/n;vs.append((p[0]+r[0]*math.sin(t)*math.cos(a),p[1]+r[1]*math.sin(t)*math.sin(a),p[2]+r[2]*math.cos(t)))
    for j in range(m):
        for i in range(n):a=j*n+i;b=j*n+(i+1)%n;fs.append((a,b,b+n,a+n))
    o=C.mesh(name,vs,fs,role,'planting')
    for f in o.data.polygons:f.use_smooth=True
    return o

def plant(x,y,z=G,scale=1,flower=False,pot=True):
    if pot:
        C.rod('terracotta planter',(x,y,z),(x,y,z+.48*scale),.32*scale,'roof','planting',16)
        obstacle(x-.37*scale,x+.37*scale,y-.37*scale,y+.37*scale,z,z+1.3*scale)
    for i in range(32):
        a=i*2.4;r=(.18+.29*(.5+.5*math.sin(i*3.7)))*scale
        dx=math.cos(a)*r;dy=math.sin(a)*r;zz=z+(.61+.46*(.5+.5*math.cos(i*1.3)))*scale
        beam('branching plant stem',(x,y,z+.45*scale),(x+dx,y+dy,zz),.014*scale,.014*scale,'leaf')
        ellipsoid('layered foliage',(x+dx,y+dy,zz),(.18*scale,.15*scale,.095*scale),'leaf_light' if i%4==0 else 'leaf')
    if flower:
        for i in range(18):
            a=i*2.4
            for j in range(3):
                ellipsoid('bougainvillea flower cluster',(x+(math.cos(a)*.42+.045*math.cos(j*2.1))*scale,y+(math.sin(a)*.42+.045*math.sin(j*2.1))*scale,z+(.66+(i%4)*.11+.035*j)*scale),(.075*scale,.07*scale,.055*scale),'flower')

def greenbed(x0,x1,y0,y1,z,density=.7):
    solid('contained roof planting',( (x0+x1)/2,(y0+y1)/2,z+.13),(x1-x0,y1-y0,.26),'soil','planting')
    density=min(density,.68)
    for i in range(max(1,int((x1-x0)/density))):
        for j in range(max(1,int((y1-y0)/density))):
            x=x0+(i+.5)*(x1-x0)/max(1,int((x1-x0)/density));y=y0+(j+.5)*(y1-y0)/max(1,int((y1-y0)/density))
            phase=i*17.13+j*31.79;x+=.14*math.sin(phase);y+=.13*math.cos(phase*1.7)
            r=.29+.09*(.5+.5*math.sin(phase*.77));hh=.12+.13*(.5+.5*math.cos(phase))
            ellipsoid('irregular sedum clump',(x,y,z+.24+hh*.4),(r,r*.88,hh),'leaf_light' if (i+j)%4==0 else 'leaf')
            if (i+j)%3==0:
                for k in range(4):
                    a=k*2.4+phase;beam('roof meadow blade',(x,y,z+.23),(x+.11*math.cos(a),y+.11*math.sin(a),z+.55+.10*math.sin(a)),.018,.026,'leaf_light')

def rail(name,a,b,z):
    S.rail(name,a,b,z)

def wall(face,length,z0,z1,holes=(),role='wall',depth=.30):
    """Partition geometry and collision together; open doors have no glass leaf."""
    us=sorted({0,length,*[v for h in holes for v in (h['u']-h['w']/2,h['u']+h['w']/2)]})
    zs=sorted({z0,z1,*[v for h in holes for v in (h['z'],h['z']+h['h'])]})
    for u,v in zip(us,us[1:]):
        for z,t in zip(zs,zs[1:]):
            if any(abs((u+v)/2-h['u'])<h['w']/2 and h['z']<(z+t)/2<h['z']+h['h'] for h in holes):continue
            o=face.part('partitioned carrier',(u+v)/2,depth/2,(z+t)/2,v-u,depth,t-z,role,'envelope',0);o['rlasm_wall_carrier']=True
            pts=[face.p(a,b,0) for a in (u,v) for b in (0,depth)]
            obstacle(min(p[0] for p in pts),max(p[0] for p in pts),min(p[1] for p in pts),max(p[1] for p in pts),z,t)
    for h in holes:
        u,z,w,hh=h['u'],h['z'],h['w'],h['h']
        if h.get('door'):
            for s in (-1,1):face.part('open portal jamb',u+s*(w/2-.04),.14,z+hh/2,.08,.15,hh,'timber','openings',0)
            face.part('open portal head',u,.14,z+hh-.04,w,.15,.08,'timber','openings',0)
            C.OPENINGS.append(dict(id=h['id'],face=face.label,u=u,z=z,width=w,height=hh,kind='open passage',clear_wall_cut=True,carrier_depth_m=depth,frame_inset_m=.14,pane_inset_m=None,face_origin=list(face.o),face_tangent=list(face.t),face_inward=list(face.n),occupied_space='authored connected room',cols=1,rows=1))
        else:
            face.window(h['id'],u,z,w,hh,cols=h.get('cols',2),rows=h.get('rows',1),frame=h.get('frame','timber'),depth=depth)
            pts=[face.p(a,b,0) for a in (u-w/2,u+w/2) for b in (0,depth)]
            obstacle(min(p[0] for p in pts),max(p[0] for p in pts),min(p[1] for p in pts),max(p[1] for p in pts),z,z+hh)

def hole(u,z,w,h,door=False,cols=2):return dict(id='portal' if door else 'occupied window',u=u,z=z,w=w,h=h,door=door,cols=cols)

def stair_core(x,y,levels):
    """Stacked dogleg flights: 22 risers per storey, open level landings."""
    rise=H/22;run=3.52
    for level in range(levels):
        z=G+level*H
        for lane,direction,base in [(0,1,z),(2.8,-1,z+H/2)]:
            xx=x+lane
            for i in range(11):
                ya=y+i*.32 if direction==1 else y+run-(i+1)*.32
                zz=base+(i+1)*rise
                floor('stair tread',xx-1.1,xx+1.1,ya,ya+.32,zz,.12)
                box('closed stair riser',(xx,ya if direction==1 else ya+.32,zz-rise/2),(2.2,.055,rise+.015),'stone','stairs')
            for side in (-1,1):
                a=(xx+side*1.14,y if direction==1 else y+run,base)
                b=(a[0],y+run if direction==1 else y,base+H/2)
                beam('bearing stair stringer',a,b,.12,.25,'timber')
                beam('continuous handrail',(a[0],a[1],a[2]+1.05),(b[0],b[1],b[2]+1.05),.065,.065,'brass')
                for i in range(12):
                    yy=a[1]+(b[1]-a[1])*i/11;zz=base+H/2*i/11
                    beam('stair baluster',(a[0],yy,zz),(a[0],yy,zz+1.05),.035,.035,'trim')
                obstacle(a[0]-.05,a[0]+.05,y,y+run,base,base+H/2+1.1)
        floor('half landing',x-1.25,x+4.05,y+run,y+5.2,z+H/2,.22)
        for xx in (x-1.25,x+4.05):rail('landing side guard',(xx,y+run),(xx,y+5.2),z+H/2)
        rail('landing back guard',(x-1.25,y+5.2),(x+4.05,y+5.2),z+H/2)
        for xx in (x-1.1,x+3.9):solid('landing bearing post',(xx,y+4.85,z+H/4),(.16,.16,H/2),'timber','structure')
        # The level floor surrounds the well; guards retain its unoccupied sides.
        upper=z+H
        for xx in (x-1.4,x+4.2):rail('stair well guard',(xx,y),(xx,y+5.5),upper)
        rail('stair well rear guard',(x-1.4,y+5.5),(x+4.2,y+5.5),upper)
        rail('stair well front guard',((x-1.4 if level==levels-1 else x+1.2),y),(x+1.6,y),upper)

def stair_route(x,y,levels):
    result=[]
    for l in range(levels):
        z=G+l*H
        result += [[x,y-1,z],[x,y,z],[x,y+3.6,z+H/2],[x,y+4.3,z+H/2],[x+2.8,y+4.3,z+H/2],[x+2.8,y+3.52,z+H/2],[x+2.8,y-.1,z+H],[x+2.8,y-1,z+H]]
        if l<levels-1:result += [[x,y-1,z+H]]
    return result

def worktable(x,y,z,w=2.4,d=1.2):
    box('solid worktop',(x,y,z+.90),(w,d,.10),'timber','studio')
    for dx in (-w/2+.12,w/2-.12):
        for dy in (-d/2+.12,d/2-.12):box('trestle leg',(x+dx,y+dy,z+.44),(.09,.09,.88),'trim','studio')
    beam('trestle lower brace',(x-w/2+.12,y,z+.25),(x+w/2-.12,y,z+.25),.08,.08,'timber')
    obstacle(x-w/2,x+w/2,y-d/2,y+d/2,z,z+1.5)

def artwork(x,y,z,w=1.2,h=.9,facing=-1):
    box('gallery frame',(x,y,z),(w+.12,.09,h+.12),'timber','artwork')
    box('canvas',(x,y+facing*.055,z),(w,.026,h),'canvas','artwork')
    for i,(dx,dz,role) in enumerate([(-.24,.1,'pigment_blue'),(.2,-.13,'pigment_red'),(.05,.22,'pigment_gold')]):
        phase=x*.8+y*.7+i
        box('abstract painted relief',(x+(dx+.09*math.sin(phase))*w,y+facing*(.075+i*.002),z+(dz+.09*math.cos(phase))*h),(w*(.22+.08*math.sin(phase)**2),.01,h*(.19+.16*math.cos(phase)**2)),role,'artwork')

def easel(x,y,z):
    for s in (-1,1):beam('easel front leg',(x+s*.38,y-.15,z),(x+s*.20,y+.12,z+1.75),.055,.06,'timber')
    beam('easel rear leg',(x,y+.6,z),(x,y+.12,z+1.62),.06,.06,'timber')
    box('easel shelf',(x,y-.09,z+.73),(.95,.16,.06),'timber','studio');artwork(x,y,z+1.23,.75,.85)
    obstacle(x-.52,x+.52,y-.22,y+.68,z,z+1.8)

def pottery(x,y,z):
    C.rod('ceramic vase foot',(x,y,z),(x,y,z+.08),.10,'roof','ceramics',16)
    ellipsoid('hand thrown ceramic body',(x,y,z+.25),(.20,.20,.24),'roof')
    C.rod('ceramic neck',(x,y,z+.39),(x,y,z+.51),.09,'roof','ceramics',20)

def sofa(x,y,z):
    solid('upholstered sofa base',(x,y,z+.30),(2,.85,.50),'interior')
    box('sofa back',(x,y+.37,z+.75),(2,.18,.75),'interior','furniture')
    for dx in (-.91,.91):box('sofa arm',(x+dx,y,z+.57),(.18,.86,.52),'interior','furniture')
    for dx in (-.48,.48):box('seat cushion',(x+dx,y-.02,z+.58),(.86,.65,.16),'canvas','furniture')

def school():
    sx,sy=8.2,2
    well=(sx-1.4,sx+4.2,sy,sy+5.5)
    box('native foundation',(0,0,.04),(36,30,.08),'foundation','foundation')
    floor('entry apron',-17.5,17.5,-15,-12.7,G)
    for l in range(3):S.floor_with_holes('occupied studio floor',-15.7,15.7,-12.7,12.7,G+l*H,[well])
    # Level four combines an enclosed setback pavilion with a broad front terrace.
    S.floor_with_holes('roof pavilion floor',-15.7,15.7,-12.7,12.7,G+3*H,[well])
    stair_core(sx,sy,3)
    for y in (-8,1,10):
        for x in (-11,-3,5):solid('glulam column',(x,y,5.4),(.22,.22,10.8),'timber','structure')
    for z in (3.52,7.12,10.72):
        for y in (-8,1,10):box('glulam floor beam',(0,y,z),(31.4,.24,.34),'timber','structure')
    # Ground glazing and open central entrance.
    for face,length in zip(B.faces(32,26),(32,26,32,26)):
        centers=[(i+.5)*length/10 for i in range(10)]
        hs=[hole(u,G,length/10-.14,3.18,cols=1) for i,u in enumerate(centers) if not (face.label=='front' and i in (4,5))]
        if face.label=='front':hs.append(hole(length/2,G,4,3.18,door=True))
        wall(face,length,G,3.6,hs,'timber',.24)
    # Front and rear have two-storey bays; side walls own a distinct dark slat language.
    for face in (B.faces(32,26)[0],B.faces(32,26)[2]):
        hs=[hole(2+i*4,3.9,2.9,6.45,cols=2) for i in range(8) if i not in (1,3,5)]
        wall(face,32,3.6,10.8,hs,'timber',.32)
        for i in (1,3,5):
            face.part('continuous living wall substrate',2+i*4,-.075,7.18,2.4,.14,6.45,'leaf','planting',0)
            for j in range(19):
                for k in range(6):
                    phase=i*13.7+j*7.31+k*29.11
                    u=2+i*4+(k-2.5)*.38+.09*math.sin(phase)
                    xx,yy,zz=face.p(u,-.16-.04*math.sin(phase),4+j*.34+.10*math.cos(phase))
                    ellipsoid('overlapping living wall foliage',(xx,yy,zz),(.27+.09*math.sin(phase)**2,.16+.06*math.cos(phase)**2,.24+.13*math.cos(phase*.8)**2),'leaf_light' if (j+k)%5==0 else 'leaf')
        face.part('deep timber sill band',16,-.04,3.6,32,.56,.28,'timber','structure',0)
        face.part('timber roof fascia',16,-.07,10.85,32.5,.54,.30,'timber','roof',0)
    for face in (B.faces(32,26)[1],B.faces(32,26)[3]):
        hs=[hole(2.2+i*4.3,3.92,.63,6.40,cols=1) for i in range(6)]
        wall(face,26,3.6,10.8,hs,'blackwood',.32)
        for i in range(131):
            u=i*.2
            if any(abs(u-h['u'])<h['w']/2+.05 for h in hs):continue
            face.part('charred timber vertical batten',u,-.045,7.2,.075,.10,7.2,'blackwood','cladding',0)
    # Upper pavilion offset to rear, front terrace and a second extensive planted roof.
    pf=[C.Face((-15.7,-4,0),(1,0,0),(0,1,0),'pavilion front'),C.Face((15.7,-4,0),(0,1,0),(-1,0,0),'pavilion right'),C.Face((15.7,12.7,0),(-1,0,0),(0,-1,0),'pavilion rear'),C.Face((-15.7,12.7,0),(0,-1,0),(1,0,0),'pavilion left')]
    for face,length in zip(pf,(31.4,16.7,31.4,16.7)):
        count=8 if length>20 else 4;step=length/count
        hs=[hole((i+.5)*step,10.92,step-.28,3.1,cols=2) for i in range(count) if not (face.label=='pavilion front' and i in (3,4))]
        if face.label=='pavilion front':hs.append(hole(length/2,10.92,4,3.1,door=True))
        wall(face,length,10.92,14.4,hs,'timber')
    box('pavilion sealed roof',(0,4.35,14.5),(32.3,17.6,.30),'timber','roof')
    greenbed(-15.6,15.6,-3.65,12.3,14.65,.95)
    greenbed(-15.6,15.6,-12.65,-8.7,10.92,.75)
    rail('terrace edge guard',(-15.7,-12.8),(15.7,-12.8),10.92)
    for x in (-15.7,15.7):rail('terrace return guard',(x,-12.8),(x,-4),10.92)
    for x in (-8,8):
        box('timber ventilation shaft',(x,-1.5,15.25),(1.25,1.3,1.65),'timber','roof plant')
        for z in (15.95,16.06,16.17,16.28):box('ventilation louvre cap',(x,-1.5,z),(1.4,1.45,.06),'trim','roof plant')
    # Ground: exhibition gallery, reception, sculpture and material library.
    solid('reception desk',(-6,-9,G+.55),(3.2,1,.95),'timber');box('reception work surface',(-6,-9,G+1.06),(3.35,1.1,.09),'stone','furniture')
    for x,y in [(-11,-3),(-6,4),(2,7)]:
        solid('sculpture plinth',(x,y,G+.45),(1,1,.9),'stone');ellipsoid('student sculpture',(x,y,G+1.35),(.35,.25,.75),'pigment_blue')
    for x in (-11,-6,0):
        artwork(x,11.95,1.85,2.5,1.5)
        for dx in (-.95,.95):
            solid('gallery display support',(x+dx,11.99,G+1.28),(.07,.08,2.56),'trim')
            solid('display stabilizing foot',(x+dx,11.99,G+.04),(.30,.60,.08),'trim')
    for x in (-11,-5):S.bench(x,-6,G,length=2.3)
    # First upper floor: six easels and stocked painting tables.
    for y in (-7,-2,5):
        for x in (-11,-5):
            easel(x,y,G+H);worktable(x,y+1.5,G+H,1.8,.75)
            for dx,role in [(-.5,'pigment_blue'),(0,'pigment_red'),(.5,'pigment_gold')]:C.rod('paint jar',(x+dx,y+1.5,G+H+.96),(x+dx,y+1.5,G+H+1.14),.09,role,'studio',12)
            for k in range(5):beam('studio brush',(x+.5,y+1.5,G+H+1.09),(x+.5+(k-2)*.026,y+1.5+.025*math.sin(k),G+H+1.38+.03*(k%2)),.012,.012,'timber')
    # Second upper floor: pottery wheels, kiln, sculpture and print bench.
    for x in (-11,-6):
        for y in (-6,0):
            solid('pottery wheel cabinet',(x,y,G+2*H+.35),(1.05,.8,.7),'stone')
            C.rod('throwing wheel',(x,y,G+2*H+.72),(x,y,G+2*H+.78),.44,'hardware','ceramics',32);pottery(x,y,G+2*H+.79)
            B.chair(x,y-1.1,G+2*H);obstacle(x-.35,x+.35,y-1.45,y-.75,G+2*H,G+2*H+1)
    solid('ceramics kiln',(-12,9,G+2*H+.65),(1.8,1.6,1.3),'stone')
    for z in (.35,.75,1.1):box('kiln vent band',(-12,8.18,G+2*H+z),(1.4,.04,.035),'hardware','ceramics')
    worktable(-5,8,G+2*H,3.2,1.3)
    for x in (-6,-5,-4):pottery(x,8,G+2*H+.96)
    worktable(2,-6,G+2*H,3,1.4)
    for y in (-6.4,-5.9,-5.4):box('print drying paper',(2,y,G+2*H+1.0),(1.4,.35,.02),'canvas','printing')
    # Roof pavilion: critique tables and library lounge, with real timber decking.
    for x in (-9,-3):
        B.table(x,5,G+3*H);obstacle(x-.85,x+.85,3.95,6.05,G+3*H,G+3*H+1.1)
    sofa(-9,10,G+3*H);sofa(-3,10,G+3*H)
    for x in (-8,8):S.bench(x,-6.5,G+3*H,2.5)
    for i in range(160):box('terrace decking joint',(-15.5+i*.195,-7.2,10.928),(.009,5.1,.008),'timber','decking')
    B.label('ART  &  DESIGN',(0,-13.07,3.25),.28,'brass')
    return [dict(name='all studio levels and roof terrace',points=[[0,-14,G],[0,-11,G],[4,-1,G],[sx,sy-1,G]]+stair_route(sx,sy,3)+[[0,1,10.92],[0,-5,10.92],[0,-8,10.92],[-12,-8,10.92]]),dict(name='ground exhibition gallery',points=[[0,-14,G],[0,-9,G],[0,-4,G],[-1,-4,G],[-1,8,G],[-10,8,G]])]

def hotel_roof():
    bounds=(-16.5,14.5,-15.5,15.5)
    holes=[(-3,4,-2,11),(-15,-10,-14,-10),(8,13.5,-14,-9.5),(-15,-11,9,14)]
    # A continuous closed underside ties offset room heads to aperture reveals.
    # Keep the same four holes open; this ceiling is not a walking surface.
    cx=sorted({bounds[0],bounds[1],*[v for h in holes for v in h[:2]]})
    cy=sorted({bounds[2],bounds[3],*[v for h in holes for v in h[2:]]})
    for a,b in zip(cx,cx[1:]):
        for c,d in zip(cy,cy[1:]):
            if any(l<(a+b)/2<r and lo<(c+d)/2<hi for l,r,lo,hi in holes):continue
            box('closed roof underside',((a+b)/2,(c+d)/2,10.65),(b-a,d-c,.14),'wall','roof contact')
    # Front room wall heads sit inside the two corner cuts, so return them
    # horizontally to the reveal. The rest of each terrace remains open.
    for x0,x1,rear in [(-15,-10,-10),(8,13.5,-9.5)]:
        front=-10.56;back=rear+.08
        box('corner partition head return',((x0+x1)/2,(front+back)/2,10.77),(x1-x0+.08,back-front,.18),'wall','roof contact')
    height=lambda x,y:10.85+.45*min(x+16.5,14.5-x,y+15.5,15.5-y,6)
    xs=sorted({-16.5,14.5,*[round(-16.5+i*.4,6) for i in range(78) if -16.5+i*.4<14.5],*[x for h in holes for x in h[:2]]})
    ys=sorted({-15.5,15.5,*[round(-15.5+i*.4,6) for i in range(78) if -15.5+i*.4<15.5],*[y for h in holes for y in h[2:]]})
    vs=[];fs=[]
    for a,b in zip(xs,xs[1:]):
        for c,d in zip(ys,ys[1:]):
            if any(l<(a+b)/2<r and lo<(c+d)/2<hi for l,r,lo,hi in holes):continue
            # Each physical tile has a rounded pan, overlap lip and closed backing.
            side=min((a+b)/2+16.5,14.5-(a+b)/2)<min((c+d)/2+15.5,15.5-(c+d)/2)
            for k in range(3):
                xa,xb=(a,b) if side else (a+(b-a)*k/3,a+(b-a)*(k+1)/3)
                ya,yb=(c+(d-c)*k/3,c+(d-c)*(k+1)/3) if side else (c,d)
                za=.045*math.sin(k*math.pi/3);zb=.045*math.sin((k+1)*math.pi/3)
                poly=[(xa,ya,height(xa,ya)+za),(xb,ya,height(xb,ya)+(za if side else zb)),(xb,yb,height(xb,yb)+zb),(xa,yb,height(xa,yb)+(zb if side else za))]
                n=len(vs);vs.extend(poly+[(x,y,z-.18) for x,y,z in poly]);fs.extend(tuple(n+i for i in p) for p in C.BOX_FACES)
    C.mesh('joined terracotta hip roof with actual court cuts',vs,fs,'roof','roof')
    for x0,x1,y0,y1 in [bounds,*holes]:
        for a,b in [((x0,y0),(x1,y0)),((x1,y0),(x1,y1)),((x1,y1),(x0,y1)),((x0,y1),(x0,y0))]:
            count=max(1,math.ceil(math.dist(a,b)/.35))
            pts=[(a[0]+(b[0]-a[0])*i/count,a[1]+(b[1]-a[1])*i/count) for i in range(count+1)]
            for p,q in zip(pts,pts[1:]):beam('bounded roof edge flashing',(p[0],p[1],height(*p)-.06),(q[0],q[1],height(*q)-.06),.10,.18,'roof')
    # Shaped reveals close every sloping roof cut back to the upper room walls.
    for x0,x1,y0,y1 in holes:
        for a,b in [((x0,y0),(x1,y0)),((x1,y0),(x1,y1)),((x1,y1),(x0,y1)),((x0,y1),(x0,y0))]:
            length=math.dist(a,b);nx=-(b[1]-a[1])/length*.16;ny=(b[0]-a[0])/length*.16
            count=max(1,math.ceil(length/.35))
            for i in range(count):
                p=(a[0]+(b[0]-a[0])*i/count,a[1]+(b[1]-a[1])*i/count)
                q=(a[0]+(b[0]-a[0])*(i+1)/count,a[1]+(b[1]-a[1])*(i+1)/count)
                vs=[(p[0],p[1],10.72),(q[0],q[1],10.72),(q[0],q[1],height(*q)-.10),(p[0],p[1],height(*p)-.10)]
                vs += [(x+nx,y+ny,z) for x,y,z in vs]
                C.mesh('closed roof terrace cheek',vs,C.BOX_FACES,'wall','roof contact')

def bed(x,y,z):
    solid('guest bed base',(x,y,z+.25),(2.05,2.25,.5),'timber')
    box('mattress',(x,y,z+.59),(2,2.15,.24),'canvas','guest room')
    box('woven bed runner',(x,y+.65,z+.72),(2.02,.56,.035),'pigment_blue','guest room')
    box('bed headboard',(x,y-1.13,z+.77),(2.18,.12,1.35),'timber','guest room')
    for dx in (-.48,.48):box('guest pillow',(x+dx,y-.72,z+.77),(.76,.4,.16),'white','guest room')
    for dx in (-1.48,1.48):
        solid('bedside cabinet',(x+dx,y-.75,z+.3),(.55,.55,.6),'timber')
        C.rod('bedside lamp stem',(x+dx,y-.75,z+.62),(x+dx,y-.75,z+.97),.035,'brass','guest room',12)
        C.rod('linen lamp shade',(x+dx,y-.75,z+.95),(x+dx,y-.75,z+1.23),.18,'canvas','guest room',20)

def hotel():
    sx,sy=-13,3;well=(sx-1.4,sx+4.2,sy,sy+5.5);court=(-3,4,-2,10)
    box('native hotel foundation',(0,0,.04),(40,36,.08),'foundation','foundation')
    floor('front hotel apron',-19.5,19.5,-18,-14.7,G)
    floor('pool access promenade',14,15.25,-14.7,15.5,G)
    floor('rear garden path',-16,15.25,15,17.5,G)
    for l in range(3):S.floor_with_holes('hotel occupied floor',-15.7,13.7,-14.7,14.7,G+l*H,[well]+([court] if l else []))
    stair_core(sx,sy,2)
    # Complete occupied perimeter; source front is west of the long pool.
    faces=[C.Face((-16,-15,0),(1,0,0),(0,1,0),'hotel front'),C.Face((14,-15,0),(0,1,0),(-1,0,0),'pool side'),C.Face((14,15,0),(-1,0,0),(0,-1,0),'hotel rear'),C.Face((-16,15,0),(0,-1,0),(1,0,0),'hotel left')]
    for face in faces:
        if face.label=='hotel front':hs=[hole(u,G+.8,2.2,2.2) for u in (3,7,11)]+[hole(16,G,3.4,3.1,True),hole(25,G,9,3.1,True)]
        elif face.label=='pool side':hs=[hole(3,G,5,3.1,True)]+[hole(u,G+.8,2.1,2.2) for u in (9,15,21,27)]
        else:hs=[hole(u,G+.8,2.2,2.2) for u in (3,9,15,21,27)]
        wall(face,30,G,3.6,hs,'stone',.38)
        wall(face,30,3.6,7.2,[hole(u,4.1,1.8,2.75) for u in (3,8,13,18,23,27)],'wall',.34)
        if face.label=='hotel front':
            # Deep open upper loggia is enclosed by a rear room wall.
            wall(face,30,7.2,10.8,[hole(u,7.32,6.7,3.25,True) for u in (4,11.3,18.6,25.9)],'wall',.4)
            inner=C.Face((-16,-10.5,0),(1,0,0),(0,1,0),'upper loggia rooms')
            # Keep the second portal fully east of the guest-wing partition.
            wall(inner,30,7.32,10.8,[hole(u,7.32,2.4,2.9,True) for u in (4,12,18,26)],'wall')
            rail('front loggia guard',(-15.5,-15),(13.5,-15),7.32)
            for x in (-12,-5,2,10):plant(x,-14.35,7.32,.95,True)
        else:
            wall(face,30,7.2,10.8,[hole(u,7.7,2.0,2.75) for u in (3,8,13,18,23,27)],'wall',.34)
        for z in (3.6,7.2):face.part('stucco floor band',15,-.045,z,30,.48,.20,'wall','envelope',0)
        face.part('continuous eave bearing',15,.12,10.7,30,.55,.28,'wall','roof contact',0)
        # Source-specific stone pilaster bands and restrained balcony ironwork.
        for u in (0.4,15,29.6):
            face.part('stone vertical pier',u,-.03,5.4,.52,.46,10.8,'stone','structure',0)
            for j in range(29):face.part('dressed stone pier course',u,-.275,.20+j*.37,.54,.06,.35,'stone','masonry',.009)
        for z in (4.1,7.7):
            if z==7.7 and face.label=='hotel front':continue
            width=1.8 if z==4.1 else 2.0
            for u in (3,8,13,18,23,27):
                for dx in (-width/2-.06,width/2+.06):face.part('recessed opening stone jamb',u+dx,-.035,z+1.375,.12,.18,2.99,'stone','openings',.008)
                for zz in (z-.065,z+2.815):face.part('recessed opening stone lintel',u,-.04,zz,width+.24,.20,.13,'stone','openings',.008)
        for u in (8,18,27):
            for z in (3.72,7.32) if face.label!='hotel front' else (3.72,):
                face.part('Juliet balcony slab',u,-.28,z,2.3,.75,.14,'stone','balcony',0)
                a=face.p(u-1.05,-.65,z);b=face.p(u+1.05,-.65,z)
                beam('balcony handrail',(a[0],a[1],z+1.02),(b[0],b[1],z+1.02),.04,.04,'trim')
                for i in range(12):
                    p=face.p(u-1.05+i*2.1/11,-.65,z);beam('iron balcony picket',p,(p[0],p[1],z+1.02),.025,.025,'trim')
    # Court galleries: open rails and doors into furnished side wings.
    for l in (1,2):
        z=G+l*H
        for a,b in [((-3,-2),(4,-2)),((4,-2),(4,10)),((4,10),(-3,10)),((-3,10),(-3,-2))]:rail('courtyard gallery guard',a,b,z)
    for x,inward in [(-5.6,(-1,0,0)),(6.6,(1,0,0))]:
        face=C.Face((x,-10.5,0),(0,1,0),inward,'guest wing inner wall')
        for l in (1,2):wall(face,25.2,G+l*H,G+(l+1)*H-.1,[hole(12,G+l*H,2.4,2.8,True),hole(22,G+l*H,2.4,2.8,True),hole(4,G+l*H+1,2,1.65)],'wall')
    # Two front guest suites, separated from the stair lobby by open doorways.
    for l in (1,2):
        z=G+l*H
        face=C.Face((-15.7,0,0),(1,0,0),(0,-1,0),'suite entry partition')
        wall(face,10.1,z,z+3.3,[hole(8.2,z,2.4,2.8,True)],'wall')
        bed(-11,-6,z);solid('guest wardrobe',(-14.9,-2.9,z+1.1),(1.0,2.1,2.2),'timber')
        worktable(-7.4,-8.4,z,2.1,.75)
        if l==1:artwork(-11,-14.60,z+1.8,1.4,1.0,facing=1)
        else:artwork(-8.5,-10.15,z+1.8,1.4,1.0,facing=1)
        bed(10,7,z);worktable(10,11.5,z,2.2,.75)
    # Roof opening supports: three sky-lit loggia corners and central court.
    hotel_roof()
    for x in (-15.4,13.4):
        for y in (-14.4,14.4):solid('corner loggia post',(x,y,9.0),(.45,.45,3.6),'wall','structure')
    # Public ground: concierge, furnished lounge and restaurant.
    solid('concierge counter',(4,-7,G+.53),(3.6,1.15,1.06),'timber');box('concierge stone top',(4,-7,G+1.1),(3.8,1.3,.10),'stone','lobby')
    B.label('RECEPTION',(4,-7.59,G+.57),.19,'brass')
    sofa(-9,-9,G);sofa(-9,-4,G)
    worktable(-9,-6.4,G,1.6,.7)
    for x,y in [(9,-7),(9,-2),(10,3)]:B.table(x,y,G);obstacle(x-.9,x+.9,y-1.1,y+1.1,G,G+1.15)
    for x in (-10,-4,2):artwork(x,14.59,1.9,1.5,1.15)
    # Ground court is an explicit authored inference from the roof court.
    solid('fountain basin',(.5,4,G+.24),(2.1,2.1,.48),'stone','courtyard')
    box('fountain water',(.5,4,G+.50),(1.7,1.7,.025),'water','courtyard')
    C.rod('fountain column',(.5,4,G+.5),(.5,4,G+1.1),.12,'stone','courtyard',20)
    for x,y in [(-2.3,-1.1),(3.3,-1.1),(-2.3,9.1),(3.3,9.1)]:plant(x,y,G,.8,True)
    S.bench(-.8,8.5,G,1.5)
    # Long side pool: closed basin, contained water, explicit non-walkable reserve.
    box('recessed pool bed',(16.95,0,.16),(3.3,27,.24),'stone','pool')
    for x in (15.4,18.5):box('pool raised coping',(x,0,.43),(.24,27,.62),'stone','pool')
    for y in (-13.38,13.38):box('pool end coping',(16.95,y,.43),(3.1,.24,.62),'stone','pool')
    box('recessed pool water',(16.95,0,.49),(2.84,26.52,.035),'water','pool');obstacle(15.25,18.65,-13.6,13.6,0,2)
    for i,y in enumerate(range(-12,14,3)):
        plant(19,y,G,.8+.13*math.sin(i),i%2==0)
        if i%2==0:plant(19.35,y+.7,G,.42,True)
    for x,y in [(-15,-16.6),(-9,-16.6),(8,-16.6),(13,-16.6)]:plant(x,y,G,.7,True)
    for x in (-12,-5,2,10):
        for z in (4.15,7.45):
            box('window planter',(x,-15.35,z),(1.35,.38,.26),'stone','planting')
            for dx in (-.4,0,.4):plant(x+dx,-15.42,z-.1,.55,True,False)
            for k in range(4):
                xx=x-.45+k*.3
                beam('trailing flowering vine',(xx,-15.58,z+.15),(xx+.10*math.sin(k),-15.59,z-.55),.018,.018,'leaf')
                for j in range(5):ellipsoid('trailing flower foliage',(xx+.12*math.sin(j*2.4+k),-15.60,z+.03-j*.12),(.13,.09,.10),'flower' if (j+k)%3==0 else 'leaf')
    B.label('COURTYARD  HOTEL',(0,-15.08,3.23),.28,'brass')
    entrance=[[0,-17,G],[0,-12,G],[0,-6,G],[-4,-1,G],[sx,sy-1,G]]
    return [dict(name='hotel stairs and courtyard galleries',points=entrance+stair_route(sx,sy,2)+[[-7.2,2,7.32],[-4.5,1.5,7.32],[-4.5,11.5,7.32],[5.3,11.5,7.32],[5.3,-3.3,7.32],[0,-3.3,7.32]]),dict(name='courtyard and lobby',points=[[0,-17,G],[0,-6,G],[0,0,G],[2.5,0,G],[2.5,7,G],[2.5,10.5,G],[-4.4,10.5,G]]),dict(name='furnished guest suite',points=[[-10.2,2,3.72],[-7.5,2,3.72],[-7.5,-2,3.72],[-10,-2,3.72]])]

def roster(kind):
    s=SPECS[kind];w,d,h=s['width'],s['depth'],s['height'];target=(0,0,h*.44)
    views=[dict(name=n,location=p,target=target,ortho_scale=max(w,d)*1.3) for n,p in [('front',(0,-90,h*.44)),('left_side',(-90,0,h*.44)),('right_side',(90,0,h*.44)),('rear',(0,90,h*.44))]]
    views += [dict(name='front_corner',location=(w*1.7,-d*1.8,h*1.45),target=target),dict(name='aerial',location=(w*1.5,-d*1.5,h+45),target=target),dict(name='top',location=(0,0,130),target=(0,.001,0),ortho_scale=max(w,d)*1.4),dict(name='rear_side',location=(-w*1.5,d*1.8,h*1.4),target=target)]
    if kind=='school':
        close=[('facade_close',(17,-24,8),(4,-13,7)),('architecture_close',(25,-24,19),(10,-4,13)),('glass_close',(-5,-17,6),(-5,-8,5)),('roof_contact',(19,-19,21),(0,-1,14)),('program_interior',(2,-10,1.77),(-6,5,1.8)),('painting_studio',(1,-7,5.37),(-9,1,5.2)),('ceramics_studio',(1,-8,8.97),(-8,1,8.5)),('gallery_stair',(8.2,.4,1.77),(10,6,3.2)),('roof_lounge',(2,1,12.57),(-6,7,12.5)),('roof_terrace',(12,-8,12.57),(-9,-6,12)),('walk',(0,-15,1.77),(0,-8,2))]
    else:
        close=[('facade_close',(22,-27,7),(5,-15,6)),('architecture_close',(22,-25,17),(8,-9,11)),('glass_close',(-8,-20,5.3),(-10,-10,5)),('roof_contact',(18,-20,24),(-1,0,11)),('courtyard',(1,-1,1.77),(.5,7,3)),('program_interior',(0,-11,1.77),(-9,-5,2)),('guest_suite',(-7.8,-1.3,5.37),(-11,-7,4.9)),('gallery_stair',(-13,1.2,1.77),(-11,7,3)),('upper_gallery',(5.3,-3.2,8.97),(-2,8,9)),('pool_loggia',(18,-19,2),(14,4,4)),('walk',(0,-18,1.77),(0,-10,2))]
    views += [dict(name=n,location=p,target=t,whole=False,lens=25 if 'studio' in n or n in ('program_interior','roof_lounge','walk') else 32) for n,p,t in close]
    return views

def main():
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=SPECS,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--version',type=int,default=1);p.add_argument('--dry-run',action='store_true');p.add_argument('--resolution',type=int,default=1440)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);s=SPECS[a.kind];sources=[]
    for role,suffix in [('front','.png'),('oblique','_angle_60.jpg'),('top','_angle_90.jpg')]:
        path=ROOT/'frontend/public/archetypes/buildings'/s['directory']/('variant_'+str(s['index'])+suffix);data=path.read_bytes();assert len(data)>10000
        sources.append(dict(role=role,path='sources/'+path.name,original_path=str(path),repo_path=path.relative_to(ROOT).as_posix(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
    entry=dict(archetype_id=s['archetype'],variant_id=s['variant'],sources=sources,_reference_root=str(path.parent),directory='.')
    identity=['Glazed timber base, projecting two-storey paired glazing and planted front strips','Dark vertically ribbed sides with narrow slit windows','Offset roof pavilion, long lower terrace and two planted roofs with two capped stacks'] if a.kind=='school' else ['Three-storey white stucco and stone loggias','Joined terracotta hip roof with top-authoritative courtyard and corner terrace cutouts','Long narrow right-side pool, iron balconies and planted loggias']
    views=roster(a.kind);manifest=dict(candidate=f'interior-{a.kind}-clay-v{a.version:03d}',method=C.METHOD,archetype_id=s['archetype'],variant_id=s['variant'],representation_kind='architectural_clay',camera_roster=views,state='prework',keeper_claimed=False,runtime_seed_allowed=False,measurement_contract=dict(dimensions_m={k:s[k] for k in ('width','depth','height')},floors=s['floors'],front='-Y',bottom_datum_m=0,measurement_basis='Exact compatible catalogue proportions interpreted at plausible metric scale; not surveyed'),identity_contract=identity,hidden_view_assumptions=['Interior programme, rooms and circulation are authored inference','Rear continues exact family materials and opening grammar']+(['Top hotel source has roof cutouts absent in oblique; top owns roof topology','Ground-level courtyard is an authored interpretation of the top roof court'] if a.kind=='hotel' else []),limitations=['Architectural clay; no photographic texture keeper claim','Fixed complete assembly and occupied floor count','Prepared level site walking pilot; runtime pending'])
    out=C.prepare_candidate(a,entry,manifest,__file__)
    if out is None:return
    for source,name in [(HERE.parent/'station_interior/build.py','station_navigation.py'),(HERE.parent/'showcase_building_trio/build.py','showcase_shared.py')]:
        target=out/'scripts'/name;shutil.copy2(source,target);manifest['provenance']['scripts'].append(dict(path='scripts/'+name,sha256=C.digest(target)))
    (out/'prework-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    cams=C.setup(PALETTE,views,a.resolution);C.fit=B.efficient_fit;C.bpy.context.scene.cycles.samples=16
    bs=C.MATS['glass'].node_tree.nodes['Principled BSDF'];bs.inputs['Alpha'].default_value=.15;bs.inputs['Roughness'].default_value=.15
    for z in (2.7,6.3,9.9,13.5):
        for x in (-9,0,9):C.qa_room_light('interior',(x,0,z),550,7)
    print('BUILD_PHASE construction',flush=True)
    routes=school() if a.kind=='school' else hotel()
    walking=dict(version=2,triangles=S.TRIANGLES,obstacles=S.OBSTACLES,entrance=[0,-s['depth']/2+1,G],maxStepM=.20,routes=routes,bodyRadiusM=.22,headroomM=1.8,footprint=[s['width'],s['depth']],portals=[[-1.5,1.5,-s['depth']/2,-s['depth']/2+2]],scope='Actual floor-top triangles and height-bounded construction; public routes only')
    C.write_json(out/'walking-network.json',walking);next(o for o in C.objects() if o.get('cityprompt_semantic_role')=='walk_floor')['cityprompt_walking_json']=json.dumps(walking,separators=(',',':'))
    print('BUILD_PHASE delivery',flush=True);report=C.deliver(out,manifest,cams)
    C.write_json(out/'walking-model-lock.json',dict(model_sha256=report['runtime']['sha256'],network_sha256=C.digest(out/'walking-network.json')))

if __name__=='__main__':main()
