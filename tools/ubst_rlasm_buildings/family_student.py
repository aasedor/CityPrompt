"""Three-storey brick U residence measured from all three generated sources."""
import clay_core as C
from assemblies import hole, faces, bed, desk, sofa, bathroom, shrub, garden_chair
from common import wall, open_door, stair, stair_hole, base_manifest, camera_set
from build import PALETTE as BASE

SLUG='ubst-student-courtyard'
PALETTE=dict(BASE,wall=(.48,.255,.16),brick=(.48,.255,.16),pale=(.50,.55,.41),roof=(.29,.30,.29))
FLOORS=(.15,4.05,7.95)
ROOF=12.05


def cameras():
    roster=camera_set(30,24,12.35,[
      ('facade_close',(11.5,-25,8),(11.75,-12,6),52),
      ('architecture_close',(2,-10,2.1),(0,5,2),32),
      ('glass_close',(-2.2,2.7,2),(-3.6,7.4,1.8),32),
      ('roof_contact',(21,-10,19),(15,-7,12),42),
      ('side_projection',(25,-15,8),(15,-4,6),42),
      ('interior',(-1.7,5.6,1.8),(-3.6,8.8,1.4),24),
      ('stairs',(6.8,5.45,1.8),(6.8,10,4),20),
      ('upper_landing',(7.4,11.4,5.65),(5,8.3,5),24),
      ('upper_stairs',(6.8,5.45,5.7),(6.8,10,8),20),
      ('bedroom',(-10.4,-10.8,5.65),(-13,-9.1,4.9),22),
      ('bathroom',(-1.4,10.3,9.55),(-3.1,11,8.8),22),
      ('courtyard',(0,-10,2),(0,5,5),24),
      ('study_room',(-5.5,5.7,1.8),(-6.4,8.3,1.3),24)])
    matched={
      'front':dict(location=(0,-31,2),target=(0,0,2),lens=18,shift_y=.13),
      'front_corner':dict(location=(13,-48,18),target=(0,0,5),lens=30),
      'aerial':dict(location=(17,-53,30),target=(0,0,5),lens=35)}
    for view in roster:
        view.update(matched.get(view['name'],{}))
    return roster


def window_rows(prefix,centres):
    return [hole(f'{prefix} {j} level{k}',u,z+.60,1.60,2.60)
            for k,z in enumerate(FLOORS) for j,u in enumerate(centres)]


def sage(face,centres,width=1.72):
    for u in centres:
        for z in FLOORS[:-1]:
            face.part('Sage spandrel panel',u,-.018,z+3.85,width,.036,1.3,'pale','source identity',0)


def sash_rails(face,holes):
    for h in holes:
        face.part('Low horizontal sash rail',h['u'],.14,h['z']+.48,h['w']-.08,.09,.045,'trim','openings')


