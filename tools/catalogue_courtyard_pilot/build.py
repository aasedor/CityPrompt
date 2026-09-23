"""Exact brick-modern courtyard frontage; external clay pilot, no runtime writes."""
import argparse
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import clay_core as C

PARENT = 'courtyard_family_housing'
VARIANT = 'courtyard_family_brick_modern'
PALETTE = dict(wall=(.48,.365,.205), mortar=(.35,.29,.20), trim=(.10,.095,.082),
    coping=(.35,.30,.21), roof=(.19,.205,.215), foundation=(.39,.38,.34),
    glass=(.38,.43,.43), hardware=(.075,.078,.072), timber=(.28,.20,.12),
    interior=(.63,.59,.51), floor=(.42,.34,.25))
W,D,EAVE,RIDGE = 23.0,10.8,9.5,12.2
CAMERAS = [
    dict(name='front',location=(0,-42,6),target=(0,0,6),ortho_scale=29),
    dict(name='front_corner',location=(-32,-39,17),target=(0,0,5.6)),
    dict(name='aerial',location=(-30,-37,38),target=(0,0,5)),
    dict(name='top',location=(0,0,50),target=(0,.001,0),ortho_scale=29),
    dict(name='left_side',location=(-42,0,6),target=(0,0,6),ortho_scale=21),
    dict(name='right_side',location=(42,0,6),target=(0,0,6),ortho_scale=21),
    dict(name='rear',location=(0,42,6),target=(0,0,6),ortho_scale=29),
    dict(name='rear_side',location=(32,36,23),target=(0,0,5)),
    dict(name='facade_close',location=(-14,-23,13),target=(-5,-5.4,5.6),whole=False,lens=55),
    dict(name='architecture_close',location=(2,-17,4.2),target=(-2.8,-3,1.8),whole=False,lens=50),
    dict(name='glass_close',location=(-12,-14,8),target=(-8,-5.4,7.35),whole=False,lens=65),
    dict(name='roof_contact',location=(-9,-13,18),target=(-7,-3,10.7),whole=False,lens=60),
    dict(name='side_projection',location=(-22,-11,7),target=(-11.5,-2.3,5.7),whole=False,lens=52),
    dict(name='passage_axis',location=(-2.8,-11,1.6),target=(-2.8,6,1.6),whole=False,lens=28),
]

def manifest(version):
    return dict(candidate=f'courtyard-brick-modern-clay-v{version:03d}',method=C.METHOD,
        representation_kind='architectural_clay',archetype_id=PARENT,variant_id=VARIANT,
        state='prework',keeper_claimed=False,runtime_seed_allowed=False,
        supersedes=f'courtyard-brick-modern-clay-v{version-1:03d}' if version>1 else None,
        finite_corrections=(['Seat wall and gable heads below the roof skin; terminate brick joints within the gable to remove exposed buff/black verge strips.'] if version>3 else ['Remove zero-area triangles introduced by arch/window and rooflight Boolean triangulation; preserve visible geometry.'] if version>2 else ['Replace siding-like horizontal courses with fine staggered brick joints, including gables and ground piers.', 'Use paired vertical balcony-door panes and dark thin balcony slabs.'] if version>1 else []),
        measurement_contract=dict(dimensions_m=dict(width=W,wall_depth=D,eave=EAVE,ridge=RIDGE),
            observed_storeys=3,occupied_floor_z=[.12,3.25,6.38],
            source_measurements=dict(front='Buff brick three-storey bar; four shallow segmental arches at grade, outer balcony pairs, narrow intermediate upper windows, two recessed vertical masonry seams.',
                oblique='Gabled left end with one balcony stack and smaller paired side openings; three rooflights on the front slope.',
                top='Straight rectangular buff-brick frontage, simple longitudinal gable and three rooflights per slope. Surrounding red-brick buildings and courtyard are separate context.',
                scale='Conceptual metres inferred from 2.2 m doors and 1 m balcony guards, not survey.'),
            source_discrepancies=['Family name says courtyard housing, but the locked variant is one buff-brick entrance bar beside separate red-brick courtyard neighbours. Those neighbours are not silently included.'],
            hidden_assumptions=['Rear upper openings continue the front rhythm; unseen residential partitions, stairs and rear doors are inferred.',
                'The two central arches are through-passages to the courtyard; outer arches hold recessed entry vestibules. No enclosed courtyard or whole-block enclosure is claimed.']),
        roof_contract=dict(type='single closed longitudinal gable, six physical rooflights, bounded ridge and eaves'),
        material_contract=dict(profile='texture-free semantic architectural clay',authority='buff masonry, dark metal, grey slate palette; geometry owns joints and arches',limitations='No texture or photoreal keeper claim.'),
        identity_contract=dict(owner='constructed arch sequence, balcony cadence, gable, rooflight positions',bitmap_stickers='none'),
        contact_contract=['Base is Z=0; two passages remain open end to end.', 'Balcony slabs bear in masonry; rails seated on slabs.', 'Gable walls meet continuous roof; rooflight cuts penetrate the full roof skin.'],
        programme_contract=dict(storeys=3,entrances=2,courtyard_passages=2,interiors='Inferred apartments and two enclosed access stairs',excluded='Neighbour buildings, public paving, trees and a complete courtyard block'),
        camera_roster=CAMERAS,mandatory_review_views=[c['name'] for c in CAMERAS])

