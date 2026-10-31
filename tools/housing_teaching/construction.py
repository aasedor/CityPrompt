"""Small housing components; no inherited family composition or dimensions."""
import math
import clay_core as C


PALETTE = dict(wall=(.74,.70,.57), trim=(.87,.85,.76), roof=(.065,.073,.078),
    floor=(.40,.36,.28), glass=(.50,.61,.60), timber=(.045,.105,.082),
    interior=(.66,.60,.46), hardware=(.065,.073,.068), foundation=(.40,.41,.37),
    brick=(.29,.115,.062), fabric=(.29,.34,.25), white=(.84,.83,.76))


def opening(ident,u,z,w,h,**extra):
    return dict(id=ident,u=u,z=z,w=w,h=h,**extra)


def wall(face,name,u0,u1,z0,z1,holes=(),role='wall',depth=.25):
    carrier=face.wall(name,u0,u1,z0,z1,depth=depth,role=role,holes=holes)
    return carrier


def sash(face,op):
    name=op['id'];u,z,w,h=(op[k] for k in ('u','z','w','h'))
    face.window(name,u,z,w,h,cols=1,rows=2,inset=.13,depth=.25,curtain=False)
    # Upper divided sash only; lower sash remains a single pane, as in source.
    for delta in (-w/6,w/6):
        face.part(name+' upper sash bar',u+delta,.118,z+h*.75,.024,.065,h*.5-.065,'trim','source sash',0)
    face.part(name+' upper sash horizontal bar',u,.118,z+h*.75,w-.065,.065,.024,'trim','source sash',0)
    for side in (-1,1):
        face.part(name+' exterior casing',u+side*(w/2+.035),-.025,z+h/2,.09,.07,h+.16,'trim','window casing',0)
    for level in (z-.05,z+h+.05):
        face.part(name+' casing head or base',u,-.025,level,w+.16,.07,.09,'trim','window casing',0)


def simple_window(face,op,cols=2):
    face.window(op['id'],op['u'],op['z'],op['w'],op['h'],cols=cols,rows=1,inset=.13,depth=.25)


def siding(face,name,u0,u1,z0,z1,holes=(),pitch=.125):
    # Only thin source-scale clapboard lower edges; wall owns the opaque field.
    from tools.teaching_style_pilot.contracts import unobstructed_spans
    z=z0+pitch
    while z<z1-.025:
        gaps=[(o['u']-o['w']/2-.075,o['u']+o['w']/2+.075)
              for o in holes if o['z']-.09<z<o['z']+o['h']+.09]
        for lo,hi in unobstructed_spans(u0,u1,gaps):
            if hi-lo>.02:face.part(name+' clapboard lap',(lo+hi)/2,-.008,z,hi-lo,.018,.018,'wall','source clapboard edges',0)
        z+=pitch


def gable_end(face,name,half_span,eave,ridge,holes=()):
    carrier=face.panel(name,[(-half_span,eave),(half_span,eave),(0,ridge)],0,.25)
    carrier['rlasm_wall_carrier']=True
    for op in holes:
        face.cut(carrier,op['id']+' triangular carrier cut',op['u'],op['z'],op['w'],op['h'],.25)
    z=eave+.125
    from tools.teaching_style_pilot.contracts import unobstructed_spans
    while z<ridge-.035:
        span=half_span*(ridge-z)/(ridge-eave)
        gaps=[(o['u']-o['w']/2-.075,o['u']+o['w']/2+.075) for o in holes if o['z']-.09<z<o['z']+o['h']+.09]
        for lo,hi in unobstructed_spans(-span,span,gaps):
            if hi-lo>.02:face.part(name+' gable clapboard',(lo+hi)/2,-.008,z,hi-lo,.018,.018,'wall','gable siding',0)
        z+=.125


def gable_roof_x(name,x0,x1,half_depth,eave,ridge,overhang=.22,center_y=0):
    """Ridge parallel to X, two closed owned planes and bounded fascia."""
    from tools.housing_teaching.contracts import roof_datums
    datums=roof_datums(eave,ridge,half_depth,overhang,.13)
    span=half_depth+overhang
    edge=datums['edge_top'];ridge=datums['ridge_top']
    for side in (-1,1):
        C.solid_surface(name+f' roof plane {side}',[(x0-overhang,center_y,ridge),(x1+overhang,center_y,ridge),
            (x1+overhang,center_y+side*span,edge),(x0-overhang,center_y+side*span,edge)],.13)
        C.box(name+' eave fascia',((x0+x1)/2,center_y+side*span,edge-.065),(x1-x0+2*overhang,.09,.15),'trim','roof fascia',0)
    for x in (x0-overhang,x1+overhang):
        for side in (-1,1):
            C.beam(name+' closed gable rake',(x,center_y,ridge-.065),(x,center_y+side*span,edge-.065),.10,.13,'trim','roof fascia',0)
    C.box(name+' bounded ridge',((x0+x1)/2,center_y,ridge+.015),(x1-x0+2*overhang,.08,.055),'roof','ridge cap',0)


