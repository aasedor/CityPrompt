"""Bauhaus-inspired workshop, measured from its own locked generated pixels."""
import clay_core as C


def specification(make_cameras):
    details = [
        ('facade_close',(3,-12,3.7),(3,-3.1,2.0),37),
        ('architecture_close',(-13,-10,9),(-6,-3,5.7),43),
        ('glass_close',(-7.1,-8.3,1.9),(-7.1,-3.1,1.6),40),
        ('stair_contact',(-2.6,1.3,2.8),(.2,-.8,1.8),25),
        ('workshop_programme',(-6.2,-4.7,1.8),(-6.2,1.0,1.3),33),
        ('entrance_low',(4,-7,1.4),(2.8,-2.7,1.4),37),
    ]
    return dict(archetype_id='bauhaus_design_workshop',variant_id='glazed_studio_low_wing',
        candidate='bauhaus-design-workshop-clay', title='Bauhaus-inspired design workshop',
        source_roles=('front','oblique','top','oblique_high'),
        dimensions_m=dict(width=20.7,depth=10,height=7.75),floors=2,
        teaching=dict(description='Bauhaus design connected art, craft and industrial production. Buildings often use clear volumes, steel-and-glass facades and spaces shaped around their functions.',
            features=['Two-storey glazed workshop','Lower white administration wing','Visible structure and working rooms'],
            main_idea='Bring design, making and modern construction together.',
            source='https://bauhaus-dessau.de/en/venues/bauhaus-building/'),
        cameras=make_cameras(20.8,10.1,7.75,details),
        palette=dict(wall=(.77,.75,.68),trim=(.045,.058,.061),roof=(.15,.16,.16),
            timber=(.40,.29,.17),interior=(.78,.74,.65),glass=(.61,.70,.70),
            hardware=(.13,.15,.15),floor=(.44,.43,.38),red=(.31,.045,.028),
            paper=(.84,.82,.73),model=(.66,.57,.40)),
        roof_contract='Two independent flat weathering decks and bounded parapets; taller studio plus lower right wing; no invented bridge or extra floor.',
        programme_contract='Two occupied design studios with model-making/drafting workstations, storage and a connected guarded return stair; low office wing connects through a real opening.',
        contact_contract=['Native foundation union, no site pad','Curtain apertures through all carriers','Recessed red main entry and landing','Stair stringers, landings and upper slab cut','Complete coping and roof decks'],
        measurement_notes=[
            'Main front has five equal curtain bays and two storeys; source front pixel proportions imply7.75m height for12m studio width, not requested7m.',
            'Main x[-10.35,1.65],y[-5,5]; low wing x[1.65,10.35],y[-3,5]. Metric scale and exact depth inferred from compatible high aerial.',
            'Main upper glass starts4.0m; horizontal black spandrel3.25–4.0m; upper floor3.55m; roof parapet7.75m.',
            'Low coping4.55m, red recessed door and three narrow horizontal front windows; requested3.8m was not followed by source pixels.',
            'Generated TRUE TOP is high aerial, not survey/orthographic. Generated REAR-LEFT repeats front; enrolled truthfully as oblique_high.',
            'Unshown rear/right aperture schedules and room/stair plan are explicit architectural inferences continuing the same functional grammar.',
            'No outside context planting/trees or enclosing base exported; only native floors and small entrance threshold.',
        ])


def window_wall(face,name,u0,u1,z0,z1,holes,role='wall'):
    face.wall(name,u0,u1,z0,z1,depth=.30,role=role,holes=holes)
    for item in holes:
        if item.get('door'):
            if item.get('flat'):
                flat_door(face,item)
            else:
                face.door(item['id'],item['u'],item['z'],item['w'],item['h'],
                          role=item.get('role','trim'),inset=item.get('inset',.19))
                C.OPENINGS[-1]['carrier_depth_m'] = .30
        elif item.get('passage'):
            C.OPENINGS.append(dict(id=item['id'],face=face.label,u=item['u'],z=item['z'],
                width=item['w'],height=item['h'],kind='open internal passage',clear_wall_cut=True,
                carrier_depth_m=.30,frame_inset_m=0,pane_inset_m=None,
                face_origin=list(face.o),face_tangent=list(face.t),face_inward=list(face.n),
                occupied_space='direct connection between low office and studio'))
        else:
            face.window(item['id'],item['u'],item['z'],item['w'],item['h'],
                cols=item.get('cols',1),rows=item.get('rows',1),frame='trim',sill=False,depth=.30)


