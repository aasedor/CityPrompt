"""Four source-specific constructors, finite clay checkpoints; no runtime writes."""
import argparse
import math
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE));sys.path.append(str(HERE.parent/'catalogue_services_batch'))
import clay_core as C
from plan import SPECS,source_entry

PALETTE=dict(wall=(.58,.56,.50),trim=(.66,.63,.54),roof=(.46,.49,.48),foundation=(.45,.44,.40),
    glass=(.31,.37,.38),hardware=(.075,.085,.085),interior=(.66,.62,.53),floor=(.46,.44,.39),
    joint=(.27,.28,.27),timber=(.44,.26,.12),bronze=(.24,.20,.15),brick=(.40,.20,.13),
    pale=(.73,.71,.63),planting=(.17,.23,.12),yellow=(.65,.43,.06))

def cameras(kind):
    s=SPECS[kind];d=s['dimensions'];scale=max(d['width'],d['depth'])/34;h=d['height']*.4
    basic=[('front',(0,-64,12)),('front_corner',(46,-58,32)),('aerial',(39,-49,69)),('top',(0,0,90)),
        ('left_side',(-64,0,12)),('right_side',(64,0,12)),('rear',(0,64,12)),('rear_side',(-46,58,32))]
    out=[dict(name=n,location=tuple(v*scale for v in loc),target=(0,.001 if n=='top' else 0,0 if n=='top' else h),
        **({'ortho_scale':d['width']*1.2} if n=='top' else {})) for n,loc in basic]
    details={
      'warehouse':[('facade_close',(18,-70,12),(5,-43,5)),('architecture_close',(87,-62,10),(63,-43,3)),
        ('glass_close',(77,-54,10),(66,-43,7)),('roof_contact',(65,-38,28),(52,-25,15)),
        ('side_projection',(96,-23,14),(72,-29,7)),('dock_close',(-17,-57,6),(-21,-43,3)),
        ('interior',(69,-40,2.5),(57,-29,3.0)),('office_stair',(63,-32.5,3.5),(58,-29.5,3.5)),
        ('stair_arrival',(61,-33,9.7),(58,-30,8.1))],
      'tiltup':[('facade_close',(-14,-36,12),(-10,-18,4)),('architecture_close',(4,-27,5),(0,-19,2)),
        ('glass_close',(-7,-22,3),(-7,-17,2.2)),('roof_contact',(-1,-18,17),(-12,-3,9.7)),
        ('side_projection',(41,-22,9),(27,-7,3)),('interior',(13,12,2.7),(-12,-8,3.5)),
        ('office_stair',(-2,-11,3),(-8,-12,3)),('stair_arrival',(-4,-17,6),(-8,-14.2,4.2)),
        ('hall_access',(17,-3,2.6),(8,-10,1.6))],
      'factory':[('facade_close',(29,-37,12),(10,-14,5)),('architecture_close',(-4,-27,5),(-13,-16,2)),
        ('glass_close',(10,-20,4),(10,-13,3.5)),('roof_contact',(10,-24,17),(8,-6,9)),
        ('side_projection',(39,-10,13),(25,0,7)),('interior',(20,-11,3),(0,7,7)),
        ('roof_inside',(1,-7,4),(1,3,8.8)),('loading_access',(0,-7,2.8),(-10,-12,1.1)),('chimney_close',(39,22,29),(25,10,20))],
      'admin':[('facade_close',(28,-36,23),(5,-17,12)),('architecture_close',(7,-27,5),(3.5,-16,3)),
        ('glass_close',(-7,-22,10),(-7,-16,9.4)),('roof_contact',(27,-25,33),(1,0,22)),
        ('side_projection',(29,-17,16),(17,-6,12)),('interior',(-10,-13,2),(-9,6,2)),
        ('office_stair',(3,4,6),(0,8,5)),('stair_arrival',(3,3.5,18),(0,7.5,16.2))],
      'peaks':[('facade_close',(25,-31,16),(5,-10,7)),('architecture_close',(3,-20,4),(.6,-11,2)),
        ('glass_close',(15,-16,7),(13.5,-10,6)),('roof_contact',(24,-18,23),(11,-4,12)),
        ('side_projection',(29,-3,14),(17,0,9)),('interior',(13,-9,2),(13,5,2)),
        ('gable_room',(13,-5.8,11),(13,1,11)),('roof_stair',(15,-3,11),(14,1,10)),
        ('stair_arrival',(14,-5,11.8),(14,-.3,10)),('rear_pavilion',(12,17,16),(6,7,12)),
        ('corner_entrance',(23,-18,3.5),(15,-10.8,1.4))],
    }[kind]
    return out+[dict(name=n,location=loc,target=target,whole=False,lens=26 if n in ('office_stair','stair_arrival','interior','roof_stair','gable_room','hall_access','roof_inside','loading_access') else 42) for n,loc,target in details]

def manifest(kind,version):
    s=SPECS[kind];cams=cameras(kind)
    return dict(candidate=f'{s["title"]}-clay-v{version:03d}',method=C.METHOD,representation_kind='architectural_clay',
        archetype_id=s['parent'],variant_id=s['variant'],state='prework',keeper_claimed=False,runtime_seed_allowed=False,
        measurement_contract=dict(dimensions_m=s['dimensions'],observed_storeys=s['floors'],source_measurements=s['measurements'],hidden_assumptions=s['assumptions']),
        roof_contract=dict(authority='Exact sources, explicit reconciliations in measurement contract; complete seated roof surfaces.'),
        identity_contract=dict(owner='Physical envelope, openings, roof graph and joinery.',bitmap_stickers='None in architectural clay.'),
        material_contract=dict(profile='Source-palette semantic architectural clay',limitations='No source-conditioned PBR or textured-keeper claim.'),
        programme_contract=dict(storeys=s['floors'],interiors='Conceptual programme and connected stairs; not surveyed.'),
        contact_contract=['Foundation reaches grade zero.','Openings cut every wall carrier.','Stairs connect physical floor apertures and guarded landings.','Roof and plant have seated support.'],
        supersedes=f'{s["title"]}-clay-v{version-1:03d}' if version>1 else None,
        finite_corrections=(['Continuous front glazing and broad raised corner ends; paired entry door details; upper stair half-edge guard; contained office QA lighting; clear roof and hall proof views.'] if kind=='tiltup' and version==2 else
            ['TI-02/TI-05: operative office-hall door hardware and dedicated clear hall-access view. Reframe complete upper stair arrival.'] if kind=='tiltup' and version==3 else
            ['Close office floor perimeter to left carrier and right end wall; extend rear partition to left carrier; retain v003 door/proof corrections.'] if kind=='tiltup' and version==4 else
            ['Lower factory trusses beneath the roof skin; connect and support the dock stair, goods-floor transition and rear access; add roof-interior and loading-circulation proof.'] if kind=='factory' and version==2 else
            ['Contain the interior goods platform inside the left brick carrier, preserving all v002 roof and circulation corrections.'] if kind=='factory' and version==3 else
            ['Correct the corridor-face normal vector; v001 construction stopped before export.'] if kind=='admin' and version==2 else
            ['Seat plant louvres on vertical posts and base framing; show top occupied-floor stair terminal/arrival.'] if kind=='admin' and version==3 else
            ['Restore the source corner glazing and ribbed side return, source timber side bay and glazed corner entrance; contain timber joints within their carriers.'] if kind=='peaks' and version==2 else
            ['Separate timber facing from the pale backing to eliminate coplanar faces; remove the planter blocking the corner entrance and provide a seated clear approach and proof camera.'] if kind=='peaks' and version==3 else
            ['WH-01: complete supported and guarded office stairs, clear floor apertures and unobstructed landings; three new interior/arrival proof cameras.'] if kind=='warehouse' else []),
        runtime_contract=dict(scale='fixed_native_only',translation=True,rotation=True,resizing=False,terrain='not tested',installation='not installed',review='not tested'),
        camera_roster=cams,mandatory_review_views=[c['name'] for c in cams])

