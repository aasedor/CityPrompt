"""Bounded Calgary-inspired concept assets; Blender, no paid services.

Native recipe: metre/Z-up, road root at zero; GLB export is +Y up.
No bounding-box recentring. All dimensions except the cited 3 ft post are
illustrative. Run Python --dry-run, then Blender -b --python FILE -- --output DIR.
"""
import argparse
import json
import math
from pathlib import Path
import sys

SPECS = [
    ('speed-cushion', 'Speed cushion', 'Speed cushions', 'Single · 1.8 × 3.4 m', 'speed-cushion-speed-hump'),
    ('speed-cushion-pair', 'Speed cushion pair', 'Speed cushions', 'Pair · 0.8 m gap', 'speed-cushion-speed-hump'),
    ('school-crossing-sign', 'In-street school crossing sign', 'School crossing reminders', 'Two faces · concept', 'elementary-schools-traffic-study'),
    ('left-turn-calming', 'Left-turn calming assembly', 'Left-turn calming', 'Rubber separators + yellow post', 'left-turn-calming'),
    ('high-visibility-crossing', 'High-visibility crossing sign', 'High-visibility crossing signs', 'Fluorescent border · concept', 'safety'),
    ('green-bike-box', 'Green bike box', 'Cycling markings', '6 × 3 m · concept', 'bike-signage-signals'),
    ('green-conflict-strip', 'Green cycling conflict strip', 'Cycling markings', '2 × 6 m · dashed', 'bike-signage-signals'),
    ('bicycle-signal', 'Bicycle signal', 'Bicycle signals', 'Unlit · static', 'bike-signage-signals'),
    ('traffic-diverter', 'Planter traffic diverter', 'Traffic diverters', 'Fixed assembly · concept', 'neighbourhood-streets-elements'),
    ('speed-display-trailer', 'Portable speed-display trailer', 'Speed displays', 'Static illustrative 30', 'neighbourhood-streets-policy'),
]


def source_url(slug):
    if slug.startswith('neighbourhood-'):
        return 'https://www.calgary.ca/planning/transportation/' + slug + '.html'
    return 'https://www.calgary.ca/roads/' + ('safety.html' if slug == 'safety' else 'safety/' + slug + '.html')


def cushion_height(x, y):
    return .075 * max(0, min(1, (.9 - abs(x)) / .25, (1.7 - abs(y)) / .9))


