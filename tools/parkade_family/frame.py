"""Native metric parking-frame recipe. Each family adds its own authored signature."""
import math
import build as P
import clay_core as C
from layout import frame_plan,partition


def stair_tower(cx,f):
    front=f['frontY'];back=front+6.55;datums=f['datums'];height=f['towerHeight']
    for x in (cx-2.3,cx+2.3):
        for y in (front+.15,back):C.box('Core structural corner',(x,y,(height+.15)/2),(.14,.14,height-.15),'steel','stair frame',0)
    for i,z in enumerate(datums):
        P.plate('Recessed full-level stair landing',(cx-2.25,cx+2.25,front+.25,front+1.65),z,.15,'concrete')
        bridge=(cx-2.65,cx-2.25,front+.25,front+1.65) if cx>0 else (cx+2.25,cx+2.65,front+.25,front+1.65)
        P.plate('Continuous inner doorway bridge',bridge,z,.15,'concrete')
        if i<len(datums)-1:
            mid=z+1.65
            P.plate('Intermediate stair landing',(cx-2.25,cx+2.25,front+4.95,front+6.5),mid,.18,'concrete')
            P.flight('Stair ascending',cx-.95,front+1.65,front+4.95,z,mid)
            P.flight('Stair returning',cx+.95,front+4.95,front+1.65,mid,datums[i+1])
            P.guard('Landing guard',(cx-2.15,front+6.42,mid),(cx+2.15,front+6.42,mid))
        top=z+3.20 if i<len(datums)-1 else height-.20
        for y in (front+.15,back):
            for a,b in [(cx-2.3,cx-.8),(cx-.8,cx+.8),(cx+.8,cx+2.3)]:
                bottom=z+2.4 if i==0 and y==front+.15 and a==cx-.8 else z+.12
                if top>bottom:C.box('Transparent core pane',((a+b)/2,y,(bottom+top)/2),(b-a-.08,.012,top-bottom),'glass','stair glazing',0)
            C.box('Core horizontal transom',(cx,y,z+.04),(4.6,.14,.08),'steel','stair frame',0)
        for x in (cx-2.3,cx+2.3):
            inward=(x==cx+2.3 if cx<0 else x==cx-2.3)
            for a,b in [(front+.15,front+1.6),(front+1.6,front+3.25),(front+3.25,front+4.9),(front+4.9,back)]:
                bottom=z+2.4 if inward and a==front+.15 else z+.12
                if top>bottom:C.box('Side optical stair pane',(x,(a+b)/2,(bottom+top)/2),(.012,b-a-.08,top-bottom),'glass','stair glazing',0)
            C.box('Side core transom',(x,front+3.35,z+.04),(.14,6.4,.08),'steel','stair frame',0)
    for x in (cx-2.3,cx-.8,cx+.8,cx+2.3):C.box('Front core mullion',(x,front+.15,(height+.15)/2),(.06,.12,height-.15),'steel','stair frame',0)
    for x in (cx-2.3,cx+2.3):
        for y in (front+1.6,front+3.25,front+4.9):C.box('Side core mullion',(x,y,(height+.15)/2),(.12,.06,height-.15),'steel','stair frame',0)
    P.plate('Seated core cap',(cx-2.4,cx+2.4,front+.05,front+6.65),height,.18,'steel')
    P.text('Core parking letter','P',(cx,front+.06,height-1.2),.65)


