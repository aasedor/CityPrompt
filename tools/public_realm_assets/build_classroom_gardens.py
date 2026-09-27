"""Finite classroom garden revisions. Originals are preserved; no provider calls.

Run with Blender --background --python-exit-code 1 --python <this file> --
  --kind reading --kit <kit.json> --source <reviewed source package> --output <new directory>
Use --dry-run before building. Outputs stay outside the source tree.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys

sys.path.insert(0, str(Path(__file__).parent))
import scene as S
import build_parks as original

READING_SOURCE = 'ff5a5e756235d361e995b162e5528042558d1a4d5c30a80e69422f60042481e2'
PLANTS = ('meadow_grass', 'flowering_perennial', 'silver_shrub')


def planted_rooms():
    """Replace sparse plants with bounded drifts while keeping authored paths clear."""
    for obj in list(S.bpy.context.scene.objects):
        if any(obj.name == kind or obj.name.startswith(kind + '.') for kind in PLANTS):
            S.bpy.data.objects.remove(obj, do_unlink=True)
    S.PLACEMENTS[:] = [p for p in S.PLACEMENTS if p['kind'] not in PLANTS]
    for room, region in enumerate(S.SURFACES):
        if region['material'] != 'soil':
            continue
        x, y, w, d = (region[k] for k in ('x', 'y', 'width', 'depth'))
        nx, ny = max(1, round((w - 1.0) / .65)), max(1, round((d - 1.0) / .65))
        for i in range(nx + 1):
            for j in range(ny + 1):
                # Shared native prototypes; deterministic offset and rotation.
                kind = PLANTS[(i // 2 + j + room) % len(PLANTS)]
                xx = x - w / 2 + .5 + (w - 1.0) * i / nx
                yy = y - d / 2 + .5 + (d - 1.0) * j / ny
                yaw = (i * 2.399963 + j * 1.37 + room) % math.tau
                scale = .76 + .07 * math.sin(i * 1.7 + j * 2.1 + room)
                # Full prototype envelope, including rotated foliage, stays in its bed.
                points = [v.co for mesh in S.KIT[kind] for v in mesh.vertices]
                radius = max(math.hypot(v.x, v.y) for v in points) * scale
                if abs(xx - x) + radius > w / 2 - .055 or abs(yy - y) + radius > d / 2 - .055:
                    continue
                S.kit(kind, xx, yy, 0, yaw, scale)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kind', choices=['reading'], required=True)
    parser.add_argument('--kit', type=Path, required=True)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    source_bytes = (args.source / 'assembly-preview.glb').read_bytes()
    if hashlib.sha256(source_bytes).hexdigest() != READING_SOURCE:
        raise ValueError('Reading source is not the reviewed tree-well revision.')
    if not args.kit.is_file() or args.output.exists():
        raise ValueError('A verified kit and a fresh output directory are required.')
    recipe = dict(original.SPECS['reading'])
    recipe.update(id='student_reading_garden_v2', revision='reading-v002',
                  programme='Two reading pergolas, connected cross paths, eight richly planted rooms and social seating',
                  source_assembly_sha256=READING_SOURCE,
                  source_recipe_sha256=hashlib.sha256((args.source / 'recipe.json').read_bytes()).hexdigest(),
                  kit_sha256=hashlib.sha256(args.kit.read_bytes()).hexdigest(),
                  reference_basis='Original City Prompt reading-garden composition; planting revision preserves paths, furniture and tree wells.')
    if args.dry_run:
        print('DRY_RUN_PASS', json.dumps(recipe))
        return
    args.output.mkdir(parents=True)
    S.init(args.kit)
    cameras = original.reading(recipe)
    planted_rooms()
    recipe['plant_count'] = sum(p['kind'] in PLANTS for p in S.PLACEMENTS)
    for path in [Path(__file__), Path(S.__file__), Path(original.__file__)]:
        shutil.copy2(path, args.output / path.name)
    S.deliver(args.output, recipe, cameras)
    # A real perspective view at eye height, from the open south entrance.
    from mathutils import Vector
    scene = S.bpy.context.scene
    cam = scene.camera
    cam.data.type = 'PERSP'
    cam.data.lens = 22
    cam.location = (0, -15.5, 1.65)
    cam.rotation_euler = (Vector((0, -1, 1.55)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = str(args.output / 'renders' / 'walk.png')
    S.bpy.ops.render.render(write_still=True)


if __name__ == '__main__':
    main()