def opening(name,u,z,w,h,**extra):
    return dict(id=name,u=u,z=z,w=w,h=h,**extra)


def flat_door(face,item):
    name,u,z,w,h=item['id'],item['u'],item['z'],item['w'],item['h']
    inset=.35
    for side in (-1,1):face.part(name+' recessed frame',u+side*(w/2-.035),inset,z+h/2,.07,.13,h,'trim','source entry')
    face.part(name+' recessed head',u,inset,z+h-.035,w,.13,.07,'trim','source entry')
    face.part(name+' flat red leaf',u,inset+.035,z+h/2,w-.13,.065,h-.06,'red','source entry')
    a=face.p(u-.27,inset-.035,z+.63);b=face.p(u-.27,inset-.035,z+2.23)
    C.rod(name+' long black pull',a,b,.021,'hardware','source entry')
    for zz in (z+.68,z+2.18):
        C.beam(name+' pull fixing',face.p(u-.27,inset-.035,zz),face.p(u-.27,inset+.01,zz),.026,.026,'hardware','source entry')
    C.OPENINGS.append(dict(id=name,face=face.label,u=u,z=z,width=w,height=h,kind='flat recessed opaque door',
        clear_wall_cut=True,carrier_depth_m=.30,frame_inset_m=inset,pane_inset_m=None,
        face_origin=list(face.o),face_tangent=list(face.t),face_inward=list(face.n),
        occupied_space='direct office entrance with an unscaled flat red source-specific leaf'))


def workbench(name,x,y,floor=.18,drafting=False):
    z=floor+.84
    C.box(name+' supported worktop',(x,y,z),(1.9,.9,.075),'timber','design workstations')
    for xx in (-.78,.78):
        for yy in (-.32,.32):
            C.box(name+' trestle leg',(x+xx,y+yy,floor+.41),(.065,.065,.82),'hardware','design workstations')
    C.box(name+' drawing sheet',(x-.25,y-.08,z+.042),(.8,.52,.008),'paper','drawing programme',0)
    # An unmistakable small architectural model, not an empty generic table.
    C.box(name+' model base',(x+.47,y+.08,z+.055),(.58,.45,.02),'model','model making',0)
    for dx,h in [(.30,.22),(.56,.34)]:
        C.box(name+' maquette mass',(x+dx,y+.07,z+.065+h/2),(.22,.30,h),'paper','model making')
    for dx in (-.22,.22):
        C.rod(name+' rolled drawing',(x+dx,y+.28,z+.075),(x+dx+.22,y+.28,z+.075),.035,'paper','drawing programme')
    if drafting:
        C.solid_surface(name+' inclined drawing board',[(x-.72,y-.32,z+.12),(x+.08,y-.32,z+.12),
            (x+.08,y+.18,z+.40),(x-.72,y+.18,z+.40)],.025,'paper','drawing programme')
        for xx in (x-.65,x+.01):
            C.beam(name+' board easel support',(xx,y+.15,z+.06),(xx,y+.15,z+.36),.03,.03,'hardware','drawing programme')
    for xx in (-.45,.45):
        C.box(name+' stool seat',(x+xx,y-.83,floor+.48),(.40,.40,.06),'timber','design seating')
        for dx in (-.14,.14):
            for dy in (-.14,.14):
                C.box(name+' stool leg',(x+xx+dx,y-.83+dy,floor+.225),(.035,.035,.45),'hardware','design seating',0)


