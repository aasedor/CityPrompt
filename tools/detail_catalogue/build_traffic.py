"""Ten static, metric traffic-planning details. No provider calls.

Run --dry-run with Python; run Blender -b --python this_file -- --output PATH
for one --id pilot or the bounded ten-object batch. Output must be a fresh
external directory. Source geometry is Z-up; GLB export converts to Y-up.
"""
import argparse
import json
import math
from pathlib import Path
import sys

SPECS = [
    ('traffic-signal', 'Traffic signal', 'Three-lens signal on a roadside pole. Rotate its face toward approaching traffic; static display.'),
    ('pedestrian-signal', 'Pedestrian signal', 'Crossing signal with a push button and illuminated walk symbol; static display.'),
    ('stop-sign', 'Stop sign', 'Octagonal STOP sign for a proposed intersection approach.'),
    ('yield-sign', 'Yield sign', 'Triangular yield sign for a proposed junction or shared access.'),
    ('speed-limit-30', 'Speed limit · 30 km/h', 'A 30 km/h MAXIMUM sign for a proposed low-speed street.'),
    ('no-entry-sign', 'Do not enter sign', 'Red disc and white bar to indicate a restricted approach.'),
    ('speed-hump', 'Speed hump', 'Rounded asphalt traffic-calming hump, 3.6 m across and 3.7 m along travel, 0.10 m high.'),
    ('raised-crossing', 'Raised pedestrian crossing', 'Six-metre-wide raised zebra crossing with approach ramps; 0.15 m high.'),
    ('flexible-bollard', 'Flexible delineator bollard', 'Reflective lane separator for cycling edges, traffic islands and restricted vehicle access.'),
    ('traffic-cone', 'Traffic cone', 'Orange cone with reflective bands for a temporary traffic or construction layout.'),
]