def cleanup():
    for obj in C.objects():
        bm=C.bmesh.new();bm.from_mesh(obj.data);C.bmesh.ops.triangulate(bm,faces=list(bm.faces))
        C.bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<=1e-10],context='FACES_ONLY')
        bm.to_mesh(obj.data);bm.free();obj.data.update()

def faces(w,d):
    return [C.Face((0,-d/2,0),(1,0,0),(0,1,0),'front'),C.Face((w/2,0,0),(0,1,0),(-1,0,0),'right'),
        C.Face((0,d/2,0),(-1,0,0),(0,-1,0),'rear'),C.Face((-w/2,0,0),(0,-1,0),(1,0,0),'left')]

def hole(ident,u,z,w,h):return dict(id=ident,u=u,z=z,w=w,h=h)

def glazed_door(f,ident,u,z,w,h,role='hardware'):
    pair=w>1.65
    f.window(ident,u,z,w,h,cols=2 if pair else 1,rows=1,frame=role,sill=False,kind='glazed entrance door')
    for du in ((-.12,.12) if pair else (w*.32,)):
        C.rod(ident+' pull',f.p(u+du,.02,z+.85),f.p(u+du,.02,z+1.45),.021,'hardware','door hardware')

def grid(f,span,zmax,holes,step=3,zs=(4.8,),role='joint'):
    for u in [i*step for i in range(math.ceil(-span/2/step),math.floor(span/2/step)+1)]:
        intervals=[(.25,zmax)]
        for h in holes:
            if abs(u-h['u'])<h['w']/2+.08:
                result=[]
                for a,b in intervals:
                    if a<h['z']:result.append((a,min(b,h['z'])))
                    if b>h['z']+h['h']:result.append((max(a,h['z']+h['h']),b))
                intervals=result
        for a,b in intervals:
            if b>a:f.part('Panel vertical reveal',u,-.004,(a+b)/2,.022,.012,b-a,role,'panel joints',0)
    for z in zs:
        intervals=[(-span/2,span/2)]
        for h in holes:
            if h['z']-.03<z<h['z']+h['h']+.03:
                result=[]
                for a,b in intervals:
                    if a<h['u']-h['w']/2:result.append((a,min(b,h['u']-h['w']/2)))
                    if b>h['u']+h['w']/2:result.append((max(a,h['u']+h['w']/2),b))
                intervals=result
        for a,b in intervals:
            if b>a:f.part('Panel horizontal reveal',(a+b)/2,-.004,z,b-a,.012,.022,role,'panel joints',0)

def roller(f,h):
    f.door(h['id'],h['u'],h['z'],h['w'],h['h'],role='roof',panels=14)
    for s in (-1,1):
        p=f.p(h['u']+s*(h['w']/2+.35),-.45,0)
        C.rod('Loading bollard',p,(p[0],p[1],1.15),.09,'yellow','loading protection',12)

def hvac(x,y,z,w=2.5,d=1.7):
    C.box('Plant support curb',(x,y,z+.16),(w+.2,d+.2,.32),'hardware','plant curb')
    C.box('Plant enclosure',(x,y,z+.67),(w,d,1.02),'roof','mechanical plant')
    for q in (-.26,.26):
        C.rod('Plant fan housing',(x+q*w,y,z+1.18),(x+q*w,y,z+1.24),min(d*.30,w*.19),'hardware','plant fans',24)
        for j in range(5):
            a=j*math.pi/5;rr=min(d*.26,w*.17)
            C.beam('Fan grille',(x+q*w-rr*math.cos(a),y-rr*math.sin(a),z+1.25),(x+q*w+rr*math.cos(a),y+rr*math.sin(a),z+1.25),.026,.026,'trim','plant grille')

def desk(x,y,z):
    C.box('Work desk',(x,y,z+.77),(1.5,.72,.07),'timber','occupied offices')
    for dx in (-.64,.64):C.box('Desk leg',(x+dx,y,z+.36),(.06,.62,.72),'hardware','occupied offices')
    C.box('Monitor',(x,y+.16,z+1.02),(.5,.045,.32),'hardware','occupied offices')
    C.box('Monitor foot',(x,y+.16,z+.83),(.20,.20,.08),'hardware','occupied offices')
    C.box('Task chair seat',(x,y-.65,z+.44),(.46,.46,.08),'bronze','occupied offices')
    C.box('Task chair back',(x,y-.86,z+.68),(.46,.07,.43),'bronze','occupied offices')
    C.rod('Chair pedestal',(x,y-.65,z+.10),(x,y-.65,z+.40),.05,'hardware','occupied offices')
    C.box('Chair feet',(x,y-.65,z+.06),(.43,.43,.08),'hardware','occupied offices')

def stair_cut(slab,x,y,run):
    # Explicit world-space bounds; slab vertices are authored in world space.
    b=C.bounds([slab]);z=(b[0][2]+b[1][2])/2
    C.cut_box(slab,'Full floor stair aperture',(x,y+(run+.75)/2,z),(2.70,run+.85,1))