def stair():
    base=.18;upper=3.55;rise=(upper-base)/20;run=.26
    for flight,x in [(0,.91),(1,-.43)]:
        for i in range(10):
            y=-2.2+(i+.5)*run if flight==0 else .4-(i+.5)*run
            z=base+(i+1+flight*10)*rise
            C.box('Return stair tread',(x,y,z-.035),(1.10,run+.015,.07),'timber','connected stair')
        a=(x,-2.2,base-.04) if flight==0 else (x,.4,base+10*rise-.04)
        b=(x,.4,base+10*rise-.04) if flight==0 else (x,-2.2,upper-.04)
        for dx in (-.48,.48):
            C.beam('Stair bearing stringer',(a[0]+dx,a[1],a[2]),(b[0]+dx,b[1],b[2]),.085,.16,'hardware','connected stair')
            for t in (0,.33,.66,1):
                y=a[1]+(b[1]-a[1])*t;z=a[2]+(b[2]-a[2])*t+.08
                C.rod('Stair seated guard post',(x+dx,y,z),(x+dx,y,z+.97),.022,'hardware','stair guards')
            C.beam('Stair continuous handrail',(x+dx,a[1],a[2]+1.05),(x+dx,b[1],b[2]+1.05),.04,.04,'hardware','stair guards')
    C.box('Intermediate stair landing',(.24,1.0,base+10*rise-.065),(2.46,1.2,.13),'floor','connected stair')
    middle=base+10*rise
    C.railing('Intermediate landing rear guard',(-.99,1.56,middle),(1.47,1.56,middle),height=1.05,spacing=.22,role='hardware')
    for x in (-.99,1.47):
        C.railing('Intermediate landing side guard',(x,.42,middle),(x,1.56,middle),height=1.05,spacing=.22,role='hardware')
    C.box('Upper stair exit landing',(-.43,-2.51,upper-.065),(1.12,.74,.13),'floor','connected stair')
    for x in (-1.18,1.53):
        C.railing('Upper slab side guard',(x,-2.55,upper),(x,1.75,upper),height=1.05,spacing=.22,role='hardware')
    C.railing('Upper rear void guard',(-1.18,1.75,upper),(1.53,1.75,upper),height=1.05,spacing=.22,role='hardware')
    for x in (-.95,1.4):
        C.box('Landing support',(x,1.3,(base+10*rise)/2),(.10,.10,base+10*rise),'hardware','connected stair')
    C.CONTACTS.append(dict(name='Return stair',floor_levels_m=[base,upper],risers=20,
        rise_m=rise,tread_m=run,landing_depth_m=1.2,slab_void_m=[2.74,4.4],
        note='Concept geometry and guard dimensions; not engineered/accessibility certification'))


