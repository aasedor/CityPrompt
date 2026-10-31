"""Source-specific wartime cottage; roof ratios come from the locked pixels."""
import clay_core as C
from tools.housing_teaching.contracts import landing_bridge
from construction import (
    PALETTE, bed, flight_x, gable_end, gable_roof_x, kitchen, opening,
    sash, siding, sofa, table, wall,
)


def specification(make_cameras):
    details=[('facade_close',(4,-9,3),(1.55,-2.75,1.7),42),
        ('architecture_close',(-8,-6,6),(-3.9,0,3.9),40),
        ('glass_close',(-2.18,-4.5,1.8),(-1.8,-1.2,1.35),40),
        ('entry_contacts',(2,-5.5,1.5),(0,-3.1,.50),38),
        ('stair_flight',(-1,-2.20,2.0),(-1,0,1.90),16),
        ('attic_stair',(2.8,-.9,4.45),(-1.2,0,3),24),
        ('roof_chimney',(4,5,8),(2.6,1.6,5.0),42)]
    return dict(candidate='wartime-victory-house-clay',
        dimensions_m=dict(width=8.34,depth=7.20,height=6.12),floors=1.5,
        cameras=make_cameras(8.34,7.20,6.12,details),palette=PALETTE,
        roof_contract='One steep side-gabled roof, ridge along X; complete end gables, shallow eaves, source-position brick chimney and seated cap. No dormers.',
        programme_contract='Living/dining/kitchen on the .53m main floor, stair through a real floor opening to an occupied 3.05m attic. Rear bath enclosure and furniture are inferred.',
        contact_contract=['Foundation bears at Z=0','Three native entry treads meet threshold','All facade and gable windows cut full carriers','Loft stair reaches its landing and guarded floor opening','Chimney crosses roof and closes at cap'],
        measurement_notes=[
            'Body width7.8m, depth5.5m inferred from front and near-top source proportions. Prompt8.6m depth is rejected as inconsistent with pixels.',
            'Main floor.53m, wall eave3.18m, wall ridge5.55m, roof skin ridge5.68m; chimney6.12m. Source side windows and gable loft windows retained.',
            'Roof rise/depth produces a steep pitch; modest one-and-a-half-storey form differs from the existing low-roof bungalow.',
            'All four compatible original board views enrolled. Top is near-vertical high aerial, not a surveyed orthographic plan.',
            'Source front and end upper sashes have a3x2 six-light grid above a single lower light. Rear door glazing differs from opaque front door.',
            'Metric sizes, internal layout, concealed roof structure and stair are architectural inferences. No historic property or accessibility certification.',
            'No rectangular site pad or landscaping exported. Green QA context is excluded from the GLB.',
        ],entrances=[dict(id='front',door_center=[0,-2.75,1.55],threshold_z=.53,
            lowest_tread_top_m=.1766666667,step_foot=[0,-3.60,0],clear_width_m=1.48,
            approach_direction=[0,-1],scaleWithPlot=False),
            dict(id='rear',door_center=[.35,2.75,1.55],threshold_z=.53,
            lowest_tread_top_m=.1766666667,step_foot=[.35,3.60,0],clear_width_m=1.35,
            approach_direction=[0,1],scaleWithPlot=False)])


