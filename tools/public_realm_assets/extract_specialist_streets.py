"""Recover finite canal/bridge components without changing their source files.

Blender --background --disable-autoexec --python this_file -- --source DIR
--delivery canal-v005|bridge-v003 --output NEW_DIR [--dry-run]. Ground, crossing,
fixed structural span and furnishings have independent ownership. This never
exports or repeats a whole preview fixture as a route module.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from extract_brt_runtime import export, sha

LOCKS = {
    'canal-v005': '8526b6d7b63718db193eff20677185ef3afbb239d1eb41df23f6994eadf791e2',
    'bridge-v003': 'e61008b07ffaf5451f5079d2fc4422504a72c03f6fc3b8e10f73069214af424d',
}
CROSSING = {
    'load bearing arch barrel', 'graded brick bridge unit', 'solid bridge ramp carrier',
    'curved black bridge rail', 'bridge railing picket', 'bridge main post',
    'arch stone voussoir face', 'graded longitudinal brick approach',
    'continuous approach masonry support', 'raised approach waterside wall',
    'graded waterside coping', 'continuous sloping curb ribbon',
    'bridge bank rail return', 'bank return picket',
}
BENCH = {'bench frame leg', 'timber bench seat slat', 'timber bench back slat', 'bench back support'}
LAMP = {'canal lamp pedestal', 'historic lamp lantern', 'lantern cap'}
FURNITURE = BENCH | LAMP | {'shade_tree', 'waterside mooring bollard'}


def main():
    import bpy
    from mathutils import Vector
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--delivery', choices=LOCKS, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    recipe = json.loads((args.source/'recipe.json').read_text())
    assert sha(args.source/'editable.blend') == recipe['authoring_sha256'] == LOCKS[args.delivery]
    assert sha(args.source/'assembly-preview.glb') == recipe['assembly_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(args.source/'editable.blend'))
    bpy.context.view_layer.update()
    objects = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    base = lambda o: re.sub(r'\.\d+$', '', o.name)
    bounds = lambda o: [[fn((o.matrix_world@Vector(c))[i] for c in o.bound_box) for i in range(3)] for fn in (min,max)]
    groups, anchors = {}, {}
    if args.delivery == 'canal-v005':
        assert len(objects) == 8483
        groups = {'canal_ground': [], 'canal_crossing': [], 'canal_furnishings': []}
        for o in objects:
            groups['canal_crossing' if base(o) in CROSSING else 'canal_furnishings' if base(o) in FURNITURE else 'canal_ground'].append(o)
        anchors = {key: [0,0,0] for key in groups}
        # Source east-side objects; complete supports/materials are retained.
        for key, names, anchor, radius in [
            ('canal_tree', {'shade_tree'}, [10.55,-22,.065], 5),
            ('canal_bench', BENCH, [10.25,-16,0], 1),
            ('canal_lamp', LAMP, [11.6,-34,0], .5),
            ('canal_bollard', {'waterside mooring bollard'}, [9.45,-24,0], .5),
        ]:
            selected = []
            for o in objects:
                lo,hi = bounds(o)
                if base(o) in names and lo[0]>0 and abs((lo[1]+hi[1])/2-anchor[1]) < radius:
                    selected.append(o)
            assert selected, key
            groups[key], anchors[key] = selected, anchor
    else:
        assert len(objects) == 1673
        # The inspection water is context, not part of the structural feature.
        excluded = [o for o in objects if 'water' in base(o).lower()]
        assert len(excluded) == 1, [o.name for o in excluded]
        groups = {'bridge_structure': [o for o in objects if o not in excluded]}
        anchors = {'bridge_structure': [0,0,0]}
    if args.dry_run:
        print('DRY_RUN_PASS', args.delivery, {k:len(v) for k,v in groups.items()}); return
    if args.output.exists():
        raise ValueError('Derived revisions are immutable; choose a new output folder')
    args.output.mkdir(parents=True)
    modules = {key:export(group, anchors[key], args.output/f'{key}.glb') for key,group in groups.items()}
    result = dict(schemaVersion=1,status='derived-candidate-not-runtime-approved',sourceDelivery=args.delivery,
        sourceAuthoringSha256=LOCKS[args.delivery],sourceRecipeSha256=sha(args.source/'recipe.json'),
        sourceAssemblySha256=recipe['assembly_sha256'],extractorSha256=sha(Path(__file__)),modules=modules,
        sourceObjectCount=len(objects),excludedContext=[o.name for o in excluded] if args.delivery=='bridge-v003' else [])
    (args.output/'extraction.json').write_text(json.dumps(result,indent=2)+'\n')
    print('EXTRACTED', args.delivery, {k:v['sha256'] for k,v in modules.items()})


if __name__ == '__main__':
    main()