def openings(face,holes):
    for h in holes:
        if h.get('door'):face.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=2 if h['w']>1.5 else 1,rows=1,sill=False,kind='glazed door')
        else:face.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=h.get('cols',2),curtain=True)

def courses(face,lo,hi,z0,z1,holes,gable=False):
    # Thin joint faces share one mesh per elevation: clay brick cadence without
    # thousands of separate objects or a bitmap skin. Clip every opening.
    vs,fs=[],[]
    def joint(l,r,b,t):
        if r-l<.001 or t-b<.001:return
        n=len(vs);vs.extend([face.p(l,-.008,b),face.p(r,-.008,b),face.p(r,-.008,t),face.p(l,-.008,t)])
        ids=(n,n+1,n+2,n+3)
        if face.t.cross(C.Vector((0,0,1))).dot(face.n)>0:ids=ids[::-1]
        fs.append(ids)
    z=z0+.08;row=0
    while z<z1:
        left,right=lo,hi
        if gable:
            half=(RIDGE-.17-z-.14)/(RIDGE-EAVE)*D/2
            if half<=0:break
            left,right=-half,half
        spans=[(left,right)]
        for h in holes:
            if h['z']-.15<z<h['z']+h['h']+.03:
                a,b=h['u']-h['w']/2-.025,h['u']+h['w']/2+.025
                spans=[part for l,r in spans for part in [(l,min(r,a)),(max(l,b),r)] if part[1]-part[0]>.025]
        for l,r in spans:
            joint(l,r,z-.004,z+.004)
            x=math.floor(l/.36)*.36+(row%2)*.18
            while x<r:
                if x>l+.008:joint(x-.0035,min(x+.0035,r),z+.004,min(z+.116,z1))
                x+=.36
        z+=.12;row+=1
    if vs:C.mesh('Staggered brick joints '+face.label,vs,fs,'mortar','brick courses')

