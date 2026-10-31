"""Original De Stijl studio: exact planes, source colours and occupied workroom."""
import clay_core as C


def specification(make_cameras):
    details = [
        ('facade_close',(5,-10,3.5),(3.9,-3.9,2.5),35),
        ('architecture_close',(-10,-9,7),(-3,-2,3.3),35),
        ('glass_close',(-4,-7.5,1.8),(-4,-1.0,1.5),40),
        ('plane_contacts',(9,-9,5.8),(3.2,-3.7,3.8),42),
        ('artist_programme',(-5.9,-3.7,1.65),(-2,1.8,1.3),28),
        ('entrance_low',(4.2,-9.8,1.5),(3.6,-4.0,1.85),32),
    ]
    return dict(archetype_id='destijl_artist_studio',variant_id='primary_planes_glazed_studio',
        candidate='destijl-artist-studio-clay',title='De Stijl artist studio',
        source_roles=('front','oblique','top','rear_oblique'),
        dimensions_m=dict(width=15.4,depth=8.9,height=5.76),floors=1,
        teaching=dict(description='De Stijl used horizontal and vertical planes, primary colours, black, white and grey to seek a balanced abstract composition. Here separate wall and roof planes shape a working studio.',
            features=['Offset white roof and wall planes','Red, blue and yellow accents','Black-framed corner glazing'],
            main_idea='Make space through balanced planes, lines and colour.',
            source='https://www.rietveldschroderhuis.nl/en'),
        cameras=make_cameras(15.4,8.9,5.76,details),
        palette=dict(wall=(.80,.79,.73),grey=(.40,.41,.40),trim=(.018,.023,.025),
            roof=(.71,.71,.67),floor=(.48,.48,.44),glass=(.62,.72,.72),
            timber=(.43,.30,.16),interior=(.74,.70,.60),hardware=(.09,.10,.11),
            red=(.55,.018,.012),blue=(.018,.07,.16),yellow=(.88,.57,.008),
            paper=(.88,.85,.75),paint=(.24,.13,.06)),
        roof_contract='Offset lower white roof and higher grey office roof. Source-specific white vertical fin and red entrance canopy, all seated on the closed envelope and posts.',
        programme_contract='Occupied one-storey artist studio with easels and blank supported canvases, paint tables, brushes, stools, open supplies storage and a connected side preparation room.',
        contact_contract=['Small native slab and entry threshold only','True curtain openings and clear interior','White fin tied into shared wall','Red canopy seated on wall/fin supports','Supported easels and tables'],
        measurement_notes=[
            'Main front has three equal black-framed bays, glazed left return, lower projecting white roof; right grey room with blue entry, yellow fin and red canopy.',
            'Main enclosed x[-7,2.1],y[-4,4]; office x[2.1,6.5],y[-3.8,4]. Native metric dimensions inferred from the generated front, not a survey.',
            'Source front fin reaches5.76m, white roof4.08m, grey roof4.43m, red canopy3.90m. Prompt4.8m fin was not followed by source pixels.',
            'Top Plan is high aerial; all four compatible panels are preserved under their real roles. Exact hidden roof junctions and internal plan are inferred.',
            'Opposite source supplies a grey side window and white rear high strip. Other unshown opening details continue that grammar as explicit inferences.',
            'Exposed planar surfaces use source-palette clay, no bitmap graphics or generic facade sticker; no exterior site pad or landscape exported.',
        ])


def op(name,u,z,w,h,**extra):
    return dict(id=name,u=u,z=z,w=w,h=h,**extra)


def wall(face,name,u0,u1,z0,z1,holes=(),role='wall',depth=.28):
    face.wall(name,u0,u1,z0,z1,depth=depth,role=role,holes=holes)
    for item in holes:
        if item.get('passage'):
            C.OPENINGS.append(dict(id=item['id'],face=face.label,u=item['u'],z=item['z'],width=item['w'],height=item['h'],kind='clear internal passage',clear_wall_cut=True,carrier_depth_m=depth,face_origin=list(face.o),face_tangent=list(face.t),face_inward=list(face.n),occupied_space='connected studio preparation room'))
        elif item.get('door'):
            C.Face.door(face,item['id'],item['u'],item['z'],item['w'],item['h'],role='blue',panels=0)
            C.OPENINGS[-1]['carrier_depth_m']=depth
        else:
            face.window(item['id'],item['u'],item['z'],item['w'],item['h'],cols=item.get('cols',1),sill=False,depth=depth,inset=.12)


