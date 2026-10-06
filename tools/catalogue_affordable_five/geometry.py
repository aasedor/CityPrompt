"""Source-neutral roof and kitchen construction primitives; no building composition inherited."""
import math
import clay_core as C

def gable(name,cx,cy,w,d,eave,ridge,axis='x',role='roof',seams=False,gable_role='wall',fascia_role='trim',over=.20,flush_gable=False):
    # Build in a local system with ridge along x, then optionally rotate the assembly.
    before=set(C.objects())
    x0,x1=-w/2-over,w/2+over
    for yy in (-d/2-over,d/2+over):
        C.solid_surface(name+' roof plane',[(x0,0,ridge),(x1,0,ridge),(x1,yy,eave),(x0,yy,eave)],.14,role,name)
        if seams:
            for i in range(math.ceil(w/.42)+1):
                x=x0+(x1-x0)*i/math.ceil(w/.42)
                C.beam(name+' standing seam',(x,0,ridge+.02),(x,yy,eave+.02),.022,.025,role,name)
        C.beam(name+' seated eave fascia',(x0,yy,eave-.075),(x1,yy,eave-.075),.12,.14,fascia_role,name)
    C.beam(name+' ridge cap',(x0,0,ridge+.01),(x1,0,ridge+.01),.12,.08,role,name)
    inneredge=ridge-(ridge-eave)*(d/2)/(d/2+over)-.12
    for xx in (-w/2,w/2):
        if flush_gable:
            C.prism(name+' closed gable',[(-d/2,eave-.14),(d/2,eave-.14),(0,ridge-.14)],'x',xx if xx<0 else xx-.23,xx+.23 if xx<0 else xx,gable_role,name)
        else:C.prism(name+' closed gable',[(-d/2,eave-.15),(d/2,eave-.15),(d/2,inneredge),(0,ridge-.13),(-d/2,inneredge)],'x',xx-.11,xx+.11,gable_role,name)
        if name.startswith('Maple'):
            for i in range(1,math.ceil((ridge-eave)/.22)):
                z=eave+i*.22
                half=min(d/2,(d/2+over)*(ridge-.14-z)/(ridge-eave))
                if half>.01:C.box('Gable clapboard lip',(xx+math.copysign(.119,xx),0,z),(.022,half*2,.018),'wall','gable cladding',0)
        for yy in (-d/2-over,d/2+over):C.beam(name+' rake fascia',(xx+(over if xx>0 else -over),0,ridge-.06),(xx+(over if xx>0 else -over),yy,eave-.06),.13,.13,fascia_role,name)
    for obj in set(C.objects())-before:
        if axis=='y':obj.rotation_euler.z=math.pi/2
        obj.location.x+=cx;obj.location.y+=cy
    C.bpy.context.view_layer.update()

def kitchen(x,y,z,w=3.2):
    C.box('Kitchen cupboards',(x,y,z+.45),(w,.65,.9),'timber','kitchen')
    C.box('Kitchen counter',(x,y,z+.925),(w+.08,.70,.05),'pale','kitchen')
    C.box('Kitchen sink',(x+.5,y,z+.956),(.62,.42,.012),'hardware','kitchen')
    C.rod('Kitchen tap',(x+.5,y+.22,z+.94),(x+.5,y+.22,z+1.23),.018,'hardware','kitchen')
    C.rod('Kitchen tap spout',(x+.5,y+.22,z+1.23),(x+.5,y,z+1.23),.018,'hardware','kitchen')
    C.box('Refrigerator',(x-w/2-.42,y,z+.95),(.75,.72,1.9),'pale','kitchen')