def stair(x,y,z,rise,run=2.7,n=10,terminal=True):
    """Switchback: bottom/upper arrival at y, full-width midlanding at y+run."""
    half=rise/2;going=run/n;rr=half/n
    for i in range(n):
        for xx,yy,zz in [(x-.70,y+(i+.5)*going,z+(i+1)*rr),(x+.70,y+run-(i+.5)*going,z+half+(i+1)*rr)]:
            C.box('Stair tread',(xx,yy,zz-.055),(1.20,going+.015,.11),'trim','stairs')
    C.box('Midlanding',(x,y+run+.35,z+half-.07),(2.65,.72,.14),'trim','stairs')
    C.box('Arrival landing',(x+.70,y-.25,z+rise-.08),(1.25,.55,.16),'floor','stairs')
    for xx in (x-1.23,x-.17):C.beam('Ascending stringer',(xx,y,z-.03),(xx,y+run,z+half-.10),.10,.22,'hardware','stairs')
    for xx in (x+.17,x+1.23):C.beam('Return stringer',(xx,y+run,z+half-.10),(xx,y,z+rise-.10),.10,.22,'hardware','stairs')
    for xx in (x-1.23,x+1.23):C.box('Landing support',(xx,y+run+.48,z+half/2),(.12,.12,half),'hardware','stairs')
    for xx,z0,z1 in [(x-1.29,z,z+half),(x-.11,z,z+half),(x+.11,z+rise,z+half),(x+1.29,z+rise,z+half)]:
        C.beam('Stair handrail',(xx,y,z0+.98),(xx,y+run,z1+.98),.043,.043,'hardware','stairs')
        for j in range(6):
            yy=y+j*run/5;zz=z0+(z1-z0)*j/5
            C.rod('Stair baluster',(xx,yy,zz),(xx,yy,zz+.98),.018,'hardware','stairs',8)
    C.railing('Midlanding rear guard',(x-1.30,y+run+.67,z+half),(x+1.30,y+run+.67,z+half),spacing=.15,role='hardware')
    for xx in (x-1.37,x+1.37):C.railing('Upper well guard',(xx,y,z+rise),(xx,y+run+.8,z+rise),spacing=.16,role='hardware')
    C.railing('Upper rear well guard',(x-1.37,y+run+.8,z+rise),(x+1.37,y+run+.8,z+rise),spacing=.16,role='hardware')
    if terminal:C.railing('Upper front half well guard',(x-1.37,y-.10,z+rise),(x-.10,y-.10,z+rise),spacing=.14,role='hardware')
    C.qa_room_light('stair',(x,y+run/2,z+rise+.8),220,2)

def tiltup():
    w,d=54,36;top=9.2
    C.box('Foundation',(0,0,.1),(w,d,.2),'foundation','foundation',0)
    fs=faces(w,d)
    for f in fs:
        span=w if f.label in ('front','rear') else d;hs=[]
        if f.label=='front':
            hs=[hole('Upper continuous office band',-7,5.2,34,2),hole('Ground left office band',-13.2,1,21.6,2),hole('Ground right office band',6.2,1,7.6,2)]
            hs.append(hole('Main entrance',0,.2,3.2,2.8))
        elif f.label=='right':hs=[hole('Rollup '+str(u),u,.2,3.15,4.2) for u in (-14,-10,-6,-2,2,6,10,14)]
        elif f.label=='rear':hs=[hole('Rollup rear '+str(u),u,.2,4,4.2) for u in (-21,-14,-7,0,7,14,21)]
        else:
            hs=[hole(f'Left office {j} {u}',u,z,3.6,2) for j,z in enumerate((1,5.2)) for u in (12,)]
            hs+=[hole('Left service',-11,.2,1.1,2.4)]
        f.wall(f.label+' tilt panel',-span/2,span/2,.2,top,holes=hs,depth=.3)
        for h in hs:
            if 'Rollup' in h['id']:roller(f,h)
            elif 'entrance' in h['id']:
                f.window(h['id'],0,.2,3.2,2.8,cols=2,rows=1,frame='hardware',sill=False,kind='paired glazed entrance')
                f.part('Entry door transom',0,.13,2.50,3.1,.10,.06,'hardware','entry hardware')
                for u in (-.15,.15):C.rod('Entry door pull',f.p(u,.01,1.1),f.p(u,.01,1.65),.023,'hardware','entry hardware')
            elif 'service' in h['id']:f.door(h['id'],h['u'],h['z'],h['w'],h['h'],role='hardware')
            else:f.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=max(3,round(h['w']/1.25)),frame='hardware',depth=.3)
        grid(f,span,top,hs,zs=(4.4,8.0))
        f.part('Parapet coping',0,.10,top+.07,span+.14,.46,.14,'hardware','parapet coping')
    C.box('Flat roof',(0,0,8.91),(53.4,35.4,.22),'pale','roof',0)
    for x in (-23.25,23.25):
        for y in (-17.85,17.85):
            C.box('Raised parapet front return',(x,y,9.82),(7.5,.3,1.26),'wall','raised corners')
            C.box('Raised parapet end coping',(x,y,10.49),(7.62,.44,.12),'hardware','raised corners')
    for x in (-26.85,26.85):
        for y in (-14.25,14.25):
            C.box('Raised corner side',(x,y,9.82),(.3,7.5,1.26),'wall','raised corners')
            C.box('Raised corner side cap',(x,y,10.49),(.44,7.62,.12),'hardware','raised corners')
    # Office floor and corridor partition; high-bay hall remains undivided.
    slab=C.box('Office upper floor',(-7.35,-13.85,4.28),(38.7,7.7,.20),'floor','office floors',0);stair_cut(slab,-8,-15.4,2.4)
    part=C.Face((-7,-10,0),(1,0,0),(0,-1,0),'office rear partition')
    hs=[hole('Office hall access',15,.2,1.5,2.5),hole('Upper internal office window',0,5.3,5,1.8)]
    part.wall('Office hall separation',-19.7,19,.2,8.8,holes=hs,depth=.18,role='interior')
    end=C.Face((12,-14,0),(0,1,0),(-1,0,0),'office right end')
    end.wall('Office full end return',-4,4,.2,8.8,depth=.18,role='interior')
    glazed_door(part,'Office hall access',15,.2,1.5,2.5)
    part.window('Upper internal office window',0,5.3,5,1.8,cols=4,frame='hardware',depth=.18)
    stair(-8,-15.4,.2,4.18,2.4,11)
    for z in (.2,4.38):
        for x in (-22,-17,-3,3,9):desk(x,-15,z)
        for lx in (-20,-5,8):C.qa_room_light('Office strip',(lx,-14,z+3.6),260,3)
    for y in (-7,3,13):
        for x in (-18,0,18):C.box('Hall steel column',(x,y,4.55),(.24,.24,8.7),'hardware','hall structure')
        C.box('Hall roof bearer',(0,y,8.54),(53,.22,.45),'hardware','hall structure')
    for x in (-18,-6,6):
        for y in (1,9):
            for lev in (0,1,2):C.box('Storage shelf',(x,y,.5+lev*1.5),(7,1.5,.12),'bronze','industrial storage')
            for dx in (-3.3,3.3):C.box('Rack upright',(x+dx,y,2.2),(.12,1.5,4.0),'hardware','industrial storage')
            for dx in (-2,0,2):C.box('Stored crate',(x+dx,y,1.05),(1.4,1.1,1),'timber','industrial storage')
    for x,y in ((-16,-3),(-8,-3)):hvac(x,y,9.02)
    for x in (-18,-10,-2):C.box('Roof hatch curb',(x,7,9.19),(2.2,1.4,.34),'trim','roof hatches')
    C.box('Entrance canopy',(0,-19.5,3.2),(6.5,3.6,.22),'hardware','entry canopy')
    for x in (-2.8,2.8):
        C.box('Canopy footing',(x,-20.8,.14),(.5,.5,.28),'foundation','entry support')
        C.box('Canopy post',(x,-20.8,1.65),(.14,.14,2.95),'hardware','entry support')
    C.box('Entrance approach',(0,-19.6,.10),(6.7,3.3,.2),'foundation','entry landing')
    C.qa_room_light('Industrial hall',(0,4,8),3500,15)
    C.CONTACTS.append(dict(name='Office stair',lower=.2,upper=4.38,physical_aperture=True))

