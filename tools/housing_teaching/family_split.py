"""Exact cross-gabled side-split source; rear and occupied plan are inferred."""
import clay_core as C
from tools.housing_teaching.contracts import split_level_datums
from construction import (
    PALETTE, bed, flight_x, gable_end, gable_roof_x, gable_roof_y, kitchen,
    opening, siding, simple_window, sofa, table, wall,
)

LEVELS = split_level_datums()


def specification(make_cameras):
    details = [
        ('facade_close',(-7,-11,3.1),(-3.4,-4,1.6),43),
        ('architecture_close',(-1.2,-8,6),(.45,-.3,3.8),36),
        ('glass_close',(-3.9,-5.6,1.8),(-4.1,-1,1.5),35),
        ('entry_contacts',(-1.3,-7,1.25),(-.4,-4.35,.43),42),
        ('stair_up',(-.7,-.25,1.8),(.75,-1.6,1.65),17),
        ('stair_up_axial',(3,-1.6,3.75),(.5,-1.6,1.3),19),
        ('upper_arrival',(3.4,-.2,3.75),(1.65,-1.6,2.30),24),
        ('stair_down',(-.7,1.55,1.75),(-.1,.3,.4),23),
        ('lower_arrival',(2.0,1.2,1.45),(.25,.3,.35),29),
        ('occupied_lower',(3.3,-1.4,1.35),(4.7,1.9,.8),19),
        ('occupied_upper',(2.7,0,3.45),(4.85,0,2.9),16),
    ]
    return dict(candidate='postwar-side-split-house-clay',
        dimensions_m=dict(width=14.54,depth=9.12,height=5.7225),floors='three staggered levels',
        cameras=make_cameras(14.54,9.12,5.7225,details),palette=PALETTE,
        roof_contract='Low left wing has ridge along X. Raised right wing has front/rear gables, ridge along Y. Low roof enters sealed shared high wall. Two seated roof vents; no dormer or garage.',
        programme_contract='Original inferred plan: living floor .53m, lower recreation .10m, raised sleeping floor2.30m; two connected stair flights through real slab and wall cuts. Unequal offsets preserve occupied room clearances above native zero. Not a measured historical plan or code-certified house.',
        contact_contract=['Foundation bottom Z0; QA green ground excluded',
            'Three exterior treads meet .53m thresholds',
            'Picture window and two upper/two lower front windows cut full carriers',
            'Both stair arrivals positively bear on destination floors',
            'Raised-floor opening has floor-seated end posts and guards',
            'Cross roof planes seat on complete gables and shared wall'],
        measurement_notes=[
            'Body14m wide; low wing6m deep, raised wing8m deep (1.333 depth ratio from source roof-edge runs about267px versus360px). Known front faces remain registered atY-4; rear outline steps atY2/Y4. Exact metres remain inferred.',
            'Source pixels override initial prompt: raised right roof is front-gabled, with ridge alongY; low left ridge runsX. Corrected near-vertical high-aerial supplies plan orientation, not surveyed orthography.',
            'Five compatible views enrolled: corrected front/oblique/top and earlier front/oblique. Prior top roof orientation is rejected. Both rear-left proposals conflict with the compatible one-window left end and are preserved as rejected evidence.',
            'Unseen rear/right elevations continue the compatible wall/opening grammar as declared architectural inference. No rejected rear window pattern is copied.',
            'Source front has one three-part picture window, a green glazed-upper door, two paired upper windows and two short paired lower windows in brick.',
            'Interior, stair geometry and unequal floor offsets are conceptual inferences. Lower clear height2.10m; living2.52m; upper at least2.15m at eaves. No engineering, accessibility or fire-compliance claim.',
            'Fixed native scale only; no large rectangular pad, plot, driveway or landscape in GLB.',
        ],entrances=[dict(id=label,door_center=[-.4,y,1.55],threshold_z=.53,
            lowest_tread_top_m=.53/3,step_foot=[-.4,y+direction*.85,0],
            clear_width_m=1.32,approach_direction=[0,direction],scaleWithPlot=False)
            for label,y,direction in [('front',-4,-1),('rear',2,1)]])


def picture_window(face,op):
    """Wide fixed centre and narrow side lights, never three equal bays."""
    simple_window(face,op,cols=1)
    for side in (-1,1):
        u=op['u']+side*op['w']*.32
        face.part(op['id']+' narrow side-light mullion',u,.122,op['z']+op['h']/2,
                  .055,.10,op['h']-.13,'trim','source picture window',0)


def steps(face):
    for i,(depth,height) in enumerate(((.82,.53/3),(.55,.53*2/3),(.28,.53))):
        face.part(face.label+f' native tread{i+1}',-.4,-depth/2-.03,height/2,
                  1.32,depth,height,'foundation','native steps',0)