def build(kind, S, bpy):
    def box(name, pos, size, mat, bevel=.006):
        obj = S.box(name, pos, size, mat)
        if bevel:
            mod = obj.modifiers.new('manufactured edge', 'BEVEL')
            mod.width = min(bevel, min(size)/4); mod.segments = 2
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier=mod.name)
        return obj

    def text(words, x, y, z, size, mat='white'):
        curve = bpy.data.curves.new('static lettering', 'FONT')
        curve.body = words; curve.align_x = 'CENTER'; curve.align_y = 'CENTER'
        curve.size = size; curve.resolution_u = 2
        obj = bpy.data.objects.new('static lettering ' + words, curve)
        bpy.context.collection.objects.link(obj)
        obj.location = (x, y, z); obj.rotation_euler = (math.pi/2, 0, 0)
        obj.data.materials.append(S.MATS[mat])
        bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True)
        bpy.context.view_layer.objects.active = obj; bpy.ops.object.convert(target='MESH')

    def face_line(name, a, b, y, width, mat):
        return S.beam(name, (a[0], y, a[1]), (b[0], y, b[1]), width/2, mat, 8)

    def circle(name, x, y, z, r, mat, axis='Y'):
        a, b = ((x,y+.008,z),(x,y,z)) if axis == 'Y' else ((x-.006,y,z),(x+.006,y,z))
        return S.beam(name, a, b, r, mat, 24)

    def walker(x, y, z, size, mat='black'):
        circle('pedestrian head', x+.08*size, y, z+.35*size, .075*size, mat)
        for a,b in [((.06,.24),(-.02,.0)), ((.02,.17),(-.22,.08)), ((.02,.17),(.22,.02)),
                    ((-.02,0),(-.20,-.32)), ((-.02,0),(.21,-.24))]:
            face_line('pedestrian pictogram', (x+a[0]*size,z+a[1]*size), (x+b[0]*size,z+b[1]*size), y, .065*size, mat)

    def bike_segments(scale=1):
        lines=[]
        for cx in (-.42,.42):
            for i in range(24):
                a=i*math.tau/24; b=(i+1)*math.tau/24
                lines.append(((cx+.26*math.cos(a),.26*math.sin(a)), (cx+.26*math.cos(b),.26*math.sin(b))))
        lines += [((-.42,0),(-.17,.43)), ((-.17,.43),(.05,0)), ((.05,0),(-.42,0)),
                  ((-.17,.43),(.28,.43)), ((.28,.43),(.05,0)), ((.42,0),(.23,.62)),
                  ((.23,.62),(.43,.62)), ((-.27,.45),(-.07,.45))]
        return [((a[0]*scale,a[1]*scale),(b[0]*scale,b[1]*scale)) for a,b in lines]

    def post(height):
        box('anchor plate',(0,0,.02),(.22,.22,.04),'steel',.008)
        S.beam('galvanized round post',(0,0,.04),(0,0,height),.035,'steel',16)
        for x in (-.075,.075):
            for y in (-.075,.075): S.beam('anchor nut',(x,y,.04),(x,y,.05),.012,'dark-steel',6)

    def delineator(x,y,height=.9144,mat='yellow'):
        box('delineator base',(x,y,.025),(.20,.27,.05),'rubber',.025)
        S.beam('flexible marker',(x,y,.05),(x,y,height),.04,mat,16)
        for z in (height-.18,height-.31): S.beam('reflective band',(x,y,z),(x,y,z+.07),.041,'white',16)

    if kind.startswith('speed-cushion'):
        for cx in ([-1.3,1.3] if kind.endswith('pair') else [0]):
            xs=[-.9,-.65,.65,.9]; ys=[-1.7,-.8,.8,1.7]
            verts=[(cx+x,y,cushion_height(x,y)) for y in ys for x in xs]
            faces=[(j*4+i,j*4+i+1,(j+1)*4+i+1,(j+1)*4+i) for j in range(3) for i in range(3)]
            faces += [(0,4,8,12,13,14,15,11,7,3,2,1)]
            S.mesh('closed asphalt cushion',verts,faces,'asphalt')
            for sign in (-1,1):
                for side in (-1,1):
                    # Paint follows the ramp, never floats above a flat proxy.
                    for i in range(12):
                        t=i/12; u=(i+1)/12
                        x=side*(.48-.48*t); xx=side*(.48-.48*u)
                        y=sign*(1.48-.65*t); yy=sign*(1.48-.65*u)
                        w=.045
                        S.mesh('cushion chevron',[(cx+x-w,y,cushion_height(x-w,y)+.004),(cx+x+w,y,cushion_height(x+w,y)+.004),
                            (cx+xx+w,yy,cushion_height(xx+w,yy)+.004),(cx+xx-w,yy,cushion_height(xx-w,yy)+.004)],[(0,1,2,3)],'white')
    elif kind == 'school-crossing-sign':
        box('weighted rubber foot',(0,0,.045),(.48,.65,.09),'rubber',.04)
        box('flexible centre spine',(0,0,.58),(.08,.04,1.02),'yellow-green',.008)
        box('two-sided fluorescent board',(0,0,.72),(.34,.065,.94),'yellow-green',.025)
        for sign in (-1,1):
            before=set(bpy.context.scene.objects)
            box('white sign insert',(0,-.039,.72),(.275,.012,.80),'white',.012)
            S.mesh('yield triangle', [(-.10,-.048,1.02),(.10,-.048,1.02),(0,-.048,.85)],[(0,1,2)],'red')
            S.mesh('yield white centre', [(-.071,-.05,1.002),(.071,-.05,1.002),(0,-.05,.882)],[(0,1,2)],'white')
            walker(0,-.052,.64,.40)
            for z in (.43,.39): box('crossing baseline',(0,-.052,z),(.19,.006,.014),'black',0)
            if sign == 1:
                for obj in set(bpy.context.scene.objects)-before:
                    # Bake a rigid 180-degree assembly rotation; no negative scale.
                    from mathutils import Matrix
                    obj.matrix_world = Matrix.Rotation(math.pi,4,'Z') @ obj.matrix_world
    elif kind == 'left-turn-calming':
        for y in (-1.35,-.35,.65,1.65):
            box('rubber centreline separator',(0,y,.0275),(.28,.90,.055),'rubber',.025)
            for yy in (y-.27,y+.27): box('yellow reflector',(0,yy,.055),(.22,.14,.004),'yellow',.001)
            for yy in (y-.34,y+.34): circle('recessed fixing',0,yy,.06,.015,'dark-steel',axis='X')
        delineator(0,-2.1)
    elif kind == 'high-visibility-crossing':
        post(2.85)
        box('fluorescent sign border',(0,-.065,2.38),(.76,.04,.90),'yellow-green',.014)
        box('aluminium back',(0,-.04,2.38),(.72,.015,.86),'steel',.008)
        box('white sign face',(0,-.09,2.38),(.63,.012,.77),'white',.006)
        walker(0,-.102,2.40,.72)
        for z in (2.12,2.08): box('crossing lines',(0,-.104,z),(.48,.006,.019),'black',0)
        for z in (2.08,2.68):
            box('rear mounting saddle',(0,.015,z),(.16,.08,.045),'dark-steel',.004)
            circle('sign bolt',0,-.104,z,.010,'steel')
    elif kind in ('green-bike-box','green-conflict-strip'):
        if kind == 'green-bike-box':
            S.mesh('green bike waiting area',[(-3,-1.5,.004),(3,-1.5,.004),(3,1.5,.004),(-3,1.5,.004)],[(0,1,2,3)],'green-paint')
            for a,b in [((-3,-1.5),(3,-1.5)),((3,-1.5),(3,1.5)),((3,1.5),(-3,1.5)),((-3,1.5),(-3,-1.5))]:S.line(a,b,.10,'white',.005)
            for a,b in bike_segments(1.2): S.line(a,b,.045,'white',.006)
        else:
            for y in (-2.5,-1.5,-.5,.5,1.5,2.5):
                S.mesh('green conflict patch',[(-1,y-.32,.004),(1,y-.32,.004),(1,y+.32,.004),(-1,y+.32,.004)],[(0,1,2,3)],'green-paint')
            for x in (-1.1,1.1):
                for y in (-2.5,-1.5,-.5,.5,1.5,2.5): S.line((x,y-.25),(x,y+.25),.10,'white',.004)
    elif kind == 'bicycle-signal':
        post(3.15)
        box('yellow signal backplate',(0,-.10,2.63),(.43,.045,1.05),'yellow',.035)
        box('black signal housing',(0,-.20,2.63),(.30,.18,.93),'black',.028)
        for z,mat in ((2.94,'red-dark'),(2.63,'amber-dark'),(2.32,'green-dark')):
            circle('unlit bicycle lens',0,-.30,z,.113,mat)
            for a,b in bike_segments(.13): face_line('bicycle lens motif',(a[0],z+a[1]-.025),(b[0],z+b[1]-.025),-.313,.006,'lens-icon')
            verts=[]
            for y in (-.295,-.45):
                verts += [(.13*math.cos(i*math.pi/16),y,z+.13*math.sin(i*math.pi/16)) for i in range(17)]
            S.mesh('curved signal visor',verts,[(i,i+1,i+18,i+17) for i in range(16)],'black')
        for z in (2.22,3.04): box('signal bracket',(0,-.04,z),(.12,.14,.06),'steel',.005)
    elif kind == 'traffic-diverter':
        for x in (-1.9,1.9):
            box('planter foot',(x,0,.055),(1.65,.70,.11),'dark-steel',.025)
            box('planter trough',(x,0,.38),(1.80,.82,.65),'corten',.03)
            box('soil',(x,0,.713),(1.67,.69,.012),'soil',.002)
            for n in range(17):
                xx=x-.7+(n%6)*.28; yy=-.22+(n//6)*.22
                for k in range(3):
                    S.beam('low grass blade',(xx,yy,.72),(xx+.10*math.sin(n+k),yy+.09*math.cos(n+k),.9+.10*((n+k)%3)),.012,'leaf',5)
        for x in (-.85,.85): delineator(x,0,.92,'white')
    elif kind == 'speed-display-trailer':
        box('trailer chassis',(0,.10,.38),(1.35,1.55,.12),'steel',.025)
        box('battery cabinet',(0,.35,.68),(1.12,.82,.46),'white',.025)
        for x in (-.78,.78):
            S.beam('rubber tyre',(x-.105,.35,.30),(x+.105,.35,.30),.30,'rubber',32)
            S.beam('wheel rim',(x-.11,.35,.30),(x+.11,.35,.30),.17,'steel',24)
            S.beam('wheel hub',(x-.12,.35,.30),(x+.12,.35,.30),.065,'dark-steel',12)
            box('mudguard',(x,.35,.61),(.30,.77,.05),'steel',.02)
        for x in (-.55,.55): S.beam('A-frame tow tongue',(x,-.63,.38),(0,-1.7,.38),.045,'steel',8)
        box('hitch coupler',(0,-1.78,.38),(.16,.24,.12),'steel',.025)
        S.beam('support jack',(0,-1.35,.02),(0,-1.35,.40),.026,'dark-steel',12)
        box('jack foot',(0,-1.35,.012),(.19,.19,.024),'steel',.01)
        box('telescopic mast',(0,.20,1.70),(.10,.10,2.6),'steel',.005)
        box('display cabinet',(0,-.04,2.20),(1.22,.24,1.15),'yellow',.045)
        box('display face',(0,-.17,2.20),(1.10,.022,1.02),'black',.025)
        text('YOUR SPEED',0,-.186,2.55,.13)
        text('30',0,-.186,2.16,.58,'amber')
        text('km/h',0,-.186,1.83,.12)
        box('solar frame',(0,.20,3.04),(1.35,.83,.055),'steel',.012)
        box('solar cells',(0,.20,3.071),(1.27,.75,.008),'solar',.003)
        for x in (-.43,0,.43):box('solar cell bus',(x,.20,3.076),(.008,.74,.001),'steel',0)
        for y in (-.04,.20,.44):box('solar cell divider',(0,y,3.076),(1.27,.008,.001),'steel',0)
        for x in (-.48,.48):box('rear reflector',(x,.78,.48),(.12,.015,.07),'red',.006)
    else:
        raise ValueError(kind)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--id',choices=[s[0] for s in SPECS])
    parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else None)
    specs=[s for s in SPECS if not args.id or args.id==s[0]]
    if args.dry_run:
        print(json.dumps({'families':len({s[2] for s in specs}),'variants':[s[0] for s in specs],'paid_calls':0}));return
    import bpy
    from mathutils import Vector
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'public_realm_assets'))
    import scene as S
    args.output.mkdir(parents=True,exist_ok=False)
    palette={'steel':(.36,.42,.46),'dark-steel':(.08,.10,.12),'black':(.012,.016,.02), 'rubber':(.025,.027,.03),
      'white':(.88,.91,.88),'yellow':(.92,.60,.015),'yellow-green':(.66,.91,.025), 'red':(.65,.012,.008),
      'asphalt':(.07,.078,.083),'green-paint':(.025,.36,.16),'red-dark':(.055,.006,.004),
      'amber-dark':(.075,.035,.004),'green-dark':(.004,.045,.016),'lens-icon':(.10,.12,.10),
      'amber':(1,.45,.015),'solar':(.012,.035,.08),'corten':(.30,.12,.048),'soil':(.07,.042,.019),'leaf':(.17,.27,.065)}
    for name,color in palette.items():
        mat=bpy.data.materials.new(name);mat.use_nodes=True;mat.diffuse_color=(*color,1)
        node=mat.node_tree.nodes['Principled BSDF'];node.inputs['Base Color'].default_value=(*color,1)
        node.inputs['Roughness'].default_value=.38 if name in ('steel','solar') else .78
        node.inputs['Metallic'].default_value=.65 if name in ('steel','dark-steel','corten') else 0
        mat.use_backface_culling=False;S.MATS[name]=mat
    S.MATS['kit']=bpy.data.materials.new('unused kit')
    catalogue=[]
    for slug,label,family,variant,source in specs:
        bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
        build(slug,S,bpy);bpy.context.view_layer.update()
        objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
        for obj in objects:
            # Consistent outward normals after authored primitives/text conversion.
            import bmesh
            bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
        pts=[o.matrix_world@Vector(v) for o in objects for v in o.bound_box]
        low=[min(p[i] for p in pts) for i in range(3)];high=[max(p[i] for p in pts) for i in range(3)]
        dimensions=[round(high[i]-low[i],6) for i in range(3)]
        info=S.export(args.output/(slug+'.glb'),objects)
        limitation='Concept visualization; dimensions and artwork are illustrative, not approved traffic-control design. Fixed size; flat supported surface only.'
        if slug=='traffic-diverter':limitation+=' Review emergency access, sightlines and clear passage; no simulated traffic restriction.'
        if slug in ('bicycle-signal','speed-display-trailer'):limitation+=' Static display; no detection, flashing or signal operation.'
        if slug.startswith('green-'):limitation+=' Paint is already 4–6 mm above road datum; gaps remain transparent.'
        catalogue.append(dict(id='detail-calgary-'+slug+'-v1',label=label+' · concept',category='Calgary safety additions',
          description=limitation,dimensions=dimensions,url='/street-kits/calgary-safety-concepts-v1/'+slug+'.glb',
          kind='object',color='#c9e44a',datumLift=0,sourceUrl=source_url(source),sourceVersion='calgary-concepts-2026-10-15-v1',
          sha256=info['sha256'],bytes=info['bytes'],nativeBoundsZUp=[low,high],runtimeApproved=False,
          safety=dict(group='Calgary safety additions',family=family,familyLabel=family,variantLabel=variant,sha256=info['sha256'],
            transforms=['translation','yaw'],placement='flat-road',nominalFootprint=dimensions[:2],limitation=limitation)))
    (args.output/'catalogue.json').write_text(json.dumps(catalogue,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'built':len(catalogue),'bytes':sum(r['bytes'] for r in catalogue),'runtime_approved':False}))


if __name__=='__main__':main()