def factory():
    w,d=49,28;walltop=6.6;ridge=10.8
    C.box('Factory foundation',(0,0,.18),(49,28,.36),'foundation','foundation',0)
    C.box('Factory industrial floor',(0,0,.41),(48.4,27.4,.10),'floor','floor',0)
    for f in faces(w,d):
        span=w if f.label in ('front','rear') else d
        if f.label=='front':
            hs=[hole('Loading shutter '+str(u),u,1.05,4.0,3.8) for u in (-21,-15,-9,-3)]
            hs += [hole('Tall works window '+str(u),u,1.7,2.2,3.4) for u in (3,7,11,15,19,23)]
        else:
            us=[-21,-14,-7,0,7,14,21] if span==49 else [-10,-5,0,5,10]
            hs=[hole(f'{f.label} works window {u}',u,1.7,2.2,3.4) for u in us]
            if f.label=='rear':
                hs=[h for h in hs if h['u']!=0];hs.append(hole('Rear personnel door',0,.46,1.3,2.5))
        f.wall(f.label+' brick carrier',-span/2,span/2,.36,walltop,holes=hs,depth=.36,role='brick')
        for h in hs:
            u,z,ww,hh=h['u'],h['z'],h['w'],h['h']
            if 'shutter' in h['id']:f.door(h['id'],u,z,ww,hh,role='bronze',panels=18)
            elif 'door' in h['id']:f.door(h['id'],u,z,ww,hh,role='bronze')
            else:
                f.window(h['id'],u,z,ww,hh,cols=4,rows=6,frame='bronze',bar=.035,depth=.36)
                # Segmental brick head has real thickness across the rectangular carrier cut.
                for side in (-1,1):
                    curve=[(u+side*ww*j/24,z+hh-.24*(j/12)**2) for j in range(13)]
                    f.panel('Segmental head infill',curve+[(u+side*ww/2,z+hh),(u,z+hh)],0,.36,'brick','arched heads')
                for j in range(16):
                    xa=-ww/2+ww*j/16;xb=-ww/2+ww*(j+1)/16
                    za=z+hh-.24*(xa/(ww/2))**2;zb=z+hh-.24*(xb/(ww/2))**2
                    f.panel('Segmental head brick arch',[(u+xa,za),(u+xb,zb),(u+xb,zb+.16),(u+xa,za+.16)],-.06,.08,'brick','arch ring')
        # Framing piers are positioned between apertures, never across the glazing.
        boundaries=sorted({-span/2+.15,span/2-.15}|{(a['u']+a['w']/2+b['u']-b['w']/2)/2 for a,b in zip(sorted(hs,key=lambda h:h['u']),sorted(hs,key=lambda h:h['u'])[1:])})
        for u in boundaries:f.part('Brick pilaster',u,-.09,3.33,.26,.22,5.94,'brick','brick articulation')
        f.part('Brick cornice',0,-.09,6.35,span,.30,.24,'brick','cornice')
        for i in range(round(span/.36)):
            f.part('Cornice dentil',-span/2+.18+i*.36,-.12,6.10,.14,.25,.14,'brick','cornice',0)
    # Seven-tooth interpretation locked to hero + oblique; each glazed slope opens into the hall.
    for tooth in range(7):
        a=-24.5+7*tooth;b=a+7;r=a+3.0
        for yy in (-14,13.64):C.prism('Sawtooth brick end',[(a,6.55),(b,6.55),(r,ridge)],'y',yy,yy+.36,'brick','roof ends')
        C.solid_surface('Opaque tooth roof',[(a,-14.18,6.6),(r,-14.18,ridge),(r,14.18,ridge),(a,14.18,6.6)],.15,'roof')
        # Last metre of the glazed slope is an opaque weathering apron.
        q=b-.8;zq=6.6+(b-q)/4*(ridge-6.6)
        C.solid_surface('Lower glazed-slope apron',[(q,-14.18,zq),(b,-14.18,6.6),(b,14.18,6.6),(q,14.18,zq)],.15,'roof')
        for j in range(28):
            y0=-14+j;y1=y0+1
            for k in range(4):
                x0=r+(q-r)*k/4;x1=r+(q-r)*(k+1)/4
                def zz(x):return ridge-(x-r)*(ridge-6.6)/4
                C.solid_surface('Roof optical pane',[(x0+.025,y0+.025,zz(x0+.025)),(x1-.025,y0+.025,zz(x1-.025)),
                    (x1-.025,y1-.025,zz(x1-.025)),(x0+.025,y1-.025,zz(x0+.025))],.012,'glass','roof glazing')
        for j in range(29):
            yy=-14+j;C.beam('Roof glazing mullion',(r,yy,ridge+.02),(q,yy,zq+.02),.045,.07,'hardware','roof glazing frame')
        for k in range(5):
            xx=r+(q-r)*k/4;zz=ridge-(xx-r)*(ridge-6.6)/4
            C.beam('Roof glazing transom',(xx,-14,zz+.02),(xx,14,zz+.02),.045,.055,'hardware','roof glazing frame')
        C.beam('Tooth ridge cap',(r,-14.2,ridge+.04),(r,14.2,ridge+.04),.14,.14,'hardware','roof ridges')
        for yy in (-14.12,14.12):
            C.beam('Roof-end coping',(a,yy,6.64),(r,yy,ridge+.04),.13,.18,'trim','roof coping')
            C.beam('Roof-end coping',(r,yy,ridge+.04),(b,yy,6.64),.13,.18,'trim','roof coping')
        for yy in (-9,0,9):
            C.beam('Truss bottom chord',(a,yy,6.32),(b,yy,6.32),.14,.18,'hardware','factory trusses')
            C.beam('Truss top chord',(a,yy,6.32),(r,yy,10.52),.13,.16,'hardware','factory trusses')
            C.beam('Truss top chord',(r,yy,10.52),(b,yy,6.32),.13,.16,'hardware','factory trusses')
            C.beam('Truss king post',(r,yy,6.32),(r,yy,10.52),.10,.12,'hardware','factory trusses')
    for xx in (-24.1,-10.5,3.5,17.5,24.1):
        for yy in (-9,0,9):C.box('Factory truss post',(xx,yy,3.39),(.2,.2,5.9),'hardware','factory structure')
    for yy in (-9,0,9):C.beam('Continuous truss bearing beam',(-24.3,yy,6.19),(24.3,yy,6.19),.24,.24,'hardware','factory structure')
    # Machinery and aligned work aisles establish an industrial programme under the transparent roof.
    for xx in (-15,-1,13):
        for yy in (-7,1,8):
            C.box('Machine base',(xx,yy,.66),(3.7,1.8,.4),'hardware','machine tools')
            C.box('Machine cabinet',(xx,yy,1.40),(3.0,1.35,1.1),'roof','machine tools')
            C.box('Machine work bed',(xx,yy-1,1.25),(2.8,.7,.16),'hardware','machine tools')
            C.box('Machine control column',(xx+1.4,yy-.8,1.75),(.35,.3,.95),'bronze','machine tools')
            C.rod('Horizontal machine spindle',(xx-1.2,yy,1.9),(xx+1.1,yy,1.9),.25,'hardware','machine tools',16)
    # Raised loading platform; visible side stair and continuous canopy supports.
    C.box('Loading dock',(-12,-15.55,.52),(27,3.1,1.04),'foundation','loading dock')
    for i in range(6):C.box('Dock steps',(1.64+i*.3,-15.55,(6-i)*1.04/12),(.32,2.6,(6-i)*1.04/6),'foundation','dock stairs')
    C.beam('Dock stair outer rail',(1.50,-16.75,2.05),(3.44,-16.75,1.05),.045,.045,'bronze','dock stairs')
    for xx,zz in ((1.64,1.04),(3.14,1.04/6)):
        C.beam('Dock stair rail post',(xx,-16.75,zz),(xx,-16.75,zz+1.0),.045,.045,'bronze','dock stairs')
    # The dock continues through loading doors before stepping down into the hall.
    C.box('Interior goods landing',(-11.3,-12.3,.745),(25.6,2.9,.59),'foundation','loading circulation')
    for xx in (-21,-15,-9,-3):
        for j in range(4):
            zz=1.04-(j+1)*.145
            C.box('Interior goods step',(xx,-10.69+j*.30,(zz+.46)/2),(3.8,.32,zz-.46+.02),'foundation','loading circulation')
    C.box('Rear door landing',(0,14.4,.23),(1.8,.85,.46),'foundation','rear access')
    for j in range(2):C.box('Rear door step',(0,14.98+j*.30,(2-j)*.46/6),(1.8,.32,(2-j)*.46/3),'foundation','rear access')
    C.solid_surface('Dock canopy',[(-25.4,-17.1,4.85),(1.4,-17.1,4.85),(1.4,-13.9,5.25),(-25.4,-13.9,5.25)],.14,'bronze','dock canopy')
    for xx in (-24,-18,-12,-6,0):
        C.box('Canopy front post',(xx,-16.65,2.94),(.13,.13,3.8),'bronze','canopy support')
        C.beam('Canopy knee brace',(xx,-16.65,4.05),(xx,-15.5,4.97),.08,.10,'bronze','canopy support')
    C.box('Canopy edge beam',(-12,-16.65,4.78),(27,.16,.20),'bronze','canopy support')
    # Hollow tapered chimney, bounded circular masonry crown and actual interior flue.
    cx,cy=27.0,9.8;N=64;z0=.35;zt=25
    C.box('Chimney footing',(cx,cy,.175),(3.8,3.8,.35),'foundation','chimney footing')
    vs=[]
    for z,r in ((z0,1.7),(zt,1.25),(zt,.93),(z0,1.36)):
        vs.extend((cx+r*math.cos(i*math.tau/N),cy+r*math.sin(i*math.tau/N),z) for i in range(N))
    polys=[]
    for ring in range(4):
        nr=(ring+1)%4
        for i in range(N):polys.append((ring*N+i,ring*N+(i+1)%N,nr*N+(i+1)%N,nr*N+i))
    C.mesh('Continuous hollow chimney',vs,polys,'brick','chimney')
    for i in range(N):
        a=i*math.tau/N;b=(i+1)*math.tau/N
        C.beam('Chimney crown band',(cx+1.26*math.cos(a),cy+1.26*math.sin(a),24.7),(cx+1.26*math.cos(b),cy+1.26*math.sin(b),24.7),.13,.18,'brick','chimney crown')
    C.qa_room_light('Factory hall',(0,0,6),3000,16)
    C.CONTACTS.append(dict(name='Sawtooth source reconciliation',front_oblique_count=7,rejected_top_count=6,chimney='independent grounded shell'))

