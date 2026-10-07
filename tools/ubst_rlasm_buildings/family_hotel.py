"""Measured three-storey garden hotel with covered planted loggias."""
import clay_core as C
from assemblies import hole, faces, bed, desk, sofa, bathroom, shrub, garden_chair, seated_guard, flat_roof
from common import wall, open_door, stair, stair_hole, base_manifest, camera_set
from build import PALETTE as BASE

SLUG='ubst-garden-hotel'
PALETTE=dict(BASE,wall=(.69,.65,.56),pale=(.70,.67,.60),timber=(.41,.27,.14),trim=(.13,.115,.08),roof=(.34,.35,.34))
FLOORS=(.15,4.90,8.70)
ROOF=12.45


def cameras():
    roster=camera_set(24,16,12.70,[
      ('facade_close',(2,-27,8),(0,-5.3,7),52),
      ('architecture_close',(2,-16,2.5),(0,-8,2.5),35),
      ('glass_close',(-9.3,-9.5,2),(-9.7,-6,1.8),35),
      ('roof_contact',(18,-5,19),(9,-4.3,12.5),42),
      ('side_projection',(24,-12,10),(10.5,0,8),42),
      ('interior',(0,-6.8,1.8),(-5,-.2,1.5),24),
      ('stairs',(9,-1.1,1.8),(9,5,4.4),20),
      ('upper_landing',(7.7,7.1,6.5),(8.5,1.7,5.6),24),
      ('upper_stairs',(9,-.30,6.5),(9,5,8.4),20),
      ('bedroom',(-1.15,-.8,10.3),(-2,-2.4,9.5),22),
      ('bathroom',(-1.7,5.1,10.3),(-3.1,6.9,9.5),22),
      ('terrace',(7,-6.2,6.5),(-7,-6.3,5.9),28),
      ('top_loggia',(7.5,-4.35,10.3),(-7,-4.3,9.7),28)])
    matched={
      'front':dict(location=(0,-42,2.2),target=(0,0,2.2),lens=32,shift_y=.12),
      'front_corner':dict(location=(20,-44,22),target=(0,0,5),lens=38),
      'aerial':dict(location=(22,-47,32),target=(0,0,5),lens=38)}
    for view in roster:
        view.update(matched.get(view['name'],{}))
    return roster


def guest_facade(width,y,floor,height,cap):
    face=C.Face((0,y,0),(1,0,0),(0,1,0),'Recessed guestroom glazing')
    pitch=(width-.8)/6
    centres=[(i-2.5)*pitch for i in range(6)]
    apertures=[hole('Guestroom combined aperture',x,floor+.05,pitch-.42,height-.8) for x in centres]
    face.wall('Recessed stone glazing carrier',-width/2+.27,width/2-.27,floor,floor+height-cap,depth=.25,holes=apertures)
    for h in apertures:
        dw=.92; ww=h['w']-dw
        face.window('Guestroom optical window',h['u']-dw/2,h['z'],ww,h['h'],cols=1,inset=.15,depth=.25,sill=False)
        open_door(face,hole('Terrace entrance',h['u']+ww/2,h['z'],dw,h['h']))
    return centres,pitch


