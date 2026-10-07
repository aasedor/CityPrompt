"""Geometry primitives and explicit clay contracts; no generic family envelope."""
import math
import clay_core as C
from assemblies import seated_guard
from build import open_door


def stair(name,x,y,lower,upper,length=5.46,width=1.2):
    count=math.ceil((upper-lower)/.18);run=length/count;rise=(upper-lower)/count
    points=[(y,lower)]
    for i in range(count):
        points += [(y+i*run,lower+(i+1)*rise),(y+(i+1)*run,lower+(i+1)*rise)]
    points += [(y+length,upper-.18),(y+.3,lower)]
    C.prism(name+' closed sloped stair',points,'x',x-width/2,x+width/2,'timber','stairs')
    for xx in (x-width/2+.04,x+width/2-.04):
        C.beam(name+' handrail',(xx,y+.08,lower+1.08),(xx,y+length-.08,upper+1.03),.045,.045,'hardware','stairs')
        for i in range(count):
            C.box(name+' supported baluster',(xx,y+(i+.5)*run,lower+(i+1)*rise+.5),(.025,.025,1),'hardware','stairs',0)
    C.CONTACTS.append(dict(name=name,lower=lower,upper=upper,treads=count,rise_m=rise,run_m=run))


def stair_hole(slab,x,y,z,length=5.46,width=1.2,front_guard=True):
    C.cut_box(slab,'Through floor stair opening',(x,y+length/2,z-.11),(width+.20,length+.16,.65))
    for xx in (x-width/2-.1,x+width/2+.1):
        seated_guard('Seated stairwell edge',(xx,y-.08,z),(xx,y+length+.08,z))
    if front_guard:
        seated_guard('Front stairwell guard',(x-width/2-.1,y-.08,z),(x+width/2+.1,y-.08,z))


def wall(face,name,span,z0,z1,holes,role='wall',depth=.27):
    face.wall(name,-span/2,span/2,z0,z1,depth=depth,role=role,holes=holes)
    for h in holes:
        if 'entrance' in h['id'].lower(): open_door(face,h)
        else: face.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=1,depth=depth,inset=.14)


def base_manifest(slug,version,cameras,measure,programme,roof):
    return dict(candidate=f'{slug}-clay-v{version:03d}',method=C.METHOD,representation_kind='architectural_clay',
        archetype_id=slug,variant_id=slug+'-v0',state='prework',keeper_claimed=False,runtime_seed_allowed=False,
        measurement_contract=measure,roof_contract=roof,
        identity_contract=dict(owner='Source-specific physical geometry',bitmap_stickers='None in architectural-clay profile'),
        material_contract=dict(profile='Source-palette architectural clay',limitation='Not a textured keeper'),
        programme_contract=programme,
        contact_contract=['Ground support','Through-carrier apertures','Physically open doors','Occupied rooms',
                          'Closed roof slabs','Sloped stairs with through-floor holes'],
        runtime_contract=dict(scale='fixed_native_only',resizing=False,installation='not installed',review='NOT TESTED'),
        camera_roster=cameras,mandatory_review_views=[v['name'] for v in cameras])


def camera_set(width,depth,height,details,front_height=None):
    r=max(width,depth)*2.1
    result=[]
    for name,pos in [('front',(0,-r,front_height or height*.6)),('front_corner',(r*.66,-r*.84,height*2)),
                     ('aerial',(r*.6,-r*.7,height*4)),('top',(0,0,r*1.3)),
                     ('left_side',(-r,0,height*.7)),('right_side',(r,0,height*.7)),
                     ('rear',(0,r,height*.7)),('rear_side',(-r*.7,r*.8,height*2))]:
        result.append(dict(name=name,location=pos,target=(0,.001 if name=='top' else 0,0 if name=='top' else height*.45),
                           **({'ortho_scale':max(width,depth)*1.4} if name=='top' else {})))
    result += [dict(name=n,location=p,target=t,lens=l,whole=False) for n,p,t,l in details]
    return result
