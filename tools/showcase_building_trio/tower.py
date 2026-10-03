"""Terracotta setback tower with occupied tiers and a constructed metal lantern."""
import math

def build(B):
    C=B.C;box=B.box
    tiers=[(32,28,0,7.2,2),(31,27,7.2,31,7),(25,22,31,44.6,4),
           (19.4,17,44.6,51.4,2),(13.4,11.6,51.4,58.2,2)]
    def footprint(w,d,tier):
        if tier==0:return [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]
        p=2.15 if tier<3 else 1.25;cx=w*.245;cy=d*.245;hx=w/2;hy=d/2
        return [(-hx+p,-hy+p),(-cx,-hy+p),(-cx,-hy),(cx,-hy),(cx,-hy+p),(hx-p,-hy+p),
                (hx-p,-cy),(hx,-cy),(hx,cy),(hx-p,cy),(hx-p,hy-p),(cx,hy-p),(cx,hy),
                (-cx,hy),(-cx,hy-p),(-hx+p,hy-p),(-hx+p,cy),(-hx,cy),(-hx,-cy),(-hx+p,-cy)]
    box('grounded dark granite plinth',(0,0,.10),(32,28,.20),'foundation','base')
    for tier,(w,d,z0,z1,floors) in enumerate(tiers):
        pitch=(z1-z0)/floors
        shape=footprint(w,d,tier)
        for edge,(a,b) in enumerate(zip(shape,shape[1:]+shape[:1])):
            dx,dy=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dy)
            face=C.Face((*a,0),(dx/L,dy/L,0),(-dy/L,dx/L,0),f'tier {tier} edge {edge}')
            bays=max(1,round(L/2.8));bay=L/bays
            has_windows=tier==0 or L>3.25
            holes=[]
            for floor in range(floors):
                for i in range(bays if has_windows else 0):
                    u=bay*(i+.5);z=z0+pitch*floor+(.22 if tier==0 and floor==0 else .48)
                    isdoor=tier==0 and floor==0 and i==bays//2
                    holes.append(dict(id=f'{face.label} floor {floor} bay {i}',u=u,z=z,
                        w=bay*(.73 if floor==0 else .48) if tier==0 else min(1.15,bay*.43),h=pitch-(.45 if tier==0 and floor==0 else .75),
                        cols=2 if tier==0 else 1,rows=2 if tier==0 else 1,frame='bronze' if tier==0 else 'trim',door=isdoor))
            if tier==0:
                B.open_wall(face,L,.2,pitch,[h for h in holes if h['z']<pitch],role='foundation',depth=.36)
                B.open_wall(face,L,pitch,z1,[h for h in holes if h['z']>=pitch],role='wall',depth=.36)
            else:B.open_wall(face,L,z0,z1,holes,role='wall',depth=.36)
            # Primary piers carry verticality through spandrels, with recessed
            # fields and fine flutes at terminations rather than a flat decal.
            for i in range(bays+1):
                u=min(L-.22,max(.22,i*bay))
                rise=(.95 if i in (0,bays) else .38) if tier else 0
                if tier:
                    face.part('terracotta vertical pier',u,-.13,(z0+z1+rise)/2,.64,.28,z1-z0+rise,'stone','vertical piers',0)
                else:
                    face.part('retail granite pier',u,-.13,pitch/2,.44,.28,pitch,'foundation','vertical piers',0)
                    face.part('cream mezzanine pier',u,-.13,pitch*1.5,.44,.28,pitch,'stone','vertical piers',0)
                if tier:
                    for offset in (-.21,-.105,0,.105,.21):face.part('gilded pier flute',u+offset,-.29,z1+rise-.60,.045,.03,1.10,'bronze','pier crowns',0)
            if tier:
                for floor in range(floors if has_windows else 0):
                    zz=z0+floor*pitch+.40
                    for i in range(bays):
                        u=bay*(i+.5)
                        face.part('recessed terracotta spandrel',u,-.025,zz,min(1.22,bay*.46),.08,.24,'stone','spandrel relief',0)
                        # Shallow stepped chevrons remain physical and legible.
                        for side in (-1,1):
                            C.beam('spandrel chevron',face.p(u+side*.38,-.075,zz+.10),face.p(u,-.075,zz-.1),.035,.025,'bronze','spandrel relief')
            for zz,thick in ((z1-.16,.13),(z1+.045,.12)):
                face.part('setback coping',L/2,-.045,zz,L+.22,.48,thick,'stone','weathering',0)
            if tier:
                for u in (.48,L-.48):
                    for step in range(3):
                        face.part('stepped corner pier capital',u,-.18-step*.055,z1+.12+step*.15,.96-step*.15,.58,.3,'stone','deco capitals',0)
                    for dx in (-.27,-.135,0,.135,.27):
                        face.part('gilded capital flute',u+dx,-.51,z1-.10,.06,.035,.96,'bronze','deco capitals',0)
            if tier==0:
                face.part('ornamental entrance frieze',L/2,-.13,7.35,L,.36,.46,'stone','retail cornice',0)
                for z in (7.09,7.61):face.part('gilded frieze bead',L/2,-.34,z,L,.10,.065,'bronze','retail cornice',0)
                for i in range(round(L/.68)):
                    u=.34+i*.68
                    for du,dz in ((-.22,0),(0,.17),(.22,0),(0,-.17)):
                        C.beam('geometric frieze diamond',face.p(u+du,-.35,7.35+dz),face.p(u+dz,-.35,7.35-du),.04,.04,'bronze','retail cornice')
            if tier in (1,2,3) and edge in (2,7,12,17):
                center=L/2;zz=z1+.13
                face.part('sunburst stone parapet',center,-.08,z1+.58,2.8,.42,1.35,'stone','sunburst relief',0)
                for j in range(13):
                    a=math.pi*j/12
                    C.beam('sunburst terracotta ray',face.p(center+.24*math.cos(a),-.32,zz+.24*math.sin(a)),
                        face.p(center+1.12*math.cos(a),-.32,zz+1.12*math.sin(a)),.09,.06,'bronze','sunburst relief')
        # Real floor slabs and occupied room depths behind the openings.
        for level in range(floors):
            z=z0+level*pitch+.16
            C.prism('occupied cross-plan storey slab',[(x*.988,y*.988) for x,y in shape],'z',z-.09,z+.09,'floor','occupied storeys')
            if tier:
                for y in (-d*.24,d*.24):box('office interior partition',(0,y,z+1.3),(w*.63,.14,2.6),'interior','occupied rooms')
        # Concave footprint follows each projecting centre bay and its shoulder
        # terraces. This closure is also the ceiling below the next tier.
        C.prism('cross-plan setback roof',shape,'z',z1-.02,z1+.04,'roof','setback roof')
    # Octagonal lantern: a closed optical enclosure inside gilded buttresses.
    z0=58.36;r=4.0
    ring=[(r*math.cos(math.pi/8+i*math.tau/8),r*math.sin(math.pi/8+i*math.tau/8)) for i in range(8)]
    C.prism('lantern seated stone base',ring,'z',58.22,59.0,'stone','lantern base')
    for i,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
        C.solid_surface('lantern optical bay',[(*a,59.0),(*b,59.0),(*b,64.1),(*a,64.1)],.025,'glass','lantern glazing')
        C.beam('gilded lantern buttress',(*a,58.5),(*a,64.3),.60,.60,'bronze','lantern frame')
        for z,size in ((59,.76),(63.75,.76),(64.25,.58)):
            box('stepped gilded buttress collar',(*a,z),(size,size,.30),'bronze','lantern frame')
        # Tapered shoulder cap continues the heavyweight vertical pier into
        # the polygonal crown, instead of stopping at a thin gazebo rail.
        C.prism('gilded buttress shoulder',[(a[0]-.26,a[1]-.26),(a[0]+.26,a[1]-.26),(a[0]+.26,a[1]+.26),(a[0]-.26,a[1]+.26)],'z',64.25,64.85,'bronze','lantern crown')
        for t in (.33,.66):
            x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t
            C.beam('lantern secondary mullion',(x,y,59),(x,y,64.1),.065,.065,'bronze','lantern frame')
        for z in (59.05,63.9):C.beam('lantern transom',(*a,z),(*b,z),.24,.24,'bronze','lantern frame')
        aa=(a[0]*.58,a[1]*.58);bb=(b[0]*.58,b[1]*.58)
        C.solid_surface('gilded sloping crown shoulder',[(*a,64.1),(*b,64.1),(*bb,66.1),(*aa,66.1)],.10,'bronze','lantern crown')
        C.solid_surface('gilded tapered crown cap',[(*aa,66.1),(*bb,66.1),(0,0,67.7)],.10,'bronze','lantern crown')
        C.beam('crown radial seam',(*a,64.17),(*aa,66.17),.15,.15,'bronze','lantern crown')
        C.beam('crown upper seam',(*aa,66.17),(0,0,67.77),.12,.12,'bronze','lantern crown')
    C.rod('terminal finial',(0,0,66.8),(0,0,68.6),.065,'bronze','crown finial')
    for x in (-5.2,5.2):
        for y in (-4.3,4.3):
            box('corner pinnacle base',(x,y,58.6),(.9,.9,1.2),'stone','pinnacles')
            C.rod('corner pinnacle',(x,y,59.1),(x,y,61.6),.20,'bronze','pinnacles',8)
            C.rod('pinnacle tip',(x,y,61.6),(x,y,62.15),.10,'bronze','pinnacles',8)
            # Centre of the actual diagonal octagon face, not an arbitrary
            # point outside it. A full structural receiver anchors each link.
            receiver=r*(math.cos(math.pi/8)+math.sin(math.pi/8))/2
            ax=math.copysign(receiver,x);ay=math.copysign(receiver,y)
            C.beam('lantern diagonal brace receiver',(ax,ay,58.85),(ax,ay,64.0),.28,.28,'bronze','lantern frame')
            C.beam('diagonal lantern pinnacle link',(ax,ay,60.2),(x,y,59.1),.16,.20,'bronze','pinnacle braces')
    # Source front entrance hierarchy, with supported canopy and legible lobby.
    box('entrance canopy',(0,-14.4,3.52),(5.4,1.0,.18),'bronze','entrance')
    for x in (-32/22,32/22):C.beam('canopy bracket',(x,-14.20,2.8),(x,-14.9,3.45),.06,.08,'bronze','entrance')
    for x in (-.16,.16):
        C.rod('entrance door pull',(x,-13.92,1.05),(x,-13.92,1.8),.026,'bronze','entrance doors')
        for z in (1.12,1.72):C.rod('door pull standoff',(x,-13.81,z),(x,-13.92,z),.018,'bronze','entrance doors')
    box('lobby desk',(0,-9,1.1),(3.4,1.1,1.0),'stone','lobby')
    B.label('TERRACOTTA',(0,-14.09,6.0),.34)
    C.qa_room_light('entry lobby',(0,-10,5.8),500,5)
    C.CONTACTS.extend([dict(name='occupied nested setbacks',status='Re-entrant cross-plan tiers retain projecting centre bays, closed shoulder terraces, narrow vertical openings, broad pier groups and staggered physical pier heads.'),
                       dict(name='gilded lantern',status='Octagonal enclosed glazed lantern, seated base, continuous crown and anchored finials.')])