def standard_frame(width,depth,levels,courtyard=None,marking_exclusions=None,roof_lights=True):
    f=frame_plan(width,depth,levels);h=width/2;front=f['frontY'];rear=f['rearY'];top=f['top']
    cores=[(-h,-h+4.9,front,front+6.6),(h-4.9,h,front,front+6.6)]
    holes=[courtyard] if courtyard else []
    for rect in partition((-h,h,front,rear),holes):P.plate('Ground slab',rect,.15,.15)
    for z in f['datums'][1:]:
        for rect in partition((-h,h,front,rear-6.5),cores+holes):P.plate('Open-well parking deck',rect,z)
        for rect in [(-h,-h+7,rear-6.5,rear),(h-7,h,rear-6.5,rear)]:P.plate('Ramp landing',rect,z)
    ys=sorted(set([front+.25,-5.25,5.25]+([rear-12.75] if depth>36 else [])))
    xs=sorted(set([-h+.25,h-.25]+f['frontColumns']))
    def in_void(x,y):return courtyard and courtyard[0]-.26<x<courtyard[1]+.26 and courtyard[2]-.26<y<courtyard[3]+.26
    for x in xs:
        for y in ys:
            if (abs(x)>h-5 and y<front+6.6) or (y!=ys[0] and h-7.25<abs(x)<h-1) or in_void(x,y):continue
            end=top+1.1 if abs(x)>h-1 or y==ys[0] else top-.01
            C.box('Ground-bearing frame column',(x,y,(.15+end)/2),(.5,.5,end-.15),'concrete','frame',0)
    for x in (-h+.25,h-.25):C.box('Rear landing column',(x,rear-.25,(.15+top+1.1)/2),(.5,.5,top+1.1-.15),'concrete','frame',0)
    for z in f['datums'][1:]:
        for y in ys:
            span=(-h+4.8,h-4.8) if y==ys[0] else (-h,h)
            beamholes=[]
            if courtyard and courtyard[2]-.25<y<courtyard[3]+.25:beamholes=[(courtyard[0],courtyard[1],y-.25,y+.25)]
            for a,b,c,d in partition((span[0],span[1],y-.24,y+.24),beamholes):C.box('Partitioned deck beam',((a+b)/2,(c+d)/2,z-.32),(b-a,d-c,.5),'concrete','frame',0)
        for x in (-h+.25,h-.25):C.box('Side beam behind glass core',(x,(front+6.6+rear)/2,z-.32),(.5,rear-front-6.6,.5),'concrete','frame',0)
    ax,bx=f['rampX'];ay,by=f['rampY'];run=bx-ax
    for i,(za,zb) in enumerate(zip(f['datums'],f['datums'][1:])):
        C.solid_surface('Continuous vehicle ramp',[(ax,ay,za),(bx,ay,zb),(bx,by,zb),(ax,by,za)],.15,'deck','vehicle ramps')
        for y in (ay+.06,by-.06):P.guard('Continuous ramp guard',(ax,y,za),(bx,y,zb))
        for y in (ay+.1,by-.1):
            t0,t1=za-.15,zb-.15
            section=[(ax,t0),(bx,t1),(bx,t1-.45)]
            section+= [(ax+(.45-t0)/3.3*run,0),(ax,0)] if t0<.45 else [(ax,t0-.45)]
            if section[0]==section[-1]:section.pop()
            C.prism('Ramp longitudinal support',section,'y',y-.09,y+.09,'concrete','ramp supports')
        for y in (ay+.45,by-.45):C.solid_surface('Ramp edge paint',[(ax,y-.04,za+.006),(bx,y-.04,zb+.006),(bx,y+.04,zb+.006),(ax,y+.04,za+.006)],.003,'yellow','road markings')
    for x in (ax,ax/2,0,bx/2,bx):
        height=f['datums'][-2]+3.3*(x-ax)/run-.15
        for y in (ay+.1,by-.1):C.box('Ground-bearing ramp pier',(x,y,height/2),(.18,.18,height),'concrete','ramp supports',0)
    for z in f['datums'][1:]:
        P.guard('Open front guard',(-h+5,front+.2,z),(h-5,front+.2,z))
        for a,b in [(-h+.2,ax),(bx,h-.2)]:P.guard('Rear landing guard',(a,rear-.15,z),(b,rear-.15,z))
        P.guard('Rear well edge',(ax,rear-6.57,z),(bx,rear-6.57,z))
        for x in (-h+.2,h-.2):P.guard('Open side guard',(x,front+6.7,z),(x,rear-.15,z))
    def excluded(rect,level):
        reserves=list(holes)+cores
        if level==0:reserves.append((f['entryX']-3,f['entryX']+3,front,front+6.5))
        for ex in marking_exclusions or []:
            if isinstance(ex,dict):
                if level in ex.get('levels',range(levels)):reserves.append(ex['rect'])
            elif level==0:reserves.append(ex)
        return any(rect[0]<p[1] and rect[1]>p[0] and rect[2]<p[3] and rect[3]>p[2] for p in reserves)
    for level,z in enumerate(f['datums']):
        # 6m side circulation and complete fixed 2.7m bays only.
        for ya in (front+1,-5.5,0):
            yb=ya+5.5
            count=math.floor((width-14)/2.7);left=-count*2.7/2
            for i in range(count):
                a=left+i*2.7;b=a+2.7
                if excluded((a,b,ya,yb),level):continue
                for x in (a,b):C.box('Fixed parking stall stripe',(x,(ya+yb)/2,z+.006),(.075,5.5,.006),'marking','road markings',0)
                C.box('Parking row head',((a+b)/2,ya,z+.006),(2.7,.075,.006),'marking','road markings',0)
    for cx in (-h+2.5,h-2.5):stair_tower(cx,f)
    entry=f['entryX']
    C.box('Vehicle portal sign',(entry,front+.12,2.95),(5.45,.2,.65),'sign','wayfinding',0)
    P.text('Entrance lettering','ENTRANCE',(entry,front+.015,2.77),.40)
    for x in (entry-2.55,entry+2.55):C.box('Entrance jamb',(x,front+.18,1.3875),(.12,.12,2.475),'yellow','wayfinding',0)
    C.box('Portal lintel',(entry,front+.18,2.625),(5.22,.12,.12),'yellow','wayfinding',0)
    if roof_lights:
        for x in (-width*.25,width*.25):
            for y in (0,9.5):
                C.rod('Roof light mast',(x,y,top),(x,y,top+2.45),.045,'steel','roof equipment',8)
                C.box('Roof light head',(x,y,top+2.45),(.65,.2,.07),'steel','roof equipment',0)
    return f