def construct():
    # U-shaped footprint; court is open to grade and has no buried podium.
    for x in (-11.75,11.75):
        C.box('Wing ground slab',(x,0,.075),(6.5,24,.15),'foundation','foundation')
    C.box('Rear connecting slab',(0,8.5,.075),(17,7,.15),'foundation','foundation')
    C.box('Ground-level courtyard',(0,-3.5,.075),(17,17,.15),'pale','court')
    C.box('Street pavement',(0,-13,.025),(31,2,.05),'foundation','court')
    for x in (-11.75,11.75):
        ff=faces(6.5,24,cx=x,label=f'Wing {x} ')
        front=window_rows('Wing front',(-1.4,1.4))
        wall(ff[0],'Brick end',6.5,.15,ROOF,front)
        sash_rails(ff[0],front)
        sage(ff[0],(0,),4.56)
        for z in FLOORS:
            ff[0].part('Sage paired-window central pier',0,-.018,z+1.9,1.2,.036,2.6,'pale','source identity',0)
        # Outer long side has eight columns. The court side's eight columns span only the open court.
        outer=ff[3 if x<0 else 1]
        outer_cs=[-10.5+3*i for i in range(8)]
        wall(outer,'Long outer brick wall',23.46,.15,ROOF,window_rows('Outer room window',outer_cs));sage(outer,outer_cs)
        sash_rails(outer,window_rows('Outer room window',outer_cs))
        inner=C.Face((x+(3.25 if x<0 else -3.25),-3.5,0),(0,1,0),(1 if x>0 else -1,0,0),'Court side')
        cs=[-7.4375+2.125*i for i in range(8)]
        wall(inner,'Inner court brick wall',17,.15,ROOF,window_rows('Court corridor window',cs));sage(inner,cs)
        sash_rails(inner,window_rows('Court corridor window',cs))
        # Six rooms along each wing; inner corridor links to rear common stair.
        hx=x+(1.55 if x<0 else -1.55)
        hall=C.Face((hx,0,0),(0,1,0),(-1 if x<0 else 1,0,0),'Bedroom corridor')
        for z in FLOORS:
            hs=[hole('Open room doorway',-10.2+3*i,z,.95,2.35) for i in range(7)]
            hall.wall('Student room enclosure',-11.73,9.3,z,z+3.68,.12,'interior',hs)
            for i in range(7):
                yy=-10.25+i*3
                bx=x+(-.6 if x<0 else .6)
                bed(bx,yy,z)
                if i<6:
                    C.box('Student room dividing wall',(x+(-.8 if x<0 else .8),yy+1.50,z+1.84),(4.35,.12,3.68),'interior','rooms')
                C.qa_room_light('Room light',(bx,yy,z+3.35),95,1.4)
            for yy in (-8,-2,4,10): C.qa_room_light('Corridor light',(x+(2.35 if x<0 else -2.35),yy,z+3.4),100,1.5)
    rear=C.Face((0,12,0),(-1,0,0),(0,-1,0),'Complete rear elevation')
    wall(rear,'Full rear wall',29.46,.15,ROOF,window_rows('Rear window',[-13.5+3*i for i in range(10)]))
    sash_rails(rear,window_rows('Rear window',[-13.5+3*i for i in range(10)]))
    front=C.Face((0,5,0),(1,0,0),(0,1,0),'Court lounge facade')
    hs=[hole('Central lounge entrance',0,.15,2.2,3.2),hole('Left lounge glazing',-4.5,.35,6,3),hole('Right lounge glazing',4.5,.35,6,3)]
    hs += [hole('Rear wing upper room',u,z+.6,1.6,2.6) for z in FLOORS[1:] for u in (-6,-2,2,6)]
    wall(front,'Brick rear court facade',17,.15,ROOF,hs);sage(front,(-6,-2,2,6))
    sash_rails(front,[h for h in hs if h['id']=='Rear wing upper room'])
    for cx in (-4.5,4.5):
        for offset in (-1.5,0,1.5):
            front.part('Lounge vertical mullion',cx+offset,.14,1.85,.055,.09,3,'trim','openings')
        front.part('Lounge transom rail',cx,.14,2.65,5.92,.09,.055,'trim','openings')
    C.box('Lounge entrance canopy',(0,4.65,3.70),(15.5,.8,.16),'trim','entry')
    floor_outline=[(-14.73,-11.73),(-8.77,-11.73),(-8.77,5.27),(8.77,5.27),
                   (8.77,-11.73),(14.73,-11.73),(14.73,11.73),(-14.73,11.73)]
    for z in FLOORS[1:]:
        slab=C.prism('Continuous U-shaped occupied floor',floor_outline,'z',z-.22,z,'floor','floors')
        stair_hole(slab,6.8,5.7,z,front_guard=z==FLOORS[-1])
    for a,b in zip(FLOORS,FLOORS[1:]): stair('Common stair',6.8,5.7,a,b)
    for z in FLOORS:
        # Rear west common rooms; circulation to east stair and wing corridors stays open.
        sofa(-3.8,8.9,z);desk(-6.8,7.3,z)
        sanitary=C.Face((0,9.6,0),(1,0,0),(0,1,0),'Shared sanitary enclosure')
        sanitary.wall('Sanitary front',-4.6,-.3,z,z+3.68,.12,'interior',[hole('Open bathroom entry',-1.25,z,.9,2.35)])
        C.box('Sanitary side',(-4.6,10.65,z+1.84),(.12,2.1,3.68),'interior','sanitary')
        C.box('Sanitary other side',(-.3,10.65,z+1.84),(.12,2.1,3.68),'interior','sanitary')
        bathroom(-3.2,11.2,z)
        C.qa_room_light('Sanitary ceiling light',(-2.6,10.7,z+3.4),100,1.2)
        for xx in (-6,-2,3,6.8): C.qa_room_light('Rear occupied space',(xx,8.5,z+3.45),180,2)
    # Continuous U-roof: independent slab modules, only perimeter parapets; no wall across roof junctions.
    C.prism('Continuous inset U-shaped roof',floor_outline,'z',ROOF-.20,ROOF,'roof','roof')
    outline=[(-15,-12),(-8.5,-12),(-8.5,5),(8.5,5),(8.5,-12),(15,-12),(15,12),(-15,12)]
    for i,a in enumerate(outline):
        b=outline[(i+1)%len(outline)]
        C.beam('Seated continuous parapet',(*a,ROOF+.12),(*b,ROOF+.12),.18,.24,'wall','roof')
        C.beam('Dark parapet coping',(*a,ROOF+.265),(*b,ROOF+.265),.26,.05,'trim','roof')
    for xx,yy in [(-12,-6),(-12,8),(12,-6),(12,8),(0,10)]:
        C.box('Roof service curb',(xx,yy,ROOF+.16),(.7,.7,.32),'trim','roof services')
        C.box('Seated service cap',(xx,yy,ROOF+.33),(.82,.82,.08),'roof','roof services')
    for x in (-5.5,5.5):
        for y in (-8.5,-3,2):
            C.box('Grounded garden bed',(x,y,.23),(3.7,3,.16),'planting','landscape')
            for dx in (-1.25,0,1.25):shrub(x+dx,y,.31,.45)
        C.box('Concrete bench',(x,-5.5,.40),(2.5,.55,.50),'foundation','landscape')
    for x in (-7,7):
        for i in range(4):
            xx=x+i*.35
            C.rod('Bike stand',(xx,-11.3,.15),(xx,-11.3,.95),.025,'hardware','landscape')
            C.beam('Bike rail',(xx,-11.3,.95),(xx,-10.5,.95),.045,.045,'hardware','landscape')
            C.rod('Bike support',(xx,-10.5,.15),(xx,-10.5,.95),.025,'hardware','landscape')


def manifest(version):
    return base_manifest(SLUG,version,cameras(),dict(dimensions_m=dict(width=30,depth=24,height=12.42),observed_storeys=3,
        source_measurements=['Front W1478px/H600px: H/W .406; 30m frontage gives about12.2m totalheight.',
          'Wing ends2columns x3rows; both visible long elevations8columns x3rows; rear4uppercolumns x2rows.',
          'Wing width6.5m, court17m clear, upperwindows1.6x2.6m, floorpitch3.9m.'],
        hidden_assumptions=['24m depth and7m rearwing authored, not surveyed.','Hidden rear, rooms and circulation inferred.']),
        dict(storeys=3,uses=['Student residence','Shared study and lounge'],legal_approval=False,
             description='Ground-level open court, two bedroom wings, rear common spaces and continuous stairs.'),
        dict(topology='One continuous U-shaped flat roof',parapets='Outer and courtyard perimeter only',authority='Three locked generated views'))