def construct():
    d=LEVELS
    # Foundation belongs to the building footprint. The low-side stairwell cuts
    # both the living slab and this raised support, not only a decorative floor.
    lowbase=C.box('Living wing foundation',(-3.325,-1,.24),(7.35,6,.48),
                  'foundation','native foundation',0)
    lowfloor=C.box('Living occupied floor',(-3.325,-1,.49),(6.85,5.5,.08),
                   'floor','occupied floors',0)
    down=d['down'];up=d['up']
    a,b=down['opening_min_x'],down['opening_max_x']
    for obj in (lowbase,lowfloor):
        C.cut_box(obj,'Actual descending stair opening',((a+b)/2,d['down_y'],.34),
                  (b-a,1.16,1.2))
    # Cover the tolerance between the saw-cut edge and descending first riser.
    # This is a floor-seated departure nose, not an unsupported step across a slot.
    C.box('Down stair continuous departure',((a+d['start_x'])/2,d['down_y'],.48),
          (d['start_x']-a+.04,1.12,.10),'floor','stair departure bearing',0)
    C.box('Raised wing ground bearing',(3.675,0,.05),(6.65,8,.10),
          'foundation','native foundation',0)
    upper=C.box('Raised sleeping occupied floor',(3.675,0,2.25),(6.15,7.5,.10),
                'floor','occupied floors',0)
    C.cut_box(upper,'Actual upper stair opening',((.25+up['cut_edge'])/2,-1.6,2.25),
              (up['cut_edge']-.25,1.16,.8))
    # Low wing front/back, including source-position openings.
    front=C.Face((0,-4,0),(1,0,0),(0,1,0),'front low wing')
    rear=C.Face((0,2,0),(1,0,0),(0,-1,0),'inferred rear low wing')
    for face in (front,rear):
        picture=opening(face.label+' picture window',-3.9,1.03,3.8,1.45)
        door=opening(face.label+' doorway',-.4,.53,1.04,2.04)
        holes=[picture,door]
        wall(face,face.label+' wall',-7,.35,.48,3.05,holes)
        siding(face,face.label,-7,.35,.48,3.05,holes)
        picture_window(face,picture)
        face.door(face.label+' green leaf',-.4,.53,1.04,2.04,panels=0,inset=.11)
        leaf=next(o for o in C.objects() if o.name.startswith(face.label+' green leaf recessed leaf'))
        face.cut(leaf,face.label+' glazed-upper leaf cut',-.4,1.35,.38,.92,.30)
        face.part(face.label+' door optical pane',-.4,.17,1.81,.37,.009,.91,
                  'glass','source door glazing',0)
        face.part(face.label+' lower door panel',-.4,.10,.91,.69,.025,.55,
                  'timber','source door panels',0)
        steps(face)
    left=C.Face((-7,-1,0),(0,1,0),(1,0,0),'source left gable')
    end=opening('Single source left-end window',0,1.15,.90,1.35)
    wall(left,'Complete low gable wall',-3,3,.48,3.05,[end])
    siding(left,'Low gable',-3,3,.48,3.05,[end])
    gable_end(left,'Closed low end gable',3,3.05,4.18)
    simple_window(left,end)
    # Raised front and rear gables. Rear is explicitly inferred, not an enrolled
    # incompatible generated rear proposal. The front owns the source hierarchy.
    for y,inward,label in ((-4,(0,1,0),'source front raised'),(4,(0,-1,0),'inferred rear raised')):
        face=C.Face((3.675,y,0),(1,0,0),inward,label)
        windows=[opening(label+f' upper{i}',u,2.88,1.45,1.08) for i,u in enumerate((-1.55,1.55))]
        windows += [opening(label+f' lower{i}',u,.40,1.45,.62) for i,u in enumerate((-1.55,1.55))]
        wall(face,label+' foundation',-3.325,3.325,.10,.28,role='foundation')
        wall(face,label+' continuous brick base',-3.325,3.325,.28,1.55,windows,role='brick')
        wall(face,label+' siding carrier',-3.325,3.325,1.55,4.45,windows)
        siding(face,label,-3.325,3.325,1.55,4.45,windows)
        gable_end(face,label+' closed gable',3.325,4.45,5.55)
        for op in windows:simple_window(face,op)
    right=C.Face((7,0,0),(0,1,0),(-1,0,0),'inferred right side')
    windows=[opening(f'Inferred right upper{i}',u,2.88,1.2,1.08) for i,u in enumerate((-1.8,1.8))]
    windows += [opening(f'Inferred right lower{i}',u,.40,1.2,.62) for i,u in enumerate((-1.8,1.8))]
    wall(right,'Right foundation',-4,4,.10,.28,role='foundation')
    wall(right,'Right brick base',-4,4,.28,1.55,windows,role='brick')
    wall(right,'Right upper carrier',-4,4,1.55,4.45,windows)
    siding(right,'Right upper',-4,4,1.55,4.45,windows)
    for op in windows:simple_window(right,op)
    # Shared wall seals the cross-roof connection, with two real circulation cuts.
    shared=C.Face((.35,0,0),(0,1,0),(1,0,0),'shared staggered-level wall')
    passages=[opening('Upper stair passage',-1.6,.53,1.18,2.88),
              opening('Lower stair passage',d['down_y'],.10,1.18,2.09)]
    rear_side_windows=[opening('Inferred exposed wing upper',3,2.88,.9,1.08),
                       opening('Inferred exposed wing lower',3,.40,.9,.62)]
    # End carriers already own the 0.25m front/rear corner returns. Excluding
    # those two strips prevents coincident exterior faces and black seam bands.
    wall(shared,'Complete shared wall',-3.75,3.75,.10,4.45,passages+rear_side_windows)
    brick_skin=C.Face((.324,0,0),(0,1,0),(1,0,0),'inferred exposed wing skin')
    wall(brick_skin,'Exposed wing brick continuation',2,4,.28,1.55,
         rear_side_windows,role='brick',depth=.026)
    wall(brick_skin,'Exposed wing foundation continuation',2,4,.10,.28,
         role='foundation',depth=.026)
    siding(shared,'Exposed rear wing siding',2,4,1.55,4.45,rear_side_windows)
    for op in rear_side_windows:simple_window(shared,op)
    # Exposed clapboard only above the low roof, not a rectangular intersecting
    # siding sheet through it. Shared opaque wall below remains the envelope.
    z=3.05+.125
    while z<4.45-.03:
        span=3 if z>=4.18 else 3*(z-3.05)/(4.18-3.05)
        # Below the low ridge, only the two exposed edge strips are visible.
        ranges=[(-4,-4+span),(2-span,2)] if z<4.18 else [(-4,2)]
        for lo,hi in ranges:
            if hi-lo>.02:shared.part('Exposed shared-wall clapboard',(lo+hi)/2,-.008,z,
                hi-lo,.018,.018,'wall','source cross-roof siding',0)
        z+=.125
    gable_roof_x('Low living side gable',-7,.42,3,3.05,4.18,.22,center_y=-1)
    gable_roof_y('Raised sleeping front gable',3.675,-4,4,3.325,4.45,5.55,.22)
    # Two modest vents sit on, and overlap, their roof skins.
    for name,x,y,z in [('Low roof vent',-1.1,.1,4.18+.13-1.1*(1.13/3)),
                       ('Raised roof vent',4.1,-1.1,5.55+.13-.425*(1.10/3.325))]:
        C.box(name+' curb',(x,y,z+.04),(.25,.25,.14),'roof','seated roof vent',0)
        C.box(name+' cap',(x,y,z+.12),(.30,.30,.035),'foundation','seated roof vent',0)
    for name,y,target in [('up',-1.6,d['upper']),('down',d['down_y'],d['lower'])]:
        f=flight_x('Living to '+name,d['start_x'],y,1.0,d['living'],target)
        bridge=d[name]['bridge']
        C.box(name+' connected arrival',(bridge['center_x'],y,target-.05),
              (bridge['length'],1.12,.10),'floor','continuous stair arrival',0)
        C.CONTACTS.append(dict(id=name+'_stair',lower_or_start_z=d['living'],target_z=target,
            steps=f['steps'],rise=f['rise'],run=f['run'],landing_bridge=bridge,
            physical_floor_and_wall_cuts=True,plan='declared unequal-offset inference'))
    for y in (-2.19,-1.01):
        C.railing('Raised floor opening guard',(.60,y,2.30),(up['cut_edge'],y,2.30),
                  height=.92,role='floor')
        for x in (.60,up['cut_edge']):
            C.box('Floor-seated guard endpoint',(x,y,2.76),(.055,.055,.92),
                  'floor','guard floor anchorage',0)
    sofa('Living sitting area',-4.1,-1.6,.53)
    table('Living dining area',-5.0,.55,.53)
    kitchen('Living rear kitchen',-2.3,1.40,.53,2.8)
    bed('Raised bedroom one',4.85,-1.5,2.30)
    bed('Raised bedroom two',4.85,1.5,2.30)
    sofa('Lower recreation room',4.65,2.1,.10)
    C.box('Recreation low table',(4.65,.75,.51),(1.1,.55,.08),
          'floor','lower recreation programme')
    for x in (4.25,5.05):
        for y in (.55,.95):C.box('Recreation table foot',(x,y,.285),(.045,.045,.37),
                                'floor','lower recreation programme',0)
    C.qa_room_light('Split living',(-3.3,0,2.65),145,2.4)
    C.qa_room_light('Split upper',(3.8,0,4.14),140,1.8)
    C.qa_room_light('Split lower',(3.5,0,1.98),100,1.7)
    C.CONTACTS.extend([dict(id='foundation',base_z=0,stepped_footprint_m=dict(width=14,low_depth=6,raised_depth=8)),
        dict(id='floors',lower_z=.10,living_z=.53,upper_z=2.30,
             lower_clear_height_m=2.10,living_clear_height_m=2.52,upper_eave_clear_height_m=2.15)])
