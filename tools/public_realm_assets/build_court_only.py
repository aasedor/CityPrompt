"""Build one finite court-only pilot. Blender --background --python ... -- --kind ... --output ..."""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import scene as S
from build_courts import sports_module, court_net, material
from court_only_specs import COURT_ONLY_KINDS, court_only_recipe


def pickleball(r):
    w, d = r['playing_m']; mw, md = r['module_m']; kitchen = r['kitchen_m']
    S.box('sport base', (0, 0, -.066), (mw, md, .108), 'runoff')
    S.box('playing surface', (0, 0, -.03), (w, d, .06), 'court')
    S.box('non volley zone', (0, 0, .002), (w, kitchen*2, .004), 'kitchen')
    # Outside edges of 2-inch lines define the playing rectangle and kitchen.
    S.rectline(0, 0, w-.0508, d-.0508, .0508)
    for sign in (-1, 1):
        y = sign*(kitchen-.0254)
        S.line((-w/2, y), (w/2, y), .0508)
        S.line((0, sign*kitchen), (0, sign*d/2), .0508)
    court_net(w+.6096, r['net_center_m'], r['net_end_m'], bottom=.04,
              mesh_step=.075, post_height=.9652)
    r['equipment'] = [dict(kind='net', center_m=r['net_center_m'], end_m=r['net_end_m'])]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--kind', choices=COURT_ONLY_KINDS, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--dry-run', action='store_true')
    a = p.parse_args(sys.argv[sys.argv.index('--')+1:])
    a.output = a.output.resolve()
    r = court_only_recipe(a.kind)
    if a.output.exists():
        raise ValueError(f'Preserve existing output: {a.output}')
    if a.dry_run:
        print('DRY_RUN_PASS', json.dumps(r)); return
    a.output.mkdir(parents=True)
    kit = a.output/'empty-kit.json'; kit.write_text('{}')
    S.init(kit); S.GROUND_SIZE[:] = r['dimensions_m']
    S.MATS['court'].diffuse_color = (*r['court_colour'], 1)
    S.MATS['court'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (*r['court_colour'], 1)
    for name, colour in {'key': [.29,.40,.35], 'padding': [.08,.13,.12],
                         'rim': [.61,.20,.06], 'board': [.65,.69,.64],
                         'sand': [.63,.54,.37], 'sand_grain': [.45,.38,.24]}.items():
        material(name, colour)
    if a.kind == 'pickleball': pickleball(r)
    else: sports_module(r, include_enclosure=False)
    r['source_components'] = dict(Counter(o.name.split('.')[0] for o in S.bpy.context.scene.objects if o.type=='MESH'))
    forbidden = ('fence', 'tree', 'bench', 'pergola', 'light', 'garden', 'paving')
    assert not any(any(word in name.lower() for word in forbidden) for name in r['source_components'])
    w, d = r['dimensions_m']
    S.deliver(a.output, r, [('aerial', (w*1.2, -d*.9, d*.9), (0,0,0), max(w,d)*1.38),
                           ('top', (0,0,60), (0,0,0), max(w,d)*1.1)], build_surfaces=False)
    # Eye-height source view of the reimported exact GLB, with perspective.
    cam = S.bpy.context.scene.camera; cam.data.type = 'PERSP'; cam.data.lens = 22
    cam.location = (w*.32, -d/2-4, 1.7)
    cam.rotation_euler = (S.Vector((0,0,1.0))-cam.location).to_track_quat('-Z','Y').to_euler()
    S.bpy.context.scene.render.filepath = str(a.output/'renders/eye-height.png')
    S.bpy.ops.render.render(write_still=True)
    from verify_court_only import verify
    verify(a.output)


if __name__ == '__main__': main()