def admin():
    w=d=34;base=.20;storey=4;top=20.4
    C.box('Office foundation',(0,0,.1),(w,d,.2),'foundation','foundation',0)
    front=C.Face((0,-17,0),(1,0,0),(0,1,0),'front left')
    hs=[hole(f'Brick window {lev} {u}',u,base+lev*storey+.45,1.70,2.9) for lev in range(5) for u in (-14.8,-11.6,-8.4,-5.2,-2.0)]
    front.wall('Front left brick',-17,0,base,top,holes=hs,depth=.32,role='brick')
    for h in hs:front.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=2,frame='bronze',depth=.32)
    # Recessed glazed circulation slot bounded by deep, load-bearing pale cheeks.
    slot=C.Face((0,-16.0,0),(1,0,0),(0,1,0),'entrance slot')
    sh=[hole('Entry pair',3.0,.2,2.0,2.8)]+[hole('Slot glass '+str(lev),3.0,4.2*0+base+lev*4+.2,4.65,3.5) for lev in range(1,5)]
    sh += [hole('Entry transom',3,3.05,4.65,.7),hole('Entry sidelight left',1.2,.2,.85,2.8),hole('Entry sidelight right',4.8,.2,.85,2.8)]
    slot.wall('Recessed glazed carrier',.3,5.7,.2,20.35,holes=sh,role='bronze')
    for h in sh:
        slot.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=2,frame='hardware',sill=False)
    for xx in (.15,5.85):C.box('Deep entrance reveal',(xx,-16.5,10.2),(.30,1.30,20.0),'trim','entry portal')
    C.box('Entry portal lintel',(3,-16.5,20.25),(6,1.30,.30),'trim','entry portal')
    C.box('Entry approach',(3,-17.35,.10),(5.3,2.8,.20),'foundation','entry approach')
    for xx in (2.48,3.52):C.rod('Entry door pull',(xx,-16.19,1.05),(xx,-16.19,1.7),.025,'hardware','entry hardware')
    # Projecting corner: brick infill, bronze structural frame, closed opaque side return.
    corner=C.Face((0,-17.6,0),(1,0,0),(0,1,0),'bronze corner')
    ch=[hole(f'Corner glass {lev} {u}',u,.65+lev*4,3.6,2.9) for lev in range(5) for u in (8.45,13.9)]
    corner.wall('Corner brick carrier',6,17,.2,20.4,holes=ch,role='brick',depth=.35)
    for h in ch:corner.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=2,frame='bronze',depth=.35)
    for xx in (6.1,16.85):C.box('Bronze full-height fin',(xx,-17.82,12.3),(.30,.75,16.2),'bronze','corner frame')
    for z in (4.2,8.2,12.2,16.2,20.3):C.box('Bronze spandrel frame',(11.5,-17.8,z),(11.3,.72,.30),'bronze','corner frame')
    C.box('Corner projection soffit',(11.5,-17.25,4.18),(11.4,1.5,.24),'bronze','corner support')
    # Narrow end closes the projection at x=6; entrance portal remains open.
    C.box('Bronze inner return',(6.02,-17.25,12.3),(.16,1.25,16.2),'bronze','corner frame')
    for f in faces(w,d)[1:]:
        us=(-7,-4,-1,2,5,8,11,14) if f.label=='right' else (-14,-10.5,-7,-3.5,0,3.5,7,10.5,14)
        hs=[hole(f'{f.label} window {lev} {u}',u,.65+lev*4,1.70,2.9) for lev in range(5) for u in us]
        if f.label=='rear':
            hs=[h for h in hs if not(h['u']==0 and h['z']<1)]
            hs.append(hole('Rear entrance',0,.2,1.8,2.9))
        f.wall(f.label+' brick envelope',-17,17,.2,20.4,holes=hs,role='brick',depth=.32)
        for h in hs:
            if 'entrance' in h['id']:glazed_door(f,h['id'],h['u'],h['z'],h['w'],h['h'],'bronze')
            else:f.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=2,frame='bronze',depth=.32)
    C.box('Bronze corner side return',(17.09,-13.5,12.3),(.23,8.4,16.2),'bronze','corner cladding')
    for xx in (6.06,17.0):C.box('Ground corner projection closure',(xx,-17.25,2.2),(.22,.85,4.0),'brick','corner closure')
    for yy in (-17.3,-15.3,-13.3,-11.3,-9.3):C.box('Side metal panel joint',(17.22,yy,12.3),(.012,.025,16.1),'joint','corner joints')
    for z in (8.2,12.2,16.2):C.box('Side metal horizontal joint',(17.22,-13.4,z),(.012,8.3,.025),'joint','corner joints')
    for lev in range(5):
        z=.2+lev*4
        slab=C.box('Office occupied floor',(0,0,z-.09),(33.36,33.36,.18),'floor','floors',0)
        C.box('Corner projection floor',(11.5,-17.15,z-.09),(11.1,1.10,.18),'floor','floors',0)
        if lev:stair_cut(slab,0,6.0,3)
        if lev<4:stair(0,6,z,4,3,11,terminal=lev==3)
        for xx in (-12,-7,8,13):
            for yy in (-12,-5,2,11):desk(xx,yy,z)
        # Offices retain an open central corridor; partitions include passable doors.
        for xx in (-4.5,4.5):
            p=C.Face((xx,0,0),(0,1,0),(1 if xx<0 else -1,0,0),f'partition {lev} {xx}')
            ph=[hole('Office suite access '+str(u),u,z,1.3,2.5) for u in (-10,-2,12)]
            p.wall('Office corridor wall',-16,16,z,z+3.7,holes=ph,role='interior',depth=.12)
            for h in ph:glazed_door(p,h['id'],h['u'],h['z'],h['w'],h['h'],'bronze')
        C.qa_room_light('Office occupied floor',(0,-3,z+3.5),1500,12)
        C.qa_room_light('Side offices',(-10,7,z+3.5),650,8)
    C.box('Office roof plate',(0,0,20.29),(34,34,.22),'roof','roof',0)
    C.box('Corner projection roof',(11.5,-17.15,20.29),(11.4,1.1,.22),'roof','roof',0)
    for f in faces(w,d):
        f.wall('Roof parapet',-17,17,20.4,21.05,role='brick',depth=.30)
        f.part('Roof coping',0,.10,21.12,34.14,.46,.14,'trim','parapet')
    C.box('Plant house',(0,0,21.65),(10.4,13.2,2.5),'bronze','plant house')
    C.box('Plant house roof',(0,0,22.98),(10.7,13.5,.18),'roof','plant house cap')
    for xx in (-5.25,5.25):
        for sign in (-1,1):
            for j in range(18):C.box('Plant louvre',(xx,sign*9.1,20.6+j*.125),(.12,5,.075),'bronze','plant screens')
    for sign in (-1,1):
        for j in range(18):C.box('Plant end louvre',(0,sign*11.65,20.6+j*.125),(10.6,.12,.075),'bronze','plant screens')
        for xx in (-5.25,5.25):
            C.box('Side screen base rail',(xx,sign*9.1,20.49),(.18,5.2,.18),'bronze','plant screen structure')
            for yy in (6.6,9.1,11.65):
                C.box('Screen seated foot',(xx,sign*yy,20.45),(.32,.32,.10),'trim','plant screen supports')
                C.box('Screen vertical post',(xx,sign*yy,21.55),(.14,.14,2.3),'bronze','plant screen structure')
        C.box('End screen base rail',(0,sign*11.65,20.49),(10.6,.18,.18),'bronze','plant screen structure')
        for xx in (-2.625,0,2.625):
            C.box('Screen seated foot',(xx,sign*11.65,20.45),(.32,.32,.10),'trim','plant screen supports')
            C.box('Screen vertical post',(xx,sign*11.65,21.55),(.14,.14,2.3),'bronze','plant screen structure')
        hvac(0,sign*8.8,20.4,3,1.8)
    for yy in (-10,-3,4,11):hvac(8.3,yy,20.4,2.3,1.6)
    C.rod('Roof exhaust',(1,1,23.07),(1,1,23.8),.22,'trim','roof exhaust',20)
    C.CONTACTS.append(dict(name='Fixed five-storey office',occupied_storeys=5,plant_house='unoccupied rooftop mechanical enclosure',stair_arrivals=[4.2,8.2,12.2,16.2]))