def construct():
    C.box('Native house foundation',(0,0,.24),(7.8,5.5,.48),'foundation','native foundation',0)
    C.box('Main timber floor',(0,0,.49),(7.3,5.0,.08),'floor','occupied floors',0)
    front=C.Face((0,-2.75,0),(1,0,0),(0,1,0),'front')
    rear=C.Face((0,2.75,0),(1,0,0),(0,-1,0),'rear')
    left=C.Face((-3.9,0,0),(0,1,0),(1,0,0),'left gable')
    right=C.Face((3.9,0,0),(0,1,0),(-1,0,0),'right gable')
    for face,door_u in ((front,0),(rear,.35)):
        holes=[opening(face.label+' left sash',-2.12,1.18,.94,1.43),
               opening(face.label+' right sash',2.12,1.18,.94,1.43),
               opening(face.label+' door',door_u,.53,.96,2.04)]
        wall(face,face.label+' complete wall',-3.9,3.9,.48,3.18,holes)
        siding(face,face.label,-3.9,3.9,.48,3.18,holes)
        for op in holes[:2]:sash(face,op)
        if face==front:
            face.door('Front dark green door',door_u,.53,.96,2.04,panels=3,panel_cols=2,inset=.11)
        else:
            face.door('Rear door lower leaf',door_u,.53,.96,2.04,panels=0,inset=.11)
            # The source has a glazed upper rear leaf: cut the leaf, then seat a pane.
            leaf=next(o for o in C.objects() if o.name.startswith('Rear door lower leaf recessed leaf'))
            face.cut(leaf,'Rear door glazed upper cut',door_u,1.46,.55,.83,.30)
            face.part('Rear door upper optical pane',door_u,.17,1.875,.54,.009,.82,'glass','rear door glazing',0)
            face.part('Rear door lower panel',door_u,.10,.96,.63,.025,.67,'timber','rear door glazing',0)
        width=1.48 if face==front else 1.35
        for i,(depth,height) in enumerate(((.82,.53/3),(.55,.53*2/3),(.28,.53))):
            face.part(face.label+f' native tread{i+1}',door_u,-depth/2-.03,height/2,width,depth,height,'foundation','native steps',0)
    for face in (left,right):
        lower=opening(face.label+' main sash',0,1.18,.94,1.43)
        upper=opening(face.label+' attic sash',0,3.64,.78,1.12)
        wall(face,face.label+' rectangular wall',-2.75,2.75,.48,3.18,[lower])
        siding(face,face.label,-2.75,2.75,.48,3.18,[lower])
        gable_end(face,face.label+' closed triangle',2.75,3.18,5.55,[upper])
        sash(face,lower);sash(face,upper)
    for x in (-3.9,3.9):
        for y in (-2.75,2.75):C.box('Seated corner trim',(x,y,1.83),(.10,.10,2.7),'trim','corner trim',0)
    gable_roof_x('Victory steep side gable',-3.9,3.9,2.75,3.18,5.55)
    # Actual attic floor opening, not a stair disappearing through a solid slab.
    loft=C.box('Attic occupied floor',(0,0,3.0),(7.3,5.0,.10),'floor','occupied floors',0)
    C.cut_box(loft,'Loft stairwell opening',(-1.0,0,3.0),(4.46,1.12,.65))
    f=flight_x('Main to attic',-3.1,0,1.0,.53,3.05,.28)
    end=-3.1+f['run']
    bridge=landing_bridge(end,1.23)
    C.box('Attic connected arrival landing',(bridge['center_x'],0,3.0),(bridge['length'],1.08,.10),'floor','stair landing',0)
    for y in (-.57,.57):C.railing('Loft opening guard',(-3.23,y,3.05),(1.23,y,3.05),height=.93,role='floor')
    C.railing('Loft low-end guard',(-3.23,-.57,3.05),(-3.23,.57,3.05),height=.93,role='floor')
    bed('Attic sleeping bay',2.45,.25,3.05)
    sofa('Main sitting room',-2.1,-1.55,.53)
    table('Main dining',2.1,-1.20,.53)
    kitchen('Rear small kitchen',-2.1,2.12,.53)
    # A small rear bathroom is a declared plan inference, with open doorway.
    bath=C.Face((0,1.05,0),(1,0,0),(0,1,0),'bath partition')
    wall(bath,'Bathroom privacy partition',1.1,3.64,.53,2.83,[opening('Bathroom doorway',1.65,.53,.78,1.95)],'interior',.10)
    C.box('Bathroom basin',(2.8,1.65,1.28),(.54,.44,.18),'white','bathroom')
    C.box('Bathroom supported vanity',(2.8,1.65,.9),(.52,.42,.58),'white','bathroom')
    C.box('Brick chimney continuous stack',(2.68,1.55,3.07),(.42,.48,6.10),'brick','source chimney',0)
    C.box('Chimney seated cap',(2.68,1.55,6.10),(.49,.55,.04),'foundation','source chimney',0)
    C.qa_room_light('Victory main',(.5,-1.1,2.68),75,2.5)
    C.qa_room_light('Victory attic',(.7,0,4.25),85,1.2)
    C.CONTACTS.extend([dict(id='foundation',base_z=0,full_footprint_m=[7.8,5.5]),
        dict(id='attic_stair',lower_z=.53,upper_z=3.05,landing_start_x=end,
             landing_bridge=bridge,physical_floor_cut=True,assumption='inferred interior, not historic plan'),
        dict(id='chimney',penetrates_roof=True,cap_top_z=6.12)])
