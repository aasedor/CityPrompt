"""One native inclusive playground, composed from preserved source equipment.

Blender --background --threads 4 --python-exit-code 1 --python <file> --
 --plan <prepared JSON> --kit <kit.json> --source-root <frontend/public>
 --output <fresh output> [--dry-run]
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
sys.path.insert(0,str(Path(__file__).parent))
import scene as S
import playground_equipment as E
from mathutils import Vector


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('plan','kit','source-root','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--dry-run',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    plan=json.loads(a.plan.read_text());assert plan['dimensions_m']==[38,36]
    source=a.source_root/'park-kits/inclusive-accessible-playground'
    locks={e['name']:sha(source/(e['name']+'.glb')) for e in plan['equipment']}
    refs=[]
    for name in ('variant_0.png','variant_0_angle_60.jpg','variant_0_angle_90.jpg'):
        ref=a.source_root/'archetypes/openspaces/inclusive-accessible-playground'/name
        assert ref.stat().st_size>1000
        refs.append(dict(path=str(ref.relative_to(a.source_root)),sha256=sha(ref)))
    if a.output.exists():raise ValueError('Use a fresh output directory.')
    if a.dry_run:print(json.dumps(dict(status='DRY_RUN_PASS',equipment=locks,references=refs)));return
    a.output.mkdir(parents=True);S.init(a.kit)
    for name,color in [('paving.blue',(.10,.32,.43)),('paving.green',(.25,.42,.27)),('paving.orange',(.55,.28,.12)),
                       ('slide_amber',(.61,.34,.075)),('slide_charcoal',(.13,.17,.18)),('play_green',(.24,.38,.14))]:
        m=S.bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
        m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*color,1)
        m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.92;S.MATS[name]=m
    S.ground(38,36,[(0,0,38,36,'soil')])
    for region in plan['ground_regions']:
        vertices=[(x,y,0) for triangle in region['triangles'] for x,y in triangle]
        S.mesh(region['material'],vertices,[tuple(range(i,i+3)) for i in range(0,len(vertices),3)],region['material'])
    r=dict(id='inclusive_accessible_playground_v0',revision='inclusive-native-v002',title='Inclusive Woodland Playground',
           dimensions_m=[38,36],clear_routes=plan['clear_routes'],image_references=refs,
           source_equipment=locks,preparation_sha256=sha(a.plan),kit_sha256=sha(a.kit),
           native_entrance=dict(x=0,y=-18,widthM=2.4,arrivalY=-16),
           programme='Two linked roofed timber play towers, ramp, swings, spinner, sensory panel, sheltered seating and layered planting.',
           limitations=['Prepared level concept only. Play equipment is conceptual; accessibility, fall zones and safety require specialist design review.'])
    # Keep every original equipment mesh and texture at its native scale.
    for e in plan['equipment']:
        before=set(S.bpy.context.scene.objects);S.bpy.ops.import_scene.gltf(filepath=str(source/(e['name']+'.glb')))
        imported=set(S.bpy.context.scene.objects)-before
        roots=[o for o in imported if o.parent not in imported]
        for o in roots:o.location+=Vector((e['x'],e['y'],0))
        S.bpy.context.view_layer.update()
        meshes=[o for o in imported if o.type=='MESH']
        # Freeze world transforms before making reusable, origin-centred modules.
        for o in meshes:
            world=o.matrix_world.copy();o.parent=None;o.matrix_world=world
        S.RIGID[e['name']]=(meshes,e['x'],e['y'])
        S.PLACEMENTS.append(dict(kind=e['name'],x=e['x'],y=e['y'],z=0,yaw=0,scale=1))
    E.main_structure();E.swings(-10,-10);E.sensory(0,-7)
    for x in (-9.5,9.5):E.canopy(x,11.2)
    trees=[(-14,14.8),(-5,14.8),(5,14.8),(14,14.8),(-15.7,-2),(15.7,-2)]
    for i,(x,y) in enumerate(trees):S.kit('ornamental_tree',x,y,0,i*1.8,1)
    for i in range(34):
        for j in range(2):
            x=-16.5+i;y=14.6+j*.85
            if any((x-tx)**2+(y-ty)**2<.7**2 for tx,ty in trees):continue
            S.kit(['flowering_perennial','silver_shrub','meadow_grass'][(i+j)%3],x,y,0,i*2.4,1.05)
    for x in (-17,17):
        for j in range(30):
            y=-14+j
            if any((x-tx)**2+(y-ty)**2<.8**2 for tx,ty in trees):continue
            S.kit(['flowering_perennial','meadow_grass'][j%2],x,y,0,j*2.4,1.05)
    for x in list(range(-16,-2))+list(range(3,17)):
        S.kit('flowering_perennial',x,-16,0,x*2.4,1)
    for f in (Path(__file__),Path(S.__file__),Path(E.__file__),a.plan):shutil.copy2(f,a.output/f.name)
    S.deliver(a.output,r,[('aerial',(43,-48,43),(0,0,0),59),('top',(0,0,85),(0,.01,0),55),('detail',(23,-23,12),(0,2,1.5),34)],build_surfaces=False)
    sc=S.bpy.context.scene;cam=sc.camera;cam.data.type='PERSP';cam.data.lens=24;cam.location=(0,-19,1.65)
    cam.rotation_euler=(Vector((0,4,1.5))-cam.location).to_track_quat('-Z','Y').to_euler()
    sc.render.filepath=str(a.output/'renders/walk.png');S.bpy.ops.render.render(write_still=True)


if __name__=='__main__':main()