def glass_guard(name,a,b,z):
    C.beam(name+' top',(a[0],a[1],z+1.05),(b[0],b[1],z+1.05),.05,.05,'hardware','terrace guards')
    C.beam(name+' base',(a[0],a[1],z+.10),(b[0],b[1],z+.10),.05,.05,'hardware','terrace guards')
    length=math.dist(a,b);n=max(1,math.ceil(length/1.1))
    for j in range(n+1):
        x=a[0]+(b[0]-a[0])*j/n;y=a[1]+(b[1]-a[1])*j/n
        C.box(name+' post',(x,y,z+.55),(.045,.045,1.10),'hardware','terrace guards')
    for j in range(n):
        aa=(a[0]+(b[0]-a[0])*(j+.03)/n,a[1]+(b[1]-a[1])*(j+.03)/n)
        bb=(a[0]+(b[0]-a[0])*(j+.97)/n,a[1]+(b[1]-a[1])*(j+.97)/n)
        C.beam(name+' pane',(aa[0],aa[1],z+.55),(bb[0],bb[1],z+.55),.014,.86,'glass','terrace guards')

def gable_room(cx,y0,y1,half,z,eave,ridge,label,front_glass=True):
    # Both roof slopes terminate on the actual eaves; no buried flat plate above rooms.
    for sign in (-1,1):
        C.solid_surface(label+' pitched roof',[(cx,y0-.16,ridge),(cx+sign*(half+.14),y0-.16,eave-.08),
            (cx+sign*(half+.14),y1+.16,eave-.08),(cx,y1+.16,ridge)],.14,'roof',label+' roof')
        for j in range(max(1,round((y1-y0)/.45))+1):
            yy=y0+j*(y1-y0)/max(1,round((y1-y0)/.45))
            C.beam(label+' standing seam',(cx,yy,ridge+.015),(cx+sign*(half+.14),yy,eave-.065),.022,.03,'roof',label+' roof seams')
        f=C.Face((cx+sign*half,(y0+y1)/2,0),(0,1,0),(-sign,0,0),label+' side '+str(sign))
        hs=[hole(label+' side window '+str(u),u,z+.8,1.6,1.0) for u in (-2,1.0)] if y1-y0>6 else []
        f.wall(label+' side wall',-(y1-y0)/2,(y1-y0)/2,z,eave,holes=hs,role='hardware',depth=.16)
        for h in hs:f.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=2,frame='hardware',depth=.16)
    front=C.Face((cx,y0,0),(1,0,0),(0,1,0),label+' front')
    if front_glass:
        # Full-depth gable opening bounded by timber jambs and rafters, with interior depth.
        for xx in (-half,half):front.part(label+' timber jamb',xx,.10,(z+eave)/2,.18,.35,eave-z,'timber',label+' frame')
        front.window(label+' glazed terrace doors',0,z+.02,half*2-.18,eave-z-.06,cols=4,rows=1,frame='hardware',sill=False,depth=.16)
        front.panel(label+' triangular optical pane',[(-half+.14,eave-.04),(half-.14,eave-.04),(0,ridge-.18)],.16,.17,'glass',label+' gable glazing')
        for sign in (-1,1):C.beam(label+' timber gable fascia',front.p(sign*half,-.06,eave),front.p(0,-.06,ridge-.03),.21,.30,'timber',label+' frame')
        for xx in (-half/2,0,half/2):
            zz=ridge-.16-abs(xx)/half*(ridge-eave)
            C.beam(label+' gable mullion',front.p(xx,.10,eave-.04),front.p(xx,.10,zz),.05,.08,'hardware',label+' gable glazing')
        for xx in (-.12,.12):C.rod(label+' terrace door pull',front.p(xx,.015,z+.95),front.p(xx,.015,z+1.45),.019,'hardware',label+' hardware')
    else:
        hs=[hole(label+' service door',0,z,1.05,1.95)]
        front.wall(label+' front carrier',-half,half,z,eave,holes=hs,role='roof',depth=.16)
        front.door(label+' service door',0,z,1.05,1.95,role='hardware')
        front.panel(label+' front gable',[(-half,eave),(half,eave),(0,ridge-.12)],0,.16,'roof',label+' ends')
    rear=C.Face((cx,y1,0),(1,0,0),(0,-1,0),label+' rear')
    rh=[hole(label+' rear door',0,z,1.05,1.95)] if front_glass else [hole(label+' rear window',0,z+.6,1.6,1.1)]
    rear.wall(label+' rear carrier',-half,half,z,eave,holes=rh,role='roof',depth=.16)
    rear.panel(label+' rear gable',[(-half,eave),(half,eave),(0,ridge-.12)],0,.16,'roof',label+' ends')
    if front_glass:rear.door(rh[0]['id'],0,z,1.05,1.95,role='hardware')
    else:rear.window(rh[0]['id'],0,z+.6,1.6,1.1,cols=2,frame='hardware',depth=.16)

