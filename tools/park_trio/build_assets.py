"""Finite original public-realm modules. Run inside Blender; output is external.

Each park is a separate immutable candidate. No AI API calls or source-image
projection. References inform composition and material choices, not surveyed dimensions.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import sys

import bpy
from mathutils import Vector

IDENTITIES = {
    'cinema': ('outdoor_cinema_lawn', 'outdoor_cinema_lawn_v1', 'outdoor-cinema-lawn', 1),
    'garden': ('research_garden_teaching_arboretum', 'research_garden_teaching_arboretum_variant_3', 'research-garden-teaching-arboretum', 3),
    'concert': ('concert_pavilion_lawn', 'concert_pavilion_lawn_v1', 'concert-pavilion-lawn', 1),
}


def mat(name, color, roughness=.75, metal=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    shader = m.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['Metallic'].default_value = metal
    m.diffuse_color = (*color, 1)
    return m


def box(name, size, pos, material, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    obj = bpy.context.object; obj.name = name; obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    if bevel:
        mod = obj.modifiers.new('Physical edge', 'BEVEL'); mod.width = bevel; mod.segments = 2
    return obj


def beam(name, a, b, radius, material, vertices=8):
    a, b = Vector(a), Vector(b); delta = b-a
    rotation=delta.to_track_quat('Z','Y'); midpoint=(a+b)*.5
    points=[midpoint+rotation@Vector((radius*math.cos(i*math.tau/vertices),radius*math.sin(i*math.tau/vertices),z)) for z in (-delta.length/2,delta.length/2) for i in range(vertices)]
    faces=[(i,(i+1)%vertices,(i+1)%vertices+vertices,i+vertices) for i in range(vertices)]
    faces += [tuple(reversed(range(vertices))),tuple(range(vertices,2*vertices))]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(points,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);mesh.materials.append(material)
    for face in mesh.polygons: face.use_smooth = face.index < vertices


def ribbon(name, lines, material, thickness=.04):
    verts = [point for line in lines for point in line]; n = len(lines[0]); faces = []
    for i in range(len(lines)-1):
        for j in range(n-1):
            k = i*n+j; faces.append((k,k+1,k+n+1,k+n))
    mesh = bpy.data.meshes.new(name); mesh.from_pydata(verts, [], faces); mesh.update()
    obj = bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(obj); obj.data.materials.append(material)
    if thickness:
        mod=obj.modifiers.new('Closed material thickness','SOLIDIFY'); mod.thickness=thickness
    for face in mesh.polygons: face.use_smooth=True
    return obj


def materials():
    return {
        'steel': mat('Graphite powder-coated steel',(.12,.145,.15),.4,.65),
        'wood': mat('Weathered honey timber',(.40,.28,.16)),
        'woodlight': mat('Fresh timber slat edges',(.56,.40,.23)),
        'stone': mat('Warm exposed aggregate',(.48,.46,.40)),
        'screen': mat('Unprojected pale screen',(.79,.82,.78),.85),
        'dark': mat('Recessed dark glass',(.045,.07,.075),.18,.15),
        'silver': mat('Brushed silver roof',(.61,.65,.65),.4,.65),
        'corten': mat('Oxidised planting-box steel',(.40,.18,.085),.88,.15),
        'soil': mat('Garden soil',(.11,.075,.045)),
    }


def screen(m):
    box('Stone screen base',(10.9,1.6,1.25),(0,0,.625),m['stone'],.055)
    # Individually coursed cap stones establish scale at close camera distance.
    for i in range(14): box('Cap stone',(.76,1.72,.13),(-5.06+i*.78,0,1.315),m['stone'],.015)
    for x in (-5.1,5.1):
        box('Screen steel upright',(.18,.32,5.7),(x,0,4.05),m['steel'],.025)
        beam('Rear bracing',(x,.05,6.75),(x,1.5,0),.065,m['steel'])
        box('Brace foot',(.5,.5,.12),(x,1.5,.06),m['stone'])
    for z in (1.55,6.8): box('Steel screen crossrail',(10.35,.32,.18),(0,0,z),m['steel'],.02)
    box('Screen backing',(9.92,.14,4.94),(0,-.03,4.17),m['dark'])
    box('Blank projection cloth',(9.6,.035,4.58),(0,-.12,4.17),m['screen'])
    for x in range(-4,5,2): beam('Screen back support',(x,.18,1.55),(x,.18,6.8),.035,m['steel'])


def booth(m):
    box('Booth foundation',(3.5,3.8,.16),(0,0,.08),m['stone'],.025)
    box('Enclosed booth',(3.25,3.5,2.5),(0,0,1.4),m['wood'])
    for i in range(26):
        x=-1.59+i*.125
        if abs(x)<.7: continue
        box('Vertical front board',(.115,.08,2.48),(x,-1.79,1.4),m['woodlight'] if i%4==0 else m['wood'],.008)
    box('Projection window reveal',(1.48,.14,.84),(0,-1.82,1.76),m['steel'])
    box('Projection window pane',(1.31,.025,.68),(0,-1.905,1.76),m['dark'])
    box('Roof edge',(3.65,3.98,.16),(0,0,2.73),m['steel'],.035)
    box('Side access door',(.05,.95,2.05),(1.65,.25,1.2),m['woodlight'])
    beam('Door handle',(1.71,-.08,1.05),(1.71,-.08,1.35),.025,m['steel'])


def bed(m):
    w,d=2.8,1.6
    for x in (-w/2,w/2): box('Corten planter side',(.06,d+.06,.55),(x,0,.275),m['corten'],.014)
    for y in (-d/2,d/2): box('Corten planter end',(w,.06,.55),(0,y,.275),m['corten'],.014)
    box('Visible soil',(w-.08,d-.08,.46),(0,0,.23),m['soil'])
    greens=[mat('Sage foliage',(.28,.39,.18)),mat('Herb green',(.20,.32,.12)),mat('Silver foliage',(.46,.53,.32))]
    rng=random.Random(71)
    for i in range(54):
        x=rng.uniform(-1.23,1.23);y=rng.uniform(-.65,.65);z=rng.uniform(.55,.88)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=rng.uniform(.11,.20),location=(x,y,z))
        o=bpy.context.object;o.name='Contained herb foliage';o.scale.z=1.5;o.data.materials.append(greens[i%3])
        beam('Plant stem',(x,y,.46),(x,y,z),.013,greens[1],5)


def label(m):
    beam('Interpretation post',(0,0,0),(0,0,.90),.045,m['steel'])
    p=box('Blank interpretation panel',(.65,.42,.045),(0,0,.91),m['stone'],.02);p.rotation_euler.x=.3
    # No invented place names, claims or unreadable pseudo-text.


def shelter(m):
    box('Teaching deck',(6.7,7.7,.18),(0,0,.09),m['wood'])
    for j in range(37): box('Deck board',(6.72,.19,.035),(0,-3.6+j*.20,.19),m['woodlight'] if j%5==0 else m['wood'],.008)
    def rib(t,y): return (3.1*math.cos(t),y,.21+4.1*math.sin(t))
    for y in (-3.5,-2.5,-1.5,-.5,.5,1.5,2.5,3.5):
        pts=[rib(math.pi*i/32,y) for i in range(33)]
        for a,b in zip(pts,pts[1:]): beam('Curved timber rib',a,b,.075,m['woodlight'],8)
    # Crossed laths follow the curved carrier, rather than unsupported spikes.
    for start in (-3,-1.5,0,1.5,3):
        for sign in (-1,1):
            pts=[rib(.18+(math.pi-.36)*i/32,max(-3.5,min(3.5,start+sign*(i/32-.5)*2.5))) for i in range(33)]
            for a,b in zip(pts,pts[1:]): beam('Diagonal timber lattice',a,b,.026,m['wood'],6)
    ribbon('Weather canopy',[[rib(.52+(math.pi-1.04)*i/32,y) for i in range(33)] for y in (-2.8,2.8)],m['wood'],.07)
    for x in (-2.4,2.4):
        box('Teaching bench',(.5,4.5,.09),(x,0,.53),m['woodlight'],.02)
        for y in (-1.7,1.7): box('Teaching bench support',(.35,.2,.30),(x,y,.35),m['steel'])


def seats(m):
    for x in (-1.5,-.5,.5,1.5):
        box('Audience seat',(.55,.47,.09),(x,0,.47),m['steel'],.045)
        back=box('Audience back',(.55,.08,.5),(x,.23,.78),m['steel'],.055);back.rotation_euler.x=-.10
        for dx in (-.20,.20):
            for y in (-.16,.17): beam('Seat leg',(x+dx,y,0),(x+dx,y,.46),.025,m['steel'])


def concert(m):
    box('Stage plinth',(35,16,.64),(0,0,.32),m['stone'],.04)
    def roof(x,y): return 3.1+8.7*math.exp(-((x+2)/11)**2)+.65*math.sin(x*.30)+.45*math.cos(y*.21)
    for i in range(60):
        x=-14.75+i*.5
        height=min(roof(x-.25,7.1),roof(x+.25,7.1))-.45-.64
        box('Roof-following acoustic wall',(.5,.3,height),(x,7.1,.64+height/2),m['wood'])
        if i%2==0: box('Acoustic timber fin',(.075,.17,height-.08),(x,6.89,.64+height/2),m['woodlight'])
    xs=[-18+i*.5 for i in range(73)];ys=[-9+j*.5 for j in range(37)]
    ribbon('Continuous wave weathering shell',[[(x,y,roof(x,y)) for x in xs] for y in ys],m['silver'],.22)
    ribbon('Timber soffit',[[(x,y,roof(x,y)-.25) for x in xs] for y in ys],m['wood'],.06)
    for x in [-18+i*.60 for i in range(61)]:
        for ya,yb in zip(ys,ys[1:]): beam('Standing seam',(x,ya,roof(x,ya)+.025),(x,yb,roof(x,yb)+.025),.020,m['silver'],5)
    for y in (-9,-4.5,0,4.5,9):
        for a,b in zip(xs,xs[1:]): beam('Roof structural rib',(a,y,roof(a,y)-.39),(b,y,roof(b,y)-.39),.10,m['steel'])
    for x in (-17,17):
        for y in (-7,0,7):
            box('Column foundation',(.85,.85,.25),(x,y,.125),m['stone'])
            beam('Roof column',(x,y,.2),(x,y,roof(x,y)-.34),.14,m['steel'],12)
    beam('Lighting truss',(-11,-5,4.2),(11,-5,4.2),.12,m['steel'])
    for x in range(-10,11,2):
        box('Stage luminaire',(.28,.38,.35),(x,-5,3.9),m['steel'],.025)
    for x in (-12,12): box('Suspended speaker',(.68,.6,2.3),(x,-4.8,3.05),m['dark'],.05)
    # A continuous shallow ramp meets the side of the stage.
    ribbon('Stage ramp', [[(x,y,.08+(x+26)/8.5*.56) for x in (-26,-17.5)] for y in (-3,-1)],m['stone'],.08)


BUILDERS={'cinema':{'screen':screen,'booth':booth},'garden':{'shelter':shelter,'bed':bed,'label':label},'concert':{'stage':concert,'seats':seats}}


def export(name,builder,out):
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    builder(materials());bpy.ops.object.select_all(action='SELECT');bpy.ops.object.convert(target='MESH')
    bpy.context.view_layer.update()
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
    vertices=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
    minimum=[min(v[i] for v in vertices) for i in range(3)];maximum=[max(v[i] for v in vertices) for i in range(3)]
    # Keep the architectural origin; ground the lowest evaluated geometry.
    for obj in objects: obj.location.z-=minimum[2]
    bymat={}
    for obj in objects: bymat.setdefault(obj.data.materials[0].name,[]).append(obj)
    for group in bymat.values():
        bpy.ops.object.select_all(action='DESELECT')
        for obj in group: obj.select_set(True)
        bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join()
        bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    bpy.ops.object.select_all(action='SELECT')
    path=out/f'{name}.glb';bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=True)
    return {'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size,
            'boundsXYZ':[minimum[:2]+[0],maximum[:2]+[maximum[2]-minimum[2]]], 'nativeScale':[1,1,1], 'meshCount':len(bymat)}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--park',choices=list(IDENTITIES),required=True)
    parser.add_argument('--source-root',type=Path,required=True);parser.add_argument('--output-dir',type=Path,required=True);parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);parent,variant,slug,index=IDENTITIES[args.park]
    sources=[]
    for suffix,role in [('.png','ground'),('_angle_60.jpg','oblique'),('_angle_90.jpg','top')]:
        relative=f'frontend/public/archetypes/openspaces/{slug}/variant_{index}{suffix}';path=args.source_root/relative
        data=path.read_bytes()
        if len(data)<500: raise ValueError(f'Source is not hydrated: {path}')
        sources.append({'path':relative,'role':role,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
    print(json.dumps({'park':args.park,'modules':list(BUILDERS[args.park]),'sources':sources,'dryRun':args.dry_run}))
    if args.dry_run:return
    if args.output_dir.exists() and any(args.output_dir.iterdir()):raise ValueError('Use a new empty candidate directory')
    args.output_dir.mkdir(parents=True,exist_ok=True)
    assets={name:export(name,builder,args.output_dir) for name,builder in BUILDERS[args.park].items()}
    (args.output_dir/'manifest.json').write_text(json.dumps({'park':args.park,'archetypeId':parent,'variantId':variant,'status':'local-pilot-not-approved','sources':sources,'assets':assets,'inferences':['Metric dimensions inferred for student design; not surveyed or construction-approved.','No people, projected source photographs or invented text in the model.']},indent=2))


if __name__=='__main__':main()
