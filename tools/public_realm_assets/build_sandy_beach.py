"""One original sandy lakeside park; immutable, metre-scale, prepared-level pilot.

Run with Blender --background --python this_file -- --kit <kit.json> --output <new dir>.
Use --dry-run first. No catalogue writes or paid image/model calls.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import shutil
import sys

sys.path.insert(0, str(Path(__file__).parent))
import scene as S
from build_showcase_parks import material
from mathutils import Vector

WIDTH, DEPTH = 44, 48
COUNT = 192


def ellipse(rx, ry, cy):
    points=[]
    for i in range(COUNT):
        a=i*math.tau/COUNT
        factor=1+.025*math.sin(3*a)+.018*math.cos(5*a)
        points.append((rx*math.cos(a)*factor,cy+ry*math.sin(a)*factor))
    return points


def ring(name, outer, inner, mat, zo=0, zi=0):
    vertices = [(x, y, zo) for x, y in outer] + [(x, y, zi) for x, y in inner]
    return S.mesh(name, vertices, [(i, (i+1) % COUNT, (i+1) % COUNT+COUNT, i+COUNT) for i in range(COUNT)], mat)


def surface_colours(obj, colour, variation, seed):
    """Embedded vertex colours survive GLB delivery; no procedural-only shader."""
    rng = random.Random(seed)
    attr = obj.data.color_attributes.new(name='Color', type='FLOAT_COLOR', domain='POINT')
    values = []
    for _ in obj.data.vertices:
        shade = rng.uniform(-variation, variation)
        values.extend([max(0, min(1, c + shade)) for c in colour] + [1])
    attr.data.foreach_set('color', values)
    m = obj.data.materials[0]
    node = m.node_tree.nodes.new('ShaderNodeVertexColor'); node.layer_name = 'Color'
    m.node_tree.links.new(node.outputs['Color'], m.node_tree.nodes['Principled BSDF'].inputs['Base Color'])


def boardwalk(x, y, w, d):
    # Flush access datum: filled joints and supported planks, no floating deck.
    S.box('boardwalk support', (x, y, -.066), (w, d, .15), 'paving')
    rows = math.ceil(d / .145)
    for i in range(rows):
        S.box('cedar boardwalk plank', (x, y-d/2+(i+.5)*d/rows, .006), (w, d/rows-.008, .012), 'paving')
    for xx in (x-w/2+.07, x+w/2-.07):
        for i in range(0, rows, 4):
            S.beam('flush deck fixing', (xx, y-d/2+(i+.5)*d/rows, .01), (xx, y-d/2+(i+.5)*d/rows, .014), .007, 'metal', 6)


def lounger(x, y, yaw=0):
    before = set(S.bpy.context.scene.objects)
    for xx in (-.31, .31):
        for yy in (-.55, .55):
            S.box('lounger timber leg', (xx, yy, .2), (.06, .07, .4), 'timber')
        S.beam('lounger side rail', (xx, -.85, .40), (xx, .3, .40), .04, 'timber')
        S.beam('lounger back rail', (xx, .3, .40), (xx, .87, .96), .04, 'timber')
    for i in range(17):
        yy = -.84+i*.1; zz = .42 if yy < .3 else .42+(yy-.3)*.95
        slat = S.box('lounger cedar slat', (0, yy, zz), (.72, .083, .045), 'cedar')
        if yy >= .3:
            for vertex in slat.data.vertices: vertex.co.z += (vertex.co.y-yy)*.95
    for o in set(S.bpy.context.scene.objects)-before:
        o.location = (x, y, 0); o.rotation_euler.z += yaw


def parasol(x, y):
    S.beam('parasol timber mast', (x,y,0), (x,y,2.55), .04, 'timber', 12)
    for i in range(12):
        a,b=i*math.tau/12,(i+1)*math.tau/12
        S.mesh('canvas parasol panel', [(x,y,2.62),(x+1.5*math.cos(a),y+1.5*math.sin(a),2.18),(x+1.5*math.cos(b),y+1.5*math.sin(b),2.18)], [(0,1,2)], 'canvas' if i%2 else 'blue_canvas')
        S.beam('parasol rib', (x,y,2.55), (x+1.48*math.cos(a),y+1.48*math.sin(a),2.17), .012, 'timber', 5)


def build(recipe):
    S.ground(WIDTH, DEPTH, [])  # Metadata for planted root ownership; curved surfaces below.
    outer = ellipse(20.7, 18, 5)
    shore = ellipse(15.4, 10, 10.5)
    rect = []
    for x,y in outer:
        factor = min(22/abs(x) if x else 1e9, 24/abs(y) if y else 1e9)
        rect.append((x*factor, y*factor))
    ring('planted ground', rect, outer, 'grass')
    # Subdivided sandy crescent. Subtle physical ripples and retained vertex hues.
    rows = 34; verts=[]; faces=[]
    for j in range(rows+1):
        t=j/rows
        for a,b in zip(outer,shore):
            x,y=a[0]*(1-t)+b[0]*t,a[1]*(1-t)+b[1]*t
            ripple=.007*math.sin(x*19+y*6)*math.sin(math.pi*t)
            verts.append((x,y,ripple))
    for j in range(rows):
        for i in range(COUNT):
            a=j*COUNT+i;b=j*COUNT+(i+1)%COUNT
            faces.append((a,b,b+COUNT,a+COUNT))
    surface_colours(S.mesh('fine rippled sand',verts,faces,'sand'),(.67,.54,.34),.035,312)
    shallow = ellipse(14.6, 9.2, 10.5)
    deep = ellipse(12.7, 7.3, 10.5)
    ring('wet sand margin',shore,shallow,'wet_sand',0,-.007)
    ring('shallow lake water',shallow,deep,'shallows',.003,.008)
    S.mesh('calm freshwater lagoon',[(x,y,.008) for x,y in deep],[tuple(range(COUNT))],'water')
    rng=random.Random(73)
    # Fine short highlights, not a high-poly simulated water surface.
    for _ in range(125):
        x=rng.uniform(-13.1,13.1);y=rng.uniform(.5,17.5)
        if (x/12.4)**2+((y-10.5)/7.0)**2<.9:
            S.line((x-.15,y),(x+rng.uniform(.12,.48),y+.012),.013,'ripple',.016)
    boardwalk(0,-16.5,37,2.6)
    boardwalk(0,-20.9,3,6.2)
    for x in (-7,7):boardwalk(x,-11.25,2.4,7.9)
    # Rest areas keep the entire through-route clear.
    for x in (-13,13):
        boardwalk(x,-20.7,7,5.4)
        S.pergola(x,-21.0,6,3.5)
        S.kit('picnic_table',x,-21.0)
    for x,y in [(-12,-6),(-4,-7.7),(4,-7.7),(12,-6)]:
        parasol(x,y)
        lounger(x-1,y-1.3,math.pi);lounger(x+1,y-1.3,math.pi)
    for x in (-17,17):
        S.kit('bench',x,-14.5,0,math.pi)
    S.kit('bike_rack',3,-22.8);S.kit('bin',-3,-22.8)
    for x,y in [(-18,-20),(18,-20),(-19,-11),(19,-11)]:
        S.kit('grove_tree',x,y,0,y*.11,.68)
    for i in range(18):
        a=i*math.tau/18
        if math.sin(a)<-.65:continue
        for _ in range(rng.randint(4,8)):
            aa=a+rng.uniform(-.09,.09);radius=rng.uniform(.94,1)
            x,y=19.8*math.cos(aa)*radius,5+17*math.sin(aa)*radius
            S.kit('meadow_grass',x,y,0,aa,rng.uniform(.5,.85))
    for sign in (-1,1):
        for x,y in [(19,-6),(20,-3),(17,-12),(20,18),(17,21)]:
            S.kit('silver_shrub',sign*x,y,0,y,.65)
    # Bleached driftwood and rounded shoreline stones, clear of paths.
    for sign in (-1,1):
        S.beam('grounded driftwood', (sign*16,-2,.13), (sign*18,1,.13), .17, 'cedar', 9)
        for yy in (3,6,10,14):
            xx=sign*(18.5-abs(yy-8)*.09)
            S.bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=(xx,yy,.20))
            o=S.bpy.context.object;o.name='shoreline glacial boulder';o.scale=(.65,.48,.34);o.data.materials.append(S.MATS['stone'])
    recipe['clear_routes']=[dict(a=[0,-23.9],b=[0,-16.5],width=2.4),dict(a=[-18,-16.5],b=[18,-16.5],width=2),
        *[dict(a=[x,-16.5],b=[x,-7.6],width=1.8) for x in (-7,7)]]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--kit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--dry-run',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    assert a.kit.is_file();assert not a.output.exists(),'Use a new candidate directory.'
    recipe=dict(id='student_sandy_beach_v1',title='Sandy Beach & Boardwalk',dimensions_m=[WIDTH,DEPTH],
        programme='A sandy freshwater crescent and lagoon, cedar boardwalk, eight loungers, four striped parasols, two picnic pergolas and native planting.',
        design_basis='Original concept; small freshwater recreation park, not a mapped natural shoreline.',
        kit_sha256=hashlib.sha256(a.kit.read_bytes()).hexdigest(),terrain_policy='prepared_level',native_scale_only=True,
        limitations=['Prepared level ground only. The lagoon is included scenery, not a connection to mapped water or a hydrological simulation.',
        'Boardwalk stays at datum. Beach slopes, swimming safety, drainage and accessibility require site design review.',
        'The complete 44 x 48 m assembly stays rigid when its parcel changes; use a larger parcel to rotate it.'])
    if a.dry_run:print('DRY_RUN_PASS',json.dumps(recipe));return
    a.output.mkdir(parents=True);S.init(a.kit)
    for n,c,rough in [('sand',(.67,.54,.34),.97),('wet_sand',(.39,.34,.23),.74),('shallows',(.22,.43,.37),.23),
        ('water',(.05,.23,.24),.16),('ripple',(.32,.49,.44),.25),('cedar',(.52,.40,.25),.84),
        ('canvas',(.91,.87,.74),.9),('blue_canvas',(.11,.27,.32),.9),('stone',(.34,.35,.29),.9)]:material(n,c,rough)
    material('paving',(.46,.32,.19),.85)
    build(recipe)
    for source in (Path(__file__),Path(S.__file__),Path(__file__).with_name('build_showcase_parks.py')):shutil.copy2(source,a.output/source.name)
    S.deliver(a.output,recipe,[('aerial',(40,-50,46),(0,0,0),66),('top',(0,0,80),(0,.001,0),66),
        ('detail',(21,-26,14),(0,-6,0),37)],build_surfaces=False)
    sc=S.bpy.context.scene;cam=sc.camera;cam.data.type='PERSP';cam.data.lens=24;cam.location=(0,-16.5,1.7)
    cam.rotation_euler=(Vector((1,4,1.3))-cam.location).to_track_quat('-Z','Y').to_euler()
    sc.render.filepath=str(a.output/'renders/walk.png');S.bpy.ops.render.render(write_still=True)


if __name__=='__main__':main()
