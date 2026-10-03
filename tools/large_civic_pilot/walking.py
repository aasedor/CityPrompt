"""Native, Z-up church circulation; derived from the authored floor and furniture."""
import json

def attach_church_walk(C,kind):
    triangles=[]
    def polygon(points,z=.04):
        for i in range(1,len(points)-1):triangles.append([[*points[0],z],[*points[i],z],[*points[i+1],z]])
    def rect(x0,y0,x1,y1,z=.04):polygon([(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z)
    if kind=='gothic':
        footprint=[28,60];entrance=[0,-28,.04]
        rect(-11.75,-21.2,11.75,18.9);rect(-1.55,-30,1.55,-20.5)
        polygon([(-7.35,18),(7.35,18),(7.35,23.8),(4.5,27.35),(-4.5,27.35),(-7.35,23.8)])
        obstacles=[[-14,-6.4,-23,-14.8,0,29]]
        portals=[[-1.55,1.55,-31,-27]]
        routes=[{'name':'Centre aisle and return','points':[[0,-28,.04],[0,21.5,.04],[0,-28,.04]]},
                {'name':'Right side aisle loop','points':[[0,-18,.04],[9,-18,.04],[9,15,.04],[0,15,.04],[0,-18,.04]]}]
    else:
        footprint=[42,48];entrance=[0,-22.5,.04]
        rect(-11.25,-18.35,11.25,18.35);rect(-1.8,-24,1.8,-18)
        # Annex visitor access follows its actual open connection.
        rect(10.8,7.2,13,10.8);rect(12.45,-.35,19.55,18.45)
        obstacles=[];portals=[[-1.8,1.8,-25,-21]]
        routes=[{'name':'Centre aisle and return','points':[[0,-22.5,.04],[0,15,.04],[0,-22.5,.04]]},
                {'name':'Side aisle and annex','points':[[0,-16,.04],[9,-16,.04],[9,9,.04],[16,9,.04],[9,9,.04]]}]
    for obj in C.objects():
        if obj.get('cityprompt_lego_module') not in ('pews','arcade','altar','annex furniture','portal structure'):continue
        verts=[v.co for v in obj.data.vertices]
        lo=[min(v[i] for v in verts) for i in range(3)];hi=[max(v[i] for v in verts) for i in range(3)]
        if lo[2]>1.8:continue
        obstacles.append([lo[0],hi[0],lo[1],hi[1],lo[2],hi[2]])
    network=dict(version=2,footprint=footprint,entrance=entrance,maxStepM=.18,triangles=triangles,obstacles=obstacles,portals=portals,routes=routes)
    floor=next(o for o in C.objects() if o.get('cityprompt_semantic_role')=='floor')
    floor['cityprompt_walking_json']=json.dumps(network,separators=(',',':'))
    return network