def arch_cut(face,owner,cx,width=4.8):
    spring,rise=2.10,.72
    poly=[(cx-width/2,-.05),(cx+width/2,-.05)]
    poly += [(cx+math.cos(a)*width/2,spring+math.sin(a)*rise) for a in [i*math.pi/24 for i in range(25)]]
    cutter=face.panel('Actual arch cutter',poly,-.3,.65,'wall','construction cutter')
    C.bpy.context.view_layer.objects.active=owner
    m=owner.modifiers.new('Open arch through brick','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter
    C.bpy.ops.object.modifier_apply(modifier=m.name);C.remove_cutter(cutter);C.normalise(owner.data)
    for i in range(24):
        a=i*math.pi/24+.003;b=(i+1)*math.pi/24-.003
        p=[(cx+math.cos(a)*width/2,spring+math.sin(a)*rise),
           (cx+math.cos(b)*width/2,spring+math.sin(b)*rise),
           (cx+math.cos(b)*(width/2+.24),spring+math.sin(b)*(rise+.24)),
           (cx+math.cos(a)*(width/2+.24),spring+math.sin(a)*(rise+.24))]
        face.panel('Seated radial arch brick',p,-.04,.32,'wall','arch ring')

def balcony(face,u,z,width=2.9):
    face.part('Bearing balcony slab',u,-.58,z-.065,width,1.42,.13,'trim','balcony',.004)
    a=face.p(u-width/2,-1.27,z);b=face.p(u+width/2,-1.27,z)
    C.railing('Balcony front guard',a,b,1.05,.13,'hardware')
    for s in (-1,1):C.railing('Balcony return',face.p(u+s*width/2,-1.27,z),face.p(u+s*width/2,.04,z),1.05,.13,'hardware')

def furniture(x,y,z):
    C.box('Apartment table',(x,y,z+.73),(1.3,.75,.10),'timber','occupied room')
    for dx in (-.52,.52):
        for dy in (-.25,.25):C.box('Table leg',(x+dx,y+dy,z+.35),(.07,.07,.70),'timber','occupied room')
    C.box('Sofa seat',(x,y+1.5,z+.38),(1.75,.70,.40),'interior','occupied room')
    C.box('Sofa back',(x,y+1.82,z+.69),(1.75,.13,.80),'interior','occupied room')

def roof_z(y):return RIDGE-abs(y)*(RIDGE-EAVE)/(D/2)

def build():
    front=C.Face((0,-D/2,0),(1,0,0),(0,1,0),'front')
    rear=C.Face((0,D/2,0),(1,0,0),(0,-1,0),'rear')
    xs=[-8,-4.8,-1.6,1.6,4.8,8]
    for face in (front,rear):
        holes=[]
        for z in (3.25,6.38):
            for x in xs:
                wide=abs(x)==8;h=2.2 if wide or abs(x)==4.8 else 1.30
                holes.append(dict(id=f'{face.label} upper opening {x} {z}',u=x,z=z if wide else z+.45,w=2.3 if wide else .92,h=h,door=wide))
        owner=face.wall(face.label+' complete carrier',-W/2,W/2,0,EAVE-.17,depth=.34,holes=holes)
        for x in (-8,-2.8,2.8,8):arch_cut(face,owner,x,4.65 if abs(x)==8 else 4.75)
        arch_masks=[dict(u=x,z=0,w=4.65 if abs(x)==8 else 4.75,h=3.04) for x in (-8,-2.8,2.8,8)]
        courses(face,-W/2,W/2,0,EAVE-.17,holes+arch_masks);openings(face,holes)
        for x in (-8,8):
            for z in (3.25,6.38):balcony(face,x,z)
        for z in (3.08,6.21,9.23):face.part('Continuous masonry string course',0,-.055,z,W,.18,.12,'wall','masonry bands',.003)
        for x in (-5.55,5.55):face.part('Vertical recessed rhythm',x,-.045,5.5,.12,.13,7.8,'mortar','masonry seams',0)
    # Gable ends: side openings and source-visible balcony on left end.
    for sign,label in ((-1,'left'),(1,'right')):
        f=C.Face((sign*W/2,0,0),(0,1,0),(-sign,0,0),label)
        holes=[]
        for z in (3.25,6.38):
            for y in (-2.6,.2,3.3):holes.append(dict(id=f'{label} opening {y} {z}',u=y,z=z if y==-2.6 else z+.6,w=1.7 if y==-2.6 else .85,h=2.2 if y==-2.6 else 1.35,door=y==-2.6))
        holes.append(dict(id=label+' ground door',u=2.8,z=.12,w=1.05,h=2.25,door=True))
        f.wall(label+' closed end',-D/2,D/2,0,EAVE-.17,.34,holes=holes)
        f.panel(label+' closed gable',[(-D/2,EAVE-.17),(D/2,EAVE-.17),(0,RIDGE-.17)],0,.34,'wall','gable')
        courses(f,-D/2,D/2,EAVE-.17,RIDGE-.17,[],gable=True)
        courses(f,-D/2,D/2,0,EAVE-.17,holes);openings(f,holes)
        for z in (3.25,6.38):balcony(f,-2.6,z,2.25)
    # Central passages: continuous sidewalls and soffits; external courtyard is context.
    for x in (-2.8,2.8):
        C.box('Passage walk',(x,0,.035),(4.75,D,.07),'foundation','passage grade',0)
        for dx in (-2.5,2.5):C.box('Passage loadbearing side',(x+dx,0,1.51),(.25,D,3.02),'wall','passage support',0)
    # Outer entry vestibules are recessed behind the arch, with actual glazed doors.
    for sign in (-1,1):
        x=sign*8
        for y,inward in ((-3.9,1),(3.9,-1)):
            f=C.Face((0,y,0),(1,0,0),(0,inward,0),'vestibule')
            holes=[dict(id=f'Entrance {x} {y}',u=x,z=.12,w=1.2,h=2.25,door=True)]
            f.wall('Recessed entry wall',x-2.55,x+2.55,0,3.02,.22,holes=holes);openings(f,holes)
        C.box('Ground entry slab',(x,0,.06),(5.05,D,.12),'foundation','ground occupied slab',0)
        # Stair reaches the two upper floor openings; keep each run outside the passages.
        for base in (.12,3.25):
            for i in range(18):
                h=(i+1)*3.13/18
                C.box('Internal apartment stair',(x,-1.9+i*.245,base+h/2),(1.1,.245,h),'floor','internal circulation',0)
    for z in (3.25,6.38,9.5):
        slab=C.box('Continuous upper floor',(0,0,z-.10),(W-.68,D-.68,.20),'floor','floor',0)
        if z<9.5:
            for x in (-8,8):C.cut_box(slab,'Stairwell through floor',(x,.18,z),(1.15,4.45,.65))
        if z<9.5:
            for x in (-8,-2.8,2.8,8):furniture(x,-3.6,z)
    for x in (-5.6,0,5.6):C.box('Apartment party wall',(x,0,6.15),(.18,D-.7,6.65),'interior','residential partitions',0)
    # Solid gable slopes with physical skylight openings and sealed frame returns.
    for sign in (-1,1):
        yedge=sign*(D/2+.16)
        outline=[(-W/2-.14,0,RIDGE),(W/2+.14,0,RIDGE),(W/2+.14,yedge,roof_z(yedge)),(-W/2-.14,yedge,roof_z(yedge))]
        skin=C.solid_surface('Continuous slate roof slope',outline,.16,'roof','roof')
        for x in (-7,0,7):
            y=sign*3.1;z=roof_z(y)
            C.cut_box(skin,'Full skylight roof aperture',(x,y,z),(1.12,1.5,3.0))
            p=[(x+dx,y+dy,roof_z(y+dy)+.035) for dx,dy in [(-.52,-.71),(.52,-.71),(.52,.71),(-.52,.71)]]
            C.solid_surface('Recessed optical rooflight',p,.015,'glass','rooflight')
            for a,b in zip(p,p[1:]+p[:1]):C.beam('Seated rooflight curb',a,b,.075,.16,'trim','rooflight curb')
        # Horizontal slate joints on the actual slope, terminated at the rooflights.
        for j in range(1,18):
            y=sign*j*(D/2)/18;z=roof_z(y)+.009
            spans=[(-W/2,W/2)]
            if abs(abs(y)-3.1)<.82:spans=[(-W/2,-7.65),(-6.35,-.65),(.65,6.35),(7.65,W/2)]
            for a,b in spans:C.beam('Slate course',(a,y,z),(b,y,z),.012,.012,'coping','roof coursing')
        C.beam('Continuous eaves gutter',(-W/2-.16,yedge,roof_z(yedge)),(W/2+.16,yedge,roof_z(yedge)),.12,.17,'trim','weathering')
    C.beam('Bounded ridge cap',(-W/2-.14,0,RIDGE+.025),(W/2+.14,0,RIDGE+.025),.18,.10,'roof','weathering')
    for x in (-W/2,W/2):
        for y in (-D/2-.1,D/2+.1):C.rod('Downpipe',(x,y,.12),(x,y,EAVE),.045,'trim','weathering')
    C.CONTACTS.extend([dict(name='two courtyard passages',status='open along entire depth',centres_x=[-2.8,2.8],clear_width_m=4.75),
        dict(name='entrances',status='recessed grounded entry slabs',front_thresholds=[[-8,-3.9,.12],[8,-3.9,.12]]),
        dict(name='rooflights',status='six full-depth cuts, recessed optical panes and seated frame curbs')])
    # Boolean n-gons can export collinear triangles. Triangulate before export
    # and remove only zero-area faces; retain all nonzero surfaces and bounds.
    removed=0
    for obj in C.objects():
        bm=C.bmesh.new();bm.from_mesh(obj.data)
        C.bmesh.ops.triangulate(bm,faces=list(bm.faces))
        bad=[f for f in bm.faces if f.calc_area()<=1e-10]
        removed+=len(bad)
        C.bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
        bm.to_mesh(obj.data);bm.free();obj.data.update()
    C.CONTACTS.append(dict(name='Boolean triangulation cleanup',removed_zero_area_faces=removed))

def main():
    p=argparse.ArgumentParser();p.add_argument('--source-root',type=Path,required=True);p.add_argument('--output',required=True)
    p.add_argument('--version',type=int,default=1);p.add_argument('--resolution',type=int,default=1440);p.add_argument('--dry-run',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);root=a.source_root/'frontend/public/archetypes/buildings/courtyard_family_housing'
    if (a.source_root/'source-entry.json').exists():
        entry=C.read_json(a.source_root/'source-entry.json');entry['_reference_root']=str(a.source_root/'sources')
    else:
        entry=dict(archetype_id=PARENT,variant_id=VARIANT,directory='.',_reference_root=str(root),sources=[dict(role=role,original_path=str(root/name),path='sources/'+name,bytes=(root/name).stat().st_size,sha256=C.digest(root/name)) for role,name in [('front','variant_2.png'),('oblique','variant_2_angle_60.jpg'),('top','variant_2_angle_90.jpg')]])
    m=manifest(a.version);out=C.prepare_candidate(a,entry,m,__file__)
    if out is None:return
    cameras=C.setup(PALETTE,CAMERAS,a.resolution);build();C.deliver(out,m,cameras)

if __name__=='__main__':main()
