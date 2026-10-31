"""Original Postmodern library, measured from the locked three-view design.

Source-specific composition only. Metric dimensions and unshown elevations are
explicit inferences; the third source image is high aerial, not a survey plan.
"""
import math

import bpy
import clay_core as C


def specification(make_cameras):
    details = [
        ('facade_close', (3, -13, 2.5), (3, -5.8, 2.2), 37),
        ('architecture_close', (9, -14, 7.3), (3, -6.2, 4.3), 40),
        ('glass_close', (-8.4, -10.5, 1.7), (-8.4, -6, 1.7), 38),
        ('portico_contact', (6, -10, 4.1), (5.5, -6.3, 3.7), 50),
        ('library_programme', (3, -3, 1.75), (3, 2, 1.2), 35),
        ('entrance_low', (3, -10, 1.4), (3, -5.5, 1.5), 32),
    ]
    return dict(
        archetype_id='postmodern_neighbourhood_library',
        variant_id='broken_pediment_reading_room',
        candidate='postmodern-neighbourhood-library-clay',
        title='Postmodern neighbourhood library', style='Postmodernism',
        reference='postmodern-library-original-reference-board.png',
        references={r: 'library-' + r + '.png' for r in ('front', 'oblique', 'top')},
        provenance_file='library-source-provenance.json',
        dimensions_m=dict(width=20, depth=12, height=5.85), floors=1,
        teaching=dict(
            description='Postmodern architecture mixes references to earlier buildings with playful shapes and colour. It often makes familiar features, such as a classical pediment, surprising or exaggerated so that buildings can communicate ideas as well as serve a use.',
            features=['Broken classical pediment', 'Circular windows and strong colour',
                      'Deliberate asymmetry'],
            main_idea='Use history, symbolism and play to give a building a readable identity.',
            source='https://historicengland.org.uk/images-books/publications/iha-post-modern-architecture/'),
        cameras=make_cameras(20, 12, 5.85, details),
        palette=dict(wall=(.72, .68, .58), trim=(.028, .105, .27),
                     salmon=(.60, .29, .22), roof=(.58, .56, .50),
                     timber=(.30, .18, .08), interior=(.76, .73, .65),
                     glass=(.60, .70, .72), hardware=(.16, .17, .18),
                     floor=(.44, .42, .37), bookgreen=(.12, .25, .17),
                     bookorange=(.60, .32, .12), bookcream=(.76, .67, .47)),
        measurement_notes=[
            'Source pixels govern: portico centre x=+3m, not requested +2m; apex5.85m, not requested6.5m.',
            'Main hall x[-4,10],y[-5,5]; left wing x[-10,-4],y[-7,2]. Rear setback is visible in the high aerial source.',
            'One occupied storey. Flat closed roofs, main coping4.4m and lower wing coping3.8m; pediment is a portico screen, not a hall roof.',
            'Two true circular front apertures, clear diameter2m, outer blue rings2.3m. No invented cross mullions.',
            'Main front small window, recessed glazed double entry with sidelights, far-right reading window. Two right-side windows.',
            'Two salmon piers support a continuous blue canopy and two solid pediment halves with an open0.5m vertical apex slot.',
            'Third source view is high aerial, not true orthographic; metric dimensions are inferred. Rear/left openings and shelf plan are explicit architectural inferences.',
            'Programme: actual shelves, coloured book spines, reading tables/chairs, circulation desk, clear entry aisle and wing passage.',
            'Only a small entrance apron is included; no enclosing rectangular site pad or QA ground is exported.',
        ])