def peaks():
    W,D=33.6,22;floorzs=(.2,3.4,6.6,9.8)
    C.box('Row continuous foundation',(0,0,.1),(W,D,.2),'foundation','foundation',0)
    centers=[-14+5.6*i for i in range(6)]
    for lev,z in enumerate(floorzs):
        slab=C.box('Row connected floor '+str(lev),(0,0,z-.09),(W-.36,D-.36,.18),'floor','floors',0)
        if lev:
            for cx in centers:stair_cut(slab,cx,-1.5,2.2)
    for i,cx in enumerate(centers):
        role='pale';style='timber' if i in (2,4) else 'ribbed' if i in (1,5) else 'white'
        f=C.Face((cx,-11,0),(1,0,0),(0,1,0),'Home '+str(i)+' front')
        hs=[hole('Private front door',-1.7,.2,1.05,2.6),hole('Living window',.72,.65,2.8,2.0)]
        if i==5:hs=[hole('Private front door',-1.7,.2,1.05,2.6),hole('Corner glazed entrance',.75,.2,4.04,2.6)]
        for lev in (1,2):
            if style=='timber':hs.append(hole('Timber bay glass '+str(lev),.45,.2+lev*3.2+.52,3.25,2.15))
            elif i==5:hs.append(hole('Corner ribbon '+str(lev),.65,.2+lev*3.2+.52,4.24,2.05))
            else:hs.append(hole('Punched bedroom '+str(lev),.55,.2+lev*3.2+.68,1.7,1.72))
        f.wall('Home facade carrier',-2.8,2.8,.2,9.8,holes=hs,role=role,depth=.26)
        for h in hs:
            if 'glazed entrance' in h['id']:glazed_door(f,h['id'],h['u'],h['z'],h['w'],h['h'])
            elif 'door' in h['id']:f.door(h['id'],h['u'],h['z'],h['w'],h['h'],role='timber',panels=1)
            else:f.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=2,frame='hardware',depth=.26)
        # Timber door recess is bounded and never crosses the glazed opening.
        for u in (-2.35,-1.06):f.part('Door timber reveal',u,-.08,1.52,.12,.28,2.64,'timber','door reveals')
        f.part('Door canopy',-1.70,-.42,2.95,1.58,.95,.13,'hardware','door canopy')
        if style=='timber':
            # Source timber bay panel is a full cut carrier on the proud face.
            bh=[h for h in hs if h['z']>3]
            bf=C.Face(f.p(0,-.04,0),f.t,f.n,f.label+' timber facing')
            bf.wall('Timber projecting bay',-1.36,2.26,3.4,9.7,depth=.06,role='timber',holes=bh)
            for u in (-1.47,2.37):f.part('Dark bay frame',u,-.15,6.57,.22,.38,6.46,'hardware','projecting bays')
            for z in (3.40,9.70):f.part('Dark bay head',.45,-.15,z,4.06,.38,.22,'hardware','projecting bays')
            timber_joints(bf,-1.36,2.26,bh)
        if style=='ribbed':
            for j in range(35):
                u=-2.7+j*.16;intervals=[(3.4,9.78)]
                for h in hs:
                    if abs(u-h['u'])<h['w']/2+.04:
                        spans=[]
                        for a,b in intervals:
                            if a<h['z']:spans.append((a,min(b,h['z'])))
                            if b>h['z']+h['h']:spans.append((max(a,h['z']+h['h']),b))
                        intervals=spans
                for a,b in intervals:
                    if b>a:f.part('Pale vertical rib',u,-.04,(a+b)/2,.034,.09,b-a,'trim','vertical cladding')
        # Three continuous stairs serve the fourth-level room, through real floor cuts.
        for lev,z in enumerate(floorzs[:3]):stair(cx,-1.5,z,3.2,2.2,9,terminal=lev==2)
        for lev,z in enumerate(floorzs[:3]):
            C.qa_room_light('Home '+str(i)+' level '+str(lev),(cx,-5,z+2.8),180,3)
            desk(cx+.4,-7,z)
            C.box('Residential sofa',(cx-1.1,5,z+.42),(1.25,2.1,.72),'interior','residential programme')
            C.box('Kitchen counter',(cx+1.6,6,z+.5),(.62,2.8,.96),'timber','residential programme')
            C.box('Kitchen worktop',(cx+1.6,6,z+1.01),(.70,2.9,.06),'trim','residential programme')
        gable_room(cx,-8.1,2.0,2.53,9.8,12.0,14.05,'Front home '+str(i))
        C.qa_room_light('Gable room '+str(i),(cx,-4,12.0),160,2)
        desk(cx,-5,9.8)
        glass_guard('Private terrace front',(cx-2.73,-10.85),(cx+2.73,-10.85),9.8)
        for xx in (cx-2.73,cx+2.73):glass_guard('Terrace side',(xx,-10.85),(xx,-8.15),9.8)
        # Low front planter, with feet of door approaches reaching grade.
        C.box('Private door approach',(cx-1.70,-11.48,.1),(1.45,.95,.2),'foundation','front access')
        if i==5:
            C.box('Corner clear entrance approach',(cx+.75,-11.45,.10),(4.05,1.10,.20),'foundation','corner access')
        else:
            C.box('Front planting bed',(cx+.60,-11.70,.25),(2.9,.9,.5),'pale','front planters')
            C.box('Contained planting',(cx+.60,-11.70,.54),(2.62,.62,.22),'planting','front planters')
    for cx in [-16.8+5.6*i for i in range(1,6)]:
        C.box('Home dividing wall',(cx,0,5.0),(.18,21.8,9.6),'interior','party walls')
    # Complete rear and end elevations continue the source grammar, without background rows.
    for f in faces(W,D)[1:]:
        span=W if f.label=='rear' else D
        us=centers if f.label=='rear' else (-8,-3,3,8)
        hs=[hole(f'{f.label} dwelling window {lev} {u}',u,.8+lev*3.2,2.05,1.95) for lev in range(3) for u in us]
        if f.label=='right':
            hs=[hole('Corner ground sidelight',-9.3,.2,3.34,2.6)]
            for lev in (1,2):
                hs += [hole('Corner ribbon return '+str(lev),-9.3,.2+lev*3.2+.52,3.34,2.05),
                    hole('Side narrow window '+str(lev),-4.7,.2+lev*3.2+.68,.85,1.72),
                    hole('Side timber bay '+str(lev),.4,.2+lev*3.2+.52,3.25,2.15),
                    hole('Side rear window '+str(lev),6.5,.8+lev*3.2,2.05,1.95)]
            hs += [hole('Side ground window '+str(u),u,.8,2.05,1.95) for u in (.4,6.5)]
        if f.label=='rear':
            hs=[h for h in hs if h['z']>1]
            hs += [hole('Rear home door '+str(u),u,.2,1.05,2.45) for u in centers]
        f.wall(f.label+' white carrier',-span/2,span/2,.2,9.8,holes=hs,role='pale',depth=.26)
        for h in hs:
            if 'door' in h['id']:f.door(h['id'],h['u'],h['z'],h['w'],h['h'],role='timber')
            else:f.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=2,frame='hardware',depth=.26)
        if f.label=='right':
            bh=[h for h in hs if 'Side timber bay' in h['id']]
            bf=C.Face(f.p(0,-.04,0),f.t,f.n,f.label+' timber facing')
            bf.wall('Side timber bay carrier',-1.41,2.21,3.4,9.7,depth=.06,role='timber',holes=bh)
            for u in (-1.52,2.32):f.part('Side bay vertical frame',u,-.15,6.57,.22,.38,6.46,'hardware','projecting bays')
            for z in (3.40,9.70):f.part('Side bay head',.4,-.15,z,4.06,.38,.22,'hardware','projecting bays')
            timber_joints(bf,-1.41,2.21,bh)
            for j in range(25):
                u=-10.95+j*.16;intervals=[(3.4,9.78)]
                for h in hs:
                    if abs(u-h['u'])<h['w']/2+.04:
                        spans=[]
                        for a,b in intervals:
                            if a<h['z']:spans.append((a,min(b,h['z'])))
                            if b>h['z']+h['h']:spans.append((max(a,h['z']+h['h']),b))
                        intervals=spans
                for a,b in intervals:
                    if b>a:f.part('Corner return pale rib',u,-.04,(a+b)/2,.034,.09,b-a,'trim','vertical cladding')
            f.part('Corner ground lintel',-9.15,-.06,3.28,3.7,.25,.24,'hardware','corner framing')
        f.part('Row base course',0,-.035,.25,span,.10,.10,'hardware','base course')
    # Three physically enclosed rear service pavilions, as locked by the overhead source.
    for cx in (-8.4,0,8.4):gable_room(cx,5.3,10.5,2.2,9.8,11.8,13.2,'Rear pavilion '+str(cx),False)
    for f in faces(W,D)[1:]:
        span=W if f.label=='rear' else D
        f.part('Low roof parapet',0,.12,10.12,span,.26,.64,'pale','roof parapet')
        f.part('Low roof coping',0,.12,10.49,span+.08,.34,.10,'hardware','roof coping')
    C.CONTACTS.append(dict(name='Six complete front homes',ground_storeys=3,occupied_gabled_level=4,front_gables=6,rear_service_pavilions=3,terrace_floor=9.8))