def gable_roof_y(name,center_x,y0,y1,half_width,eave,ridge,overhang=.22):
    """Raised source wing: ridge runs front-to-rear, perpendicular to low wing."""
    from tools.housing_teaching.contracts import roof_datums
    d=roof_datums(eave,ridge,half_width,overhang,.13)
    span=half_width+overhang
    for side in (-1,1):
        x=center_x+side*span
        C.solid_surface(name+f' roof plane {side}',[(center_x,y0-overhang,d['ridge_top']),
            (center_x,y1+overhang,d['ridge_top']),(x,y1+overhang,d['edge_top']),
            (x,y0-overhang,d['edge_top'])],.13)
        C.box(name+' eave fascia',(x,(y0+y1)/2,d['edge_top']-.065),
              (.09,y1-y0+2*overhang,.15),'trim','roof fascia',0)
    for y in (y0-overhang,y1+overhang):
        for side in (-1,1):
            C.beam(name+' closed gable rake',(center_x,y,d['ridge_top']-.065),
                (center_x+side*span,y,d['edge_top']-.065),.10,.13,'trim','roof fascia',0)
    C.box(name+' bounded ridge',(center_x,(y0+y1)/2,d['ridge_top']+.015),
          (.08,y1-y0+2*overhang,.055),'roof','ridge cap',0)


def bed(name,x,y,z):
    C.box(name+' frame',(x,y,z+.22),(1.36,1.95,.28),'floor','residential bed')
    C.box(name+' mattress',(x,y,z+.42),(1.30,1.9,.20),'white','residential bed')
    C.box(name+' quilt',(x,y-.23,z+.54),(1.31,1.3,.05),'fabric','residential bed')
    C.box(name+' pillow',(x,y+.65,z+.56),(.92,.40,.10),'white','residential bed')
    C.box(name+' headboard',(x,y+1,z+.48),(1.4,.075,.8),'floor','residential bed')


def table(name,x,y,z):
    C.box(name+' top',(x,y,z+.75),(1.25,.75,.065),'floor','residential dining')
    for dx in (-.50,.50):
        for dy in (-.27,.27):C.box(name+' leg',(x+dx,y+dy,z+.37),(.055,.055,.74),'floor','residential dining')
    for dx in (-.85,.85):
        C.box(name+' chair seat',(x+dx,y,z+.44),(.43,.45,.055),'floor','residential dining')
        C.box(name+' chair back',(x+dx+math.copysign(.19,dx),y,z+.69),(.045,.45,.48),'floor','residential dining')
        for xx in (-.16,.16):
            for yy in (-.16,.16):C.box(name+' chair leg',(x+dx+xx,y+yy,z+.21),(.035,.035,.42),'floor','residential dining',0)


def sofa(name,x,y,z):
    C.box(name+' base',(x,y,z+.24),(1.7,.72,.35),'floor','living room')
    C.box(name+' seat',(x,y-.06,z+.45),(1.58,.65,.19),'fabric','living room')
    C.box(name+' back',(x,y+.29,z+.73),(1.7,.16,.73),'fabric','living room')
    for dx in (-.78,.78):C.box(name+' arm',(x+dx,y,z+.64),(.18,.76,.34),'fabric','living room')


def kitchen(name,x,y,z,width=2.25):
    C.box(name+' base cabinets',(x,y,z+.43),(width,.58,.86),'white','residential kitchen')
    C.box(name+' counter',(x,y,z+.89),(width+.035,.63,.055),'floor','residential kitchen')
    C.box(name+' inset sink',(x-.35,y,z+.923),(.55,.4,.012),'hardware','residential kitchen',0)
    C.rod(name+' tap',(x-.35,y+.15,z+.92),(x-.35,y+.15,z+1.16),.018,'hardware','residential kitchen',10)
    for i in range(4):C.box(name+' cabinet face',(x-width/2+(i+.5)*width/4,y-.301,z+.44),(width/4-.018,.022,.78),'white','residential kitchen',0)


def flight_x(name,start_x,y,width,z0,z1,going=.28):
    from tools.housing_teaching.contracts import stair_flight, stair_posts
    f=stair_flight(z0,z1,going)
    # Solid stair body bears on lower floor; exact upper endpoint meets landing.
    for i,z in enumerate(f['levels']):
        base=max(0,min(z0,z1)-.12)
        C.box(name+f' supported tread {i+1}',(start_x+going*(i+.5),y,(base+z)/2),
              (going+.004,width,z-base),'floor','connected residential stairs',0)
    for side in (-1,1):
        C.beam(name+' handrail',(start_x,y+side*(width/2-.04),z0+.92),
            (start_x+f['run'],y+side*(width/2-.04),z1+.92),.035,.035,'floor','stair rails')
        for post in stair_posts(z0,z1,going):
            lo,hi=post['bottom_z'],post['top_z']
            C.box(name+' rail post',(start_x+post['x_offset'],y+side*(width/2-.04),(lo+hi)/2),
                  (.045,.045,hi-lo),'floor','stair rails')
    return f