def circular_window(face, owner, name, u, z, radius=1.0):
    """Through-wall circular opening, closed annular frame and inset optical disc."""
    sides = 64
    # Leave 35mm between the structural cut and the blue inner reveal. Matching
    # radii create coincident opaque surfaces after triangulated GLB export.
    carrier_radius = radius + .035
    circle = [(u + carrier_radius * math.cos(i * math.tau / sides),
               z + carrier_radius * math.sin(i * math.tau / sides)) for i in range(sides)]
    cutter = face.panel(name + ' full circular cutter', circle, -.3, .8,
                        'wall', 'construction cutter')
    bpy.context.view_layer.objects.active = owner
    mod = owner.modifiers.new(name + ' circular carrier cut', 'BOOLEAN')
    mod.operation = 'DIFFERENCE'; mod.solver = 'EXACT'; mod.object = cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)
    C.remove_cutter(cutter); C.normalise(owner.data)
    # Four rings: front/back, outer/inner. All reveals and back surfaces close.
    verts = [face.p(u + r * math.cos(i * math.tau / sides), d,
                    z + r * math.sin(i * math.tau / sides))
             for d, r in [(-.055, 1.15), (-.055, radius),
                          (.20, 1.15), (.20, radius)] for i in range(sides)]
    faces = []
    for i in range(sides):
        j = (i + 1) % sides
        faces.extend([(i, j, sides+j, sides+i),
                      (2*sides+i, 3*sides+i, 3*sides+j, 2*sides+j),
                      (i, 2*sides+i, 2*sides+j, j),
                      (sides+i, sides+j, 3*sides+j, 3*sides+i)])
    C.mesh(name + ' deep annular blue frame', verts, faces, 'trim', 'round windows')
    glass = [(u + .99 * radius * math.cos(i * math.tau / sides),
              z + .99 * radius * math.sin(i * math.tau / sides)) for i in range(sides)]
    face.panel(name + ' inset optical disc', glass, .218, .227, 'glass', 'round windows')
    C.OPENINGS.append(dict(id=name, face=face.label, u=u, z=z-radius,
        width=radius*2, height=radius*2, kind='circular window', clear_wall_cut=True,
        carrier_depth_m=.30, frame_inset_m=.075, pane_inset_m=.2225,
        face_origin=list(face.o), face_tangent=list(face.t), face_inward=list(face.n),
        occupied_space='enclosed reading room with shelving beyond circular reveal',
        aperture_shape='circle', radius_m=radius, structural_cut_radius_m=carrier_radius,
        reveal_radial_clearance_m=.035))


def bookcase(name, x, y, width=1.8):
    floor = .15; h = 2.05; depth = .42
    for dx in (-width/2+.035, width/2-.035):
        C.box(name+' side', (x+dx, y, floor+h/2), (.07, depth, h), 'timber', 'library shelving')
    C.box(name+' back', (x, y+.185, floor+h/2), (width-.10, .045, h), 'timber', 'library shelving')
    for level in range(6):
        shelf_top = floor + .07 + level*.39
        C.box(name+' shelf', (x, y, shelf_top-.025), (width-.07, depth, .05), 'timber', 'library shelving')
        if level == 5:
            continue
        for i in range(14):
            bw = (width-.22)/14
            bh = .24 + .018*((i+level)%5)
            role = ('bookgreen', 'bookorange', 'bookcream', 'trim')[(i+level)%4]
            C.box(name+' book', (x-(width-.22)/2+bw*(i+.5), y-.055, shelf_top+bh/2),
                  (bw-.012, .26, bh), role, 'library books', 0)


