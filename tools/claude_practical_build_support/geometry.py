"""Metric construction primitives. Building compositions live in family modules."""
import math
import clay_core as C
from contract import subtract_openings


def optical_surface(name, points, normal, thickness=.01, module='glazing'):
    """Extrude glazing along its wall normal, never vertically within its plane."""
    n=len(points)
    vertices=[tuple(p[i]+sign*normal[i]*thickness/2 for i in range(3))
              for sign in (-1,1) for p in points]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return C.mesh(name,vertices,faces,'glass',module)


def open_door(face, h):
    u, z, w, height = (h[k] for k in ('u', 'z', 'w', 'h'))
    for sign in (-1, 1):
        face.part(h['id']+' jamb', u+sign*(w/2-.035), .15, z+height/2, .07, .12, height)
    face.part(h['id']+' head', u, .15, z+height-.035, w, .12, .07)
    # Two leaves parked against the reveals leave the complete central opening free.
    for sign in (-1, 1):
        for zz in (z+.04, z+height-.04):
            face.part('Open door rail',u+sign*(w/2-.08),.15+w/4,zz,.05,w/2,.06,'trim',soft=0)
        for dd in (.15,.15+w/2):
            face.part('Open door stile',u+sign*(w/2-.08),dd,z+height/2,.05,.06,height,'trim',soft=0)
        face.part('Open glass leaf',u+sign*(w/2-.08),.15+w/4,z+height/2,.01,w/2-.08,height-.12,'glass',soft=0)
    C.OPENINGS.append(dict(id=h['id'],face=face.label,u=u,z=z,width=w,height=height,
        kind='open public doorway',clear_wall_cut=True,carrier_depth_m=.28,
        face_origin=list(face.o),face_tangent=list(face.t),face_inward=list(face.n)))


def brick_courses(face, lo, hi, z0, z1, holes, spacing=.085):
    """Source-measured recessed mortar lines, batched in one mesh per elevation.

    This is physical source-palette construction, not a photoreal texture claim.
    Cuts are subtracted before construction so no trim can cover a doorway.
    """
    vertices, faces = [], []
    for row in range(math.ceil((z1-z0)/spacing)):
        z=z0+row*spacing
        for a,b in subtract_openings(lo,hi,z,z+.006,holes):
            offset=len(vertices)
            vertices.extend([face.p(a,-.002,z),face.p(b,-.002,z),face.p(b,-.002,z+.006),face.p(a,-.002,z+.006)])
            faces.append(tuple(offset+i for i in range(4)))
    if faces:C.mesh(face.label+' measured mortar courses',vertices,faces,'joint','brick joints')


def wall(face, span, z0, z1, holes, role='wall', courses=False):
    owner=face.wall(face.label+' wall',-span/2,span/2,z0,z1,depth=.28,role=role,holes=holes)
    if courses:brick_courses(face,-span/2,span/2,z0,z1,holes)
    for h in holes:
        if h.get('open'):open_door(face,h)
        else:face.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=h.get('cols',2),depth=.28,curtain=h.get('curtain',False))
    return owner


def stair(name,x,y,lower,upper,length=6,width=1.4,landing_gap=.15):
    count=math.ceil((upper-lower)/.175);run=length/count;rise=(upper-lower)/count
    points=[(y,lower)]
    for i in range(count):
        points.extend([(y+i*run,lower+(i+1)*rise),(y+(i+1)*run,lower+(i+1)*rise)])
    points.extend([(y+length,upper-.18),(y+.3,lower)])
    C.prism(name,points,'x',x-width/2,x+width/2,'pale','stairs')
    # Floor cuts extend .15m beyond the last tread; bridge to the intact slab.
    C.box(name+' landing tongue',(x,y+length+landing_gap/2,upper-.09),(width,landing_gap,.18),'pale','stairs',0)
    for xx in (x-width/2+.035,x+width/2-.035):
        C.beam(name+' handrail',(xx,y+.08,lower+1.08),(xx,y+length-.08,upper+1.03),.045,.045,'hardware','stairs')
        for i in range(0,count,2):
            C.box(name+' supported baluster',(xx,y+(i+.5)*run,lower+(i+1)*rise+.5),(.03,.03,1),'hardware','stairs',0)
    C.CONTACTS.append(dict(name=name,x=x,y=y,lower=lower,upper=upper,length=length,width=width,treads=count,rise_m=rise,run_m=run))


def camera_roster(w,d,h,details):
    r=max(w,d)*1.7
    values=[('front',(0,-r,h*.48)),('front_corner',(-r*.78,-r*.84,h*2)),
            ('aerial',(r*.7,-r*.8,h*3)),('top',(0,0,r*1.5)),
            ('left_side',(-r,0,h*.6)),('right_side',(r,0,h*.6)),
            ('rear',(0,r,h*.6)),('rear_side',(r*.7,r*.8,h*1.8))]
    cameras=[dict(name=n,location=p,target=(0,.001 if n=='top' else 0,0 if n=='top' else h*.45),
                  **({'ortho_scale':max(w,d)*1.4} if n=='top' else {})) for n,p in values]
    return cameras+[dict(name=n,location=p,target=t,lens=l,whole=False) for n,p,t,l in details]