def easel(name,x,y):
    for dx in (-.47,.47):
        C.beam(name+' splayed front leg',(x+dx,y-.27,.18),(x+dx*.66,y+.12,2.36),.055,.055,'timber','artist easels')
    C.beam(name+' rear support',(x,y+.78,.18),(x,y+.12,2.16),.055,.055,'timber','artist easels')
    C.box(name+' seated canvas ledge',(x,y-.03,.98),(1.12,.18,.055),'timber','artist easels')
    C.box(name+' canvas stretcher',(x,y+.035,1.59),(.94,.055,1.2),'timber','artist easels')
    C.box(name+' blank canvas',(x,y-.001,1.59),(.91,.018,1.17),'paper','artist easels',0)
    C.box(name+' top retaining clip',(x,y-.01,2.22),(.13,.10,.07),'timber','artist easels')


def table(name,x,y):
    C.box(name+' worktop',(x,y,.98),(1.9,.88,.08),'timber','artist tables')
    for dx in (-.76,.76):
        for dy in (-.31,.31):C.box(name+' table leg',(x+dx,y+dy,.56),(.07,.07,.76),'timber','artist tables')
    C.box(name+' paper sheet',(x-.32,y-.08,1.026),(.65,.46,.009),'paper','painting supplies',0)
    C.rod(name+' oval palette',(x+.42,y+.04,1.024),(x+.42,y+.04,1.046),.16,'paint','painting supplies',24)
    for dx in (-.1,0,.1):
        C.rod(name+' brush handle',(x+.6+dx,y+.25,1.03),(x+.6+dx,y+.25,1.35),.012,'timber','painting supplies',8)
    C.rod(name+' brush cup',(x+.6,y+.25,1.03),(x+.6,y+.25,1.17),.105,'grey','painting supplies',16)
    for dx in (-.52,.52):
        C.box(name+' stool',(x+dx,y-.82,.67),(.40,.4,.06),'timber','artist seating')
        for xx in (-.14,.14):
            for yy in (-.14,.14):C.box(name+' stool leg',(x+dx+xx,y-.82+yy,.41),(.035,.035,.46),'timber','artist seating',0)


def supplies(x,y):
    for xx in (-.7,.7):C.box('Open shelving side',(x+xx,y,1.30),(.07,.42,2.24),'timber','artist storage')
    C.box('Shelving rear',(x,y+.18,1.3),(1.47,.04,2.24),'timber','artist storage')
    for z in (.22,.75,1.28,1.81,2.40):C.box('Open supply shelf',(x,y,z),(1.47,.42,.06),'timber','artist storage')
    for z in (.80,1.33,1.86):
        for i in range(5):
            C.box('Supply folio',(x-.52+i*.23,y-.07,z+.13),(.08,.28,.26),'paper' if i%2 else 'grey','artist storage',0)