def construct():
    C.box('Grounded hotel foundation',(0,0,.075),(24,16,.15),'foundation','foundation')
    C.box('Entrance forecourt',(0,-9.2,.075),(24.6,2.4,.15),'pale','entry')
    # Ground level: six front structural bays with a double-width central lobby aperture.
    ff=faces(24,16,label='Ground ')
    hs=[hole('Left restaurant glazing',-9.7,.25,3.2,3.55),hole('Left café glazing',-5.8,.25,3.2,3.55),
        hole('Lobby aperture',0,.15,7.0,3.65),hole('Right library glazing',5.8,.25,3.2,3.55),hole('Right lounge glazing',9.7,.25,3.2,3.55)]
    ff[0].wall('Ground stone front',-12,12,.15,FLOORS[1]-.30,.30,'wall',hs)
    for h in hs:
        if h['id']=='Lobby aperture':
            for x in (-2.35,2.35):ff[0].window('Lobby sidelights',x,.15,2.3,3.65,cols=1,depth=.30)
            open_door(ff[0],hole('Right paired hotel entrance',.60,.15,1.2,3.65))
            reverse=C.Face((0,-8,0),(-1,0,0),(0,1,0),'Mirrored lobby entrance')
            open_door(reverse,hole('Left paired hotel entrance',.60,.15,1.2,3.65))
        else:ff[0].window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=2,depth=.30)
    for side in (1,3):wall(ff[side],'Ground side stone',15.4,.15,4.60,[hole('Ground side window',u,.6,2.5,3.15) for u in (-5,0,5)],depth=.30)
    wall(ff[2],'Complete ground rear',23.4,.15,4.60,[hole('Rear service entrance',-8.8,.15,1.2,2.8)]+[hole('Rear lounge window',u,.8,2.4,2.65) for u in (-4,0,4,8)],depth=.30)
    C.box('Entrance canopy',(0,-8.65,4.02),(8.1,1.5,.22),'trim','entry')
    # Slabs include the forward planter strip; upper rooms sit behind separate stone loggia frames.
    for i,(z,width,front_edge,frame_y,glass_y,ceiling) in enumerate([
        (4.90,22.4,-8,-6.5,-5.2,8.70),
        (8.70,21.0,-6.5,-4.85,-3.55,ROOF)]):
        slab_width=24 if i==0 else 22.4
        slab_front=front_edge-.275
        slab=C.box('Closed planted terrace slab',(0,(8+slab_front)/2,z-.15),(slab_width,8-slab_front,.30),'wall','floors')
        stair_hole(slab,9,-.2,z,length=7.2,width=1.2,front_guard=i==1)
        # The slab edge and loggia head below jointly form the front band.
        # A separate fascia would duplicate both of their exterior faces.
        cap=.30 if i==0 else .20
        centres,pitch=guest_facade(width,glass_y,z,ceiling-z,cap)
        for x in [-width/2+.20]+[(j-2)*pitch for j in range(5)]+[width/2-.20]:
            C.box('Stone loggia column',(x,frame_y,(z+ceiling-.72)/2),(.40,.55,ceiling-.72-z),'wall','frame')
        C.box('Spanning stone loggia head',(0,frame_y,ceiling-(.72+cap)/2),(width,.55,.72-cap),'wall','frame')
        C.box('Closed wood loggia soffit',(0,(frame_y+glass_y)/2,ceiling-.735),(width-.4,glass_y-frame_y,.03),'timber','soffit')
        for sign in (-1,1):
            # Butt the side carrier behind the entire post/head envelope.
            # Sharing their exterior plane over any depth produces visible z-fighting.
            side_start=frame_y+.275
            side=C.Face((sign*width/2,(side_start+8)/2,0),(0,1,0),(-sign,0,0),'Stepped side')
            d=8-side_start
            wall(side,'Upper side stone',d,z,ceiling-(.30 if i==0 else .20),[hole('Side guestroom window',u,z+.45,1.8,ceiling-z-1.20) for u in (-d*.30,0,d*.30)])
        rear=C.Face((0,8,0),(-1,0,0),(0,-1,0),'Upper rear')
        wall(rear,'Rear guestroom wall',width-.54,z,ceiling-(.30 if i==0 else .20),[hole('Rear window',x,z+.6,1.5,2.30) for x in (-8,-4,0,4,8)])
        # Continuous planted strip sits on terrace floor, with a walkable loggia behind it.
        C.box('Terrace planter base',(0,front_edge+.5,z+.12),(slab_width-.6,.62,.24),'wall','planting')
        C.box('Terrace planting soil',(0,front_edge+.5,z+.25),(slab_width-.8,.48,.04),'planting','planting')
        for j in range(28):shrub(-slab_width/2+.8+j*(slab_width-1.6)/27,front_edge+.5,z+.27,.27)
        seated_guard('Front terrace guard',(-slab_width/2+.2,front_edge+.13,z),(slab_width/2-.2,front_edge+.13,z),height=1.02)
        for sign in (-1,1):
            seated_guard('Terrace return guard',(sign*(slab_width/2-.2),front_edge+.13,z),(sign*(slab_width/2-.2),frame_y,z))
        # Enclosed bedrooms with openings to a cross-corridor; each front bay has a terrace exit.
        for j,x in enumerate(centres):
            bed(x,glass_y+1.45,z)
            if j<5:C.box('Guestroom dividing wall',(x+pitch/2,(glass_y-.45)/2,(z+ceiling-.30)/2),(.12,-.45-glass_y,ceiling-.30-z),'interior','rooms')
            C.qa_room_light('Guest room light',(x,glass_y+1.1,ceiling-.40),130,1.8)
        hallway=C.Face((0,-.45,0),(1,0,0),(0,-1,0),'Guest room entry wall')
        hallway.wall('Room hallway enclosure',-width/2+.27,width/2-.27,z,ceiling-.30,.12,'interior',
                     [hole('Open guestroom entry',x-.7,z,.85,2.35) for x in centres])
        bathroom_front=C.Face((0,4.5,0),(1,0,0),(0,1,0),'Rear bathrooms')
        bathroom_front.wall('Sanitary front',-5,-.5,z,ceiling-.30,.12,'interior',[hole('Bathroom entry',-1.35,z,.95,2.35)])
        for x in (-5,-.5):C.box('Sanitary side',(x,6.1,(z+ceiling-.30)/2),(.12,3.2,ceiling-.30-z),'interior','sanitary')
        bathroom(-3.2,7.0,z);C.qa_room_light('Bathroom light',(-2.5,6,ceiling-.4),140,1.8)
        for xx in (-7,0,6,9):C.qa_room_light('Corridor light',(xx,2.5,ceiling-.4),170,2)
    # The main roof extends to the top loggia frame, not just to recessed glass.
    C.box('Closed structural hotel roof',(0,1.4375,ROOF-.10),(21,13.125,.20),'wall','roof')
    C.box('Inset roof membrane',(0,1.4375,ROOF+.004),(20.46,12.585,.008),'roof','roof')
    for yy in (-5.035,7.91):
        C.box('Front and rear roof parapet',(0,yy,ROOF+.09),(21,.18,.18),'wall','roof')
        C.box('Front and rear coping',(0,yy,ROOF+.205),(21.08,.26,.05),'trim','roof')
    for xx in (-10.41,10.41):
        C.box('Butted side parapet',(xx,1.4375,ROOF+.09),(.18,12.765,.18),'wall','roof')
        C.box('Butted side coping',(xx,1.4375,ROOF+.205),(.26,12.685,.05),'trim','roof')
    for x in (-4,4):
        C.box('Roof vent curb',(x,4,ROOF+.18),(.9,.8,.36),'trim','roof services')
        C.box('Roof vent seated lid',(x,4,ROOF+.39),(1.03,.93,.06),'roof','roof services')
    for a,b in zip(FLOORS,FLOORS[1:]):stair('Hotel continuous stair',9,-.2,a,b,length=7.2)
    for x in (-8,-4,4):sofa(x,-1,.15)
    desk(-8,5,.15)
    C.box('Grounded reception counter',(0,4.8,.70),(4.5,.9,1.1),'timber','lobby')
    for x in (-9,-5):
        garden_chair(x,-9.2,.15)
        C.box('Cafe table top',(x+1,-9.3,.88),(.70,.7,.08),'timber','cafe')
        C.box('Cafe table foot',(x+1,-9.3,.19),(.45,.45,.08),'trim','cafe')
        C.box('Cafe table stem',(x+1,-9.3,.535),(.08,.08,.61),'trim','cafe')
    C.box('Ground front planter',(7.5,-8.9,.47),(7,.65,.64),'wall','planting')
    for x in (5,6,7,8,9,10):shrub(x,-8.9,.79,.28)
    for xx in (-8,-3,3,9):
        for y in (-4,3):C.qa_room_light('Ground lobby illumination',(xx,y,4.35),220,2.5)


def manifest(version):
    return base_manifest(SLUG,version,cameras(),dict(dimensions_m=dict(width=24,depth=16,height=12.9),observed_storeys=3,
        source_measurements=['Front-derived height12.4m abovegrade; occupied terraces4.75m and8.55m abovegrade.',
          'Groundwidth24m; middle22.4m; top21m. Six framed guest bays per upperfloor, three sidewindowcolumns.',
          'Upper glazed planes recess behind stone post/head frames; main roof covers top loggia.'],
        hidden_assumptions=['16m depth authored, not surveyed.','Exact setbacks, rear, room interiors and circulation inferred.']),
        dict(storeys=3,front_guestrooms=12,uses=['Hotel','Café','Lounge'],legal_approval=False,
             description='Active lobby and café, two room levels with covered garden loggias and internal stairs.'),
        dict(topology='Three stepped stages; two covered loggias; single complete top roof',authority='Three locked source photographs'))
