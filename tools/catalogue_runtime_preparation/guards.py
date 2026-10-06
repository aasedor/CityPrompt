"""Bounded correction: guard infill carried by slab-seated structural posts."""
import math
import clay_core as C

ANCHORS=[]

def seated_guard(name,a,b,height=1.02,spacing=.105,role='trim',bottom=.07,end_posts=True):
    C.railing(name,a,b,height=height,spacing=spacing,role=role,bottom=bottom,end_posts=False)
    count=max(1,math.ceil(math.dist(a,b)/1.2))
    for i in range(count+1):
        p=tuple(a[j]+(b[j]-a[j])*i/count for j in range(3))
        if any(math.dist(p,q)<.145 for q in ANCHORS):continue
        ANCHORS.append(p)
        x,y,z=p
        C.box(name+' seated foot plate',(x,y,z),(.14,.14,.03),role,'guard load path',0)
        C.beam(name+' structural post',(x,y,z+.01),(x,y,z+height+.02),.04,.04,role,'guard load path',0)
        for dx in (-.045,.045):
            for dy in (-.045,.045):
                C.rod(name+' floor fixing',(x+dx,y+dy,z+.012),(x+dx,y+dy,z+.025),.008,role,'guard load path',6)