def timber_joints(f,lo,hi,holes):
    """Physical board joints stay within the actual timber carrier and its openings."""
    for j in range(37):
        z=3.6+j*.16;intervals=[(lo,hi)]
        for h in holes:
            if h['z']-.03<z<h['z']+h['h']+.03:
                spans=[]
                for a,b in intervals:
                    if a<h['u']-h['w']/2:spans.append((a,min(b,h['u']-h['w']/2)))
                    if b>h['u']+h['w']/2:spans.append((max(a,h['u']+h['w']/2),b))
                intervals=spans
        for a,b in intervals:
            if b>a:f.part('Timber board joint',(a+b)/2,-.004,z,b-a,.012,.014,'joint','timber joints',0)

def warehouse():
    from warehouse import warehouse as construct
    construct(stair,stair_cut,desk)

def main():
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=list(SPECS),required=True);p.add_argument('--source-root',type=Path,required=True)
    p.add_argument('--output',required=True);p.add_argument('--version',type=int,default=1);p.add_argument('--resolution',type=int,default=1440);p.add_argument('--dry-run',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);m=manifest(a.kind,a.version)
    out=C.prepare_candidate(a,source_entry(a.kind,a.source_root),m,__file__,extra_scripts=[HERE/'plan.py',HERE/'warehouse.py'])
    if out is None:return
    palette=PALETTE.copy()
    if a.kind=='warehouse':palette.update(wall=(.58,.54,.43),joint=(.34,.33,.29),trim=(.32,.33,.30),roof=(.64,.65,.62),floor=(.46,.44,.39))
    cams=C.setup(palette,m['camera_roster'],a.resolution);C.bevel=lambda obj,width=.012,segments=1:None
    for obj in C.bpy.context.scene.objects:
        q=6 if a.kind=='warehouse' else 3
        if obj.type=='LIGHT':obj.location*=q;obj.data.energy*=q*q;obj.data.size*=q
        if obj.name=='QA ground - excluded':obj.scale*=8
    print('CONSTRUCTION_STARTED '+a.kind,flush=True)
    globals()[a.kind]()
    print('CONSTRUCTION_FINISHED '+a.kind,flush=True)
    cleanup();C.deliver(out,m,cams)

if __name__=='__main__':main()