def build(kind, S, bpy):
    def post(height=2.7):
        S.box('base plate', (0, 0, .025), (.24, .24, .05), 'steel')
        S.beam('galvanized post', (0, 0, .025), (0, 0, height), .035, 'steel', 12)

    def polygon(name, points, y, mat):
        return S.mesh(name, [(x, y, z) for x, z in points], [tuple(range(len(points)))], mat)

    def disc(name, x, z, radius, mat, y=-.105, sides=32):
        S.beam(name, (x, y+.018, z), (x, y, z), radius, mat, sides)

    def label(words, z, size, mat='white', y=-.115):
        curve = bpy.data.curves.new('sign lettering', 'FONT')
        curve.body = words; curve.align_x = 'CENTER'; curve.align_y = 'CENTER'
        curve.size = size; curve.extrude = .001; curve.resolution_u = 3
        obj = bpy.data.objects.new('sign lettering', curve)
        bpy.context.collection.objects.link(obj)
        obj.location = (0, y, z); obj.rotation_euler = (math.pi/2, 0, 0)
        obj.data.materials.append(S.MATS[mat])
        bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True)
        bpy.context.view_layer.objects.active = obj; bpy.ops.object.convert(target='MESH')

    if kind in ('traffic-signal', 'pedestrian-signal'):
        post(3.3 if kind == 'traffic-signal' else 2.85)
        for z in (2.25, 2.85): S.box('pole bracket', (0, -.07, z), (.12, .18, .08), 'steel')
        if kind == 'traffic-signal':
            S.box('signal backplate', (0, -.16, 2.65), (.52, .06, 1.23), 'yellow')
            S.box('signal housing', (0, -.22, 2.65), (.34, .18, 1.09), 'black')
            for z, color in ((2.99, 'red'), (2.65, 'amber-dark'), (2.31, 'green-dark')):
                disc('signal lens', 0, z, .125, color, -.322)
                S.box('lens hood', (0, -.39, z+.14), (.30, .28, .035), 'black')
        else:
            S.box('pedestrian signal', (0, -.18, 2.62), (.43, .22, .49), 'yellow')
            S.box('dark face', (0, -.295, 2.62), (.365, .015, .42), 'black')
            disc('walk head', 0, 2.75, .033, 'white', -.31, 16)
            for a, b in [((0,2.70),(0,2.58)), ((0,2.67),(-.10,2.61)), ((0,2.67),(.08,2.58)), ((0,2.58),(-.08,2.46)), ((0,2.58),(.08,2.49))]:
                S.beam('walk symbol', (a[0],-.312,a[1]), (b[0],-.312,b[1]), .014, 'white', 6)
            S.box('push button box', (0, -.09, 1.10), (.14, .12, .20), 'yellow')
            disc('push button', 0, 1.10, .04, 'black', -.158, 16)
    elif kind.endswith('sign') or kind == 'speed-limit-30':
        post()
        if kind == 'stop-sign':
            for radius, mat, y in ((.405,'white',-.08),(.375,'red',-.085)):
                polygon('octagonal sign', [(radius*math.cos(math.pi/8+i*math.tau/8),2.35+radius*math.sin(math.pi/8+i*math.tau/8)) for i in range(8)], y, mat)
            label('STOP', 2.35, .235)
        elif kind == 'yield-sign':
            polygon('yield border', [(-.45,2.7),(0,1.94),(.45,2.7)], -.08, 'red')
            polygon('yield face', [(-.34,2.63),(0,2.05),(.34,2.63)], -.085, 'white')
            label('YIELD', 2.44, .14, 'black')
        elif kind == 'no-entry-sign':
            disc('white border', 0, 2.35, .39, 'white', -.08)
            disc('red face', 0, 2.35, .365, 'red', -.10)
            S.box('white horizontal bar', (0,-.12,2.35), (.56,.012,.13), 'white')
        else:
            S.box('sign border', (0,-.08,2.32), (.62,.035,.80), 'black')
            S.box('sign face', (0,-.10,2.32), (.58,.012,.76), 'white')
            label('MAXIMUM',2.59,.088,'black',-.112)
            label('30',2.31,.40,'black',-.112)
            label('km/h',2.05,.08,'black',-.112)
    elif kind in ('speed-hump', 'raised-crossing'):
        width, length, height = (3.6,3.7,.10) if kind == 'speed-hump' else (6,4,.15)
        def profile(y):
            t=(y+length/2)/length
            return height*math.sin(math.pi*t)**2 if kind == 'speed-hump' else height*min(1,t*4,(1-t)*4)
        n=32; verts=[]
        for i in range(n+1):
            y=-length/2+i*length/n
            verts += [(-width/2,y,profile(y)),(width/2,y,profile(y))]
        S.mesh('ramped asphalt surface',verts,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(n)],'asphalt')
        for x in (-width/2,width/2):
            for i in range(n):
                y=-length/2+i*length/n; yy=y+length/n
                S.mesh('closed ramp edge',[(x,y,0),(x,yy,0),(x,yy,profile(yy)),(x,y,profile(y))],[(0,1,2,3)],'asphalt')
        for x in ([-1.2,0,1.2] if kind == 'speed-hump' else [-2.5,-1.5,-.5,.5,1.5,2.5]):
            w=.22 if kind=='speed-hump' else .5
            for i in range(4,n-4):
                y=-length/2+i*length/n; yy=y+length/n
                S.mesh('reflective crossing marking',[(x-w/2,y,profile(y)+.002),(x+w/2,y,profile(y)+.002),(x+w/2,yy,profile(yy)+.002),(x-w/2,yy,profile(yy)+.002)],[(0,1,2,3)],'white')
    elif kind == 'flexible-bollard':
        S.beam('rubber base',(0,0,0),(0,0,.055),.15,'black',20)
        S.beam('flexible post',(0,0,.055),(0,0,.94),.045,'orange',16)
        for z in (.64,.78):S.beam('reflective collar',(0,0,z),(0,0,z+.07),.046,'white',16)
    elif kind == 'traffic-cone':
        S.box('rubber foot',(0,0,.025),(.42,.42,.05),'black')
        for bottom,top,mat in ((.05,.30,'orange'),(.30,.40,'white'),(.40,.51,'orange'),(.51,.61,'white'),(.61,.74,'orange')):
            vertices=[((.17-.145*z/.74)*math.cos(i*math.tau/24),(.17-.145*z/.74)*math.sin(i*math.tau/24),z) for z in (bottom,top) for i in range(24)]
            S.mesh('cone band',vertices,[(i,(i+1)%24,(i+1)%24+24,i+24) for i in range(24)]+[tuple(range(24,48))],mat)
    else:
        raise ValueError(kind)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--id', choices=[s[0] for s in SPECS])
    parser.add_argument('--dry-run', action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else None)
    specs=[s for s in SPECS if not args.id or args.id==s[0]]
    if args.dry_run:
        print(json.dumps({'objects':[s[0] for s in specs], 'paid_calls':0})); return
    import bpy
    from mathutils import Vector
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'public_realm_assets'))
    import scene as S
    args.output.mkdir(parents=True,exist_ok=False)
    palette={'steel':(.42,.47,.49),'black':(.018,.022,.026),'white':(.91,.93,.89),
             'red':(.72,.018,.016),'yellow':(.94,.56,.015),'orange':(.98,.17,.012),
             'amber-dark':(.17,.075,.012),'green-dark':(.012,.085,.042),'asphalt':(.065,.07,.073)}
    for name,color in palette.items():
        m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
        node=m.node_tree.nodes['Principled BSDF'];node.inputs['Base Color'].default_value=(*color,1)
        node.inputs['Roughness'].default_value=.45 if name=='steel' else .72
        m.use_backface_culling=False;S.MATS[name]=m
    S.MATS['kit']=bpy.data.materials.new('unused kit')
    catalogue=[]
    for id,label,description in specs:
        bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
        build(id,S,bpy);bpy.context.view_layer.update()
        objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
        bounds=[o.matrix_world @ Vector(v) for o in objects for v in o.bound_box]
        low=[min(v[i] for v in bounds) for i in range(3)];high=[max(v[i] for v in bounds) for i in range(3)]
        dims=[round(high[i]-low[i],4) for i in range(3)]
        path=args.output/(id+'.glb');info=S.export(path,objects)
        triangles=0
        for o in objects:o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
        catalogue.append(dict(id='detail-'+id,label=label,category='Traffic & safety',description=description,
            dimensions=dims,url='/street-kits/traffic-safety-v1/'+id+'.glb',color='#e6b828',kind='object',
            offset=[round(-(low[0]+high[0])/2,5),round(-low[2],5),round((low[1]+high[1])/2,5)],
            sourceKit='traffic-safety-v1',sha256=info['sha256'],triangles=triangles,
            meshes=len({o.data.materials[0].name for o in objects}),bytes=info['bytes']))
    (args.output/'catalogue.json').write_text(json.dumps(catalogue,indent=2)+'\n')
    print(json.dumps({'built':len(catalogue),'bytes':sum(m['bytes'] for m in catalogue)}))


if __name__=='__main__':main()
