"""Navigation surfaces follow the physical floor/tread datums, in native Z-up."""
import json
import geometry_core as C

def attach(kind):
    triangles=[];obstacles=[];routes=[]
    def rect(x0,y0,x1,y1,z):
        a=[x0,y0,z];b=[x1,y0,z];c=[x1,y1,z];d=[x0,y1,z]
        triangles.extend([[a,b,c],[a,c,d]])
    school=kind=='school'
    sx,sy,w,rise,levels=(-5,4.2,1.25,3.8,3) if school else (0,-4.9,1.05,3.45,2)
    left,right,bottom,top=(-13.6,3.6,-10.6,10.6) if school else (-7.6,7.6,-6.6,6.6)
    holeleft,holeright=sx-w*1.24,sx+w*1.24
    for level in range(levels):
        z=.14+rise*level
        # Perimeter of the actual stair void; no hidden floor beneath flights.
        if not school and level:
            rect(left,bottom,-1.08,-5.7,z);rect(1.08,bottom,right,-5.7,z)
            rect(left,-5.7,right,sy-.15,z)
        else:rect(left,bottom,right,sy-.15,z)
        rect(left,sy-.15,holeleft,sy+4.25,z)
        rect(holeright,sy-.15,right,sy+4.25,z)
        rect(left,sy+4.25,right,top,z)
        if level:rect(holeleft,sy-.95,holeright,sy-.125,z)
        if level<levels-1:
            for i in range(11):
                y0=sy+i*.25-.135;y1=y0+.27
                rect(sx-w*1.05,y0,sx-w*.05,y1,z+(i+1)*rise/22)
                rect(sx+w*.05,y0,sx+w*1.05,y1,z+rise-(i)*rise/22)
            rect(sx-w*1.05,sy+2.625,sx+w*1.05,sy+3.675,z+rise/2)
            pts=[[sx-w*.55,sy-.35,z],[sx-w*.55,sy+2.8,z+rise/2],[sx+w*.55,sy+2.8,z+rise/2],[sx+w*.55,sy-.35,z+rise]]
            routes.append(dict(name=f'Stair {level+1} ascent',points=pts))
            routes.append(dict(name=f'Stair {level+1} descent',points=list(reversed(pts))))
    if school:
        entrance=[-1.9,-15,.04];footprint=[32,30]
        rect(-4,-15.1,.2,-11,.04);rect(-4,-11,.2,-9.5,.14)
        rect(3.5,-1.3,4.5,.3,.14);rect(4.4,-10.5,13.6,10.5,.18)
        portals=[[-4,.2,-15.5,-14.5]]
        routes.extend([dict(name='Entrance to gym',points=[entrance,[-1.9,-8,.14],[-1.9,-.5,.14],[9,-.5,.18]]),
                       dict(name='Ground classroom',points=[[-1.9,0,.14],[-7.67,0,.14],[-7.67,-3.6,.14]])])
        for level in range(3):
            z=.14+level*3.8
            rooms=[(-10.275,6.65),(-3.45,7),(1.825,3.55)] if level else [(-10.275,6.65)]
            for x,width in rooms:
                door=x+width/2-.72
                obstacles.extend([[x-width/2,door-.475,-2.93,-2.8,z,z+3.2],[door+.475,x+width/2,-2.93,-2.8,z,z+3.2]])
            for x in ([-6.95,.05] if level else [-6.95]):obstacles.append([x-.06,x+.06,-10.625,-2.875,z,z+3.2])
        obstacles.extend([[3.64,4,-10.7,-1.4,.14,8],[3.64,4,.4,10.7,.14,8]])
    else:
        entrance=[0,-11,.04];footprint=[20,22]
        rect(-.4,-11.1,.9,-7,.04);rect(-.4,-7,.9,-6.5,.14)
        portals=[[-.4,.9,-11.5,-10.5]]
        routes.append(dict(name='Entry to ground apartments',points=[entrance,[.4,-5.7,.14],[1.5,-5.7,.14],[1.5,1,.14],[3,1,.14]]))
        for level in range(2):
            z=.14+level*3.45
            for s in (-1,1):
                x=s*1.9
                obstacles.extend([[x-.13,x+.13,-6.6,.5,z,z+3.25],[x-.13,x+.13,1.5,6.6,z,z+3.25]])
                c=s*4.8
                obstacles.extend([[c-2.7,c-.475,3.45,3.57,z,z+3.1],[c+.475,c+2.7,3.45,3.57,z,z+3.1]])
                bx=s*3.05
                obstacles.extend([[bx-.85,bx-.75,1.75,3.45,z,z+3.1],[bx+.75,bx+.85,1.75,3.45,z,z+3.1],
                                  [bx-.8,bx-.475,1.75,1.85,z,z+3.1],[bx+.475,bx+.8,1.75,1.85,z,z+3.1]])
                routes.append(dict(name=f'Dwelling {level*2+(1 if s<0 else 2)} doorway',points=[[1.5,-.4,z],[0,1,z],[s*3,1,z]]))
                unit=level*2+(1 if s<0 else 2)
                routes.append(dict(name=f'Dwelling {unit} bedroom',points=[[s*3,1,z],[s*3,.65,z],[s*4.8,.65,z],[s*4.8,3.75,z]]))
                routes.append(dict(name=f'Dwelling {unit} bathroom',points=[[s*3,1,z],[bx+.2,1.4,z],[bx+.2,2.1,z]]))
    # Furniture volume is real mesh extent, not an arbitrary walk prohibition.
    for o in C.objects():
        if o.get('cityprompt_lego_module') not in ('furniture','interior'):continue
        if any(k in o.name for k in ('ceiling','luminaire','diffuser','back','curtain')):continue
        vs=[o.matrix_world@v.co for v in o.data.vertices]
        lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)]
        if hi[2]-lo[2]>.015:obstacles.append([lo[0],hi[0],lo[1],hi[1],lo[2],hi[2]])
    n=dict(version=2,footprint=footprint,entrance=entrance,maxStepM=.18,triangles=triangles,obstacles=obstacles,portals=portals,routes=routes)
    return n

def embed(network):
    obj=next(o for o in C.objects() if o.get('cityprompt_semantic_role')=='floor')
    obj['cityprompt_walking_json']=json.dumps(network,separators=(',',':'))