def construct():
    glass=C.MATS['glass'].node_tree.nodes['Principled BSDF']
    glass.inputs['Alpha'].default_value=.22
    glass.inputs['Transmission Weight'].default_value=.92
    glass.inputs['Roughness'].default_value=.065
    C.box('Studio native foundation',(-4.35,0,.09),(12,10,.18),'floor','native foundation',0)
    C.box('Office native foundation',(6,-0+1,.09),(8.7,8,.18),'floor','native foundation',0)
    front=C.Face((0,-5,0),(1,0,0),(0,1,0),'workshop front')
    left=C.Face((-10.35,0,0),(0,1,0),(1,0,0),'workshop left')
    rear=C.Face((0,5,0),(1,0,0),(0,-1,0),'workshop rear inferred')
    right=C.Face((1.65,0,0),(0,1,0),(-1,0,0),'workshop right inferred')
    for face,u0,span,bays in [(front,-10.35,12,5),(left,-5,10,5)]:
        holes=[opening(f'{face.label} bay{b+1} floor{floor+1}',u0+span*(b+.5)/bays,z,span/bays-.08,h)
            for b in range(bays) for floor,(z,h) in enumerate([(.18,3.07),(4.0,3.05)])]
        window_wall(face,'Black curtain perimeter carrier',u0,u0+span,.18,7.15,holes,'trim')
    rearholes=[opening(f'Rear strip bay{b+1} floor{f+1}',-9.15+2.4*b,z,1.85,1.85,cols=2)
               for b in range(5) for f,z in enumerate([1.0,4.75])]
    window_wall(rear,'Complete rear studio elevation',-10.35,1.65,.18,7.15,rearholes)
    window_wall(right,'Projecting glass return',-5,-3,.18,7.15,
        [opening('Return lower glass',-4,.18,1.82,3.07),opening('Return upper glass',-4,4,1.82,3.05)],'trim')
    window_wall(right,'Shared workshop-office wall',-3,5,.18,7.15,
        [opening('Internal office studio connection',-1.25,.18,1.20,2.45,passage=True),
         *[opening('Upper office roof-facing window'+str(i),u,4.85,1.8,1.75,cols=2) for i,u in enumerate([-1.2,1.1,3.4])]])
    officefront=C.Face((0,-3,0),(1,0,0),(0,1,0),'office front')
    officeback=C.Face((0,5,0),(1,0,0),(0,-1,0),'office rear inferred')
    officeside=C.Face((10.35,0,0),(0,1,0),(-1,0,0),'office right inferred')
    window_wall(officefront,'Office recessed entrance facade',1.65,10.35,.18,4.45,
        [opening('Recessed red main entry',2.8,.18,1.42,2.86,door=True,flat=True),
         *[opening('Office front strip'+str(i),u,2.0,1.55,.50) for i,u in enumerate([5,6.9,8.8])]])
    window_wall(officeback,'Office rear',1.65,10.35,.18,4.45,
        [opening('Office service exit',9.0,.18,1,2.35,door=True),
         *[opening('Office rear strip'+str(i),u,1.3,1.4,1.1) for i,u in enumerate([3,5,7])]])
    window_wall(officeside,'Office end',-3,5,.18,4.45,
        [opening('Office side strip'+str(i),u,2.0,1.5,.5) for i,u in enumerate([-1.4,.8,3])])
    upper=C.box('Upper occupied slab with stair opening',(-4.35,0,3.47),(11.7,9.7,.16),'floor','occupied floors',0)
    C.cut_box(upper,'Stair opening through full upper slab',(.19,-.40,3.47),(2.74,4.4,.7))
    C.box('Studio closed roof deck',(-4.35,0,7.20),(12.08,10.08,.22),'roof','weathering roof')
    for x in (-10.36,1.66): C.box('Studio coping side',(x,0,7.45),(.12,10.12,.60),'trim','weathering roof')
    for y in (-5.01,5.01): C.box('Studio coping front rear',(-4.35,y,7.45),(12.12,.12,.60),'trim','weathering roof')
    C.box('Office closed roof',(6,1,4.38),(8.7,8,.18),'roof','weathering roof')
    for x in (1.65,10.35): C.box('Office coping side',(x,1,4.49),(.10,8.10,.12),'trim','weathering roof')
    for y in (-3,5): C.box('Office coping front rear',(6,y,4.49),(8.8,.10,.12),'trim','weathering roof')
    C.box('Studio roof vent',(-9.0,3.5,7.40),(.45,.45,.22),'hardware','weathering roof')
    C.box('Office roof vent',(9,2.6,4.62),(.40,.40,.30),'hardware','weathering roof')
    C.box('Main entrance native landing',(2.8,-3.45,.09),(1.9,1.1,.18),'floor','entry',0)
    for x in (-9.5,-5.0,.8):
        for y in (-4.1,4.1): C.box('Set-back studio structural column',(x,y,3.60),(.16,.16,6.84),'interior','structural frame')
    for level in (.18,3.55):
        for x,y in [(-8,-2.0),(-4.4,-2.0),(-8,1.2),(-4.4,1.2)]:
            workbench(f'Studio{level} workbench{x} {y}',x,y,level,drafting=level>1)
        C.box('Studio storage cabinet',(-7.1,4.2,level+.8),(4.8,.5,1.6),'timber','workshop storage')
        C.box('Rear pinboard',(-4.5,4.80,level+2.0),(3,.06,1.3),'paper','design display',0)
        for x in (-5.3,-4.5,-3.7):
            C.box('Pinned drawing line',(x,4.75,level+2.0),(.035,.015,.8),'hardware','design display',0)
        C.qa_room_light('Studio floor'+str(level),(-5,0,level+2.9),175,4)
    stair()
    for x in (4.3,7.5): workbench('Office desk'+str(x),x,1.7,.18)
    C.qa_room_light('Office',(6,1,3.9),130,3)
    C.CONTACTS.extend([dict(name='Native foundations',base_m=0,top_m=.18,no_site_pad=True),
        dict(name='Office entrance',door_base_m=.18,landing_top_m=.18,clear_width_m=1.42),
        dict(name='Two closed flat roofs',supported_by='columns and complete wall carriers',main_coping_m=7.75,low_coping_m=4.55)])