def construct():
    glass=C.MATS['glass'].node_tree.nodes['Principled BSDF']
    glass.inputs['Alpha'].default_value=.22;glass.inputs['Transmission Weight'].default_value=.92;glass.inputs['Roughness'].default_value=.065
    C.box('Studio native slab',(-2.45,0,.09),(9.38,8.22,.18),'floor','native foundation',0)
    C.box('Preparation room native slab',(4.3,.1,.09),(4.4,7.8,.18),'floor','native foundation',0)
    front=C.Face((0,-4,0),(1,0,0),(0,1,0),'studio front')
    left=C.Face((-7,0,0),(0,1,0),(1,0,0),'studio left')
    rear=C.Face((0,4,0),(1,0,0),(0,-1,0),'white rear')
    shared=C.Face((2.1,0,0),(0,1,0),(1,0,0),'studio preparation join')
    wall(front,'Black front curtain frame',-7,2.1,.18,3.58,
         [op('Front glazed bay'+str(i),-7+9.1*(i+.5)/3,.18,9.1/3-.09,3.35) for i in range(3)],'trim',.18)
    wall(left,'Black glazed return',-4,4,.18,3.58,
         [op('Left glazed bay'+str(i),-4+2*(i+.5),.18,1.91,3.35) for i in range(4)],'trim',.18)
    wall(rear,'Rear white wall',-7,2.1,.18,3.65,
         [op('Rear high studio strip',-.8,2.55,5.30,.9,cols=3)])
    wall(shared,'Complete shared white wall',-4,4,.18,4.27,
         [op('Studio preparation passage',.25,.18,1.30,2.45,passage=True)])
    officefront=C.Face((0,-3.8,0),(1,0,0),(0,1,0),'blue entrance front')
    officeend=C.Face((6.5,0,0),(0,1,0),(-1,0,0),'grey end')
    officerear=C.Face((0,4,0),(1,0,0),(0,-1,0),'grey rear')
    wall(officefront,'White entry recess',2.1,4.97,.18,3.90,
         [op('Plain blue entry',3.25,.18,1.30,2.75,door=True),op('Blue entry transom',3.25,2.98,1.30,.42)])
    wall(officefront,'Grey end return',4.97,6.5,.18,3.90,role='grey')
    wall(officefront,'Continuous source grey raised header',2.1,6.5,3.90,4.27,role='grey')
    wall(officeend,'Grey opposite end wall',-3.52,3.72,.18,4.27,
         [op('Grey end source window',0,1.30,2.05,1.55,cols=2)],'grey')
    wall(officerear,'Grey rear completion',2.1,6.5,.18,4.27,
         [op('Preparation rear window',4.1,2.1,1.9,.9,cols=2)],'grey')
    C.box('Lower projecting white roof',(-2.975,-.05,3.805),(10.45,8.9,.55),'wall','source roof planes',0)
    C.box('Higher grey closed roof',(4.3,.10,4.35),(4.4,7.8,.16),'grey','source roof planes',0)
    for y in (-3.35,3.35):
        C.box('Source rising white vertical plane',(2.25,y,2.88),(.34,1.50,5.76),'wall','source vertical planes',0)
    C.box('Source red entrance canopy',(4.875,-4.10,3.74),(4.95,.90,.32),'red','source colour planes',0)
    C.box('Source yellow entrance fin',(4.97,-3.90,1.86),(.40,1.22,3.36),'yellow','source colour planes',0)
    C.box('Native entry and fin landing',(3.80,-4.15,.09),(2.90,.85,.18),'floor','entry',0)
    for y in (-3.9,3.85):
        C.box('Set-back black roof post',(-7.12,y,1.90),(.15,.15,3.44),'trim','roof bearing frame')
    for x in (-6.85,-2,1.90):
        C.box('Roof bearing rear post',(x,3.80,1.90),(.12,.12,3.44),'trim','roof bearing frame')
    for x,y in [(-5.1,1.6),(-2.0,1.8),(.5,1.5)]:easel('Studio easel',x,y)
    for x,y in [(-4.7,-1.5),(-.75,-1.2)]:table('Artist paint table',x,y)
    for x in (-5.7,-.1):supplies(x,3.56)
    C.box('Preparation counter',(5.8,.3,1.01),(.65,3.0,.12),'interior','preparation room')
    for yy in (-.9,1.5):C.box('Counter support',(5.8,yy,.60),(.48,.13,.84),'grey','preparation room')
    C.box('Preparation wash basin',(5.8,.6,1.09),(.44,.58,.06),'grey','preparation room')
    C.CONTACTS.append(dict(name='Planar studio envelope',notes='Closed single-storey envelope; shared wall supports lower roof and entrance canopy. White fins bear on slab. Front and corner posts support glazing roof edge. Native scale only.'))
    for x,y in [(-4,-1),(-3,2),(4.4,1.4)]:C.qa_room_light('studio inspection',(x,y,3.2),105,2.0)