def construct(face_wall, hole, table, chair):
    footprint = [(-10,-7),(-4,-7),(-4,-5),(10,-5),(10,5),(-4,5),(-4,2),(-10,2)]
    C.prism('Native jogged library floor', footprint, 'z', 0, .15, 'floor', 'foundation')
    front = C.Face((0,-5,0),(1,0,0),(0,1,0),'main front')
    wingfront = C.Face((0,-7,0),(1,0,0),(0,1,0),'round-window wing front')
    right = C.Face((10,0,0),(0,1,0),(-1,0,0),'right side')
    left = C.Face((-10,0,0),(0,1,0),(1,0,0),'left inferred side')
    rear = C.Face((0,5,0),(1,0,0),(0,-1,0),'main inferred rear')
    wingrear = C.Face((0,2,0),(1,0,0),(0,-1,0),'wing inferred rear')
    entry_holes = [hole('Front small reading window',-1.8,.55,1.7,2.6),
                   hole('Double entry and sidelights',3,.15,3.8,3.0),
                   hole('Front large reading window',8,.55,3,2.6)]
    face_wall(front,'Ivory main front',-4,10,.15,4.25,entry_holes)
    # Add explicit sidelights, two central leaves and an upper transom inside
    # the actual carrier void. There is no opaque panel behind this glazing.
    for u in (2.22,3,3.78):
        front.part('Blue double-entry leaf stile',u,.124,1.65,.045,.09,2.87,'trim','entrance')
    front.part('Blue entry transom',3,.124,2.72,3.67,.09,.05,'trim','entrance')
    for u in (2.88,3.12):
        p=front.p(u,.055,1.45)
        C.rod('Entrance pull handle',(p[0],p[1],1.23),(p[0],p[1],1.67),.019,'hardware','entrance')
    wing_owner=wingfront.wall('Ivory circle-window wall',-10,-4,.15,3.64,depth=.30)
    for u in (-8.4,-5.6):circular_window(wingfront,wing_owner,'Round reading window '+str(u),u,1.65)
    face_wall(right,'Main right wall',-5,5,.15,4.25,
              [hole('Right reading window A',-2.5,.55,2.6,2.6),hole('Right reading window B',2.5,.55,2.6,2.6)])
    face_wall(left,'Lower left wall',-6.7,1.7,.15,3.64,
              [hole('Inferred left window '+str(y),y,.55,1.6,2.3) for y in (-4.9,-1.7,.9)])
    face_wall(wingrear,'Lower wing rear',-10,-4,.15,3.64,
              [hole('Inferred wing rear A',-8.4,.55,1.7,2.3),hole('Inferred wing rear B',-5.7,.55,1.7,2.3)])
    face_wall(rear,'Main rear',-4,10,.15,4.25,
              [hole('Inferred rear reading window A',-1.4,.55,2.6,2.6),
               hole('Inferred rear service door',3,.15,1.1,2.5,door=True),
               hole('Inferred rear reading window B',7.3,.55,3.4,2.6)])
    # Shared-wall void links the two occupied wings; no glazed divider blocks it.
    inner=C.Face((-4,0,0),(0,1,0),(1,0,0),'wing shared wall')
    passage=hole('Open reading-wing passage',-1.5,.15,2.6,2.8)
    inner.wall('Shared wall with circulation passage',-5,2,.15,3.64,depth=.22,role='interior',holes=[passage])
    C.OPENINGS.append(dict(id=passage['id'],face=inner.label,u=-1.5,z=.15,width=2.6,height=2.8,
        kind='open internal passage',clear_wall_cut=True,carrier_depth_m=.22,frame_inset_m=None,pane_inset_m=None,
        face_origin=list(inner.o),face_tangent=list(inner.t),face_inward=list(inner.n),occupied_space='connected library rooms'))
    face_wall(inner,'Exposed main rear return',2,5,.15,4.25,[hole('Inferred rear return window',3.5,.55,1.7,2.6)])
    C.box('Exposed main upper step wall',(-3.85,-1.5,3.945),(.30,7,.61),'wall','envelope',0)
    C.box('Wing projecting side return',(-4.15,-6,1.895),(.30,2,3.49),'wall','envelope',0)
    # Closed roof slabs provide a continuous ceiling and weathering surface.
    C.box('Main flat roof slab',(3,0,4.18),(14,10,.14),'roof','weathering roof',0)
    C.box('Wing flat roof slab',(-7,-2.5,3.58),(6,9,.16),'roof','weathering roof',0)
    for name,x,y,w,d,z in [('Main front',3,-5,14,.28,4.26),('Main rear',3,5,14,.28,4.26),
                         ('Main right',10,0,.28,10,4.26),('Main step',-4,0,.28,10,4.26),
                         ('Wing front',-7,-7,6,.28,3.66),('Wing rear',-7,2,6,.28,3.66),
                         ('Wing left',-10,-2.5,.28,9,3.66),('Wing short return',-4,-6,.28,2,3.66)]:
        C.box(name+' blue coping',(x,y,z),(w,d,.28),'trim','roof edge')
    # Pink plinth follows exterior walls only and stays below glazing.
    for name,x,y,w,d in [('main front',3,-5,14,.06),('main rear',3,5,14,.06),
                        ('right',10,0,.06,10),('wing front',-7,-7,6,.06),
                        ('wing rear',-7,2,6,.06),('wing left',-10,-2.5,.06,9),
                        ('wing return',-4,-6,.06,2),('rear step',-4,3.5,.06,3)]:
        if name in ('main front','main rear'):
            # Explicit gaps at the doorways: no opaque band across the leaves.
            half = 1.9 if name=='main front' else .55
            for lo,hi in [(-4,3-half),(3+half,10)]:
                C.box(name+' pink plinth',((lo+hi)/2,y,.235),(hi-lo,d,.17),'salmon','plinth',0)
        else:C.box(name+' pink plinth',(x,y,.235),(w,d,.17),'salmon','plinth',0)
    # Portico is a supported projecting canopy, not a second roof storey.
    C.box('Small entry apron',(3,-5.9,.075),(6.4,2.1,.15),'floor','entrance',0)
    C.box('Rear service threshold',(3,5.2,.075),(1.4,.65,.15),'floor','entrance',0)
    for x in (.5,5.5):
        C.box('Salmon portico square pier',(x,-6.15,1.875),(.85,.7,3.45),'salmon','portico')
        C.box('Portico pier base',(x,-6.15,.25),(1.0,.84,.2),'salmon','portico')
    C.box('Continuous blue canopy',(3,-5.85,3.85),(6.4,1.9,.5),'trim','portico')
    for side in (-1,1):
        points=[(3+side*3.05,4.10),(3+side*.25,4.10),(3+side*.25,5.85)]
        C.prism('Solid split pediment half',points,'y',-6.66,-6.30,'salmon','pediment')
    # Useful occupied depth. Furnishings sit on the native 150mm floor.
    for y in (.8,3.3):
        for x in (-1.5,1.8,5.1):bookcase('Main book stack',x,y)
    for x in (-8.5,-5.8):bookcase('Wing book stack',x,-.25,width=1.65)
    table('Left reading table',-7.2,-4.25,z=.15,width=2,depth=.85)
    for x in (-7.8,-6.6):chair('Wing reading chair',x,-3.55,z=.15)
    table('Right reading table',8.0,-2.3,z=.15,width=1.8,depth=.85)
    for x in (7.4,8.6):chair('Hall reading chair',x,-1.6,z=.15)
    C.box('Circulation desk base',(-.9,-2.55,.65),(2.0,.65,1.0),'timber','library desk')
    C.box('Circulation desk counter',(-.9,-2.55,1.18),(2.16,.78,.07),'interior','library desk')
    C.box('Book return tray',(-1.3,-2.55,1.26),(.48,.34,.09),'trim','library desk')
    for loc in [(-7,-3,3.15),(0,-1,3.5),(6,-1,3.5),(3,3,3.5)]:C.qa_room_light('Library reading room',loc,240,4)
    C.CONTACTS.extend([
        dict(name='Portico',piers_base_m=.15,piers_top_m=3.6,canopy_bottom_m=3.6,canopy_top_m=4.1,pediment_base_m=4.1),
        dict(name='Broken pediment',apex_m=5.85,open_slot_width_m=.5,slot_has_no_filler=True),
        dict(name='Flat roof',closed_slabs=True,stepped_wall_closed=True),
        dict(name='Main entry',floor_m=.15,landing_top_m=.15,entry_clear_route_m=1.5),
    ])
